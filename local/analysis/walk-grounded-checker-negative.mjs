// Mutations must be rejected except for explicitly proven undefined fields.
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {verifyScriptState} from './walk-ledge-checks.mjs';
const base='local/analysis/',wasm=readFileSync(base+'walk-grounded-draft.wasm');
const original=JSON.parse(readFileSync(base+'walk-grounded-fixtures.json'));
const chosen=original.cases.findIndex(c=>c.steps[0]?.fn==='0x52d300'&&c.steps[0].indeterminate_provenance?.some(r=>r.source_offset===0x70));
if(chosen<0)throw Error('No cached-probe provenance case');
const load=name=>readFileSync(existsSync(base+name)?base+name:'local/validation/collision/'+name);
const fixture=()=>({...structuredClone(original),cases:[structuredClone(original.cases[chosen])]});
const set=(step,at,value)=>{const text=Buffer.alloc(4);text.writeUInt32LE(value>>>0);const old=step.outputs.find(r=>r[0]===at);if(old)old[1]=text.toString('hex');else step.outputs.push([at,text.toString('hex')]);};
const results=[];
await verifyScriptState(wasm,fixture(),load);
async function reject(label,modify){
 const f=fixture();modify(f,f.cases[0].steps[0]);
 try{await verifyScriptState(wasm,f,load);}catch(error){results.push({label,rejected:true,message:String(error.message)});return;}
 throw Error('Corruption accepted: '+label);
}
await reject('defined floor normal',(f,s)=>set(s,0x18c1798,0xdeadbeef));
await reject('stored probe pointer',(f,s)=>set(s,s.stack_pointer_fields[0].field,0));
await reject('missing field provenance',(f,s)=>s.indeterminate_provenance.pop());
await reject('wrong source field',(f,s)=>s.indeterminate_provenance[0].source_offset=0x74);
await reject('defined field given an allowance',(f,s)=>{s.indeterminate_words.push(0x18c1798);f.indeterminate_word_addresses.push(0x18c1798);s.indeterminate_provenance.push({...s.indeterminate_provenance[0],destination:0x18c1798});});
await reject('missing source probe identity',(f,s)=>s.stack_pointer_fields=[]);
const allowed=fixture(),step=allowed.cases[0].steps[0];
for(const at of step.indeterminate_words)set(step,at,0xdeadbeef);
await verifyScriptState(wasm,allowed,load);
const report={result:'pass',corruptions_rejected:results.length,undefined_word_mutation_accepted:true,case_index:chosen,checks:results};
writeFileSync(base+'walk-grounded-checker-negative.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
