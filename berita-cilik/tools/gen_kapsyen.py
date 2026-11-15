"""Generate compositions/kapsyen.html from corrected caption groups (times are in the cut video)."""
import os, json
G = [
 ("Assalamualaikum dan selamat sejahtera.", 0.15, 2.36),
 ("Saya Muhamad Rifhaan Deeniy", 2.42, 3.96),
 ("bin Muhamad Firdaus,", 3.96, 4.80),
 ("Wartawan Cilik melaporkan", 4.84, 6.14),
 ("kejadian kebakaran hutan.", 6.14, 7.55),
 ("Api telah merebak dengan cepat", 7.72, 9.84),
 ("kerana cuaca panas dan kering.", 9.84, 11.85),
 ("Asap tebal memenuhi udara", 11.92, 14.10),
 ("dan menyebabkan jarak penglihatan", 14.10, 17.06),
 ("menjadi terhad.", 17.06, 18.0),
 ("Fakta sains:", 18.18, 19.10),
 ("Api memerlukan tiga perkara", 19.34, 21.46),
 ("untuk terus menyala,", 21.46, 23.26),
 ("iaitu haba, bahan api", 23.32, 25.66),
 ("dan oksigen.", 25.66, 26.68),
 ("Tiga perkara ini", 26.70, 28.20),
 ("dikenali sebagai segi tiga api.", 28.20, 31.50),
 ("Orang ramai dinasihatkan", 31.72, 33.86),
 ("supaya menjauhi kawasan kebakaran", 33.86, 36.52),
 ("dan memakai pelitup muka", 36.52, 37.94),
 ("jika terdapat jerebu.", 37.94, 39.45),
 ("Kita juga perlu menjaga alam sekitar", 39.58, 43.42),
 ("dan tidak membuang", 43.42, 44.50),
 ("puntung rokok sebarangan.", 44.50, 46.0),
 ("Saya Muhamad Rifhaan Deeniy", 46.20, 48.12),
 ("bin Muhamad Firdaus", 48.12, 48.84),
 ("melaporkan dari lokasi kejadian.", 48.84, 50.72),
 ("Sekian, terima kasih.", 50.86, 52.6),
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
      position: absolute; left: 0; top: 1218px; width: 1080px; height: 130px;
      display: flex; align-items: center; justify-content: center; overflow: visible;
    }}
    .kp-teks {{
      display: inline-block; max-width: 940px; text-align: center;
      padding: 10px 26px; border-radius: 14px;
      background: rgba(5, 12, 35, 0.72);
      font-family: "Montserrat", sans-serif; font-weight: 800; font-size: 48px; line-height: 1.15;
      color: #fff; text-shadow: 0 2px 6px rgba(0,0,0,0.6);
    }}
  </style>
  <div id="root" data-composition-id="kapsyen" data-width="1080" data-height="1920">
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
