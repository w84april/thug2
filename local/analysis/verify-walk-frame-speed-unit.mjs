import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {verifyScriptState} from './walk-speed-checks.mjs';
const p='local/analysis/',name=process.argv[2]??'walk-frame-speed';
const result=await verifyScriptState(readFileSync(p+'walk-frame-speed-draft.wasm'),JSON.parse(readFileSync(p+name+'-fixtures.json')),n=>readFileSync(existsSync(p+n)?p+n:'local/validation/collision/'+n));
writeFileSync(p+name+'-unit.json',JSON.stringify(result,null,2)+'\n');console.log(result);
