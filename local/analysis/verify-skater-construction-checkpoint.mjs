import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {resolve} from 'node:path';
import {verifyScriptState as verifyTrainingTexture} from './lock-frame-training-checks.mjs';
import {verifyScriptState as verifySetup} from './training-setup-checks.mjs';
import {verifyScriptState} from '../../tools/script_state_wasm_checks.mjs';
import {verifyScriptState as verifyPropScript} from './training-prop-script-checks.mjs';
import {verifyScriptState as verifyModel} from './training-model-component-checks.mjs';
import {verifyScriptState as verifyPrefix} from './model-initialize-prefix-checks.mjs';
import {verifyInputCommands} from './input-command-checks.mjs';
const base='local/analysis/',wasm=readFileSync(base+'skater-construction-draft.wasm');
const load=name=>readFileSync(existsSync(resolve(base,name))?resolve(base,name):resolve('local/validation/collision',name));
const inherited=Object.keys(JSON.parse(readFileSync(base+'input-command-browser.json')).observed.suites).map(n=>n.replaceAll('_','-'));
const names=process.argv.includes('--unit-only')?['skater-construction']:process.argv.includes('--inherited')?inherited:[ 'skater-construction',...inherited];
for(const name of names) {
 const fixture=JSON.parse(readFileSync(base+name+'-fixtures.json'));
 const result=await (name==='skater-construction'?verifyPrefix:name==='input-command'?verifyInputCommands:['rigidbody-update-training','rigidbody-update-active-training','motion-rotation-training','particle-dispatch-training','lock-frame-training','proximity-frame-training','motion-frame-training','particle-setup-training','particle-image-training','particle-create-training','particle-engine-training','particle-component-training','rigidbody-initialize-training','level-collision-component','level-collision-load','level-object-startup','training-scene-create','training-model-transform','training-renderer-bounds','training-render-instance','training-asset-ready','training-texture-asset','training-model-file','training-material-buffer','training-scene-construction','training-mesh-index','training-vertex-upload','training-mesh-register','training-scene-finalize'].includes(name)?verifyTrainingTexture:name==='training-setup'?verifySetup:name==='training-prop-script'?verifyPropScript:['model-initialize-prefix','model-configuration-prefix'].includes(name)?verifyPrefix:['training-model-component','training-model-initialize','training-model-configuration'].includes(name)?verifyModel:verifyScriptState)(wasm,fixture,load);
 if(name==='training-load')Object.assign(result,{completed_setup_calls:4,completed_execute_calls:1,execute_result:0,final_instruction:0,ready_skeleton_bones:34,playable:false});
 if(name==='training-setup')Object.assign(result,{completed_setup_calls:10,interrupted_execute_calls:2,next_missing_handler:'Kill at 0x5a5030',playable:false});
 writeFileSync(base+'skater-construction-checkpoint-'+name+'-result.json',JSON.stringify(result,null,2)+'\n');
 console.log(name,result.result,result.cases,result.calls,result.nan_fields_classification_only);
}
