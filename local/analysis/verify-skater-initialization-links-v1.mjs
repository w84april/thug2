import {readFileSync,writeFileSync} from 'node:fs';
import {verifyScriptState} from './skater-walk-checks.mjs';
const p='local/analysis/',fixture=JSON.parse(readFileSync(p+'skater-initialization-links-v1-fixtures.json'));
const result=await verifyScriptState(readFileSync(p+'skater-initialization-links-v1.wasm'),fixture,n=>readFileSync(p+n));
writeFileSync(p+'skater-initialization-links-v1-result.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
