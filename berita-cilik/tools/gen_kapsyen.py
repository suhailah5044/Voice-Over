"""Generate compositions/kapsyen.html from corrected caption groups (times are in the cut video)."""
import os, json
G = [
 ("Assalamualaikum dan selamat sejahtera.", 0.15, 2.30),
 ("Saya Muhammad Rifhaan Deeniy", 2.38, 3.86),
 ("bin Muhammad Firdaus,", 3.86, 4.84),
 ("Wartawan Cilik melaporkan", 4.90, 6.42),
 ("keadaan jerebu yang berlaku", 6.42, 8.20),
 ("di beberapa kawasan.", 8.20, 9.66),
 ("Jerebu menyebabkan udara", 9.74, 10.80),
 ("menjadi kurang bersih", 10.80, 11.94),
 ("dan jarak penglihatan berkurangan.", 11.94, 14.26),
 ("Keadaan ini boleh berlaku", 14.34, 16.10),
 ("akibat asap daripada kebakaran hutan", 16.10, 18.54),
 ("dan pembakaran terbuka.", 18.54, 20.52),
 ("Fakta sains:", 20.56, 21.22),
 ("jerebu mengandungi zarah halus", 21.26, 23.42),
 ("yang terapung di udara.", 23.42, 25.08),
 ("Zarah ini boleh masuk", 25.10, 27.02),
 ("ke dalam sistem pernafasan", 27.02, 28.74),
 ("apabila kita bernafas.", 28.74, 30.86),
 ("Orang ramai dinasihatkan", 30.88, 32.22),
 ("supaya mengurangkan aktiviti di luar", 32.22, 34.48),
 ("ketika keadaan jerebu teruk.", 34.48, 36.56),
 ("Jangan melakukan pembakaran terbuka", 36.64, 39.24),
 ("kerana perbuatan ini boleh mencemarkan udara.", 39.24, 42.86),
 ("Saya Muhammad Rifhaan Deeniy", 42.98, 44.38),
 ("bin Muhammad Firdaus,", 44.38, 45.18),
 ("melaporkan untuk Wartawan Cilik.", 45.18, 46.98),
 ("Sekian, terima kasih.", 47.00, 48.55),
]
items = "\n".join(
  f'      <div id="kp-{i}" class="kp-grup clip" data-start="{s:.2f}" data-duration="{e-s:.2f}"><span class="kp-teks">{t}</span></div>'
  for i, (t, s, e) in enumerate(G))
js = "\n".join(
  f'    tl.fromTo("#kp-{i} .kp-teks", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.16, ease: "power2.out" }}, {s:.2f});\n'
  f'    tl.to("#kp-{i} .kp-teks", {{ opacity: 0, duration: 0.1, ease: "power2.in" }}, {e-0.1:.2f});'
  for i, (t, s, e) in enumerate(G))
html = f'''<template>
  <style>
    #root {{ position: absolute; inset: 0; }}
    .kp-grup {{
      position: absolute; left: 0; top: 770px; width: 1920px; height: 96px;
      display: flex; align-items: center; justify-content: center; overflow: visible;
    }}
    .kp-teks {{
      display: inline-block; max-width: 1500px; text-align: center;
      padding: 10px 26px; border-radius: 14px;
      background: rgba(5, 12, 35, 0.72);
      font-family: "Montserrat", sans-serif; font-weight: 800; font-size: 46px; line-height: 1.15;
      color: #fff; text-shadow: 0 2px 6px rgba(0,0,0,0.6);
    }}
  </style>
  <div id="root" data-composition-id="kapsyen" data-width="1920" data-height="1080">
{items}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{js}
    window.__timelines["kapsyen"] = tl;
  </script>
</template>
'''
open(os.path.join(os.path.dirname(__file__), "..", "compositions", "kapsyen.html"), "w").write(html)
print("kapsyen ok", len(G))
