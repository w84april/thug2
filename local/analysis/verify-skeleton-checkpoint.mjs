import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {resolve} from 'node:path';
import {verifyScriptState} from '../../tools/script_state_wasm_checks.mjs';
import {verifyScriptState as verifyStartup} from './training-startup-checks.mjs';
const base='local/analysis/',wasm=readFileSync(base+'skeleton-buffer-draft.wasm');
const load=name=>readFileSync(existsSync(resolve(base,name))?resolve(base,name):resolve('local/validation/collision',name));
for(const name of ['skeleton-buffer','script-change','training-startup']) {
 const fixture=JSON.parse(readFileSync(base+name+'-fixtures.json'));
 const result=await (name==='training-startup'?verifyStartup:verifyScriptState)(wasm,fixture,load);
 if(name==='training-startup')Object.assign(result,{completed_setup_calls:4,interrupted_execute_calls:1,next_missing_handler:'LoadSkeleton at 0x445640',playable:false});
 writeFileSync(base+'skeleton-checkpoint-'+name+'-result.json',JSON.stringify(result,null,2)+'\n');
 console.log(name,result.result,result.cases,result.calls,result.nan_fields_classification_only);
}
