import sys, subprocess, json
from gtts import gTTS
out = sys.argv[1]
lines = [
 "Anak nak masuk MRSM? Jom sertai kelas Last Minute U K K M, Ujian Khas Kemasukan MRSM, secara online di Zoom!",
 "Empat hari intensif, enam belas hingga sembilan belas November, Isnin hingga Khamis.",
 "Setiap malam, tiga subjek.",
 "Sains, bersama Cikgu Shukry, pukul enam petang.",
 "Keperibadian, bersama Sir Koala, pukul lapan malam.",
 "Matematik, bersama G B Shahril, pukul sembilan tiga puluh lima malam.",
 "Hanya enam puluh ringgit sehari, atau ambil pakej penuh, seratus sembilan puluh sembilan ringgit sahaja!",
 "Daftar sekarang bersama Fly High Education Centre!",
]
durs=[]
for i,t in enumerate(lines):
    gTTS(t, lang='ms').save(f'{out}/raw{i}.mp3')
    # speed up 1.18x, trim silence, to wav
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',f'{out}/raw{i}.mp3','-af',
      'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,atempo=1.18',
      '-ar','44100','-ac','1',f'{out}/vo{i}.wav'],check=True)
    d=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f'{out}/vo{i}.wav']))
    durs.append(d)
json.dump(durs, open(f'{out}/durs.json','w'))
print(durs)
