import {readFileSync,writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {verifyScriptState} from './script_state_wasm_checks.mjs';
import {verifyCompression} from './compression_wasm_checks.mjs';
const directory=process.argv[2];
const result=await verifyCompression(readFileSync(resolve(directory,'../../build/thug-core.wasm')),
  JSON.parse(readFileSync(resolve(directory,'compression-fixtures.json'),'utf8')),name=>readFileSync(resolve(directory,name)),verifyScriptState);
writeFileSync(resolve(directory,'../compression-wasm.json'),JSON.stringify(result,null,2)+'\n');
console.log('WebAssembly compression:',result);
