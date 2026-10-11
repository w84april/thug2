import {readFileSync,writeFileSync} from 'node:fs';
import {verifyScriptState} from '../../tools/script_state_wasm_checks.mjs';
const base='local/analysis/';
const result=await verifyScriptState(readFileSync(base+'physics-script-values-draft.wasm'),JSON.parse(readFileSync(base+'physics-script-outputs-fixtures.json','utf8')),n=>readFileSync(base+n));
writeFileSync(base+'physics-script-outputs-result.json',JSON.stringify(result,null,2)+'\n');console.log(result);
