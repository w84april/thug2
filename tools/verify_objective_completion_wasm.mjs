import {readFileSync,writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {verifyScriptState} from './script_state_wasm_checks.mjs';
const directory=process.argv[2];
const result=await verifyScriptState(readFileSync(resolve(directory,'../../build/thug-core.wasm')),
 JSON.parse(readFileSync(resolve(directory,'objective-completion-fixtures.json'),'utf8')),name=>readFileSync(resolve(directory,name)));
writeFileSync(resolve(directory,'../objective-completion-wasm.json'),JSON.stringify(result,null,2)+'\n');
console.log('WebAssembly goal completion:',result);
