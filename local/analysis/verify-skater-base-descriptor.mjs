import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {verifyScriptState} from './skater-walk-checks.mjs';
const p='local/analysis/',load=n=>readFileSync(existsSync(p+n)?p+n:'local/validation/collision/'+n),fixture=JSON.parse(readFileSync(p+'skater-base-descriptor-fixtures.json'));
const result=await verifyScriptState(readFileSync(p+'skater-descriptor-corrected.wasm'),fixture,load);
writeFileSync(p+'skater-base-descriptor-unit.json',JSON.stringify(result,null,2)+'\n');
let rejection;try {await verifyScriptState(readFileSync(p+'skater-descriptor-negative.wasm'),fixture,load);}catch(error){rejection=String(error);}
if(!rejection?.includes('RuntimeError'))throw Error('Incorrect extended virtual unexpectedly passed: '+rejection);
writeFileSync(p+'skater-base-descriptor-negative.json',JSON.stringify({result:'pass',incorrect_virtual_rejected:true,rejection,counted_new_functions:0},null,2)+'\n');console.log(result,rejection);
for(const [name,out] of [['skater-local-net','skater-local-net-descriptor-candidate-unit.json'],['skater-end-run-lifecycle','skater-end-run-lifecycle-descriptor-candidate-unit.json'],['skater-end-run-startup','skater-end-run-startup-descriptor-candidate-unit.json']]) {
 const value=await verifyScriptState(readFileSync(p+'skater-descriptor-corrected.wasm'),JSON.parse(readFileSync(p+name+'-fixtures.json')),load);
 writeFileSync(p+out,JSON.stringify(value,null,2)+'\n');console.log(name,value.result,value.cases,value.calls);
}
