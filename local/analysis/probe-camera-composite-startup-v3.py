"""Original generic camera initialization and actual QB five-component assembly."""
from pathlib import Path
source=Path('local/analysis/probe-skater-camera-initialization-v3.py').read_text().split('\nfor fill,alignment in itertools')[0]
exec(compile(source,'<preserved original camera services; builders omitted>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear();prefix_hits.clear()
specs=[(0x41b7f0,24,'thug_generic_camera_initialize_priority_v1',1,'void',True,False,True)]
for row in specs:bind_new(*row)
bind(0x45f330,'thug_composite_create_draft',0,'word',True)
bind(0x45f3a0,'thug_composite_create_from_array_draft',3,'word',True,True)
function_exports.append([0x4619d0,'thug_object_manager_set_priority']);fields.add(MANAGER_METHODS+0x10)
function_exports.extend([[0x4e42e0,'thug_skater_camera_object_create_storage_v1'],[0x4fa800,'thug_skater_camera_create_storage_v1'],[0x525dc0,'thug_skater_camera_roll_create_storage_v1'],[0x41b840,'thug_camera_component_create_v2']])
class CameraCompositeGraph(CameraInitializeGraph):
 def __init__(self,fill=0):
  super().__init__(fill);self.put(MANAGER_METHODS+0x10,'<I',0x4619d0);self.put(ALLOCATOR+0x114,'<I',ALLOCATOR+0x20c)
  self.registry([(0x81c7122d,0x4e42e0),(0x5e43a604,0x4fa800),(0xc7d37ec2,0x525dc0),(0xc4e311fa,0x41b840),(0x27d7cd28,0x41eec0)])
for fill,alignment,param in itertools.product([0,0xa5,255],[0,1,4],[0,0xffffffff]):
 g=CameraCompositeGraph(fill);p=P+alignment;stages=g.run([call(0x45f330,MANAGER)],f'priority owner creation/{fill}/{alignment}/{param}');owner=stages[-1]['result']
 # Patches cannot be inserted between calls. Start the second case from a
 # fresh graph with the same real constructor sequence; known first allocation
 # identity is HEAP and is checked against the separate original create result.
 assert owner==HEAP;g=CameraCompositeGraph(fill);g.put(p+12,'<I',owner)
 g.run([call(0x45f330,MANAGER),call(0x41b7f0,p,[param]),call(0x41b7f0,p,[param])],f'generic camera priority repeats/{fill}/{alignment}/{param}')
 assert oracle.word(owner+0x30)==0xfffffc18
discovery=json.loads((folder/'skater-camera-qb-v1-discovery.json').read_text());asset=ROOT/discovery['asset']['path'];assert hashlib.sha256(asset.read_bytes()).hexdigest()==discovery['asset']['sha256']
integration=[]
for fill,route,flag in itertools.product([0,0xa5,255],['missing','primary','secondary'],[0,1,256,257]):
 g=CameraCompositeGraph(fill);target=g.target('complete',route,42)
 descriptors=[g.structure([(int(r['name'],16),r['type'],int(r['value'],16)) for r in rows]) for rows in discovery['descriptors']]
 array=g.array(10,descriptors);params=g.structure([(0x4c48da58,13,42),(0xa1dc81f9,13,0xe17b231a)])
 stages=g.run([call(0x45f3a0,MANAGER,[array,params,flag])],f'actual five camera descriptors/{fill}/{route}/{flag}');owner=stages[-1]['result'];chain=[];c=oracle.word(owner+0x100)
 while c:chain.append((c,oracle.word(c+4)));assert len(chain)<=5;c=oracle.word(c+16)
 assert [t for _,t in chain]==[0x81c7122d,0x5e43a604,0xc7d37ec2,0xc4e311fa,0x27d7cd28]
 links={t:c for c,t in chain};assert oracle.word(owner+0x30)==0xfffffc18
 assert oracle.word(links[0x5e43a604]+0x170)==(target if route!='missing' else 0)
 assert oracle.word(links[0xc7d37ec2]+0x9c)==(target if route!='missing' else 0)
 if flag&255:
  assert oracle.word(links[0x81c7122d]+0x40)==links[0x27d7cd28]
  assert oracle.word(links[0x5e43a604]+0x168)==links[0x81c7122d]
  assert [oracle.word(links[0xc7d37ec2]+o) for o in [0x90,0x94,0x98]]==[links[0x81c7122d],links[0xc4e311fa],links[0x5e43a604]]
  assert oracle.word(owner+0x104)&0x60==0x60
 integration.append({'fill':fill,'lookup':route,'finalize_word':flag,'low_byte_finalized':bool(flag&255),'owner':owner,'components':chain,'target':target if route!='missing' else 0})
scope='One new24-byte generic Camera initialization calls the original manager virtual priority setter. Bounded poison/unaligned component storage, unused invalid QB pointer and repeated real registry re-registration compare. Integrated45f3a0 root assembles actual five type descriptors from original skutils QB through real factories, typed startup initialize/finalize/moved slots, primary/secondary/missing target routes, merged overrides, camera priority, node rename and low-byte finalize0/1/256/257. All original game callees execute; initialized heap/platform boundaries retained. Derived method tables expose only verified startup slots, not disposal/frame/commands. No full profile startup, camera update/reset, controllable skater, rendered game frame, matching or new credit for reused functions.'
finish('camera-composite-startup-v3',scope,{}, {**extra,'function_exports':function_exports})
(folder/'camera-composite-startup-v3-integration.json').write_text(json.dumps({'result':'original pass; Wasm pending','descriptor_asset':discovery['asset'],'records':integration,'no_game_callee_substitution':True,'full_create_from_array_root_replayed':True,'playable':False},indent=2)+'\n')
(folder/'camera-composite-startup-v3-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n')
