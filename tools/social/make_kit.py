"""Render the Instagram kit for the current T.O. Culture Radar edition.

    python3 tools/social/make_kit.py OUTDIR [--week-start YYYY-MM-DD]

Reads the picks and listings from radar/index.html and writes:
  OUTDIR/feed-00-cover.png … feed-NN-*.png   (1080×1350 carousel: cover, one slide per pick, closing slide)
  OUTDIR/story-this-week.png                  (1080×1920, events in the 7 days from --week-start)
  OUTDIR/caption.txt                          (carousel caption)
Needs Playwright with a Chromium/Chrome binary.
"""
import os, re, sys, json, html, asyncio, datetime as dt

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FONTS = os.path.join(ROOT, "assets", "fonts")
MON = {m: i for i, m in enumerate(["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"], 1)}
CAT = {"film": "Film", "art": "Art", "music": "Music", "theatre": "Theatre"}

def load():
    page = open(os.path.join(ROOT, "radar", "index.html"), encoding="utf8").read()
    month = re.search(r'class="issue[^"]*"><strong>([A-Z][a-z]+ \d{4})</strong>', page).group(1)
    rows = []
    for m in re.finditer(r'^ (\["(?:film|art|music|theatre)".*\]),?$', page, re.M):
        line = re.sub(r",SRC\.\w+,", ',"",', m.group(1))
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return month, rows

def key(w, year):
    m = re.match(r"([A-Z][a-z]{2}) (\d+)", w)
    if not m:
        return 0
    mo = MON[m.group(1)]
    return (mo + 12 if mo < 6 else mo) * 100 + int(m.group(2))

CSS = f"""
@font-face{{font-family:Archivo;src:url(file://{FONTS}/archivo-latin-wdth-normal.woff2);font-weight:100 900;font-stretch:62% 125%}}
@font-face{{font-family:Newsreader;src:url(file://{FONTS}/newsreader-latin-opsz-normal.woff2);font-weight:200 800}}
@font-face{{font-family:Plex;src:url(file://{FONTS}/ibm-plex-mono-latin-400-normal.woff2);font-weight:400}}
*{{box-sizing:border-box;margin:0}}
body{{width:var(--w);height:var(--h);background:#fafaf7;color:#15171a;font-family:Newsreader,serif;overflow:hidden}}
.dark body,body.dark{{background:#111214;color:#ecebe6}}
.frame{{position:absolute;inset:64px;display:flex;flex-direction:column}}
.mono{{font-family:Plex,monospace;font-size:26px;letter-spacing:.08em;text-transform:uppercase}}
.soft{{color:#5d6168}} body.dark .soft{{color:#9a9ca1}}
.blue{{color:#2340c8}} body.dark .blue{{color:#9cb0ff}}
.mast{{font-family:Archivo;font-stretch:62%;font-weight:900;text-transform:uppercase;line-height:.84}}
.rule{{border-top:6px solid currentColor;margin:28px 0}}
.hair{{border-top:2px solid #dcdcd5}} body.dark .hair{{border-color:#2c2e32}}
.title{{font-family:Archivo;font-stretch:80%;font-weight:800;line-height:1.02;text-wrap:balance}}
.flag{{display:inline-block;font-family:Plex,monospace;font-size:22px;letter-spacing:.08em;text-transform:uppercase;padding:4px 12px;background:#2340c8;color:#fff}}
body.dark .flag{{background:#9cb0ff;color:#111214}}
.foot{{margin-top:auto;display:flex;justify-content:space-between;align-items:baseline}}
"""

def shell(w, h, body, dark=False):
    return f"<!doctype html><html><head><meta charset=utf-8><style>:root{{--w:{w}px;--h:{h}px}}{CSS}</style></head><body class='{'dark' if dark else ''}'>{body}</body></html>"

def cover(month, n):
    mname = month.split()[0]
    return shell(1080, 1350, f"""<div class=frame>
<div class='mono soft'>Toronto · {html.escape(month)}</div>
<div class=rule></div>
<div class=mast style='font-size:250px'>T.O.<br>Culture<br><span class=blue>Radar</span></div>
<div class=rule></div>
<div style='font-size:46px;line-height:1.25;max-width:22ch'>{n} picks for {html.escape(mname)}: film, art, music, and theatre.</div>
<div class='foot mono soft'><span>@to.cultureradar</span><span>Swipe →</span></div></div>""")

def pick(r, i, n, month):
    cat, when, title, where, desc = r[0], r[1], r[2], r[3], r[4]
    m = re.match(r"^To (.+)$", when)
    big = ("Until " + m.group(1)) if m else when
    return shell(1080, 1350, f"""<div class=frame>
<div class='mono soft' style='display:flex;justify-content:space-between'><span>{CAT[cat]}</span><span>{i:02d} / {n:02d}</span></div>
<div class=rule></div>
<div class='mast blue' style='font-size:{150 if len(big)<9 else 112}px'>{html.escape(big)}</div>
<div class=title style='font-size:{84 if len(title)<34 else 66}px;margin-top:44px'>{html.escape(title)}</div>
<div class='mono soft' style='margin-top:26px;font-size:24px;line-height:1.5'>{html.escape(where)}</div>
<div style='font-size:40px;line-height:1.32;margin-top:36px;max-width:26ch'>{html.escape(desc)}</div>
<div class='foot mono soft'><span>T.O. Culture Radar · {html.escape(month)}</span><span>Pick</span></div></div>""")

