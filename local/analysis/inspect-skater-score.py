"""Read-only Score startup disassembly for the next recovery step, not validation."""
import csv,hashlib,json
from pathlib import Path
import pefile
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
r=Path.cwd();p=r/'local/analysis';specimen=r/'local/discs/cd3/Crack/THUG2.exe'
digest=hashlib.sha256(specimen.read_bytes()).hexdigest()
assert digest=='52fc88849654b34839ec2f96bff3a8c0b7a855df9a207aab9f2fca2e6bd440f3'
pe=pefile.PE(str(specimen));decoder=Cs(CS_ARCH_X86,CS_MODE_32)
rows={int(row['address'],16):row for row in csv.DictReader((p/'skater-score-discovery-ghidra/functions.tsv').open(),delimiter='\t')}
addresses=[0x518b60,0x518660,0x518be0,0x518c50,0x563440,0x561470,0x561730,0x561290,0x564b80]
# Ghidra omits alignment instructions from these noncontiguous bodies. Raw
# disassembly confirms their final RET at563577 and56188b respectively.
reviewed_ends={0x563440:0x563578,0x561730:0x56188c}
text=['DISCOVERY ONLY. Ghidra sizes and raw instructions require review; no routines are counted recovered.']
functions=[]
for at in addresses:
 row=rows[at];size=reviewed_ends.get(at,at+int(row['body_bytes']))-at;instructions=list(decoder.disasm(pe.get_data(at-pe.OPTIONAL_HEADER.ImageBase,size),at))
 assert instructions and instructions[-1].address+instructions[-1].size==at+size,(hex(at),'noncontiguous body or incomplete decode')
 calls=[i.op_str for i in instructions if i.mnemonic=='call']
 functions.append({'address':hex(at),'bytes':size,'ghidra_body_bytes':int(row['body_bytes']),'instructions':len(instructions),'calls':calls})
 text.append(f'\nFUNCTION {at:08x}, {size} bytes, {len(instructions)} decoded instructions')
 text.extend(f'{i.address:08x}: {i.mnemonic} {i.op_str}' for i in instructions)
(p/'skater-score-inspection.txt').write_text('\n'.join(text)+'\n')
(p/'skater-score-discovery.json').write_text(json.dumps({'specimen_sha256':digest,'scope':'Static discovery only; not original execution or recovered code.','functions':functions},indent=2)+'\n')
print(json.dumps(functions))
