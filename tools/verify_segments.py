"""Original x86 oracle for hit selection and complete static-object queries.

The callback is test instrumentation, not game behavior: it records each hit,
optionally mutates result fields, and/or changes the original selection global.
The same fixture callback is compiled separately and installed in the production
WebAssembly module's function table, sharing its memory. Core code is unmodified.
"""
import hashlib
import json
import math
import random
import struct
import subprocess
from collections import Counter

from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
from unicorn.x86_const import (UC_X86_REG_EAX, UC_X86_REG_ECX, UC_X86_REG_EIP,
                              UC_X86_REG_ESP, UC_X86_REG_FPCW)
from specimen import ROOT, SHA256, load

out = ROOT / "local/validation/collision"
report_path = out.parent / "segments.json"
report_path.unlink(missing_ok=True)
data = (out / "training-relocated.bin").read_bytes()
geometry = json.loads((out / "geometry-fixtures.json").read_text())
layout = json.loads((out / "fixtures.json").read_text())["datasets"][0]["layout"]
vertices = (out / "vertices.bin").read_bytes()
normals = (out / "normals.bin").read_bytes()
DATA, INSTANCE, SEGMENT, DELTA = 0x1000000, 0x2000000, 0x2000100, 0x2000140
BOUNDS, HIT, RESULT, CONTROL, STATE = 0x2000180, 0x20001c0, 0x2000200, 0x2000400, 0x2000500
LOG, STACK, STOP, CALLBACK = 0x2100000, 0x3000000, 0x3f00000, 0x3f00100
SELECT, QUERY_STATE = 0x691910, 0x691968
pe = load()
cpu = Uc(UC_ARCH_X86, UC_MODE_32)
cpu.mem_map(0x400000, (pe.OPTIONAL_HEADER.SizeOfImage + 4095) & ~4095)
cpu.mem_write(0x400000, pe.get_memory_mapped_image())
for address, size in [(DATA, 0x200000), (INSTANCE, 0x200000), (STACK, 0x20000), (STOP, 4096)]:
    cpu.mem_map(address, size)
cpu.mem_write(DATA, data)
cpu.mem_write(CALLBACK, b"\xc3")
cpu.mem_write(0x67c6b8, struct.pack("<2048H", *range(2048)))
counts = Counter()
fixtures = {"addresses": {"data": DATA, "instance": INSTANCE, "segment": SEGMENT, "delta": DELTA,
                         "bounds": BOUNDS, "hit": HIT, "result": RESULT, "control": CONTROL,
                         "state": STATE, "log": LOG, "callback": CALLBACK},
            "objects": [], "copies": [], "vectors": [], "cases": []}
rng = random.Random(0x4131f0)
callback_results = []


def callback_hook(uc, address, size, context):
    pointer = struct.unpack("<I", uc.mem_read(uc.reg_read(UC_X86_REG_ESP) + 4, 4))[0]
    assert pointer == RESULT
    value = bytes(uc.mem_read(pointer, 80))
    callback_results.append(value)
    mode = struct.unpack("<I", uc.mem_read(CONTROL, 4))[0]
    if mode & 1:
        uc.mem_write(pointer, bytes(byte ^ 0x5a if i < 0x3c or i >= 0x40 else byte
                                   for i, byte in enumerate(value)))
    if mode & 2: uc.mem_write(SELECT, bytes([uc.mem_read(SELECT, 1)[0] ^ 1]))


cpu.hook_add(UC_HOOK_CODE, callback_hook, begin=CALLBACK, end=CALLBACK)


