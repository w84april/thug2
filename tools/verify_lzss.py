"""Compare recovered archive decompression with the pinned executable's x86.

Run: PYTHONPATH=.tools/python python3 tools/verify_lzss.py
On this Mac, Unicorn needs normal host CPU detection outside the Codex sandbox.
"""
import ctypes
import hashlib
import json
import random
import struct
import subprocess
from collections import Counter

from unicorn import Uc, UC_ARCH_X86, UC_MODE_32
from unicorn.x86_const import (UC_X86_REG_EAX, UC_X86_REG_EIP, UC_X86_REG_ESP,
                              UC_X86_REG_EBX, UC_X86_REG_EBP, UC_X86_REG_ESI,
                              UC_X86_REG_EDI)
from specimen import ROOT, SHA256, load
from prx import entries, decoded_size

report_path = ROOT / "local/validation/lzss.json"
report_path.parent.mkdir(parents=True, exist_ok=True)
report_path.unlink(missing_ok=True)
library = report_path.with_suffix(".dylib")
subprocess.run(["clang", "-std=c99", "-O2", "-Wall", "-Wextra", "-Werror",
                "-dynamiclib", str(ROOT / "src/core/lzss.c"),
                str(ROOT / "src/core/checksum.c"), "-o", str(library)], check=True)
native = ctypes.CDLL(str(library))
native.thug_lzss_decode_unchecked.argtypes = [ctypes.c_void_p, ctypes.c_char_p,
                                            ctypes.c_void_p, ctypes.c_uint32]
native.thug_lzss_decode_unchecked.restype = ctypes.c_void_p
native.thug_crc32_string.argtypes = [ctypes.c_char_p]
native.thug_crc32_string.restype = ctypes.c_uint32
pe = load()
cpu = Uc(UC_ARCH_X86, UC_MODE_32)
cpu.mem_map(0x400000, (pe.OPTIONAL_HEADER.SizeOfImage + 4095) & ~4095)
cpu.mem_write(0x400000, pe.get_memory_mapped_image())
STACK, INPUT, OUTPUT, STOP = 0x10000000, 0x20000000, 0x24000000, 0x30000000
CAPACITY = 0x1000000
for address, size in [(STACK, 0x10000), (INPUT, CAPACITY),
                      (OUTPUT, CAPACITY), (STOP, 0x1000)]:
    cpu.mem_map(address, size)
rng = random.Random(0x4c5a5353)
counts = Counter()


def compare(data, size, label):
    assert decoded_size(data) == size, (label, "invalid stream size")
    assert len(data) < CAPACITY and size + 32 < CAPACITY
    initial_window = rng.randbytes(4096)
    state = ctypes.create_string_buffer(initial_window, 4096)
    destination = ctypes.create_string_buffer(b"\xcd" * (size + 32), size + 32)
    end = native.thug_lzss_decode_unchecked(state, data, destination, len(data))
    assert end - ctypes.addressof(destination) == size, (label, "native size")
    assert destination.raw[size:] == b"\xcd" * 32, (label, "native overrun")
    cpu.mem_write(0x68ff68, initial_window)
    cpu.mem_write(INPUT, data or b"\0")
    cpu.mem_write(OUTPUT, b"\xab" * (size + 32))
    stack = STACK + 0x8000
    cpu.mem_write(stack, struct.pack("<IIII", STOP, INPUT, OUTPUT, len(data)))
    cpu.reg_write(UC_X86_REG_ESP, stack)
    preserved = {register: rng.getrandbits(32) for register in
                 (UC_X86_REG_EBX, UC_X86_REG_EBP, UC_X86_REG_ESI, UC_X86_REG_EDI)}
    for register, value in preserved.items(): cpu.reg_write(register, value)
    cpu.emu_start(0x4014f0, STOP, count=size * 50 + 100000)
    assert cpu.reg_read(UC_X86_REG_EIP) == STOP, (label, "oracle did not return")
    assert cpu.reg_read(UC_X86_REG_ESP) == stack + 4, (label, "stack imbalance")
    assert cpu.reg_read(UC_X86_REG_EAX) == OUTPUT + size, (label, "oracle size")
    for register, value in preserved.items():
        assert cpu.reg_read(register) == value, (label, "callee-saved register")
    original = bytes(cpu.mem_read(OUTPUT, size + 32))
    assert original[size:] == b"\xab" * 32, (label, "oracle overrun")
    assert destination.raw[:size] == original[:size], (label, "different output")
    assert state.raw == bytes(cpu.mem_read(0x68ff68, 4096)), (label, "different state")
    counts["oracle_comparisons"] += 1
    counts["decoded_bytes_compared"] += size
    return destination.raw[:size]


