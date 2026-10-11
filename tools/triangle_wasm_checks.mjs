export async function verifyTriangles(wasm, fixture, loadBinary) {
  const { instance: { exports: engine } } = await WebAssembly.instantiate(wasm);
  const memory = new Uint8Array(engine.memory.buffer);
  const view = new DataView(engine.memory.buffer);
  const records = await loadBinary('triangles.bin');
  if (records.length !== fixture.count * 88) throw new Error('Triangle fixture length');
  const expected = new DataView(records.buffer, records.byteOffset, records.byteLength);
  let hits = 0, written = 0, nanOutputs = 0;
  for (let index = 0; index < fixture.count; index++) {
    const offset = index * 88;
    const input = records.subarray(offset, offset + 80);
    memory.set(input, fixture.input);
    memory.fill(0xad, fixture.output, fixture.output + 16);
    const result = engine.thug_collision_triangle(fixture.input, fixture.input + 16,
      fixture.input + 32, fixture.input + 48, fixture.input + 64, fixture.output);
    if (result !== expected.getUint32(offset + 80, true))
      throw new Error('Triangle ' + index + ': hit flag');
    const bits = expected.getUint32(offset + 84, true);
    const nan = Number.isNaN(expected.getFloat32(offset + 84, true));
    if (nan) {
      if (!Number.isNaN(view.getFloat32(fixture.output, true)))
        throw new Error('Triangle ' + index + ': expected NaN fraction');
      nanOutputs++;
    } else if (view.getUint32(fixture.output, true) !== bits) {
      throw new Error('Triangle ' + index + ': fraction ' +
        view.getUint32(fixture.output, true).toString(16) + ' != ' + bits.toString(16));
    }
    for (let byte = 4; byte < 16; byte++) {
      if (memory[fixture.output + byte] !== 0xad) throw new Error('Triangle output guard');
    }
    for (let byte = 0; byte < 80; byte++) {
      if (memory[fixture.input + byte] !== input[byte]) throw new Error('Triangle input modified');
    }
    hits += result;
    written += bits !== 0xadadadad;
  }
  return { result: 'pass', comparisons: fixture.count, hits, fraction_writes: written,
           nan_outputs_classification_only: nanOutputs, real_faces: fixture.real_faces,
           x87_reference_control_word: fixture.x87_control_word };
}
