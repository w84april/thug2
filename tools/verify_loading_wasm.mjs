import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { verifyLoading } from './loading_wasm_checks.mjs';
const directory = process.argv[2];
const fixture = JSON.parse(readFileSync(resolve(directory, 'loading-fixtures.json'), 'utf8'));
const wasm = readFileSync(resolve(directory, '../../build/thug-core.wasm'));
console.log('WebAssembly collision loading:', await verifyLoading(wasm, fixture,
  name => readFileSync(resolve(directory, name))));
