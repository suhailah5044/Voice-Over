"""Generate compositions/latar.html: an animated haze / forest-fire backdrop (deterministic)."""
import random, math, os
R = random.Random(42)
W, H, D = 1920, 1080, 61.1

def treeline(base, amp, step, seed, jag=1.0):
    r = random.Random(seed); pts = [(-40, H)]; x = -40
    pts.append((x, base))
    while x < W + 40:
        h = base - r.uniform(0.3, 1.0) * amp
        w = r.uniform(step*0.6, step*1.4)
        # conifer-ish triangle + rounded canopy mix
        pts += [(x + w*0.5, h), (x + w, base - r.uniform(0, amp*0.25*jag))]
        x += w
    pts.append((W + 40, H))
    return "M" + " L".join(f"{a:.0f} {b:.0f}" for a, b in pts) + " Z"

layers = [
    ("lt-far",  1180, 120, 46, 1, "#9a7a63", 0.55),
    ("lt-mid",  1300, 170, 60, 2, "#6e5040", 0.75),
    ("lt-near", 1470, 230, 80, 3, "#3a2620", 0.95),
]
svg_layers = "\n".join(
    f'<path id="{i}" d="{treeline(b, a, s, sd)}" fill="{c}" opacity="{o}" />' for i, b, a, s, sd, c, o in layers)

smoke = []
for k in range(9):
    x = R.uniform(-300, 1700); y = R.uniform(150, 850); s = R.uniform(500, 900)
    o = R.uniform(0.18, 0.38); dx = R.uniform(120, 320)
    smoke.append((f"lt-asap{k}", x, y, s, o, dx))
smoke_html = "\n".join(
    f'<div id="{i}" class="lt-asap" style="left:{x:.0f}px;top:{y:.0f}px;width:{s:.0f}px;height:{s*0.6:.0f}px;opacity:{o:.2f}"></div>'
    for i, x, y, s, o, dx in smoke)
smoke_js = "\n".join(
    f'tl.fromTo("#{i}", {{ x: 0, scale: 1 }}, {{ x: {dx:.0f}, scale: 1.25, duration: D, ease: "none" }}, 0);'
    for i, x, y, s, o, dx in smoke)

ash = []
for k in range(46):
    x = R.uniform(0, W); y = R.uniform(150, 1050); sz = R.uniform(4, 11)
    ember = k % 9 == 0
    ash.append((f"lt-abu{k}", x, y, sz, ember, R.uniform(-200, -600), R.uniform(-160, 260), R.uniform(0.35, 0.85)))
ash_html = "\n".join(
    f'<div id="{i}" class="lt-abu{" lt-bara" if e else ""}" style="left:{x:.0f}px;top:{y:.0f}px;width:{sz:.1f}px;height:{sz:.1f}px;opacity:{o:.2f}"></div>'
    for i, x, y, sz, e, dy, dx, o in ash)
ash_js = "\n".join(
    f'tl.fromTo("#{i}", {{ y: 0, x: 0 }}, {{ y: {dy:.0f}, x: {dx:.0f}, duration: D, ease: "none" }}, 0);'
    for i, x, y, sz, e, dy, dx, o in ash)

# flicker of the fire glow: deterministic sequence of tweens
fl = []; t = 0.0; r2 = random.Random(9)
while t < D:
    d = r2.uniform(0.25, 0.7); fl.append(f'tl.to("#lt-api", {{ opacity: {r2.uniform(0.55, 1):.2f}, duration: {d-0.02:.2f}, ease: "sine.inOut" }}, {t:.2f});'); t += d
flicker_js = "\n".join(fl)

html = f'''<template>
  <style>
    #root {{ position: absolute; inset: 0; overflow: hidden; }}
    #lt-foto {{
      position: absolute; left: 0; top: 0; width: 2410px; height: 1080px;
    }}
    #lt-matahari {{
      position: absolute; left: 1080px; top: 60px; width: 160px; height: 160px; border-radius: 50%;
      background: radial-gradient(circle, rgba(255,226,170,0.85) 0%, rgba(255,190,110,0.35) 45%, rgba(255,170,90,0) 72%);
    }}
    .lt-asap {{
      position: absolute; border-radius: 50%;
      background: radial-gradient(closest-side, rgba(205,190,175,0.95), rgba(190,170,150,0.5) 55%, rgba(180,160,140,0) 100%);
      filter: blur(30px);
    }}
    .lt-abu {{ position: absolute; border-radius: 50%; background: #e9ded2; }}
    .lt-bara {{ background: #ffb050; box-shadow: 0 0 10px 3px rgba(255,140,40,0.8); }}
    #lt-kabus {{
      position: absolute; inset: 0;
      background: linear-gradient(180deg, rgba(205,190,160,0.45) 0%, rgba(200,180,140,0.18) 45%, rgba(90,70,50,0.25) 100%);
    }}
    #lt-vignet {{
      position: absolute; inset: 0;
      background: radial-gradient(120% 80% at 50% 45%, rgba(0,0,0,0) 55%, rgba(25,12,6,0.55) 100%);
    }}
  </style>
  <div id="root" data-composition-id="latar" data-width="1920" data-height="1080">
    <div id="lt-pentas" class="clip" data-start="0" data-duration="{D}" data-layout-ignore data-layout-allow-overflow>
      <img id="lt-foto" src="assets/jerebu-kl.jpg" alt="Jerebu di Kuala Lumpur" />
      <div id="lt-matahari"></div>
      {smoke_html}
      <div id="lt-kabus"></div>
      {ash_html}
      <div id="lt-vignet"></div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    const D = {D};
    tl.fromTo("#lt-pentas", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.01 }}, 0);
    tl.fromTo("#lt-foto", {{ x: -60, scale: 1.04 }}, {{ x: -440, scale: 1.0, duration: D, ease: "none" }}, 0);
    tl.fromTo("#lt-matahari", {{ y: 0, opacity: 0.7 }}, {{ y: 40, opacity: 0.9, duration: D, ease: "none" }}, 0);
    tl.fromTo("#lt-kabus", {{ opacity: 0.85 }}, {{ opacity: 1, duration: D, ease: "sine.inOut" }}, 0);
    {smoke_js}
    {ash_js}
    window.__timelines["latar"] = tl;
  </script>
</template>
'''
open(os.path.join(os.path.dirname(__file__), "..", "compositions", "latar.html"), "w").write(html)
print("latar ok")
