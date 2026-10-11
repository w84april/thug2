import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { verifyMoving } from './moving_wasm_checks.mjs';
const directory = process.argv[2];
const fixture = JSON.parse(readFileSync(resolve(directory, 'moving-fixtures.json'), 'utf8'));
const wasm = readFileSync(resolve(directory, '../../build/thug-core.wasm'));
console.log('WebAssembly moving collision:', await verifyMoving(wasm, fixture,
  name => readFileSync(resolve(directory, name))));
