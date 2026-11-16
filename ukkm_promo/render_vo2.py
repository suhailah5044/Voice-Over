import json, math, subprocess, sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = os.path.dirname(os.path.abspath(__file__))
FD = f'{S}/npmf/package/files'
POSTER = '/root/.claude/uploads/e8e434eb-1b00-5252-8764-d8b275a098fa/92b6ae41-image.png'
OUT = sys.argv[1] if len(sys.argv) > 1 else f'{S}/out.mp4'
PREVIEW = '--preview' in sys.argv
W, H, FPS = 1080, 1920, 30

def F(w, size, italic=False):
    return ImageFont.truetype(f'{FD}/poppins-latin-{w}-{"italic" if italic else "normal"}.woff', size)

BLUE1, BLUE2 = (6, 46, 160), (24, 120, 255)
YEL, RED, NAVY, WHITE = (255, 212, 0), (226, 24, 30), (10, 24, 74), (255, 255, 255)

# ---------- helpers ----------
def text_img(txt, font, fill, stroke=0, stroke_fill=NAVY, shadow=True):
    b = font.getbbox(txt, stroke_width=stroke)
    w, h = b[2] - b[0] + 30, b[3] - b[1] + 30
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if shadow:
        sh = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((15 - b[0] + 5, 15 - b[1] + 8), txt, font=font, fill=(0, 0, 30, 140), stroke_width=stroke, stroke_fill=(0, 0, 30, 140))
        im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(5)))
        d = ImageDraw.Draw(im)
    d.text((15 - b[0], 15 - b[1]), txt, font=font, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    return im

def pill(txt, font, bg, fg, padx=40, pady=18, r=None, outline=None):
    b = font.getbbox(txt)
    tw, th = b[2] - b[0], b[3] - b[1]
    w, h = tw + 2 * padx, th + 2 * pady
    r = h // 2 if r is None else r
    im = Image.new('RGBA', (w + 20, h + 24), (0, 0, 0, 0))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((10, 16, w + 10, h + 16), r, fill=(0, 0, 30, 110))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(6)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 8, w + 10, h + 8), r, fill=bg, outline=outline, width=6 if outline else 0)
    d.text((10 + padx - b[0], 8 + pady - b[1]), txt, font=font, fill=fg)
    return im

def clock(d, cx, cy, r, col):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=col, width=6)
    d.line((cx, cy, cx, cy - r * 0.6), fill=col, width=6)
    d.line((cx, cy, cx + r * 0.45, cy), fill=col, width=6)

def subject_card(subj, teacher, time):
    w, h = 940, 250
    im = Image.new('RGBA', (w + 40, h + 50), (0, 0, 0, 0))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((20, 34, w + 20, h + 34), 40, fill=(0, 0, 40, 130))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((20, 20, w + 20, h + 20), 40, fill=WHITE)
    d.rounded_rectangle((20, 20, 44, h + 20), 12, fill=YEL)
    p = pill(subj, F(800, 58), BLUE2, WHITE, padx=34, pady=12)
    im.alpha_composite(p, (60, 36))
    d = ImageDraw.Draw(im)
    d.text((80, 150), teacher, font=F(600, 40), fill=(70, 90, 140))
    tf = F(800, 48); tb = tf.getbbox(time); tx = w + 20 - 40 - (tb[2] - tb[0])
    clock(d, tx - 44, 186, 26, NAVY)
    d.text((tx - tb[0], 186 - (tb[1] + tb[3]) / 2), time, font=tf, fill=NAVY)
    return im

ease_out = lambda x: 1 - (1 - x) ** 3
def ease_back(x, s=1.7):
    x -= 1; return x * x * ((s + 1) * x + s) + 1
clamp = lambda x: max(0.0, min(1.0, x))

