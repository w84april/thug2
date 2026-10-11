"""Generate x86 collision oracles, then compare the recovered wasm32 build.

Requires tools/build_wasm.py first. Run with PYTHONPATH=.tools/python.
The original instructions execute in Unicorn; Node runs the same WebAssembly
module that can be instantiated by a browser, with no WASI/Windows imports.
"""
import hashlib
import json
import random
import struct
import subprocess
from collections import Counter
from pathlib import Path

from unicorn import Uc, UC_ARCH_X86, UC_MODE_32
from unicorn.x86_const import (UC_X86_REG_EAX, UC_X86_REG_EBX, UC_X86_REG_ECX,
                              UC_X86_REG_EIP, UC_X86_REG_ESP, UC_X86_REG_FPCW)
from specimen import ROOT, SHA256, load
from collision_file import layout

out = ROOT / "local/validation/collision"
out.mkdir(parents=True, exist_ok=True)
report_path = out.parent / "collision.json"
report_path.unlink(missing_ok=True)
pe = load()
cpu = Uc(UC_ARCH_X86, UC_MODE_32)
cpu.mem_map(0x400000, (pe.OPTIONAL_HEADER.SizeOfImage + 4095) & ~4095)
cpu.mem_write(0x400000, pe.get_memory_mapped_image())
DATA, OUTPUT, COUNT, QUERY, STATE = 0x1000000, 0x2000000, 0x2001000, 0x2002000, 0x2003000
STACK, STOP, FALLBACK = 0x3000000, 0x3f00000, 0x67c6b8
for address, size in [(0, 4096), (DATA, 0x200000), (OUTPUT, 0x10000),
                      (STACK, 0x10000), (STOP, 4096)]: cpu.mem_map(address, size)
counts = Counter()
rng = random.Random(0x425350)


def call(address, this, args, cleanup, until=STOP):
    stack = STACK + 0x8000
    cpu.mem_write(stack, struct.pack("<" + "I" * (len(args) + 1), STOP, *args))
    cpu.reg_write(UC_X86_REG_ESP, stack)
    cpu.reg_write(UC_X86_REG_ECX, this)
    cpu.reg_write(UC_X86_REG_FPCW, 0x007f)  # Single precision selected by Direct3D setup
    cpu.emu_start(address, until, count=2000000)
    assert cpu.reg_read(UC_X86_REG_EIP) == until, (hex(address), "did not finish")
    if until == STOP:
        assert cpu.reg_read(UC_X86_REG_ESP) == stack + 4 + cleanup
    return cpu.reg_read(UC_X86_REG_EAX)


def word(address): return struct.unpack("<I", cpu.mem_read(address, 4))[0]


def check_loader_prefix(data, spec):
    cpu.mem_write(DATA, data)
    cpu.mem_write(0x7cc979, b"\1")  # heap already initialized; stop before allocation
    call(0x49cbb0, 0, [DATA, COUNT, COUNT + 4, COUNT + 8, QUERY, 0], 0, until=0x49cc58)
    stack = cpu.reg_read(UC_X86_REG_ESP)
    assert word(COUNT) == len(spec["objects"]) and word(COUNT + 8) == DATA + 32
    for name, offset in [("vertices", 0x20), ("vertex_aux", 0x1c), ("nodes", 0x18),
                         ("face_list", 0x14), ("extra", 0x5c)]:
        assert word(stack + offset) == DATA + spec[name], name
    assert cpu.reg_read(UC_X86_REG_EBX) == DATA + spec["faces"]
    counts["loader_prefix_comparisons"] += 1


def queries(data, offset, spec):
    raw = data[offset + 16:offset + 48]
    values = struct.unpack("<8f", raw)
    lower, upper = values[:3], values[4:7]
    center = [(a + b) * 0.5 for a, b in zip(lower, upper)]
    yield raw, False
    yield struct.pack("<8f", -1e7, -1e7, -1e7, 1, 1e7, 1e7, 1e7, 1), False
    for point in [lower, upper, center]:
        yield struct.pack("<8f", *point, 1, *point, 1), False
    for _ in range(4):
        point = [rng.uniform(a - 100, b + 100) for a, b in zip(lower, upper)]
        radius = rng.choice([0, 0.1, 1, 16, 128])
        yield struct.pack("<8f", *[x - radius for x in point], 1,
                          *[x + radius for x in point], 1), False
    root = struct.unpack_from("<I", data, offset + 0x34)[0]
    split_word = struct.unpack_from("<I", data, spec["nodes"] + root)[0]
    if split_word & 3 != 3:
        axis = split_word & 3
        signed = struct.unpack("<i", struct.pack("<I", split_word))[0]
        for delta in [-0.0625, 0, 0.0625]:
            point = list(center)
            point[axis] = (signed >> 2) / 16 + delta
            yield struct.pack("<8f", *point, 1, *point, 1), False
        for component in [axis, axis + 4]:
            for nan in [0x7fc01234, 0x7f801234]:
                special = bytearray(raw)
                struct.pack_into("<I", special, component * 4, nan)
                yield bytes(special), False
    # Exercise the no-tree fast path and its untouched global state.
    yield raw, True


