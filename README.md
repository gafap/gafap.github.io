# gafap.github.io

Source for my academic website: **<https://gafap.github.io>**

I am Gabriel Facchini, Associate Professor of Economics at Royal Holloway, University of London.
I work on labour, health and development economics. The site carries my research, teaching and CV.

---

## How the site is put together

It is a [Jekyll](https://jekyllrb.com/) site built on the
[al-folio](https://github.com/alshedivat/al-folio) starter, migrated from Weebly in August 2026.

Editing happens on `main`. A GitHub Action ([`.github/workflows/deploy.yml`](.github/workflows/deploy.yml))
builds the site and pushes the result to the `gh-pages` branch, which is what GitHub Pages serves.
A push takes 1–2 minutes to appear. GitHub's own built-in Jekyll builder cannot build al-folio, so
Pages must stay pointed at `gh-pages` rather than at `main`.

Most of the theme lives in versioned Ruby gems pinned in the [`Gemfile`](Gemfile), not in this
repository. A handful of templates are overridden locally by copying them in at the same path; each
override opens with a comment explaining what it changes and why.

### Content lives in data files, not in pages

| What | Where | Notes |
| ---- | ----- | ----- |
| Every paper | [`_bibliography/papers.bib`](_bibliography/papers.bib) | The BibTeX entry type picks the section: `@article` → Publications, `@techreport` → Working Papers, `@unpublished` → Work in Progress. Promoting a working paper is a one-word change. |
| Homepage news | [`_news/`](_news/) | One file per item, `YYYY-MM-DD-slug.md`. The five most recent show. |
| The CV | [`_cv/Facchini_CV.tex`](_cv/Facchini_CV.tex) | Single source of truth — see below. |
| Coauthor links | [`_data/coauthors.yml`](_data/coauthors.yml) | Names on the Research page become links when the person is listed here. |
| Every style decision | [`assets/css/main.scss`](assets/css/main.scss) | One shared type scale; no page sets its own fonts or colours. |

### The CV is generated, not hand-maintained

The website's CV page and the downloadable PDF are both built from the same LaTeX file:

```bash
python bin/cv_from_tex.py                                 # _cv/*.tex  ->  _data/cv.yml
pdflatex -output-directory=assets/pdf _cv/Facchini_CV.tex  # run twice
```

The deploy workflow runs `bin/cv_from_tex.py --check` and **fails the build** if `_data/cv.yml` has
drifted from the `.tex`. That guard exists because the two were once maintained by hand and fell out
of step — the PDF went eleven commits stale while the page kept being updated, so the download
contradicted the page beside it.

Full maintenance notes, including the traps worth knowing before changing anything, are in
[`CLAUDE.md`](CLAUDE.md).

---

## About the inherited files

This repository was started from the al-folio template rather than forked, so GitHub shows no
"forked from" banner — but a good deal of what is here still comes from upstream and is **not mine**:

- [`docs/`](docs/) — al-folio's own documentation (installation, customisation, its showcase and
  release notes), kept so the theme stays self-documenting through upgrades.
- [`.github/`](.github/) — upstream issue and PR templates, plus its Copilot instruction files.
  Only `workflows/deploy.yml` is specific to this site.
- [`bin/`](bin/) — upstream helper scripts. Only `cv_from_tex.py` is mine and used here.
- `Dockerfile`, `docker-compose*.yml`, [`.devcontainer/`](.devcontainer/) — upstream's local-preview
  setup, unused here.

These are left in place deliberately: deleting them makes future theme upgrades harder to reason
about, and they cost nothing at build time.

## Licence

The al-folio starter and theme are MIT-licensed, © Maruan Al-Shedivat and contributors — see
[`LICENSE`](LICENSE), which is retained unchanged as that licence requires.

The site's **content** — the text, the CV, the bibliography, the photographs and the papers linked
from it — is mine and is not covered by that licence.
