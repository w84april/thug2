"""Compare original scene/sector construction and mesh list initialization."""
from pathlib import Path
source=Path('local/analysis/probe-texture-buffer.py').read_text().split('for fill in [0,0xa5,0xff]:')[0]
exec(compile(source,'<pinned texture heap setup>','exec'))
functions.clear();code.clear();hits.clear();oracle.counts.clear();oracle.coverage.clear()
import random,math
specs=[(0x4d5900,61,'mesh_set_bounds',4,'void',False),
 (0x4b52f0,101,'model_geometry_append_mesh',1,'void',True),
 (0x4de340,146,'model_scene_data_bounds',0,'void',False)]
instructions=[]
for a,n,name,argc,result,heap in specs:
 functions[hex(a)]={'name':'thug_'+name+'_draft','this':True,'result':result,'cleanup':argc*4,'memory':heap}
 code[a]=list(md.disasm(pe.get_data(a-0x400000,n),a));oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:hits.update([at]),begin=a,end=a+n-1)
 instructions += [f'FUNCTION {a:08x} {n} bytes']+[f'{i.address:08x} {i.mnemonic} {i.op_str}' for i in code[a]]
(folder/'mesh-register-instructions.txt').write_text('\n'.join(instructions)+'\n')
exports += [[0x64a434,'thug_model_mesh_node_methods_draft'],[0x64a438,'thug_model_mesh_list_methods_draft']]
put(MANAGER+0x110,'<I',MANAGER+0x240);oracle.scope_entries[MANAGER+0x240]=2
initial=bytes(memory);oracle.initial=initial
for fill in [0,0xa5,0xff]:
 for offset in [-12,-4,0,4,8,12,16,20,256]:
  g=Graph();g.data[P-BASE-16:P-BASE+216]=bytes([fill])*232
  g.put(P+offset,'<3I',0x3f800000,0x7fa12345,0x80000000)
  run(g,[call(0x4d5900,P,[P+offset,0xff812345,0,0])],f'mesh bounds fill{fill}/overlap{offset}')
for existing in [0,1,3]:
 for fill in [0,0xa5,0xff]:
  g=Graph();g.data[P-BASE:P-BASE+100]=bytes([fill])*100;head=g.alloc(20);g.put(head,'<5I',0x64a438,0xffffffff,0,head,head)
  for i in range(existing):
   node=g.alloc(20);tail=g.word(head+16);g.put(node,'<5I',0x64a434,P+512+i*32,i+3,head,tail);g.put(tail+12,'<I',node);g.put(head+16,'<I',node)
  g.put(P+0x38,'<I',head)
  run(g,[call(0x4b52f0,P,[v]) for v in [0,P+640,0xffffffff,P+640]],f'append existing{existing}/fill{fill}')
patterns=[0,0x80000000,1,0x80000001,0x007fffff,0x00800000,0x3f800000,0xbf800000,0x4b000001,0xcb000001,0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc12345,0x7fa12345,0xffa43210]
for i,value in enumerate(patterns):
 for axis in range(3):
  for mode in ['same','opposite','zero']:
   low=[0x3f800000,0xbf800000,0x40000000];high=[0x40a00000,0x41000000,0x40e00000]
   low[axis]=value;high[axis]=value if mode=='same' else value^0x80000000 if mode=='opposite' else 0
   g=Graph();g.put(P+0x44,'<4I',*low,0xdeadbeef);g.put(P+0x54,'<4I',*high,0x01234567)
   run(g,[call(0x4de340,P)]*2,f'scene bounds pattern{i}/axis{axis}/{mode}')
rng=random.Random(0x4de340)
for i in range(160):
 g=Graph();lo=[rng.getrandbits(32) for _ in range(3)];hi=[rng.getrandbits(32) for _ in range(3)]
 g.put(P+0x44,'<3I',*lo);g.put(P+0x54,'<3I',*hi);run(g,[call(0x4de340,P)],f'scene bounds random{i}')
coverage={hex(a):{'total':len(c),'covered':sum(bool(hits[i.address]) for i in c),'missing':[hex(i.address) for i in c if not hits[i.address]]} for a,c in code.items()}
for a,c in coverage.items():
 c['excluded']={'0x4b532f':'successful allocation contract; original null path dereferences null'} if a=='0x4b52f0' else {};assert set(c['missing'])==set(c['excluded']),(a,c)
scope='Three original routines assign raw mesh bounds, append mesh-list nodes under the compression heap scope, and calculate scene centers/radii with x87 spill and rounding order. Successful allocation and valid lists are internal contracts. Only resulting center/radius NaN payloads use classification comparison; finite outputs and all other bytes compare exactly.'
fixture={'base':BASE,'memory':'mesh-register-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'texture-buffer-ports.wasm','memory_exports':['fixture_texture_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[P+o for o in [0x64,0x68,0x6c,0x70]],'cases':oracle.cases,'case_labels':labels,'pointer_fields':sorted(fields),'pointer_exports':exports,'scope':scope}
# Explicit method identities already present in synthetic lists need relocation.
for case in oracle.cases:
 for at,data in case.get('patches',[]):
  if int.from_bytes(bytes.fromhex(data),'little') in [0x64a434,0x64a438]:fields.add(at)
fixture['pointer_fields']=sorted(fields)
(folder/fixture['memory']).write_bytes(initial);(folder/'mesh-register-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(len(c['steps']) for c in oracle.cases),'instruction_coverage':coverage,'scope':scope}
(folder/'mesh-register-original.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
