#!/usr/bin/env python3
"""Build _data/cv.yml from _cv/Facchini_CV.tex.

The .tex is the single source of truth for the CV (see the header comment in it).
This script reads the \\cv* macros out of it and writes the YAML that
_includes/cv/render.liquid expects, so the CV page and the downloadable PDF
cannot drift apart the way they did before -- the PDF once went 11 commits stale
while the page kept being edited.

    python bin/cv_from_tex.py            # rewrite _data/cv.yml
    python bin/cv_from_tex.py --check    # exit 1 if _data/cv.yml is out of date

--check is what the deploy workflow runs. A forgotten regeneration then fails the
build instead of quietly shipping a CV page that disagrees with the PDF beside it.

WHY A MACRO FORMAT AND NOT A PARSER FOR ORDINARY LaTeX: the previous .tex wrote a
job as free prose --

    \\item Associate Professor, Economics Department, Royal Holloway (University of
          London) Aug2026-- current.

-- from which no rule reliably says which comma-separated chunk is the role, which
the department and which the institution. Rather than guess with heuristics that
break the first time a comma moves, the .tex now labels the parts. This script
therefore does no inference at all: it reads arguments.

Requires PyYAML only for --check (to compare parsed structures); the writer is
hand-rolled so the output stays diff-friendly and comment-free.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEX = ROOT / "_cv" / "Facchini_CV.tex"
OUT = ROOT / "_data" / "cv.yml"

# Section name in the .tex -> section name on the website. A section absent from
# this map is DROPPED, which is how Research (built from papers.bib instead) and
# References (four colleagues' email addresses, not for a public page) stay off
# the site. Renaming a heading in the .tex without updating this map silently
# drops that section -- --check will not catch it, because it compares against
# this script's own output.
SECTION_MAP = {
    "Academic Positions": "Experience",
    "Education": "Education",
    "Fields of Interest": "Fields of Interest",
    "Grants": "Grants",
    "Awards": "Awards",
    "Professional Service": "Professional Service",
    "Invited Seminars": "Invited Seminars",
    "Conference Presentations": "Conference Presentations",
    "Teaching": "Teaching",
    "Referee Service": "Referee Service",
    "Other Employment": "Other Employment",
    "Languages": "Languages",
}

# Order of sections on the CV page. Sections are emitted in this order regardless
# of where they sit in the .tex, so the PDF's ordering and the page's ordering can
# differ where that reads better.
SECTION_ORDER = [
    "Experience",
    "Education",
    "Fields of Interest",
    "Research",
    "Grants",
    "Awards",
    "Professional Service",
    "Invited Seminars",
    "Conference Presentations",
    "Teaching",
    "Referee Service",
    "Other Employment",
    "Languages",
]

# Sections the website adds that have no counterpart in the .tex.
SYNTHETIC = {
    "Research": [
        {
            "bullet": "See the [publications page](/publications/) for the full list of "
            "published papers, book chapters, working papers and work in progress."
        }
    ]
}

MONTHS = {
    "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", "06": "Jun",
    "07": "Jul", "08": "Aug", "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec",
}

# ---------------------------------------------------------------------------
# LaTeX -> text
# ---------------------------------------------------------------------------

# Accent macros: \'{e} -> é. Written as (macro, letter) -> character rather than
# via unicodedata so that the mapping is explicit and reviewable.
ACCENTS = {
    ("'", "a"): "á", ("'", "e"): "é", ("'", "i"): "í", ("'", "o"): "ó",
    ("'", "u"): "ú", ("'", "A"): "Á", ("'", "E"): "É", ("'", "I"): "Í",
    ("'", "O"): "Ó", ("'", "U"): "Ú",
    ("`", "a"): "à", ("`", "e"): "è", ("`", "i"): "ì", ("`", "o"): "ò",
    ("`", "u"): "ù", ("`", "A"): "À", ("`", "E"): "È", ("`", "O"): "Ò",
    ("^", "a"): "â", ("^", "e"): "ê", ("^", "i"): "î", ("^", "o"): "ô",
    ("^", "u"): "û", ("^", "E"): "Ê",
    ('"', "a"): "ä", ('"', "e"): "ë", ('"', "i"): "ï", ('"', "o"): "ö",
    ('"', "u"): "ü", ('"', "U"): "Ü",
    ("~", "n"): "ñ", ("~", "N"): "Ñ", ("~", "a"): "ã", ("~", "o"): "õ",
    ("c", "c"): "ç", ("c", "C"): "Ç",
}


def detex(s: str) -> str:
    """Turn a LaTeX fragment into the plain text the website should show."""
    # Accents, both \'{e} and \'e forms.
    for (macro, letter), char in ACCENTS.items():
        s = s.replace("\\" + macro + "{" + letter + "}", char)
        s = s.replace("\\" + macro + letter, char)

    # Currency. \euro{115,000} and \pounds4,000 -> the symbol.
    s = re.sub(r"\\euro\{([^}]*)\}", r"€\1", s)
    s = s.replace("\\euro", "€").replace("\\pounds", "£")
    s = s.replace("\\$", "$").replace("\\&", "&").replace("\\%", "%")

    # Superscript ordinals: $39^{th}$ -> 39th.
    s = re.sub(r"\$(\d+)\^\{(\w+)\}\$", r"\1\2", s)

    # Quotes: LaTeX ``...'' -> "...". Do the pair before the lone apostrophe.
    s = s.replace("``", '"').replace("''", '"')

    # Emphasis and font switches: keep the text, drop the wrapper.
    s = re.sub(r"\\(?:textit|textbf|emph|texttt|textsc)\{([^{}]*)\}", r"\1", s)
    s = re.sub(r"\{\\(?:bf|it|em|tt|sc)\s+([^{}]*)\}", r"\1", s)

    # Escaped spacing and remaining control sequences.
    s = s.replace("\\ ", " ").replace("\\,", " ").replace("~", " ")
    s = re.sub(r"\\[a-zA-Z]+\s*", "", s)

    # Leftover braces.
    s = s.replace("{", "").replace("}", "")

    return re.sub(r"\s+", " ", s).strip()


def strip_comments(text: str) -> str:
    """Remove LaTeX comments, keeping line count so offsets stay meaningful.

    Necessary, not cosmetic: the .tex header documents the macros by example, so
    the file contains lines like `%   \\cvposition{role}{institution}{...}`. Without
    this the parser reads those illustrations as real entries -- and, because the
    example is wrapped across two comment lines, fails outright trying to find
    their arguments.

    An escaped \\% is not a comment.
    """
    out = []
    for line in text.split("\n"):
        i, n = 0, len(line)
        while i < n:
            if line[i] == "\\":
                i += 2
                continue
            if line[i] == "%":
                line = line[:i]
                break
            i += 1
        out.append(line)
    return "\n".join(out)


def split_args(text: str, start: int, count: int):
    """Read `count` brace-delimited arguments beginning at `start`.

    Returns (args, index_after_last). Brace-counting rather than a regex, because
    the arguments contain braces of their own (\\euro{115,000}, \\'{o}).
    """
    args, i, n = [], start, len(text)
    for _ in range(count):
        while i < n and text[i] in " \t\r\n":
            i += 1
        if i >= n or text[i] != "{":
            raise ValueError(f"expected {{ at offset {i}: {text[i:i+40]!r}")
        depth, j = 1, i + 1
        while j < n and depth:
            if text[j] == "\\":                      # skip an escaped character
                j += 2
                continue
            depth += (text[j] == "{") - (text[j] == "}")
            j += 1
        args.append(text[i + 1 : j - 1])
        i = j
    return args, i


def iter_macros(text: str, name: str, arity: int):
    """Yield (position, args) for every \\name{..}{..} occurrence, in order."""
    for m in re.finditer(r"\\" + name + r"(?![a-zA-Z])", text):
        try:
            args, _ = split_args(text, m.end(), arity)
        except ValueError as exc:
            raise SystemExit(f"{TEX.name}: malformed \\{name} at offset {m.start()}: {exc}")
        yield m.start(), args


def iso(date: str) -> str:
    """'2026-08' stays as-is; it is what the CV template wants."""
    date = date.strip()
    if not date:
        return ""
    if not re.fullmatch(r"\d{4}(-\d{2})?", date):
        raise SystemExit(f"{TEX.name}: date {date!r} is not YYYY or YYYY-MM")
    return date


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse(text: str) -> dict:
    text = strip_comments(text)

    # Identity, from the \def block.
    ident = {}
    for m in re.finditer(r"\\def\\cv([A-Za-z]+)\{((?:[^{}]|\{[^{}]*\})*)\}", text):
        ident[m.group(1)] = detex(m.group(2))

    for required in ("Name", "Label", "Email", "Homepage"):
        if required not in ident:
            raise SystemExit(f"{TEX.name}: \\def\\cv{required} is missing")

    # Entries are read from the document body only. The preamble defines the very
    # macros we are looking for (\newcommand{\cvposition}[5]{...}), and scanning it
    # would read each definition as an entry.
    split = text.find(r"\begin{document}")
    if split < 0:
        raise SystemExit(rf"{TEX.name}: no \begin{{document}}")
    text = text[split:]

    # Where each section starts, so an entry can be attributed to one.
    heads = [
        (m.start(), detex(m.group(1)))
        for m in re.finditer(r"\\section\*\{([^}]*)\}", text)
    ]

    def section_of(pos: int) -> str | None:
        name = None
        for start, title in heads:
            if start < pos:
                name = title
            else:
                break
        return SECTION_MAP.get(name) if name else None

    # (position, entry) per section. Positions are kept because \cvhighlight has to
    # attach to the entry it physically follows in the file, and macros are read
    # macro-by-macro rather than in document order.
    collected: dict[str, list[tuple[int, dict]]] = {}

    def add(pos: int, entry: dict):
        sec = section_of(pos)
        if sec:
            collected.setdefault(sec, []).append((pos, entry))

    for pos, (role, org, loc, start, end) in iter_macros(text, "cvposition", 5):
        entry = {
            "company": detex(org),
            "position": detex(role),
            "location": detex(loc),
            "start_date": iso(start),
        }
        if end.strip():
            entry["end_date"] = iso(end)
        add(pos, entry)

    for pos, (degree, inst, loc, year) in iter_macros(text, "cveducation", 4):
        add(pos, {
            "institution": detex(inst),
            "location": detex(loc),
            "studyType": detex(degree),
            "date": detex(year),
        })

    for pos, (txt,) in iter_macros(text, "cvbullet", 1):
        add(pos, {"bullet": detex(txt)})

    for pos, (label, title, details) in iter_macros(text, "cvgrant", 3):
        add(pos, {"label": detex(label), "title": detex(title), "details": detex(details)})

    for pos, (title, awarder, date, note) in iter_macros(text, "cvaward", 4):
        entry = {"title": detex(title), "awarder": detex(awarder), "date": detex(date)}
        if note.strip():
            entry["summary"] = detex(note) + "."
        add(pos, entry)

    for pos, (label, details) in iter_macros(text, "cvyear", 2):
        add(pos, {"label": detex(label), "details": detex(details)})

    # \cvhighlight belongs to the entry it physically follows -- the thesis
    # committee under the PhD, not under whichever entry happened to be read last.
    # Attaching to sections[sec][-1] is the obvious version and is WRONG: by the
    # time highlights are processed, [-1] is the final degree in the section.
    for pos, (txt,) in iter_macros(text, "cvhighlight", 1):
        sec = section_of(pos)
        if not sec or sec not in collected:
            continue
        earlier = [e for p, e in collected[sec] if p < pos]
        if earlier:
            earlier[-1].setdefault("highlights", []).append(detex(txt))

    sections = {sec: [e for _, e in sorted(v)] for sec, v in collected.items()}
    sections.update(SYNTHETIC)

    ordered = {k: sections[k] for k in SECTION_ORDER if k in sections}
    for extra in sections:                       # anything mapped but not ordered
        if extra not in ordered:
            ordered[extra] = sections[extra]

    return {
        "name": ident["Name"],
        "label": ident["Label"],
        "email": ident["Email"],
        "website": ident["Homepage"],
        "address": {
            "street": ident.get("Street", ""),
            "city": ident.get("City", ""),
            "region": ident.get("Region", ""),
            "postalCode": ident.get("Postcode", ""),
            "countryCode": ident.get("Country", ""),
        },
        "sections": ordered,
    }


# ---------------------------------------------------------------------------
# Emitting
# ---------------------------------------------------------------------------

def q(v: str) -> str:
    """Quote a scalar only when YAML needs it, so the file stays readable."""
    s = str(v)
    if s == "":
        return '""'
    needs = (
        s[0] in "-?:,[]{}#&*!|>'\"%@`" or s[-1] in " :" or ": " in s or " #" in s
        or s.lower() in {"true", "false", "null", "yes", "no", "on", "off", "~"}
        or re.fullmatch(r"-?\d+(\.\d+)?([eE][-+]?\d+)?", s) is not None
    )
    if not needs:
        return s
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


# Key order within an entry, so regenerating never reshuffles a file.
KEY_ORDER = [
    "company", "institution", "position", "studyType", "location",
    "start_date", "end_date", "date", "highlights",
    "label", "title", "awarder", "details", "summary", "bullet",
]


def emit(cv: dict) -> str:
    L: list[str] = []
    L.append("# GENERATED FILE -- DO NOT EDIT BY HAND.")
    L.append("#")
    L.append("# Written by bin/cv_from_tex.py from _cv/Facchini_CV.tex, which is the")
    L.append("# single source of truth for the CV. Edit the .tex, then run:")
    L.append("#")
    L.append("#     python bin/cv_from_tex.py")
    L.append("#     pdflatex -output-directory=assets/pdf _cv/Facchini_CV.tex   (twice)")
    L.append("#")
    L.append("# Any edit made directly here is lost the next time that runs, and the")
    L.append("# deploy workflow fails the build when this file disagrees with the .tex.")
    L.append("cv:")
    L.append(f"  name: {q(cv['name'])}")
    L.append(f"  label: {q(cv['label'])}")
    L.append(f"  email: {q(cv['email'])}")
    L.append(f"  website: {q(cv['website'])}")
    L.append("  address:")
    for k, v in cv["address"].items():
        L.append(f"    {k}: {q(v)}")
    L.append("")
    L.append("  sections:")
    for name, entries in cv["sections"].items():
        L.append(f"    {q(name) if ':' in name else name}:")
        for entry in entries:
            keys = [k for k in KEY_ORDER if k in entry]
            keys += [k for k in entry if k not in keys]
            first = True
            for k in keys:
                v = entry[k]
                lead = "      - " if first else "        "
                first = False
                if k == "highlights":
                    L.append(f"{lead}{k}:")
                    for h in v:
                        L.append(f"          - {q(h)}")
                else:
                    L.append(f"{lead}{k}: {q(v)}")
        L.append("")
    while L and L[-1] == "":
        L.pop()
    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if _data/cv.yml is out of date instead of rewriting it")
    args = ap.parse_args()

    if not TEX.exists():
        print(f"error: {TEX} not found", file=sys.stderr)
        return 1

    generated = emit(parse(TEX.read_text(encoding="utf-8")))

    if args.check:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current.replace("\r\n", "\n") == generated:
            print(f"ok: {OUT.relative_to(ROOT)} matches {TEX.relative_to(ROOT)}")
            return 0
        print(
            f"error: {OUT.relative_to(ROOT)} is out of date with respect to "
            f"{TEX.relative_to(ROOT)}.\n"
            f"       Run: python bin/cv_from_tex.py",
            file=sys.stderr,
        )
        return 1

    OUT.write_text(generated, encoding="utf-8", newline="\n")
    n = sum(len(v) for v in parse(TEX.read_text(encoding='utf-8'))["sections"].values())
    print(f"wrote {OUT.relative_to(ROOT)} ({n} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
