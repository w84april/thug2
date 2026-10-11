import {readFileSync,writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {verifyComponentContext} from './component_context_wasm_checks.mjs';
const base=resolve(process.argv[2]??'local/validation/collision');
const result=await verifyComponentContext(readFileSync('local/build/thug-core.wasm'),
 JSON.parse(readFileSync(base+'/component-context-fixtures.json','utf8')),name=>readFileSync(base+'/'+name));
writeFileSync(resolve(base,'../component-context-wasm.json'),JSON.stringify(result,null,2)+'\n');console.log(result);
