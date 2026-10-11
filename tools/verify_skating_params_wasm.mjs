import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {verifySkatingParams} from './skating_params_wasm_checks.mjs';
const directory=process.argv[2];
console.log('WebAssembly skating parameters:',await verifySkatingParams(readFileSync(resolve(directory,'../../build/thug-core.wasm')),
  JSON.parse(readFileSync(resolve(directory,'skating-params-fixtures.json'),'utf8')),name=>readFileSync(resolve(directory,name))));
