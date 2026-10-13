import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {verifyGoalActive} from './skater-goal-active-v1-checks.mjs';
const out='local/analysis/skater-goal-active-v1-node.json';if(existsSync(out))throw Error('Preserve original output');
const wasm=readFileSync('local/analysis/skater-grounded-bootstrap-v6.wasm'),reference=JSON.parse(readFileSync('local/analysis/skater-goal-active-v1-original.json'));
const report={...await verifyGoalActive(wasm,reference),wasm_sha256:createHash('sha256').update(wasm).digest('hex')};
writeFileSync(out,JSON.stringify(report,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({...report,results:undefined}));
