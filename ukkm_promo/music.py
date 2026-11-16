import numpy as np, json, wave, sys
S=sys.argv[1]; END=json.load(open(f'{S}/timing.json'))['end']
sr=44100; n=int(END*sr); t=np.arange(n)/sr; out=np.zeros(n)
bpm=120; beat=60/bpm
def add(sig,start):
    i=int(start*sr); j=min(n,i+len(sig)); out[i:j]+=sig[:j-i]
kt=np.arange(int(0.25*sr))/sr
kick=np.sin(2*np.pi*(50+90*np.exp(-kt*30))*kt)*np.exp(-kt*12)
ht=np.arange(int(0.05*sr))/sr; hat=np.random.randn(len(ht))*np.exp(-ht*80)*0.25
prog=[(220.0,277.18,329.63),(174.61,220.0,261.63),(130.81,164.81,196.0),(196.0,246.94,293.66)]  # A F C G
k=0
while k*beat<END:
    s=k*beat; add(kick*0.9,s); add(hat,s+beat/2)
    if k%4==0:
        ch=prog[(k//4)%4]; ct=np.arange(int(4*beat*sr))/sr
        env=np.minimum(1,ct*8)*np.exp(-ct*0.4)
        pad=sum(np.sin(2*np.pi*f*ct)+0.3*np.sin(2*np.pi*f*2*ct) for f in ch)*env*0.08
        bass=np.sign(np.sin(2*np.pi*ch[0]/2*ct))*0.12*env
        add(pad+bass,s)
    k+=1
fade=np.minimum(1,(END-t)/1.5); out*=np.clip(fade,0,1)*np.minimum(1,t/0.3)
out=out/np.abs(out).max()*0.9
w=wave.open(f'{S}/music.wav','wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
w.writeframes((out*32767).astype(np.int16).tobytes()); w.close()
