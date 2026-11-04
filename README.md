# Culture Calendar

A small static site, published with GitHub Pages at https://cultureradar.to/

- `index.html` — the home page: Culture Radar Toronto, a monthly list of picks across seven lanes (film, art, music, theatre, talks, outdoors, festivals), with This week / This weekend and Free only filters. Data lives in the `E` array in the page script; the masthead’s `.issue` block holds the edition month and date. Picks, tabs, counts, and sections are all built from `E`.
- `links/index.html` — Culture Calendar T.O., a secondary page linking the Radar, the Fox, and both archives (served at /links/).
- `fox/index.html` — Fox Theatre screenings for the next four weeks. Data lives in the `F` (films) and `S` (schedule) objects in the page script.
- `tiff/index.html` — TIFF Lightbox screenings for the next four weeks, same layout as the Fox page. `F` entries are [title, year, runtime, kind (new|cin|special|partner), blurb, director, series, ticket URL, format]; `S` keys are November day numbers. tiff.net blocks automated reads, so it is refreshed through Chrome (calendar at tiff.net/calendar) with CinemaClock as a cloud fallback. iCal files in `tiff/ics/` and `tiff/tiff.ics`: `python3 tools/make_ics.py tiff/index.html tiff/ics tiff/tiff.ics YEAR MONTH tiff`.
- `revue/index.html` — Revue Cinema screenings for the next four weeks, built from the TIFF template (same `F`/`S` format; kinds: cin = repertory and series, new = new films, special = guests and live events, partner = festivals and rentals). Data comes from revuecinema.ca by WebFetch: the film list from `https://revuecinema.ca/wp-json/wp/v2/films?per_page=40&page=N&orderby=modified&order=desc&_fields=slug,modified` (films still on the schedule were all modified the same morning), each film page `https://revuecinema.ca/films/<slug>/` for showtimes and details, and the monthly PDF calendar linked from `https://revuecinema.ca/calendar/` for sold-out notes. Ticket links are the Revue film pages. iCal: `python3 tools/make_ics.py revue/index.html revue/ics revue/revue.ics YEAR MONTH revue`. Leave out private rentals, staff closures, members-only screenings, and the Film Society AGM.
- `fox/ics/` and `fox/fox.ics` — iCal files, one per showing plus a subscribable feed. Generated from the page data; never edit by hand.
- `radar/index.html` — redirect only: the Radar used to live at /radar/ and now lives at the site root.
- `assets/fonts.css` + `assets/fonts/` — self-hosted typefaces (Archivo, Newsreader, IBM Plex Mono; SIL Open Font License) shared by every page.
- `radar/archive/` — one folder per edition (`YYYY-MM/`) plus an index. Generated; never edit by hand.
- `tools/archive_radar.py` — run after every change to the Radar (`index.html`): copies the edition into `radar/archive/<month>/` and rebuilds the archive index (`python3 tools/archive_radar.py`).
- `fox/archive/` — one folder per weekly Fox snapshot (`YYYY-MM-DD/`, with its iCal files) plus an index. Generated; never edit by hand.
- `tiff/archive/` and `tools/archive_tiff.py` — the same weekly snapshots for the TIFF Lightbox page (`python3 tools/archive_tiff.py` before and after each refresh).
- `revue/archive/` and `tools/archive_revue.py` — the same weekly snapshots for the Revue page (`python3 tools/archive_revue.py` before and after each refresh).
- `tools/archive_fox.py` — run after every weekly refresh of `fox/index.html` (`python3 tools/archive_fox.py`).
- `tools/social/make_kit.py` — renders the Instagram kit (carousel, weekly story, caption) from the Radar, plus the link-preview image every page uses (`assets/social/og.png`): `python3 tools/social/make_kit.py OUTDIR --week-start YYYY-MM-DD --og assets/social/og.png`
- `tools/social/make_fox_og.py` — renders the Fox page’s evergreen link-preview image (`assets/social/og-fox.png`); only needs re-running if the design changes.
- `tools/make_ics.py` — rebuilds the iCal files: `python3 tools/make_ics.py fox/index.html fox/ics fox/fox.ics YEAR MONTH` (add `tiff` or `revue` as a sixth argument for those pages)
- `tools/social/make_tiff_og.py` — the TIFF page’s evergreen link-preview image (`assets/social/og-tiff.png`).
- `tools/social/make_revue_og.py` — the Revue page’s evergreen link-preview image (`assets/social/og-revue.png`).

Both pages are refreshed by scheduled Claude tasks: the Fox page every Monday, the Radar on the 1st of each month.

All internal links are root-relative (`/...`). The site is served from the custom domain in `CNAME` (cultureradar.to).
