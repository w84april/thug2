import subprocess
"""Original node vectors, including actual node-table and typed QB lookup."""
from pathlib import Path
prefix=Path('tools/verify_contact_nodes.py').read_text().split('initial=bytes(memory);')[0]
prefix=prefix.replace('contact-nodes.json','node-vectors.json')
exec(compile(prefix,'<node table and symbol fixture setup>','exec'))
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
from script_heap_oracle import ScriptHeapOracle
folder=ROOT/'local/validation/collision'
PAYLOAD,OTHER,OUTPUT=alloc(16),alloc(16),alloc(64)
put(PAYLOAD,'<4I',0,0x3f800000,0x40000000,0x40400000)
put(OTHER,'<4I',0,0x40a00000,0x40c00000,0x40e00000)
sets=[]
for entries in [[],[(0x7f261953,6,PAYLOAD)],[(0xb9d31b0a,6,PAYLOAD)],[(0x7f261953,6,PAYLOAD),(0xb9d31b0a,6,OTHER)],[(0x9d2d0915,6,PAYLOAD)],[(0x7f261953,1,1),(0xb9d31b0a,6,OTHER)],[(0x7f261953,6,PAYLOAD),(0x7f261953,6,OTHER)]]:
 sets.append(structure(entries)[0])
symbol(0x71234444,10,sets[3]);sets.append(structure([(0,13,0x71234444)])[0])
CONTEXT=alloc(32);MANAGER=alloc(0x500);LOG=alloc(512);HEAP=alloc(256)
put(CONTEXT,'<8I',HEAP,HEAP+256,0,LOG,BASE,BASE+len(memory),0,0)
globals_=[['thug_script_symbol_buckets',0x6f3624,4],['thug_node_table',0x6f0d84,4]]
functions={hex(at):{'name':name,'this':False,'result':'void','cleanup':0} for at,name in [(0x45c050,'thug_node_position'),(0x45c560,'thug_node_position_by_name'),(0x45c180,'thug_node_angles')]}
initial=bytes(memory);oracle=ScriptHeapOracle(initial,BASE,CONTEXT,MANAGER,globals_,[BASE,table],functions,observe=[0x45cfc0,0x476fb0,0x476950])
ranges={0x45c050:89,0x45c560:33,0x45c180:38};hits=Counter();labels=[]
def trace(cpu,at,size,user):hits[at]+=1
for at,n in ranges.items():oracle.cpu.hook_add(UC_HOOK_CODE,trace,begin=at,end=at+n-1)
def case(fn,args,p=(),label='node vector'):
 oracle.case([(fn,0,args)]*2,p);labels.append(label)
words=[0,0x80000000,1,0x80000001,0x3f800000,0xbf800000,0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc12345,0xffc23456]
for i in range(len(words)):
 p=[patch(PAYLOAD+4,'<3I',*[words[(i+j)%len(words)] for j in range(3)])]
 for node in sets:
  for fn in [0x45c050,0x45c180]:case(fn,[node,OUTPUT],p,'field priority, types, nested inclusion and numeric lanes')
for fn in [0x45c050,0x45c180]:
 for node in sets[1:5]:
  for delta in [-4,0,4,8,12]:case(fn,[node,PAYLOAD+delta],label='output overlaps vector payload')
# Defaults are written before reading the angles structure. Aliasing its header
# therefore changes the actual lookup input; compare that ordering directly.
case(0x45c180,[sets[4],sets[4]],label='angles output aliases structure header')
for i,node in enumerate(sets):
 key=0x73500001+i
 p=[patch(table+(key&0x3fff)*4,'<Hh',0,-2),patch(node_members[0]+8,'<I',key),patch(node_structs[0]+4,'<I',word(node+4))]
 # Keep the required Name component, then append this node's property list.
 p[-1]=patch(node_members[0]+12,'<I',word(node+4))
 case(0x45c560,[key,OUTPUT],p,'actual named node lookup')
coverage={};pe=load();md=Cs(CS_ARCH_X86,CS_MODE_32)
for at,n in ranges.items():
 rows=list(md.disasm(pe.get_data(at-0x400000,n),at));missing=[hex(i.address) for i in rows if not hits[i.address]]
 coverage[hex(at)]={'total':len(rows),'covered':len(rows)-len(missing),'missing':missing}
scope='Complete45c050 position,45c560 named-position and45c180 angles helpers, with actual typed QB access and node lookup. Includes retained calls, field precedence, missing/wrong types, nested symbols, aliases, finite values, signedzero, infinities and quietNaN payloads. SignalingNaN inputs are not in this corpus. Named lookup requires an existing node, as in the original. Integrated into the main module; full game integration remains unfinished.'
fixture={'base':BASE,'memory':'node-vectors-memory.bin','globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope}
(folder/'node-vectors-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')));(folder/fixture['memory']).write_bytes(initial)
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'counts':dict(oracle.counts),'instruction_coverage':coverage,'callee_coverage':dict(oracle.coverage),'scope':scope}
(folder.parent/'node-vectors.json').write_text(json.dumps(report,indent=2)+'\n');print('Original node vectors',len(labels),sum(oracle.counts.values()),coverage,flush=True)

subprocess.run(['node',str(ROOT/'tools/verify_node_vectors_wasm.mjs')],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [folder/'node-vectors-fixtures.json',folder/fixture['memory']]}
(folder.parent/'node-vectors.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS node-vectors',report['cases'],sum(oracle.counts.values()))
