import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {verifySkater} from './skater_wasm_checks.mjs';
const directory=process.argv[2];
console.log('WebAssembly skater routines:',await verifySkater(readFileSync(resolve(directory,'../../build/thug-core.wasm')),
  JSON.parse(readFileSync(resolve(directory,'skater-fixtures.json'),'utf8')),name=>readFileSync(resolve(directory,name))));
