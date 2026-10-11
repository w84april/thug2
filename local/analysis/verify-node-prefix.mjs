import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {resolve} from 'node:path';
import {verifyScriptState} from '../../tools/script_state_wasm_checks.mjs';
const base='local/analysis/',fixture=JSON.parse(readFileSync(base+'node-prefix-fixtures.json'));
const load=name=>readFileSync(existsSync(resolve(base,name))?resolve(base,name):resolve('local/validation/collision',name));
const result=await verifyScriptState(readFileSync(base+'training-mode-draft.wasm'),fixture,load);
writeFileSync(base+'node-prefix-result.json',JSON.stringify(result,null,2)+'\n');console.log(result);
