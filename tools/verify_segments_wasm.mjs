import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { verifySegments } from './segment_wasm_checks.mjs';
const directory = process.argv[2];
const fixture = JSON.parse(readFileSync(resolve(directory, 'segment-fixtures.json'), 'utf8'));
const wasm = readFileSync(resolve(directory, '../../build/thug-core.wasm'));
console.log('WebAssembly static collision:', await verifySegments(wasm, fixture,
  name => readFileSync(resolve(directory, name))));
