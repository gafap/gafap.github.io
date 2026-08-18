# Maintaining this website

This is Gabriel Facchini's academic website: <https://gafap.github.io>. It is a
[Jekyll](https://jekyllrb.com/) site built on the [al-folio](https://github.com/alshedivat/al-folio)
theme, migrated from Weebly in August 2026.

This file is the maintenance guide. It is also what Claude Code reads automatically at the start of
every session in this repo, so the conventions below are instructions, not just notes.

---

## 1. Before anything else: five rules

1. **This repo must stay outside Dropbox.** It lives at `C:\Users\gabri\Git\gafap.github.io`.
   Dropbox and git both want to manage `.git/`, and they corrupt it between them. Never move or
   copy the working repo into `~/Dropbox`.
2. **GitHub Pages must stay pointed at the `gh-pages` branch, not `main`.** You edit `main`; a
   GitHub Action builds the site and writes the result to `gh-pages`. GitHub's own built-in Jekyll
   builder cannot build al-folio, so pointing Pages at `main` breaks the site.
3. **There is no Ruby installed on this machine, and that is deliberate.** You cannot build or
   preview the site locally. See §4 for how to preview.
4. **Style decisions go in one place.** Never give a page its own font size, weight or colour —
   see §6.
5. **`robots.txt` currently blocks every search engine.** That is on purpose while the site is
   under construction, and it must be reverted before the site is announced. See §8.

---

## 2. Everyday tasks

### Add a paper

Everything on the Research page comes from one file: `_bibliography/papers.bib`. There is no second
list to keep in sync. The BibTeX **entry type** decides which section the paper appears under:

| Entry type      | Section on the page |
| --------------- | ------------------- |
| `@article`      | Publications        |
| `@incollection` | Book Chapters       |
| `@techreport`   | Working Papers      |
| `@unpublished`  | Work in Progress    |

So a working paper that gets accepted is promoted by changing `@techreport` to `@article` and
adding the `journal`, `volume`, `pages` and `doi` fields. Nothing else moves.

Beyond the standard BibTeX fields, these are the custom ones this site understands:

| Field         | What it does |
| ------------- | ------------ |
| `abbr`        | Entry-type badge text. Not currently displayed (the badge column was removed in `_layouts/bib.liquid`) but keep setting it — it is filtered out of the `+bib` output and the column can be restored. |
| `abstract`    | Adds an **+abstract** button that expands the text underneath the entry. |
| `bibtex_show` | Set to `{true}` to add a **+bib** button showing the BibTeX. |
| `doi`         | Adds a **journal** button linking to the published article. |
| `pdf`         | Adds a **WP** button. A full URL is used as-is; a bare filename is looked up in `assets/pdf/`. |
| `pdf_label`   | Overrides the **WP** button label, for when the PDF is not a working paper. |
| `award`       | Adds an **+awarded** button that expands the award text. `award_name` renames the button. |
| `links_note`  | Plain text printed after the buttons, e.g. `New version coming soon`. Not a button — nothing to click. |
| `selected`    | Marks a paper for the homepage's selected-papers block. **Currently inert**: `selected_papers: false` in `_pages/about.md` turns that block off. |
| `annotation`  | Adds a small info popover next to the authors. |

Sorting within each section is newest first (`sort_by: year`, `order: descending` in `_config.yml`).
**Work-in-progress entries carry no `year`** — they have no real one yet — so all four tie and that
section displays them in the *reverse* of their order in the file. Reorder them in `papers.bib` to
change what the page shows.

Coauthor names become links if the person is listed in `_data/coauthors.yml`.

### Add a button next to +abstract and +bib

The little grey boxes under a paper are all generated from BibTeX fields. **Most of the time you do
not need to touch any template** — the field already exists and you just add it to the entry in
`papers.bib`. These are every button the template can already produce, in the order they appear on
the page:

| Add this field | Button you get | Notes |
| -------------- | -------------- | ----- |
| `award`        | **+awarded**   | Expands the award text. `award_name` renames the button. |
| `abstract`     | **+abstract**  | Expands the abstract. |
| `doi`          | **journal**    | Just the DOI, no `https://doi.org/` prefix. |
| `arxiv`        | **arXiv**      | The arXiv ID only. |
| `hal`          | **HAL**        | The HAL ID only. |
| `bibtex_show`  | **+bib**       | Set it to `{true}`. |
| `html`         | **HTML**       | Full URL, or a bare filename found in `assets/html/`. |
| `pdf`          | **WP**         | Full URL, or a bare filename found in `assets/pdf/`. `pdf_label` renames the button. |
| `supp`         | **Supp**       | Supplementary material. Full URL or a filename in `assets/pdf/`. |
| `video`        | **Video**      | Opens the link in a new tab (`enable_video_embedding` is `false`). |
| `blog`         | **Blog**       | Full URL. |
| `code`         | **Code**       | Full URL — a GitHub repo, say. |
| `poster`       | **Poster**     | Full URL or a filename in `assets/pdf/`. |
| `slides`       | **Slides**     | Full URL or a filename in `assets/pdf/`. |
| `website`      | **Website**    | Full URL — a project page. |

So a **Slides** button is one line in the entry, nothing more:

```bibtex
slides = {my-talk.pdf},
```

with `my-talk.pdf` dropped into `assets/pdf/`.

The naming convention on this site: **a `+` prefix means the button expands text underneath the
entry; no prefix means it navigates away.** Keep that distinction if you add anything new.

#### A button that does not exist yet

Only if none of the above fits — say a **Data** button for a replication archive. Three steps, all
required:

1. In `_layouts/bib.liquid`, inside the `<!-- Links/Buttons -->` block, copy an existing simple case
   (the `code` one is the shortest) and change the field name and label:

   ```liquid
   {% if entry.data %}
     <a href="{{ entry.data }}" class="btn btn-sm z-depth-0" role="button">Data</a>
   {% endif %}
   ```

   Its position in that block is its position on the page.

2. Add `data,` to the `filtered_bibtex_keywords` list in `_config.yml`, keeping the list
   alphabetical. **Skipping this is the classic mistake**: the field is not real BibTeX, so without
   it the raw `data = {...}` line leaks into what the **+bib** button shows.

3. Note the addition in the comment block at the top of `bib.liquid`, which is the running list of
   how this file differs from the gem's version. That comment is what makes the next theme upgrade
   survivable.

Do not style the button. `btn btn-sm z-depth-0` is the theme's own class set and every button on the
site already uses it.

### Add a news item

News appears on the homepage. One file per item in `_news/`, named `YYYY-MM-DD-short-slug.md`:

```markdown
---
layout: post
date: 2026-09-01 09:00:00+0100
inline: true
related_posts: false
---

New project: **EDUCARE** — a study of early childhood education. Funded by Fundació "la Caixa".
```

- The date in the filename orders the list; the `date:` in the front matter is what gets displayed.
  Keep the two the same. The `+0100` / `+0000` is a timezone offset — `+0100` for British Summer
  Time, `+0000` for winter. It only affects the printed date at the very edges of a day.
- `inline: true` means the item is a one-liner shown in place, not a linked blog post. Every item on
  this site is inline. Keep it that way unless you actually want a separate post page.
- The body is markdown: `**bold**`, `*italic*` and `[text](https://url)` all work.
- The homepage shows the **5 most recent** (`announcements.limit` in `_pages/about.md`). Older items
  stay in the folder and simply stop showing. Delete the file to remove one entirely.

### Update the CV

Two things have to move together:

1. `_data/cv.yml` — the text of the CV as rendered on the website.
2. `assets/pdf/Facchini_CV.pdf` — the downloadable PDF, linked from the icon in the CV page header
   and from the CV icon on the homepage.

They are maintained by hand and do not check each other, so **when you update the PDF, update the
YAML in the same commit.**

`_data/cv.yml` has a `sections:` block, and each section name becomes a heading on the page. The
layout of a section is decided by the *shape of its entries*, not by the section name:

| Entry shape | Renders as | Used by |
| ----------- | ---------- | ------- |
| `company` / `position` / `location` / `start_date` / `end_date` | Two columns: dates left, role right | Experience |
| `institution` / `studyType` / `date` / `location` / `highlights` | Two columns: year left, degree right | Education |
| `label` / `title` / `details` | Two columns: `label` left, the rest right | Grants, Awards, Seminars, Conferences |
| `bullet` | One full-width line | Fields of Interest, Research, Teaching, Referee Service, Languages |

Two traps here:

- **Markdown only works inside `bullet`.** A `details:` or `title:` string is printed raw, so
  `[link](/publications/)` in a `details` field shows up as literal square brackets. This is why the
  Research and Teaching sections are written as `bullet` entries.
- **An entry with no `label` gets an empty left column** and visually groups itself under the entry
  above it. Every dated entry needs one.

### Update the teaching page

`_pages/teaching.md` is hand-written HTML rather than a data file, because it is a short list that
changes once a year. Copy an existing `<li class="teaching-item">` block and edit it. Do not add any
styling to it — the classes (`.teaching-course`, `.teaching-level`, `.teaching-years`) are already
typeset by the shared type scale (§6).

### Change the photos

`assets/img/prof_pic.jpg` is the light-mode photo, `assets/img/prof_pic_dark.jpg` the dark-mode one.
**Keep both at the same pixel dimensions** — both are rendered and one is hidden with CSS, so
mismatched sizes make the page jump when the theme is toggled.

---

## 3. Publishing a change

```bash
cd C:/Users/gabri/Git/gafap.github.io
git add -A
git commit -m "Short description of what changed"
git push origin main
```

Pushing to `main` triggers `.github/workflows/deploy.yml`, which builds the site and pushes the
result to `gh-pages`. It takes **1–2 minutes**. Watch it at
<https://github.com/gafap/gafap.github.io/actions> — a green tick means the change is live.

If the build fails the site does not change; the previous version stays up. Open the failed run on
that Actions page and read the log for the step marked in red.

## 4. Previewing

There is no local preview — there is no Ruby on this machine (rule 3). The way to see a change is to
push it and look at the live site a couple of minutes later. That is acceptable here because the
site is currently blocked from search engines and gets essentially no traffic.

If a genuine local preview is ever wanted, the options are installing Ruby and running
`bundle install`, or using the `Dockerfile` / `docker-compose.yml` already in this repo. Both are
real installations — discuss before doing either.

## 5. The theme is a gem, not files in this repo

Most of al-folio lives in Ruby gems (`al_folio_core` and friends, pinned in the `Gemfile`), not in
this repository. If you go looking for the template that produces something on the page and cannot
find it here, that is why — it is inside the gem.

To change one of those templates you **copy it into this repo at the same path**, and the copy wins.
The files below are the copies that already exist. Each one opens with a comment saying what was
changed and why; read that comment before touching it.

| Local override | What it changes |
| -------------- | --------------- |
| `assets/css/main.scss` | Passes two custom colours into the theme, then defines the shared type scale and all site-specific CSS (§6). |
| `_layouts/bib.liquid` | Renames the publication buttons (`+abstract`, `+bib`, `journal`, `WP`), removes the badge column, adds `links_note`. |
| `_layouts/about.liquid` | Photo above the header, whole name bold, dark-mode photo support, `_styles` support. |
| `_includes/cv/render.liquid` | Two-column CV entries, one-line Languages, email as a `mailto:` link. |
| `_includes/news.liquid` | News as a bulleted list instead of the gem's wide-column table. |
| `_includes/footer.liquid` | Shorter one-line footer. |

After a `bundle update`, check whether the gem's version of an overridden file has moved on:

```bash
bundle exec al-folio upgrade overrides diff _layouts/bib.liquid
```

(That command needs Ruby, so it is not runnable on this machine today.)

## 6. Design rules

These exist because the Research, Teaching and CV pages drifted apart when each was styled
separately. They are the fix, and undoing them re-creates the problem.

- **One shared type scale, in `assets/css/main.scss`.** Five levels: page title, section heading,
  entry title, entry detail, small print. Each is set once and applies to every page.
- **No page sets a font size, weight or colour of its own.** Do not add `_styles:` blocks to page
  front matter for typography. The single intentional exception is the name on the homepage, which
  `_pages/about.md` sets to 2.1rem because it is a name, not a page title.
- **Colour goes on section headings and on muted metadata — never on titles.** Paper titles and
  course names are deliberately uncoloured and are distinguished by weight (500) instead. A coloured
  heading with no underline does not read as a link, but a coloured 1rem line sitting directly above
  a row of buttons does.
- **Two colour tokens**, both defined at the top of `main.scss`: `--heading-accent` (the site blue,
  `#094a83` light / `#6fb3e8` dark) and `--meta-color` (a neutral slate for venues, years and course
  levels). Both were chosen to pass WCAG AA contrast in both themes. Use the tokens; do not write
  new hex values into a rule.
- **All three content pages show a title and nothing else** — none has a `description:` in its front
  matter. Adding one to a single page makes it look unlike the other two.

## 7. Where everything lives

```
_bibliography/papers.bib     every paper, in every section of the Research page
_news/                       one file per homepage news item
_data/cv.yml                 the CV text
_data/coauthors.yml          coauthor names -> their websites
_data/socials.yml            which contact icons appear, and their targets
_pages/about.md              homepage: bio, photo settings, news limit
_pages/publications.md       Research page: section headings and their bib queries
_pages/teaching.md           Teaching page: hand-written HTML list
_pages/cv.md                 CV page: points the layout at _data/cv.yml
assets/pdf/                  the CV PDF
assets/img/                  the two profile photos
assets/css/main.scss         every style decision on the site
_config.yml                  site-wide settings
robots.txt                   currently blocking all crawlers -- see below
```

The `_books/`, `_projects/`, `_teachings/` and `_posts/` folders are empty on purpose — those parts
of al-folio are not used here. Three of them are still declared under `collections:` in
`_config.yml`, so if you ever want to be rid of a section properly, remove its declaration there as
well as the folder.

## 8. Known open items

- **`robots.txt` blocks all search engines.** It has `Disallow: /` and the `Sitemap:` line is
  commented out. **Revert both before announcing the site**, or it will never appear in Google. The
  file itself carries instructions on how.
- **Unlisted pages are not set up yet.** For teaching materials that should be reachable by URL but
  neither listed nor indexed, the agreed pattern is `nav: false` + `sitemap: false` in the front
  matter plus a noindex meta tag. The repo itself stays public.
- **The email address sits in the page source as a plain `mailto:`**, both in the homepage contact
  icons and in the CV contact table. `protect_email: true` in `_config.yml` does not prevent it,
  because the contact icons are generated by the `jekyll-socials` plugin, which ignores that
  setting. This is a known and accepted trade-off — a clickable address is worth more than weak
  obfuscation — but do not assume that setting is doing anything.
