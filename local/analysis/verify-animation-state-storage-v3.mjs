import {readFileSync,writeFileSync} from 'node:fs';
import {verifyScriptState} from './skater-walk-checks.mjs';
const p='local/analysis/',fixture=JSON.parse(readFileSync(p+'animation-state-storage-v3-fixtures.json'));
const result=await verifyScriptState(readFileSync(p+'animation-state-storage-v1.wasm'),fixture,n=>readFileSync(p+n));
writeFileSync(p+'animation-state-storage-v3-result.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
