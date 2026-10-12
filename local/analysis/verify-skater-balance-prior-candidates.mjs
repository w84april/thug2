import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {verifyScriptState} from './skater-walk-checks.mjs';
const p='local/analysis/',w=readFileSync(p+'skater-balance-startup-draft.wasm');
for(const name of ['skater-base-descriptor','skater-local-net','skater-end-run-lifecycle','skater-end-run-startup']){
 const result=await verifyScriptState(w,JSON.parse(readFileSync(p+name+'-fixtures.json')),n=>readFileSync(existsSync(p+n)?p+n:'local/validation/collision/'+n));
 writeFileSync(p+name+'-balance-candidate-unit.json',JSON.stringify(result,null,2)+'\n');console.log(name,result.result,result.cases,result.calls);
}
