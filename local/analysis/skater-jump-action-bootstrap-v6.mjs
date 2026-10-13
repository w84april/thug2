// Private authored startup orchestration around original recovered routines.
// Inputs are raw QB/COL and executable tables; native outputs are never inputs.
import {createSkaterMotion} from './skater-browser-motion-v1.mjs';
import {mountWarehouseCollision} from './warehouse-shared-collision-v2.mjs';
const bytes=s=>Uint8Array.from(s.match(/../g)??[],n=>parseInt(n,16));
export async function createGroundedSkater(wasm,motionRuntime,collisionRuntime,runtime,load){
 const motion=await createSkaterMotion(wasm,motionRuntime,load),world=await mountWarehouseCollision(motion,collisionRuntime,load);
 const {exports:e,memory:m,view:v}=motion,set=(p,n)=>v.setUint32(p,n,true),word=p=>v.getUint32(p,true),adapter=motion.memoryAdapter,body=motion.base,physics=motion.physics;
 const table=e.__indirect_function_table;
 function slot(fn){for(let i=0;i<table.length;i++)if(table.get(i)===fn)return i;const i=table.grow(1);table.set(i,fn);return i;}
 // A diagnostic or unrecovered command fails visibly; it cannot silently pass.
 const missingSlot=slot(e.thug_script_native_missing_v1),printfSlot=slot(e.thug_script_printf_binding_v1),goalActiveSlot=slot(e.thug_script_goal_is_active_v1),gotParamSlot=slot(e.thug_script_got_parameter_draft);
 const nativeSlot=b=>b.address===0x5b9760?printfSlot:b.address===0x5594f0?goalActiveSlot:b.address===0x44bd30?gotParamSlot:missingSlot;
 m.set(bytes(motionRuntime.caller_hex),body);for(const [name,n] of motionRuntime.caller_globals)set(e[name].value,n);
 m.fill(0,e.thug_collision_cache_registry.value,e.thug_collision_cache_registry.value+36);
 m.fill(0,e.thug_component_type_heads.value,e.thug_component_type_heads.value+512);
 m.fill(0,runtime.registry,runtime.registry+0x1000);set(runtime.registry+0x44,runtime.factories.length);
 for(const [i,f] of runtime.factories.entries()){set(runtime.registry+0x48+8*i,f.type);set(runtime.registry+0x4c+8*i,f.native);}
 set(e.thug_component_type_registry.value,runtime.registry);
 m.set(await load(runtime.binding_raw),runtime.binding_data);
 for(const binding of runtime.natives)set(binding.slot,nativeSlot(binding));
 e.thug_script_register_natives_v1(runtime.native_table,runtime.natives.length,adapter);
 e.thug_script_register_members_v1(runtime.member_table,runtime.members.length,adapter);
 const registration=[];
 for(const b of [...runtime.natives.map(b=>({...b,kind:8})),...runtime.members.map(b=>({...b,kind:9}))]){
  const p=e.thug_script_symbol_find(b.checksum),kind=m[p+1],value=word(p+12);
  if(!p||kind!==b.kind||(kind===8&&value!==nativeSlot(b))||(kind===9&&value!==0))throw Error('Original binding registration mismatch '+b.name);
  registration.push({name:b.name,checksum:b.checksum,kind});
 }
 for(const file of runtime.raw_inputs){
  m.set(await load(file.raw),file.address);m.set(new TextEncoder().encode(file.path.replaceAll('/','\\')+'\0'),runtime.filename);
  e.thug_script_load_qb(runtime.filename,file.address,0,1,0,adapter);
 }
 // Authored sound-table startup around recovered primitives, following raw
 // terrain QB definitions and actual static constructors640950/640970.
 for(const name of ['thug_sound_materials','thug_sound_events'])e.thug_object_table_initialize(e[name].value,8,adapter);
 const allocate=(n)=>table.get(word(adapter+4))(word(adapter),n,1),key=runtime.diagnostics+0x200;
 const materials=e.thug_script_get_global_array(0x533ad720,1),events=e.thug_script_get_global_array(0x828087b8,1);
 if(!materials||!events)throw Error('Actual terrain sound definitions missing');
 for(let i=0;i<word(materials+4);i++){
  const p=allocate(8),s=e.thug_script_array_structure(materials,i);m[p]=i&255;
  e.thug_script_get_checksum(s,0x21902065,p+4,0);e.thug_object_table_insert(e.thug_sound_materials.value,p+4,p,adapter);
 }
 for(let i=0;i<word(events+4);i++){
  const p=allocate(12),s=e.thug_script_array_structure(events,i);m[p]=i&255;
  e.thug_script_get_checksum(s,0x7321a8d6,p+4,1);e.thug_script_get_checksum(s,0xb833736d,p+8,1);
  set(key,i);e.thug_object_table_insert(e.thug_sound_events.value,key,p,adapter);
 }
 const nodes=e.thug_script_get_global_array(runtime.node_array_key,1);if(!nodes||word(nodes+4)!==1917)throw Error('Actual TR_NodeArray missing');
 m.fill(0xad,runtime.node_table,runtime.node_table+0x100fc);e.thug_node_table_initialize_draft(runtime.node_table);
 set(runtime.node_table+0x10008,runtime.node_array_key);set(runtime.node_table+0x1000c,nodes);set(runtime.node_table+0x10010,0);set(runtime.node_table+0x10004,1);
 e.thug_node_links_resolve_draft(nodes);e.thug_node_table_index_array_draft(runtime.node_table,0);set(e.thug_node_table.value,runtime.node_table);set(e.thug_script_cache.value,runtime.cache);
 m.fill(0,runtime.event_manager,runtime.event_manager+0xb218);m.fill(0,runtime.primary,runtime.primary+0x200);
 for(const p of [runtime.primary,runtime.secondary,runtime.listeners])e.thug_object_table_initialize(p,8,adapter);
 set(runtime.event_manager+8,runtime.primary);set(runtime.event_manager+12,runtime.secondary);set(runtime.event_manager+16,runtime.listeners);set(e.thug_object_lookup_manager.value,runtime.event_manager);
 e.thug_object_manager_initialize(runtime.object_manager);e.thug_composite_initialize_draft(body);set(body+0x14,0x100);e.thug_object_manager_add(runtime.object_manager,body,adapter);
 for(let i=0;i<12;i++)v.setFloat32(body+0x290+4*i,-1,true);set(body+0x278,body+0x2000);set(body+0x2018,body+0x2040);
 const components=new Map(),methodRelocations=new Map([[0x647650,e.thug_composite_methods_draft.value],[0x6477e4,e.thug_ui_object_queue_methods.value],[0x6477e0,e.thug_ui_object_secondary_methods.value],[0x64ed24,e.thug_balance_record_methods_draft.value]]);
 let vtableCursor=runtime.vtable_data;
 for(const f of runtime.factories){
  let p;if(f.type===0x5bd63b29){m.fill(0,physics,physics+0x153c);p=e[f.export](physics);}else p=e[f.export](adapter);
  if(!p||word(p+4)!==f.type)throw Error('Actual component factory failed '+f.export);
  // Existing startup tables intentionally trap unavailable commands. The real
  // executable gives these exact tables the already recovered unhandled slot.
  // Derive a table only when that original slot is proven to be0051adc0.
  if(f.slots[12]===0x51adc0){
   const old=word(p);m.set(m.slice(old,old+52),vtableCursor);set(vtableCursor+48,word(e.thug_component_methods.value+48));set(p,vtableCursor);vtableCursor+=52;
  }
  // Native v10 and jump-action reference observed these EndGap/StartGap branches returning2 with all
  // receiver bytes unchanged. Every other command remains unavailable.
  if([0x518760,0x523560,0x517c80,0x4f9420].includes(f.slots[12])){
   const old=word(p);m.set(m.slice(old,old+52),vtableCursor);set(vtableCursor+48,slot(e.thug_component_endgap_unhandled_v1));set(p,vtableCursor);vtableCursor+=52;
  }
  methodRelocations.set(f.vtable,word(p));e.thug_composite_add_component_draft(body,p);components.set(f.type,p);
 }
 const state=components.get(0x43686585),input=components.get(0x27d7cd28),pad=input+0x20,packetPointer=body+0x1f00;
 e.thug_skater_initialize_physics(physics,body+0x3500);e.thug_skater_link_physics(physics);
 e.thug_trick_finalize_draft(components.get(0x270f56e1));e.thug_physics_control_finalize_draft(components.get(0xd9151d4d));e.thug_input_pad_reset_draft(pad);set(body+0x280,physics);
 e.thug_skater_state_initialize_draft(state,body+0x3500);
 m.fill(0,runtime.diagnostics,runtime.diagnostics+8);set(runtime.diagnostics+4,missingSlot);
 e.thug_score_component_initialize_draft(components.get(0xd262802f),body+0x3500,runtime.diagnostics,adapter);
 m.fill(0,runtime.diagnostics,runtime.diagnostics+8);set(runtime.diagnostics+4,missingSlot);
 e.thug_skater_change_state(physics,0,runtime.diagnostics,adapter);
 runtime.initial_position.forEach((n,i)=>v.setFloat32(body+0x4c+4*i,n,true));e.thug_vector_copy(body+0x5c,body+0x4c);e.thug_vector_copy(physics+0x3b0,body+0x4c);
 v.setFloat32(physics+0x8c,1/60,true);m[physics+0x311]=1;
 m.fill(0,runtime.orientation_context,runtime.orientation_context+0x44);set(runtime.orientation_context+0x40,runtime.orientation_context_identifier);set(e.thug_skater_orientation_context.value,runtime.orientation_context);
 m.fill(0,runtime.empty_objective_objects,runtime.empty_objective_objects+0x38);e.thug_object_table_initialize(runtime.empty_objective_objects+8,8,adapter);e.thug_object_table_initialize(runtime.empty_objective_objects+0x20,8,adapter);set(e.thug_objective_objects.value,runtime.empty_objective_objects);
 set(e.thug_frame_counter.value,0);v.setFloat32(e.thug_frame_rate.value,60,true);set(e.thug_timer_origin.value,0);set(e.thug_timer_offset.value,0);v.setFloat32(e.thug_time_scale.value,1,true);
 m[e.thug_collision_grid_stamp.value]=0;m[e.thug_collision_select_farthest.value]=0;m.fill(0,world.addresses.state,world.addresses.state+12);
 const initialPacket=new Uint8Array(32);initialPacket.fill(128,0,4);initialPacket.fill(128,0x12,0x16);initialPacket[6]=255;m.set(initialPacket,packetPointer);
 e.thug_input_pad_update_draft(pad,packetPointer);e.thug_physics_force_auto_kick_on_member(physics,0,0);
 function step(packet,frame){
  if(packet.length!==32||![0,1].includes(word(state+0x18)))throw Error('Grounded/air-only candidate frame contract');
  const jumpReleased=m[packetPointer+10]!==0&&packet[10]===0;
  m.set(packet,packetPointer);set(e.thug_frame_counter.value,frame);e.thug_vector_copy(body+0x5c,body+0x4c);e.thug_vector_copy(physics+0x3b0,body+0x4c);
  e.thug_input_pad_update_draft(pad,packetPointer);(packet[6]?e.thug_physics_force_auto_kick_on_member:e.thug_physics_force_auto_kick_off_member)(physics,0,0);
  // Explicit host ABI service scope for recovered original fixed-argument
  // virtual calls. This orchestration is not original510830 frame recovery.
  const services=runtime.diagnostics+0x100,previous=word(e.thug_component_services.value);
  set(services,world.addresses.state);set(services+4,runtime.diagnostics);set(services+8,adapter);set(e.thug_component_services.value,services);
  try{if(jumpReleased&&word(state+0x18)===0){
    if(!e.thug_skater_handle_input_release(physics,runtime.diagnostics,adapter))throw Error('Original charged-release contract missing');
    e.thug_skater_jump(physics,body+0x3500,world.addresses.state,runtime.diagnostics,adapter);
   }
   e.thug_skater_update_movement(physics,world.addresses.state,runtime.diagnostics,adapter);
  }finally{set(e.thug_component_services.value,previous);}

  return {position:[0,1,2,3].map(i=>v.getFloat32(body+0x4c+4*i,true)),velocity:[0,1,2,3].map(i=>v.getFloat32(body+0xac+4*i,true)),mode:word(state+0x18)};
 }
 return {motion,world,exports:e,memory:m,view:v,body,physics,state,pad,components,methodRelocations,registration,step,scope:runtime.scope,completion_credit:0,matching_credit:0,playable:false};
}
