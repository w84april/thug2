import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { verifyCollision } from './collision_wasm_checks.mjs';

const fixturePath = process.argv[2];
const directory = dirname(fixturePath);
const fixture = JSON.parse(readFileSync(fixturePath, 'utf8'));
const wasm = readFileSync(resolve(directory, '../../build/thug-core.wasm'));
const report = await verifyCollision(wasm, fixture, name => readFileSync(resolve(directory, name)));
console.log('WebAssembly:', JSON.stringify(report));
