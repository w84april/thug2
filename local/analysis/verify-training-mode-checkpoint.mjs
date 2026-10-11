import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {resolve} from 'node:path';
import {verifyScriptState as verifySetup} from './training-setup-checks.mjs';
import {verifyScriptState} from '../../tools/script_state_wasm_checks.mjs';
const base='local/analysis/',wasm=readFileSync(base+'training-mode-draft.wasm');
const load=name=>readFileSync(existsSync(resolve(base,name))?resolve(base,name):resolve('local/validation/collision',name));
for(const name of ['training-mode','node-prefix','scene-name','training-setup','asset-factory','training-load','skeleton-asset','skeleton-buffer','script-change']) {
 const fixture=JSON.parse(readFileSync(base+name+'-fixtures.json'));
 const result=await (name==='training-setup'?verifySetup:verifyScriptState)(wasm,fixture,load);
 if(name==='training-load')Object.assign(result,{completed_setup_calls:4,completed_execute_calls:1,execute_result:0,final_instruction:0,ready_skeleton_bones:34,playable:false});
 if(name==='training-setup')Object.assign(result,{completed_setup_calls:10,interrupted_execute_calls:2,next_missing_handler:'Kill at 0x5a5030',playable:false});
 writeFileSync(base+'training-mode-checkpoint-'+name+'-result.json',JSON.stringify(result,null,2)+'\n');
 console.log(name,result.result,result.cases,result.calls,result.nan_fields_classification_only);
}
