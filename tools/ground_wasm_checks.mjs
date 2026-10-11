export async function verifyGround(wasm,fixture,loadBinary){
  const {instance:{exports:e}}=await WebAssembly.instantiate(wasm);
  const memory=new Uint8Array(e.memory.buffer),v=new DataView(e.memory.buffer),a=fixture.addresses,base=fixture.loader;
  const unhex=text=>Uint8Array.from(text.match(/../g)??[],b=>parseInt(b,16)),guard=new Uint8Array(16).fill(0xad);
  let nanFields=0;const counts={};
  function equal(actual,expected,label){if(actual!==expected)throw new Error(`${label}: ${actual} != ${expected}`);}
  function bytes(at,expected,label){for(let i=0;i<expected.length;i++)if(memory[at+i]!==expected[i])throw new Error(`${label} byte ${i}: ${memory[at+i]} != ${expected[i]}`);}
  function floats(at,expected,label){const dv=new DataView(expected.buffer,expected.byteOffset,expected.byteLength);
    for(let i=0;i<expected.length;i+=4){
      if(Number.isNaN(v.getFloat32(at+i,true))&&Number.isNaN(dv.getFloat32(i,true))){nanFields++;continue;}
      equal(v.getUint32(at+i,true),dv.getUint32(i,true),label+' float '+i);
    }
  }
  function f32(word){const buffer=new ArrayBuffer(4),dv=new DataView(buffer);dv.setUint32(0,word,true);return dv.getFloat32(0,true);}
  for(const [i,t] of fixture.helpers.entries()){
    const label=t.kind+' '+i;counts[t.kind]=(counts[t.kind]??0)+1;
    if(t.kind==='copy'){
      memory.set(unhex(t.input),a.matrix);
      equal(e.thug_matrix_copy(a.matrix+64+t.offset,a.matrix+64),a.matrix+64+t.offset,label+' return');
      bytes(a.matrix,unhex(t.output),label);
    }else if(t.kind==='multiply'){
      memory.set(unhex(t.left),a.left);memory.fill(0xad,a.left+64,a.left+96);
      memory.set(unhex(t.right),a.right);memory.fill(0xad,a.right+64,a.right+96);memory.fill(0xad,a.matrix,a.matrix+80);
      const target=[a.matrix,a.left,a.right,a.left+4][t.alias];
      equal(e.thug_matrix_multiply_sse(target,a.left,a.right),target,label+' return');
      floats(a.matrix,unhex(t.out),label+' output');floats(a.left,unhex(t.left_after),label+' left');floats(a.right,unhex(t.right_after),label+' right');
    }else{
      const axis=unhex(t.axis);memory.set(axis,a.axis);memory.fill(0xad,a.matrix,a.matrix+80);
      if(t.kind==='rotate')memory.set(unhex(t.input),a.matrix);
      const returned=t.kind==='axis'?e.thug_matrix_axis_angle(a.matrix,a.axis,f32(t.angle)):e.thug_matrix_rotate_axis(a.matrix,a.axis,f32(t.angle));
      equal(returned,a.matrix,label+' return');floats(a.matrix,unhex(t.output),label);bytes(a.matrix+64,guard,label+' guard');bytes(a.axis,axis,label+' axis');
    }
  }
  function timer(config){['thug_frame_counter','thug_frame_rate','thug_timer_origin','thug_time_scale','thug_timer_offset'].forEach((name,i)=>v.setUint32(e[name].value,config[i],true));}
  for(const [i,t] of fixture.timers.entries()){
    timer(t.config);equal(e.thug_frame_time()>>>0,t.frame,'frame timer '+i);equal(e.thug_elapsed_time()>>>0,t.elapsed,'elapsed timer '+i);
  }
  for(const [i,t] of fixture.release.entries()){
    memory.set(unhex(t.probe),a.probe);memory.set(unhex(t.owners),a.owners);memory.set(unhex(t.refs),a.refs);
    for(let repeat=0;repeat<2;repeat++){
      e.thug_collision_probe_release(a.probe);bytes(a.probe,unhex(t.probe_after),'release probe '+i);bytes(a.owners,unhex(t.owners_after),'release owner '+i);bytes(a.refs,unhex(t.refs_after),'release refs '+i);
    }
  }
  const statMemory=await loadBinary('ground-stats.bin');memory.set(statMemory,fixture.stat_base);
  for(const [name,,value] of fixture.stat_globals)v.setUint32(e[name].value,value,true);
  const data=await loadBinary(base.loaded),grid=await loadBinary(base.grid),heap=Uint8Array.from(await loadBinary(base.heap));
  const hv=new DataView(heap.buffer);
  for(let i=0;i<base.count;i++)hv.setUint32(base.instances-a.heap+i*24,e.thug_static_collision_methods.value,true);
  memory.set(data,a.data);memory.set(grid,a.grid);memory.fill(0,a.scene,a.scene+0xd4);v.setUint32(a.scene+0xd4,a.grid,true);
  [0,a.scene,0,a.scenes+16,0,0xffffffff,0,a.scenes+16].forEach((n,i)=>v.setUint32(a.scenes+i*4,n,true));
  v.setUint32(e.thug_collision_scene_list.value,a.scenes,true);v.setUint32(e.thug_moving_collision_list.value,a.nodes,true);v.setUint32(e.thug_collision_default_cache.value,0,true);
  for(let j=0;j<3;j++)[0,a.runtime+j*0x100,0,a.nodes+(j+1)*16].forEach((n,i)=>v.setUint32(a.nodes+j*16+i*4,n,true));
  [0,0xffffffff,0,a.nodes+48].forEach((n,i)=>v.setUint32(a.nodes+48+i*4,n,true));
  for(let i=0;i<base.count;i++)e.thug_collision_has_tree(a.data+32+i*64);
  function actors(text){const b=unhex(text),dv=new DataView(b.buffer);for(let i=0;i<3;i++)dv.setUint32(i*0x100,e.thug_moving_collision_methods.value,true);return b;}
  const worldCounts={updates:0};
  for(const [i,t] of fixture.world.entries()){
    const label='ground update '+i;
    memory.set(heap,a.heap);memory.set(unhex(fixture.owners),a.owners);memory.set(unhex(fixture.references),a.refs);
    memory.set(actors(t.actors),a.runtime);memory.set(unhex(t.body),a.body);memory.set(unhex(t.physics),a.physics);
    memory.set(unhex(t.skater_state),a.skater_state);memory.set(unhex(t.gate),a.gate);memory.set(unhex(t.initial_state),a.state);timer(t.timer);
    memory[e.thug_collision_grid_stamp.value]=t.stamp;memory[e.thug_collision_select_farthest.value]=0;memory[e.thug_last_gameplay_flag.value]=0xad;
    e.thug_skater_ground_update(a.physics,a.state);
    const body=unhex(t.body_after),physics=unhex(t.physics_after);
    bytes(a.body,body.slice(0,0x6c),label+' body prefix');floats(a.body+0x6c,body.slice(0x6c,0xac),label+' orientation');bytes(a.body+0xac,body.slice(0xac),label+' body suffix');
    bytes(a.physics,physics.slice(0,0x18),label+' physics prefix');floats(a.physics+0x18,physics.slice(0x18,0x58),label+' cached orientation');bytes(a.physics+0x58,physics.slice(0x58),label+' physics suffix');
    bytes(a.skater_state,unhex(t.skater_state_after),label+' state flags/timestamps');bytes(a.gate,unhex(t.gate),label+' gate');
    bytes(a.runtime,actors(t.actors_after),label+' actors');bytes(a.owners,unhex(fixture.owners),label+' owners');bytes(a.refs,unhex(fixture.references),label+' refs');
    bytes(a.state,unhex(t.state),label+' collision state');equal(memory[e.thug_collision_grid_stamp.value],t.final_stamp,label+' stamp');
    equal(memory[e.thug_last_gameplay_flag.value],t.gameplay_flag,label+' stat flag');
    const expectedHeap=heap.slice(),stamps=unhex(t.stamps);for(let j=0;j<base.count;j++)expectedHeap[base.instances-a.heap+j*24+10]=stamps[j];bytes(a.heap,expectedHeap,label+' collision heap');
    worldCounts.updates++;for(const [name,count] of Object.entries(t.events))worldCounts[name]=(worldCounts[name]??0)+count;
  }
  bytes(a.data,data,'preserved geometry');bytes(a.grid,grid,'preserved grid');bytes(fixture.stat_base,statMemory,'preserved stat graphs');
  return {result:'pass',helpers:counts,timer_cases:fixture.timers.length,probe_release_cases:fixture.release.length,...worldCounts,
    nan_fields_classification_only:nanFields,dispatch_backend:'Original SSE routine 005df4ac; CPU/registry selection not recovered',
    scope:'Complete downward update with training collision, stat lookup and timing; constructed states, no full movement loop. Hardware transcendental accuracy unverified.'};
}
