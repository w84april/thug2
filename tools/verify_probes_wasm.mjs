import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { verifyProbes } from './probe_wasm_checks.mjs';
const directory = process.argv[2];
const fixture = JSON.parse(readFileSync(resolve(directory, 'probe-fixtures.json'), 'utf8'));
const wasm = readFileSync(resolve(directory, '../../build/thug-core.wasm'));
console.log('WebAssembly collision probes:', await verifyProbes(wasm, fixture,
  name => readFileSync(resolve(directory, name))));
