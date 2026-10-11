export async function verifyGeometry(wasm, fixture, loadBinary) {
  const { instance: { exports: engine } } = await WebAssembly.instantiate(wasm);
  const memory = new Uint8Array(engine.memory.buffer);
  const data = await loadBinary('training-relocated.bin');
  const vertices = await loadBinary('vertices.bin');
  const normals = await loadBinary('normals.bin');
  memory.set(data, fixture.data);
  let vertexCount = 0, normalCount = 0;
  function check(fn, args, expected, start, label, returnsPointer) {
    memory.fill(0xad, fixture.output, fixture.output + 32);
    const result = fn(...args);
    if (returnsPointer && result !== fixture.output) throw new Error(label + ': return pointer');
    for (let byte = 0; byte < 32; byte++) {
      const value = byte < 16 ? expected[start + byte] : 0xad;
      if (memory[fixture.output + byte] !== value)
        throw new Error(label + ': byte ' + byte + ', got ' + memory[fixture.output + byte] + ', expected ' + value);
    }
  }
  for (const entry of fixture.objects) {
    const object = fixture.data + entry.object;
    for (let index = 0; index < entry.vertices; index++) {
      const start = entry.vertex_start + index * 16;
      check(engine.thug_collision_vertex, [object, fixture.output, index], vertices, start,
            'vertex ' + entry.object + '/' + index, true);
      check(engine.thug_collision_vertex_into, [object, index, fixture.output], vertices, start,
            'vertex_into ' + entry.object + '/' + index, false);
      vertexCount++;
    }
    for (let index = 0; index < entry.faces; index++) {
      check(engine.thug_collision_face_normal, [object, fixture.output, index], normals,
            entry.normal_start + index * 16, 'normal ' + entry.object + '/' + index, true);
      normalCount++;
    }
  }
  for (let index = 0; index < data.length; index++) {
    if (memory[fixture.data + index] !== data[index]) throw new Error('Geometry was modified');
  }
  return { result: 'pass', vertices: vertexCount, vertex_accessors: 2, normals: normalCount,
           x87_reference_control_word: fixture.x87_control_word };
}
