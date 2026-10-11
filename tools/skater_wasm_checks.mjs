export async function verifySkater(wasm, fixture, loadBinary) {
  const {instance:{exports:engine}}=await WebAssembly.instantiate(wasm);
  const memory=new Uint8Array(engine.memory.buffer),view=new DataView(engine.memory.buffer),a=fixture.addresses,base=fixture.loader;
  const unhex=text=>Uint8Array.from(text.match(/../g)??[],b=>parseInt(b,16)),guard=new Uint8Array(16).fill(0xad);
  function equal(actual,expected,label){if(actual!==expected)throw new Error(label+': '+actual+' != '+expected);}
  function atEqual(at,expected,label){for(let i=0;i<expected.length;i++)if(memory[at+i]!==expected[i])throw new Error(label+': byte '+i+', '+memory[at+i]+' != '+expected[i]);}
  let nanFields=0;
  function vectorEqual(at,text,label){
    const expected=unhex(text),v=new DataView(expected.buffer);
    for(let i=0;i<16;i+=4){
      if(Number.isNaN(view.getFloat32(at+i,true))&&Number.isNaN(v.getFloat32(i,true))){nanFields++;continue;}
      equal(view.getUint32(at+i,true),v.getUint32(i,true),label+' field '+i);
    }
  }
  for(const [i,test] of fixture.constructors.entries()){
    memory.set(unhex(test.initial),a.probe);memory.set(guard,a.probe+176);memory.set(unhex(test.points),a.points);
    if(test.kind==='default')equal(engine.thug_collision_probe_initialize(a.probe),a.probe,'constructor return');
    else if(test.kind==='points')equal(engine.thug_collision_probe_from_points(a.probe,a.points,a.points+16),a.probe,'point constructor return');
    else engine.thug_collision_probe_set_points(a.probe,a.points,a.points+16);
    atEqual(a.probe,unhex(test.output),'probe helper '+i);atEqual(a.probe+176,guard,'probe helper guard');atEqual(a.points,unhex(test.points),'point input');
  }
  for(const [i,test] of fixture.vectors.entries()){
    memory.set(unhex(test.input),a.vector);memory.set(guard,a.vector+16);
    equal(engine.thug_vector_set_length(a.vector,test.length),a.vector,'set length return');
    vectorEqual(a.vector,test.output,'set length '+i);atEqual(a.vector+16,guard,'set length guard');
  }
  const counts={drag:0,friction:0,nearby_queries:0,forward_queries:0,directions_found:0,forward_hits:0};
  for(const [i,test] of fixture.velocity.entries()){
    memory.fill(0xad,a.body,a.body+0xcc);memory.fill(0xad,a.physics,a.physics+0x328);
    memory.set(unhex(test.input),a.body+0xac);view.setUint32(a.physics+12,a.body,true);
    view.setFloat32(a.physics+0x8c,test.time_step,true);view.setFloat32(a.physics+0x314,test.coefficient,true);
    const physics=memory.slice(a.physics,a.physics+0x328);
    if(test.kind==='drag')engine.thug_skater_apply_quadratic_drag(a.physics,test.coefficient);
    else engine.thug_skater_apply_friction(a.physics);
    vectorEqual(a.body+0xac,test.output,test.kind+' '+i);
    atEqual(a.body,new Uint8Array(0xac).fill(0xad),'body prefix');atEqual(a.body+0xbc,guard,'body guard');
    atEqual(a.physics,physics,'physics fields unchanged');counts[test.kind]++;
  }
  const data=await loadBinary(base.loaded),grid=await loadBinary(base.grid),heap=Uint8Array.from(await loadBinary(base.heap));
  const hv=new DataView(heap.buffer);
  for(let i=0;i<base.count;i++)hv.setUint32(base.instances-a.heap+i*24,engine.thug_static_collision_methods.value,true);
  memory.set(data,a.data);memory.set(grid,a.grid);memory.fill(0,a.scene,a.scene+0xd4);view.setUint32(a.scene+0xd4,a.grid,true);
  [0,a.scene,0,a.scenes+16,0,0xffffffff,0,a.scenes+16].forEach((v,i)=>view.setUint32(a.scenes+i*4,v,true));
  view.setUint32(engine.thug_collision_scene_list.value,a.scenes,true);
  view.setUint32(engine.thug_moving_collision_list.value,a.nodes,true);view.setUint32(engine.thug_collision_default_cache.value,0,true);
  for(let j=0;j<3;j++)[0,a.runtime+j*0x100,0,a.nodes+(j+1)*16].forEach((v,i)=>view.setUint32(a.nodes+j*16+i*4,v,true));
  [0,0xffffffff,0,a.nodes+48].forEach((v,i)=>view.setUint32(a.nodes+48+i*4,v,true));
  memory.set(unhex(fixture.script_memory),a.symbols);view.setUint32(engine.thug_script_symbol_buckets.value,a.symbols,true);
  for(let i=0;i<base.count;i++)engine.thug_collision_has_tree(a.data+32+i*64);
  function actors(text){const bytes=unhex(text),v=new DataView(bytes.buffer);for(let i=0;i<3;i++)v.setUint32(i*0x100,engine.thug_moving_collision_methods.value,true);return bytes;}
  for(const [i,test] of fixture.world.entries()){
    const label='skater world '+i;
    memory.set(heap,a.heap);memory.set(unhex(fixture.owners),a.owners);memory.set(unhex(fixture.references),a.refs);
    memory.set(actors(test.actors),a.runtime);memory.set(unhex(test.body),a.body);memory.set(guard,a.body+0xbc);
    memory.set(unhex(test.physics),a.physics);memory.set(guard,a.physics+0x318);memory.set(unhex(test.params),a.params);
    memory.set(unhex(test.initial_state),a.state);
    memory[engine.thug_collision_grid_stamp.value]=test.stamp;memory[engine.thug_collision_select_farthest.value]=0;
    engine.thug_skater_nearby_obstacle(a.physics,a.state);
    equal(view.getUint32(a.physics+0x2d4,true),test.direction,label+' direction');
    equal(engine.thug_skater_forward_obstruction(a.physics,a.params,0xdeadbeef,a.state),test.returned,label+' forward return');
    atEqual(a.physics,unhex(test.physics_after),label+' physics');atEqual(a.physics+0x318,guard,label+' physics guard');
    atEqual(a.body,unhex(test.body),label+' body');atEqual(a.body+0xbc,guard,label+' body guard');
    atEqual(a.runtime,actors(test.actors_after),label+' actors');atEqual(a.owners,unhex(fixture.owners),label+' owners');
    atEqual(a.refs,unhex(fixture.references),label+' references');atEqual(a.params,unhex(test.params),label+' params');
    atEqual(a.state,unhex(test.state),label+' BSP state');equal(memory[engine.thug_collision_grid_stamp.value],test.final_stamp,label+' stamp');
    const expectedHeap=heap.slice(),stamps=unhex(test.stamps);
    for(let j=0;j<base.count;j++)expectedHeap[base.instances-a.heap+j*24+10]=stamps[j];
    atEqual(a.heap,expectedHeap,label+' static heap');
    counts.nearby_queries++;counts.forward_queries++;counts.directions_found+=test.direction?1:0;counts.forward_hits+=test.returned;
  }
  atEqual(a.data,data,'skater preserves collision geometry');atEqual(a.grid,grid,'skater preserves collision grid');
  return {result:'pass',...counts,probe_helpers:fixture.constructors.length,vector_length_cases:fixture.vectors.length,
    nan_fields_classification_only:nanFields,scope:'Individual skater velocity and obstacle routines; constructed states, no complete movement loop'};
}
