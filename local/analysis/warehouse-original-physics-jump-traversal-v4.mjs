// Authored input/time/bootstrap adapter. Original routines own position/contact.
import {createGroundedSkater} from './skater-jump-action-bootstrap-v6.mjs';
export async function createOriginalPhaseTraversal(wasm,motion,collision,runtime,load){
 const engine=await createGroundedSkater(wasm,motion,collision,runtime,load),v=engine.view;
 const position=[0,1,2].map(i=>v.getFloat32(engine.body+0x4c+4*i,true));
 let frame=0,jumpActions=0,previousJumpHeld=false;
 function snapshot(){
  const mode=v.getUint32(engine.state+0x18,true),orientation=[...new Float32Array(engine.memory.buffer,engine.body+0x6c,16)],velocity=[0,1,2].map(i=>v.getFloat32(engine.body+0xac+4*i,true));
  position.splice(0,3,...[0,1,2].map(i=>v.getFloat32(engine.body+0x4c+4*i,true)));
  if([...position,...orientation,...velocity].some(n=>!Number.isFinite(n)))throw Error('Nonfinite original movement state');
  return {frame,position:position.slice(),velocity,orientation,mode,grounded:mode===0,original_physics_update_calls:frame,authored_jump_action_calls:jumpActions,
   original_contact_flag:v.getUint8(engine.state+0x80),original_transition_flag:v.getUint8(engine.state+0x30),original_bounded_ground_and_air_phases_verified:true,original_bounded_physics_update_entry_verified:true,authored_grounded_jump_mapping:true,original_jump_script_controller_verified:false,
   authored_position_floor_wall_updates:false,original_full_frame_dispatcher:false,original_live_input_paths_fully_verified:false,original_gameplay_frame_verified:false,completion_credit:0,playable:false};
 }
 function step(packet){
  const mode=v.getUint32(engine.state+0x18,true);
  const released=previousJumpHeld&&packet[10]===0;
  engine.step(packet,frame);frame++;if(released&&mode===0)jumpActions++;previousJumpHeld=packet[10]!==0;
  return snapshot();
 }
 return {engine,position,step,snapshot,scope:runtime.scope,completion_credit:0,playable:false};
}
