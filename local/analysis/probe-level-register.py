"""Original scene registration with real finalization and existing sector lookup."""
from pathlib import Path
source=Path('local/analysis/probe-scene-finalize.py').read_text()
exec(compile(source.split('specs=')[0],'<preserved scene finalization fixture setup>','exec'))
exec(compile(Path('local/analysis/probe-scene-finalize.py').read_text().split('# Explicit-list and valid mesh storage builders; payloads are never substituted.')[1].split('for fn in [0x4b5ec0')[0],'<preserved valid graph builders>','exec'))
exec(compile((folder/'level-register-oracle-setup.py').read_text(),'<registry initialization>','exec'))
functions.update({'0x48c560':{'name':'thug_level_scene_register_draft','this':False,'result':'void','cleanup':0,'memory':True},'0x48c510':{'name':'thug_scenes_find_object','this':False,'result':'word','cleanup':0,'memory':False}})
exports += [[0x64a434,'thug_model_mesh_node_methods_draft'],[0x64a438,'thug_model_mesh_list_methods_draft'],[0x64a6b8,'thug_model_scene_pc_methods_draft']]
code={0x48c560:list(md.disasm(pe.get_data(0x8c560,225),0x48c560))};hits.clear()
for a,c in code.items():oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:hits.update([at]),begin=a,end=c[-1].address)
initial=bytes(memory);oracle.initial=initial

def scene(g,sectors,n):
 scene=g.alloc(644);g.data[scene-BASE:scene-BASE+644]=bytes(644);header=g.alloc(132);g.data[header-BASE:header-BASE+132]=bytes(132);rows=[]
 for si in range(sectors):
  sector=g.alloc(52);geometry=g.alloc(100);values=[mesh(g,i+si)[0] for i in range(n)];head,nodes=linked(g,values)
  g.put(geometry+0x34,'<4I',scene,head,0,n);g.put(sector+0x14,'<I',geometry);g.put(sector+4,'<I',si+1);rows.append((si+1,sector))
 table=g.table(rows);g.put(scene,'<I',0x64a6b8);g.put(scene+0xd0,'<I',table);g.put(scene+0x280,'<I',header);return scene

for name in [b'',b'TR',b'tr',b'Mixed/Path',b'percent%s',b'a'*55,b'back\\slash']:
 for skip in [0,1,256,257,0x10000,0xffffffff]:
  g=Graph();s=scene(g,3,3);text=g.alloc(len(name)+1);g.data[text-BASE:text-BASE+len(name)+1]=name+b'\0'
  run(g,[call(0x48c560,0,[s,text,0x12345678,skip,0]),call(0x48c510,0,[1]),call(0x48c510,0,[3]),call(0x48c510,0,[99])],f'name{name!r}/skip{skip}')
for sectors in [0,1,3]:
 for n in [0,1,3]:
  for prefix in [0,1,3]:
   g=Graph();text=g.alloc(3);g.data[text-BASE:text-BASE+3]=b'TR\0';calls=[]
   for i in range(prefix):calls.append(call(0x48c560,0,[scene(g,1,0),text,0x12345678,1,0]))
   s=scene(g,sectors,n);calls += [call(0x48c560,0,[s,text,0x87654321,0,0]),call(0x48c560,0,[s,text,0x87654321,1,0]),call(0x48c510,0,[1]),call(0x48c510,0,[3]),call(0x48c510,0,[99])]
   run(g,calls,f'prefix{prefix}/sectors{sectors}/meshes{n}')
coverage={hex(a):{'total':len(c),'covered':sum(bool(hits[i.address]) for i in c),'missing':[hex(i.address) for i in c if not hits[i.address]]} for a,c in code.items()}
coverage['0x48c560']['excluded']={'0x48c608':'successful allocation internal contract'}
assert set(coverage['0x48c560']['missing'])==set(coverage['0x48c560']['excluded'])
for case in oracle.cases:
 for at,data in case.get('patches',[]):
  if int.from_bytes(bytes.fromhex(data),'little') in {e[0] for e in exports}:fields.add(at)
prior=json.loads((folder/'scene-finalize-fixtures.json').read_text())
scope='Original48c560 path formatting/name checksum, optional real scene finalization, global registry append and existing48c510 sector lookup. Empty/populated registry, duplicate registrations, fitting literal names and low-byte flags; valid successful-allocation internal contracts. Original CRT formatting executes unchanged with initialized C locale. No graphics/gameplay callbacks substituted.'
fixture={**prior,'memory':'level-register-memory.bin','globals':globals_,'functions':functions,'cases':oracle.cases,'case_labels':labels,'pointer_fields':sorted(fields),'pointer_exports':exports,'pointer_globals':registry_pointer_globals,'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'level-register-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(len(c['steps']) for c in oracle.cases),'instruction_coverage':coverage,'scope':scope}
(folder/'level-register-original.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
