import subprocess
"""Original component-wait invalidation; no gameplay callbacks are stubbed."""
import hashlib,itertools,json,random,struct
from collections import Counter
from specimen import ROOT,SHA256,load
from script_heap_oracle import ScriptHeapOracle
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
from unicorn import UC_HOOK_CODE
folder=ROOT/'local/validation/collision';BASE,SIZE=0x1800000,0x20000
CONTEXT,ADAPTER,MANAGER=BASE+0x20,BASE+0x50,BASE+0x100
SCRIPTS,FRAMES,OWNER,OTHER=BASE+0x1000,BASE+0x4000,BASE+0x7000,BASE+0x7100
LOG,HEAP=BASE+0x8000,BASE+0xa000
memory=bytearray(b'\xad'*SIZE)
def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
put(CONTEXT,'<8I',HEAP,BASE+SIZE,0,LOG,BASE,BASE+SIZE,0,0)
put(ADAPTER,'<4I',CONTEXT,0,0,0)
functions={
 '0x472d20':{'name':'thug_script_clear_component_wait','this':True,'result':'void','cleanup':4},
 '0x472e70':{'name':'thug_script_clear_component_waits','this':False,'result':'void','cleanup':0}}
globals_=[['thug_script_list',0x6f3538,4]];initial=bytes(memory)
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,MANAGER,globals_,[0],functions,observe=[0x472d20,0x472e70])
ranges={0x472d20:89,0x472e70:41};hits=Counter()
def trace(cpu,at,size,user):hits[at]+=1
for at,n in ranges.items():oracle.cpu.hook_add(UC_HOOK_CODE,trace,begin=at,end=at+n-1)
labels=[]
def state(count,current=OWNER,flags=0xfedcba9f,ordinal=0):
 s=SCRIPTS+ordinal*0x100;frames=FRAMES+ordinal*0x600
 p=[patch(s,'<I',0),patch(s+0x30,'<I',count&0xffffffff),patch(s+0x94,'<I',frames),patch(s+0xa4,'<3I',flags,0x12345678,current)]
 for j in range(max(0,count)):
  p += [patch(frames+j*48+0x18,'<I',[0,OWNER,OTHER][j%3]),patch(frames+j*48+0x28,'<I',flags^(j<<8))]
 return p
def case(calls,p=(),head=0,label='component waits'):
 oracle.case(calls,p,{0:head});labels.append(label)
for count,current,owner in itertools.product([-1,0,1,2,3,7],[0,OWNER,OTHER],[0,OWNER,OTHER]):
 case([(0x472d20,SCRIPTS,[owner])]*2,state(count,current),label='signed frame count and owner identity')
for bits_ in [0,1,2,3,15,16,255,0x80000000,0xffffffff]:
 case([(0x472d20,SCRIPTS,[OWNER])],state(9,flags=bits_),label='low wait nibble and retained upper bits')
for length,owner in itertools.product([0,1,2,3],[0,OWNER,OTHER]):
 p=[]
 for j in range(length):p+=state(j+2,[0,OWNER,OTHER][j],ordinal=j)+[patch(SCRIPTS+j*0x100,'<I',SCRIPTS+(j+1)*0x100 if j+1<length else 0)]
 case([(0x472e70,0,[owner])]*2,p,SCRIPTS if length else 0,label='live script list and repeated invalidation')
# A saved-frame mask can alias the live call-depth field. The original reloads
# depth each iteration; one matching frame clears it and stops traversal.
p=state(1)+[patch(SCRIPTS+0x94,'<I',SCRIPTS+8),patch(SCRIPTS+0x20,'<I',OWNER)]
case([(0x472d20,SCRIPTS,[OWNER])],p,label='saved mask aliases live depth')
# A saved frame in the first script can modify its own next link. The list
# walker reads that link after the callee, reaching the corrected script address.
p=state(1)+state(3,ordinal=1)+[patch(SCRIPTS,'<I',SCRIPTS+0x100),patch(SCRIPTS+0x94,'<I',SCRIPTS-0x28),patch(SCRIPTS-0x10,'<I',OWNER)]
# Clearing a nibble cannot zero an aligned valid pointer; use a pointer whose
# low nibble changes to the next valid fixture script instead.
p[-3]=patch(SCRIPTS,'<I',SCRIPTS+0x108)
case([(0x472e70,0,[OWNER])],p+[patch(SCRIPTS+0x100,'<I',0)],SCRIPTS,label='saved mask mutates next pointer before traversal')
coverage={};pe=load();md=Cs(CS_ARCH_X86,CS_MODE_32)
for at,n in ranges.items():
 rows=list(md.disasm(pe.get_data(at-0x400000,n),at));missing=[hex(i.address) for i in rows if not hits[i.address]]
 coverage[hex(at)]={'total':len(rows),'covered':len(rows)-len(missing),'missing':missing}
scope='Complete00472d20 per-script and00472e70 list-wide component wait invalidation, including signed depth, masks, owner identity, repeated calls and aliased live depth/list links. Full game integration remains unfinished.'
fixture={'base':BASE,'memory':'component-waits-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope}
(folder/'component-waits-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')));(folder/fixture['memory']).write_bytes(initial)
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'counts':dict(oracle.counts),'instruction_coverage':coverage,'callee_coverage':dict(oracle.coverage),'scope':scope}
(folder.parent/'component-waits.json').write_text(json.dumps(report,indent=2)+'\n');print('Original component waits',len(labels),coverage,flush=True)

subprocess.run(['node',str(ROOT/'tools/verify_component_waits_wasm.mjs')],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [folder/'component-waits-fixtures.json',folder/fixture['memory']]}
(folder.parent/'component-waits.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS component-waits',report['cases'],sum(oracle.counts.values()))
