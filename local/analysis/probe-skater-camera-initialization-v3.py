"""Original camera QB initialization and bounded target/finalize dependencies."""
from pathlib import Path
source=Path('local/analysis/probe-skater-camera-factories-v1.py').read_text().split('for fill,alignment,failure')[0]
exec(compile(source,'<preserved original initialized camera services>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear();prefix_hits.clear()
specs=[(0x4fa3c0,84,'thug_skater_camera_bind_target_v1',1,'void',False,False,True),(0x524c50,83,'thug_skater_camera_roll_bind_target_v1',1,'void',False,False,True),(0x4e3f70,24,'thug_skater_camera_object_initialize_v1',1,'void',False,False,True),(0x4e4040,21,'thug_skater_camera_object_finalize_v1',0,'void',False,False,True),(0x524fb0,62,'thug_skater_camera_roll_finalize_v1',0,'void',False,False,True),(0x4fa5c0,189,'thug_skater_camera_initialize_v1',1,'void',False,False,True),(0x524f50,88,'thug_skater_camera_roll_initialize_v1',1,'void',False,False,True)]
for row in specs:bind_new(*row)
class CameraInitializeGraph(FinalGraph):
 def chain(self,owner,types):
  nodes=[self.component(t) for t in types]
  for a,b in zip(nodes,nodes[1:]):self.put(a+16,'<I',b)
  self.put(owner+0x100,'<I',nodes[0] if nodes else 0);return nodes
 def target(self,shape,route='primary',id=42):
  target=self.alloc(0x110);types=[] if shape=='absent' else [0x43686585,0x726e85aa,0xd9151d4d] if shape=='complete' else [0x12345678,0x43686585,0x726e85aa,0xd9151d4d] if shape=='decoy' else [0x43686585,0x43686585,0x726e85aa,0x726e85aa,0xd9151d4d,0xd9151d4d]
  self.chain(target,types);table=self.table([(id,target)]);empty=self.table([])
  self.put(EM+8,'<2I',table if route=='primary' else empty,table if route=='secondary' else empty);return target
for fill,alignment in itertools.product([0,0xa5,255],[0,1,4]):
 g=CameraInitializeGraph(fill);p=P+alignment;g.run([call(0x4e3f70,p,[0xffffffff])]*2,f'camera object QB ignores parameter/{fill}/{alignment}')
 for routine in [0x4e4040,0x524fb0]:
  for shape in ['absent','complete','decoy','duplicates']:
   g=CameraInitializeGraph(fill);p=P+alignment;g.put(p+12,'<I',OBJ)
   types=[] if shape=='absent' else [0x81c7122d,0xc4e311fa,0x5e43a604,0x27d7cd28]
   if shape=='decoy':types.insert(0,0x12345678)
   if shape=='duplicates':types+=types
   g.chain(OBJ,types);g.run([call(routine,p)]*2,f'camera final component links/{routine:x}/{fill}/{alignment}/{shape}')
 for routine in [0x4fa3c0,0x524c50]:
  for shape in ['absent','complete','decoy','duplicates']:
   g=CameraInitializeGraph(fill);p=P+alignment;target=g.target(shape)
   g.run([call(routine,p,[target]),call(routine,p,[0]),call(routine,p,[target])],f'camera target bind transitions/{routine:x}/{fill}/{alignment}/{shape}')
for fill,alignment,routine,params_kind,route in itertools.product([0,0xa5,255],[0,1,4],[0x4fa5c0,0x524f50],['absent','wrong','typed','duplicate','high bit'],['missing','primary','secondary']):
 g=CameraInitializeGraph(fill);p=P+alignment;g.put(p+12,'<I',OBJ);id=0x81234567 if params_kind=='high bit' else 42;target=g.target('decoy',route,id)
 kind=13
 rows=[] if params_kind=='absent' else [(0x4c48da58,3,g.text('wrong parameter kind'))] if params_kind=='wrong' else [(0x4c48da58,kind,id)]
 if params_kind=='duplicate':rows.insert(0,(0x4c48da58,kind,7))
 params=g.structure(rows)
 g.put(OBJ+0x6c,'<16I',*[0x80000000 if i%3==0 else 0x7fa12345 if i%3==1 else 0x11223344+i for i in range(16)])
 g.run([call(routine,p,[params])]*2,f'camera required QB initialize/{routine:x}/{fill}/{alignment}/{params_kind}/{route}')
 assert oracle.word(p+(0x170 if routine==0x4fa5c0 else 0x9c))==(target if params_kind not in ['absent','wrong'] and route!='missing' else 0),(routine,fill,alignment,params_kind,route,hex(oracle.word(p+(0x170 if routine==0x4fa5c0 else 0x9c))),hex(target),hex(id))
scope='Seven complete camera QB initialization, target binding and final component-link routines. Direct original callees perform required checksum getter variants, primary/secondary global object lookup and first component scans. Missing/wrong/duplicate/high-bit QB parameters, bounded absent/decoy/duplicate graphs, target/null/target transitions, poisoned/unaligned caller storage, preserved partial bytes and exact matrix words compare. No frame, command, virtual table, full composite/profile startup, numeric/checker change or gameplay claim; reused callees earn no repeated bytes.'
finish('skater-camera-initialization-v3',scope,{},extra)
(folder/'skater-camera-initialization-v3-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n')
