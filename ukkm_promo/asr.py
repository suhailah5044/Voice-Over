import sys
from faster_whisper import WhisperModel
m=WhisperModel('small',device='cpu',compute_type='int8')
for f in sys.argv[1:]:
    print('=====',f)
    import wave,numpy as np; w=wave.open(f); a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
    segs,_=m.transcribe(a,language='ms',word_timestamps=True,vad_filter=False)
    for s in segs:
        print(f'[{s.start:6.2f}-{s.end:6.2f}] {s.text}')
        print('   ', ' '.join(f'{w.word.strip()}@{w.start:.2f}' for w in s.words))
