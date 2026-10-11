export async function verifyMoving(wasm, fixture, loadBinary) {
  const { instance: { exports: engine } } = await WebAssembly.instantiate(wasm);
  const memory = new Uint8Array(engine.memory.buffer), view = new DataView(engine.memory.buffer);
  const a = fixture.addresses, unhex = text => Uint8Array.from(text.match(/../g) ?? [], b => parseInt(b, 16));
  const data = await loadBinary('training-relocated.bin'); memory.set(data, a.data);
  const { instance: { exports: callback } } = await WebAssembly.instantiate(await loadBinary('callback-fixture.wasm'),
    { env: { memory: engine.memory } });
  const callbackIndex = engine.__indirect_function_table.grow(1);
  engine.__indirect_function_table.set(callbackIndex, callback.record_hit);
  const methods = engine.thug_moving_collision_methods.value, selection = engine.thug_collision_select_farthest.value;
  const guard = new Uint8Array(16).fill(0xad);
  function equal(actual, expected, label) { if (actual !== expected) throw new Error(label + ': ' + actual + ' != ' + expected); }
  function atEqual(at, expected, label) {
    for (let i = 0; i < expected.length; i++)
      if (memory[at + i] !== expected[i]) throw new Error(label + ': byte ' + i + ', ' + memory[at + i] + ' != ' + expected[i]);
  }
  function patchInstance(text) {
    const bytes = unhex(text); new DataView(bytes.buffer).setUint32(0, methods, true); return bytes;
  }
  function patchCallback(text) {
    const bytes = unhex(text), v = new DataView(bytes.buffer);
    for (let i = 0; i < bytes.length; i += 80)
      if (v.getUint32(i + 0x3c, true) === a.callback) v.setUint32(i + 0x3c, callbackIndex, true);
    return bytes;
  }
  for (const [i, test] of fixture.matrices.entries()) {
    const target = test.alias ? a.vector : a.output;
    memory.set(unhex(test.matrix), a.matrix); memory.set(unhex(test.input), a.vector);
    memory.set(guard, a.vector + 16); memory.fill(0xad, a.output, a.output + 32);
    equal(engine.thug_matrix_rotate_vector(a.matrix, target, a.vector), target, 'matrix return ' + i);
    atEqual(target, unhex(test.output), 'matrix output ' + i); atEqual(target + 16, guard, 'matrix guard ' + i);
    atEqual(a.matrix, unhex(test.matrix), 'matrix unchanged ' + i);
  }
  for (const [i, test] of fixture.helpers.entries()) {
    const label = 'moving helper ' + i;
    memory.set(unhex(test.initial), a.instance); memory.set(guard, a.instance + 0xd4);
    equal(engine.thug_moving_collision_initialize(a.instance, a.data + test.object), a.instance, label + ' return');
    atEqual(a.instance, patchInstance(test.initialized), label + ' initialized');
    memory.set(unhex(test.position), a.vector); memory.set(unhex(test.matrix), a.matrix);
    engine.thug_moving_collision_set_position(a.instance, a.vector);
    equal(engine.thug_moving_collision_set_orientation(a.instance, a.matrix), a.instance + 0x60, label + ' orientation return');
    engine.thug_moving_collision_set_owner(a.instance, 0x12345678);
    equal(engine.thug_moving_collision_owner(a.instance), 0x12345678, label + ' owner');
    atEqual(a.instance, patchInstance(test.positioned), label + ' positioned');
    engine.thug_moving_collision_update_bounds(a.instance);
    atEqual(a.instance, patchInstance(test.updated), label + ' updated');
    memory.set(unhex(test.bounds), a.bounds);
    equal(engine.thug_moving_collision_intersects(a.instance, a.bounds), test.overlap, label + ' overlap');
    atEqual(a.instance, patchInstance(test.final), label + ' overlap instance');
    atEqual(a.instance + 0xd4, guard, label + ' guard');
    const target = test.alias ? a.segment : a.output;
    memory.set(unhex(test.local_input), a.segment); memory.set(guard, a.segment + 32);
    memory.fill(0xad, a.output, a.output + 48);
    engine.thug_moving_collision_local_segment(a.instance, a.segment, target);
    atEqual(target, unhex(test.local_output), label + ' local segment'); atEqual(target + 32, guard, label + ' local guard');
    atEqual(a.instance, patchInstance(test.final), label + ' final instance');
    engine.thug_collision_has_tree(a.data + test.object);
  }
  const counts = { queries: 0, hits: 0, callbacks: 0, fallback_queries: 0, callbacks_without_selected_hit: 0 };
  for (const [i, test] of fixture.cases.entries()) {
    const label = 'moving query ' + i + ' object ' + test.object;
    memory.set(patchInstance(test.instance), a.instance); memory.set(guard, a.instance + 0xd4);
    memory.set(unhex(test.segment), a.segment);
    memory.fill(0xad, a.delta, a.delta + 16); memory.fill(0xad, a.bounds, a.bounds + 32);
    memory.set(guard, a.result - 16); memory.set(patchCallback(test.initial), a.result); memory.set(guard, a.result + 80);
    memory.set(unhex(test.initial_state), a.state); memory[selection] = test.farthest;
    [Math.max(0, test.callback_mode), 0, selection].forEach((v, j) => view.setUint32(a.control + j * 4, v, true));
    const treeAt = a.data + test.object + 0x34, tree = view.getUint32(treeAt, true);
    if (test.no_tree) view.setUint32(treeAt, 0, true);
    const returned = engine.thug_moving_collision_segment(a.instance, a.segment, a.delta, a.result, a.bounds, a.state);
    view.setUint32(treeAt, tree, true);
    equal(returned, test.returned, label + ' return');
    atEqual(a.result, patchCallback(test.result), label + ' result');
    atEqual(a.result - 16, guard, label + ' prefix guard'); atEqual(a.result + 80, guard, label + ' suffix guard');
    atEqual(a.state, unhex(test.state), label + ' BSP state');
    atEqual(a.instance, patchInstance(test.instance), label + ' instance'); atEqual(a.instance + 0xd4, guard, label + ' instance guard');
    atEqual(a.segment, unhex(test.segment), label + ' input');
    atEqual(a.delta, guard, label + ' unused delta'); atEqual(a.bounds, new Uint8Array(32).fill(0xad), label + ' unused bounds');
    equal(memory[selection], test.final_farthest, label + ' selection');
    const n = view.getUint32(a.control + 4, true), expectedCallbacks = patchCallback(test.callbacks);
    equal(n * 80, expectedCallbacks.length, label + ' callback count'); atEqual(a.log, expectedCallbacks, label + ' callbacks');
    counts.queries++; counts.hits += returned; counts.callbacks += n; counts.fallback_queries += test.no_tree ? 1 : 0;
    if (n && !returned) counts.callbacks_without_selected_hit++;
  }
  atEqual(a.data, data, 'moving queries preserve geometry');
  return { result: 'pass', ...counts, constructors: fixture.helpers.length, matrix_cases: fixture.matrices.length,
    scope: 'Rigid moving collision under constructed transforms of original training geometry' };
}
