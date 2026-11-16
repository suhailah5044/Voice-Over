const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage();await p.goto('file://'+process.argv[2]+'/gen.html');
const r=await p.evaluate(()=>{const o={sc:S.map(s=>s.s),ends:S.map(s=>s.e),sfx:[],pops:[],big:[],hits:S.flatMap(s=>s.shakes),panic:S.filter(s=>s.sp.panic).map(s=>[s.s,s.e])};
 S.forEach(s=>{s.v.querySelectorAll('[data-t]').forEach(n=>{const t=+n.dataset.t;if(n.dataset.sfx)o.sfx.push([n.dataset.sfx,t]);else if(['pop','slide','stamp'].includes(n.dataset.a))o.pops.push(t)});
  s.el.querySelectorAll('.w.b[data-t]').forEach(n=>o.big.push(+n.dataset.t));});
 return o});
console.log(JSON.stringify(r));await b.close();})();
