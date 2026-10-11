import {readFileSync,writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {verifyGround} from './ground_wasm_checks.mjs';
const directory=process.argv[2];
const result=await verifyGround(readFileSync(resolve(directory,'../../build/thug-core.wasm')),
  JSON.parse(readFileSync(resolve(directory,'ground-fixtures.json'),'utf8')),name=>readFileSync(resolve(directory,name)));
writeFileSync(resolve(directory,'../ground-wasm.json'),JSON.stringify(result,null,2)+'\n');console.log('WebAssembly ground:',result);
