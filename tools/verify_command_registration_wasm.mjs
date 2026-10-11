import {readFileSync,writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {verifyJumpContext} from './jump_context_wasm_checks.mjs';
const base=resolve(process.argv[2]??'local/validation/collision');
const result=await verifyJumpContext(readFileSync('local/build/thug-core.wasm'),
 JSON.parse(readFileSync(base+'/command-registration-fixtures.json','utf8')),name=>readFileSync(base+'/'+name));
writeFileSync(resolve(base,'../command-registration-wasm.json'),JSON.stringify(result,null,2)+'\n');console.log(result);
