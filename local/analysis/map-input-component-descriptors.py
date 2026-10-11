"""Read the straight-line static initializer; never execute the game binary."""
import hashlib,json,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
from capstone.x86 import X86_OP_REG,X86_OP_IMM,X86_OP_MEM
from specimen import load,SHA256

root=Path.cwd();out=root/'local/analysis';pe=load();base=pe.OPTIONAL_HEADER.ImageBase
start=0x6445b0;table=0x684c78;count=14;stride=24
decoder=Cs(CS_ARCH_X86,CS_MODE_32);decoder.detail=True
body=[]
for ins in decoder.disasm(pe.get_data(start-base,0x4000),start):
 body.append(ins)
 if ins.mnemonic=='ret':break
assert len(body)==82 and body[-1].address==0x64475c
registers={};writes={};saved=[]
for ins in body:
 ops=ins.operands
 if ins.mnemonic=='push':
  assert len(ops)==1 and ops[0].type==X86_OP_REG
  saved.append((ops[0].reg,registers.get(ops[0].reg)))
 elif ins.mnemonic=='pop':
  reg,value=saved.pop();assert ops[0].type==X86_OP_REG and reg==ops[0].reg
  registers[reg]=value
 elif ins.mnemonic=='ret':assert not saved
 elif ins.mnemonic=='xor':
  assert all(o.type==X86_OP_REG for o in ops) and ops[0].reg==ops[1].reg
  registers[ops[0].reg]=0
 elif ins.mnemonic=='or':
  assert ops[0].type==X86_OP_REG and ops[1].type==X86_OP_IMM
  registers[ops[0].reg]=(registers[ops[0].reg]|ops[1].imm)&0xffffffff
 elif ins.mnemonic=='mov':
  a,b=ops;assert a.size==b.size==4
  assert b.type in (X86_OP_REG,X86_OP_IMM)
  value=registers[b.reg] if b.type==X86_OP_REG else b.imm&0xffffffff
  assert value is not None
  if a.type==X86_OP_REG:registers[a.reg]=value
  else:
   assert a.type==X86_OP_MEM and a.mem.base==a.mem.index==a.mem.segment==0
   address=a.mem.disp;relative=address-table
   assert 0<=relative<(count+1)*stride and relative%stride in (8,12,16,20)
   assert address not in writes
   writes[address]={'value':value,'instruction':f'{ins.address:08x}'}
 else:raise AssertionError((hex(ins.address),ins.mnemonic,ins.op_str))
assert len(writes)==4*(count+1)
names={}
for file in ['input-component-names.json']:
 data=json.loads((out/file).read_text())
 for checksum,items in data.items():
  if not isinstance(items,list):continue
  for item in items:
   if isinstance(item,dict) and 'name' in item:names.setdefault(checksum,set()).add(item['name'])
rows=[]
for i in range(count+1):
 address=table+i*stride;raw=list(struct.unpack('<6I',pe.get_data(address-base,stride)))
 updated=raw[:2]+[writes[address+j]['value'] for j in (8,12,16,20)]
 assert updated[2]!=0 if i<count else updated[0]==updated[2]==0
 assert updated[3:]==[0,0,0 if i<count else 0xffffffff]
 rows.append({'index':i,'address':f'{address:08x}','name_checksum':f'{updated[0]:08x}',
  'known_names':sorted(names.get(f'{updated[0]:08x}',set())),
  'component_type':f'{updated[1]:08x}','member':f'{updated[2]:08x}',
  'receiver_offset':updated[3],'word_10':updated[4],'word_14':updated[5],
  'initializer_instructions':{f'{j:02x}':writes[address+j]['instruction'] for j in (8,12,16,20)}})
raw=pe.get_data(start-base,body[-1].address+body[-1].size-start)
report={'specimen_sha256':SHA256,'scope':'Static constant propagation through the complete straight-line initializer. Member addresses are discovery evidence, not recovered or browser-verified command implementations.',
 'initializer':f'{start:08x}','initializer_end':f'{body[-1].address:08x}',
 'initializer_sha256':hashlib.sha256(raw).hexdigest(),'instructions':len(body),
 'stores':len(writes),'entries':rows[:-1],'terminator':rows[-1],
 'unique_members':len({r['member'] for r in rows[:-1]}),
 'name_evidence':'local/analysis/input-component-names.json',
 'name_evidence_sha256':hashlib.sha256((out/'input-component-names.json').read_bytes()).hexdigest()}
(out/'input-component-descriptor-bindings.json').write_text(json.dumps(report,indent=2)+'\n')
(out/'input-component-descriptor-initializer.txt').write_text('\n'.join(f'{i.address:08x} {i.mnemonic:8} {i.op_str}' for i in body)+'\n')
print(json.dumps({'instructions':len(body),'stores':len(writes),'commands':count,'unique_members':report['unique_members'],'named':sum(bool(r['known_names']) for r in rows[:-1])}))
