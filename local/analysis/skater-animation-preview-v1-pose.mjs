// Authored browser assembly of compared original parsers/sampler/matrix code.
// Inputs are raw assets. Original profile/controller startup is not claimed.
export async function createSkaterPose(hawk,metadata,load) {
 const e=hawk.exports,m=hawk.memory,v=hawk.view,u32=p=>v.getUint32(p,true),set=(p,n)=>v.setUint32(p,n,true);
 const raw={};for(const [name,spec] of Object.entries(metadata.inputs))raw[name]=new Uint8Array(await load(spec.file));
 const table=e.__indirect_function_table;let slot=-1;for(let i=0;i<table.length;i++)if(table.get(i)===e.thug_matrix_multiply_sse){slot=i;break;}
 if(slot<0){slot=table.grow(1);table.set(slot,e.thug_matrix_multiply_sse);}set(e.thug_matrix_multiply.value,slot);
 for(const name of ['rotation','translation'])m.set(raw[name],e['thug_animation_'+name+'_table'].value);
 const asset=0x4000000,skeletonFile=0x4001000,instance=0x4003000,pose=0x4004000,channel=0x4005000,animationBase=0x4006000,fileBase=0x4010000;
 if(m.length<fileBase+6*0x2000)throw Error('Insufficient explicit pose arena');
 m.fill(0,asset,fileBase+6*0x2000);m.set(raw.skeleton,skeletonFile);
 const memoryAdapter=hawk.memoryAdapter;
 e.thug_skeleton_initialize_draft(asset);
 if(!e.thug_skeleton_parse_draft(asset,skeletonFile,raw.skeleton.length,1,memoryAdapter))throw Error('Skeleton parse failed');
 e.thug_skeleton_instance_construct_v1(instance,asset,memoryAdapter);
 const bones=u32(instance+20),matrices=u32(instance+4),bind=u32(asset+0x590);
 if(bones!==50)throw Error('Expected original50-bone player skeleton');
 const bindTranslations=m.slice(bind,bind+bones*16),clips=new Map();
 for(const [i,name] of ['Idle','AirIdle','AirTurnLeft','AirTurnRight','Ollie','Land'].entries()){
  const animation=animationBase+i*64,file=fileBase+i*0x2000,bytes=raw[name];if(bytes.length>0x2000)throw Error('Clip exceeds fixed assembly arena');
  m.set(bytes,file);e.thug_keyframe_animation_initialize(animation);
  if(!e.thug_keyframe_animation_load_buffer(animation,file,bytes.length,0,memoryAdapter))throw Error('Clip parse failed '+name);
  if(u32(animation+8)!==bones||u32(animation+0x24))throw Error('Unsupported clip bone/cache configuration');
  clips.set(name,{animation,duration:v.getFloat32(animation,true)});
 }
 e.thug_animation_timeline_initialize(channel);
 let clipName='Idle';
 const select=name=>{const clip=clips.get(name);if(!clip)throw Error('Unknown original clip');clipName=name;e.thug_animation_set_timeline(channel,0,0,clip.duration,1,0,1);};
 select(clipName);
 function sample(){
  m.fill(0,pose,pose+0x840);m.set(bindTranslations,pose+0x400);
  const clip=clips.get(clipName),seconds=v.getFloat32(channel+0x18,true);
  if(e.thug_keyframe_sample_uncached_partial_v1(clip.animation,pose,pose+0x400,pose+0x800,seconds,-1,0)!==1)throw Error('Pose sampling failed');
  e.thug_skeleton_evaluate_pose_block_partial_v1(instance,pose);
  const matrixData=new Float32Array(e.memory.buffer,matrices,bones*16);
  if(!matrixData.every(Number.isFinite))throw Error('Nonfinite original pose matrix');
  return {matrixData,matrixBytes:m.slice(matrices,matrices+bones*64),poseBytes:new Uint8Array([...m.slice(pose,pose+bones*16),...m.slice(pose+0x400,pose+0x400+bones*16),...m.slice(pose+0x800,pose+0x800+bones)]),seconds,clip:clipName,duration:clip.duration};
 }
 function seek(seconds){const current=v.getFloat32(channel+0x18,true);e.thug_animation_offset_time(channel,seconds-current);return sample();}
 function advance(seconds){v.setFloat32(e.thug_frame_length_scale.value,Math.min(seconds,.1)*60,true);e.thug_animation_update_time(channel);return sample();}
 return {sample,seek,advance,select,clips,bones,rawDecodedOutputInputs:0};
}
// Explicit WebGL adapter: three original packed weights and bone indices.
// Original CPU/GPU skinning and D3D shader equivalence remain unverified.
export function skinVertices(mesh,matrices,bones,target) {
 const input=new DataView(mesh.vertexData.buffer,mesh.vertexData.byteOffset,mesh.vertexData.byteLength),out=new DataView(target.buffer,target.byteOffset,target.byteLength);
 for(let i=0;i<mesh.vertices;i++){
  const at=i*76,p=[input.getFloat32(at,true),input.getFloat32(at+4,true),input.getFloat32(at+8,true)],xyz=[0,0,0];
  for(let j=0;j<3;j++){
   const weight=input.getFloat32(at+64+j*4,true);if(!weight)continue;
   const bone=input.getUint8(at+60+j);if(bone>=bones||!Number.isFinite(weight))throw Error('Invalid packed skin binding');
   const k=bone*16;for(let axis=0;axis<3;axis++)xyz[axis]+=weight*(p[0]*matrices[k+axis]+p[1]*matrices[k+4+axis]+p[2]*matrices[k+8+axis]+matrices[k+12+axis]);
  }
  for(let axis=0;axis<3;axis++){if(!Number.isFinite(xyz[axis]))throw Error('Nonfinite adapted skin vertex');out.setFloat32(at+axis*4,xyz[axis],true);}
 }
 return target;
}
