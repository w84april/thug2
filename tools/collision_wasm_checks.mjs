// The exact same checks run under Node and the browser, against x86 fixtures.
export async function verifyCollision(wasm, fixture, loadBinary) {
  function equal(actual, expected, label) {
    if (actual !== expected) throw new Error(label + ': got ' + actual + ', expected ' + expected);
  }
  function unhex(text) { return Uint8Array.from(text.match(/../g) ?? [], byte => parseInt(byte, 16)); }
  const module = await WebAssembly.compile(wasm);
  equal(WebAssembly.Module.imports(module).length, 0, 'No external runtime imports');
  const { exports: engine } = await WebAssembly.instantiate(module);
  const bytes = new Uint8Array(engine.memory.buffer);
  const view = new DataView(engine.memory.buffer);
  const addr = fixture.addresses;
  const fallback = engine.thug_collision_fallback_indices.value;
  let checked = 0, objects = 0;
  function equalMemory(pointer, expected, label) {
    for (let index = 0; index < expected.length; index++)
      equal(bytes[pointer + index], expected[index], label + ' byte ' + index);
  }
  for (const dataset of fixture.datasets) {
    const data = await loadBinary(dataset.name + '.bin');
    const relocated = await loadBinary(dataset.name + '-relocated.bin');
    const relocatedView = new DataView(relocated.buffer, relocated.byteOffset, relocated.byteLength);
    bytes.set(data, addr.data);
    const layout = dataset.layout;
    for (const offset of layout.objects) {
      const args = ['vertices', 'vertex_aux', 'faces', 'nodes', 'face_list'].map(key => addr.data + layout[key]);
      equal(engine.thug_collision_bind(addr.data + offset, 0xa5a5a5a5, ...args), 1, 'Bind object');
      equal(engine.thug_collision_has_tree(addr.data + offset), 1, 'Initialize fallback indices');
      objects++;
    }
    equalMemory(addr.data, relocated, dataset.name + ': relocated object/tree bytes');
    for (let index = 0; index < 2048; index++) equal(view.getUint16(fallback + index * 2, true), index, 'Fallback index');
    for (const test of dataset.cases) {
      const label = dataset.name + ': object ' + test.object + ', query ' + checked;
      const object = addr.data + test.object;
      const tree = relocatedView.getUint32(test.object + 0x34, true);
      view.setUint32(object + 0x34, test.no_tree ? 0 : tree, true);
      const buffer = unhex(test.buffer);
      bytes.fill(0xad, addr.output, addr.output + buffer.length);
      view.setUint32(addr.count, 0xffffffff, true);
      bytes.set(unhex(test.query), addr.query);
      test.initial_state.forEach((value, index) => view.setUint32(addr.state + index * 4, value, true));
      const result = engine.thug_collision_query(object, addr.query, addr.count, addr.output, 0x42, addr.state);
      equal(result, test.fallback ? fallback : addr.output, label + ': return buffer');
      equal(view.getUint32(addr.count, true), test.count, label + ': count');
      equalMemory(result, unhex(test.indices), label + ': ordered indices');
      equalMemory(addr.output, buffer, label + ': output writes/guard');
      test.state.forEach((value, index) => equal(view.getUint32(addr.state + index * 4, true), value, label + ': context'));
      view.setUint32(object + 0x34, tree, true);
      checked++;
    }
    equalMemory(addr.data, relocated, dataset.name + ': query must not modify geometry');
  }
  return { result: 'pass', datasets: fixture.datasets.length, objects, queries: checked,
           wasm_bytes: wasm.byteLength, runtime_imports: 0 };
}
