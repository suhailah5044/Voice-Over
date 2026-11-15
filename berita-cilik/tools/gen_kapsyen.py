"""Generate compositions/kapsyen.html from corrected caption groups (times are in the cut video)."""
import os, json
G = [
 ("Assalamualaikum dan selamat sejahtera.", 0.15, 2.66),
 ("Saya Muhammad Rifhaan Deeniy", 2.68, 4.60),
 ("bin Muhammad Firdaus,", 4.60, 5.66),
 ("Wartawan Cilik melaporkan", 5.68, 7.66),
 ("keadaan jerebu yang berlaku", 7.66, 9.78),
 ("di beberapa kawasan.", 9.78, 11.40),
 ("Jerebu menyebabkan udara", 11.46, 13.30),
 ("menjadi kurang bersih", 13.30, 14.68),
 ("dan jarak penglihatan berkurangan.", 14.68, 17.40),
 ("Keadaan ini boleh berlaku", 17.46, 20.74),
 ("akibat asap daripada kebakaran hutan", 20.74, 23.60),
 ("dan pembakaran terbuka.", 23.60, 27.05),
 ("Fakta sains:", 27.10, 28.00),
 ("jerebu mengandungi zarah halus", 28.04, 30.62),
 ("yang terapung di udara.", 30.62, 32.62),
 ("Zarah ini boleh masuk", 32.66, 34.86),
 ("ke dalam sistem pernafasan", 34.86, 36.86),
 ("apabila kita bernafas.", 36.86, 39.45),
 ("Orang ramai dinasihatkan", 39.52, 41.34),
 ("supaya mengurangkan aktiviti di luar", 41.34, 44.06),
 ("ketika keadaan jerebu teruk.", 44.06, 46.40),
 ("Jangan melakukan pembakaran terbuka", 46.44, 49.46),
 ("kerana perbuatan ini boleh mencemarkan udara.", 49.46, 53.62),
 ("Saya Muhammad Rifhaan Deeniy", 53.68, 55.44),
 ("bin Muhammad Firdaus", 55.44, 56.38),
 ("melaporkan untuk Wartawan Cilik.", 56.38, 58.48),
 ("Sekian, terima kasih.", 58.52, 60.40),
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
