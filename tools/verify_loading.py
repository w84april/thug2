"""Original loader -> grid builder -> scene-query oracle for extracted collision data.

Only heap allocation, release and heap-context calls are instrumented. Original
loader, constructors, relocation, bounds, grid population and queries execute.
"""
import hashlib
import json
import random
import struct
import subprocess
from collections import Counter

from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_ECX, UC_X86_REG_EIP, UC_X86_REG_ESP, UC_X86_REG_FPCW
from specimen import ROOT, SHA256, load

out = ROOT / "local/validation/collision"
report_path = out.parent / "loading.json"
report_path.unlink(missing_ok=True)
DATA, GRID, SCENE, NODES = 0x1000000, 0x1200000, 0x1400000, 0x1402000
SEGMENT, BOUNDS, RESULT = 0x2000100, 0x2000180, 0x2000200
OUTPUT, SERVICES, CONTEXT, EVENTS = 0x2000600, 0x2000700, 0x2000800, 0x2001000
MANAGER, HEAP, LIMIT = 0x2200000, 0x2400000, 0x2600000
STACK, STOP = 0x3000000, 0x3f00000
pe = load()
cpu = Uc(UC_ARCH_X86, UC_MODE_32)
cpu.mem_map(0x400000, (pe.OPTIONAL_HEADER.SizeOfImage + 4095) & ~4095)
cpu.mem_write(0x400000, pe.get_memory_mapped_image())
for at, size in [(0, 4096), (DATA, 0x500000), (0x2000000, 0x600000), (STACK, 0x20000), (STOP, 4096)]: cpu.mem_map(at, size)
cpu.mem_write(0x7cc979, b"\1")
cpu.mem_write(0x7d1800, struct.pack("<I", MANAGER))
cpu.mem_write(MANAGER + 0x110, struct.pack("<I", MANAGER + 0x200))
events = []
cursor = HEAP
scope = 0


def word(at): return struct.unpack("<I", cpu.mem_read(at, 4))[0]


def memory_hook(uc, address, size, context):
    global cursor, scope
    sp = uc.reg_read(UC_X86_REG_ESP)
    cleanup = 0
    result = 0
    if address in (0x5bbae0, 0x5bafc0):
        requested = word(sp + 4)
        route = int(address == 0x5bafc0)
        if route:
            assert word(sp + 8) == 1 and word(sp + 12) == 0
            cleanup = 12
        result = (cursor + 31) & ~15
        assert result + requested + 16 <= LIMIT
        cursor = result + requested + 16
        uc.mem_write(result, b"\xa5" * requested)
        events.append([1, requested, route, result])
    elif address == 0x5baba0:
        events.append([2, word(sp + 4), 0, 0]); cleanup = 4
    elif address == 0x5bb0e0:
        assert word(sp + 4) == MANAGER + 0x200
        scope = 1; events.append([3, 1, 0, 0]); cleanup = 4
    elif address == 0x5bb110:
        scope = 0; events.append([3, 0, 0, 0])
    else: raise AssertionError(hex(address))
    uc.reg_write(UC_X86_REG_EAX, result)
    uc.reg_write(UC_X86_REG_ESP, sp + 4 + cleanup)
    uc.reg_write(UC_X86_REG_EIP, word(sp))


for at in (0x5bbae0, 0x5bafc0, 0x5baba0, 0x5bb0e0, 0x5bb110):
    cpu.hook_add(UC_HOOK_CODE, memory_hook, begin=at, end=at)


def call(address, this, args=(), cleanup=0):
    stack = STACK + 0x18000
    cpu.mem_write(stack, struct.pack("<" + "I" * (len(args) + 1), STOP, *args))
    cpu.reg_write(UC_X86_REG_ESP, stack)
    cpu.reg_write(UC_X86_REG_ECX, this)
    cpu.reg_write(UC_X86_REG_FPCW, 0x007f)
    cpu.emu_start(address, STOP, count=10000000)
    assert cpu.reg_read(UC_X86_REG_EIP) == STOP, hex(address)
    assert cpu.reg_read(UC_X86_REG_ESP) == stack + 4 + cleanup, hex(address)
    return cpu.reg_read(UC_X86_REG_EAX)


def save(name, bytes_):
    (out / name).write_bytes(bytes(bytes_))
    return name


raw = (ROOT / "local/game-files/Game/Data/levels/TR/TR.col.xbx").read_bytes()
geometry = json.loads((out / "geometry-fixtures.json").read_text())
vertices, normals = [(out / f).read_bytes() for f in ("vertices.bin", "normals.bin")]
reset_bounds = struct.pack("<8f", 1e7, 1e7, 1e7, 1, -1e7, -1e7, -1e7, 1)
wide_bounds = struct.pack("<8f", -1e6, -1e6, -1e6, 7, 1e6, 1e6, 1e6, 9)
zero_file = struct.pack("<9I", 10, 0, 0, 0, 0, 0, 0, 0, 0)
empty_file = bytearray(108)
struct.pack_into("<8I", empty_file, 0, 10, 1, 0, 0, 0, 0, 0, 0)
struct.pack_into("<IHHHBBI8fIIIf", empty_file, 32, 0xabcdef01, 0, 0, 0, 1, 1, 0,
                 1e7, 1e7, 1e7, 1, -1e7, -1e7, -1e7, 1, 0, 0, 0, 1)