class El:
    def __init__(self, img, cx, cy, t0, t1, kind='pop', dur=0.45, dx=0, dy=0, pulse=False):
        self.img, self.cx, self.cy, self.t0, self.t1 = img, cx, cy, t0, t1
        self.kind, self.dur, self.dx, self.dy, self.pulse = kind, dur, dx, dy, pulse
    def draw(self, frame, t):
        if t < self.t0 or t > self.t1: return
        p = clamp((t - self.t0) / self.dur)
        out = clamp((self.t1 - t) / 0.25)
        a = min(ease_out(p), out)
        sc = 1.0; ox = oy = 0
        if self.kind == 'pop': sc = 0.3 + 0.7 * ease_back(p)
        elif self.kind == 'slam': sc = 1 + 1.5 * (1 - ease_out(p))
        elif self.kind == 'slide':
            ox = self.dx * (1 - ease_out(p)); oy = self.dy * (1 - ease_out(p))
        if self.pulse and p >= 1: sc *= 1 + 0.04 * math.sin((t - self.t0) * 2 * math.pi * 1.6)
        sc *= 1 + 0.02 * (t - self.t0) / max(1, self.t1 - self.t0)  # slow push-in
        im = self.img
        if abs(sc - 1) > 0.003:
            im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BILINEAR)
        if a < 0.999:
            al = im.getchannel('A').point(lambda v: int(v * a)); im = im.copy(); im.putalpha(al)
        frame.alpha_composite(im, (int(self.cx + ox - im.width / 2), int(self.cy + oy - im.height / 2)))

