"""Synthesise an original news-style intro sting, a soft news bed and an outro sting.
Deterministic (seeded). Writes WAVs into ../assets/."""
import numpy as np, wave, os
SR = 48000
rng = np.random.default_rng(7)
OUT = os.path.join(os.path.dirname(__file__), "..", "assets")

def t(d): return np.arange(int(d*SR))/SR
def env(n, a=0.005, r=0.3):
    e = np.ones(n); A = int(a*SR); R = min(n, int(r*SR))
    if A: e[:A] = np.linspace(0, 1, A)
    e[-R:] *= np.linspace(1, 0, R)**2
    return e
def saw(f, d, det=0.0):
    x = t(d); s = np.zeros_like(x)
    for dd in (-det, 0, det):
        ph = (x*f*(1+dd)) % 1.0; s += 2*ph-1
    return s/3
def lp(x, k=0.15):
    y = np.zeros_like(x); acc = 0.0
    # one-pole lowpass (vectorised via cumulative approach is messy; small loops fine)
    for i in range(len(x)):
        acc += k*(x[i]-acc); y[i] = acc
    return y
def midi(n): return 440*2**((n-69)/12)
def put(buf, sig, at):
    i = int(at*SR); j = min(len(buf), i+len(sig)); buf[i:j] += sig[:j-i]
def timpani(f=55, d=1.2):
    x = t(d); e = np.exp(-x*3.2)
    s = np.sin(2*np.pi*f*x*(1+0.08*np.exp(-x*20)))*e
    s += 0.4*np.sin(2*np.pi*f*1.5*x)*np.exp(-x*5)
    s += 0.25*rng.standard_normal(len(x))*np.exp(-x*30)
    return s
def hit(chord, d=1.6, vol=0.5):
    s = sum(saw(midi(n), d, 0.004) for n in chord)/len(chord)
    s = lp(s, 0.08) * env(len(s), 0.004, d*0.9) * np.exp(-t(d)*1.2)
    return s*vol
def tick(d=0.05):
    x = t(d); return np.sin(2*np.pi*2400*x)*np.exp(-x*120)
def swell(d, notes, vol=0.3):
    s = sum(saw(midi(n), d, 0.006) for n in notes)/len(notes)
    s = lp(s, 0.05)*np.linspace(0, 1, len(s))**2
    return s*vol
def reverb(x, mix=0.25):
    y = x.copy()
    for dly, g in ((0.031, .5), (0.047, .42), (0.071, .35), (0.113, .28), (0.173, .2)):
        n = int(dly*SR); z = np.zeros_like(x); z[n:] = x[:-n]*g; y += z*mix
    return y
def stereo_write(name, x):
    x = x/np.max(np.abs(x))*0.89
    d = (np.clip(x, -1, 1)*32767).astype(np.int16)
    st = np.stack([d, d], 1).ravel()
    with wave.open(os.path.join(OUT, name), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes())

# ---------- intro sting: 6.0 s ----------
D = 6.0; b = np.zeros(int(D*SR))
bpm = 120; beat = 60/bpm
for k in range(int(4.0/ (beat/2))):          # ticking clock pulse
    put(b, tick()*(0.35 if k % 2 else 0.6), k*beat/2)
put(b, swell(3.0, [50, 57, 62, 65], 0.35), 0.0)    # D minor swell
for k, at in enumerate([0.0, 1.0, 2.0, 2.5, 3.0, 3.25, 3.5, 3.75]):
    put(b, timpani(43.65 if k < 4 else 49, 0.9)*0.6, at)
put(b, hit([50, 57, 62, 65, 69], 1.0, 0.55), 2.0)
put(b, hit([46, 53, 58, 62, 65], 1.0, 0.55), 3.0)
put(b, hit([48, 55, 60, 64, 67], 0.6, 0.55), 3.5)
put(b, hit([50, 57, 62, 66, 69, 74], 2.4, 0.8), 4.0)   # final D major stab
put(b, timpani(36.7, 2.0), 4.0)
b = reverb(b, 0.35); b[-int(0.3*SR):] *= np.linspace(1, 0, int(0.3*SR))
stereo_write("intro-sting.wav", b)

# ---------- news bed: 60 s, very soft pulse + pad ----------
D = 60.0; b = np.zeros(int(D*SR))
prog = [[50, 57, 62, 65], [46, 53, 58, 62], [48, 55, 60, 64], [45, 52, 57, 61]]
bar = 4*beat
for i in range(int(D/bar)):
    ch = prog[i % 4]
    pad = sum(np.sin(2*np.pi*midi(n)*t(bar)) for n in ch)/4
    pad *= env(len(pad), 0.4, 0.5)*0.22
    put(b, pad, i*bar)
    for k in range(8):
        put(b, tick(0.03)*(0.18 if k % 2 else 0.28), i*bar + k*beat/2)
    put(b, timpani(midi(ch[0]-12), 0.8)*0.25, i*bar)
b = reverb(b, 0.3)
fade = int(2*SR); b[:fade] *= np.linspace(0, 1, fade); b[-fade:] *= np.linspace(1, 0, fade)
stereo_write("news-bed.wav", b)

# ---------- outro sting: 4.5 s ----------
D = 4.5; b = np.zeros(int(D*SR))
put(b, timpani(43.65, 0.9)*0.6, 0.0)
put(b, hit([46, 53, 58, 62, 65], 0.5, 0.5), 0.0)
put(b, hit([48, 55, 60, 64, 67], 0.5, 0.5), 0.5)
put(b, hit([50, 57, 62, 66, 69, 74], 3.0, 0.85), 1.0)
put(b, timpani(36.7, 2.5), 1.0)
b = reverb(b, 0.35); b[-int(0.6*SR):] *= np.linspace(1, 0, int(0.6*SR))
stereo_write("outro-sting.wav", b)
print("ok")
