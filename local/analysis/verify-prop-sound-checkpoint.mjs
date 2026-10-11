import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {resolve} from 'node:path';
import {verifyScriptState as verifySetup} from './training-setup-checks.mjs';
import {verifyScriptState} from '../../tools/script_state_wasm_checks.mjs';
const base='local/analysis/',wasm=readFileSync(base+'prop-sound-draft.wasm');
const load=name=>readFileSync(existsSync(resolve(base,name))?resolve(base,name):resolve('local/validation/collision',name));
const names=process.argv.includes('--training-only')?['training-prop-components']:process.argv.includes('--math-only')?['composite-math']:process.argv.includes('--unit-only')?['prop-sound']:process.argv.includes('--new-only')?['prop-sound','training-prop-components','prop-lifecycle','composite-math','composite-construction']:['prop-sound','training-prop-components','prop-lifecycle','composite-math','composite-construction','node-registration','training-node-registration','node-index','training-node-index','scene-kill','scene-subscribe','scene-lifetime','scene-proximity','scene-state','scene-disposal','scene-visitor','training-mode','node-prefix','scene-name','training-setup','asset-factory','training-load','skeleton-asset','skeleton-buffer','script-change'];
for(const name of names) {
 const fixture=JSON.parse(readFileSync(base+name+'-fixtures.json'));
 const result=await (name==='training-setup'?verifySetup:verifyScriptState)(wasm,fixture,load);
 if(name==='training-load')Object.assign(result,{completed_setup_calls:4,completed_execute_calls:1,execute_result:0,final_instruction:0,ready_skeleton_bones:34,playable:false});
 if(name==='training-setup')Object.assign(result,{completed_setup_calls:10,interrupted_execute_calls:2,next_missing_handler:'Kill at 0x5a5030',playable:false});
 writeFileSync(base+'prop-sound-checkpoint-'+name+'-result.json',JSON.stringify(result,null,2)+'\n');
 console.log(name,result.result,result.cases,result.calls,result.nan_fields_classification_only);
}
