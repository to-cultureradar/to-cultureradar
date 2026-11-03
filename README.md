# Culture Calendar

A small static site, published with GitHub Pages at https://safetydept.github.io/Culture-calendar/

- `index.html` — home page linking the two calendars
- `fox/index.html` — Fox Theatre screenings for the next four weeks. Data lives in the `F` (films) and `S` (schedule) objects in the page script.
- `fox/ics/` and `fox/fox.ics` — iCal files, one per showing plus a subscribable feed. Generated from the page data; never edit by hand.
- `radar/index.html` — T.O. Culture Radar, a monthly list of picks. Data lives in the `E` array in the page script; the masthead’s `.issue` block holds the edition month and date. Picks, tabs, counts, and sections are all built from `E`.
- `assets/fonts.css` + `assets/fonts/` — self-hosted typefaces (Archivo, Newsreader, IBM Plex Mono; SIL Open Font License) shared by every page.
- `tools/make_ics.py` — rebuilds the iCal files: `python3 tools/make_ics.py fox/index.html fox/ics fox/fox.ics YEAR MONTH`

Both pages are refreshed by scheduled Claude tasks: the Fox page every Monday, the Radar on the 1st of each month.
