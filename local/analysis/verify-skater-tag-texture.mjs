import {readFileSync,writeFileSync} from 'node:fs';
import {verifyScriptState} from '../../tools/script_state_wasm_checks.mjs';
const p='local/analysis/',fixture=JSON.parse(readFileSync(p+'skater-tag-texture-fixtures.json'));
const result=await verifyScriptState(readFileSync(p+'skater-tag-texture-draft.wasm'),fixture,n=>readFileSync(p+n));
writeFileSync(p+'skater-tag-texture-result.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
