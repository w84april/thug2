export async function verifySegments(wasm, fixture, loadBinary) {
  const { instance: { exports: engine } } = await WebAssembly.instantiate(wasm);
  const memory = new Uint8Array(engine.memory.buffer);
  const view = new DataView(engine.memory.buffer);
  const address = fixture.addresses;
  const fromHex = text => Uint8Array.from(text.match(/../g) ?? [], byte => parseInt(byte, 16));
  const data = await loadBinary('training-relocated.bin');
  memory.set(data, address.data);
  const callbackWasm = await loadBinary('callback-fixture.wasm');
  const { instance: { exports: callback } } = await WebAssembly.instantiate(callbackWasm,
    { env: { memory: engine.memory } });
  const callbackIndex = engine.__indirect_function_table.grow(1);
  engine.__indirect_function_table.set(callbackIndex, callback.record_hit);
  const selection = engine.thug_collision_select_farthest.value;
  const methods = engine.thug_static_collision_methods.value;
  const objects = new Map(fixture.objects.map(object => [object.object, object]));
  const statePointer = address.state;

  function equal(actual, expected, label) {
    for (let i = 0; i < expected.length; i++) {
      if (actual[i] !== expected[i]) throw new Error(label + ': byte ' + i + ', ' + actual[i] + ' != ' + expected[i]);
    }
  }
  function patchCallback(bytes) {
    const words = new DataView(bytes.buffer, bytes.byteOffset, bytes.length);
    for (let at = 0; at < bytes.length; at += 80) {
      if (words.getUint32(at + 0x3c, true) === address.callback)
        words.setUint32(at + 0x3c, callbackIndex, true);
    }
    return bytes;
  }
  let nanComparisons = 0;
  function resultEqual(actual, expected, label) {
    const a = new DataView(actual.buffer, actual.byteOffset, actual.byteLength);
    const b = new DataView(expected.buffer, expected.byteOffset, expected.byteLength);
    for (let at = 0; at < expected.length; at += 80) {
      for (let field = 0; field < 40; field += 4) {
        if (field === 32) continue; // face index, not floating point
        if (Number.isNaN(a.getFloat32(at + field, true)) && Number.isNaN(b.getFloat32(at + field, true))) {
          // NaN payload preservation is not a WebAssembly guarantee.
          actual = actual.slice();
          actual.set(expected.subarray(at + field, at + field + 4), at + field);
          nanComparisons++;
        }
      }
    }
    equal(actual, expected, label);
  }
  function bind(object) {
    const source = address.data + object.object;
    view.setUint32(address.instance, methods, true);
    view.setUint32(address.instance + 4, view.getUint32(source, true), true);
    view.setUint32(address.instance + 8, 0, true);
    view.setUint32(address.instance + 12, source, true);
    view.setUint32(address.instance + 16, object.radii, true);
    view.setUint32(address.instance + 20, view.getUint32(source + 60, true), true);
  }
  for (const test of fixture.copies) {
    memory.set(fromHex(test.source), address.segment);
    memory.fill(0xad, address.result, address.result + 96);
    memory.set(fromHex(test.initial), address.result);
    const result = engine.thug_collision_result_copy(address.result, test.self ? address.result : address.segment);
    if (result !== address.result) throw new Error('Result copy return pointer');
    equal(memory.subarray(address.result, address.result + 80), fromHex(test.final), 'Result copy');
    equal(memory.subarray(address.result + 80, address.result + 96), new Uint8Array(16).fill(0xad), 'Copy guard');
  }
  for (const test of fixture.vectors) {
    memory.fill(0xad, address.result, address.result + 32);
    memory.set(fromHex(test.input), address.result);
    if (engine.thug_vector_normalize(address.result) !== address.result) throw new Error('Normalize return pointer');
    equal(memory.subarray(address.result, address.result + 16), fromHex(test.output), 'Normalization');
    equal(memory.subarray(address.result + 16, address.result + 32), new Uint8Array(16).fill(0xad), 'Normalize guard');
  }
  let faces = 0;
  for (const object of fixture.objects) {
    bind(object);
    engine.thug_collision_has_tree(address.data + object.object);
    const fields = fromHex(object.surface_fields);
    const fieldView = new DataView(fields.buffer);
    for (let face = 0; face < object.faces; face++) {
      if (engine.thug_collision_surface_flags(address.instance, face) !== fieldView.getUint16(face * 4, true))
        throw new Error('Surface flags ' + object.object + '/' + face);
      if (engine.thug_collision_surface_metadata(address.instance, face) !== fieldView.getUint16(face * 4 + 2, true))
        throw new Error('Surface metadata ' + object.object + '/' + face);
      faces++;
    }
  }
  let selects = 0, statics = 0, callbacks = 0;
  for (let index = 0; index < fixture.cases.length; index++) {
    const test = fixture.cases[index];
    const object = objects.get(test.object);
    bind(object);
    const instance = memory.slice(address.instance, address.instance + 24);
    const inputs = [[address.segment, fromHex(test.segment)], [address.delta, fromHex(test.delta)],
                    [address.bounds, fromHex(test.bounds)]];
    if (test.hit) inputs.push([address.hit, fromHex(test.hit)]);
    for (const [at, bytes] of inputs) memory.set(bytes, at);
    memory.fill(0xad, address.result - 16, address.result + 96);
    memory.set(patchCallback(fromHex(test.initial)), address.result);
    memory.set(fromHex(test.initial_state), statePointer);
    memory[selection] = test.farthest;
    view.setUint32(address.control, Math.max(0, test.callback_mode), true);
    view.setUint32(address.control + 4, 0, true);
    view.setUint32(address.control + 8, selection, true);
    const treeAt = address.data + object.object + 0x34;
    const tree = view.getUint32(treeAt, true);
    if (test.no_tree) view.setUint32(treeAt, 0, true);
    let result;
    if (test.kind === 'select') {
      view.setUint32(address.delta + 12, test.fraction, true);
      const fraction = view.getFloat32(address.delta + 12, true);
      memory.set(inputs[1][1], address.delta);
      result = engine.thug_collision_select_hit(address.segment, address.instance, address.hit, fraction, address.result);
      selects++;
    } else {
      result = engine.thug_static_collision_segment(address.instance, address.segment, address.delta,
        address.result, address.bounds, statePointer);
      statics++;
    }
    view.setUint32(treeAt, tree, true);
    const label = test.kind + ' case ' + index + ' object ' + test.object;
    if (result !== test.result) throw new Error(label + ': return value ' + result + ' != ' + test.result);
    resultEqual(memory.subarray(address.result, address.result + 80), patchCallback(fromHex(test.final)), label);
    equal(memory.subarray(address.result - 16, address.result), new Uint8Array(16).fill(0xad), label + ' prefix guard');
    equal(memory.subarray(address.result + 80, address.result + 96), new Uint8Array(16).fill(0xad), label + ' suffix guard');
    const count = view.getUint32(address.control + 4, true);
    const expectedCallbacks = patchCallback(fromHex(test.callbacks));
    if (count * 80 !== expectedCallbacks.length) throw new Error(label + ': callback count');
    resultEqual(memory.subarray(address.log, address.log + count * 80), expectedCallbacks, label + ' callbacks');
    if (memory[selection] !== test.final_farthest) throw new Error(label + ': selection global');
    equal(memory.subarray(statePointer, statePointer + 12), fromHex(test.state), label + ' query state');
    equal(memory.subarray(address.instance, address.instance + 24), instance, label + ' instance modified');
    for (const [at, bytes] of inputs) equal(memory.subarray(at, at + bytes.length), bytes, label + ' input modified');
    callbacks += count;
  }
  equal(memory.subarray(address.data, address.data + data.length), data, 'Collision data modified');
  return { result: 'pass', static_queries: statics, hit_selections: selects, callbacks,
           surface_faces: faces, copies: fixture.copies.length, normalizations: fixture.vectors.length,
           nan_fields_classification_only: nanComparisons };
}
