// Require the new global quieting rule to reject changed payloads/signs and
// to leave the integer-copied X lane untouched; no NaN classification shortcut.
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {resolve} from 'node:path';
import assert from 'node:assert/strict';
import {verifyScriptState} from './skater-cleanup-checks.mjs';
const base='local/analysis/',wasm=readFileSync(base+'skater-cleanup-draft.wasm'),full=JSON.parse(readFileSync(base+'skater-cleanup-fixtures.json'));
const load=n=>readFileSync(existsSync(resolve(base,n))?resolve(base,n):resolve('local/validation/collision',n));
const indices=[0,1,2].map(l=>full.globals.findIndex(row=>row[1]===0x70166c+4*l));
const c=full.cases[full.case_labels.indexOf('global alias/0')];assert(c);
const fixture={...full,cases:[c]};const baseline=await verifyScriptState(wasm,fixture,load);assert.equal(baseline.nan_fields_classification_only,0);
const rejected=[];
for(const [lane,mask] of [[0,0x400000],[1,1],[1,0x80000000],[2,1],[2,0x80000000]]){
 const f=structuredClone(fixture);f.cases[0].steps[0].globals[indices[lane]]=(f.cases[0].steps[0].globals[indices[lane]]^mask)>>>0;
 await assert.rejects(verifyScriptState(wasm,f,load),/global thug_light_shared_direction_draft/);rejected.push({lane,mask});
}
writeFileSync(base+'skater-cleanup-checker-guard.json',JSON.stringify({result:'pass',baseline,rejected},null,2)+'\n');
console.log('Precise global quieting guard: pass; five changed results rejected');
