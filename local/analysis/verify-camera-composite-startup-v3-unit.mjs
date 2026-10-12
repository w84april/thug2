import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {resolve} from 'node:path';
import {verifyScriptState} from './skater-walk-checks.mjs';
const base='local/analysis/',name='camera-composite-startup-v3';
const load=n=>readFileSync(existsSync(resolve(base,n))?resolve(base,n):resolve('local/validation/collision',n));
const result=await verifyScriptState(readFileSync(base+'camera-composite-startup-v2.wasm'),JSON.parse(readFileSync(base+name+'-fixtures.json')),load);
writeFileSync(base+name+'-unit-result.json',JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(result));
