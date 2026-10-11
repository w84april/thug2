import {readFileSync,writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {verifyRepulsion} from './repulsion_wasm_checks.mjs';
const directory=process.argv[2];
const result=await verifyRepulsion(readFileSync(resolve(directory,'../../build/thug-core.wasm')),
  JSON.parse(readFileSync(resolve(directory,'repulsion-fixtures.json'),'utf8')),name=>readFileSync(resolve(directory,name)));
writeFileSync(resolve(directory,'../repulsion-wasm.json'),JSON.stringify(result,null,2)+'\n');console.log('WebAssembly repulsion:',result);
