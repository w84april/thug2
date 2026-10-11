"""Compare recovered segment/triangle tests with 0x0040b420 on the training mesh.

Fixture construction is host test tooling, not recovered engine behavior.
Nonaliasing inputs/outputs; single-precision x87 mode inferred from CreateDevice.
Finite outputs compare bit for bit; NaN payloads compare by classification only.
"""
import hashlib
import json
import math
import random
import struct
import subprocess
from collections import Counter

from unicorn import Uc, UC_ARCH_X86, UC_MODE_32
from unicorn.x86_const import (UC_X86_REG_EAX, UC_X86_REG_ESI, UC_X86_REG_EIP,
                              UC_X86_REG_ESP, UC_X86_REG_FPCW)
from specimen import ROOT, SHA256, load

out = ROOT / "local/validation/collision"
report_path = out.parent / "triangles.json"
report_path.unlink(missing_ok=True)
data = (out / "training-relocated.bin").read_bytes()
vertices = (out / "vertices.bin").read_bytes()
normals = (out / "normals.bin").read_bytes()
geometry = json.loads((out / "geometry-fixtures.json").read_text())
INPUT, OUTPUT, STACK, STOP = 0x1000000, 0x2000000, 0x3000000, 0x3f00000
pe = load()
cpu = Uc(UC_ARCH_X86, UC_MODE_32)
cpu.mem_map(0x400000, (pe.OPTIONAL_HEADER.SizeOfImage + 4095) & ~4095)
cpu.mem_write(0x400000, pe.get_memory_mapped_image())
for address, size in [(INPUT, 4096), (OUTPUT, 4096), (STACK, 0x10000), (STOP, 4096)]:
    cpu.mem_map(address, size)
stack = STACK + 0x8000
arguments = struct.pack("<7I", STOP, INPUT, INPUT + 16, INPUT + 32,
                        INPUT + 48, INPUT + 64, OUTPUT)
records = bytearray()
counts, outcomes = Counter(), Counter()


def check(label, origin, delta, a, b, c):
    raw = b"".join(struct.pack("<4f", *vector, 0.0) for vector in (origin, delta, a, b, c))
    cpu.mem_write(INPUT, raw)
    cpu.mem_write(OUTPUT, b"\xad" * 16)
    cpu.mem_write(stack, arguments)
    cpu.reg_write(UC_X86_REG_ESP, stack)
    cpu.reg_write(UC_X86_REG_ESI, 0x12345678)
    cpu.reg_write(UC_X86_REG_FPCW, 0x007f)
    cpu.emu_start(0x40b420, STOP, count=1000)
    assert cpu.reg_read(UC_X86_REG_EIP) == STOP
    assert cpu.reg_read(UC_X86_REG_ESP) == stack + 4
    assert cpu.reg_read(UC_X86_REG_ESI) == 0x12345678
    result = cpu.reg_read(UC_X86_REG_EAX) & 255
    assert result in (0, 1)
    output = bytes(cpu.mem_read(OUTPUT, 16))
    assert output[4:] == b"\xad" * 12
    assert bytes(cpu.mem_read(INPUT, 80)) == raw
    records.extend(raw + struct.pack("<I", result) + output[:4])
    counts[label] += 1
    outcomes["hits" if result else "misses"] += 1
    if output[:4] != b"\xad" * 4: outcomes["fraction_writes"] += 1
    if math.isnan(struct.unpack("<f", output[:4])[0]): outcomes["nan_outputs"] += 1


