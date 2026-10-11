import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { verifyGeometry } from './geometry_wasm_checks.mjs';
const directory = process.argv[2];
const fixtures = JSON.parse(readFileSync(resolve(directory, 'geometry-fixtures.json'), 'utf8'));
const wasm = readFileSync(resolve(directory, '../../build/thug-core.wasm'));
console.log('WebAssembly geometry:', await verifyGeometry(wasm, fixtures, name => readFileSync(resolve(directory, name))));
