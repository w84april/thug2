import {readFileSync,existsSync} from 'node:fs';
import {verifyScriptState} from './particle-setup-debug-checks.mjs';
const base='local/analysis/';
const load=n=>readFileSync(existsSync(base+n)?base+n:'local/validation/collision/'+n);
console.log(await verifyScriptState(load('particle-setup-draft.wasm'),JSON.parse(load('particle-setup-training-fixtures.json')),load));
