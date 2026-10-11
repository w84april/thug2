"""Static, checksum-verified names and registry factory addresses for next stage."""
import json,struct,zlib
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
from specimen import load,SHA256
p=Path('local/analysis');keys={0xce0ca665,0x0a015e17,0x1d5b1ae6,0x07713c7b,0x5cb5cb7e,0xb87c8e43,0x735a20ba,0xf3b84da6,0x413b766d};names={}
for path in Path('local/game-files/Game/Data').rglob('*.qb'):
    data=path.read_bytes()
    for k in keys:
        offset=data.find(b'\x2b'+struct.pack('<I',k))
        if offset<0:continue
        end=data.find(b'\0',offset+5);raw=data[offset+5:end]
        if zlib.crc32(raw.lower().replace(b'/',b'\\'))^0xffffffff!=k:continue
        names.setdefault(hex(k),{'text':raw.decode('latin1'),'file':str(path),'offset':offset})
pe=load();code=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(0xe4860,1641),0x4e4860));factories={}
for i,c in enumerate(code):
    if c.mnemonic!='call' or c.op_str!='0x45f270':continue
    pushes=[j for j in code[max(0,i-6):i] if j.mnemonic=='push'][-3:]
    if len(pushes)!=3 or not all(j.op_str.startswith('0x') or j.op_str=='0' for j in pushes):continue
    initialize,factory,kind=[int(j.op_str,0) for j in pushes]
    if kind in keys:factories[hex(kind)]={'call_site':hex(c.address),'factory':hex(factory),'registration_initializer':hex(initialize)}
report={'result':'static discovery only','specimen_sha256':SHA256,'checksum_verified_qb_names':names,'registry_factories':factories,
 'scope':'Names require an exact token2b/checksum/text record plus a checksum recomputation. Factories are literal push arguments immediately before original45f270 in the registration routine4e4860. These factories and prop-specific methods are not newly recovered or executed here. The original-only descriptor inventory separately verifies the four component types.'}
(p/'prop-component-dependencies.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'names':{k:v['text'] for k,v in names.items()},'factories':factories}))