# ---------- background ----------
def make_bg():
    y = np.linspace(0, 1, H)[:, None]; x = np.linspace(0, 1, W)[None, :]
    m = np.clip(0.6 * y + 0.4 * (1 - np.abs(x - 0.5) * 2) * (1 - y), 0, 1)[..., None]
    arr = (np.array(BLUE1) * m + np.array(BLUE2) * (1 - m)).astype(np.uint8)
    bg = Image.fromarray(np.broadcast_to(arr, (H, W, 3)).copy()).convert('RGBA')
    rays = Image.new('RGBA', (W * 2, H * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(rays)
    c = (W, int(H * 0.75))
    for k in range(18):
        a0 = k * 20; a1 = a0 + 8
        r = 3000
        p = [c, (c[0] + r * math.cos(math.radians(a0)), c[1] + r * math.sin(math.radians(a0))),
             (c[0] + r * math.cos(math.radians(a1)), c[1] + r * math.sin(math.radians(a1)))]
        d.polygon(p, fill=(255, 255, 255, 16))
    return bg, rays

BG, RAYS = make_bg()
SWOOSH = Image.new('RGBA', (W, 700), (0, 0, 0, 0))
ds = ImageDraw.Draw(SWOOSH)
ds.ellipse((-600, 330, W + 600, 1500), fill=YEL)
ds.ellipse((-600, 380, W + 600, 1550), fill=WHITE)
SWOOSH = SWOOSH.filter(ImageFilter.GaussianBlur(1))

def background(t):
    f = BG.copy()
    ang = t * 6
    r = RAYS.rotate(ang, resample=Image.BILINEAR, center=(W, int(H * 0.75)))
    f.alpha_composite(r.crop((W // 2, int(H * 0.75) - int(H * 0.75), W // 2 + W, int(H * 0.75) + int(H * 0.25))))
    # diagonal speed streaks
    d = ImageDraw.Draw(f)
    for k in range(7):
        sp = 900 + 140 * k
        x = ((t * sp + k * 431) % (W + 900)) - 450
        yy = (k * 263) % H
        d.line((x, yy, x + 260, yy - 90), fill=(255, 255, 255, 60), width=4 + k % 3)
    f.alpha_composite(SWOOSH, (0, H - 520))
    return f

# ---------- footer brand ----------
brand = Image.new('RGBA', (W, 140), (0, 0, 0, 0))
bd = ImageDraw.Draw(brand)
bt = 'FLY HIGH'; bf = F(900, 56, True)
bb = bf.getbbox(bt); bx = (W - (bb[2] - bb[0])) // 2
bd.text((bx, 6), bt, font=bf, fill=BLUE1)
st = 'EDUCATION CENTRE'; sf = F(700, 30)
sb = sf.getbbox(st); bd.text(((W - (sb[2] - sb[0])) // 2, 82), st, font=sf, fill=NAVY)



# ---------- timing = user's own voiceover ("Link Voice over") ----------
END = 44.0
sc = {'hook': (0, 4.05), 'mrsm': (4.05, 7.8), 'days': (7.8, 13.5), 'zoom': (13.5, 16.1), 'sched': (16.1, 23.05),
      'cikgu': (23.05, 28.8), 'rakam': (28.8, 33.6), 'cta': (33.6, 40.45), 'end': (40.45, END)}
def tick_pill(txt, size=56, bg=WHITE, fg=NAVY):
    p = pill(txt, F(800, size), bg, fg, padx=40 + int(size * 1.15), pady=20, r=24)
    d = ImageDraw.Draw(p); h = p.height - 24; cx, cy, r = 10 + 40 + int(size * 0.45), 8 + h // 2, int(size * 0.45)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(20, 170, 80))
    d.line([(cx - r * 0.5, cy), (cx - r * 0.1, cy + r * 0.45), (cx + r * 0.55, cy - r * 0.4)], fill=WHITE, width=max(4, size // 10), joint='curve')
    return p
def bag(sz=300):
    im = Image.new('RGBA', (sz, sz), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.arc((sz*0.3, sz*0.08, sz*0.7, sz*0.5), 180, 360, fill=NAVY, width=int(sz*0.06))
    d.rounded_rectangle((sz*0.12, sz*0.28, sz*0.88, sz*0.95), int(sz*0.1), fill=YEL, outline=NAVY, width=int(sz*0.04))
    return im
els = []
b = sc['hook'][1]
els += [El(pill('BERITA BAIK!', F(900, 84, True), RED, WHITE, outline=WHITE), W / 2, 520, 0.0, b, 'slam', dur=0.3),
        El(text_img('Kelas online', F(800, 84), WHITE, 0), W / 2, 700, 0.7, b, 'slide', dx=-900),
        El(text_img('UKKM 2026', F(900, 165, True), YEL, 10), W / 2, 900, 1.45, b, 'slam', dur=0.3),
        El(pill('DAH DIBUKA!', F(900, 80, True), WHITE, NAVY), W / 2, 1110, 3.2, b, 'pop')]
b = sc['mrsm'][1]
els += [El(text_img('Anak nak masuk', F(800, 84), WHITE, 0), W / 2, 520, 4.1, b, 'pop'),
        El(text_img('MRSM?', F(900, 230, True), YEL, 10), W / 2, 720, 4.45, b, 'slam', dur=0.3),
        El(pill('PELUANG TERAKHIR', F(900, 72, True), RED, WHITE, outline=WHITE), W / 2, 930, 5.45, b, 'slam', dur=0.3),
        El(text_img('untuk ulangkaji sebelum ujian', F(700, 56), WHITE, 0), W / 2, 1080, 6.55, b, 'pop')]
b = sc['days'][1]
els += [El(text_img('3 MALAM', F(900, 200, True), WHITE, 8), W / 2, 500, 8.55, b, 'slam', dur=0.3)]
for i, (lab, t0) in enumerate([('SELASA  17', 9.2), ('RABU  18', 10.5), ('KHAMIS  19', 12.0)]):
    els.append(El(pill(lab, F(900, 70, True), YEL, NAVY, padx=50, pady=20), W / 2, 720 + i * 150, t0, b, 'slide', dx=1100 if i % 2 == 0 else -1100))
els.append(El(text_img('NOVEMBER 2026', F(900, 100, True), WHITE, 6), W / 2, 1200, 13.05, b, 'pop', dur=0.3))
b = sc['zoom'][1]
els += [El(text_img('Kelas melalui', F(800, 84), WHITE, 0), W / 2, 560, 13.55, b, 'pop'),
        El(pill('ZOOM  •  ONLINE', F(900, 90, True), BLUE1, WHITE, outline=WHITE), W / 2, 730, 14.3, b, 'slam', dur=0.3),
        El(text_img('Belajar dari rumah', F(900, 96, True), YEL, 6), W / 2, 930, 15.05, b, 'slide', dx=-900)]
b = sc['sched'][1]
els += [El(pill('JADUAL SETIAP MALAM', F(900, 64, True), YEL, NAVY), W / 2, 420, 16.15, b, 'pop'),
        El(text_img('17 – 19 Nov 2026', F(700, 50), WHITE, 0), W / 2, 540, 16.4, b, 'pop')]
for i, (c, t0) in enumerate(zip([('Sains', 'Cikgu Shukry', '6.00 – 7.00 pm'), ('Keperibadian', 'Sir Koala', '8.00 – 9.00 pm'),
                                 ('Matematik', 'GB Shahril', '9.35 – 10.35 pm')], [17.05, 18.65, 20.6])):
    els.append(El(subject_card(*c), W / 2, 800 + i * 300, t0, b, 'slide', dx=1100 if i % 2 == 0 else -1100, dur=0.45))
b = sc['cikgu'][1]
els += [El(text_img('Cikgu yang dah biasa', F(800, 76), WHITE, 0), W / 2, 480, 23.1, b, 'pop'),
        El(text_img('format UKKM', F(900, 130, True), YEL, 8), W / 2, 630, 24.2, b, 'slam', dur=0.3),
        El(tick_pill('Cara jawab yang betul', 58), W / 2, 850, 25.6, b, 'slide', dx=1100),
        El(tick_pill('Bincang soalan berpotensi', 52), W / 2, 1010, 27.05, b, 'slide', dx=-1100),
        El(text_img('keluar', F(800, 52), WHITE, 0), W / 2, 1110, 28.55, b, 'pop')]
b = sc['rakam'][1]
els += [El(text_img('Ada aktiviti lain?', F(800, 84), WHITE, 0), W / 2, 500, 29.6, b, 'pop'),
        El(pill('JANGAN RISAU!', F(900, 96, True), RED, WHITE, outline=WHITE), W / 2, 680, 30.45, b, 'slam', dur=0.3),
        El(tick_pill('Rakaman kelas', 64), W / 2, 890, 31.4, b, 'slide', dx=1100),
        El(tick_pill('Modul diberikan', 64), W / 2, 1060, 32.35, b, 'slide', dx=-1100)]
b = sc['cta'][1]
els += [El(text_img('CARA JOIN?', F(900, 130, True), WHITE, 6), W / 2, 380, 33.65, b, 'slam', dur=0.3),
        El(pill('SENANG JE!', F(900, 64, True), YEL, NAVY), W / 2, 520, 34.2, b, 'pop'),
        El(bag(240), W / 2 - 300, 720, 34.85, b, 'pop', pulse=True),
        El(text_img('Tekan beg kuning', F(900, 60, True), YEL, 4), W / 2 + 120, 690, 35.0, b, 'slide', dx=900),
        El(text_img('& buat bayaran', F(800, 52), WHITE, 0), W / 2 + 120, 770, 36.1, b, 'slide', dx=900),
        El(pill('RM60/hari  •  Full Pakej RM199', F(900, 50, True), RED, WHITE, outline=WHITE), W / 2, 930, 36.3, b, 'pop'),
        El(text_img('Lepas tu, mesej Fly High', F(800, 64), WHITE, 0), W / 2, 1110, 37.5, b, 'pop'),
        El(pill('untuk dapatkan link kelas', F(800, 56), WHITE, NAVY), W / 2, 1240, 39.45, b, 'pop')]
b = END
els += [El(text_img('LAST MINUTE UKKM', F(900, 100, True), WHITE, 6), W / 2, 460, 40.5, b, 'pop'),
        El(text_img('Tempat sangat-sangat', F(800, 76), WHITE, 0), W / 2, 640, 40.6, b, 'pop'),
        El(text_img('TERHAD!', F(900, 220, True), YEL, 10), W / 2, 820, 41.55, b, 'slam', dur=0.3),
        El(pill('JANGAN TUNGGU ESOK!', F(900, 80, True), RED, WHITE, outline=WHITE), W / 2, 1060, 42.1, b, 'slam', dur=0.3, pulse=True)]

# ---------- render ----------
N = int(END * FPS)
frames = range(0, N, 15) if PREVIEW else range(N)
if PREVIEW:
    os.makedirs(f'{S}/prev', exist_ok=True)
else:
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', f'{S}/video_vo2_noaudio.mp4'], stdin=subprocess.PIPE)
for n in frames:
    t = n / FPS
    f = background(t)
    for e in els: e.draw(f, t)
    if True:
        f.alpha_composite(brand, (0, H - 190))
    # flash at scene cuts
    for k, (s0, _) in sc.items():
        if 0 <= t - s0 < 0.12 and s0 > 0:
            f.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(150 * (1 - (t - s0) / 0.12)))))
    rgb = f.convert('RGB')
    if PREVIEW: rgb.save(f'{S}/prev3/f{n:04d}.jpg', quality=80)
    else: ff.stdin.write(rgb.tobytes())
if not PREVIEW:
    ff.stdin.close(); ff.wait()
json.dump({'end': END, 'scenes': sc}, open(f'{S}/timing_vo2.json', 'w'))
print('frames', N, 'dur', END)