def call(address, this, args, cleanup=0):
    stack = STACK + 0x18000
    cpu.mem_write(stack, struct.pack("<" + "I" * (len(args) + 1), STOP, *args))
    cpu.reg_write(UC_X86_REG_ESP, stack)
    cpu.reg_write(UC_X86_REG_ECX, this)
    cpu.reg_write(UC_X86_REG_FPCW, 0x007f)
    cpu.emu_start(address, STOP, count=2000000)
    assert cpu.reg_read(UC_X86_REG_EIP) == STOP, hex(address)
    assert cpu.reg_read(UC_X86_REG_ESP) == stack + 4 + cleanup, hex(address)
    return cpu.reg_read(UC_X86_REG_EAX)


def f32(value): return struct.unpack("<f", struct.pack("<f", value))[0]
def bits(value): return struct.unpack("<I", struct.pack("<f", value))[0]


def initial(fraction, excluded=0, required=0, callback=-1):
    raw = bytearray((index * 17 + 3) & 255 for index in range(80))
    struct.pack_into("<8fIfHH", raw, 0, 1, 2, 3, 4, 5, 6, 7, 8, 0x12345678, fraction, excluded, required)
    struct.pack_into("<I", raw, 0x3c, CALLBACK if callback >= 0 else 0)
    return bytes(raw)


def instance(obj):
    raw = struct.pack("<5I", 0x645c18, struct.unpack_from("<I", data, obj["object"])[0],
                      0, DATA + obj["object"], obj["radii"])
    raw += data[obj["object"] + 60:obj["object"] + 64]
    cpu.mem_write(INSTANCE, raw)
    return raw


def check(kind, obj, start, end, fraction, prior, farthest=0, callback=-1,
          normal=(0, 1, 0), face=0, no_tree=False):
    callback_results.clear()
    start, end = [[f32(v) for v in point] for point in (start, end)]
    segment = struct.pack("<8f", *start, 1, *end, 1)
    delta = struct.pack("<4f", *[f32(b - a) for a, b in zip(start, end)], 0)
    bounds = struct.pack("<8f", *[min(a, b) for a, b in zip(start, end)], 1,
                         *[max(a, b) for a, b in zip(start, end)], 1)
    hit = struct.pack("<8fI", *normal, 0, *start, 0, face)
    original_instance = instance(obj)
    state = struct.pack("<3I", 0x12345678, 0xabcdef01, 0x13579bdf)
    for address, raw in [(SEGMENT, segment), (DELTA, delta), (BOUNDS, bounds), (HIT, hit),
                         (RESULT - 16, b"\xad" * 16 + prior + b"\xad" * 16),
                         (CONTROL, struct.pack("<I", max(0, callback))), (QUERY_STATE, state)]:
        cpu.mem_write(address, raw)
    cpu.mem_write(SELECT, bytes([farthest]))
    tree_at = DATA + obj["object"] + 0x34
    original_tree = bytes(cpu.mem_read(tree_at, 4))
    if no_tree: cpu.mem_write(tree_at, b"\0" * 4)
    if kind == "select":
        returned = call(0x4131f0, 0, [SEGMENT, INSTANCE, HIT, bits(fraction), RESULT])
    else:
        returned = call(0x413b50, INSTANCE, [SEGMENT, DELTA, RESULT, BOUNDS], 16) & 255
    cpu.mem_write(tree_at, original_tree)
    assert returned in (0, 1)
    assert bytes(cpu.mem_read(RESULT - 16, 16)) == b"\xad" * 16
    assert bytes(cpu.mem_read(RESULT + 80, 16)) == b"\xad" * 16
    assert bytes(cpu.mem_read(INSTANCE, 24)) == original_instance
    assert bytes(cpu.mem_read(SEGMENT, 32)) == segment
    assert bytes(cpu.mem_read(DELTA, 16)) == delta
    assert bytes(cpu.mem_read(BOUNDS, 32)) == bounds
    assert bytes(cpu.mem_read(HIT, 36)) == hit
    case = {"kind": kind, "object": obj["object"], "segment": segment.hex(), "delta": delta.hex(),
            "bounds": bounds.hex(), "initial": prior.hex(), "farthest": farthest,
            "callback_mode": callback, "no_tree": no_tree, "result": returned,
            "final": bytes(cpu.mem_read(RESULT, 80)).hex(),
            "callbacks": b"".join(callback_results).hex(), "final_farthest": cpu.mem_read(SELECT, 1)[0],
            "initial_state": state.hex(), "state": bytes(cpu.mem_read(QUERY_STATE, 12)).hex()}
    if kind == "select": case.update(hit=hit.hex(), fraction=bits(fraction))
    fixtures["cases"].append(case)
    counts[kind] += 1
    counts[kind + "_accepted"] += returned
    counts["callbacks"] += len(callback_results)
    if callback_results and not returned: counts["callbacks_without_selected_hit"] += 1
    if no_tree: counts["no_tree_queries"] += 1