def synthetic(tag):
    data = bytearray(232)
    struct.pack_into("<IHHHBBI8fIIII", data, 32, 0x12345678, 0, 0, 6, 1, 1, 0,
                     -100, -100, -100, 1, 100, 100, 100, 1, 0, 0, 0, 0)
    nodes = [(0, 8 | tag), ((-32 * 64 + 1) & 0xffffffff, 24 | tag),
             (32 * 64 + 2, 40 | tag)]
    nodes += [((2 << 16) | 3, index * 2) for index in range(4)]
    for index, pair in enumerate(nodes): struct.pack_into("<II", data, 160 + index * 8, *pair)
    struct.pack_into("<8H", data, 216, 0, 2, 4, 1, 3, 5, 0, 1)
    return bytes(data), {"objects": [32], "vertices": 96, "vertex_aux": 112,
                         "faces": 128, "nodes": 160, "face_list": 216}


real_path = ROOT / "local/game-files/Game/Data/levels/TR/TR.col.xbx"
real = real_path.read_bytes()
real_layout = layout(real)
check_loader_prefix(real, real_layout)
datasets = [("training", real, real_layout)]
datasets += [("synthetic-tag-" + str(tag), *synthetic(tag)) for tag in range(4)]
fixture = {"addresses": {"data": DATA, "output": OUTPUT, "count": COUNT,
                         "query": QUERY, "state": STATE}, "datasets": []}
for name, data, spec in datasets:
    cpu.mem_write(DATA, data)
    for offset in spec["objects"]:
        args = [0xa5a5a5a5] + [DATA + spec[key] for key in
                              ("vertices", "vertex_aux", "faces", "nodes", "face_list")]
        assert call(0x4169c0, DATA + offset, args, 24) & 255 == 1
        assert call(0x414d30, DATA + offset, [], 0) & 255 == 1
        counts["object_relocations"] += 1
    assert bytes(cpu.mem_read(FALLBACK, 4096)) == struct.pack("<2048H", *range(2048))
    relocated = bytes(cpu.mem_read(DATA, len(data)))
    (out / (name + ".bin")).write_bytes(data)
    (out / (name + "-relocated.bin")).write_bytes(relocated)
    cases = []
    for offset in spec["objects"]:
        face_count = struct.unpack_from("<H", data, offset + 8)[0]
        capacity = face_count * 2 + 32
        tree = cpu.mem_read(DATA + offset + 0x34, 4)
        for query, no_tree in queries(data, offset, spec):
            cpu.mem_write(DATA + offset + 0x34, b"\0" * 4 if no_tree else bytes(tree))
            cpu.mem_write(OUTPUT, b"\xad" * capacity)
            cpu.mem_write(COUNT, b"\xff" * 4)
            cpu.mem_write(QUERY, query)
            initial_state = [0x12345678, 0xffffff19, 0xabcdef12]
            cpu.mem_write(0x691968, struct.pack("<3I", *initial_state))
            result = call(0x416320, DATA + offset, [QUERY, COUNT, OUTPUT, 0x42], 16)
            assert result in (FALLBACK, OUTPUT)
            count = word(COUNT)
            assert count <= face_count
            indices = bytes(cpu.mem_read(result, count * 2))
            buffer = bytes(cpu.mem_read(OUTPUT, capacity))
            assert buffer[-32:] == b"\xad" * 32
            state = list(struct.unpack("<3I", cpu.mem_read(0x691968, 12)))
            cases.append({"object": offset, "query": query.hex(), "no_tree": no_tree,
                          "count": count, "fallback": result == FALLBACK,
                          "indices": indices.hex(), "buffer": buffer.hex(),
                          "initial_state": initial_state, "state": state})
            counts["queries"] += 1
            counts["fallback_queries" if result == FALLBACK else "tree_queries"] += 1
        cpu.mem_write(DATA + offset + 0x34, bytes(tree))
    assert bytes(cpu.mem_read(DATA, len(data))) == relocated
    fixture["datasets"].append({"name": name, "layout": spec, "cases": cases})
    print(name, len(spec["objects"]), "objects,", len(cases), "query oracles", flush=True)

fixture_path = out / "fixtures.json"
fixture_path.write_text(json.dumps(fixture, separators=(",", ":")))
subprocess.run(["node", str(ROOT / "tools/verify_collision_wasm.mjs"), str(fixture_path)], check=True)
wasm = ROOT / "local/build/thug-core.wasm"
report = {"result": "pass", "specimen_sha256": SHA256,
          "x87_control_word": "0x007f",
          "wasm_sha256": hashlib.sha256(wasm.read_bytes()).hexdigest(),
          "counts": dict(counts), "training_layout": real_layout,
          "fixture_sha256": hashlib.sha256(fixture_path.read_bytes()).hexdigest(),
          "collision_sha256": hashlib.sha256(real).hexdigest(),
          "scope": "Full object/tree relocation; ordered query results, fallback, buffers and context; wasm32 versus original x86",
          "source_hashes": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in sorted((ROOT / "src/collision").glob("*")) if p.is_file()},
          "byte_matching": "not attempted"}
report_path.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({"result": "pass", "counts": dict(counts)}, indent=2))
