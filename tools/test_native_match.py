"""Synthetic comparator controls, with optional private native-proof replay."""
import struct
import argparse
import copy
import json
import tempfile
from pathlib import Path
from native_match import Coff, ROOT, compare


def object_bytes(kind=6, offset=0, raw=b'\x04\0\0\0'):
    # One /Gy section and one long external symbol, with a section relocation.
    symbol_at = 60 + len(raw) + 10
    header = struct.pack('<HHIIIHH', 0x14c, 1, 0, symbol_at, 2, 0, 0)
    section = struct.pack('<8sIIIIIIHHI', b'.text', 0, 0, len(raw), 60,
                          60 + len(raw), 0, 1, 0, 0x1020)
    symbols = struct.pack('<8sIhHBB', b'_test', 0, 1, 0x20, 2, 0)
    symbols += struct.pack('<8sIhHBB', struct.pack('<II', 0, 4), 0, 0, 0, 2, 0)
    strings = b'long_target\0'
    return header + section + raw + struct.pack('<IIH', offset, 1, kind) + symbols + \
        struct.pack('<I', 4 + len(strings)) + strings


def rejects(call):
    try:
        call()
    except (ValueError, KeyError, struct.error):
        return
    raise AssertionError('Invalid input accepted')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exe', type=Path)
    parser.add_argument('--object', type=Path)
    args = parser.parse_args()
    if bool(args.exe) != bool(args.object):
        parser.error('--exe and --object must be supplied together')
    raw = object_bytes()
    coff = Coff(raw)
    section = coff.function('_test')
    linked, relocations = coff.relocate(section, 0x401000, {'long_target': 0x670000})
    assert linked == struct.pack('<I', 0x670004) and linked != section['bytes']
    assert relocations[0]['offset'] == 0 and relocations[0]['addend'] == 4
    assert coff.data == raw and section['bytes'] == b'\x04\0\0\0'
    relative = Coff(object_bytes(kind=0x14))
    assert relative.relocate(relative.function('_test'), 0x401000,
                             {'long_target': 0x402000})[0] == struct.pack('<I', 0x1000)
    # A real opcode difference stays different after relocation.
    changed = Coff(object_bytes(offset=1, raw=b'\x90\x04\0\0\0'))
    assert changed.relocate(changed.function('_test'), 0x401000,
                            {'long_target': 0x670000})[0][0] == 0x90
    rejects(lambda: coff.relocate(section, 0x401000, {}))
    rejects(lambda: coff.function('_missing'))
    unsupported = Coff(object_bytes(kind=7))
    rejects(lambda: unsupported.relocate(unsupported.function('_test'), 0x401000,
                                         {'long_target': 0x670000}))
    outside = Coff(object_bytes(offset=1))
    rejects(lambda: outside.relocate(outside.function('_test'), 0x401000,
                                     {'long_target': 0x670000}))
    for cut in (0, 19, 59, len(raw) - 1):
        rejects(lambda cut=cut: Coff(raw[:cut]))
    rejects(lambda: Coff(b'\x64\x86' + raw[2:]))
    print('COFF relocation, immutable raw bytes, and rejection controls pass')
    if args.exe:
        manifest = json.loads((ROOT / 'matching/manifest.json').read_text())
        baseline = compare(args.exe, args.object, manifest)
        assert baseline['credited_bytes'] == 406 and baseline['raw_equal_bytes'] == 189
        with tempfile.TemporaryDirectory(dir=ROOT / 'local/matching-trial') as folder:
            corrupt = Path(folder) / 'corrupt.obj'
            data = bytearray(args.object.read_bytes())
            native = Coff(data)
            symbol = next(s for s in native.symbols.values() if s['name'].startswith('?copy@'))
            raw_at = struct.unpack_from('<I', data, 20 + (symbol['section'] - 1) * 40 + 20)[0]
            data[raw_at] ^= 1
            corrupt.write_bytes(data)
            assert compare(args.exe, corrupt, manifest)['credited_bytes'] == 375
        wrong_target = copy.deepcopy(manifest)
        wrong_target['symbols']['?crc_table@@3QBIB'] = '0067c249'
        assert compare(args.exe, args.object, wrong_target)['credited_bytes'] == 189
        short = copy.deepcopy(manifest)
        short['functions'][0]['size'] -= 1
        rejects(lambda: compare(args.exe, args.object, short))
        duplicate = copy.deepcopy(manifest)
        duplicate['functions'].append(duplicate['functions'][0])
        rejects(lambda: compare(args.exe, args.object, duplicate))
        print('Real match replay, opcode/target corruption, truncated claim, and duplicate controls pass')


if __name__ == '__main__':
    main()
