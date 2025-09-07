# jsnet-website
Templates, scripts, and content for www.jamessiddle.net

## Local Preview (Jekyll)

This site uses Jekyll collections for the bibliography. To preview locally, use a Homebrew- or rbenv-managed Ruby (avoid the macOS system Ruby at `/usr/bin/ruby`).

Prerequisites
- macOS Command Line Tools: `xcode-select --install`
- Ruby 3.1.x, via homebrew:

1) Install Ruby: `brew install ruby@3.1`
2) Add Ruby to your PATH and restart your shell:
   - Apple Silicon: `echo 'export PATH="/opt/homebrew/opt/ruby@3.1/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc`
3) Verify: `ruby -v` (should be 3.1.x), `which ruby` (not `/usr/bin/ruby`)

Install dependencies
- Install bundler: `gem install bundler`
- From the repo root: `bundle install`

Run locally
- Serve with live reload: `bundle exec jekyll serve`
- Open: http://127.0.0.1:4000
- Build only: `bundle exec jekyll build` (outputs to `_site/`)

Notes
- GitHub Pages builds the site from source when you push; do not commit `_site/`.
- If port 4000 is busy: `bundle exec jekyll serve --port 4001`

## TODO

- Tidy up CSS for content vs cover

## Bibliography content schema

Add bibliography items as Markdown files under `_biblio/` with YAML front matter. The list page groups items by `type` and item pages render buttons from `links`.

Required fields
- `title`: Human-readable title.
- `topic`: One of `software`, `agile`, `medical`, `dataviz`, `tutorials`, `life`.
- `type`: One of `talks`, `journals`, `conferences`, `articles`, `posts`, `press`.
- `date`: ISO date `YYYY-MM-DD` (displayed as `Mon YYYY`).
- `outlet`: Venue/source (conference, journal, blog, etc.).
- `slug`: URL slug used in permalink `/biblio/:slug/`.

Optional fields
- `summary`: Short teaser shown on item page.
- `links`: Buttons shown on the item page if present:
  - `pdf`: URL to a PDF (download).
  - `video`: URL to a video.
  - `slides`: URL to slides.
  - `external`: External article/link.
- `tags`: Array of tags, e.g. `[agile, architecture]`.
- `location`: Free text location (not currently displayed).
- `featured`: Boolean flag (not currently displayed).

Example
```yaml
---
title: Agile Product Roadmaps for Software Architecture
slug: agile-product-roadmaps
topic: software
type: talks
date: 2018-02-01
outlet: O'Reilly Software Architecture Conference
summary: How to align evolving architecture with agile product planning.
links:
  video: https://example.com/video
  slides: https://example.com/slides
tags: [agile, architecture, product]
---

Optional long-form content/notes here.
```

Notes
- The list page is `biblio.html`; it groups by `topic`.
- Item layout is `_layouts/biblio_item.html`.
- Styles live in `css/biblio.css` (e.g., `.bib-summary` for the summary text sizing).
