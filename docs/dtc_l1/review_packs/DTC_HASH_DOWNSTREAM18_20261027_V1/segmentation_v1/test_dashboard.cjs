// CPU-only DOM rendering checks; no browser network or simulator access.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const page=fs.readFileSync(process.argv[2]||'dashboard.html','utf8');
const payload=page.match(/<script id="payload" type="application\/json">([\s\S]*?)<\/script>/)[1];
const code=page.match(/<script>\s*([\s\S]*?)<\/script>/)[1];
const elements=new Map();
for(const id of ['payload','stamp','cards','missing','identity','sources','program','kernel','metric','download','semantic','chart','legend','chartnote','pairs','runs','mapping','evidence','segmentrows'])
 elements.set(id,{textContent:id==='payload'?payload:'',innerHTML:'',value:({program:'ATAX',kernel:'1',metric:'cpi'})[id],addEventListener(){}});
const ctx={document:{getElementById:id=>{assert(elements.has(id),'Unknown element '+id);return elements.get(id)}},console,setTimeout,URL,Blob};
vm.createContext(ctx);vm.runInContext(code,ctx);
let checks=0;
for(const program of ['ATAX','MVT','BICG'])for(const kernel of ['1','2'])for(const metric of ['cpi','dram','fifo','miss']){
 elements.get('program').value=program;elements.get('kernel').value=kernel;elements.get('metric').value=metric;vm.runInContext('update()',ctx);
 for(const id of ['pairs','runs','mapping','chart','segmentrows']){
  const value=elements.get(id).innerHTML;assert(value.length>20,id+' empty');assert(!value.includes('NaN'),id+' NaN');assert(!value.includes('undefined'),id+' undefined');checks++;
 }
 assert(elements.get('mapping').innerHTML.includes(program));checks++;
}
console.log(JSON.stringify({all_controls_pass:true,checks,case_count:JSON.parse(payload).cases.length}));
