import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {verifyScriptState} from './skater-walk-checks.mjs';
const p='local/analysis/',load=n=>readFileSync(existsSync(p+n)?p+n:'local/validation/collision/'+n);
const controls=[];
for(const [module,suite] of [['walk-component-frame-draft.wasm','skater-local-net'],['skater-local-net-draft.wasm','skater-end-run-lifecycle'],['skater-end-run-draft.wasm','skater-end-run-startup']]) {
 let error;
 try {await verifyScriptState(readFileSync(p+module),JSON.parse(readFileSync(p+suite+'-fixtures.json')),load);} catch(e) {error=String(e);}
 if(!error)throw Error('Prior module falsely accepted '+suite);
 controls.push({module,suite,rejected:true,error});
}
const {instance:{exports:e}}=await WebAssembly.instantiate(readFileSync(p+'skater-end-run-startup-draft.wasm'));
const view=new DataView(e.memory.buffer),settings=0x1500000;
view.setUint32(settings+4,0,true);view.setUint32(settings+8,0,true);
let missing;
try {e.thug_end_run_settings_gate_draft(settings);} catch(e) {missing=String(e);}
if(missing!=='RuntimeError: unreachable')throw Error('Missing required setting did not stop: '+missing);
const result={result:'pass',controls,missing_required_boolean:{result:'explicit unsupported boundary',error:missing,counted_complete:false},playable:false};
writeFileSync(p+'skater-end-run-negative.json',JSON.stringify(result,null,2)+'\n');console.log(result);
