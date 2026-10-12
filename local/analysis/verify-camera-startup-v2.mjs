import {readFileSync,writeFileSync} from 'node:fs';
import {verifyScriptState} from './skater-walk-checks.mjs';
const p='local/analysis/',fixture=JSON.parse(readFileSync(p+'camera-startup-v2-fixtures.json'));
const result=await verifyScriptState(readFileSync(p+'camera-startup-v2.wasm'),fixture,n=>readFileSync(p+n));
writeFileSync(p+'camera-startup-v2-result.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
