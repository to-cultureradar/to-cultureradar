"""Render the TIFF Lightbox page's 1200×630 link-preview image (Open Graph). Evergreen: no dates or counts.

    python3 tools/social/make_fox_og.py            # writes assets/social/og-tiff.png

Uses the Fox page's own palette. Only needs re-running if the design changes.
"""
import os, re, html, asyncio

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FONTS = os.path.join(ROOT, "assets", "fonts")
OUT = os.path.join(ROOT, "assets", "social", "og-tiff.png")
BG, SURFACE, INK, MUTED, LINE, ACCENT, SOFT = "#f3f4f1", "#fdfdfb", "#191c1c", "#5f6866", "#d9dedb", "#0b6b63", "#dcefeb"

def data():
    page = open(os.path.join(ROOT, "tiff", "index.html"), encoding="utf8").read()
    rng = re.search(r"<h1>TIFF Lightbox <span>([^<]+)</span></h1>", page).group(1)
    shows = re.findall(r'"\d\d:\d\d ([a-z0-9-]+)(?: !)?"', page)
    return rng, len(set(shows)), len(shows)

def doc(rng, films, shows):
    css = f"""
@font-face{{font-family:Archivo;src:url(file://{FONTS}/archivo-latin-wdth-normal.woff2);font-weight:100 900;font-stretch:62% 125%}}
@font-face{{font-family:Newsreader;src:url(file://{FONTS}/newsreader-latin-opsz-normal.woff2);font-weight:200 800}}
@font-face{{font-family:Plex;src:url(file://{FONTS}/ibm-plex-mono-latin-500-normal.woff2);font-weight:500}}
*{{box-sizing:border-box;margin:0}}
body{{width:1200px;height:630px;background:{BG};color:{INK};font-family:Newsreader,serif;overflow:hidden;position:relative}}
.mono{{font-family:Plex,monospace;font-weight:500;font-size:20px;letter-spacing:.06em;text-transform:uppercase}}
.disp{{font-family:Archivo;font-stretch:62%;font-weight:800;text-transform:uppercase;line-height:.86}}
.chip{{display:inline-block;font-family:Archivo;font-stretch:85%;font-weight:700;font-size:22px;letter-spacing:.04em;text-transform:uppercase;padding:10px 16px;border:2px solid {LINE};background:{SURFACE}}}
.chip.on{{background:{ACCENT};border-color:{ACCENT};color:#fff}}
"""
    body = f"""
<div style='position:absolute;left:0;top:0;bottom:0;width:22px;background:{ACCENT}'></div>
<div style='position:absolute;inset:52px 60px 48px 82px;display:flex;flex-direction:column'>
  <div class=mono style='color:{MUTED};display:flex;justify-content:space-between'><span>350 King St. W · Toronto</span><span>Updated Mondays</span></div>
  <div class=disp style='font-size:170px;margin-top:40px'>TIFF Lightbox</div>
  <div class=disp style='font-size:150px;color:{ACCENT};margin-top:6px'>Every screening</div>
  <div style='font-size:34px;margin-top:26px;color:{INK}'>The next four weeks, with directors, series, and calendar links.</div>
  <div style='margin-top:auto;display:flex;gap:10px;align-items:center'>
    <span class='chip on'>Everything</span><span class=chip>Cinematheque</span><span class=chip>New releases</span>
    <span class=mono style='margin-left:auto;color:{INK}'>cultureradar.to/tiff</span>
  </div>
</div>"""
    return f"<!doctype html><html><head><meta charset=utf-8><style>{css}</style></head><body>{body}</body></html>"

async def render(path, d):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        exe = "/usr/bin/google-chrome" if os.path.exists("/usr/bin/google-chrome") else None
        b = await p.chromium.launch(executable_path=exe, args=["--no-sandbox", "--allow-file-access-from-files"])
        tmp = path + ".html"; open(tmp, "w", encoding="utf8").write(d)
        pg = await b.new_page(viewport={"width": 1200, "height": 630})
        await pg.goto("file://" + tmp); await pg.wait_for_timeout(400)
        await pg.screenshot(path=path); os.remove(tmp); await b.close()

if __name__ == "__main__":
    rng, films, shows = data()  # kept for reference; the card itself is evergreen
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    asyncio.run(render(OUT, doc(rng, films, shows)))
    print(f"TIFF preview (evergreen) -> {OUT}")
