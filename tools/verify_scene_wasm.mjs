import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { verifyScene } from './scene_wasm_checks.mjs';
const directory = process.argv[2];
const fixture = JSON.parse(readFileSync(resolve(directory, 'scene-fixtures.json'), 'utf8'));
const wasm = readFileSync(resolve(directory, '../../build/thug-core.wasm'));
console.log('WebAssembly scene collision:', await verifyScene(wasm, fixture,
  name => readFileSync(resolve(directory, name))));
