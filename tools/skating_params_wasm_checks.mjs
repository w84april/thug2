export async function verifySkatingParams(wasm,fixture,loadBinary){
  const {instance:{exports:e}}=await WebAssembly.instantiate(wasm);
  const memory=new Uint8Array(e.memory.buffer),v=new DataView(e.memory.buffer),a=fixture.addresses;
  const unhex=text=>Uint8Array.from(text.match(/../g)??[],b=>parseInt(b,16)),guard=new Uint8Array(16).fill(0xad);
  function equal(actual,expected,label){if(actual!==expected)throw new Error(label+': '+actual+' != '+expected);}
  function atEqual(at,expected,label){for(let i=0;i<expected.length;i++)if(memory[at+i]!==expected[i])throw new Error(label+': byte '+i+', '+memory[at+i]+' != '+expected[i]);}
  let nanFields=0;
  function floatWordsEqual(at,text,label){const data=unhex(text),dv=new DataView(data.buffer);for(let i=0;i<data.length;i+=4){
    if(Number.isNaN(v.getFloat32(at+i,true))&&Number.isNaN(dv.getFloat32(i,true))){nanFields++;continue;}
    equal(v.getUint32(at+i,true),dv.getUint32(i,true),label+' float '+i);
  }}
  const old=await loadBinary('params-memory.bin');memory.set(old,a.symbols);v.setUint32(e.thug_script_symbol_buckets.value,a.symbols,true);
  for(const [name,assertMissing,expected] of fixture.global_structures)equal(e.thug_script_get_global_structure(name,assertMissing)>>>0,expected,'global structure '+name);
  atEqual(a.symbols,old,'global structure getter preserves symbol data');
  const body=unhex(fixture.body_initial),physics=unhex(fixture.physics_initial),components=unhex(fixture.component_memory),scripts=fixture.scripts.map(unhex);
  memory.set(body,a.body);memory.set(physics,a.physics);memory.set(components,a.components);memory.fill(0xad,a.state,a.state+0x24);
  for(const [head,name,expected] of fixture.component_cases){
    v.setUint32(a.body+0x100,head,true);equal(e.thug_object_find_component(a.body,name),expected,'component lookup');
  }
  atEqual(a.physics,physics,'component lookup preserves physics');atEqual(a.components,components,'component lookup preserves list');
  function configure(t){
    memory.set(scripts[t.profile],a.symbols);memory.set(guard,a.symbols+scripts[t.profile].length);
    memory.set(body,a.body);memory.set(guard,a.body+0x104);memory.set(physics,a.physics);memory.set(guard,a.physics+0x152c);
    memory[a.body+0xbc]=t.enabled;memory[a.physics+0x2ed]=t.active;v.setUint32(a.physics+0x2f0,t.mode,true);memory[a.physics+0x302]=t.fallback;
    return t.null_body?0:a.body;
  }
  function unchanged(t,beforeBody,beforePhysics,label){
    atEqual(a.body,beforeBody,label+' body');atEqual(a.physics,beforePhysics,label+' physics');
    atEqual(a.symbols,scripts[t.profile],label+' script');atEqual(a.symbols+scripts[t.profile].length,guard,label+' script guard');
    atEqual(a.components,components,label+' component list');
  }
  for(const [i,t] of fixture.selections.entries()){
    const ptr=configure(t),beforeBody=memory.slice(a.body,a.body+0x114),beforePhysics=memory.slice(a.physics,a.physics+0x153c);
    equal(e.thug_skater_parameter_set(ptr),t.selected,'parameter set '+i);unchanged(t,beforeBody,beforePhysics,'parameter set '+i);
  }
  for(const [i,t] of fixture.parameters.entries()){
    const ptr=configure(t),beforeBody=memory.slice(a.body,a.body+0x114),beforePhysics=memory.slice(a.physics,a.physics+0x153c);
    const actual=e.thug_skater_get_parameter(t.name,t.assert_missing,ptr),expected=new DataView(unhex(t.output).buffer).getFloat64(0,true);
    if(Number.isNaN(actual)&&Number.isNaN(expected))nanFields++;
    else if(!Object.is(actual,expected))throw new Error('numeric parameter '+i+': '+actual+' != '+expected);
    unchanged(t,beforeBody,beforePhysics,'numeric parameter '+i);
  }
  for(const [i,t] of fixture.drag.entries()){
    configure(t);memory.set(unhex(t.velocity),a.body+0xac);v.setFloat32(a.physics+0x8c,t.time_step,true);
    v.setUint32(a.physics+0x350,t.override_flag,true);v.setFloat32(a.physics+0x35c,t.override,true);
    memory.fill(0xad,a.state,a.state+0x24);memory[a.state+0x20]=t.selector;
    const expectedBody=memory.slice(a.body,a.body+0x114),beforePhysics=memory.slice(a.physics,a.physics+0x153c),state=memory.slice(a.state,a.state+0x24);
    e.thug_skater_apply_drag(a.physics);
    floatWordsEqual(a.body+0xac,t.output,'configured drag '+i);
    // Exclude the velocity words already compared, retaining exact byte checks for everything else.
    expectedBody.set(memory.slice(a.body+0xac,a.body+0xbc),0xac);
    unchanged(t,expectedBody,beforePhysics,'configured drag '+i);atEqual(a.state,state,'configured drag state');
  }
  return {result:'pass',global_structures:fixture.global_structures.length,component_cases:fixture.component_cases.length,
    selections:fixture.selections.length,parameter_cases:fixture.parameters.length,drag_calls:fixture.drag.length,
    original_parameter_reads:fixture.drag.length*2,nan_fields_classification_only:nanFields,
    scope:'Complete script-selected drag chain using constructed component lists and QB graphs; no script loader or full movement loop'};
}
