"""Copy the current Culture Radar T.O. edition into the archive and rebuild the archive index.

Run from the repo root after every change to index.html (the Radar, served at the site root):
    python3 tools/archive_radar.py

- Reads the edition month from the `.issue` block (<strong>November 2026</strong>).
- Writes radar/archive/YYYY-MM/index.html (overwrites that month's copy, so the
  archive always holds the final version of each month).
- Rebuilds radar/archive/index.html from every month folder present.
"""
import os
import re
import html
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "/"
RADAR = os.path.join(ROOT, "index.html")
ARCH = os.path.join(ROOT, "radar", "archive")

BANNER_CSS = (
    ".archived{margin:0;padding-block:10px;border-bottom:1px solid var(--rule);"
    "font-family:var(--f-mono);font-size:12px;letter-spacing:.04em;text-transform:uppercase;color:var(--soft)}"
    ".archived a{color:var(--accent)}"
)


def month_of(page):
    m = re.search(r'class="issue[^"]*"><strong>([A-Z][a-z]+ \d{4})</strong>', page)
    if not m:
        raise SystemExit("No edition month found in the .issue block")
    label = m.group(1)
    return label, datetime.strptime(label, "%B %Y").strftime("%Y-%m")


def stats(page):
    rows = re.findall(r'^ \["(film|art|music|theatre)","[^"]*","([^"]*)".*?,\[([^\]]*)\]\],?$', page, re.M)
    picks = [t for _, t, tags in rows if '"pick"' in tags]
    return len(rows), picks


def archive_copy(page, label):
    page = page.replace("<title>Culture Radar Toronto</title>", f"<title>Culture Radar Toronto, {label}</title>")
    page = re.sub(r'<meta property="og:url"[^>]*>\n?', "", page)  # archived copies are not the canonical page
    page = page.replace("</style>", BANNER_CSS + "\n</style>", 1)
    banner = (
        f'<p class="archived">Archived edition · {html.escape(label)} · '
        f'<a href="{BASE}">Current edition →</a> · <a href="{BASE}radar/archive/">All editions</a></p>'
    )
    page = re.sub(r'(<div class="topbar">.*?</div>)', r"\1\n" + banner, page, count=1, flags=re.S)
    # keep per-edition filter memory separate from the live page
    page = page.replace('"radar-cat"', '"radar-arch-cat"').replace('"radar-free"', '"radar-arch-free"')
    return page


def build_index(current_slug):
    eds = []
    for slug in sorted(os.listdir(ARCH), reverse=True):
        f = os.path.join(ARCH, slug, "index.html")
        if not re.fullmatch(r"\d{4}-\d{2}", slug) or not os.path.exists(f):
            continue
        page = open(f, encoding="utf8").read()
        label, _ = month_of(page)
        n, picks = stats(page)
        eds.append((slug, label, n, picks))
    items = []
    for slug, label, n, picks in eds:
        cur = ' <span class="cur">Current</span>' if slug == current_slug else ""
        pk = ", ".join(html.escape(p) for p in picks[:4]) + ("…" if len(picks) > 4 else "")
        items.append(
            f'<a class="ed" href="{BASE}radar/archive/{slug}/"><span class="mo">{html.escape(label)}{cur}</span>'
            f'<span class="ct">{n} listings</span><span class="pk">Picks: {pk}</span></a>'
        )
    tpl = open(os.path.join(ROOT, "tools", "archive_index_template.html"), encoding="utf8").read()
    out = tpl.replace("{{EDITIONS}}", "\n".join(items))
    open(os.path.join(ARCH, "index.html"), "w", encoding="utf8").write(out)
    return len(eds)


def main():
    page = open(RADAR, encoding="utf8").read()
    label, slug = month_of(page)
    os.makedirs(os.path.join(ARCH, slug), exist_ok=True)
    open(os.path.join(ARCH, slug, "index.html"), "w", encoding="utf8").write(archive_copy(page, label))
    n = build_index(slug)
    print(f"Archived {label} -> radar/archive/{slug}/ ({n} editions in archive)")


if __name__ == "__main__":
    main()
