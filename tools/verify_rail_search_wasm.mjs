import {readFileSync,writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {verifyScriptState} from './script_state_wasm_checks.mjs';
const base=resolve(process.argv[2]??'local/validation/collision');
const result=await verifyScriptState(readFileSync('local/build/thug-core.wasm'),
 JSON.parse(readFileSync(base+'/rail-search-fixtures.json','utf8')),name=>readFileSync(base+'/'+name));
writeFileSync(resolve(base,'../rail-search-wasm.json'),JSON.stringify(result,null,2)+'\n');console.log(result);
