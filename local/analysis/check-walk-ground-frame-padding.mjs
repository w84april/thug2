// Negative controls for the only byte-specific comparison allowance.
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {verifyScriptState} from './walk-ground-frame-checks.mjs';
const base='local/analysis/',wasm=readFileSync(base+'walk-ground-frame-draft.wasm');
const fixture=JSON.parse(readFileSync(base+'walk-ground-frame-fixtures.json'));
const selected=fixture.cases.find(c=>c.steps.some(s=>s.indeterminate_bytes.length));
const stepIndex=selected?.steps.findIndex(s=>s.indeterminate_bytes.length);
if(!selected)throw Error('Missing populated-queue evidence');
const one=()=>({...structuredClone(fixture),cases:[{...structuredClone(selected),steps:structuredClone(selected.steps.slice(0,stepIndex+1))}]});
const load=n=>readFileSync(existsSync(base+n)?base+n:'local/validation/collision/'+n);
const results=[];
async function check(name,mutate,reject){
 const f=one();mutate(f,f.cases[0].steps[stepIndex]);let error;
 try{await verifyScriptState(wasm,f,load);}catch(e){error=String(e);}
 if(reject?!error||!reject.test(error):error)throw Error(`${name}: ${error??'unexpected pass'}`);
 results.push({name,result:'pass',rejected:Boolean(error),...(error?{error}:{})});
}
await check('unchanged populated queue',()=>{});
await check('padding contents are unspecified',(f,s)=>s.outputs.push([s.payload_provenance[0].destination,'fa']));
await check('speed bytes remain exact',(f,s)=>s.outputs.push([s.payload_provenance[0].payload,'fa']),/word|byte/);
await check('object ID remains exact',(f,s)=>s.outputs.push([s.payload_provenance[0].payload+4,'fa']),/word|byte/);
await check('missing original-write evidence',(f,s)=>s.payload_provenance=[],/incomplete payload-byte/);
await check('wrong copy instruction',(f,s)=>s.payload_provenance[0].copy_instruction='0x455010',/invalid payload-byte/);
await check('defined source byte cannot be waived',(f,s)=>s.payload_provenance[0].source_writes_before_copy=1,/invalid payload-byte/);
await check('unlisted address cannot be waived',f=>f.indeterminate_byte_addresses=[],/invalid payload-byte/);
await check('ID cannot be widened into padding',(f,s)=>{
 const r={...s.payload_provenance[0],destination:s.payload_provenance[0].payload+4,source_offset:4};
 f.indeterminate_byte_addresses.push(r.destination);s.indeterminate_bytes.push(r.destination);s.payload_provenance.push(r);
},/invalid payload-byte/);
await check('source must be an original stack address',(f,s)=>s.payload_provenance[0].source=0,/invalid payload-byte/);
await check('defined prefix requires observed writes',(f,s)=>s.payload_provenance[0].defined_prefix_writes[4]=0,/invalid payload-byte/);
await check('duplicate proof rejected',(f,s)=>s.payload_provenance.push({...s.payload_provenance[0]}),/invalid payload-byte/);
const sha=n=>createHash('sha256').update(readFileSync(base+n)).digest('hex');
const report={result:'pass',checks:results.length,results,files:Object.fromEntries(['walk-ground-frame-checks.mjs','walk-speed-checks.mjs','walk-ground-frame-fixtures.json','walk-ground-frame-draft.wasm','probe-walk-ground-frame.py'].map(n=>[n,sha(n)]))};
writeFileSync(base+'walk-ground-frame-padding-checks.json',JSON.stringify(report,null,2)+'\n');console.log('PASS',results.length,'payload padding controls');
