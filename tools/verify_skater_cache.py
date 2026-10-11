"""Full-instruction checks for the per-frame embedded collision cache."""
from pathlib import Path
prefix=Path('tools/verify_side_contact.py').read_text().split('# Writable checksum')[0]
prefix=prefix.replace("report_path=out.parent/'side-contact.json'","report_path=out.parent/'skater-cache.json'")
exec(compile(prefix,'<existing training collision arena>','exec'))
from unicorn.x86_const import UC_X86_REG_FPSW,UC_X86_REG_FPTAG,UC_X86_REG_MXCSR
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
from specimen import load
import math
embedded=PHYS+0x4f4
functions.clear()
bind(0x500670,'thug_skater_build_collision_cache')
bind(0x40ab50,'thug_collision_cache_initialize',result='word')
for j in range(8):glob('thug_collision_cache_registry',0x6918ec+4*j,0,offset=j*4)
glob('thug_collision_cache_mask',0x69190c)
for at in [0x500670,0x40ab50,0x402600,0x40aba0,0x40ad00,0x40ad8a]:
 if at not in observe:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at);observe.append(at)
instruction_hits=Counter()
def trace_parent(cpu,at,size,user):instruction_hits[at]+=1
oracle.cpu.hook_add(UC_HOOK_CODE,trace_parent,begin=0x500670,end=0x500704)
def run(position,label,extra=(),changes=None,repeat=1):
 oracle.cpu.reg_write(UC_X86_REG_FPSW,0);oracle.cpu.reg_write(UC_X86_REG_FPTAG,0xffff);oracle.cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
 p=[patch(BODIES+0x4c,'<4f',*position)]+list(extra)
 result=case([call(0x40ab50,embedded)]+[call(0x500670,PHYS) for _ in range(repeat)],p,changes,label)
 assert oracle.word(0x691974)==embedded
 assert oracle.word(embedded+0xfc0)<=500
 assert oracle.word(embedded+0xfc0)==oracle.word(embedded+0xfc4)+oracle.word(embedded+0xfc8)
 return result
selected=[0,1,2,3,13,24,26,30,34,39,57,70,98,129,278,400,488,510,521,545]
for i in selected:
 point=struct.unpack_from('<4f',bytes.fromhex(loader['queries'][i]['result']),16)
 for moving in [False,True]:
  links=[]
  if moving:links=[patch(COLL_NODES+j*16,'<4I',0,RUNTIME+j*256,0,COLL_NODES+(j+1)*16) for j in range(3)]+[patch(COLL_NODES+48,'<4I',0,0xffffffff,0,COLL_NODES+48)]
  run(point,f'training point {i} moving {moving}',links,repeat=2 if i in [34,70] else 1)
for p in [[0,0,0,1],[-0.,-0.,-0.,-0.],[20000,20000,20000,1],[-20000,-20000,-20000,0],[1e38,0,1e38,1],[math.inf,0,0,1],[-math.inf,0,0,1],[math.nan,0,0,1],[0,math.nan,0,1],[0,0,math.nan,1]]:
 run(p,'finite extremes and unordered scene selection')
for word in [0,0x80000000,0x3f800000,0x7f800001,0x7fc12345,0xffc12345,0x7f800000]:
 run([0,0,0,1],'fourth position lane raw bits',[patch(BODIES+0x58,'<I',word)])
for flags in [0,2,4,6]:
 point=struct.unpack_from('<4f',bytes.fromhex(loader['queries'][34]['result']),16)
 run(point,f'moving flags {flags} and stamp wrap',[patch(COLL_NODES,'<8I',0,RUNTIME,0,COLL_NODES+16,0,0xffffffff,0,COLL_NODES+16),patch(RUNTIME+8,'<H',flags)],{0x693998:255})
run([0,0,0,1],'empty scene retains entry storage',[patch(SCENES+4,'<I',0xffffffff)])
for offset in [-204,-96,0,96,204]:
 point=struct.unpack_from('<4f',bytes.fromhex(loader['queries'][34]['result']),16)
 run([point[0],point[1]+offset,point[2],point[3]],f'asymmetric vertical bounds {offset}')
instructions={i.address for i in Cs(CS_ARCH_X86,CS_MODE_32).disasm(load().get_data(0x100670,0x95),0x500670)}
assert set(instruction_hits)==instructions
assert oracle.coverage['0x40ad00']>0
scope='Complete 00500670 frame collision-cache builder. Full original parent instructions and real static/moving training collision callees; exact arena/global byte comparison. No gameplay substitute. Integrated with the main WebAssembly build; not the complete dispatcher.'
fixture={'base':BASE,'memory':'skater-cache-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields)}
path=out/'skater-cache-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
report={'result':'original pass; Wasm comparison pending','specimen_sha256':SHA256,'cases':len(labels),'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'parent_instructions':len(instructions),'parent_instructions_executed':len(instruction_hits),'scope':scope}
report_path.write_text(json.dumps(report,indent=2)+'\n')
print('Original cache complete',len(labels),dict(oracle.counts),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_skater_cache_wasm.mjs'),str(out)],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [out/'skater-cache-fixtures.json',out/fixture['memory']]}
report_path.write_text(json.dumps(report,indent=2)+'\n')
print('PASS skater cache',len(labels),sum(oracle.counts.values()),flush=True)
