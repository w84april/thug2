import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {resolve} from 'node:path';
import {verifyScriptState} from '../../tools/script_state_wasm_checks.mjs';
const base='local/analysis/',fixture=JSON.parse(readFileSync(base+'script-change-fixtures.json'));
const load=name=>readFileSync(existsSync(resolve(base,name))?resolve(base,name):resolve('local/validation/collision',name));
const result=await verifyScriptState(readFileSync(base+'script-change-draft.wasm'),fixture,load);
writeFileSync(base+'script-change-result.json',JSON.stringify(result,null,2)+'\n');console.log(result);
