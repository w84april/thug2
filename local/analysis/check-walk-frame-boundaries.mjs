// Reuse unchanged original dispatcher-prefix evidence for unfinished states.
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {verifyScriptState} from './skater-walk-checks.mjs';
const p='local/analysis/',fixture=JSON.parse(readFileSync(p+'skater-walk-fixtures.json'));
fixture.cases=fixture.cases.filter(c=>c.steps.length===1&&c.steps[0].fn==='0x52d4b0'&&c.steps[0].boundary_factory!==0x52ad10);
if(fixture.cases.length!==96)throw Error('Original unsupported-state corpus changed: '+fixture.cases.length);
fixture.functions['0x52d4b0'].name='thug_walk_update_animation_prefix_draft';
const result=await verifyScriptState(readFileSync(p+'walk-frame-speed-draft.wasm'),fixture,n=>readFileSync(existsSync(p+n)?p+n:'local/validation/collision/'+n));
writeFileSync(p+'walk-frame-speed-boundaries.json',JSON.stringify(result,null,2)+'\n');console.log('PASS',result.cases,'original dispatcher boundaries');
