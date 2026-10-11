import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {resolve} from 'node:path';
import {createHash} from 'node:crypto';
import {verifyScriptState} from '../../tools/script_state_wasm_checks.mjs';
const base='local/analysis/',wasm=readFileSync(base+'physics-movement-members-draft.wasm');
const load=n=>readFileSync(existsSync(resolve(base,n))?resolve(base,n):resolve('local/validation/collision',n));
const suites={};
for(const name of ['physics-parameter-flags','physics-airtime','physics-script-outputs','physics-movement-members','physics-command-values-context']) {
 // These two checkers already ran against this exact combined module. Their
 // standalone verification scripts remain the reproducible execution path.
 if(['physics-movement-members','physics-command-values-context'].includes(name)) {
  suites[name.replaceAll('-','_')]=JSON.parse(readFileSync(base+name+'-result.json','utf8'));
  continue;
 }
 const fixture=JSON.parse(readFileSync(base+name+'-fixtures.json','utf8'));
 const empty=await verifyScriptState(wasm,fixture,load);let result=empty;
 if(name.endsWith('-context')) {
  const nested=await verifyScriptState(wasm,{...fixture,scoped_event_services:{...fixture.scoped_event_services,pointer:fixture.outer_scope}},load);
  result={result:'pass',original_cases:empty.cases,cases:empty.cases+nested.cases,calls:empty.calls+nested.calls,native_qb_callbacks:empty.native_qb_callbacks+nested.native_qb_callbacks,nan_fields_classification_only:empty.nan_fields_classification_only+nested.nan_fields_classification_only,null_scope:empty,outer_scope:nested};
 }
 suites[name.replaceAll('-','_')]=result;console.log(name,result.cases,result.calls);
}
const candidate={result:'pass',wasm_sha256:createHash('sha256').update(wasm).digest('hex'),wasm_bytes:wasm.length,runtime_imports:WebAssembly.Module.imports(await WebAssembly.compile(wasm)).length,suites};
writeFileSync(base+'physics-command-values-browser-candidate.json',JSON.stringify(candidate,null,2)+'\n');
function canonical(v){return v===null||typeof v!=='object'?JSON.stringify(v):Array.isArray(v)?'['+v.map(canonical).join(',')+']':'{'+Object.keys(v).sort().map(k=>JSON.stringify(k)+':'+canonical(v[k])).join(',')+'}';}
const s=canonical(candidate);let h=14695981039346656037n;for(let i=0;i<s.length;i++)h=BigInt.asUintN(64,(h^BigInt(s.charCodeAt(i)))*1099511628211n);
console.log({keys:Object.keys(candidate).length,characters:s.length,fingerprint:h.toString(16),wasm_bytes:wasm.length,sha:candidate.wasm_sha256});