def closing(month, total):
    return shell(1080, 1350, f"""<div class=frame>
<div class='mono soft'>{html.escape(month)}</div>
<div class=rule></div>
<div class=mast style='font-size:170px'>{total} more<br>listings<br><span class=blue>online</span></div>
<div class=rule></div>
<div style='font-size:46px;line-height:1.3;max-width:22ch'>Repertory and experimental film, exhibitions, concerts, and theatre, with ticket links.</div>
<div class='foot mono soft'><span>Link in bio</span><span>@to.cultureradar</span></div></div>""", dark=True)

def story(rows, start):
    end = start + dt.timedelta(days=6)
    def in_week(w):
        m = re.match(r"([A-Z][a-z]{2}) (\d+)(?:–(\d+))?", w)
        if not m: return False
        d0 = dt.date(start.year, MON[m.group(1)], int(m.group(2)))
        d1 = dt.date(start.year, MON[m.group(1)], int(m.group(3))) if m.group(3) else d0
        return d0 <= end and d1 >= start
    wk = sorted([r for r in rows if in_week(r[1])], key=lambda r: key(r[1], start.year))[:8]
    items = "".join(
        f"<div class=hair style='padding:26px 0;display:grid;grid-template-columns:200px 1fr;gap:24px'>"
        f"<div class='mast blue' style='font-size:{44 if '–' in r[1] else 64}px;white-space:nowrap'>{html.escape(r[1])}</div>"
        f"<div><div class=title style='font-size:42px'>{html.escape(r[2])}</div>"
        f"<div class='mono soft' style='font-size:20px;margin-top:8px'>{html.escape(r[3].split(' · ')[0])}{' · sold out' if 'sold' in r[6] else ''}</div></div></div>"
        for r in wk)
    rng = f"{start.strftime('%b')} {start.day}–{end.day}" if start.month == end.month else f"{start.strftime('%b')} {start.day}–{end.strftime('%b')} {end.day}"
    return shell(1080, 1920, f"""<div class=frame style='inset:120px 64px'>
<div class='mono soft'>@to.cultureradar</div>
<div class=rule></div>
<div class=mast style='font-size:190px'>This<br><span class=blue>week</span></div>
<div class='mono soft' style='margin:18px 0 30px'>{rng}</div>
{items}
<div class='foot mono soft'><span>Tickets: link in bio</span></div></div>""", dark=True), len(wk)

async def render(jobs):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        exe = "/usr/bin/google-chrome" if os.path.exists("/usr/bin/google-chrome") else None
        b = await p.chromium.launch(executable_path=exe, args=["--no-sandbox", "--allow-file-access-from-files"])
        for path, doc, w, h in jobs:
            tmp = path + ".html"
            open(tmp, "w", encoding="utf8").write(doc)
            pg = await b.new_page(viewport={"width": w, "height": h})
            await pg.goto("file://" + tmp); await pg.wait_for_timeout(400)
            await pg.screenshot(path=path); await pg.close(); os.remove(tmp)
        await b.close()

def main():
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    month, rows = load()
    ws = None
    if "--week-start" in sys.argv:
        ws = dt.date.fromisoformat(sys.argv[sys.argv.index("--week-start") + 1])
    picks = sorted([r for r in rows if "pick" in r[6]], key=lambda r: key(r[1], 0))
    jobs = [(os.path.join(out, "feed-00-cover.png"), cover(month, len(picks)), 1080, 1350)]
    for i, r in enumerate(picks, 1):
        slug = re.sub(r"[^a-z0-9]+", "-", r[2].lower()).strip("-")[:40]
        jobs.append((os.path.join(out, f"feed-{i:02d}-{slug}.png"), pick(r, i, len(picks), month), 1080, 1350))
    jobs.append((os.path.join(out, f"feed-{len(picks)+1:02d}-more.png"), closing(month, len(rows) - len(picks)), 1080, 1350))
    if ws:
        doc, n = story(rows, ws); jobs.append((os.path.join(out, "story-this-week.png"), doc, 1080, 1920))
    asyncio.run(render(jobs))
    cap = [f"T.O. Culture Radar, {month}. {len(picks)} picks:", ""]
    for r in picks:
        cap.append(f"{r[1]} · {r[2]} · {r[3].split(' · ')[0]}")
    cap += ["", f"Plus {len(rows) - len(picks)} more listings across film, art, music, and theatre, with ticket links. Full guide: link in bio.", "", "#toronto #torontofilm #torontoart #torontoevents"]
    open(os.path.join(out, "caption.txt"), "w", encoding="utf8").write("\n".join(cap) + "\n")
    print(f"{len(jobs)} images + caption -> {out}")

if __name__ == "__main__":
    main()
