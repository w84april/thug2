import {readFileSync,writeFileSync} from 'node:fs';
import {verifyScriptState} from '../../tools/script_state_wasm_checks.mjs';
const base='local/analysis/';
const result=await verifyScriptState(readFileSync(base+'physics-parameter-flags-draft.wasm'),
 JSON.parse(readFileSync(base+'physics-parameter-flags-fixtures.json','utf8')),name=>readFileSync(base+name));
writeFileSync(base+'physics-parameter-flags-result.json',JSON.stringify(result,null,2)+'\n');console.log(result);
