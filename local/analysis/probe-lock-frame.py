"""Original full attachment update and bone/matrix dependencies."""
from pathlib import Path
exec(compile(Path('local/analysis/probe-prop-lifecycle.py').read_text().split('# Constructor/reset fields')[0],'<preserved prop services>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
for a,n,name,argc,result in [(0x404100,26,'lock_matrix_pair',1,'word'),(0x4a2b60,36,'lock_bone_index',1,'word'),
 (0x4a2c50,14,'lock_bone_parent',1,'word'),(0x4a36e0,388,'lock_bone_matrix',2,'byte'),
 (0x41f760,1973,'lock_update',0,'void'),(0x41ff90,15,'lock_update_enabled',0,'void')]:
 bind_new(a,n,'thug_'+name+'_draft',argc,result)
bind(0x461a00,'thug_object_manager_add',1,heap=True)
for name,at,value in [('thug_frame_counter',0x7d1ec8,60),('thug_frame_rate',0x684fd0,bits(60)),
 ('thug_frame_length_scale',0x684fc8,bits(1)),('thug_timer_origin',0x696d64,0),
 ('thug_timer_offset',0x696d60,0),('thug_time_scale',0x67d7c0,bits(1))]:global_default(name,at,value)
initial=bytes(memory);oracle.initial=initial
IDENTITY=[1.,0.,0.,0.,0.,1.,0.,0.,0.,0.,1.,0.,0.,0.,0.,1.]
class LockGraph(PropGraph):
 def __init__(self,key=100,flags=4,model=None,bone='none',root=False):
  super().__init__();self.image[P-BASE:P-BASE+0x90]=bytes(0x90)
  self.put(P+12,'<I',OBJ);self.put(P+0x18,'<I',key);self.put(P+0x8c,'<I',flags)
  self.put(P+0x24,'<4f',.25,-.75,2,1);self.put(P+0x34,'<16f',*IDENTITY)
  self.put(P+0x74,'<5f',.25,.1,.9,1.5,2.25);self.put(P+0x88,'<I',29)
  self.put(OBJ+0x4c,'<4f',2,3,4,1);self.put(OBJ+0x6c,'<16f',*IDENTITY);self.put(OBJ+0xc0,'<16f',*([7.]*16))
  self.target=self.alloc(0x140);self.image[self.target-BASE:self.target-BASE+0x140]=bytes(0x140)
  self.put(self.target,'<I',0x647650);fields.add(self.target);self.put(self.target+0x14,'<I',key)
  self.put(self.target+0x4c,'<4f',10,-2,6,1);self.put(self.target+0xac,'<4f',.2,2,-.5,1)
  matrix=IDENTITY[:];matrix[0]=.8;matrix[2]=-.6;matrix[8]=.6;matrix[10]=.8
  self.put(self.target+0xc0,'<16f',*matrix);head=0
  self.model=0
  if model is not None:
   self.model=self.alloc(0x240);self.image[self.model-BASE:self.model-BASE+0x240]=bytes(0x240)
   self.put(self.model+4,'<I',0x286a8d26);self.put(self.model+12,'<I',self.target);self.put(self.model+0x234,'<B',model)
   self.put(self.model+0x1f8,'<4f',.7,-1.2,2.5,0);head=self.model
  self.skeleton=0;self.provider=0;self.names=[]
  if bone!='none':
   self.put(P+0x20,'<I',0x71231122)
   if bone!='missing-component':
    component=self.alloc(0x30);self.image[component-BASE:component-BASE+0x30]=bytes(0x30)
    self.put(component+4,'<I',0x222756d5);self.put(component+16,'<I',head);head=component
    if bone!='null-skeleton':
     self.skeleton=self.alloc(0x20);self.provider=self.alloc(0x600)
     self.image[self.skeleton-BASE:self.skeleton-BASE+0x20]=bytes(0x20)
     self.image[self.provider-BASE:self.provider-BASE+0x600]=bytes(0x600)
     self.names=[0x71231122,0x71231123]+([0x9f173eeb] if root else [])
     records=self.alloc(28*len(self.names));current=self.alloc(64*len(self.names));base=self.alloc(64*len(self.names))
     self.put(self.skeleton+4,'<2I',current,self.provider);self.put(self.skeleton+0x14,'<2I',len(self.names),records)
     self.put(self.provider+0x58c,'<I',base);self.put(component+0x18,'<I',self.skeleton)
     for i,name in enumerate(self.names):
      self.put(records+28*i,'<7I',name,0,0,0,0,0,0);self.put(self.provider+0x108+4*i,'<I',self.names[1])
      a=IDENTITY[:];a[12:15]=[i+.5,i*2-1,i-3.5];self.put(base+64*i,'<16f',*a)
      a=matrix[:];a[12:15]=[i+2.,i*3+4.,i*2-6.];self.put(current+64*i,'<16f',*a)
     if root:
      a=matrix[:];a[12:15]=[11.,12.,13.];self.put(base+128,'<16f',*a)
     if bone=='missing-bone':self.put(P+0x20,'<I',0x777)
  self.put(self.target+0x100,'<I',head)
 def registered(self):return [call(0x461a00,MANAGER,[self.target])]
def run_lock(g,calls,label,changes=None):
 try:result=case(calls,g.patches(),changes,label)
 except Exception:print('FAILED',label,flush=True);raise
 if len(labels)%25==0:print('Original lock cases',len(labels),flush=True)
 return result
# Matrix wrapper operands may alias the destination, or the pair itself.
for out_index in range(5):
 g=LockGraph();a=g.alloc(64);b=g.alloc(64);out=g.alloc(64);pair=g.alloc(64)
 g.put(a,'<16f',*[i/7-1 for i in range(16)]);g.put(b,'<16f',*[2-i/9 for i in range(16)]);g.put(pair,'<2I',a,b)
 out=[out,a,b,a+4,pair][out_index]
 run_lock(g,[call(0x404100,out,[pair])],f'matrix-pair/{out_index}')
for root in [False,True]:
 for key in [0x777,0x71231122,0x71231123,0x9f173eeb]:
  g=LockGraph(bone='valid',root=root);out=g.alloc(64)
  run_lock(g,[call(0x4a2b60,g.skeleton,[key]),call(0x4a36e0,g.skeleton,[key,out])],f'bone-matrix/{root}/{key:x}')
 for index_ in range(2+root):
  g=LockGraph(bone='valid',root=root);run_lock(g,[call(0x4a2c50,g.provider,[index_])],f'bone-parent/{root}/{index_}')
for count in [0,0xffffffff]:
 g=LockGraph(bone='valid');g.put(g.skeleton+0x14,'<I',count);out=g.alloc(64)
 run_lock(g,[call(0x4a2b60,g.skeleton,[0x71231122]),call(0x4a36e0,g.skeleton,[0x71231122,out])],f'empty-skeleton/{count}')
# Full attachment graph: every flag, optional model, player-ID transform branch,
# provider absence, valid bones, and special root orientation handling.
for flags in range(8):
 for model in [None,0,1]:
  for bone in ['none','missing-component','null-skeleton','missing-bone','valid']:
   for key in [3,100]:
    g=LockGraph(key,flags,model,bone,root=bool(flags&2))
    run_lock(g,g.registered()+[call(0x41ff90,P)]*2+[call(0x41f760,P)],f'attachment/{flags}/{model}/{bone}/{key}')
for select in ['absent','override','fallback','same-owner']:
 g=LockGraph()
 if select=='absent':calls=[]
 else:calls=g.registered()
 if select=='override':g.put(P+0x1c,'<I',100);g.put(P+0x18,'<I',200)
 if select=='fallback':g.put(P+0x1c,'<I',200)
 if select=='same-owner':g.put(P+12,'<I',g.target)
 run_lock(g,calls+[call(0x41f760,P)]*3,f'target-selection/{select}')
# Nontrivial extra matrices, interpolation extremes, wrapped timing, and model
# transform channels exercise real existing dependencies within the update.
for bone in ['none','valid']:
 for factor in [0.,1.,-.5,2.,.123456789]:
  for frame in [0,1,0xffffffff]:
   g=LockGraph(100,7,1,bone,True);g.put(P+0x74,'<f',factor);g.put(P+0x88,'<I',0xfffffffe)
   a=IDENTITY[:];a[0]=a[10]=.6;a[2]=.8;a[8]=-.8;g.put(P+0x34,'<16f',*a)
   g.put(g.model+0x1f4,'<B',1);g.put(g.model+0x28,'<4f',1,2,3,1)
   g.put(g.model+0x38,'<4f',10000,0,30,0);g.put(g.model+0x4c,'<B',5);g.put(g.model+0xc8,'<B',1)
   run_lock(g,g.registered()+[call(0x41ff90,P)]*3,f'smoothing/{bone}/{factor}/{frame}',{0x7d1ec8:frame})
missing={hex(a):[hex(i.address) for i in code if not hits[i.address]] for a,code in coverage.items()};print('MISSING',json.dumps(missing),flush=True)
excluded={'0x41fe2d':'unreachable signed-negative timer correction after masking to 0..1023'}
scope='Six complete attachment/bone/matrix control flows. Real registry lookup, component lookup, model transforms, skeleton bind/current matrices, selected SSE multiplication and PC24 vector arithmetic execute. All attachment flag combinations, missing targets/providers/bones, both transformed-object branches, special root, smoothing, wrapping timers and extra orientation compare over entire arena/globals/returns/preserved registers. Valid skeleton indices and resolvable parent bone are required; the original otherwise reads an uninitialized parent matrix. Existing platform FSIN adapter and finite inputs; no numerical masks. No full game frame or playability claimed.'
finish('lock-frame',scope,excluded,extra)
