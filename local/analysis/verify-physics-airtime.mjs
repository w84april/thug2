import {readFileSync,writeFileSync} from 'node:fs';
import {verifyScriptState} from '../../tools/script_state_wasm_checks.mjs';
const base='local/analysis/';
const result=await verifyScriptState(readFileSync(base+'physics-script-values-draft.wasm'),JSON.parse(readFileSync(base+'physics-airtime-fixtures.json','utf8')),n=>readFileSync(base+n));
writeFileSync(base+'physics-airtime-result.json',JSON.stringify(result,null,2)+'\n');console.log(result);
