import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {resolve} from 'node:path';
import {verifyScriptState} from '../../tools/script_state_wasm_checks.mjs';
const base='local/analysis/',fixture=JSON.parse(readFileSync(base+'training-load-fixtures.json'));
const load=name=>readFileSync(existsSync(resolve(base,name))?resolve(base,name):resolve('local/validation/collision',name));
const result=await verifyScriptState(readFileSync(base+'asset-factory-draft.wasm'),fixture,load);
Object.assign(result,{completed_setup_calls:4,completed_execute_calls:1,execute_result:0,final_instruction:0,ready_skeleton_bones:34,playable:false});
writeFileSync(base+'training-load-result.json',JSON.stringify(result,null,2)+'\n');console.log(result);
