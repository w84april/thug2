export async function verifyParams(wasm, fixture, loadBinary) {
  const {instance:{exports:engine}} = await WebAssembly.instantiate(wasm);
  const a=fixture.addresses, bytes=new Uint8Array(engine.memory.buffer), view=new DataView(engine.memory.buffer);
  const source=await loadBinary('params-memory.bin');bytes.set(source,a.base);
  view.setUint32(engine.thug_script_symbol_buckets.value,a.base,true);
  function equal(actual,expected,label) { if(actual!==expected) throw new Error(label+': '+actual+' != '+expected); }
  for(const [name,expected] of fixture.lookups) equal(engine.thug_script_resolve_symbol(name),expected,'symbol '+name);
  for(const [index,test] of fixture.cases.entries()) {
    view.setUint32(a.output,test.initial,true);bytes.fill(0xad,a.output+4,a.output+20);
    const returned=test.kind==='typed'?engine.thug_script_get_typed(test.root,test.name,test.type,a.output):
      engine.thug_script_get_float(test.root,test.name,a.output,test.assert_missing);
    equal(returned,test.returned,'parameter '+index+' return');equal(view.getUint32(a.output,true),test.output,'parameter '+index+' output');
    for(let i=4;i<20;i++) equal(bytes[a.output+i],0xad,'parameter guard');
  }
  for(let i=0;i<source.length;i++) equal(bytes[a.base+i],source[i],'script memory unchanged');
  return {result:'pass',lookups:fixture.lookups.length,parameter_cases:fixture.cases.length,
    scope:'Constructed symbol/component graphs; no script file loading or execution'};
}
