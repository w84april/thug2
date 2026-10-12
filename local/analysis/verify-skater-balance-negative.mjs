import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {verifyScriptState} from './skater-walk-checks.mjs';
const p='local/analysis/',fixture=JSON.parse(readFileSync(p+'skater-balance-lifecycle-fixtures.json')),load=n=>readFileSync(existsSync(p+n)?p+n:'local/validation/collision/'+n);
let rejection;try{await verifyScriptState(readFileSync(p+'skater-balance-no-qb-negative.wasm'),fixture,load);}catch(e){rejection=String(e);}
if(!rejection?.includes('case 1 step 0 pointer'))throw Error('Missing conditional QB control unexpectedly passed: '+rejection);
const report={result:'pass',missing_conditional_qb_rejected:true,rejection,counted_new_functions:0};
writeFileSync(p+'skater-balance-lifecycle-negative.json',JSON.stringify(report,null,2)+'\n');console.log(report);
