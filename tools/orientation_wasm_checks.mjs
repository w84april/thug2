export async function verifyOrientation(wasm,fixture,loadBinary){
  const {instance:{exports:e}}=await WebAssembly.instantiate(wasm);
  const memory=new Uint8Array(e.memory.buffer),v=new DataView(e.memory.buffer),a=fixture.addresses,base=fixture.loader;
  const unhex=text=>Uint8Array.from(text.match(/../g)??[],b=>parseInt(b,16)),guard=new Uint8Array(16).fill(0xad);
  function equal(actual,expected,label){if(actual!==expected)throw new Error(label+': '+actual+' != '+expected);}
  function atEqual(at,expected,label){for(let i=0;i<expected.length;i++)if(memory[at+i]!==expected[i])throw new Error(label+': byte '+i+', '+memory[at+i]+' != '+expected[i]);}
  let nanFields=0;
  function floatsEqual(at,expected,label){
    const dv=new DataView(expected.buffer,expected.byteOffset,expected.byteLength);
    for(let i=0;i<expected.length;i+=4){
      if(Number.isNaN(v.getFloat32(at+i,true))&&Number.isNaN(dv.getFloat32(i,true))){nanFields++;continue;}
      equal(v.getUint32(at+i,true),dv.getUint32(i,true),label+' float '+i);
    }
  }
  for(const [i,t] of fixture.comparisons.entries()){
    memory.set(unhex(t.left),a.left);memory.set(unhex(t.right),a.right);
    equal(e.thug_vector_not_equal(a.left,a.right),t.returned,'vector compare '+i);
    atEqual(a.left,unhex(t.left),'left preserved');atEqual(a.right,unhex(t.right),'right preserved');
  }
  for(const [i,t] of fixture.matrices.entries()){
    memory.set(unhex(t.input),a.matrix);memory.set(guard,a.matrix+64);
    equal(e.thug_matrix_orthogonalize(a.matrix,t.axis),a.matrix,'matrix return');
    floatsEqual(a.matrix,unhex(t.output),'matrix '+i);atEqual(a.matrix+64,guard,'matrix guard');
    atEqual(a.matrix+t.axis*16,unhex(t.input).slice(t.axis*16,t.axis*16+16),'fixed axis preserved');
    atEqual(a.matrix+48,unhex(t.input).slice(48),'translation preserved');
  }
  const data=await loadBinary(base.loaded),grid=await loadBinary(base.grid),heap=Uint8Array.from(await loadBinary(base.heap));
  const hv=new DataView(heap.buffer);
  for(let i=0;i<base.count;i++)hv.setUint32(base.instances-a.heap+i*24,e.thug_static_collision_methods.value,true);
  memory.set(data,a.data);memory.set(grid,a.grid);memory.fill(0,a.scene,a.scene+0xd4);v.setUint32(a.scene+0xd4,a.grid,true);
  [0,a.scene,0,a.scenes+16,0,0xffffffff,0,a.scenes+16].forEach((n,i)=>v.setUint32(a.scenes+i*4,n,true));
  v.setUint32(e.thug_collision_scene_list.value,a.scenes,true);v.setUint32(e.thug_moving_collision_list.value,a.nodes,true);
  v.setUint32(e.thug_collision_default_cache.value,0,true);v.setUint32(e.thug_skater_orientation_context.value,a.context,true);
  for(let j=0;j<3;j++)[0,a.runtime+j*0x100,0,a.nodes+(j+1)*16].forEach((n,i)=>v.setUint32(a.nodes+j*16+i*4,n,true));
  [0,0xffffffff,0,a.nodes+48].forEach((n,i)=>v.setUint32(a.nodes+48+i*4,n,true));
  for(let i=0;i<base.count;i++)e.thug_collision_has_tree(a.data+32+i*64);
  function actors(text){const b=unhex(text),dv=new DataView(b.buffer);for(let i=0;i<3;i++)dv.setUint32(i*0x100,e.thug_moving_collision_methods.value,true);return b;}
  const counts={updates:0,probes:0,probe_hits:0,matrix_updates:0,unchanged_targets:0};
  for(const [i,t] of fixture.world.entries()){
    const label='orientation update '+i;
    memory.set(heap,a.heap);memory.set(unhex(fixture.owners),a.owners);memory.set(unhex(fixture.references),a.refs);
    memory.set(actors(t.actors),a.runtime);memory.set(unhex(t.body),a.body);memory.set(guard,a.body+0xbc);
    memory.set(unhex(t.physics),a.physics);memory.set(guard,a.physics+0x318);memory.set(unhex(t.initial_state),a.state);
    memory.fill(0xad,a.context,a.context+64);v.setUint32(a.context+64,t.mode,true);const context=memory.slice(a.context,a.context+68);
    memory[e.thug_collision_grid_stamp.value]=t.stamp;memory[e.thug_collision_select_farthest.value]=0;
    const up=new DataView(unhex(t.up).buffer);
    e.thug_skater_set_up_vector(a.physics,up.getFloat32(0,true),up.getFloat32(4,true),up.getFloat32(8,true),up.getFloat32(12,true),a.state);
    const physics=unhex(t.physics_after),body=unhex(t.body_after);
    atEqual(a.physics,physics.slice(0,0x58),label+' physics prefix');floatsEqual(a.physics+0x58,physics.slice(0x58,0x8c),label+' orientation state');
    atEqual(a.physics+0x8c,physics.slice(0x8c),label+' physics suffix');atEqual(a.physics+0x318,guard,label+' physics guard');
    atEqual(a.body,body.slice(0,0x6c),label+' body prefix');floatsEqual(a.body+0x6c,body.slice(0x6c,0xac),label+' matrix');
    atEqual(a.body+0xac,body.slice(0xac),label+' velocity');atEqual(a.body+0xbc,guard,label+' body guard');
    atEqual(a.runtime,actors(t.actors_after),label+' actors');atEqual(a.owners,unhex(fixture.owners),label+' owners');
    atEqual(a.refs,unhex(fixture.references),label+' references');atEqual(a.context,context,label+' context');
    atEqual(a.state,unhex(t.state),label+' BSP state');equal(memory[e.thug_collision_grid_stamp.value],t.final_stamp,label+' grid stamp');
    const expectedHeap=heap.slice(),stamps=unhex(t.stamps);
    for(let j=0;j<base.count;j++)expectedHeap[base.instances-a.heap+j*24+10]=stamps[j];
    atEqual(a.heap,expectedHeap,label+' static heap');
    counts.updates++;for(const name of ['probes','probe_hits','matrix_updates'])counts[name]+=t.events[name]??0;
    if(!t.events.matrix_updates)counts.unchanged_targets++;
  }
  atEqual(a.data,data,'orientation preserves geometry');atEqual(a.grid,grid,'orientation preserves grid');
  return {result:'pass',...counts,vector_comparisons:fixture.comparisons.length,matrix_cases:fixture.matrices.length,
    nan_fields_classification_only:nanFields,coverage_source:'Probe and matrix-call counts observed in the original x86 oracle',
    scope:'Up-vector changes, obstruction probes and basis repair; constructed states, no complete movement loop'};
}
