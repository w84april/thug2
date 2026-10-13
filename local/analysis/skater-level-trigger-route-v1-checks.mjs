import {createGroundedSkater} from './skater-jump-action-bootstrap-v6.mjs';
const hex=b=>Array.from(b,n=>n.toString(16).padStart(2,'0')).join(''),bytes=s=>Uint8Array.from(s.match(/../g)??[],n=>parseInt(n,16));
export async function verifyJumpActionBootstrap(wasm,motion,collision,runtime,original,load,hash){
 if(original.error||original.windows_debug_output_port.diagnostics.length||original.frames.length!==1200||original.active_commands_on_stop.length)throw Error('Invalid native integration reference');
 if(original.command_observations.length!==95||original.command_observations.some(c=>!['0xe5399fb2','0x65b9ec39'].includes(c.name)||c.result!==2||c.before!==c.after||c.return_stack!==c.stack+16))throw Error('Unverified partial StartGap/EndGap path');
if(!original.authored_orientation_context||original.authored_orientation_context.identifier!==0||original.low_memory_abi_read_audit.some(r=>!r.instruction.includes('fs:')))throw Error('Unverified native caller/low-memory contract');
 const engine=await createGroundedSkater(wasm,motion,collision,runtime,load),{memory:m,view:v}=engine;
async function equal(wanted,pointer,label,offsets=[0]){
 const expected=bytes(wanted),observed=m.slice(pointer,pointer+expected.length),ev=new DataView(expected.buffer),ov=new DataView(observed.buffer);
 // Only declared immutable method-table identities relocate; every other byte
 // including numeric results, live heap links, event logs and timers is exact.
 for(const i of offsets){const old=ev.getUint32(i,true);if(engine.methodRelocations.has(old))ev.setUint32(i,engine.methodRelocations.get(old),true);}
 for(let i=0;i<expected.length;i++)if(expected[i]!==observed[i])throw Error(label+' mismatch offset0x'+i.toString(16)+' expected '+hex(expected.slice(Math.max(0,i-4),i+12))+' observed '+hex(observed.slice(Math.max(0,i-4),i+12)));
 return hash(observed);
}
await equal(original.initial_native.body_bits,engine.body,'initial body',[0,0x28,0x40]);await equal(original.initial_native.physics_bits,engine.physics,'initial physics');
for(const [key,wanted] of Object.entries(original.initial_native.components)){
 if(engine.components.get(Number(key))!==original.components[key])throw Error('Original factory allocation differs '+key);
 await equal(wanted,engine.components.get(Number(key)),'initial component '+key,Number(key)===0x589e5fb3?[0,0x24,0x7c,0xd4,0x12c]:[0]);
}
await equal(original.initial_native.manager_bits,runtime.event_manager,'initial event manager',[]);
async function equalScore(wanted,label){
 const pointer=v.getUint32(engine.components.get(0xd262802f)+0x18,true);if(pointer!==wanted.pointer)throw Error('Actual Score allocation mismatch');
 const array=v.getUint32(pointer+0x4c,true),capacity=v.getUint32(pointer+0x50,true);
 if(array!==wanted.array_pointer||capacity!==wanted.array_capacity)throw Error('Actual Score array allocation mismatch');
 return {score_sha256:await equal(wanted.bits,pointer,label+' score',[]),score_array_sha256:await equal(wanted.array_bits,array,label+' score array',[])};
}
async function equalSound(wanted,label){
 const result={};
 for(const [name,data] of Object.entries(wanted)){
  const table=engine.exports[name==='materials'?'thug_sound_materials':'thug_sound_events'].value;
  if(v.getUint32(table+4,true)!==data.buckets)throw Error('Sound bucket allocation mismatch');
  result[name]={table_sha256:await equal(data.table_bits,table,label+' sound table '+name,[]),buckets_sha256:await equal(data.buckets_bits,data.buckets,label+' sound buckets '+name,[]),records:[]};
  for(const record of data.records){if(v.getUint32(record.node+4,true)!==record.pointer)throw Error('Sound record link mismatch');result[name].records.push(await equal(record.bits,record.pointer,label+' sound record '+name,[]));}
 }
 return result;
}
await equalScore(original.initial_native.score,'initial');await equalSound(original.initial_native.sound,'initial');
const frames=[];
for(const wanted of original.frames){
 const state=engine.step(bytes(wanted.packet),wanted.frame);
 const observed={frame:wanted.frame,...await equalScore(wanted.score,'frame'+wanted.frame),sound:await equalSound(wanted.sound,'frame'+wanted.frame),body_sha256:await equal(wanted.body_bits,engine.body,'frame'+wanted.frame+' body',[0,0x28,0x40]),physics_sha256:await equal(wanted.physics_bits,engine.physics,'frame'+wanted.frame+' physics'),components:{},manager_sha256:await equal(wanted.manager_bits,runtime.event_manager,'frame'+wanted.frame+' manager',[]),query_state_bits:hex(m.slice(engine.world.addresses.state,engine.world.addresses.state+12)),instance_stamps_bits:hex(Uint8Array.from({length:engine.world.count},(_,i)=>m[engine.world.instances+i*24+10])),final_stamp:m[engine.exports.thug_collision_grid_stamp.value],...state};
 for(const [key,data] of Object.entries(wanted.component_bits))observed.components[key]=await equal(data,engine.components.get(Number(key)),'frame'+wanted.frame+' component '+key,Number(key)===0x589e5fb3?[0,0x24,0x7c,0xd4,0x12c]:[0]);
 for(const key of ['query_state_bits','instance_stamps_bits','final_stamp','position','velocity','mode'])if(JSON.stringify(observed[key])!==JSON.stringify(wanted[key]))throw Error('Original grounded frame mismatch '+wanted.frame+' '+key);
 frames.push(observed);
}
const result={result:'pass',original_frames:frames.length,ground_frames:frames.filter(f=>f.mode===0).length,air_frames:frames.filter(f=>f.mode===1).length,native_low_memory_audit_passed:true,actual_score_storage_and_array_bytes_equal:true,actual_sound_table_bucket_record_bytes_equal:true,original_bounded_ground_and_air_phases_verified:true,original_bounded_movement_dispatcher_verified:true,authored_jump_action_mapping_verified:true,original_jump_script_controller_verified:false,original_gameplay_frame_verified:false,decoded_output_inputs:0,registration_entries:engine.registration.length,whole_component_body_physics_event_query_bytes_equal:true,frame_results_sha256:await hash(new TextEncoder().encode(JSON.stringify(frames))),frames,completion_credit:0,matching_credit:0,playable:false,original_whole_profile_startup:false,original_full_frame_dispatcher:false,scope:runtime.scope};
return result;
}
