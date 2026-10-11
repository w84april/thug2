export async function verifyScene(wasm, fixture, loadBinary) {
  const { instance: { exports: engine } } = await WebAssembly.instantiate(wasm);
  const memory = new Uint8Array(engine.memory.buffer), view = new DataView(engine.memory.buffer);
  const a = fixture.addresses;
  const unhex = text => Uint8Array.from(text.match(/../g) ?? [], b => parseInt(b, 16));
  const globals = {
    scene_output: engine.thug_collision_selected_scenes.value,
    grid_selection: engine.thug_collision_selected_grids.value,
    grid_output: engine.thug_collision_grid_output.value,
    stamp: engine.thug_collision_grid_stamp.value,
    selection: engine.thug_collision_select_farthest.value,
    head: engine.thug_collision_scene_list.value
  };
  const callbackWasm = await loadBinary('callback-fixture.wasm');
  const { instance: { exports: callback } } = await WebAssembly.instantiate(callbackWasm,
    { env: { memory: engine.memory } });
  const callbackIndex = engine.__indirect_function_table.grow(1);
  engine.__indirect_function_table.set(callbackIndex, callback.record_hit);
  if (engine.thug_collision_get_selected_scenes() !== globals.scene_output) throw new Error('Selected scenes getter');

  function equal(actual, expected, label) {
    for (let i = 0; i < expected.length; i++)
      if (actual[i] !== expected[i]) throw new Error(label + ': byte ' + i + ', ' + actual[i] + ' != ' + expected[i]);
  }
  function atEqual(at, expected, label) { equal(memory.subarray(at, at + expected.length), expected, label); }
  function patchResults(bytes) {
    const v = new DataView(bytes.buffer, bytes.byteOffset, bytes.length);
    for (let at = 0; at < bytes.length; at += 80)
      if (v.getUint32(at + 0x3c, true) === a.callback) v.setUint32(at + 0x3c, callbackIndex, true);
    return bytes;
  }
  function patchMethods(bytes, objects) {
    const v = new DataView(bytes.buffer, bytes.byteOffset, bytes.length);
    for (const object of objects) v.setUint32(object.pointer - a.data, engine.thug_static_collision_methods.value, true);
  }
  for (const helper of fixture.helpers) {
    memory.set(unhex(helper.a), a.segment); memory.set(unhex(helper.b), a.bounds);
    if (engine.thug_bounds_overlap(a.segment, a.bounds) !== helper.overlap) throw new Error('Box overlap');
    if (engine.thug_bounds_contains(a.segment, a.bounds) !== helper.contains) throw new Error('Box containment');
    atEqual(a.segment, unhex(helper.a), 'Box receiver changed');
    atEqual(a.bounds, unhex(helper.b), 'Box argument changed');
    if (helper.point_bounds) {
      memory.fill(0xad, a.bounds, a.bounds + 48);
      if (engine.thug_bounds_from_point(a.bounds, a.segment) !== a.bounds) throw new Error('Box return pointer');
      atEqual(a.bounds, unhex(helper.point_bounds), 'Point bounds');
      atEqual(a.bounds + 32, new Uint8Array(16).fill(0xad), 'Point bounds guard');
    }
  }
  const counts = { grid: 0, scenes: 0, scene: 0, farthest: 0, cached: 0, callbacks: 0 };
  for (const dataset of fixture.datasets) {
    const initialMemory = await loadBinary(dataset.name + '.bin');
    patchMethods(initialMemory, dataset.objects);
    memory.set(initialMemory, a.data);
    for (const object of dataset.objects) engine.thug_collision_has_tree(object.geometry);
    for (let index = 0; index < dataset.cases.length; index++) {
      const test = dataset.cases[index], label = dataset.name + '/' + index + '/' + test.kind;
      for (const [at, bytes] of test.patches) memory.set(unhex(bytes), at);
      view.setUint32(globals.head, test.head, true);
      for (const [name, size] of [['scene_output', 64], ['grid_selection', 64], ['grid_output', 8192]])
        memory.fill(0xad, globals[name], globals[name] + size);
      memory[globals.stamp] = test.stamp; memory[globals.selection] = test.farthest;
      memory.set(unhex(test.segment), a.segment);
      memory.fill(0xad, a.count, a.count + 4);
      memory.fill(0xad, a.result - 16, a.result + 96);
      memory.set(unhex(test.initial), a.result);
      memory.set(unhex(test.initial_state), a.state);
      view.setUint32(a.control, Math.max(0, test.callback_mode), true);
      view.setUint32(a.control + 4, 0, true);
      view.setUint32(a.control + 8, globals.selection, true);
      let result, expected = test.returned;
      if (test.kind === 'grid') {
        result = engine.thug_collision_grid_query(a.grid, a.segment, test.optional_count ? a.count : 0);
        expected = globals.grid_output;
      } else if (test.kind === 'scenes') {
        result = engine.thug_collision_select_scenes(a.segment);
        expected = expected ? globals.grid_selection : 0;
      } else {
        const fn = test.kind === 'farthest' ? engine.thug_collision_scene_segment_farthest : engine.thug_collision_scene_segment;
        result = fn(a.segment, a.result, test.callback_mode >= 0 ? callbackIndex : 0,
          test.cache ? a.cache : 0, a.state);
      }
      if (result !== expected) throw new Error(label + ': return ' + result + ' != ' + expected);
      atEqual(a.result, patchResults(unhex(test.result)), label + ' result');
      atEqual(a.result - 16, new Uint8Array(16).fill(0xad), label + ' prefix guard');
      atEqual(a.result + 80, new Uint8Array(16).fill(0xad), label + ' suffix guard');
      atEqual(a.segment, unhex(test.segment), label + ' segment changed');
      atEqual(a.count, unhex(test.count), label + ' optional count');
      atEqual(a.state, unhex(test.state), label + ' BSP state');
      for (const name of ['scene_output', 'grid_selection', 'grid_output'])
        atEqual(globals[name], unhex(test[name]), label + ' ' + name);
      if (memory[globals.stamp] !== test.final_stamp || memory[globals.selection] !== test.final_farthest)
        throw new Error(label + ': query mode/stamp');
      const stamps = unhex(test.stamps);
      for (let i = 0; i < dataset.objects.length; i++)
        if (memory[dataset.objects[i].pointer + 10] !== stamps[i]) throw new Error(label + ': object stamp ' + i);
      const callbacks = patchResults(unhex(test.callbacks));
      const n = view.getUint32(a.control + 4, true);
      if (callbacks.length !== n * 80) throw new Error(label + ': callback count');
      atEqual(a.log, callbacks, label + ' callback observations');
      counts[test.kind]++;
      counts.cached += test.cache ? 1 : 0;
      counts.callbacks += n;
    }
    const expectedMemory = await loadBinary(dataset.name + '-after.bin');
    patchMethods(expectedMemory, dataset.objects);
    atEqual(a.data, expectedMemory, dataset.name + ' final memory');
  }
  return { result: 'pass', ...counts, box_comparisons: fixture.helpers.length * 2,
           point_bounds_cases: fixture.helpers.filter(x => x.point_bounds).length,
           scope: 'Constructed scene grids and caches; original training geometry' };
}
