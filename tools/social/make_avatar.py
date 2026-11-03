"""Render Instagram profile-picture options (1080×1080, composed for the circular crop).

    python3 tools/social/make_avatar.py OUTDIR
"""
import os, sys, asyncio
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_kit import shell, INK, PAPER, BLACK, render  # same fonts, palette, and halftone

def a_monogram():
    return shell(1080, 1080, f"""
<div style='position:absolute;inset:0;display:grid;place-items:center'>
 <div style='text-align:center'>
  <div class='mast mis' style='font-size:560px;line-height:.78;--c:{INK["film"]};letter-spacing:-.02em'>CR</div>
  <div class=mast style='font-size:150px;margin-top:34px'><span style='display:inline-block;background:{INK["film"]};border:8px solid {BLACK};padding:16px 30px 0;transform:rotate(-3deg);box-shadow:12px 12px 0 {BLACK}'>T.O.</span></div>
 </div></div>""", bg=INK["art"])

def b_stack():
    return shell(1080, 1080, f"""
<div style='position:absolute;inset:0;display:grid;place-items:center'>
 <div style='text-align:center;transform:rotate(-4deg)'>
  <div class='mast mis' style='font-size:250px;--c:{INK["film"]}'>Culture</div>
  <div class='mast mis' style='font-size:250px;color:{PAPER};-webkit-text-stroke:8px {BLACK};--c:{BLACK}'>Radar</div>
  <div class=mast style='font-size:120px;margin-top:22px'><span style='display:inline-block;background:{INK["music"]};border:7px solid {BLACK};padding:12px 26px 0;box-shadow:10px 10px 0 {BLACK}'>T.O.</span></div>
 </div></div>""", bg=INK["art"])

def c_radar():
    rings = "".join(f"<div style='position:absolute;left:50%;top:50%;width:{d}px;height:{d}px;margin:-{d//2}px 0 0 -{d//2}px;border:10px solid {BLACK};border-radius:50%'></div>" for d in (900, 640, 380))
    return shell(1080, 1080, f"""
<div style='position:absolute;left:50%;top:50%;width:900px;height:900px;margin:-450px 0 0 -450px;border-radius:50%;
  background:conic-gradient(from 20deg,{INK["film"]} 0deg,{INK["film"]} 62deg,transparent 62deg)'></div>
{rings}
<div style='position:absolute;inset:0;display:grid;place-items:center'>
  <div class=mast style='font-size:190px;background:{BLACK};color:{INK["art"]};padding:26px 34px 6px;transform:rotate(-3deg);box-shadow:12px 12px 0 {INK["music"]}'>T.O.</div></div>""",
        bg=INK["art"])

if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    jobs = [(os.path.join(out, f"avatar-{k}.png"), f(), 1080, 1080) for k, f in (("a-monogram", a_monogram), ("b-stack", b_stack), ("c-radar", c_radar))]
    asyncio.run(render(jobs))
    print("\n".join(j[0] for j in jobs))
