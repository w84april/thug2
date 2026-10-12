import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {verifyScriptState} from './skater-walk-checks.mjs';
const p='local/analysis/',name='skater-local-net';
const result=await verifyScriptState(readFileSync(p+'skater-end-run-startup-draft.wasm'),JSON.parse(readFileSync(p+name+'-fixtures.json')),n=>readFileSync(existsSync(p+n)?p+n:'local/validation/collision/'+n));
writeFileSync(p+name+'-end-run-candidate-unit.json',JSON.stringify(result,null,2)+'\n');console.log(result);
