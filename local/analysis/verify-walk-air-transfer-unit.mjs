import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {verifyScriptState} from './walk-ground-frame-checks.mjs';
const p='local/analysis/',name=process.argv[2]??'walk-air-transfer';
const result=await verifyScriptState(readFileSync(p+'walk-air-transfer-draft.wasm'),JSON.parse(readFileSync(p+name+'-fixtures.json')),n=>readFileSync(existsSync(p+n)?p+n:'local/validation/collision/'+n));
writeFileSync(p+name+'-unit.json',JSON.stringify(result,null,2)+'\n');console.log(result);
