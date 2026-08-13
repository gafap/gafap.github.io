---
layout: page
permalink: /publications/
title: research
description: Publications by categories in reversed chronological order.
nav: true
nav_order: 1
# Page-scoped CSS (al-folio injects this as a <style> block on this page only).
_styles: >
  /* The page title and description are kept in the front matter above so the
     navbar label and the page's SEO description still work, but they are not
     shown on the page itself. */
  .post-header {
    display: none;
  }

  /* A bit more breathing room between the category sections. */
  .post h2 {
    margin-top: 2.75rem;
  }

  .post h2:first-of-type {
    margin-top: 0.5rem;
  }
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
