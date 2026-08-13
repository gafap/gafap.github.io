---
layout: page
permalink: /publications/
title: publications
description:
nav: true
nav_order: 1
---

<!-- _pages/publications.md -->

<!-- Bibsearch Feature -->

{% include bib_search.liquid %}

## Publications

<div class="publications">
{% bibliography -f papers %}
</div>

## Book Chapters

<div class="publications">
{% bibliography -f chapters %}
</div>

## Working Papers

<div class="publications">
{% bibliography -f working_papers %}
</div>

## Work in Progress

<div class="publications">
{% bibliography -f wip %}
</div>