# Verify copy padding, return pointer, guards, and self assignment independently.
for index in range(128):
    source = bytes(rng.randrange(256) for _ in range(80))
    destination = source if index % 2 else bytes(rng.randrange(256) for _ in range(80))
    cpu.mem_write(SEGMENT, source)
    cpu.mem_write(RESULT, destination + b"\xad" * 16)
    source_pointer = RESULT if index % 2 else SEGMENT
    assert call(0x4f8160, RESULT, [source_pointer], 4) == RESULT
    assert bytes(cpu.mem_read(RESULT + 80, 16)) == b"\xad" * 16
    fixtures["copies"].append({"source": source.hex(), "initial": destination.hex(),
                               "self": bool(index % 2), "final": bytes(cpu.mem_read(RESULT, 80)).hex()})

# Normalize inputs independently of the complete object query.
vectors = [(0, 0, 0, 1), (-0.0, 0, -0.0, -0.0), (1, 0, 0, 7), (1, 2, 3, 4)]
vectors += [tuple(rng.uniform(-10000, 10000) for _ in range(4)) for _ in range(1000)]
for vector in vectors:
    raw = struct.pack("<4f", *vector)
    cpu.mem_write(RESULT, raw + b"\xad" * 16)
    assert call(0x4023f0, RESULT, []) == RESULT
    assert bytes(cpu.mem_read(RESULT + 16, 16)) == b"\xad" * 16
    fixtures["vectors"].append({"input": raw.hex(), "output": bytes(cpu.mem_read(RESULT, 16)).hex()})

radii = DATA + layout["extra"]
for obj in geometry["objects"]:
    entry = {**obj, "radii": radii}
    if not data[obj["object"] + 10]: radii += obj["faces"]
    fixtures["objects"].append(entry)
    instance(entry)
    fields = bytearray()
    for face in range(obj["faces"]):
        flags = call(0x410bf0, INSTANCE, [face], 4)
        metadata = call(0x411750, INSTANCE, [face], 4) & 65535
        fields.extend(struct.pack("<HH", flags, metadata))
        counts["surface_flags"] += 1
        counts["surface_metadata"] += 1
    entry["surface_fields"] = fields.hex()
    if not obj["faces"]:
        check("static", entry, [0, 0, 0], [0, 1, 0], 0, initial(1))
    for face in range(obj["faces"]):
        small = data[obj["object"] + 10]
        faces_at = struct.unpack_from("<I", data, obj["object"] + 12)[0] - DATA
        indices = struct.unpack_from("<3B" if small else "<3H", data, faces_at + face * (8 if small else 10) + 4)
        corners = [struct.unpack_from("<3f", vertices, obj["vertex_start"] + index * 16) for index in indices]
        center = [sum(point[axis] for point in corners) / 3 for axis in range(3)]
        normal = struct.unpack_from("<3f", normals, obj["normal_start"] + face * 16)
        start = [center[i] + normal[i] * 32 for i in range(3)]
        end = [center[i] - normal[i] * 32 for i in range(3)]
        callback = 0 if face % 5 == 0 else -1
        farthest = face % 2
        excluded, required = ((2, 0) if face % 7 == 0 else (0, 64) if face % 7 == 1 else (0, 0))
        prior = initial(0 if farthest else 1, excluded, required, callback)
        check("static", entry, start, end, 0, prior, farthest, callback, no_tree=face % 31 == 0)
        if face == 0:
            # Reverse, zero length, far away, and callback-driven selection changes.
            for extra_start, extra_end, mode in [(end, start, 0), (start, start, 0),
                ([x + 100000 for x in start], [x + 100000 for x in end], -1), (start, end, 2)]:
                check("static", entry, extra_start, extra_end, 0, initial(1, callback=mode), callback=mode)
            for mode in (-1, 0, 1, 2, 3):
                for far in (0, 1):
                    for fraction in (0.25, 0.5, 0.75):
                        check("select", entry, start, end, fraction, initial(0.5, callback=mode),
                              far, mode, normal, face)
    if len(fixtures["objects"]) % 100 == 0:
        print(len(fixtures["objects"]), "objects tested", dict(counts), flush=True)
