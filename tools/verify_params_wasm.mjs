import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {verifyParams} from './params_wasm_checks.mjs';
const directory=process.argv[2];
console.log('WebAssembly script parameters:',await verifyParams(readFileSync(resolve(directory,'../../build/thug-core.wasm')),
  JSON.parse(readFileSync(resolve(directory,'params-fixtures.json'),'utf8')),name=>readFileSync(resolve(directory,name))));
