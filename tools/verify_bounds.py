"""Check three recovered bounds helpers against x86, including actual TR boxes."""
import ctypes
import hashlib
import itertools
import json
import random
import struct
import subprocess
from collections import Counter

from unicorn import Uc, UC_ARCH_X86, UC_MODE_32
from unicorn.x86_const import (UC_X86_REG_EAX, UC_X86_REG_ECX, UC_X86_REG_EIP,
                              UC_X86_REG_ESP, UC_X86_REG_FPCW)
from specimen import ROOT, SHA256, load

report_path = ROOT / "local/validation/bounds.json"
report_path.parent.mkdir(parents=True, exist_ok=True)
report_path.unlink(missing_ok=True)
library = report_path.with_suffix(".dylib")
subprocess.run(["clang", "-std=c99", "-O2", "-Wall", "-Wextra", "-Werror",
                "-dynamiclib", str(ROOT / "src/core/bounds.c"), "-o", str(library)], check=True)
native = ctypes.CDLL(str(library))
native.thug_bounds_reset.argtypes = [ctypes.c_void_p]
native.thug_bounds_reset.restype = None
native.thug_bounds_expand.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
native.thug_bounds_expand.restype = None
native.thug_bounds_count_containing_axes.argtypes = [ctypes.c_void_p] * 3
native.thug_bounds_count_containing_axes.restype = ctypes.c_int32
pe = load()
cpu = Uc(UC_ARCH_X86, UC_MODE_32)
cpu.mem_map(0x400000, (pe.OPTIONAL_HEADER.SizeOfImage + 4095) & ~4095)
cpu.mem_write(0x400000, pe.get_memory_mapped_image())
STACK, BOX, POINT, MASK, STOP = 0x10000000, 0x20000000, 0x20001000, 0x20002000, 0x30000000
for address in (STACK, BOX, POINT, MASK, STOP): cpu.mem_map(address, 0x1000)
counts = Counter()


def original(address, args, bounds, point):
    cpu.mem_write(BOX, bounds)
    cpu.mem_write(POINT, point)
    cpu.mem_write(MASK, b"\xff" * 4)
    stack = STACK + 0x800
    cpu.mem_write(stack, struct.pack("<" + "I" * (len(args) + 1), STOP, *args))
    cpu.reg_write(UC_X86_REG_ECX, BOX)
    cpu.reg_write(UC_X86_REG_ESP, stack)
    cpu.reg_write(UC_X86_REG_FPCW, 0x037f)
    cpu.emu_start(address, STOP, count=10000)
    assert cpu.reg_read(UC_X86_REG_EIP) == STOP
    assert cpu.reg_read(UC_X86_REG_ESP) == stack + 4 * (len(args) + 1)
    return bytes(cpu.mem_read(BOX, 32)), cpu.reg_read(UC_X86_REG_EAX), bytes(cpu.mem_read(MASK, 4))


def compare(bounds, point):
    box = ctypes.create_string_buffer(bounds, 32)
    vector = ctypes.create_string_buffer(point, 16)
    native.thug_bounds_expand(box, vector)
    expected, _, _ = original(0x403450, [POINT], bounds, point)
    assert box.raw == expected, ("expand", bounds.hex(), point.hex(), box.raw.hex(), expected.hex())
    counts["expand"] += 1
    box = ctypes.create_string_buffer(bounds, 32)
    mask = ctypes.c_uint32(0xffffffff)
    count = native.thug_bounds_count_containing_axes(box, vector, ctypes.byref(mask))
    expected, eax, expected_mask = original(0x4034d0, [POINT, MASK], bounds, point)
    assert expected == bounds == box.raw
    assert count == eax and struct.pack("<I", mask.value) == expected_mask
    counts["count_containing_axes"] += 1


rng = random.Random(0x424f554e4453)
box = ctypes.create_string_buffer(rng.randbytes(32), 32)
native.thug_bounds_reset(box)
expected, _, _ = original(0x4033e0, [], rng.randbytes(32), bytes(16))
assert box.raw == expected
counts["reset"] += 1
# Raw bit patterns retain signed zero and NaN payloads through comparisons.
special = [0, 0x80000000, 0x3f800000, 0xbf800000, 1, 0x80000001,
           0x7f7fffff, 0xff7fffff, 0x7f800000, 0xff800000,
           0x7fc01234, 0xffc01234, 0x7f801234]
for lower, upper, point in itertools.product(special, repeat=3):
    compare(struct.pack("<8I", lower, lower, lower, 0xa5a5a5a5,
                        upper, upper, upper, 0x5a5a5a5a),
            struct.pack("<4I", point, point, point, 0xffffffff))
for _ in range(1024): compare(rng.randbytes(32), rng.randbytes(16))

collision = ROOT / "local/game-files/Game/Data/levels/TR/TR.col.xbx"
data = collision.read_bytes()
version, objects = struct.unpack_from("<II", data)
assert version == 10 and 32 + objects * 64 <= len(data)
# Object stride and bounds offset are from the collision loader at 0x0049cbb0.
for index in range(objects):
    bounds = data[32 + index * 64 + 16:32 + index * 64 + 48]
    values = struct.unpack("<8f", bounds)
    center = [(values[axis] + values[axis + 4]) * 0.5 for axis in range(3)]
    points = [bounds[:16], bounds[16:], struct.pack("<4f", *center, 1)]
    for axis in range(3):
        for limit, delta in [(values[axis], -1), (values[axis + 4], 1)]:
            point = list(center)
            point[axis] = limit + delta
            points.append(struct.pack("<4f", *point, 1))
    for point in points: compare(bounds, point)

report = {"specimen_sha256": SHA256, "result": "pass", "counts": dict(counts),
          "total_comparisons": sum(counts.values()), "training_collision_objects": objects,
          "collision_sha256": hashlib.sha256(data).hexdigest(),
          "scope": "Bounds memory, axis mask/count, stack cleanup; FPU exception flags not compared",
          "byte_matching": "not attempted",
          "source_hashes": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                            for name in ("src/core/bounds.c", "src/core/bounds.h")}}
report_path.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
