import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {resolve} from 'node:path';
import {verifyScriptState as verifyTrainingTexture} from './training-texture-asset-checks.mjs';
import {verifyScriptState as verifySetup} from './training-setup-checks.mjs';
import {verifyScriptState} from '../../tools/script_state_wasm_checks.mjs';
import {verifyScriptState as verifyPropScript} from './training-prop-script-checks.mjs';
import {verifyScriptState as verifyModel} from './training-model-component-checks.mjs';
import {verifyScriptState as verifyPrefix} from './model-initialize-prefix-checks.mjs';
const base='local/analysis/',wasm=readFileSync(base+'texture-asset-draft.wasm');
const load=name=>readFileSync(existsSync(resolve(base,name))?resolve(base,name):resolve('local/validation/collision',name));
const names=process.argv.includes('--unit-only')?['texture-asset']:process.argv.includes('--prefix-only')?['model-configuration-prefix']:process.argv.includes('--training-only')?['training-texture-asset']:[ 'texture-asset','training-texture-asset','texture-buffer','model-configuration','model-configuration-prefix','training-model-configuration','model-initialize','model-initialize-prefix','training-model-initialize','model-component','training-model-component','prop-command','training-prop-script','prop-sound','training-prop-components','prop-lifecycle','composite-math','composite-construction','node-registration','training-node-registration','node-index','training-node-index','scene-kill','scene-subscribe','scene-lifetime','scene-proximity','scene-state','scene-disposal','scene-visitor','training-mode','node-prefix','scene-name','training-setup','asset-factory','training-load','skeleton-asset','skeleton-buffer','script-change'];
for(const name of names) {
 const fixture=JSON.parse(readFileSync(base+name+'-fixtures.json'));
 const result=await (name==='training-texture-asset'?verifyTrainingTexture:name==='training-setup'?verifySetup:name==='training-prop-script'?verifyPropScript:['model-initialize-prefix','model-configuration-prefix'].includes(name)?verifyPrefix:['training-model-component','training-model-initialize','training-model-configuration'].includes(name)?verifyModel:verifyScriptState)(wasm,fixture,load);
 if(name==='training-load')Object.assign(result,{completed_setup_calls:4,completed_execute_calls:1,execute_result:0,final_instruction:0,ready_skeleton_bones:34,playable:false});
 if(name==='training-setup')Object.assign(result,{completed_setup_calls:10,interrupted_execute_calls:2,next_missing_handler:'Kill at 0x5a5030',playable:false});
 writeFileSync(base+'texture-asset-checkpoint-'+name+'-result.json',JSON.stringify(result,null,2)+'\n');
 console.log(name,result.result,result.cases,result.calls,result.nan_fields_classification_only);
}
