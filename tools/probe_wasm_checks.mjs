export async function verifyProbes(wasm, fixture, loadBinary) {
  const { instance: { exports: engine } } = await WebAssembly.instantiate(wasm);
  const memory = new Uint8Array(engine.memory.buffer), view = new DataView(engine.memory.buffer);
  const a = fixture.addresses, base = fixture.loader;
  const unhex = text => Uint8Array.from(text.match(/../g) ?? [], b => parseInt(b, 16));
  const table = engine.__indirect_function_table;
  const callbackIndex = table.grow(2);
  const { instance: { exports: ordinary } } = await WebAssembly.instantiate(await loadBinary('callback-fixture.wasm'), { env: { memory: engine.memory } });
  const { instance: { exports: probeCallback } } = await WebAssembly.instantiate(await loadBinary('probe-callback-fixture.wasm'), { env: { memory: engine.memory } });
  table.set(callbackIndex, ordinary.record_hit); table.set(callbackIndex + 1, probeCallback.record_probe);
  let bridge = -1;
  for (let i = 0; i < table.length; i++) if (table.get(i) === engine.thug_collision_probe_callback) bridge = i;
  if (bridge < 0) throw new Error('Probe callback bridge missing from function table');
  const selection = engine.thug_collision_select_farthest.value, stamp = engine.thug_collision_grid_stamp.value;
  const data = await loadBinary(base.loaded), grid = await loadBinary(base.grid);
  const heap = await loadBinary(base.heap), heapView = new DataView(heap.buffer, heap.byteOffset, heap.length);
  for (let i = 0; i < base.count; i++) heapView.setUint32(base.instances - a.heap + i * 24, engine.thug_static_collision_methods.value, true);
  memory.set(data, a.data); memory.set(grid, a.grid);
  for (let i = 0; i < base.count; i++) engine.thug_collision_has_tree(a.data + 32 + i * 64);
  memory.fill(0, a.scene, a.scene + 0xd4); view.setUint32(a.scene + 0xd4, a.grid, true);
  [0,a.scene,0,a.scenes+16,0,0xffffffff,0,a.scenes+16].forEach((v,i) => view.setUint32(a.scenes+i*4,v,true));
  view.setUint32(engine.thug_collision_scene_list.value, a.scenes, true);
  const runtime = await loadBinary('probe-runtime.bin'), guard = new Uint8Array(16).fill(0xad);
  function equal(actual, expected, label) { if (actual !== expected) throw new Error(label + ': ' + actual + ' != ' + expected); }
  function atEqual(at, expected, label) {
    for (let i = 0; i < expected.length; i++)
      if (memory[at+i] !== expected[i]) throw new Error(label + ': byte ' + i + ', ' + memory[at+i] + ' != ' + expected[i]);
  }
  function patchRuntime(bytes, actors) {
    const result = Uint8Array.from(bytes), v = new DataView(result.buffer);
    for (const actor of actors) v.setUint32(actor - a.runtime, engine.thug_moving_collision_methods.value, true);
    return result;
  }
  function patchCallbacks(text, isProbe) {
    const bytes = unhex(text), v = new DataView(bytes.buffer), stride = isProbe ? 176 : 80;
    for (let at = 0; at < bytes.length; at += stride) {
      const result = at + (isProbe ? 36 : 0);
      const cb = v.getUint32(result + 0x3c, true);
      if (cb === a.callback) v.setUint32(result + 0x3c, callbackIndex, true);
      if (cb === 0x417110) v.setUint32(result + 0x3c, bridge, true);
      if (isProbe && v.getUint32(at + 32, true) === a.probe_callback) v.setUint32(at + 32, callbackIndex + 1, true);
    }
    return bytes;
  }
  const counts = { moving: 0, farthest: 0, probe: 0, callbacks: 0, nonzero_returns: 0, attached_moving_objects: 0 };
  for (const [i,test] of fixture.cases.entries()) {
    const label = 'probe test ' + i + '/' + test.kind;
    memory.set(heap, a.heap);
    memory.set(patchRuntime(runtime.subarray(test.runtime_offset, test.runtime_offset + 0x5000), test.actors), a.runtime);
    memory.set(unhex(test.segment), a.segment);
    memory.set(patchCallbacks(test.initial_probe, true), a.probe); memory.set(guard, a.probe + 176);
    memory.set(patchCallbacks(test.initial_result, false), a.result); memory.set(guard, a.result + 80);
    memory.set(unhex(test.initial_state), a.state);
    view.setUint32(engine.thug_moving_collision_list.value, test.head, true);
    view.setUint32(engine.thug_collision_default_cache.value, test.default_cache, true);
    memory[selection] = test.selection; memory[stamp] = test.stamp;
    [Math.max(0,test.mode),0,selection].forEach((v,j) => view.setUint32(a.control+j*4,v,true));
    const isProbe = test.kind === 'probe';
    let returned;
    if (isProbe) returned = engine.thug_collision_probe_query(a.probe, test.check_moving, test.farthest, a.state);
    else {
      const fn = test.kind === 'farthest' ? engine.thug_moving_scene_segment_farthest : engine.thug_moving_scene_segment;
      returned = fn(a.segment,a.result,test.mode>=0 ? callbackIndex : 0,test.cache,a.state);
    }
    equal(returned,test.returned,label+' return');
    atEqual(a.probe,patchCallbacks(test.probe,true),label+' probe');
    atEqual(a.result,patchCallbacks(test.result,false),label+' result');
    atEqual(a.probe+176,guard,label+' probe guard'); atEqual(a.result+80,guard,label+' result guard');
    atEqual(a.state,unhex(test.state),label+' BSP state'); atEqual(a.segment,unhex(test.segment),label+' input segment');
    equal(memory[selection],test.final_selection,label+' selection'); equal(memory[stamp],test.final_stamp,label+' stamp');
    atEqual(a.runtime,patchRuntime(runtime.subarray(test.runtime_offset+0x5000,test.runtime_offset+0xa000),test.actors),label+' runtime/reference lists');
    const expectedHeap = Uint8Array.from(heap), stamps = unhex(test.stamps);
    for (let j = 0; j < base.count; j++) expectedHeap[base.instances-a.heap+j*24+10] = stamps[j];
    atEqual(a.heap,expectedHeap,label+' static heap');
    const n = view.getUint32(a.control+4,true), observations = patchCallbacks(test.callbacks,isProbe);
    equal(n*(isProbe?176:80),observations.length,label+' callback count'); atEqual(a.log,observations,label+' callbacks');
    counts[test.kind]++; counts.callbacks+=n; counts.nonzero_returns+=returned?1:0;
    if (isProbe && view.getUint32(a.probe+0x98,true)) counts.attached_moving_objects++;
  }
  atEqual(a.data,data,'probe preserves geometry'); atEqual(a.grid,grid,'probe preserves grid');
  return { result: 'pass', ...counts, scope: 'Complete probes using loader-built static grid, rigid moving objects and instrumented callbacks' };
}
