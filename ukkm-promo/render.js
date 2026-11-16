const {chromium}=require('playwright');
(async()=>{const [,,dir,out]=process.argv;const fps=30,N=Math.ceil(43.28*fps);
const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+dir+'/index.html');await p.evaluate(()=>document.fonts.ready);
for(let i=0;i<N;i++){await p.evaluate(t=>seek(t),i/fps);await p.screenshot({path:`${out}/f${String(i).padStart(5,'0')}.jpg`,type:'jpeg',quality:95});}
await b.close();})();