struct.pack_into("<3I", empty_file, 96, 8, 3, 0)
fixture = {"addresses": {"data": DATA, "grid": GRID, "scene": SCENE, "nodes": NODES,
                        "segment": SEGMENT, "bounds": BOUNDS, "result": RESULT,
                        "output": OUTPUT, "services": SERVICES, "context": CONTEXT,
                        "events": EVENTS, "heap": HEAP, "limit": LIMIT, "state": 0x2000500},
           "helpers": [], "datasets": []}
counts = Counter()

# Constructor preserves uninitialized checksum/stamp bytes; null geometry keeps checksum.
cpu.mem_write(DATA, raw)
rng = random.Random(0x412730)
for obj in geometry["objects"][::20]:
    initial = bytes(rng.randrange(256) for _ in range(24))
    cpu.mem_write(RESULT, initial + b"\xad" * 16)
    assert call(0x412730, RESULT) == RESULT
    stages = [bytes(cpu.mem_read(RESULT, 24)).hex()]
    call(0x40b370, RESULT, [DATA + obj["object"]], 4)
    stages.append(bytes(cpu.mem_read(RESULT, 24)).hex())
    radii = DATA + 0x10000
    returned = call(0x410bc0, RESULT, [radii, DATA + obj["object"]], 8)
    stages.append(bytes(cpu.mem_read(RESULT, 24)).hex())
    assert call(0x412750, RESULT) == DATA + obj["object"] + 16
    call(0x40b370, RESULT, [0], 4)
    stages.append(bytes(cpu.mem_read(RESULT, 24)).hex())
    assert bytes(cpu.mem_read(RESULT + 24, 16)) == b"\xad" * 16
    fixture["helpers"].append({"initial": initial.hex(), "object": obj["object"], "radii": radii,
                                "returned": returned, "stages": stages})

