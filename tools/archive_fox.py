"""Snapshot the current Fox Theatre page into the archive and rebuild the archive index.

Run from the repo root after every weekly refresh of fox/index.html:
    python3 tools/archive_fox.py

- Reads the "Listings as of <Mon D, YYYY>" date from the intro.
- Writes fox/archive/YYYY-MM-DD/index.html plus a copy of that week's iCal files
  (overwrites that week's snapshot if re-run).
- The snapshot shows every day of its window (no hiding past days), drops the
  live subscribe link, and links back to the current week.
- Rebuilds fox/archive/index.html from every week folder present.
"""
import os, re, html, shutil
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "/"
FOX = os.path.join(ROOT, "fox", "index.html")
ARCH = os.path.join(ROOT, "fox", "archive")

BANNER_CSS = (".archived{margin:0 0 10px;font-family:var(--f-mono);font-size:12px;letter-spacing:.04em;"
              "text-transform:uppercase;color:var(--muted)}.archived a{color:var(--accent)}")


def info(page):
    d = re.search(r"Listings as of ([A-Z][a-z]{2} \d{1,2}, \d{4})", page)
    r = re.search(r"<h1>The Fox <span>([^<]+)</span></h1>", page)
    if not d or not r:
        raise SystemExit("Could not find the listings date or the date range on fox/index.html")
    when = datetime.strptime(d.group(1), "%b %d, %Y")
    return when, r.group(1)


def snapshot(page, when, rng):
    label = when.strftime("%B %-d, %Y")
    page = page.replace("<title>Fox Theatre Calendar</title>", f"<title>Fox Theatre Calendar, week of {label}</title>")
    page = page.replace("</style>", BANNER_CSS + "\n</style>", 1)
    page = re.sub(r'<p class="subscribe">.*?</p>\n?', "", page, count=1, flags=re.S)
    page = re.sub(r"const todayNum=.*?;", "const todayNum=null;", page, count=1)
    page = page.replace('"fox-filter"', '"fox-arch-filter"')
    banner = (f'<p class="archived">Archived week · listings as of {html.escape(label)} · '
              f'<a href="{BASE}fox/">Current week →</a> · <a href="{BASE}fox/archive/">All weeks</a></p>')
    page = re.sub(r'(<p class="home">.*?</p>)', r"\1\n  " + banner, page, count=1, flags=re.S)
    return page


def build_index(current):
    weeks = []
    for slug in sorted(os.listdir(ARCH), reverse=True):
        f = os.path.join(ARCH, slug, "index.html")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", slug) or not os.path.exists(f):
            continue
        page = open(f, encoding="utf8").read()
        when, rng = info(page)
        n = len(re.findall(r'"\d{1,2}:\d{2} [a-z0-9-]+(?: !)?"', page))
        weeks.append((slug, when, rng, n))
    rows = []
    for slug, when, rng, n in weeks:
        cur = ' <span class="cur">Current</span>' if slug == current else ""
        rows.append(f'<a class="ed" href="{BASE}fox/archive/{slug}/"><span class="mo">{html.escape(rng)}{cur}</span>'
                    f'<span class="ct">{n} screenings</span><span class="pk">Listings as of {when.strftime("%B %-d, %Y")}</span></a>')
    tpl = open(os.path.join(ROOT, "tools", "archive_index_template.html"), encoding="utf8").read()
    out = (tpl.replace("<title>Radar Archive</title>", "<title>Fox Archive</title>")
              .replace('content="Every past edition of Culture Radar T.O."', 'content="Every past week of the Fox Theatre calendar."')
              .replace("<h1>Radar <span>Archive</span></h1>", "<h1>The Fox <span>Archive</span></h1>")
              .replace("Every edition of Culture Radar T.O., kept as it stood at the end of its month.",
                       "Every weekly Fox Theatre calendar, kept as it stood when it was published. Each week covers the four weeks from its listing date.")
              .replace(f'href="{BASE}">Current edition →', f'href="{BASE}fox/">Current week →')
              .replace("A new edition is added at the start of each month.", "A new week is added every Monday.")
              .replace("{{EDITIONS}}", "\n".join(rows)))
    open(os.path.join(ARCH, "index.html"), "w", encoding="utf8").write(out)
    return len(weeks)


def main():
    page = open(FOX, encoding="utf8").read()
    when, rng = info(page)
    slug = when.strftime("%Y-%m-%d")
    dest = os.path.join(ARCH, slug)
    os.makedirs(dest, exist_ok=True)
    open(os.path.join(dest, "index.html"), "w", encoding="utf8").write(snapshot(page, when, rng))
    src_ics = os.path.join(ROOT, "fox", "ics")
    if os.path.isdir(src_ics):
        shutil.rmtree(os.path.join(dest, "ics"), ignore_errors=True)
        shutil.copytree(src_ics, os.path.join(dest, "ics"))
    n = build_index(slug)
    print(f"Archived Fox week of {slug} -> fox/archive/{slug}/ ({n} weeks in archive)")


if __name__ == "__main__":
    main()
