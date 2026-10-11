export async function verifyLowSpeed(wasm,fixture,loadBinary){
  const {instance:{exports:e}}=await WebAssembly.instantiate(wasm);
  const memory=new Uint8Array(e.memory.buffer),v=new DataView(e.memory.buffer),a=fixture.addresses,base=fixture.loader;
  const unhex=text=>Uint8Array.from(text.match(/../g)??[],b=>parseInt(b,16));
  let nanFields=0;
  function equal(actual,expected,label){if(actual!==expected)throw new Error(`${label}: ${actual} != ${expected}`);}
  function bytes(at,expected,label,floatRanges=[]){const dv=new DataView(expected.buffer,expected.byteOffset,expected.byteLength);
    for(let i=0;i<expected.length;){
      if(i%4===0&&floatRanges.some(([start,length])=>i>=start&&i+4<=start+length)
          &&Number.isNaN(v.getFloat32(at+i,true))&&Number.isNaN(dv.getFloat32(i,true))){nanFields++;i+=4;continue;}
      if(memory[at+i]!==expected[i])throw new Error(`${label} byte ${i.toString(16)}: ${memory[at+i]} != ${expected[i]}`);
      i++;
    }
  }
  function timer(config){['thug_frame_counter','thug_frame_rate','thug_timer_origin','thug_time_scale','thug_timer_offset'].forEach((name,i)=>v.setUint32(e[name].value,config[i],true));}
  for(const [i,t] of fixture.vectors.entries()){
    const label='axis projection '+i;memory.set(unhex(t.input),a.vector_block);
    equal(e.thug_vector_project_axis(a.vector_block+48,a.vector_block+48+t.offset),a.vector_block+48,label+' return');
    bytes(a.vector_block,unhex(t.output),label,[[48,16]]);
  }
  for(const [i,t] of fixture.buttons.entries()){
    const data=unhex(t.input);memory.set(data,a.button);timer(t.timer);
    equal(e.thug_input_button_elapsed(a.button+8)>>>0,t.result,'button timer '+i);bytes(a.button,data,'preserved button '+i);
  }
  memory.set(unhex(fixture.script_memory),a.symbols);v.setUint32(e.thug_script_symbol_buckets.value,a.symbols,true);
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
  const tail=unhex(fixture.physics_tail);
  for(const [i,t] of fixture.world.entries()){
    const label='low-speed correction '+i;
    memory.set(heap,a.heap);memory.set(unhex(t.owners),a.owners);memory.set(unhex(t.refs),a.refs);
    memory.set(actors(t.actors),a.runtime);memory.set(unhex(t.body),a.body);memory.set(unhex(t.physics),a.physics);
    memory.set(tail,a.physics+0x318);memory.set(unhex(t.input),a.input);memory.set(unhex(t.initial_state),a.state);timer(t.timer);
    for(const [j,[kind,value]] of t.settings.entries()){
      memory[a.symbols+0x4001+(j+1)*20]=kind;v.setUint32(a.symbols+0x400c+(j+1)*20,value,true);
    }
    memory[e.thug_collision_grid_stamp.value]=t.stamp;memory[e.thug_collision_select_farthest.value]=0;
    e.thug_skater_correct_low_speed_collision(a.physics,a.state);
    bytes(a.body,unhex(t.body_after),label+' body',[[0x4c,16]]);
    bytes(a.physics,unhex(t.physics_after),label+' physics',[[0xa8,32],[0xcc,32],[0xf0,4],[0x11c,36],[0x208,32]]);
    bytes(a.physics+0x318,tail,label+' preserved tail');bytes(a.input,unhex(t.input),label+' preserved input');
    bytes(a.runtime,actors(t.actors_after),label+' actors');bytes(a.owners,unhex(t.owners_after),label+' owners');bytes(a.refs,unhex(t.refs_after),label+' refs');
    bytes(a.state,unhex(t.state),label+' collision state');equal(memory[e.thug_collision_grid_stamp.value],t.final_stamp,label+' grid stamp');
    const expectedHeap=heap.slice(),stamps=unhex(t.stamps);for(let j=0;j<base.count;j++)expectedHeap[base.instances-a.heap+j*24+10]=stamps[j];bytes(a.heap,expectedHeap,label+' collision heap');
  }
  bytes(a.data,data,'preserved geometry');bytes(a.grid,grid,'preserved grid');
  return {result:'pass',vector_cases:fixture.vectors.length,button_cases:fixture.buttons.length,...fixture.totals,nan_fields_classification_only:nanFields,
    scope:'Complete low-speed side collision correction with two training-geometry probes, original input timer and numeric parameter dependencies; constructed input states, no complete movement loop.'};
}
