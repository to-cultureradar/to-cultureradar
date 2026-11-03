"""Render the Instagram kit for the current Culture Radar T.O. edition.

    python3 tools/social/make_kit.py OUTDIR [--week-start YYYY-MM-DD] [--og assets/social/og.png]

Reads the picks and listings from index.html (the Radar) and writes:
  OUTDIR/feed-00-cover.png … feed-NN-*.png   (1080×1350 carousel: cover, one slide per pick, closing slide)
  OUTDIR/story-this-week.png                  (1080×1920, events in the 7 days from --week-start)
  OUTDIR/caption.txt                          (carousel caption)
  --og PATH                                   (1200×630 evergreen link-preview image; the site uses assets/social/og.png)
Needs Playwright with a Chromium/Chrome binary.
"""
import os, re, sys, json, html, asyncio, datetime as dt

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FONTS = os.path.join(ROOT, "assets", "fonts")
MON = {m: i for i, m in enumerate(["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"], 1)}
CAT = {"film": "Film", "art": "Art", "music": "Music", "theatre": "Theatre"}

def load():
    page = open(os.path.join(ROOT, "index.html"), encoding="utf8").read()
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

HANDLE = "@cultureradar.to"
SITE = "cultureradar.to"
# 90s alt-weekly look: newsprint, halftone, misregistered spot colour, one bright ink per section
INK = {"film": "#ff2e88", "art": "#ffd600", "music": "#00b2ff", "theatre": "#ff5a1f"}
PAPER, BLACK = "#f3eddc", "#111111"

CSS = f"""
@font-face{{font-family:Archivo;src:url(file://{FONTS}/archivo-latin-wdth-normal.woff2);font-weight:100 900;font-stretch:62% 125%}}
@font-face{{font-family:Newsreader;src:url(file://{FONTS}/newsreader-latin-opsz-normal.woff2);font-weight:200 800}}
@font-face{{font-family:Plex;src:url(file://{FONTS}/ibm-plex-mono-latin-500-normal.woff2);font-weight:500}}
*{{box-sizing:border-box;margin:0}}
body{{width:var(--w);height:var(--h);background:var(--bg,{PAPER});color:{BLACK};font-family:Newsreader,serif;overflow:hidden;position:relative}}
.dots{{position:absolute;inset:0;background-image:radial-gradient(rgba(0,0,0,.16) 2px,transparent 2.4px);background-size:14px 14px}}
.dots.fade{{-webkit-mask-image:linear-gradient(160deg,#000 0,transparent 45%);mask-image:linear-gradient(160deg,#000 0,transparent 45%)}}
.frame{{position:absolute;inset:56px;display:flex;flex-direction:column}}
.mono{{font-family:Plex,monospace;font-weight:500;font-size:24px;letter-spacing:.06em;text-transform:uppercase}}
.strip{{display:flex;justify-content:space-between;background:{BLACK};color:{PAPER};padding:12px 18px}}
.mast{{font-family:Archivo;font-stretch:62%;font-weight:900;text-transform:uppercase;line-height:.82;letter-spacing:-.01em}}
.mis{{text-shadow:7px 7px 0 var(--c)}}
.title{{font-family:Archivo;font-stretch:75%;font-weight:900;line-height:.95;text-transform:uppercase;text-wrap:balance}}
.rule{{border-top:8px solid {BLACK}}}
.thin{{border-top:3px solid {BLACK}}}
.stamp{{display:inline-block;background:{BLACK};color:var(--c);padding:18px 26px 10px;transform:rotate(-2.5deg);box-shadow:10px 10px 0 var(--c)}}
.hl{{display:inline;background:var(--c);box-decoration-break:clone;-webkit-box-decoration-break:clone;padding:2px 8px}}
.burst{{position:absolute;display:grid;place-items:center;text-align:center;background:var(--c2,#ffd600);color:{BLACK};
  clip-path:polygon(50% 0,61% 15%,79% 6%,80% 25%,98% 25%,89% 41%,100% 54%,85% 63%,90% 82%,71% 81%,62% 98%,50% 86%,37% 98%,29% 81%,10% 82%,15% 63%,0 54%,11% 41%,2% 25%,20% 25%,21% 6%,39% 15%)}}
.stub{{border:4px dashed {BLACK};padding:18px 24px;display:flex;justify-content:space-between;align-items:center}}
.foot{{margin-top:auto}}
"""

