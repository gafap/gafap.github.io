---
layout: page
permalink: /publications/
title: Research
# No `description:`. Teaching and CV have none either, so the three pages share
# the same header shape: title only. Adding a line here would also become the
# page's SEO description.
nav: true
nav_order: 1
# No `_styles` block. This page used to hide its own header and set its own
# heading margins, which is why it looked unlike the teaching and CV pages. The
# heading spacing now lives in the shared type scale in assets/css/main.scss and
# applies to every page, and the title is shown here just as it is elsewhere.
---

<!-- Sections come from the BibTeX entry type in _bibliography/papers.bib, so
     there is only one file to maintain:
       @article      -> Publications
       @incollection -> Book Chapters
       @techreport   -> Working Papers
       @unpublished  -> Work in Progress
     Within each section, entries are sorted newest first (see the `scholar`
     block in _config.yml). -->

## Publications

<div class="publications">
{% bibliography --query @article %}
</div>

## Book Chapters

<div class="publications">
{% bibliography --query @incollection %}
</div>

## Working Papers

<div class="publications">
{% bibliography --query @techreport %}
</div>

## Work in Progress

<div class="publications">
{% bibliography --query @unpublished %}
</div>

<!-- Explains the music-note button. Comment this out again if the last `song`
     field ever leaves _bibliography/papers.bib, or it promises something the
     page does not show. -->
<p class="publications-footnote">
  Some papers carry a <i class="fa-solid fa-music" aria-hidden="true"></i> — a song that fits the
  paper. A paper takes years to finish, which is worth a small celebration.
</p>
