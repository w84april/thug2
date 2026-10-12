"""Record the unexercised ground-event branch without excluding its instructions."""
import hashlib,json
from collections import Counter
from pathlib import Path
import capstone,pefile
p=Path('local/analysis');exe=Path('local/discs/cd3/Crack/THUG2.exe')
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(exe)=='52fc88849654b34839ec2f96bff3a8c0b7a855df9a207aab9f2fca2e6bd440f3'
pe=pefile.PE(str(exe));dis=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
code={i.address:(i.mnemonic,i.op_str) for i in dis.disasm(pe.get_data(0x52899a-pe.OPTIONAL_HEADER.ImageBase,0x26),0x52899a)}
assert code[0x5289b0]==('mov','dword ptr [esi + 0x78], 0x9b46e749')
assert code[0x5289b9]==('mov','dword ptr [esi + 0x78], 0xaf895b3f')
parent={i.address:(i.mnemonic,i.op_str) for i in dis.disasm(pe.get_data(0x52d31f-pe.OPTIONAL_HEADER.ImageBase,0x45),0x52d31f)}
assert parent[0x52d31f]==('mov','eax, dword ptr [esi + 0x78]')
assert parent[0x52d324]==('cmp','eax, 0x1d537eff') and parent[0x52d329]==('jne','0x52d364')
original=json.loads((p/'walk-grounded-original.json').read_text())
observed=original['acceleration_events'];assert len(observed)==174
for row in observed:
 assert (row['last_write'],row['event']) in [('0x5289b0',0x9b46e749),('0x5289b9',0xaf895b3f)]
missing=original['instruction_coverage']['0x52d300']['missing'];assert len(missing)==16
assert missing==[hex(a) for a in parent if 0x52d32b<=a<0x52d364]
report={'result':'pass','original_sha256':sha(p/'walk-grounded-original.json'),
 'scope':'Observed initialized finite graphs using the recovered collision methods and no probe callback. Not a proof for arbitrary virtual methods or malformed objects.',
 'observations':len(observed),'last_write_counts':dict(Counter(row['last_write'] for row in observed)),
 'required_event':'0x1d537eff','observed_events':sorted({hex(row['event']) for row in observed}),
 'missing_instructions':missing,'exclusions':{},
 'conclusion':'The preceding acceleration overwrites the event before each observed ground-branch test. Retain the complete translated branch and all 16 unexercised instructions in the denominator.'}
(p/'walk-grounded-event-evidence.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
