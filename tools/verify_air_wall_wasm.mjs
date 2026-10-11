import {readFileSync,writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {verifyScriptState} from './script_state_wasm_checks.mjs';
const directory=process.argv[2];
const fixture=JSON.parse(readFileSync(resolve(directory,'air-wall-fixtures.json'),'utf8'));
const result=await verifyScriptState(readFileSync(resolve(directory,'../../build/thug-core.wasm')),fixture,name=>readFileSync(resolve(directory,name)));
writeFileSync(resolve(directory,'../air-wall-wasm.json'),JSON.stringify(result,null,2)+'\n');
console.log('WebAssembly air-wall:',result);