face_count = 0
for obj in geometry["objects"]:
    offset = obj["object"]
    small = data[offset + 10]
    faces = struct.unpack_from("<I", data, offset + 12)[0] - geometry["data"]
    for face in range(obj["faces"]):
        indices = struct.unpack_from("<3B" if small else "<3H", data,
                                     faces + face * (8 if small else 10) + 4)
        a, b, c = [struct.unpack_from("<3f", vertices, obj["vertex_start"] + index * 16)
                   for index in indices]
        normal = struct.unpack_from("<3f", normals, obj["normal_start"] + face * 16)
        center = [(a[i] + b[i] + c[i]) / 3 for i in range(3)]
        # Cross the face in each direction, include endpoints and beyond-segment misses.
        for label, distance, length in [("front", 32, -64), ("back", -32, 64),
                                         ("start", 0, -64), ("end", 32, -32),
                                         ("too_short", 32, -16), ("behind", -32, -64)]:
            check(label, [center[i] + normal[i] * distance for i in range(3)],
                  [normal[i] * length for i in range(3)], a, b, c)
        # Points beyond either barycentric edge, with a segment through the plane.
        for label, weights in [("outside_u", (-1, 2, 0)), ("outside_v", (-1, 0, 2))]:
            point = [weights[0] * a[i] + weights[1] * b[i] + weights[2] * c[i]
                     for i in range(3)]
            check(label, [point[i] + normal[i] * 32 for i in range(3)],
                  [normal[i] * -64 for i in range(3)], a, b, c)
        face_count += 1

# Determinant cutoff, relaxed upper barycentric limit, zero-area faces and NaNs.
a, b, c = (0, 0, 0), (1, 0, 0), (0, 1, 0)
cutoff_bits = struct.unpack("<I", struct.pack("<f", 0.03))[0]
lengths = [struct.unpack("<f", struct.pack("<I", cutoff_bits + step))[0] for step in (-1, 0, 1)]
lengths += [0, 0.5, 1, -1]
for length in lengths:
    for u, v in [(0, 0), (1, 0), (0, 1), (0.5, 0.5), (-0.000001, 0.5),
                 (0.5, -0.000001), (1.000005, 0), (1.00002, 0), (0.5, 0.500005),
                 (0.5, 0.50002), (0.2, 0.3)]:
        for fraction in [-0.1, 0, 0.5, 1, 1.1]:
            check("boundary", (u, v, length * fraction), (0, 0, -length), a, b, c)
for triangle in [(a, a, a), (a, b, (2, 0, 0)), (a, c, b)]:
    check("degenerate_or_reversed", (0.2, 0.3, 1), (0, 0, -2), *triangle)
for vector_index in range(5):
    for axis in range(3):
        for special in [float("nan"), float("inf"), -float("inf")]:
            vectors = [list(v) for v in [(0.2, 0.3, 1), (0, 0, -2), a, b, c]]
            vectors[vector_index][axis] = special
            check("nonfinite", *vectors)
rng = random.Random(0x40b420)
for _ in range(5000):
    vectors = [[rng.uniform(-5000, 5000) for _ in range(3)] for _ in range(5)]
    check("random", *vectors)

(out / "triangles.bin").write_bytes(records)
fixture = {"input": INPUT, "output": OUTPUT, "count": len(records) // 88,
           "real_faces": face_count, "x87_control_word": "0x007f", "categories": dict(counts)}
(out / "triangle-fixtures.json").write_text(json.dumps(fixture, indent=2) + "\n")
subprocess.run(["node", str(ROOT / "tools/verify_triangles_wasm.mjs"), str(out)], check=True)
report = {"result": "pass", "original_function": "0x0040b420", "specimen_sha256": SHA256,
          **fixture, "outcomes": dict(outcomes),
          "scope": "Nonaliasing segment/triangle inputs; all training faces and synthetic cases. Finite output bits and untouched outputs exact; NaN classification only.",
          "runtime_control_word_observed_in_game": False,
          "wasm_sha256": hashlib.sha256((ROOT / "local/build/thug-core.wasm").read_bytes()).hexdigest(),
          "source_hashes": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in sorted((ROOT / "src/collision").glob("geometry.*"))},
          "fixture_hashes": {name: hashlib.sha256((out / name).read_bytes()).hexdigest()
                             for name in ("triangles.bin", "triangle-fixtures.json", "training-relocated.bin",
                                          "vertices.bin", "normals.bin")},
          "byte_matching": "not attempted"}
report_path.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({"result": "pass", "count": fixture["count"], "outcomes": dict(outcomes)}, indent=2))