def shell(w, h, body, bg=PAPER, c="#ff2e88", dots="dots"):
    return (f"<!doctype html><html><head><meta charset=utf-8><style>:root{{--w:{w}px;--h:{h}px;--bg:{bg};--c:{c}}}{CSS}</style></head>"
            f"<body><div class='{dots}'></div>{body}</body></html>")

def issue_no(month):
    d = dt.datetime.strptime(month, "%B %Y")
    return (d.year - 2026) * 12 + d.month - 10  # Nov 2026 = No. 1

def cover(month, n):
    mname = month.split()[0]
    chips = "".join(f"<span class=mono style='background:{INK[k]};padding:10px 16px;border:3px solid {BLACK}'>{CAT[k]}</span>" for k in CAT)
    return shell(1080, 1350, f"""<div class=frame>
<div class='strip mono'><span>Toronto · Free</span><span>No. {issue_no(month)} · {html.escape(month)}</span></div>
<div class='mast mis' style='font-size:300px;margin-top:44px;--c:{INK["film"]}'>Culture</div>
<div class='mast mis' style='font-size:300px;color:{PAPER};-webkit-text-stroke:6px {BLACK};--c:{BLACK}'>Radar</div>
<div class=mast style='font-size:130px;margin-top:22px'><span style='display:inline-block;background:{INK["film"]};border:6px solid {BLACK};padding:14px 22px 2px;transform:rotate(-2deg);box-shadow:9px 9px 0 {BLACK}'>T.O.</span></div>
<div class=rule style='margin-top:36px'></div>
<div style='font-size:46px;line-height:1.2;margin-top:22px;max-width:19ch;font-weight:600'>What’s on in {html.escape(mname)}: film, art, music, and theatre.</div>
<div class=foot style='display:flex;gap:14px;flex-wrap:wrap'>{chips}</div>
<div class='mono' style='margin-top:22px;display:flex;justify-content:space-between'><span>{HANDLE}</span><span>Swipe →</span></div></div>
<div class='burst mast' style='width:330px;height:330px;right:60px;top:830px;transform:rotate(12deg);--c2:{INK["music"]};font-size:76px;line-height:.85'>{n}<br>picks</div>""",
        bg=INK["art"])

def pick(r, i, n, month):
    cat, when, title, where, desc = r[0], r[1], r[2], r[3], r[4]
    c = INK[cat]
    m = re.match(r"^To (.+)$", when)
    big = ("Until " + m.group(1)) if m else when
    venue = where.split(" · ")
    return shell(1080, 1350, f"""<div class=frame>
<div class='strip mono'><span>{CAT[cat]}</span><span>Pick {i:02d}/{n:02d} · {html.escape(month)}</span></div>
<div style='margin-top:54px'><span class='stamp mast' style='font-size:{150 if len(big)<8 else 108}px'>{html.escape(big)}</span></div>
<div class='title' style='font-size:{100 if len(title)<26 else 80 if len(title)<44 else 64}px;margin-top:60px'>{html.escape(title)}</div>
<div class=mono style='margin-top:28px;font-size:26px;line-height:1.7'><span class=hl>{html.escape(where)}</span></div>
<div class=thin style='margin-top:34px'></div>
<div style='font-size:42px;line-height:1.3;margin-top:24px;max-width:27ch'>{html.escape(desc)}</div>
<div class='foot mast' style='font-size:210px;color:{c};-webkit-text-stroke:5px {BLACK};margin-bottom:18px;line-height:.8'>{CAT[cat]}</div>
<div class='stub mono'><span>Tickets & details</span><span>{SITE}</span></div></div>""",
        c=c, dots="dots fade")