assert radii == DATA + layout["extra"] + struct.unpack_from("<I", data, 12)[0]
assert bytes(cpu.mem_read(DATA, len(data))) == data

# Exhaust both flag masks on each individual bit, plus NaN/tie comparisons.
entry = fixtures["objects"][0]
flags = struct.unpack_from("<H", bytes.fromhex(entry["surface_fields"]), 0)[0]
for bit in range(16):
    for excluded, required in [(1 << bit, 0), (0, 1 << bit), (1 << bit, 1 << bit)]:
        check("select", entry, [1, 2, 3], [4, 5, 6], 0.5,
              initial(0.75, excluded, required, 1), callback=1)
for farthest in (0, 1, 255):
    for fraction, previous in [(float("nan"), 0.5), (0.5, float("nan")), (0, 0), (1, 1)]:
        check("select", entry, [1, 2, 3], [4, 5, 6], fraction,
              initial(previous, callback=0), farthest, 0)

fixtures["counts"] = dict(counts)
fixture_path = out / "segment-fixtures.json"
fixture_path.write_text(json.dumps(fixtures, separators=(",", ":")))
compiler = ROOT / ".tools/wasi-sdk-34.0-arm64-macos/bin/clang"
callback_module = out / "callback-fixture.wasm"
command = [str(compiler), "--target=wasm32-unknown-unknown", "-O2", "-ffreestanding", "-fno-builtin",
           "-nostdlib", "-Wl,--no-entry,--export-all,--import-memory,--global-base=8388608",
           "-Wl,-z,stack-size=65536,--initial-memory=67108864,--max-memory=134217728",
           str(ROOT / "tools/collision_callback_fixture.c"), "-o", str(callback_module)]
subprocess.run(command, check=True)
subprocess.run(["node", str(ROOT / "tools/verify_segments_wasm.mjs"), str(out)], check=True)
report = {"result": "pass", "specimen_sha256": SHA256, "counts": dict(counts),
          "copy_cases": len(fixtures["copies"]), "normalization_cases": len(fixtures["vectors"]),
          "x87_control_word": "0x007f", "runtime_control_word_observed_in_game": False,
          "wasm_sha256": hashlib.sha256((ROOT / "local/build/thug-core.wasm").read_bytes()).hexdigest(),
          "scope": "Static object queries on training geometry; flag/metadata accessors, hit selection, copy semantics, normalization. Nonaliasing inputs. Callback is test instrumentation, not recovered gameplay.",
          "fixture_sha256": hashlib.sha256(fixture_path.read_bytes()).hexdigest(),
          "callback_build_command": command,
          "callback_sha256": hashlib.sha256(callback_module.read_bytes()).hexdigest(),
          "source_hashes": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in sorted((ROOT / "src").rglob("*")) if p.is_file()},
          "byte_matching": "not attempted"}
report_path.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({"result": "pass", "counts": dict(counts)}, indent=2))
