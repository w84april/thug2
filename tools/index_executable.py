"""Recover native QB bindings and compiler metadata from the pinned specimen."""
import json
import re
import struct
from collections import defaultdict
from specimen import ROOT, EXE, SHA256, load

pe = load()
base = pe.OPTIONAL_HEADER.ImageBase
count_code = pe.get_data(0x5a5660 - base, 6)
assert count_code[0] == 0xb8 and count_code[5] == 0xc3
count = struct.unpack_from("<I", count_code, 1)[0]
assert count == 1254
bindings, by_address = [], defaultdict(list)
for index in range(count):
    pointer, address = struct.unpack("<II", pe.get_data(0x67f3a0 - base + index * 8, 8))
    name = pe.get_string_at_rva(pointer - base).decode("ascii")
    assert re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", name), name
    assert 0x401000 <= address < 0x645000, hex(address)
    bindings.append({"name": name, "address": f"{address:08x}",
                     "name_address": f"{pointer:08x}", "table_index": index})
    by_address[address].append(name)
out = ROOT / "local/analysis"
out.mkdir(parents=True, exist_ok=True)
(out / "script-bindings.json").write_text(json.dumps(bindings, indent=2) + "\n")
names = {address: "Script_" + (aliases[0] if len(aliases) < 6 else "SharedStub")
         for address, aliases in by_address.items()}
names.update({0x401aa0: "thug_crc32_buffer", 0x401af0: "thug_crc32_extend_buffer",
              0x401b30: "thug_crc32_normalized_buffer", 0x401b90: "thug_crc32_string",
              0x401be0: "thug_crc32_extend_string"})
(out / "symbols.tsv").write_text("".join(f"{a:08x}\t{n}\n" for a, n in sorted(names.items())))
rich = pe.RICH_HEADER.values
report = {"source": str(EXE.relative_to(ROOT)), "sha256": SHA256,
          "provenance": "User-supplied modified/unpacked build, identical copies in download and CD3. Not pristine retail.",
          "script_bindings": count, "unique_script_functions": len(by_address),
          "compiler_evidence": {"linker_version": [pe.OPTIONAL_HEADER.MajorLinkerVersion,
                                                   pe.OPTIONAL_HEADER.MinorLinkerVersion],
             "rich_records": [{"tool_id": v >> 16, "build": v & 65535, "count": n}
                              for v, n in zip(rich[::2], rich[1::2])]},
          "imports": {e.dll.decode(): [i.name.decode() if i.name else f"ordinal_{i.ordinal}"
                                       for i in e.imports] for e in pe.DIRECTORY_ENTRY_IMPORT}}
(out / "specimen.json").write_text(json.dumps(report, indent=2) + "\n")
print(f"Recovered {count} bindings for {len(by_address)} functions; wrote {out}")
