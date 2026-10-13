import {verifyGoalActive} from './skater-goal-active-v1-checks.mjs';
import {verifyJumpActionBootstrap} from './skater-jump-action-bootstrap-v6-checks.mjs';
import {verifyJumpActionBootstrap as verifyRoute} from './skater-level-trigger-route-v1-checks.mjs';
const load=async n=>{const r=await fetch('/'+n);if(!r.ok)throw Error('Missing input '+n);return new Uint8Array(await r.arrayBuffer());};
const read=async n=>JSON.parse(new TextDecoder().decode(await load(n)));
const hash=async b=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',b)),n=>n.toString(16).padStart(2,'0')).join('');
try{
 const runtime=await read('skater-jump-action-bootstrap-v6-inputs.json'),motion=await read('skater-browser-motion-v1-inputs.json'),collision=await read('skater-shared-ground-v1-inputs.json'),wasm=await load(runtime.module);
 for(const inputs of [runtime,motion,collision])for(const [name,wanted] of Object.entries(inputs.input_sha256))if(await hash(await load(name))!==wanted)throw Error('Changed preserved input '+name);
 const goal=await verifyGoalActive(wasm,await read('skater-goal-active-v1-original.json'));
 const jump=await verifyJumpActionBootstrap(wasm,motion,collision,runtime,await read('skater-jump-action-live-v3-original.json'),load,hash);
 const air_release=await verifyJumpActionBootstrap(wasm,motion,collision,runtime,await read('skater-jump-action-live-v4-original.json'),load,hash);
 const route=await verifyRoute(wasm,motion,collision,runtime,await read('skater-level-trigger-route-v1-original.json'),load,hash);
 postMessage({result:'pass',wasm_sha256:await hash(wasm),goal,jump,air_release,route,completion_credit:0,matching_credit:0,playable:false});
}catch(error){postMessage({result:'fail',error:String(error.stack??error)});}
