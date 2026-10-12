import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {verifyScriptState} from './skater-walk-checks.mjs';
const p='local/analysis/',name='skater-balance-lifecycle',wasm=readFileSync(p+'skater-balance-startup-draft.wasm');
const fixture=JSON.parse(readFileSync(p+name+'-fixtures.json'));
const result=await verifyScriptState(wasm,fixture,n=>readFileSync(existsSync(p+n)?p+n:'local/validation/collision/'+n));
writeFileSync(p+name+'-unit.json',JSON.stringify(result,null,2)+'\n');console.log(result);