for name, data, bounds in [("training", raw, reset_bounds), ("wide", raw, wide_bounds),
                            ("zero", zero_file, reset_bounds), ("empty", bytes(empty_file), wide_bounds)]:
    cursor, scope = HEAP, 0
    events.clear()
    cpu.mem_write(HEAP, b"\xcd" * (LIMIT - HEAP))
    cpu.mem_write(DATA, data + b"\xad" * 32)
    cpu.mem_write(BOUNDS, bounds + b"\xad" * 16)
    cpu.mem_write(OUTPUT, b"\xad" * 32)
    cpu.mem_write(0x67c6b8, struct.pack("<2048H", 65535, *([0] * 2047)))
    assert call(0x49cbb0, 0xcafebabe, [DATA, OUTPUT, OUTPUT + 4, OUTPUT + 8, BOUNDS, 0x1234], 24) & 255 == 1
    assert word(0) == 0, "SEH chain not restored"
    count, instances, objects = struct.unpack("<3I", cpu.mem_read(OUTPUT, 12))
    assert count == struct.unpack_from("<I", data, 4)[0] and objects == DATA + 32
    assert bytes(cpu.mem_read(DATA + len(data), 32)) == b"\xad" * 32
    assert bytes(cpu.mem_read(BOUNDS + 32, 16)) == b"\xad" * 16
    entry = {"name": "loading-" + name, "input": save("loading-" + name + "-input.bin", data),
             "initial_bounds": bounds.hex(), "count": count, "instances": instances,
             "outputs": bytes(cpu.mem_read(OUTPUT, 32)).hex(), "bounds": bytes(cpu.mem_read(BOUNDS, 32)).hex(),
             "loaded": save("loading-" + name + "-loaded.bin", cpu.mem_read(DATA, len(data))),
             "heap_loaded": save("loading-" + name + "-heap-loaded.bin", cpu.mem_read(HEAP, cursor - HEAP)),
             "loader_cursor": cursor, "loader_events": list(events),
             "fallback": bytes(cpu.mem_read(0x67c6b8, 4096)).hex(), "queries": []}
    cpu.mem_write(GRID, b"\xad" * (0x4b30 + 32))
    for i in range(400):
        at = GRID + 48 + i * 48
        assert call(0x4183b0, at) == at
    entry["cells"] = save(entry["name"] + "-cells.bin", cpu.mem_read(GRID, 0x4b30 + 32))
    call(0x418440, GRID, [BOUNDS], 4)
    entry["grid_initialized"] = save(entry["name"] + "-grid-initialized.bin", cpu.mem_read(GRID, 0x4b30 + 32))
    call(0x418bd0, GRID, [instances, count], 8)
    assert scope == 0
    entry["grid"] = save(entry["name"] + "-grid.bin", cpu.mem_read(GRID, 0x4b30 + 32))
    entry["heap"] = save(entry["name"] + "-heap.bin", cpu.mem_read(HEAP, cursor - HEAP))
    entry["cursor"], entry["events"] = cursor, list(events)
    cell_counts = [word(GRID + 48 + i * 48 + 36) for i in range(400)]
    entry["cell_references"], entry["nonempty_cells"] = sum(cell_counts), sum(bool(n) for n in cell_counts)
    assert bytes(cpu.mem_read(DATA, len(data))) == (out / entry["loaded"]).read_bytes()
    assert bytes(cpu.mem_read(GRID + 0x4b30, 32)) == b"\xad" * 32

    # A minimal scene/list shell exercises the recovered query on this loader-built grid.
    cpu.mem_write(SCENE, b"\0" * 0xd4 + struct.pack("<I", GRID))
    cpu.mem_write(NODES, struct.pack("<8I", 0, SCENE, 0, NODES + 16, 0, 0xffffffff, 0, NODES + 16))
    cpu.mem_write(0x6fa7ec, struct.pack("<I", NODES))
    probes = []
    if count > 1:
        for obj in geometry["objects"]:
            if not obj["faces"]: continue
            offset = obj["object"]
            record = word(DATA + offset + 12)
            indices = struct.unpack("<3B" if data[offset + 10] else "<3H",
                                    cpu.mem_read(record + 4, 3 if data[offset + 10] else 6))
            points = [struct.unpack_from("<3f", vertices, obj["vertex_start"] + i * 16) for i in indices]
            center = [sum(p[a] for p in points) / 3 for a in range(3)]
            normal = struct.unpack_from("<3f", normals, obj["normal_start"])
            probes.append([[center[i] + normal[i] * distance for i in range(3)] for distance in (64, -64)])
    else: probes = [[[0, 50, 0], [0, -50, 0]], [[1e5] * 3, [1e5 + 10] * 3]]
    for index, (start, end) in enumerate(probes):
        segment = struct.pack("<8f", *start, 1, *end, 1)
        initial = bytearray(b"\xad" * 80)
        struct.pack_into("<HHI", initial, 0x28, 0, 0, 0)
        struct.pack_into("<I", initial, 0x3c, 0)
        cpu.mem_write(RESULT, bytes(initial) + b"\xad" * 16)
        cpu.mem_write(SEGMENT, segment)
        cpu.mem_write(0x691910, bytes([index & 1]))
        cpu.mem_write(0x693998, bytes([index & 255]))
        returned = call(0x4106c0, 0, [SEGMENT, RESULT, 0, 0]) & 255
        assert returned in (0, 1)
        assert bytes(cpu.mem_read(RESULT + 80, 16)) == b"\xad" * 16
        entry["queries"].append({"segment": segment.hex(), "initial": initial.hex(), "returned": returned,
                                 "result": bytes(cpu.mem_read(RESULT, 80)).hex(), "farthest": index & 1,
                                 "stamp": index & 255, "final_stamp": cpu.mem_read(0x693998, 1)[0]})
        counts["queries"] += 1; counts["query_hits"] += returned
    entry["heap_after_queries"] = save(entry["name"] + "-heap-after-queries.bin", cpu.mem_read(HEAP, cursor - HEAP))
    counts["files"] += 1; counts["instances"] += count; counts["cells"] += 400
    counts["allocations"] += sum(e[0] == 1 for e in events)
    fixture["datasets"].append(entry)
    print(name, count, "objects;", entry["cell_references"], "cell references;", len(probes), "scene queries", flush=True)

fixture_path = out / "loading-fixtures.json"
fixture_path.write_text(json.dumps(fixture, separators=(",", ":")))
compiler = ROOT / ".tools/wasi-sdk-34.0-arm64-macos/bin/clang"
command = [str(compiler), "--target=wasm32-unknown-unknown", "-O2", "-ffreestanding", "-fno-builtin", "-nostdlib",
           "-Wl,--no-entry,--export-all,--import-memory,--global-base=8388608",
           "-Wl,-z,stack-size=65536,--initial-memory=67108864,--max-memory=134217728",
           str(ROOT / "tools/memory_fixture.c"), "-o", str(out / "memory-fixture.wasm")]
subprocess.run(command, check=True)
subprocess.run(["node", str(ROOT / "tools/verify_loading_wasm.mjs"), str(out)], check=True)
report = {"result": "pass", "specimen_sha256": SHA256, "counts": dict(counts), "instance_helper_cases": len(fixture["helpers"]),
          "x87_control_word": "0x007f", "runtime_control_word_observed_in_game": False,
          "scope": "Full collision-file loading, grid initialization/population and queries on the resulting grid. Heap calls instrumented; PC memory manager, render-sector binding and full scene-load wrapper not recovered.",
          "wasm_sha256": hashlib.sha256((ROOT / "local/build/thug-core.wasm").read_bytes()).hexdigest(),
          "memory_fixture_command": command,
          "source_hashes": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in sorted((ROOT / "src").rglob("*")) if p.is_file()},
          "fixture_hashes": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.glob("loading-*")) if p.is_file()},
          "memory_fixture_sha256": hashlib.sha256((out / "memory-fixture.wasm").read_bytes()).hexdigest(),
          "byte_matching": "not attempted"}
report_path.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({"result": "pass", "counts": dict(counts)}, indent=2))
