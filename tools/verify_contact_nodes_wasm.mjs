import {readFileSync,writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {verifyMotion} from './motion_wasm_checks.mjs';
const directory=process.argv[2];
const result=await verifyMotion(readFileSync(resolve(directory,'../../build/thug-core.wasm')),
  JSON.parse(readFileSync(resolve(directory,'contact-nodes-fixtures.json'),'utf8')),name=>readFileSync(resolve(directory,name)));
writeFileSync(resolve(directory,'../contact-nodes-wasm.json'),JSON.stringify(result,null,2)+'\n');
console.log('WebAssembly contact nodes:',result);
