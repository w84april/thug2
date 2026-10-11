import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {resolve} from 'node:path';
import {verifyScriptState} from '../../tools/script_state_wasm_checks.mjs';
const base='local/analysis/';
const result=await verifyScriptState(readFileSync(base+'physics-movement-members-draft.wasm'),JSON.parse(readFileSync(base+'physics-movement-members-fixtures.json','utf8')),n=>readFileSync(existsSync(resolve(base,n))?resolve(base,n):resolve('local/validation/collision',n)));
writeFileSync(base+'physics-movement-members-result.json',JSON.stringify(result,null,2)+'\n');console.log(result);
