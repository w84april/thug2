import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {verifyJumpActionBootstrap} from './skater-jump-action-bootstrap-v6-checks.mjs';
const p='local/analysis/',target=p+'skater-level-trigger-air-release-v1-node.json';if(existsSync(target))throw Error('Preserve prior proof');
const load=n=>new Uint8Array(readFileSync(existsSync(p+n)?p+n:'local/validation/collision/'+n)),read=n=>JSON.parse(readFileSync(p+n)),hash=b=>createHash('sha256').update(b).digest('hex');
const runtime=read('skater-jump-action-bootstrap-v6-inputs.json'),motion=read('skater-browser-motion-v1-inputs.json'),collision=read('skater-shared-ground-v1-inputs.json'),original=read('skater-jump-action-live-v4-original.json');
for(const inputs of [runtime,motion,collision])for(const [name,wanted] of Object.entries(inputs.input_sha256))if(hash(load(name))!==wanted)throw Error('Changed private input '+name);
const result=await verifyJumpActionBootstrap(load(runtime.module),motion,collision,runtime,original,load,hash);
writeFileSync(target,JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({...result,frames:undefined}));
