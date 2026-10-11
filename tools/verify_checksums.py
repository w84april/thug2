"""Differential test: compiled recovered C versus the original x86 functions.

PYTHONPATH=.tools/python python3 tools/verify_checksums.py
"""
import ctypes
import hashlib
import json
import random
import struct
import subprocess
from collections import Counter
from pathlib import Path

from unicorn import Uc, UC_ARCH_X86, UC_MODE_32
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_EIP, UC_X86_REG_ESP
from specimen import ROOT, SHA256, load

pe = load()
output = ROOT / "local/validation"
output.mkdir(parents=True, exist_ok=True)
(output / "checksums.json").unlink(missing_ok=True)
library = output / "checksum.dylib"
subprocess.run(["clang", "-std=c99", "-O2", "-Wall", "-Wextra", "-Werror",
                "-dynamiclib", str(ROOT / "src/core/checksum.c"), "-o", str(library)], check=True)
native = ctypes.CDLL(str(library))
for name, args in [
    ("buffer", [ctypes.c_char_p, ctypes.c_int32]),
    ("extend_buffer", [ctypes.c_char_p, ctypes.c_int32, ctypes.c_uint32]),
    ("normalized_buffer", [ctypes.c_char_p, ctypes.c_int32]),
    ("string", [ctypes.c_char_p]),
    ("extend_string", [ctypes.c_uint32, ctypes.c_char_p]),
]:
    fn = getattr(native, "thug_crc32_" + name)
    fn.argtypes, fn.restype = args, ctypes.c_uint32

cpu = Uc(UC_ARCH_X86, UC_MODE_32)
image = pe.get_memory_mapped_image()
cpu.mem_map(0x400000, (pe.OPTIONAL_HEADER.SizeOfImage + 4095) & ~4095)
cpu.mem_write(0x400000, image)
STACK, INPUT, STOP = 0x10000000, 0x20000000, 0x30000000
for address in (STACK, INPUT, STOP): cpu.mem_map(address, 0x10000)
counts = Counter()


def compare(name, address, data, args):
    if data is not None:
        if len(data) + 1 > 0x10000: raise ValueError("Input exceeds emulated buffer")
        cpu.mem_write(INPUT, data + b"\0")
    pointer = 0 if data is None else INPUT
    x86args = [pointer if a == "pointer" else a & 0xffffffff for a in args]
    cargs = [data if a == "pointer" else a for a in args]
    stack = STACK + 0x8000
    cpu.mem_write(stack, struct.pack("<" + "I" * (1 + len(args)), STOP, *x86args))
    cpu.reg_write(UC_X86_REG_ESP, stack)
    cpu.reg_write(UC_X86_REG_EAX, 0xa5a5a5a5)
    cpu.emu_start(address, STOP, count=1000000)
    assert cpu.reg_read(UC_X86_REG_EIP) == STOP, (name, "did not return")
    assert cpu.reg_read(UC_X86_REG_ESP) == stack + 4, (name, "stack imbalance")
    expected = cpu.reg_read(UC_X86_REG_EAX)
    actual = getattr(native, "thug_crc32_" + name)(*cargs)
    assert actual == expected, (name, repr(data), args, hex(actual), hex(expected))
    counts[name] += 1


rng = random.Random(0x5448554732)
samples = [b"", b"A/Z\\file.qb", b"a\0B", bytes(range(256)), b"A" * 4096]
samples += [rng.randbytes(rng.randrange(0, 257)) for _ in range(1024)]
for data in samples:
    seed = rng.getrandbits(32)
    for length in {-1, 0, len(data)}:
        compare("buffer", 0x401aa0, data, ["pointer", length])
        compare("normalized_buffer", 0x401b30, data, ["pointer", length])
        compare("extend_buffer", 0x401af0, data, ["pointer", length, seed])
    compare("string", 0x401b90, data, ["pointer"])
    compare("extend_string", 0x401be0, data, [seed, "pointer"])
for length in [-2147483648, -1, 0, 1, 2147483647]:
    compare("buffer", 0x401aa0, None, ["pointer", length])
    compare("normalized_buffer", 0x401b30, None, ["pointer", length])
    if length <= 0: compare("extend_buffer", 0x401af0, None, ["pointer", length, 123])
compare("string", 0x401b90, None, ["pointer"])
for seed in [0, 1, 0xffffffff]: compare("extend_string", 0x401be0, None, [seed, "pointer"])

paths = [p.relative_to(ROOT / "local/game-files/Game/Data").as_posix().encode("ascii")
         for p in (ROOT / "local/game-files/Game/Data").rglob("*") if p.is_file()]
bindings = json.loads((ROOT / "local/analysis/script-bindings.json").read_text())
for text in paths + [b["name"].encode("ascii") for b in bindings]:
    compare("string", 0x401b90, text, ["pointer"])
report = {"specimen_sha256": SHA256, "oracle": "Unicorn executes the pinned specimen's x86 instructions",
          "recovered_source_sha256": hashlib.sha256((ROOT / "src/core/checksum.c").read_bytes()).hexdigest(),
          "source_hashes": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                            for name in ("src/core/checksum.c", "src/core/checksum.h", "src/core/crc_table.inc")},
          "comparisons": dict(counts), "total_comparisons": sum(counts.values()),
          "real_asset_paths": len(paths), "script_binding_names": len(bindings),
          "result": "pass", "byte_matching": "not yet attempted", "scope": "Five checksum functions only"}
(output / "checksums.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
