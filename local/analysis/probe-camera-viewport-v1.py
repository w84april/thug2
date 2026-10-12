"""Original viewport registration with real camera constructors/deletion/update."""
from pathlib import Path
source=Path('local/analysis/probe-camera-startup-v2.py').read_text().split('for fov,ratio')[0]
exec(compile(source,'<preserved camera oracle; no builders or output writes>','exec'))
coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear();prefix_hits.clear()
specs=[(0x4a0d70,57,'thug_viewport_clear_owned_camera_v1',0,'void',True,True,True),
 (0x4a0970,73,'thug_viewport_assign_camera_v1',2,'void',True,True,False),
 (0x59f890,149,'thug_player_register_camera_v1',3,'byte',True,True,False)]
for row in specs:bind_new(*row)
functions['0x4637c0']={'name':'thug_object_reference_link','this':True,'result':'void','cleanup':4,'memory':False}
MAP=BASE+0x3c0000
global_default('thug_viewport_mapping',0x67e540,MAP)
for i in range(10):glob('thug_viewports',0x701350+4*i,0,offset=4*i)
oracle.globals=globals_;oracle.defaults=defaults
initial=bytes(memory);oracle.initial=initial
class ViewportGraph(FinalGraph):
 def __init__(self):
  super().__init__();self.put(MAP,'<10i',*([-1]*10))
 def camera(self):
  p=self.alloc(0xc4);fields.add(p);return p
 def viewport(self,camera=0,flags=0):
  p=self.alloc(0x24);self.put(p+0x14,'<I',flags);self.put(p+0x18,'<3I',camera,0,0);return p
 def link_calls(self,camera,refs):
  # The original linker expects fresh links; allocated graph storage is poison.
  for reference in refs:self.put(reference,'<3I',camera,0,0)
  return [call(0x4637c0,camera,[reference]) for reference in refs]
for flags,shape in itertools.product([0,1,2,3,255,256,257,0xffffffff],['empty','linked','unregistered owned']):
 g=ViewportGraph();camera=0 if shape=='empty' else g.camera();viewport=g.viewport(camera,flags);calls=[]
 if camera:
  calls=[call(0x485ba0,camera)]
  if shape=='linked':calls+=g.link_calls(camera,[g.alloc(12),viewport+0x18,g.alloc(12)])
 g.put(CONTEXT+24,'<I',viewport+0x18)
 g.run(calls+[call(0x4a0d70,viewport)]*2,f'owned viewport release/{flags}/{shape}')
for flags,shape,new in itertools.product([0,1,255],['empty','linked'],['null','distinct','same']):
 g=ViewportGraph();old=0 if shape=='empty' else g.camera();camera=0 if new=='null' else old if new=='same' else g.camera();viewport=g.viewport(old,flags)
 calls=[call(0x485ba0,p) for p in dict.fromkeys([old,camera]) if p]
 if old:calls+=g.link_calls(old,[g.alloc(12),viewport+0x18,g.alloc(12)])
 g.put(MAP,'<i',2)
 g.run(calls+[call(0x4a0970,args=[0,camera])]*2+[call(0x4a0970,args=[0,0])],f'viewport assignment/{flags}/{shape}/{new}',{0x701358:viewport})
 assert oracle.word(viewport+0x18)==0
g=ViewportGraph();g.run([call(0x4a0970,args=[0,0xffffffff])]*2,'unused viewport mapping skips invalid supplied camera')
for shape,force in itertools.product(['absent','missing component','primary','secondary','collision','null payload'],[0,1,2,255,256,257]):
 if shape=='null payload' and force&255:continue
 g=ViewportGraph();key=2;old=g.camera();camera=0 if shape=='null payload' else g.camera();v0=g.viewport();viewport=g.viewport(old,0x80000000)
 g.put(MAP,'<10i',0,1,*([-1]*8))
 component=g.alloc(0x1c);fields.add(component);g.put(component,'<7I',0x645e34,0xc4e311fa,0,OBJ,0,0,camera)
 g.put(OBJ+0x100,'<I',0 if shape=='missing component' else component)
 entries=[] if shape=='absent' else [(key,OBJ)]
 if shape=='collision':entries=[(key^4,g.alloc(0x110)),(key,0),(key,OBJ)]
 g.put(EM+8,'<2I',g.table([] if shape=='secondary' else entries),g.table(entries if shape=='secondary' else []))
 calls=[call(0x485ba0,p) for p in dict.fromkeys([old,camera]) if p]+g.link_calls(old,[viewport+0x18])
 g.run(calls+[call(0x59f890,args=[key,1,force])]*2,f'player camera lookup/force/{shape}/{force}',{0x701350:v0,0x701354:viewport})
 assert oracle.cases[-1]['steps'][-1]['result']==(0 if shape=='absent' else 1)
scope='Three viewport-registration routines execute with real camera object lifecycle, intrusive reference operations, global owner/component lookup and virtual Camera update. Owned flag low-bit, low-byte force, absent/secondary/colliding lookup, null payload without forced update, unused mappings, linked/external references and raw unregistered owned pointer storage compare. The comparison allocator retains released storage; assigning the same owned pointer is a raw original behavior case, not a valid gameplay lifetime claim. Initialized bounded mappings/UI services and nonnull camera for forced updates required. No new numeric allowances, fake game callee, full profile/startup or gameplay credit.'
finish('camera-viewport-v1',scope,{},extra)
(folder/'camera-viewport-v1-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n')