def closing(month, total):
    return shell(1080, 1350, f"""<div class=frame>
<div class='strip mono'><span>{html.escape(month)}</span><span>Toronto · Free</span></div>
<div class='mast mis' style='font-size:330px;margin-top:60px;--c:{INK["art"]}'>+{total}</div>
<div class='mast' style='font-size:150px'>more listings</div>
<div class=rule style='margin-top:36px'></div>
<div style='font-size:46px;line-height:1.25;margin-top:24px;max-width:21ch;font-weight:600'>Repertory and experimental film, exhibitions, concerts, and theatre, with ticket links.</div>
<div class='foot' style='background:{BLACK};color:{INK["art"]};padding:26px 30px;display:flex;justify-content:space-between;align-items:baseline'>
<span class=mast style='font-size:84px;text-transform:lowercase'>{SITE}</span><span class=mono style='color:{PAPER}'>Link in bio</span></div></div>""",
        bg=INK["film"])

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
        f"<div style='padding:22px 0;border-bottom:3px solid {BLACK};display:grid;grid-template-columns:210px 1fr;gap:24px;align-items:start'>"
        f"<div class=mast style='background:{INK[r[0]]};border:3px solid {BLACK};padding:10px 12px 4px;font-size:{40 if '–' in r[1] else 56}px;white-space:nowrap;text-align:center'>{html.escape(r[1])}</div>"
        f"<div><div class=title style='font-size:44px'>{html.escape(r[2])}</div>"
        f"<div class=mono style='font-size:20px;margin-top:10px'>{html.escape(r[3].split(' · ')[0])}{' · <b>Sold out</b>' if 'sold' in r[6] else ''}</div></div></div>"
        for r in wk)
    rng = f"{start.strftime('%b')} {start.day}–{end.day}" if start.month == end.month else f"{start.strftime('%b')} {start.day}–{end.strftime('%b')} {end.day}"
    legend = "".join(f"<span style='display:inline-flex;align-items:center;gap:8px'><i style='width:22px;height:22px;background:{INK[k]};border:3px solid {BLACK};display:inline-block'></i>{CAT[k]}</span>" for k in CAT)
    return shell(1080, 1920, f"""<div class=frame style='inset:110px 56px'>
<div class='strip mono'><span>{HANDLE}</span><span>{rng}</span></div>
<div class='mast mis' style='font-size:230px;margin-top:34px;--c:{INK["film"]}'>This week</div>
<div class=rule style='margin:26px 0 4px'></div>
{items}
<div class='mono foot' style='display:flex;gap:26px;font-size:20px'>{legend}</div>
<div class='mono' style='margin-top:22px;background:{BLACK};color:{INK["art"]};padding:16px 20px;display:flex;justify-content:space-between'><span>Tickets</span><span>{SITE}</span></div></div>""",
        dots="dots fade"), len(wk)

def og_card(month=None, n=None):
    """1200×630 link-preview image (Open Graph), same look as the cover. Evergreen: no month or count."""
    chips = "".join(f"<span class=mono style='background:{INK[k]};padding:8px 14px;border:3px solid {BLACK};font-size:20px'>{CAT[k]}</span>" for k in CAT)
    return shell(1200, 630, f"""<div class=frame style='inset:44px 52px'>
<div class='strip mono' style='font-size:20px'><span>Toronto · Free</span><span>New edition on the 1st</span></div>
<div style='display:flex;align-items:flex-end;gap:26px;margin-top:30px'>
<div><div class='mast mis' style='font-size:190px;--c:{INK["film"]}'>Culture</div>
<div class='mast mis' style='font-size:190px;color:{PAPER};-webkit-text-stroke:5px {BLACK};--c:{BLACK}'>Radar</div></div>
<div class=mast style='font-size:110px;margin-bottom:6px'><span style='display:inline-block;background:{INK["film"]};border:5px solid {BLACK};padding:10px 18px 0;transform:rotate(-2deg);box-shadow:8px 8px 0 {BLACK}'>T.O.</span></div></div>
<div class=foot style='display:flex;gap:12px;align-items:center'>{chips}<span class=mono style='margin-left:auto;font-size:22px'>{SITE}</span></div></div>
<div class='burst mast' style='width:240px;height:240px;right:40px;top:105px;transform:rotate(12deg);--c2:{INK["music"]};font-size:46px;line-height:.88'>Monthly<br>picks</div>""",
        bg=INK["art"])

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
    if "--og" in sys.argv:
        jobs.append((os.path.abspath(sys.argv[sys.argv.index("--og") + 1]), og_card(month, len(picks)), 1200, 630))
    if ws:
        doc, n = story(rows, ws); jobs.append((os.path.join(out, "story-this-week.png"), doc, 1080, 1920))
    asyncio.run(render(jobs))
    cap = [f"Culture Radar T.O., {month}. {len(picks)} picks:", ""]
    for r in picks:
        cap.append(f"{r[1]} · {r[2]} · {r[3].split(' · ')[0]}")
    cap += ["", f"Plus {len(rows) - len(picks)} more listings across film, art, music, and theatre, with ticket links. Link in bio.", "", f"Full guide: {SITE}", "", "#toronto #torontofilm #torontoart #torontoevents"]
    open(os.path.join(out, "caption.txt"), "w", encoding="utf8").write("\n".join(cap) + "\n")
    print(f"{len(jobs)} images + caption -> {out}")

if __name__ == "__main__":
    main()
