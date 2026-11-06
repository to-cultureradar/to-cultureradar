"""Render a weekend Instagram carousel (1080×1350) in the Culture Radar kit style.

    python3 tools/social/make_weekend.py WEEKEND.json OUTDIR

WEEKEND.json:
  {"range": "Nov 6–8",
   "days": [{"day": "Friday", "date": "Nov 6",
             "items": [{"cat": "music", "time": "Late", "title": "…", "where": "…", "note": "Free"}, …]}, …],
   "all_weekend": [{"cat": "theatre", "title": "…", "where": "…", "note": "To Nov 29"}, …],
   "caption": "…"}
Writes OUTDIR/weekend-00-cover.png, one slide per day, an "all weekend" slide, a closing slide, and caption.txt.
"""
import os, sys, json, html, asyncio
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_kit import shell, render, INK, CAT, BLACK, PAPER, HANDLE, SITE

E = html.escape

def cover(d):
    n = sum(len(x["items"]) for x in d["days"]) + len(d.get("all_weekend", []))
    chips = "".join(f"<span class=mono style='background:{INK[k]};padding:10px 16px;border:3px solid {BLACK}'>{CAT[k]}</span>"
                    for k in CAT if any(i["cat"] == k for x in d["days"] for i in x["items"]) or any(i["cat"] == k for i in d.get("all_weekend", [])))
    return shell(1080, 1350, f"""<div class=frame>
<div class='strip mono'><span>Culture Radar · Toronto</span><span>{E(d["range"])}</span></div>
<div class='mast mis' style='font-size:250px;margin-top:60px;--c:{INK["music"]}'>This</div>
<div class='mast mis' style='font-size:250px;color:{PAPER};-webkit-text-stroke:6px {BLACK};--c:{BLACK}'>weekend</div>
<div class=mast style='font-size:120px;margin-top:30px'><span style='display:inline-block;background:{INK["music"]};border:6px solid {BLACK};padding:14px 22px 2px;transform:rotate(-2deg);box-shadow:9px 9px 0 {BLACK}'>{E(d["range"])}</span></div>
<div class=rule style='margin-top:44px'></div>
<div style='font-size:46px;line-height:1.2;margin-top:22px;max-width:20ch;font-weight:600'>Club nights, 35mm noir, a birding walk, and a book fair.</div>
<div class=foot style='display:flex;gap:14px;flex-wrap:wrap'>{chips}</div>
<div class='mono' style='margin-top:22px;display:flex;justify-content:space-between'><span>{HANDLE}</span><span>Swipe →</span></div></div>
<div class='burst mast' style='width:300px;height:300px;right:70px;top:640px;transform:rotate(12deg);--c2:{INK["art"]};font-size:72px;line-height:.85'>{n}<br>things</div>""",
        bg=INK["film"])

def row(i, timecol=True):
    c = INK[i["cat"]]
    note = f" · <b>{E(i['note'])}</b>" if i.get("note") else ""
    left = (f"<div class=mast style='background:{c};border:3px solid {BLACK};padding:10px 8px 4px;font-size:{50 if len(i.get('time',''))<7 else 38}px;white-space:nowrap;text-align:center'>{E(i.get('time',''))}</div>"
            if timecol else f"<div style='background:{c};border:3px solid {BLACK};height:48px;margin-top:8px'></div>")
    t = i["title"]
    return (f"<div style='padding:30px 0;border-bottom:3px solid {BLACK};display:grid;grid-template-columns:190px 1fr;gap:28px;align-items:start'>{left}"
            f"<div><div class=title style='font-size:{58 if len(t)<30 else 46}px'>{E(t)}</div>"
            f"<div class=mono style='font-size:24px;margin-top:12px;line-height:1.4'>{E(i['where'])}{note}</div></div></div>")

def day_slide(x, k, n, rng):
    c = INK[x["items"][0]["cat"]]
    rows = "".join(row(i) for i in x["items"])
    return shell(1080, 1350, f"""<div class=frame>
<div class='strip mono'><span>{E(x["date"])}</span><span>This weekend · {k:02d}/{n:02d}</span></div>
<div class='mast mis' style='font-size:210px;margin-top:40px;--c:{c}'>{E(x["day"])}</div>
<div class=rule style='margin:22px 0 4px'></div>
{rows}
<div class='stub mono foot'><span>Tickets & details</span><span>{SITE}</span></div></div>""", c=c, dots="dots fade")

def all_weekend(items, k, n):
    rows = "".join(row(i, timecol=False) for i in items)
    return shell(1080, 1350, f"""<div class=frame>
<div class='strip mono'><span>Fri–Sun</span><span>This weekend · {k:02d}/{n:02d}</span></div>
<div class='mast mis' style='font-size:170px;margin-top:40px;--c:{INK["theatre"]}'>All weekend</div>
<div class=rule style='margin:22px 0 4px'></div>
{rows}
<div class='stub mono foot'><span>Tickets & details</span><span>{SITE}</span></div></div>""", c=INK["theatre"], dots="dots fade")

def closing():
    return shell(1080, 1350, f"""<div class=frame>
<div class='strip mono'><span>Culture Radar · Toronto</span><span>Every month</span></div>
<div class='mast mis' style='font-size:250px;margin-top:70px;--c:{INK["art"]}'>The full</div>
<div class='mast' style='font-size:250px'>guide</div>
<div class=rule style='margin-top:36px'></div>
<div style='font-size:46px;line-height:1.25;margin-top:24px;max-width:22ch;font-weight:600'>The month’s film, art, music, theatre, talks, and walks, plus every screening at the Fox, TIFF Lightbox, and the Revue.</div>
<div class='foot' style='background:{BLACK};color:{INK["art"]};padding:26px 30px;display:flex;justify-content:space-between;align-items:baseline'>
<span class=mast style='font-size:84px;text-transform:lowercase'>{SITE}</span><span class=mono style='color:{PAPER}'>Link in bio</span></div></div>""",
        bg=INK["music"])

def main():
    d = json.load(open(sys.argv[1], encoding="utf8")); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    n = len(d["days"]) + (1 if d.get("all_weekend") else 0)
    jobs = [(os.path.join(out, "weekend-00-cover.png"), cover(d), 1080, 1350)]
    for k, x in enumerate(d["days"], 1):
        jobs.append((os.path.join(out, f"weekend-{k:02d}-{x['day'].lower()}.png"), day_slide(x, k, n, d["range"]), 1080, 1350))
    if d.get("all_weekend"):
        jobs.append((os.path.join(out, f"weekend-{n:02d}-all-weekend.png"), all_weekend(d["all_weekend"], n, n), 1080, 1350))
    jobs.append((os.path.join(out, f"weekend-{n+1:02d}-guide.png"), closing(), 1080, 1350))
    asyncio.run(render(jobs))
    open(os.path.join(out, "caption.txt"), "w", encoding="utf8").write(d["caption"].rstrip() + "\n")
    print(f"{len(jobs)} images + caption -> {out}")

if __name__ == "__main__":
    main()
