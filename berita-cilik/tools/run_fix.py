"""Decode a VP9-alpha cutout, solidify ears/edges with fixalpha.fix, re-encode VP9 alpha."""
import subprocess, sys, numpy as np
from multiprocessing import Pool
sys.path.insert(0, sys.path[0])
from fixalpha import fix
src, dst = sys.argv[1], sys.argv[2]
W, H = 1080, 1920; N = W*H*4
dec = subprocess.Popen(['ffmpeg','-v','error','-c:v','libvpx-vp9','-i',src,'-f','rawvideo','-pix_fmt','rgba','-'], stdout=subprocess.PIPE)
enc = subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgba','-s',f'{W}x{H}','-r','30','-i','-',
    '-c:v','libvpx-vp9','-b:v','0','-crf','14','-deadline','good','-row-mt','1','-cpu-used','4','-auto-alt-ref','0',
    '-pix_fmt','yuva420p','-metadata:s:v:0','alpha_mode=1',dst], stdin=subprocess.PIPE)
def frames():
    while True:
        b = dec.stdout.read(N)
        if len(b) < N: return
        yield b
def work(b):
    return fix(np.frombuffer(b, np.uint8).reshape(H, W, 4)).tobytes()
with Pool(3) as p:
    for k, out in enumerate(p.imap(work, frames(), chunksize=4)):
        enc.stdin.write(out)
        if k % 150 == 0: print('frame', k, flush=True)
enc.stdin.close(); enc.wait(); dec.wait(); print('done', k+1)
