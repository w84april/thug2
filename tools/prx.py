"""Host-side reader for the version-3 archive records observed on these discs.

This is analysis tooling, not recovered engine source. It yields bounded payloads
without writing any archive-supplied path to disk.
"""
import struct
from dataclasses import dataclass


@dataclass
class Entry:
    name: str
    checksum: int
    size: int
    compressed: bool
    payload: bytes


def entries(data):
    if len(data) < 12:
        raise ValueError("Truncated archive header")
    size, version, count = struct.unpack_from("<III", data)
    if size != len(data) or version != 0xabcd0003:
        raise ValueError("Unexpected archive size or version")
    offset = 12
    result = []
    for _ in range(count):
        if offset + 16 > len(data):
            raise ValueError("Truncated entry header")
        size, packed, name_size, _references, checksum = struct.unpack_from("<IIHHI", data, offset)
        offset += 16
        end = offset + name_size
        if not name_size or end > len(data) or b"\0" not in data[offset:end]:
            raise ValueError("Truncated or unterminated entry name")
        name = data[offset:end].split(b"\0", 1)[0].decode("ascii")
        offset = end
        end = offset + (packed or size)
        if end > len(data):
            raise ValueError("Truncated entry payload")
        result.append(Entry(name, checksum, size, bool(packed), data[offset:end]))
        offset = (end + 3) & ~3
    if offset != len(data):
        raise ValueError("Unexpected trailing bytes")
    return result


def decoded_size(data):
    """Preflight token lengths before calling the original unchecked decoder."""
    offset = size = 0
    while offset < len(data):
        flags = data[offset]
        offset += 1
        for bit in range(8):
            if offset == len(data):
                return size
            if flags & (1 << bit):
                offset += 1
                size += 1
            else:
                if offset + 2 > len(data):
                    raise ValueError("Truncated LZSS reference")
                size += (data[offset + 1] & 15) + 3
                offset += 2
    return size
