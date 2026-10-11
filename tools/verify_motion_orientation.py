import subprocess
"""Original node orientation through real angle lookup and selected SSE math."""
from pathlib import Path
prefix=Path('tools/verify_node_vectors.py').read_text().split('initial=bytes(memory);oracle=')[0]
prefix=prefix.replace('node-vectors.json','motion-orientation.json')
exec(compile(prefix,'<node vector fixture setup>','exec'))
import math
COMPONENT=alloc(32);BODY=alloc(0x300)
put(COMPONENT+12,'<I',BODY)
functions={'0x425970':{'name':'thug_motion_orient_to_node','this':True,'result':'void','cleanup':4}}
initial=bytes(memory);oracle=ScriptHeapOracle(initial,BASE,CONTEXT,MANAGER,globals_,[BASE,table],functions,observe=[0x45c180,0x476fb0,0x404dd0,0x404e20,0x404e70,0x5df4ac,0x404090])
oracle.setword(0x684fe4,0x5df4ac)
hits=Counter();labels=[]
def trace(cpu,at,size,user):hits[at]+=1
oracle.cpu.hook_add(UC_HOOK_CODE,trace,begin=0x425970,end=0x425a77)
def case(node,p=(),label='node orientation'):
 oracle.case([(0x425970,COMPONENT,[node])]*2,p);labels.append(label)
for node in sets:case(node,label='missing angles, wrong fields and real angles')
for axis in range(3):
 for angle in [0.,-0.,.125,-.5,math.pi/2,-math.pi,3.,10.,-100.,10000.]:
  angles=[0.,0.,0.];angles[axis]=angle
  case(sets[4],[patch(PAYLOAD+4,'<3f',*angles)],label='single axis and signed zero')
for _ in range(40):
 angles=[rng.uniform(-4,4) for _ in range(3)]
 case(sets[4],[patch(PAYLOAD+4,'<3f',*angles)],label='three-axis postmultiply ordering')
# The node's vector can point into the body basis: identity is written first.
# The vector header is followed by its three values, so this tests the actual
# read/write order through the original typed getter.
member=word(sets[4]+4)
for offset in [0x48,0x4c,0x68,0x6c,0x70,0x78,0x8c,0xbc,0xc0]:
 case(sets[4],[patch(member+8,'<I',BODY+offset)],label='angle vector aliases body storage')
pe=load();md=Cs(CS_ARCH_X86,CS_MODE_32);rows=list(md.disasm(pe.get_data(0x25970,264),0x425970));missing=[hex(i.address) for i in rows if not hits[i.address]]
scope='Complete00425970 node orientation with actual45c180 angle lookup, original sin/cos and selected SSE matrix multiply. Finite angles, signed zero, three-axis order, repeated calls and body/vector aliasing. Nonfinite inputs are outside this corpus. Integrated into the main module; full game integration remains unfinished.'
fixture={'base':BASE,'memory':'motion-orientation-memory.bin','globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope}
(folder/'motion-orientation-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')));(folder/fixture['memory']).write_bytes(initial)
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'counts':dict(oracle.counts),'instruction_coverage':{'total':len(rows),'covered':len(rows)-len(missing),'missing':missing},'callee_coverage':dict(oracle.coverage),'scope':scope}
(folder.parent/'motion-orientation.json').write_text(json.dumps(report,indent=2)+'\n');print('Original node orientation',len(labels),sum(oracle.counts.values()),report['instruction_coverage'],flush=True)

subprocess.run(['node',str(ROOT/'tools/verify_motion_orientation_wasm.mjs')],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [folder/'motion-orientation-fixtures.json',folder/fixture['memory']]}
(folder.parent/'motion-orientation.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS motion-orientation',report['cases'],sum(oracle.counts.values()))
