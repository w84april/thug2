// Shared by Node and the browser. Only allocator/virtual-table addresses differ.
export async function verifyLoading(wasm, fixture, loadBinary) {
  const { instance: { exports: engine } } = await WebAssembly.instantiate(wasm);
  const memory = new Uint8Array(engine.memory.buffer), view = new DataView(engine.memory.buffer);
  const a = fixture.addresses;
  const unhex = text => Uint8Array.from(text.match(/../g) ?? [], b => parseInt(b, 16));
  const { instance: { exports: allocator } } = await WebAssembly.instantiate(
    await loadBinary('memory-fixture.wasm'), { env: { memory: engine.memory } });
  const table = engine.__indirect_function_table;
  const first = table.grow(3);
  ['fixture_allocate', 'fixture_release', 'fixture_temp_scope'].forEach((name, i) => table.set(first + i, allocator[name]));
  [a.context, first, first + 1, first + 2].forEach((value, i) => view.setUint32(a.services + i * 4, value, true));
  const methods = engine.thug_static_collision_methods.value;
  const fallback = engine.thug_collision_fallback_indices.value;
  const guard = new Uint8Array(32).fill(0xad);
  function equal(actual, expected, label) {
    if (actual !== expected) throw new Error(label + ': ' + actual + ' != ' + expected);
  }
  function atEqual(at, expected, label) {
    for (let i = 0; i < expected.length; i++)
      if (memory[at + i] !== expected[i]) throw new Error(label + ': byte ' + i + ', ' + memory[at + i] + ' != ' + expected[i]);
  }
  function patchMethods(bytes, offset, count) {
    const v = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
    for (let i = 0; i < count; i++) v.setUint32(offset + i * 24, methods, true);
    return bytes;
  }
  function checkAllocator(cursor, events, label) {
    equal(view.getUint32(a.context, true), cursor, label + ' allocation cursor');
    equal(view.getUint32(a.context + 4, true), a.limit, label + ' allocation limit');
    equal(view.getUint32(a.context + 8, true), events.length, label + ' allocation event count');
    equal(view.getUint32(a.context + 12, true), 0, label + ' temporary scope');
    events.forEach((event, i) => event.forEach((value, j) =>
      equal(view.getUint32(a.events + i * 16 + j * 4, true), value, label + ' event ' + i + '/' + j)));
  }
  memory.set(await loadBinary(fixture.datasets[0].input), a.data);
  for (const [index, helper] of fixture.helpers.entries()) {
    const label = 'instance helper ' + index;
    memory.set(unhex(helper.initial), a.result);
    memory.set(guard, a.result + 24);
    equal(engine.thug_static_collision_initialize(a.result), a.result, label + ' constructor return');
    atEqual(a.result, patchMethods(unhex(helper.stages[0]), 0, 1), label + ' initialized');
    engine.thug_collision_set_geometry(a.result, a.data + helper.object);
    atEqual(a.result, patchMethods(unhex(helper.stages[1]), 0, 1), label + ' bound');
    equal(engine.thug_collision_bind_radii(a.result, helper.radii, a.data + helper.object), helper.returned, label + ' radius return');
    atEqual(a.result, patchMethods(unhex(helper.stages[2]), 0, 1), label + ' radii');
    equal(engine.thug_static_collision_bounds(a.result), a.data + helper.object + 16, label + ' bounds pointer');
    engine.thug_collision_set_geometry(a.result, 0);
    atEqual(a.result, patchMethods(unhex(helper.stages[3]), 0, 1), label + ' cleared');
    atEqual(a.result + 24, guard, label + ' guard');
  }
  const counts = { files: 0, instances: 0, cells: 0, allocations: 0, queries: 0, query_hits: 0 };
  for (const dataset of fixture.datasets) {
    const label = dataset.name;
    const input = await loadBinary(dataset.input), loaded = await loadBinary(dataset.loaded);
    memory.fill(0xcd, a.heap, a.limit);
    [a.heap, a.limit, 0, 0].forEach((value, i) => view.setUint32(a.context + i * 4, value, true));
    memory.set(input, a.data); memory.set(guard, a.data + input.length);
    memory.set(unhex(dataset.initial_bounds), a.bounds); memory.set(guard, a.bounds + 32);
    memory.fill(0xad, a.output, a.output + 32);
    memory.fill(0, fallback, fallback + 4096); view.setUint16(fallback, 65535, true);
    equal(engine.thug_collision_load(0xcafebabe, a.data, a.output, a.output + 4,
      a.output + 8, a.bounds, 0x1234, a.services), 1, label + ' loader return');
    atEqual(a.output, unhex(dataset.outputs), label + ' outputs');
    atEqual(a.bounds, unhex(dataset.bounds), label + ' bounds');
    atEqual(a.bounds + 32, guard, label + ' bounds guard');
    atEqual(a.data, loaded, label + ' relocated data');
    atEqual(a.data + input.length, guard, label + ' data guard');
    atEqual(fallback, unhex(dataset.fallback), label + ' fallback indices');
    const instanceOffset = dataset.instances - a.heap;
    atEqual(a.heap, patchMethods(await loadBinary(dataset.heap_loaded), instanceOffset, dataset.count), label + ' loaded heap');
    checkAllocator(dataset.loader_cursor, dataset.loader_events, label + ' loader');

    memory.fill(0xad, a.grid, a.grid + 0x4b30 + 32);
    for (let i = 0; i < 400; i++) {
      const cell = a.grid + 48 + i * 48;
      equal(engine.thug_collision_cell_initialize(cell), cell, label + ' cell constructor');
    }
    atEqual(a.grid, await loadBinary(dataset.cells), label + ' constructed cells');
    engine.thug_collision_grid_initialize(a.grid, a.bounds);
    atEqual(a.grid, await loadBinary(dataset.grid_initialized), label + ' initialized grid');
    engine.thug_collision_grid_populate(a.grid, dataset.instances, dataset.count, a.services);
    const grid = await loadBinary(dataset.grid);
    atEqual(a.grid, grid, label + ' populated grid');
    atEqual(a.heap, patchMethods(await loadBinary(dataset.heap), instanceOffset, dataset.count), label + ' populated heap');
    checkAllocator(dataset.cursor, dataset.events, label + ' grid');

    memory.fill(0, a.scene, a.scene + 0xd4); view.setUint32(a.scene + 0xd4, a.grid, true);
    [0, a.scene, 0, a.nodes + 16, 0, 0xffffffff, 0, a.nodes + 16].forEach((value, i) => view.setUint32(a.nodes + i * 4, value, true));
    view.setUint32(engine.thug_collision_scene_list.value, a.nodes, true);
    for (const [index, query] of dataset.queries.entries()) {
      const qlabel = label + ' query ' + index;
      memory.set(unhex(query.segment), a.segment);
      memory.set(unhex(query.initial), a.result); memory.set(guard, a.result + 80);
      memory[engine.thug_collision_select_farthest.value] = query.farthest;
      memory[engine.thug_collision_grid_stamp.value] = query.stamp;
      const returned = engine.thug_collision_scene_segment(a.segment, a.result, 0, 0, a.state);
      equal(returned, query.returned, qlabel + ' return');
      atEqual(a.result, unhex(query.result), qlabel + ' result');
      atEqual(a.result + 80, guard, qlabel + ' guard');
      atEqual(a.segment, unhex(query.segment), qlabel + ' segment');
      equal(memory[engine.thug_collision_grid_stamp.value], query.final_stamp, qlabel + ' stamp');
      counts.queries++; counts.query_hits += returned;
    }
    atEqual(a.heap, patchMethods(await loadBinary(dataset.heap_after_queries), instanceOffset, dataset.count), label + ' final heap');
    atEqual(a.data, loaded, label + ' final data');
    atEqual(a.data + input.length, guard, label + ' final data guard');
    atEqual(a.grid, grid, label + ' final grid');
    checkAllocator(dataset.cursor, dataset.events, label + ' final allocator');
    counts.files++; counts.instances += dataset.count; counts.cells += 400;
    counts.allocations += dataset.events.filter(e => e[0] === 1).length;
  }
  return { result: 'pass', ...counts, instance_helper_cases: fixture.helpers.length,
    scope: 'Original collision-file loader and grid builder; heap services instrumented' };
}
