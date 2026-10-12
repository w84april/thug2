"""Original camera descriptor storage; no old builders/output writes."""
from pathlib import Path
source=Path('local/analysis/probe-skater-camera-reset-v1.py').read_text().split('for fill,alignment,layout')[0]
exec(compile(source,'<preserved initialized original camera setup>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear();prefix_hits.clear()
specs=[(0x5902e0,3,'thug_camera_extra_storage_construct_v1',0,'word',False,False,True),(0x4fa4b0,224,'thug_skater_camera_construct_storage_v1',0,'word',True,False,True),(0x4fa800,89,'thug_skater_camera_create_storage_v1',0,'word',True,False,False),(0x4e42e0,87,'thug_skater_camera_object_create_storage_v1',0,'word',True,False,False),(0x525dc0,127,'thug_skater_camera_roll_create_storage_v1',0,'word',True,False,False),(0x4f9a20,24,'thug_skater_camera_bind_object_v1',0,'void',False,False,True)]
for row in specs:bind_new(*row)
exports.extend([[0x64ba74,'thug_skater_camera_pending_methods_v1'],[0x64b28c,'thug_skater_camera_object_pending_methods_v1'],[0x64c5e0,'thug_skater_camera_roll_pending_methods_v1']])
for fill,alignment,failure in itertools.product([0,0xa5,255],[0,1,4],[False,True]):
 g=FinalGraph(fill);p=P+alignment;fields.add(p)
 if failure:g.put(CONTEXT+32,'<I',1)
 g.run([call(0x4fa4b0,p)]*2,f'camera repeated constructor/{fill}/{alignment}/{failure}')
 assert oracle.word(p+4)==0x5e43a604 and oracle.word(p+0x24)==0
for factory in [0x4fa800,0x4e42e0,0x525dc0]:
 for count in [1,2,4]:
  g=FinalGraph();g.run([call(factory)]*count,f'camera descriptor factory/{factory:x}/{count}')
 g=FinalGraph();g.put(CONTEXT+32,'<I',1);g.run([call(factory)]*2,f'camera descriptor allocation failure/{factory:x}')
for value in [0,P,P+1,P+4,0x12345678,0xffffffff]:
 g=FinalGraph();g.run([call(0x5902e0,value)]*2,f'extra storage identity only/{value}')
for fill,alignment,shape in itertools.product([0,0xa5,255],[0,1,4],['absent','matching','decoy','duplicates','null owner list']):
 g=FinalGraph(fill);p=P+alignment;g.put(p+12,'<I',OBJ)
 nodes=[] if shape in ['absent','null owner list'] else [g.component(0x81c7122d)] if shape=='matching' else [g.component(0x12345678),g.component(0x81c7122d)] if shape=='decoy' else [g.component(0x81c7122d),g.component(0x81c7122d)]
 for a,b in zip(nodes,nodes[1:]):g.put(a+16,'<I',b)
 g.put(OBJ+0x100,'<I',nodes[0] if nodes else 0);g.run([call(0x4f9a20,p)]*2,f'camera object first component bind/{fill}/{alignment}/{shape}')
 assert oracle.word(p+0x168)==(next((n for n in nodes if oracle.word(n+4)==0x81c7122d),0))
scope='Six camera descriptor dependencies: three initialized-heap factories, SkaterCamera constructor storage, actual three-byte extra-storage identity routine and direct first CameraObject binding. Poisoned/unaligned storage, repeat allocation/construction, allocation failures, absent/decoy/duplicate bounded component graphs and unchanged auxiliary98h bytes compare. Only literal4fa4f3 cold allocator bootstrap call excluded under initialized-service contract. Pending identity-only tables establish no virtual initialization, disposal, updates, full original camera composite startup or gameplay. Existing component base/allocator callees receive no repeated credit; no fake game callee, numeric/comparator change or matching claim.'
finish('skater-camera-factories-v1',scope,{'0x4fa4f3':'initialized allocator contract excludes the literal cold bootstrap call'},extra)
(folder/'skater-camera-factories-v1-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n')
