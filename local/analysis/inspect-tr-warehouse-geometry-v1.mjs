import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {loadTraining} from './training-webgl-v1-load.mjs';
const load=async n=>new Uint8Array(await readFile(new URL(n,import.meta.url)));
const runtime=JSON.parse(await readFile(new URL('training-webgl-v1-runtime.json',import.meta.url)));
const identity=JSON.parse(await readFile(new URL('tr-scene-identity-v2-original.json',import.meta.url)));
const proof=JSON.parse(await readFile(new URL('training-webgl-v1-storage-proof-v2.json',import.meta.url)));
const hash=data=>createHash('sha256').update(data).digest('hex');
for(const [n,wanted] of Object.entries(runtime.input_sha256))if(hash(await load(n))!==wanted)throw Error('Changed raw runtime input '+n);
const world=await loadTraining(await load(runtime.wasm),runtime,load);
const buffers=[];for(const m of world.meshes){buffers.push(m.vertexData);for(const s of m.strips)buffers.push(s.data);}for(const t of world.textures.values())buffers.push(...t.mips);
if(buffers.length!==proof.ordered_storage_buffers||hash(buffers.map(hash).join('\n'))!==proof.ordered_storage_sha256)throw Error('Changed original storage');
const sectorBounds=identity.sectors.map(s=>{
  const low=[Infinity,Infinity,Infinity],high=[-Infinity,-Infinity,-Infinity];
  for(const i of s.mesh_indices){const m=world.meshes[i],v=new DataView(m.vertexData.buffer,m.vertexData.byteOffset,m.vertexData.byteLength);for(let j=0;j<m.vertices;j++)for(let k=0;k<3;k++){const x=v.getFloat32(j*m.stride+4*k,true);if(!Number.isFinite(x))throw Error('Nonfinite vertex');low[k]=Math.min(low[k],x);high[k]=Math.max(high[k],x);}}
  const same=s.serialized_bounds,flipped=[same[0],same[1],-same[5],same[3],same[4],-same[2]],actual=[...low,...high];
  return {...s,loaded_bounds:actual,same_axis_max_error:Math.max(...same.map((x,i)=>Math.abs(x-actual[i]))),flipped_z_max_error:Math.max(...flipped.map((x,i)=>Math.abs(x-actual[i])))};
});
const restart=identity.nodes_registered.find(n=>n.text==='TRG_Ware_Restart01');
const result={result:'original storage verified; sector/coordinate identity discovery',original_storage_sha256:proof.ordered_storage_sha256,sectors:sectorBounds,restart,completion_credit:0,matching_credit:0,playable:false};
await writeFile(new URL('tr-warehouse-geometry-v1-discovery.json',import.meta.url),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({sameWithinPointOne:sectorBounds.filter(s=>s.same_axis_max_error<.1).length,flippedWithinPointOne:sectorBounds.filter(s=>s.flipped_z_max_error<.1).length,total:sectorBounds.length,restart}));
for(const name of ['SkWare_Dark_Floor06','SkWare_Main_9','SkWare_Roof03','g_warehouseNew_qp']){const s=sectorBounds.find(s=>s.text===name);console.log(name,s?.loaded_bounds,s?.same_axis_max_error,s?.flipped_z_max_error);}
