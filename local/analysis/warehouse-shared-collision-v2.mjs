// Explicit static scene bootstrap in the motion engine's existing memory.
// Real raw collision loading, grid building and queries run unchanged.
export async function mountWarehouseCollision(motion,runtime,load){
 const {exports:e,memory,view}=motion,a=runtime.addresses;
 const set=(p,n)=>view.setUint32(p,n,true),flt=(p,n)=>view.setFloat32(p,n,true),context=view.getUint32(motion.memoryAdapter,true);
 if(a.data<0x4000000||a.state+12>memory.length)throw Error('Collision arena overlaps the preserved motion inputs');
 const heapBegin=view.getUint32(context,true),raw=await load(runtime.raw);memory.set(raw,a.data);
 memory.fill(0xad,a.output,a.output+32);[1e7,1e7,1e7,1,-1e7,-1e7,-1e7,1].forEach((n,i)=>flt(a.bounds+4*i,n));
 memory.fill(0,e.thug_collision_fallback_indices.value,e.thug_collision_fallback_indices.value+4096);view.setUint16(e.thug_collision_fallback_indices.value,65535,true);
 if(e.thug_collision_load(0xcafebabe,a.data,a.output,a.output+4,a.output+8,a.bounds,0x1234,motion.memoryAdapter)!==1)throw Error('Shared raw collision load failed');
 const count=view.getUint32(a.output,true),instances=view.getUint32(a.output+4,true),objects=view.getUint32(a.output+8,true);
 memory.fill(0xad,a.grid,a.grid+0x4b30+32);for(let i=0;i<400;i++)e.thug_collision_cell_initialize(a.grid+48+i*48);
 e.thug_collision_grid_initialize(a.grid,a.bounds);e.thug_collision_grid_populate(a.grid,instances,count,motion.memoryAdapter);
 memory.fill(0,a.scene,a.scene+0xd4);set(a.scene+0xd4,a.grid);
 [0,a.scene,0,a.nodes+16,0,0xffffffff,0,a.nodes+16].forEach((n,i)=>set(a.nodes+4*i,n));
 [0,0xffffffff,0,a.moving].forEach((n,i)=>set(a.moving+4*i,n));
 set(e.thug_collision_scene_list.value,a.nodes);set(e.thug_moving_collision_list.value,a.moving);set(e.thug_collision_default_cache.value,0);
 const heapEnd=view.getUint32(context,true);set(motion.physics+0x152c,runtime.gate);
 memory[e.thug_collision_grid_stamp.value]=0;
 function query(start,end,excluded=0x10,required=0){
  [...start,1,...end,1].forEach((n,i)=>flt(a.segment+4*i,n));memory.fill(0xad,a.result,a.result+80);
  view.setUint16(a.result+0x28,excluded,true);view.setUint16(a.result+0x2a,required,true);set(a.result+0x2c,0);set(a.result+0x3c,0);
  memory[e.thug_collision_select_farthest.value]=0;
  const hit=e.thug_collision_scene_segment(a.segment,a.result,0,0,a.state);
  return {hit,resultBytes:memory.slice(a.result,a.result+80),point:hit?[0,1,2].map(i=>view.getFloat32(a.result+16+4*i,true)):null,normal:hit?[0,1,2].map(i=>view.getFloat32(a.result+4*i,true)):null,fraction:view.getFloat32(a.result+0x24,true),flags:view.getUint16(a.result+0x2c,true),checksum:view.getUint32(a.result+0x34,true),finalStamp:memory[e.thug_collision_grid_stamp.value]};
 }
 function updateGround(){e.thug_skater_ground_update(motion.physics,a.state);}
 return {exports:e,memory,view,addresses:a,count,instances,objects,rawBytes:raw.length,context,heapBegin,heapEnd,query,updateGround,scope:'Shared original ground helper plus raw static geometry; caller/bootstrap and position integration remain authored; moving-object list explicitly empty',completion_credit:0,playable:false};
}
