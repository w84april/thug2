import {readFileSync,writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {verifyPhysicsStateActionsContext} from './physics_state_actions_context_wasm_checks.mjs';
const base=resolve(process.argv[2]??'local/validation/collision');
const result=await verifyPhysicsStateActionsContext(readFileSync('local/build/thug-core.wasm'),
 JSON.parse(readFileSync(base+'/physics-state-actions-context-fixtures.json','utf8')),name=>readFileSync(base+'/'+name));
writeFileSync(resolve(base,'../physics-state-actions-context-wasm.json'),JSON.stringify(result,null,2)+'\n');console.log(result);
