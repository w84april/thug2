import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {resolve} from 'node:path';
import {verifyScriptState} from '../../tools/script_state_wasm_checks.mjs';
const base='local/analysis/';
const load=name=>readFileSync(existsSync(resolve(base,name))?resolve(base,name):resolve('local/validation/collision',name));
for(const name of ['scene-state','scene-disposal','scene-visitor']) {
 const fixture=JSON.parse(readFileSync(base+name+'-fixtures.json'));
 const result=await verifyScriptState(readFileSync(base+'scene-state-draft.wasm'),fixture,load);
 writeFileSync(base+name+'-result.json',JSON.stringify(result,null,2)+'\n');console.log(name,result);
}
