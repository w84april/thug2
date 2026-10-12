import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {loadTraining} from './training-webgl-v1-load.mjs';
const load=async n=>new Uint8Array(await readFile(new URL(n,import.meta.url)));
const runtime=JSON.parse(await readFile(new URL('training-webgl-v1-runtime.json',import.meta.url)));
const reference=JSON.parse(await readFile(new URL('training-webgl-v1-original-reference.json',import.meta.url)));
const hash=data=>createHash('sha256').update(data).digest('hex');
for(const [n,wanted] of Object.entries(runtime.input_sha256))if(hash(await load(n))!==wanted)throw Error('Changed runtime input '+n);
const start=performance.now(),world=await loadTraining(await load(runtime.wasm),runtime,load);
for(const [i,m] of world.meshes.entries()) {
 const wanted=reference.meshes[i];
 for(const k of ['at','stride','vertices','fvf','materialKey','texture','passes'])if(m[k]!==wanted[k])throw Error('Original mesh field '+i+' '+k);
 if(hash(m.vertexData)!==wanted.vertex_sha256)throw Error('Original vertices '+i);
 if(m.strips.length!==wanted.strips.length)throw Error('Original strip count');
 for(const [j,s] of m.strips.entries())if(s.slot!==wanted.strips[j].slot||s.count!==wanted.strips[j].count||hash(s.data)!==wanted.strips[j].sha256)throw Error('Original indices '+i+':'+j);
}
const boundTextures=new Set(world.meshes.map(m=>m.textureHandle).filter(Boolean));
const missing=[...boundTextures].filter(p=>!world.textures.has(p));
if(missing.length)throw Error('Unresolved GPU texture handle');
const report={result:'pass',...world.summary,original_gpu_storage_hashes_equal:true,elapsed_ms:Math.round(performance.now()-start),bound_texture_references:boundTextures.size,missing_texture_references:missing.map(p=>p.toString(16)),completion_credit:0,frame_equivalence_verified:false};
console.log(JSON.stringify(report));
await writeFile(new URL('training-webgl-v1-node-v2.json',import.meta.url),JSON.stringify(report,null,2)+'\n');
