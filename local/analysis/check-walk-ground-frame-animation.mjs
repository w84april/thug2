// Check the new partial export on the unchanged original animation-frame corpus.
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {verifyScriptState} from './walk-speed-checks.mjs';
const p='local/analysis/',fixture=JSON.parse(readFileSync(p+'walk-frame-speed-flow-fixtures.json'));
fixture.functions['0x52d4b0'].name='thug_walk_update_ground_prefix_draft';
const result=await verifyScriptState(readFileSync(p+'walk-ground-frame-draft.wasm'),fixture,n=>readFileSync(existsSync(p+n)?p+n:'local/validation/collision/'+n));
if(result.cases!==48||result.calls!==336||result.counts.thug_walk_update_ground_prefix_draft!==168)throw Error('Animation corpus changed');
writeFileSync(p+'walk-ground-frame-animation-parity.json',JSON.stringify(result,null,2)+'\n');console.log('PASS 168 animation frames through the new partial dispatcher');
