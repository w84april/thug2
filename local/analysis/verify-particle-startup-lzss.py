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

library=ROOT/'local/validation/lzss.dylib'
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


archive=ROOT/'local/game-files/Game/Data/pre/qb_scripts.prx';raw=archive.read_bytes()
entry=next(e for e in entries(raw) if e.name.lower()=='scripts\\fx\\particle_scripts.qb')
assert entry.compressed
contents=compare(entry.payload,entry.size,entry.name)
assert contents==(ROOT/'local/analysis/particle-startup-archived.qb').read_bytes()
report={'result':'pass','specimen_sha256':SHA256,'original_function':'0x4014f0','archive_sha256':hashlib.sha256(raw).hexdigest(),'member':entry.name,'decoded_sha256':hashlib.sha256(contents).hexdigest(),'decoded_bytes':len(contents),'checks':'Exact decoded bytes, dictionary, output pointer, bounded output, stack balance and preserved registers','counts':dict(counts)}
(ROOT/'local/analysis/particle-startup-lzss.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
