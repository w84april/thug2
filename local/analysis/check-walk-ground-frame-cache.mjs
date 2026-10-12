// The cache must match at destruction, before later frames reuse its storage.
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {verifyScriptState} from './walk-ground-frame-checks.mjs';
const base='local/analysis/',wasm=readFileSync(base+'walk-ground-frame-draft.wasm');
const fixture=JSON.parse(readFileSync(base+'walk-ground-frame-fixtures.json'));
const selected=fixture.cases[77];
if(fixture.cache_capture!=='destructor-v1'||!selected.steps[0].stack_objects.length)throw Error('Missing live-cache evidence');
const load=n=>readFileSync(existsSync(base+n)?base+n:'local/validation/collision/'+n);
const results=[];
async function check(name,mutate,reject){
 const f={...structuredClone(fixture),cases:[structuredClone(selected)]};mutate(f,f.cases[0].steps[0]);let error;
 try{await verifyScriptState(wasm,f,load);}catch(e){error=String(e);}
 if(reject?!error||!reject.test(error):error)throw Error(`${name}: ${error??'unexpected pass'}`);
 results.push({name,result:'pass',rejected:Boolean(error),...(error?{error}:{})});
}
await check('unchanged live cache',()=>{});
await check('missing destruction record',(f,s)=>s.stack_objects=[],/cache observation count/);
await check('wrong live registry slot',(f,s)=>s.stack_objects[0].mask[1]=7,/cache live identity/);
await check('changed live cache field',(f,s)=>{
 const block=s.stack_objects[0].blocks.find(b=>b[0]===0xfc0);
 if(!block)throw Error('Missing cache counts');
 block[1]='ff'+block[1].slice(2);
},/automatic object \+fc0/);
await check('unknown observation boundary',f=>f.cache_capture='after-return',/Unknown cache observation boundary/);
const sha=n=>createHash('sha256').update(readFileSync(base+n)).digest('hex');
const report={result:'pass',checks:results.length,results,files:Object.fromEntries(['walk-ground-frame-checks.mjs','walk-ground-frame-cache-capture.c','walk-ground-frame-fixtures.json','walk-ground-frame-draft.wasm','probe-walk-ground-frame.py'].map(n=>[n,sha(n)]))};
writeFileSync(base+'walk-ground-frame-cache-checks.json',JSON.stringify(report,null,2)+'\n');console.log('PASS',results.length,'cache lifetime controls');