def generated_stream(tokens):
    result = bytearray()
    for first in range(0, tokens, 8):
        flags = 0
        payload = bytearray()
        for bit in range(min(8, tokens - first)):
            if rng.randrange(2):
                flags |= 1 << bit
                payload.append(rng.randrange(256))
            else:
                offset = rng.randrange(4096)
                length = rng.randrange(3, 19)
                payload.extend((offset & 255, ((offset >> 4) & 240) | (length - 3)))
        result.append(flags)
        result.extend(payload)
    return bytes(result)


# Explicitly exercise initial spaces, persistent dictionary tail, overlapping
# references, ring wrap, every token length, empty input, and flag-only endings.
samples = [b"", b"\0", b"\xff", b"\x01A\xee\xff", b"\x00\xfe\xff",
           b"\xffABCDEFGH", b"\xffABCDEFGH\x00"]
samples += [bytes([0, 0xee, 0xf0 | length]) for length in range(16)]
samples += [generated_stream(rng.randrange(1, 300)) for _ in range(128)]
samples += [generated_stream(5200)]
for index, data in enumerate(samples):
    compare(data, decoded_size(data), "synthetic:" + str(index))
counts["synthetic_streams"] = len(samples)

data_root = ROOT / "local/game-files/Game/Data"
loose_files = {path.relative_to(data_root).as_posix().lower(): path
               for path in data_root.rglob("*") if path.is_file()}
archive_report = []
for archive in sorted((data_root / "pre").glob("TR*.prx")):
    raw = archive.read_bytes()
    members = []
    for entry in entries(raw):
        assert native.thug_crc32_string(entry.name.encode("ascii")) == entry.checksum
        counts["archive_name_checksums"] += 1
        if entry.compressed:
            contents = compare(entry.payload, entry.size, archive.name + ":" + entry.name)
            counts["compressed_assets"] += 1
        else:
            contents = entry.payload
            assert len(contents) == entry.size
            counts["uncompressed_assets"] += 1
        path = loose_files.get(entry.name.replace("\\", "/").lower())
        loose_match = None if path is None else contents == path.read_bytes()
        counts["loose_missing" if path is None else
               "loose_matches" if loose_match else "loose_differences"] += 1
        members.append({"name": entry.name, "size": entry.size,
                        "compressed": entry.compressed,
                        "sha256": hashlib.sha256(contents).hexdigest(),
                        "loose_file_matches": loose_match})
    archive_report.append({"name": archive.name, "sha256": hashlib.sha256(raw).hexdigest(),
                           "members": members})
    print(archive.name, len(members), "entries verified", flush=True)

report = {"specimen_sha256": SHA256, "original_function": "0x004014f0",
          "oracle": "Unicorn executes the pinned specimen's x86 instructions",
          "scope": "LZSS output, return pointer, dictionary, preserved registers; training archives",
          "adaptation": "Dictionary global is an explicit state parameter",
          "byte_matching": "not attempted", "counts": dict(counts), "result": "pass",
          "source_hashes": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                            for name in ("src/core/lzss.c", "src/core/lzss.h")},
          "archives": archive_report}
report_path.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({"result": report["result"], "counts": report["counts"]}, indent=2))
