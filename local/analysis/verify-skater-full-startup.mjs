import {readFileSync,writeFileSync} from 'node:fs';
import {verifyScriptState} from './skater-walk-checks.mjs';
const p='local/analysis/',fixture=JSON.parse(readFileSync(p+'skater-full-startup-fixtures.json'));
const result=await verifyScriptState(readFileSync(p+'skater-full-startup-draft.wasm'),fixture,n=>readFileSync(p+n));
writeFileSync(p+'skater-full-startup-result.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
