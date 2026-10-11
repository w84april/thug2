export async function verifySurface(wasm, fixture, loadBinary) {
  const {instance:{exports:e}}=await WebAssembly.instantiate(wasm);
  const memory=new Uint8Array(e.memory.buffer),v=new DataView(e.memory.buffer),a=fixture.addresses,base=fixture.loader;
  const unhex=text=>Uint8Array.from(text.match(/../g)??[],b=>parseInt(b,16)),guard=new Uint8Array(16).fill(0xad);
  function equal(actual,expected,label){if(actual!==expected)throw new Error(label+': '+actual+' != '+expected);}
  function atEqual(at,expected,label){for(let i=0;i<expected.length;i++)if(memory[at+i]!==expected[i])throw new Error(label+': byte '+i+', '+memory[at+i]+' != '+expected[i]);}
  memory.set(unhex(fixture.script_memory),a.symbols);v.setUint32(e.thug_script_symbol_buckets.value,a.symbols,true);
  function symbol(type,word){memory[a.symbols+0x4001]=type;v.setUint32(a.symbols+0x400c,word,true);}
  let nanFields=0,documentedOracleDifferences=0,infinitySpecificationChecks=0;
  for(const [i,t] of fixture.globals.entries()){
    symbol(t.type,t.value);const actual=e.thug_script_get_global_number(0x3eede4d3,1),expected=new DataView(unhex(t.output).buffer).getFloat64(0,true);
    if(Number.isNaN(actual)&&Number.isNaN(expected)){nanFields++;continue;}
    if(!Object.is(actual,expected))throw new Error('numeric getter '+i+': '+actual+' != '+expected);
  }
  for(const [i,t] of fixture.flags.entries()){
    memory.set(unhex(t.initial),a.probe);memory.set(guard,a.probe+176);
    e.thug_collision_probe_set_flags(a.probe,t.excluded,t.required);
    atEqual(a.probe,unhex(t.output),'flag setter '+i);atEqual(a.probe+176,guard,'flag setter guard');
  }
  for(const [i,t] of fixture.classifications.entries()){
    symbol(t.type,t.angle);memory.fill(0xad,a.physics,a.physics+0x328);
    v.setUint16(a.physics+0xf8,t.flags,true);v.setUint32(a.physics+0x100,t.checksum,true);
    memory[a.physics+0x115]=t.flag40;v.setUint32(a.physics+0x134,t.normal,true);
    const expected=memory.slice(a.physics,a.physics+0x328);
    expected.set(unhex(t.cleared),0x104);expected.set(unhex(t.documented_processor_output??t.output),0x228);
    if(t.documented_processor_output){infinitySpecificationChecks++;if(t.output!==t.documented_processor_output)documentedOracleDifferences++;}
    e.thug_skater_classify_surface(a.physics);
    atEqual(a.physics,expected,'surface classification '+i+' '+JSON.stringify(t));
  }
  const data=await loadBinary(base.loaded),grid=await loadBinary(base.grid),heap=Uint8Array.from(await loadBinary(base.heap));
  const hv=new DataView(heap.buffer);
  for(let i=0;i<base.count;i++)hv.setUint32(base.instances-a.heap+i*24,e.thug_static_collision_methods.value,true);
  memory.set(data,a.data);memory.set(grid,a.grid);memory.fill(0,a.scene,a.scene+0xd4);v.setUint32(a.scene+0xd4,a.grid,true);
  [0,a.scene,0,a.scenes+16,0,0xffffffff,0,a.scenes+16].forEach((n,i)=>v.setUint32(a.scenes+i*4,n,true));
  v.setUint32(e.thug_collision_scene_list.value,a.scenes,true);v.setUint32(e.thug_moving_collision_list.value,a.nodes,true);
  v.setUint32(e.thug_collision_default_cache.value,0,true);
  for(let j=0;j<3;j++)[0,a.runtime+j*0x100,0,a.nodes+(j+1)*16].forEach((n,i)=>v.setUint32(a.nodes+j*16+i*4,n,true));
  [0,0xffffffff,0,a.nodes+48].forEach((n,i)=>v.setUint32(a.nodes+48+i*4,n,true));
  for(let i=0;i<base.count;i++)e.thug_collision_has_tree(a.data+32+i*64);
  function actors(text){const b=unhex(text),dv=new DataView(b.buffer);for(let i=0;i<3;i++)dv.setUint32(i*0x100,e.thug_moving_collision_methods.value,true);return b;}
  const counts={queries:0,hits:0,skatable:0,flag_8:0,flag_4:0};
  for(const [i,t] of fixture.world.entries()){
    const label='surface query '+i;
    memory.set(heap,a.heap);memory.set(unhex(t.owners),a.owners);memory.set(unhex(t.references),a.refs);
    memory.set(actors(t.actors),a.runtime);memory.set(unhex(t.body),a.body);memory.set(guard,a.body+0xbc);
    memory.set(unhex(t.physics),a.physics);memory.set(guard,a.physics+0x318);memory.set(unhex(t.initial_state),a.state);
    memory[a.symbols+0x4001]=2;v.setFloat32(a.symbols+0x400c,t.angle,true);
    memory[e.thug_collision_grid_stamp.value]=t.stamp;memory[e.thug_collision_select_farthest.value]=0;
    equal(e.thug_skater_query_surface(a.physics,t.excluded,t.required,a.state),t.returned,label+' return');
    atEqual(a.physics,unhex(t.physics_after),label+' physics');atEqual(a.physics+0x318,guard,label+' physics guard');
    atEqual(a.body,unhex(t.body),label+' body');atEqual(a.body+0xbc,guard,label+' body guard');
    atEqual(a.runtime,actors(t.actors_after),label+' actors');atEqual(a.owners,unhex(t.owners_after),label+' owners');
    atEqual(a.refs,unhex(t.references_after),label+' references');atEqual(a.state,unhex(t.state),label+' BSP state');
    equal(memory[e.thug_collision_grid_stamp.value],t.final_stamp,label+' grid stamp');
    const expectedHeap=heap.slice(),stamps=unhex(t.stamps);
    for(let j=0;j<base.count;j++)expectedHeap[base.instances-a.heap+j*24+10]=stamps[j];
    atEqual(a.heap,expectedHeap,label+' static heap');
    counts.queries++;counts.hits+=t.returned;
    if(t.returned){counts.skatable+=memory[a.physics+0x228];counts.flag_8+=memory[a.physics+0x229];counts.flag_4+=memory[a.physics+0x22a];}
  }
  atEqual(a.data,data,'surface query preserves geometry');atEqual(a.grid,grid,'surface query preserves grid');
  return {result:'pass',...counts,numeric_getters:fixture.globals.length,flag_setters:fixture.flags.length,
    classifications:fixture.classifications.length,nan_fields_classification_only:nanFields,
    documented_oracle_differences:documentedOracleDifferences,infinity_specification_checks:infinitySpecificationChecks,
    scope:'Full surface query; Unicorn FSIN uses host double sine, infinity follows Intel documentation; hardware transcendental accuracy remains unverified'};
}
