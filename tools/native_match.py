"""Strict i386 COFF function comparison; no instruction masking or fuzzy credit."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from specimen import ROOT, SHA256
import pefile


def sha(data):
    return hashlib.sha256(data).hexdigest()


class Coff:
    def __init__(self, data):
        self.data = data
        if len(data) < 20:
            raise ValueError('Truncated COFF header')
        machine, count, _, sym_at, sym_count, optional, _ = struct.unpack_from('<HHIIIHH', data)
        if machine != 0x14c or optional != 0 or count == 0:
            raise ValueError('Only ordinary i386 COFF objects are supported')
        if 20 + count * 40 > len(data) or sym_at + sym_count * 18 + 4 > len(data):
            raise ValueError('Truncated COFF tables')
        string_at = sym_at + sym_count * 18
        string_size = struct.unpack_from('<I', data, string_at)[0]
        if string_size < 4 or string_at + string_size > len(data):
            raise ValueError('Truncated COFF strings')
        strings = data[string_at:string_at + string_size]
        self.sections = []
        for i in range(count):
            row = struct.unpack_from('<8sIIIIIIHHI', data, 20 + i * 40)
            name, _, _, size, raw, reloc, _, nreloc, _, flags = row
            if raw + size > len(data) or reloc + nreloc * 10 > len(data):
                raise ValueError('Truncated COFF section/relocations')
            self.sections.append({'name': name.rstrip(b'\0').decode(), 'size': size,
                                  'bytes': data[raw:raw + size], 'reloc': reloc,
                                  'nreloc': nreloc, 'flags': flags})
        self.symbols = {}
        i = 0
        while i < sym_count:
            name, value, section, kind, storage, aux = struct.unpack_from('<8sIhHBB', data, sym_at + i * 18)
            if name[:4] == b'\0' * 4:
                offset = struct.unpack_from('<I', name, 4)[0]
                if not 4 <= offset < len(strings) or b'\0' not in strings[offset:]:
                    raise ValueError('Invalid COFF symbol string')
                name = strings[offset:].split(b'\0')[0]
            else:
                name = name.rstrip(b'\0')
            self.symbols[i] = {'name': name.decode(), 'value': value, 'section': section,
                               'kind': kind, 'storage': storage}
            if i + aux >= sym_count:
                raise ValueError('Truncated auxiliary symbols')
            i += 1 + aux

    def function(self, name):
        matches = [s for s in self.symbols.values() if s['name'] == name]
        if len(matches) != 1:
            raise ValueError(f'Expected one symbol for {name}, got {len(matches)}')
        symbol = matches[0]
        if symbol['kind'] != 0x20 or not 1 <= symbol['section'] <= len(self.sections) or symbol['value'] != 0:
            raise ValueError('Function must start an individual /Gy section')
        section = self.sections[symbol['section'] - 1]
        if not section['flags'] & 0x20 or not section['flags'] & 0x1000:
            raise ValueError('Function is not in a COMDAT code section')
        peers = [s for s in self.symbols.values()
                 if s['kind'] == 0x20 and s['section'] == symbol['section']]
        if len(peers) != 1:
            raise ValueError('Multiple functions in one section are unsupported')
        return section

    def relocate(self, section, address, targets):
        code = bytearray(section['bytes'])
        records = []
        occupied = set()
        for i in range(section['nreloc']):
            offset, index, kind = struct.unpack_from('<IIH', self.data, section['reloc'] + 10 * i)
            symbol = self.symbols[index]
            name = symbol['name']
            if name not in targets or kind not in (0x06, 0x14):
                raise ValueError(f'Unresolved or unsupported relocation: {name}, {kind:#x}')
            if offset + 4 > len(code) or occupied.intersection(range(offset, offset + 4)):
                raise ValueError('Invalid/overlapping relocation')
            occupied.update(range(offset, offset + 4))
            addend = struct.unpack_from('<I', code, offset)[0]
            value = targets[name] + addend
            if kind == 0x14:
                value -= address + offset + 4
            struct.pack_into('<I', code, offset, value & 0xffffffff)
            records.append({'offset': offset, 'type': 'DIR32' if kind == 6 else 'REL32',
                            'symbol': name, 'target': f'{targets[name]:08x}', 'addend': addend})
        return bytes(code), records


def compare(exe, obj, manifest):
    reference = exe.read_bytes()
    if sha(reference) != SHA256:
        raise ValueError('Wrong reference specimen')
    pe = pefile.PE(data=reference)
    if pe.FILE_HEADER.Machine != 0x14c:
        raise ValueError('Reference must be i386')
    object_bytes = obj.read_bytes()
    coff = Coff(object_bytes)
    inventory_bytes = (ROOT / 'progress/function-inventory.tsv').read_bytes()
    inventory = {}
    for line in inventory_bytes.decode().splitlines()[1:]:
        address, size, ranges = line.split('\t')
        inventory[address] = (int(size), ranges)
    targets = {k: int(v, 16) for k, v in manifest['symbols'].items()}
    results = []
    used = set()
    for f in manifest['functions']:
        address = int(f['address'], 16)
        size = f['size']
        expected_range = f'{address:08x}:{address + size - 1:08x}'
        if size <= 0 or inventory.get(f['address']) != (size, expected_range):
            raise ValueError('Trial requires the complete contiguous inventory body')
        rva = address - pe.OPTIONAL_HEADER.ImageBase
        code_section = pe.get_section_by_rva(rva)
        if code_section is None or not code_section.Characteristics & 0x20 or \
                rva + size > code_section.VirtualAddress + code_section.Misc_VirtualSize:
            raise ValueError('Original body lies outside executable code')
        span = set(range(address, address + size))
        if used.intersection(span):
            raise ValueError('Original function extents overlap')
        used.update(span)
        section = coff.function(f['symbol'])
        original = pe.get_data(rva, size)
        if len(original) != size:
            raise ValueError('Truncated original body')
        compiled, relocations = coff.relocate(section, address, targets)
        equal = compiled == original
        results.append({**f, 'compiled_size': len(compiled), 'raw_object_equal': section['bytes'] == original,
                        'relocated_equal': equal, 'relocations': relocations,
                        'reference_sha256': sha(original), 'raw_object_sha256': sha(section['bytes']),
                        'relocated_sha256': sha(compiled), 'credited_bytes': size if equal else 0,
                        'first_difference': next((i for i, (a, b) in enumerate(zip(original, compiled))
                                                  if a != b), min(len(original), len(compiled))
                                                 if len(original) != len(compiled) else None)})
    return {'reference_sha256': sha(reference), 'object_sha256': sha(object_bytes),
            'inventory_sha256': sha(inventory_bytes),
            'functions': results, 'credited_bytes': sum(f['credited_bytes'] for f in results),
            'raw_equal_bytes': sum(f['size'] for f in results if f['raw_object_equal']),
            'relocation_policy': 'Apply only declared COFF DIR32/REL32 targets; compare every resulting byte.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exe', type=Path, required=True)
    parser.add_argument('--object', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = compare(args.exe, args.object, json.loads(args.manifest.read_text()))
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(f"{report['credited_bytes']} relocated-equal bytes; {report['raw_equal_bytes']} raw-equal bytes")


if __name__ == '__main__':
    main()
