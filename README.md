# Culture Calendar

A small static site, published with GitHub Pages at https://cultureradar.to/

- `index.html` — home page linking the two calendars
- `fox/index.html` — Fox Theatre screenings for the next four weeks. Data lives in the `F` (films) and `S` (schedule) objects in the page script.
- `fox/ics/` and `fox/fox.ics` — iCal files, one per showing plus a subscribable feed. Generated from the page data; never edit by hand.
- `radar/index.html` — T.O. Culture Radar, a monthly list of picks. Data lives in the `E` array in the page script; the masthead’s `.issue` block holds the edition month and date. Picks, tabs, counts, and sections are all built from `E`.
- `assets/fonts.css` + `assets/fonts/` — self-hosted typefaces (Archivo, Newsreader, IBM Plex Mono; SIL Open Font License) shared by every page.
- `radar/archive/` — one folder per edition (`YYYY-MM/`) plus an index. Generated; never edit by hand.
- `tools/archive_radar.py` — run after every change to `radar/index.html`: copies the edition into `radar/archive/<month>/` and rebuilds the archive index (`python3 tools/archive_radar.py`).
- `fox/archive/` — one folder per weekly Fox snapshot (`YYYY-MM-DD/`, with its iCal files) plus an index. Generated; never edit by hand.
- `tools/archive_fox.py` — run after every weekly refresh of `fox/index.html` (`python3 tools/archive_fox.py`).
- `tools/make_ics.py` — rebuilds the iCal files: `python3 tools/make_ics.py fox/index.html fox/ics fox/fox.ics YEAR MONTH`

Both pages are refreshed by scheduled Claude tasks: the Fox page every Monday, the Radar on the 1st of each month.

All internal links are root-relative (`/...`). The site is served from the custom domain in `CNAME` (cultureradar.to).
