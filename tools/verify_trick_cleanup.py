"""Pending-trick cancellation with original concrete deleting destructors."""
import hashlib,itertools,json,random,struct,subprocess
from collections import Counter
from specimen import ROOT,SHA256,load
from script_heap_oracle import ScriptHeapOracle
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
from unicorn import UC_HOOK_CODE
folder=ROOT/'local/validation/collision';BASE,SIZE=0x1800000,0x20000
CONTEXT,ADAPTER,MANAGER,LISTS=BASE+0x20,BASE+0x50,BASE+0x100,BASE+0x800
PRIMARY,SECONDARY=BASE+0x1000,BASE+0x2000
LOG,HEAP=BASE+0x8000,BASE+0xa000
memory=bytearray(b'\xad'*SIZE)
def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
def call(at,this,*args):return (at,this,list(args))
put(CONTEXT,'<8I',HEAP,BASE+SIZE,0,LOG,BASE,BASE+SIZE,LISTS+0x24,0)
put(ADAPTER,'<4I',CONTEXT,0,0,0)
put(LISTS+0x18,'<5I',0x64be88,0xffffffff,0,LISTS+0x18,LISTS+0x18)
put(LISTS+0x2c,'<5I',0x64be8c,0xffffffff,0,LISTS+0x2c,LISTS+0x2c)
initial=bytes(memory);functions={};ranges={0x511e50:31,0x511e70:31,0x511e90:58,0x511ed0:58,0x511f60:193}
for at,name,argc,heap,result in [
 (0x511e50,'thug_trick_primary_destroy',0,False,'void'),
 (0x511e70,'thug_trick_secondary_destroy',0,False,'void'),
 (0x511e90,'thug_trick_primary_delete',1,True,'word'),
 (0x511ed0,'thug_trick_secondary_delete',1,True,'word'),
 (0x511f60,'thug_tricks_cancel',2,True,'void')]:
 functions[hex(at)]={'name':name,'this':True,'memory':heap,'result':result,'cleanup':argc*4}
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,MANAGER,[],[],functions,observe=list(ranges),event_limit=(HEAP-LOG)//48)
hits=Counter()
def trace(cpu,at,size,user):hits[at]+=1
for at,n in ranges.items():oracle.cpu.hook_add(UC_HOOK_CODE,trace,begin=at,end=at+n-1)
labels=[];fields={LISTS+0x18,LISTS+0x2c}
def ring(values,secondary=False):
 sentinel=LISTS+(0x2c if secondary else 0x18);start=SECONDARY if secondary else PRIMARY
 nodes=[start+j*0x40 for j in range(len(values))];chain=[sentinel,*nodes];table=0x64be8c if secondary else 0x64be88
 p=[patch(sentinel,'<5I',table,0xffffffff,0x12345678,nodes[0] if nodes else sentinel,nodes[-1] if nodes else sentinel)]
 for j,(at,values) in enumerate(zip(nodes,values)):
  fields.add(at);p.append(patch(at,'<11IB3x',table,j,0xabcdef00+j,chain[(j+2)%len(chain)],chain[j],*values))
 return p
def case(calls,p=(),label='trick cleanup'):
 stages=oracle.case(calls,p);labels.append(label);return stages
# Actual destructors: empty sentinel, single item, first/middle/last, flags.
for secondary in [False,True]:
 destroy,delete=(0x511e70,0x511ed0) if secondary else (0x511e50,0x511e90)
 start=SECONDARY if secondary else PRIMARY;sentinel=LISTS+(0x2c if secondary else 0x18)
 for length in [0,1,3]:
  for target in range(max(length,1)):
   node=start+target*0x40 if length else sentinel;p=ring([(7,15,9,0,0,1,0)]*length,secondary)
   case([call(destroy,node)],p,'standalone unlink')
   for flags in [0,1,2,255,256,257,0xffffffff]:case([call(delete,node,flags)],p,'concrete deleting destructor flags')
def cancel(primary,secondary,select,clear,label='mask selection and related match'):
 return case([call(0x511f60,LISTS,select,clear)]*2,ring(primary)+ring(secondary,True),label)
for select,clear in itertools.product([0,1,2,4,7,0x80000000,0xffffffff],repeat=2):
 cancel([],[],select,clear,'empty primary list')
 cancel([(7,f,9,0,0,0,0) for f in [0,1,2,3,7,0x80000000,0xffffffff]],[],select,clear)
primary=[(7,1,9,0,0,12,0)]
match=(0,0,0,7,9,12,0)
misses=[(0,0,0,7,9,12,1),(0,0,0,7,9,12,255),(0,0,0,8,9,12,0),(0,0,0,7,9,13,0),(0,0,0,7,10,12,0)]
for entries in [[],[match],*[[m] for m in misses],[match,match],[*misses,match,match],[match,*misses],misses]:
 cancel(primary,entries,1,0,'secondary gates and first matching instance only')
for n in [1,2,3,7]:
 for related in [0,12]:
  cancel([(7,1,9,0,0,related,0)]*n,[match]*5,1,0,'successive deletions with duplicate secondary keys')
rng=random.Random(0x511f60)
for _ in range(120):
 primary=[(rng.randrange(3),rng.randrange(16),rng.randrange(3),0,0,rng.randrange(4),0) for _ in range(rng.randrange(9))]
 secondary=[(0,0,0,rng.randrange(3),rng.randrange(3),rng.randrange(4),rng.choice([0,0,1,255])) for _ in range(rng.randrange(13))]
 cancel(primary,secondary,rng.getrandbits(4),rng.getrandbits(4),'ordered random lists and repeated cancellation')
coverage={};pe=load();md=Cs(CS_ARCH_X86,CS_MODE_32);raw=[]
for at,n in ranges.items():
 ins=list(md.disasm(pe.get_data(at-0x400000,n),at));missing=[hex(i.address) for i in ins if not hits[i.address]]
 coverage[hex(at)]={'total':len(ins),'covered':len(ins)-len(missing),'missing':missing}
 raw+=['\n'+hex(at)]+[f'{i.address:08x} {i.mnemonic:8} {i.op_str}' for i in ins]
assert all(not row['missing'] for row in coverage.values()),coverage
(folder/'trick-cleanup-instructions.txt').write_text('\n'.join(raw)+'\n')
fields.update(LOG+j*48+off for j in range((HEAP-LOG)//48) for off in [16,20,24,28])
scope='Five recovered original routines: primary/secondary unlink and concrete deleting destructors, then full511f60 cancellation. Valid circular lists cover clear-before-select masks, all secondary matching gates, first-match deletion, duplicates, captured primary next, idempotence, heap release order and flags. Every fixture byte and release snapshot is compared. Integrated into the main module; the complete playable level remains unfinished.'
fixture={'base':BASE,'memory':'trick-cleanup-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':[],'functions':functions,'float_fields':[],'cases':oracle.cases,'scope':scope,'case_labels':labels,'pointer_fields':sorted(fields),'pointer_exports':[[0x64be88,'thug_trick_primary_methods'],[0x64be8c,'thug_trick_secondary_methods']]}
(folder/'trick-cleanup-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')));(folder/fixture['memory']).write_bytes(initial)
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'instruction_coverage':coverage,'heap_events':dict(oracle.heap_events),'scope':scope}
report_path=folder.parent/'trick-cleanup.json';report_path.write_text(json.dumps(report,indent=2)+'\n');print('Original trick cleanup',len(labels),coverage,flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_trick_cleanup_wasm.mjs')],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [folder/'trick-cleanup-fixtures.json',folder/fixture['memory']]}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS trick cleanup',len(labels),sum(oracle.counts.values()))
