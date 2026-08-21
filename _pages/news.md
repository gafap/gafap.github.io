---
layout: page
permalink: /news/
title: News
description:
# Not in the navbar. The homepage's "News" heading links here, which is the only
# route to this page and the reason it exists -- before it, that heading pointed
# at a URL that 404'd.
nav: false
---

<!-- `news.liquid` is a local override (see the comment at the top of it). Called
     WITHOUT `limit=true`, it falls through to `news_limit = news_size` and lists
     every file in _news/, rather than the 5 most recent that the homepage shows
     via `announcements.limit` in _pages/about.md. That difference is the whole
     point of this page: older items stop appearing on the homepage but are still
     reachable here. -->

{% include news.liquid %}
