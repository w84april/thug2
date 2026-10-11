import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {verifySurface} from './surface_wasm_checks.mjs';
const directory=process.argv[2];
console.log('WebAssembly skater surface:',await verifySurface(readFileSync(resolve(directory,'../../build/thug-core.wasm')),
  JSON.parse(readFileSync(resolve(directory,'surface-fixtures.json'),'utf8')),name=>readFileSync(resolve(directory,name))));
