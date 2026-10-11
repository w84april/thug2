import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { verifyTriangles } from './triangle_wasm_checks.mjs';
const directory = process.argv[2];
const fixtures = JSON.parse(readFileSync(resolve(directory, 'triangle-fixtures.json'), 'utf8'));
const wasm = readFileSync(resolve(directory, '../../build/thug-core.wasm'));
console.log('WebAssembly triangles:', await verifyTriangles(wasm, fixtures,
  name => readFileSync(resolve(directory, name))));
