// The preceding module must still stop at its preserved partial walking entry.
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {verifyScriptState} from './walk-ground-frame-checks.mjs';
const p='local/analysis/',fixture=JSON.parse(readFileSync(p+'walk-component-frame-fixtures.json'));
fixture.cases=fixture.cases.slice(0,1);fixture.case_labels=fixture.case_labels.slice(0,1);
let rejection;
try {
 await verifyScriptState(readFileSync(p+'walk-complete-update-draft.wasm'),fixture,n=>readFileSync(existsSync(p+n)?p+n:'local/validation/collision/'+n));
} catch(error) {
 if(!(error instanceof WebAssembly.RuntimeError)||!String(error).includes('unreachable'))throw error;
 rejection=String(error);
}
if(!rejection)throw Error('The old partial component unexpectedly completed the new component-loop fixture');
const report={result:'pass',prior_module:'walk-complete-update-draft.wasm',fixture:'walk-component-frame-fixtures.json',tested_cases:1,rejection,scope:'The original partial vtable update traps in the first component-loop movement case; the recovered full update is required.'};
writeFileSync(p+'walk-component-negative.json',JSON.stringify(report,null,2)+'\n');console.log(report);
