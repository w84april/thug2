"""Check both vertex accessors and face normals for the entire training collision mesh."""
import hashlib
import json
import struct
import subprocess
from collections import Counter

from unicorn import Uc, UC_ARCH_X86, UC_MODE_32
from unicorn.x86_const import (UC_X86_REG_EAX, UC_X86_REG_ECX, UC_X86_REG_EIP,
                              UC_X86_REG_ESP, UC_X86_REG_FPCW)
from specimen import ROOT, SHA256, load

out = ROOT / "local/validation/collision"
report_path = out.parent / "geometry.json"
report_path.unlink(missing_ok=True)
data = (out / "training-relocated.bin").read_bytes()
fixture = json.loads((out / "fixtures.json").read_text())
objects = fixture["datasets"][0]["layout"]["objects"]
DATA, OUTPUT, STACK, STOP = 0x1000000, 0x2000000, 0x3000000, 0x3f00000
pe = load()
cpu = Uc(UC_ARCH_X86, UC_MODE_32)
cpu.mem_map(0x400000, (pe.OPTIONAL_HEADER.SizeOfImage + 4095) & ~4095)
cpu.mem_write(0x400000, pe.get_memory_mapped_image())
for address, size in [(DATA, 0x200000), (OUTPUT, 0x10000), (STACK, 0x10000), (STOP, 4096)]:
    cpu.mem_map(address, size)
cpu.mem_write(DATA, data)
counts = Counter()
records = []
expected_vertices = bytearray()
expected_normals = bytearray()


def vector(address, object_offset, index, reverse=False):
    stack = STACK + 0x8000
    args = (index, OUTPUT) if reverse else (OUTPUT, index)
    cpu.mem_write(stack, struct.pack("<III", STOP, *args))
    cpu.mem_write(OUTPUT, b"\xad" * 32)
    cpu.reg_write(UC_X86_REG_ESP, stack)
    cpu.reg_write(UC_X86_REG_ECX, DATA + object_offset)
    cpu.reg_write(UC_X86_REG_FPCW, 0x007f)  # Direct3D default: single precision, nearest
    cpu.emu_start(address, STOP, count=10000)
    assert cpu.reg_read(UC_X86_REG_EIP) == STOP
    assert cpu.reg_read(UC_X86_REG_ESP) == stack + 12
    if not reverse: assert cpu.reg_read(UC_X86_REG_EAX) == OUTPUT
    result = bytes(cpu.mem_read(OUTPUT, 32))
    assert result[16:] == b"\xad" * 16
    return result[:16]


for offset in objects:
    vertices, faces = struct.unpack_from("<HH", data, offset + 6)
    records.append({"object": offset, "vertices": vertices, "faces": faces,
                    "vertex_start": len(expected_vertices), "normal_start": len(expected_normals)})
    for index in range(vertices):
        result = vector(0x40b230, offset, index)
        assert result == vector(0x40b2d0, offset, index, reverse=True)
        expected_vertices.extend(result)
        counts["vertex"] += 1
        counts["vertex_into"] += 1
    for index in range(faces):
        expected_normals.extend(vector(0x414d80, offset, index))
        counts["face_normal"] += 1
assert bytes(cpu.mem_read(DATA, len(data))) == data
(out / "vertices.bin").write_bytes(expected_vertices)
(out / "normals.bin").write_bytes(expected_normals)
geometry = {"data": DATA, "output": OUTPUT, "x87_control_word": "0x007f", "objects": records}
(out / "geometry-fixtures.json").write_text(json.dumps(geometry, separators=(",", ":")))
subprocess.run(["node", str(ROOT / "tools/verify_geometry_wasm.mjs"), str(out)], check=True)
wasm = ROOT / "local/build/thug-core.wasm"
report = {"result": "pass", "specimen_sha256": SHA256, "counts": dict(counts),
          "x87_control_word": "0x007f", "scope": "Nonaliasing outputs: all training collision vertices and face normals, bit-for-bit",
          "floating_point_evidence": "CreateDevice at 0x004d7cd6 passes flags 0x24/0x44 (no FPU preserve), selecting single precision",
          "runtime_control_word_observed_in_game": False,
          "wasm_sha256": hashlib.sha256(wasm.read_bytes()).hexdigest(),
          "source_hashes": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in sorted((ROOT / "src/collision").glob("geometry.*"))},
          "fixture_hashes": {name: hashlib.sha256((out / name).read_bytes()).hexdigest()
                             for name in ("geometry-fixtures.json", "vertices.bin", "normals.bin", "training-relocated.bin")},
          "byte_matching": "not attempted"}
report_path.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({"result": "pass", "counts": dict(counts)}, indent=2))
