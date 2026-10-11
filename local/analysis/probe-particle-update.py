"""Original camera/culling and particle ownership prerequisites for full frames."""
from pathlib import Path
exec(compile(Path('local/analysis/probe-particle-setup.py').read_text().split('for fn in [0x497790')[0],'<preserved particle setup>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
for a,n,name,argc,result,heap,diag,this in [
 (0x4a06d0,49,'particle_viewport',1,'word',False,False,False),(0x4a09c0,17,'particle_camera',1,'word',False,False,False),
 (0x496b40,230,'particle_distance_count',1,'word',False,False,True),
 (0x5e1616,212,'particle_vector3_transform_sse',3,'word',False,False,False),(0x5bf19f,6,'particle_vector3_transform_entry',3,'word',False,False,False),
 (0x4db570,168,'particle_sphere_culled_pc',2,'word',False,False,False),(0x4b2310,5,'particle_sphere_culled_forward',2,'word',False,False,False),(0x48c490,17,'particle_sphere_culled',2,'word',False,False,False),
 (0x4d2bd0,211,'particle_material_data_destroy',0,'void',True,False,True),(0x4d9cd0,28,'particle_material_destroy',0,'void',True,False,True),
 (0x49ad60,38,'particle_manager_unlink',1,'void',False,False,True),(0x498690,339,'particle_destroy',0,'void',True,True,True),
 (0x49b600,18,'particle_buffer_destroy',0,'void',True,True,True),(0x4c2260,112,'particle_point_destroy',0,'void',True,True,True),
 (0x4c2af0,33,'particle_point_delete',1,'word',True,True,True),(0x49b630,33,'particle_buffer_delete',1,'word',True,True,True),
 (0x49ad90,31,'particle_manager_delete',1,'void',True,True,True),(0x49adb0,34,'particle_manager_expire',1,'void',False,False,True)]:bind_new(a,n,'thug_'+name+'_draft',argc,result,heap,diag,this)
for a in [0x5e1616,0x5bf19f]:functions[hex(a)]['cleanup']=12
for a in [0x4db570,0x4b2310,0x48c490]:functions[hex(a)]['float_args']=[1]
for a,name,argc in [(0x4c21a0,'particle_point_construct',5),(0x49b660,'particle_buffer_construct',8)]:bind(a,'thug_'+name+'_draft',argc,'word',True)
for a,name in [(0x497790,'particle_setup_script'),(0x497900,'particle_update_script')]:bind(a,'thug_'+name+'_draft',3,'void',True,True)
bind(0x41d1d0,'thug_object_reference_assign',1,'void')
exports.append([0x649420,'thug_particle_unlinked_node_methods_draft'])
function_exports.append([0x5e1616,'thug_particle_vector3_transform_sse_draft'])
glob('thug_particle_vector3_transform_draft',0x684fdc,0x5e1616)
extra['pointer_globals']=[index[0x684fdc]]
glob('thug_particle_viewport_count_draft',0x701378,1);glob('thug_viewport_mapping',0x67e540,P+0x500)
for i in range(10):glob('thug_viewports',0x701350+i*4,P+0x600+i*32,offset=i*4)
for i in range(16):glob('thug_particle_view_matrix_draft',0x786bd0+i*4,bits(1 if i%5==0 else 0),offset=i*4)
glob('thug_particle_view_near_draft',0x786ca8,bits(1))
for i,v in enumerate([-.7,-.6,.8,.9]):glob('thug_particle_view_planes_draft',0x786e20+i*4,bits(v),offset=i*4)
initial=bytes(memory);oracle.initial=initial
class UpdateGraph(SetupGraph):
 def __init__(self):
  super().__init__();self.image[P-BASE:P-BASE+0x138]=bytes(0x138)
  self.put(P+12,'<5I',0x649424,P,0,P+12,P+12);fields.add(P+12)
  self.put(P+0x500,'<10i',0,-1,2,3,-1,5,6,-1,8,9)
  for i in range(10):self.put(P+0x600+i*32+24,'<I',P+0xa00+i*0x100);self.put(P+0xa00+i*0x100+0x5c,'<4f',1,2,3,1)
  self.put(P+0x20,'<4f',3,5,7,1);self.put(P+0x7c,'<I',100);self.put(P+0x80,'<I',10);self.put(P+0x84,'<2f',9,49)
 def constructor(self,point=True):
  self.texture('direct');return call(0x4c21a0 if point else 0x49b660,P,[0x11223344,7,0xe9d12353,0x02e58c18,128] if point else [0x11223344,7,0,0,0,0,0,0])
 def link(self):
  self.put(P+12,'<5I',0x649424,P,0,LIST,LIST);self.put(LIST+12,'<2I',P+12,P+12)
 def material(self,mask=255,count=3):
  p=self.alloc(0x110);self.image[p-BASE:p-BASE+0x110]=bytes(0x110)
  if mask&1:
   a=self.alloc(max(12,12*count));self.put(p+0xf0,'<2I',count,a)
   for i in range(count):self.put(a+i*12+8,'<I',0 if i==1 else self.alloc(16))
  if mask&2:self.put(p+0xf8,'<I',self.alloc(16))
  for i in range(4):
   if mask&(4<<i):self.put(p+0xd0+i*4,'<I',self.alloc(16))
  if mask&64:
   a=self.alloc(0x44);self.put(p+0xfc,'<I',a)
   for i in range(4):self.put(a+0x34+i*4,'<I',0 if i==2 else self.alloc(16))
  return p
def run(g,calls,label,changes=None):
 try:result=case(calls,g.patches(),changes,label)
 except Exception:print('FAILED',label,flush=True);raise
 if len(labels)%25==0:print('Original update prerequisites',len(labels),flush=True)
 return result
for mapping in [[-1]*10,list(range(10)),[0,-1,2,3,-1,5,6,-1,8,9],[2,2,2,-2,-1,9,-1,-1,-1,-1]]:
 for index_ in [0,1,3,6,9,10,0xffffffff]:
  g=UpdateGraph();g.put(P+0x500,'<10i',*mapping);calls=[call(0x4a06d0,args=[index_])]
  if index_<len([x for x in mapping if x>=0]):calls.append(call(0x4a09c0,args=[index_]))
  run(g,calls,f'viewport/{mapping}/{index_}')
for count in [0,7,60,200,0xffffffff]:
 for near,far in [(0,0),(49,9),(9,49),(-4,49)]:
  for x in [0,2,3,4,7,8,1e20]:
   g=UpdateGraph();g.put(P+0x20,'<3f',1+x,2,3);g.put(P+0x84,'<2f',near,far)
   run(g,[call(0x496b40,P,[count])],f'distance/{count}/{near}/{far}/{x}')
for players in [0,1,2,0xffffffff,0x80000000]:
 for minimum in [0,100,0x7fffffff,0x80000000,0xffffffff]:
  g=UpdateGraph();g.put(P+0x80,'<I',minimum);run(g,[call(0x496b40,P,[25])],f'distance-signed/{players}/{minimum}',{0x701378:players})
g=UpdateGraph();g.put(P+0x600+24,'<I',0);run(g,[call(0x496b40,P,[17])],'null camera')
# Snapshot behavior, unaligned matrices and output aliases for actual SSE.
for alignment in [0,4,8,12]:
 for alias in ['distinct','input','input+4','matrix','matrix+4']:
  for scale in [1.,1e-15,1e15]:
   g=UpdateGraph();matrix=(g.alloc(96)+15)&~15;matrix+=alignment;inp=g.alloc(32);out=g.alloc(16)
   g.put(matrix,'<16f',*[(i/7-1)*scale for i in range(16)]);g.put(inp,'<4f',.2,-.3,.7,8)
   out={'distinct':out,'input':inp,'input+4':inp+4,'matrix':matrix,'matrix+4':matrix+4}[alias]
   run(g,[call(0x5e1616,args=[out,inp,matrix])],f'vector/{alignment}/{alias}/{scale}')
g=UpdateGraph();m=g.alloc(64);v=g.alloc(16);out=g.alloc(16);g.put(m,'<16f',*[1 if i%5==0 else 0 for i in range(16)]);g.put(v,'<4f',2,3,4,9)
run(g,[call(0x5bf19f,args=[out,v,m])],'actual initialized D3DX dispatch')
for xyz in [(0,0,-10),(0,0,0),(0,0,10),(-20,0,10),(20,0,10),(0,20,10),(0,-20,10),(.2,-.3,.5)]:
 for radius in [-1.,0.,1.,5.,20.]:
  for players in [1,2]:
   g=UpdateGraph();g.put(P+0x200,'<4f',*xyz,7)
   run(g,[call(a,args=[P+0x200,bits(radius)]) for a in [0x4db570,0x4b2310,0x48c490]],f'cull/{xyz}/{radius}/{players}',{0x701378:players})
for mask in [0,1,2,4,8,16,32,64,127]:
 for count in [0,1,3]:
  g=UpdateGraph();p=g.material(mask,count);wrapper=g.alloc(8);g.put(wrapper,'<I',p)
  run(g,[call(0x4d9cd0,wrapper)],f'material/{mask}/{count}')
g=UpdateGraph();p=g.alloc(8);g.put(p,'<I',0);run(g,[call(0x4d9cd0,p)],'material null')
g=UpdateGraph();p=g.material();run(g,[call(0x4d2bd0,p)],'direct material destruction')
for linked in [False,True]:
 g=UpdateGraph()
 if linked:g.link()
 run(g,[call(0x49ad60,PM,[0]),call(0x49ad60,PM,[P])]*2,f'unlink/{linked}')
# Every owned particle resource presence; no fake script destructor.
for mask in range(32):
 g=UpdateGraph();g.link()
 for i,o in enumerate([0x10c,0x110,0x114,0x11c,0xf8]):
  if mask&(1<<i):
   a=g.alloc(160);g.put(a,'<I',3);g.put(P+o,'<I',a+4 if o==0xf8 else a)
 run(g,[call(0x498690,P)],f'owned arrays/{mask}')
for point in [False,True]:
 for flags in [0,1,2,3,255,256,257,0xffffffff]:
  g=UpdateGraph();run(g,[g.constructor(point),call(0x4c2af0 if point else 0x49b630,P,[flags])],f'delete/{point}/{flags}')
for fn in [0x49b600,0x4c2260]:
 g=UpdateGraph();run(g,[g.constructor(fn==0x4c2260),call(fn,P)],f'direct destroy/{fn:x}')
for slots in [0,1,2,3]:
 for owner in [0,OBJ]:
  g=UpdateGraph();g.programs();args=g.structure([(0x123,1,17)]);calls=[g.constructor(True)]
  if slots&1:calls.append(call(0x497790,P,[0xcd1e6836,args,owner]))
  if slots&2:calls.append(call(0x497900,P,[0x11223344,args,owner]))
  reference=g.alloc(12);g.put(reference,'<3I',0,0,0);calls.append(call(0x41d1d0,reference,[P]));calls.append(call(0x4c2af0,P,[1]))
  run(g,calls,f'scripts refs/{slots}/{owner}')
for found in [False,True]:
 for point in [False,True]:
  g=UpdateGraph();calls=[g.constructor(point)];g.put(LIST+12,'<2I',P+12,P+12)
  # Constructor leaves its node self-linked; manager sees that node first.
  # Deletion unlinks the self-node and clears references without a list stub.
  name=0x11223344 if found else 0x88776655
  if not found:g.put(PM+20,'<I',0)
  calls += [call(0x49adb0,PM,[name]),call(0x49ad90,PM,[name])]
  run(g,calls,f'manager/{found}/{point}')
missing={hex(a):[hex(i.address) for i in code if not hits[i.address]] for a,code in coverage.items()};print('MISSING',json.dumps(missing),flush=True)
scope='Complete camera active-slot lookup, camera accessor, distance emission limit, selected original SSE vector transform and dispatch, sphere culling and wrappers, particle/material ownership teardown and manager deletion/expiry. Actual original script destruction, reference unlinking, list removal and heap calls execute. Finite arithmetic, initialized SSE dispatch and valid bounded internal graphs; whole arena/globals/returns and heap effects compare. These are full frame prerequisites, not a completed engine frame or playable game.'
finish('particle-update',scope,{},extra)
