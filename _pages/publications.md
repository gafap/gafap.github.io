---
layout: page
permalink: /publications/
title: research
description: Publications by categories in reversed chronological order.
nav: true
nav_order: 1
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
