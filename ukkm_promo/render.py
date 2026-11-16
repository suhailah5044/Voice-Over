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

# ---------- timing from VO ----------
durs = json.load(open(f'{S}/vo/durs.json'))
GAP = 0.35
starts = []; t = 0.4
for i, d in enumerate(durs):
    starts.append(t); t += d + GAP
    if i in (0, 1, 5, 6): t += 0.3   # breath at scene boundaries
END = t + 1.6
# scenes: (start, end)
sc = {
 'hook': (0, starts[1] - 0.15),
 'date': (starts[1] - 0.15, starts[2] - 0.15),
 'sched': (starts[2] - 0.15, starts[6] - 0.15),
 'price': (starts[6] - 0.15, starts[7] - 0.15),
 'cta': (starts[7] - 0.15, END),
}

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

# ---------- scenes ----------
els = []
a, b = sc['hook']
els += [
 El(pill('ZOOM  •  ONLINE', F(800, 50), RED, WHITE), W / 2, 500, a + 0.1, b, 'pop'),
 El(text_img('LAST MINUTE', F(900, 130, True), WHITE, 6), W / 2, 650, a + 0.35, b, 'slide', dx=-900),
 El(text_img('UKKM', F(900, 280, True), YEL, 12), W / 2, 860, a + 0.7, b, 'slam', dur=0.35),
 El(pill('Ujian Khas Kemasukan MRSM', F(800, 54, True), YEL, NAVY, padx=40, pady=16, r=14), W / 2, 1100, a + 1.2, b, 'slide', dx=900),
 El(text_img('Anak nak masuk MRSM?', F(700, 64), WHITE, 0), W / 2, 1270, starts[0], b, 'pop'),
]
a, b = sc['date']
els += [
 El(pill('4 HARI INTENSIF', F(900, 64, True), YEL, NAVY), W / 2, 500, a + 0.05, b, 'pop'),
 El(text_img('16 – 19', F(900, 260, True), WHITE, 10), W / 2, 760, a + 0.3, b, 'slam', dur=0.35),
 El(text_img('NOVEMBER 2026', F(900, 100, True), YEL, 6), W / 2, 960, a + 0.6, b, 'slide', dy=200),
]
days = [('ISNIN', '16'), ('SELASA', '17'), ('RABU', '18'), ('KHAMIS', '19')]
for i, (dn, dd) in enumerate(days):
    cx = 165 + i * 250
    els.append(El(pill(f'{dd}  {dn}', F(800, 38), WHITE, NAVY, padx=24, pady=14), cx, 1150, a + 1.0 + i * 0.22, b, 'pop'))
els.append(El(text_img('Online di Zoom', F(700, 60), WHITE, 0), W / 2, 1300, a + 2.0, b, 'pop'))

a, b = sc['sched']
els += [El(pill('JADUAL SETIAP MALAM', F(900, 64, True), YEL, NAVY), W / 2, 420, a + 0.05, b, 'pop'),
        El(text_img('16 – 19 Nov 2026', F(700, 50), WHITE, 0), W / 2, 540, a + 0.3, b, 'pop')]
cards = [('Sains', 'Cikgu Shukry', '6.00 – 7.00 pm'),
         ('Keperibadian', 'Sir Koala', '8.00 – 9.00 pm'),
         ('Matematik', 'GB Shahril', '9.35 – 10.35 pm')]
for i, c in enumerate(cards):
    els.append(El(subject_card(*c), W / 2, 780 + i * 300, starts[3 + i] - 0.1, b, 'slide', dx=1100 if i % 2 == 0 else -1100, dur=0.5))

a, b = sc['price']
els += [El(pill('HARGA ISTIMEWA', F(900, 64, True), YEL, NAVY), W / 2, 440, a + 0.05, b, 'pop')]
pc = Image.new('RGBA', (980, 580), (0, 0, 0, 0))
sh = Image.new('RGBA', pc.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((20, 40, 960, 560), 60, fill=(0, 0, 30, 150))
pc = Image.alpha_composite(pc, sh.filter(ImageFilter.GaussianBlur(12)))
ImageDraw.Draw(pc).rounded_rectangle((20, 20, 960, 540), 60, fill=RED, outline=WHITE, width=10)
els.append(El(pc, W / 2, 880, a + 0.25, b, 'pop'))
els.append(El(text_img('RM60 / hari', F(900, 140, True), WHITE, 6, (120, 0, 0)), W / 2, 760, a + 0.45, b, 'slam', dur=0.3))
els.append(El(text_img('atau', F(700, 50), YEL, 0, shadow=False), W / 2, 885, a + 2.2, b, 'pop'))
fp = pill('Full Pakej  RM199', F(900, 96, True), YEL, NAVY, padx=46, pady=14, r=20)
els.append(El(fp, W / 2, 1000, a + 2.6, b, 'slam', dur=0.3, pulse=True))
els.append(El(text_img('4 hari • 3 subjek • 12 kelas', F(700, 54), WHITE, 0), W / 2, 1260, a + 3.4, b, 'pop'))

a, b = sc['cta']
src = Image.open(POSTER).convert('RGB')
arr = np.asarray(src).astype(int).sum(2)
rows = np.where(arr.mean(1) > 60)[0]
# largest contiguous bright band = poster
bands = np.split(rows, np.where(np.diff(rows) > 5)[0] + 1)
band = max(bands, key=len)
poster = src.crop((0, band[0], src.width, band[-1] + 1)).convert('RGBA')
pw = 960; poster = poster.resize((pw, int(poster.height * pw / poster.width)), Image.LANCZOS)
fr = Image.new('RGBA', (pw + 40, poster.height + 40), (0, 0, 0, 0))
ImageDraw.Draw(fr).rounded_rectangle((0, 0, pw + 39, poster.height + 39), 30, fill=WHITE)
m = Image.new('L', poster.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, pw - 1, poster.height - 1), 20, fill=255)
fr.paste(poster, (20, 20), m)
els.append(El(fr, W / 2, 140 + fr.height / 2, a + 0.05, b, 'pop', dur=0.5))
els.append(El(pill('DAFTAR SEKARANG!', F(900, 84, True), RED, WHITE, outline=WHITE), W / 2, 140 + fr.height + 150, a + 0.6, b, 'slam', dur=0.3, pulse=True))

# ---------- render ----------
N = int(END * FPS)
frames = range(0, N, 15) if PREVIEW else range(N)
if PREVIEW:
    os.makedirs(f'{S}/prev', exist_ok=True)
else:
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', f'{S}/video_noaudio.mp4'], stdin=subprocess.PIPE)
for n in frames:
    t = n / FPS
    f = background(t)
    for e in els: e.draw(f, t)
    if t < sc['cta'][0]:
        f.alpha_composite(brand, (0, H - 190))
    # flash at scene cuts
    for k, (s0, _) in sc.items():
        if 0 <= t - s0 < 0.12 and s0 > 0:
            f.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(150 * (1 - (t - s0) / 0.12)))))
    rgb = f.convert('RGB')
    if PREVIEW: rgb.save(f'{S}/prev/f{n:04d}.jpg', quality=80)
    else: ff.stdin.write(rgb.tobytes())
if not PREVIEW:
    ff.stdin.close(); ff.wait()
json.dump({'starts': starts, 'end': END, 'scenes': sc}, open(f'{S}/timing.json', 'w'))
print('frames', N, 'dur', END)
