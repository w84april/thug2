import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {verifyOrientation} from './orientation_wasm_checks.mjs';
const directory=process.argv[2];
console.log('WebAssembly skater orientation:',await verifyOrientation(readFileSync(resolve(directory,'../../build/thug-core.wasm')),
  JSON.parse(readFileSync(resolve(directory,'orientation-fixtures.json'),'utf8')),name=>readFileSync(resolve(directory,name))));
