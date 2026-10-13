// Authored caller/input/frame adapter; the existing recovered engine callees run unchanged.
export async function createSkaterMotion(wasm,runtime,load) {
 const {instance:{exports:e}}=await WebAssembly.instantiate(wasm);
 const memory=new Uint8Array(e.memory.buffer),view=new DataView(e.memory.buffer),set=(p,n)=>view.setUint32(p,n,true);
 const pointers=new Map(runtime.pointer_symbols.map(([old,name])=>[old,e[name].value]));
 for(const [old,name,offset=0] of runtime.pointer_exports)pointers.set(old,e[name].value+offset);
 memory.set(await load(runtime.memory),runtime.base);
 const {instance:{exports:allocator}}=await WebAssembly.instantiate(await load(runtime.memory_fixture),{env:{memory:e.memory}});
 for(const [i,name] of runtime.memory_exports.entries()){
  const slot=e.__indirect_function_table.grow(1);e.__indirect_function_table.set(slot,allocator[name]);set(runtime.memory_adapter+4*(i+1),slot);
 }
 set(runtime.context_loading_file_slot,e.thug_script_loading_file.value);
 const table=e.__indirect_function_table;let mathSlot=-1;for(let i=0;i<table.length;i++)if(table.get(i)===e.thug_matrix_multiply_sse){mathSlot=i;break;}
 if(mathSlot<0){mathSlot=table.grow(1);table.set(mathSlot,e.thug_matrix_multiply_sse);}set(e.thug_matrix_multiply.value,mathSlot);
 runtime.globals.forEach(([name,width,offset,value],i)=>{
  const n=runtime.pointer_globals.includes(i)?(pointers.get(value)??value):value;
  view[width===1?'setUint8':'setUint32'](e[name].value+offset,n,true);
 });
 // Execute the two-pass original QB loader directly on the raw private file.
 memory.set(await load(runtime.raw_physics),runtime.data);
 e.thug_script_load_qb(runtime.filename,runtime.data,0,1,0,runtime.memory_adapter);
 const base=runtime.caller_base,physics=base+0x400,input=base+0x1c00,pad=input+0x20,packetPointer=base+0x1f00;
 const caller=Uint8Array.from(runtime.caller_hex.match(/../g).map(n=>parseInt(n,16)));
 memory.set(caller,base);for(const [name,n] of runtime.caller_globals)set(e[name].value,n);
 e.thug_input_pad_construct_draft(pad);e.thug_input_pad_reset_draft(pad);
 function step(packet,seconds,frame,hz){
  if(packet.length!==32||!(seconds>0)||!Number.isFinite(seconds))throw Error('Invalid caller frame input');
  memory.set(packet,packetPointer);set(e.thug_frame_counter.value,frame);view.setFloat32(e.thug_frame_rate.value,hz,true);
  set(e.thug_timer_origin.value,0);set(e.thug_timer_offset.value,0);view.setFloat32(e.thug_time_scale.value,1,true);view.setFloat32(physics+0x8c,seconds,true);
  e.thug_input_pad_update_draft(pad,packetPointer);
  // This Up-to-auto-kick binding is an explicit browser adapter.
  (packet[6]?e.thug_physics_force_auto_kick_on_member:e.thug_physics_force_auto_kick_off_member)(physics,0,0);
  e.thug_skater_steer(physics);
  const shouldBrake=e.thug_skater_should_brake(physics);let canAccelerate=0;
  if(shouldBrake)e.thug_skater_brake(physics);
  else {canAccelerate=e.thug_skater_can_accelerate(physics);if(canAccelerate)e.thug_skater_accelerate(physics);}
  return {should_brake:shouldBrake,can_accelerate:canAccelerate,caller_bytes:memory.slice(base,base+caller.length),velocity_bytes:memory.slice(base+0xac,base+0xbc),orientation_bytes:memory.slice(base+0x6c,base+0xac),cached_orientation_bytes:memory.slice(physics+0x18,physics+0x58),gameplay_flag:view.getUint8(e.thug_last_gameplay_flag.value)};
 }
 return {exports:e,memory,view,base,physics,input,pad,packetPointer,memoryAdapter:runtime.memory_adapter,step,scope:runtime.scope,completion_credit:0,playable:false};
}
