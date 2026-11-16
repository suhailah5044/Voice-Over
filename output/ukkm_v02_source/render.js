const {chromium}=require('playwright');
const [,,html,out,mode,dur]=process.argv;
(async()=>{
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
 await p.goto('file://'+html); await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(500);
 const times = mode==='stills' ? [2.8,5.3,8.5,10.4,13.5,17.8,22.5,25.3,29,32,36.2] : null;
 const fs=require('fs');
 if(times){ for(const t of times){await p.evaluate(t=>render(t),t); await p.screenshot({path:`${out}/s_${t}.png`});} }
 else { const N=Math.ceil(+dur*30); for(let i=0;i<N;i++){await p.evaluate(t=>render(t),i/30); await p.screenshot({path:`${out}/f_${String(i).padStart(5,'0')}.jpg`,type:'jpeg',quality:95});} }
 await b.close();
})();
