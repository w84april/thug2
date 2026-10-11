"""Original retained particle scripts and full FlexParticle initializer."""
from pathlib import Path
source=Path('local/analysis/probe-particle-create.py').read_text().split('for fill in [0,0xa5,0xff]:')[0]
exec(compile(source,'<preserved initialized particle and script services>','exec'))
coverage.clear();hits.clear();oracle.counts.clear();labels.clear()
for a,n,name,argc in [(0x497790,363,'particle_setup_script',3),(0x497900,363,'particle_update_script',3),(0x41db00,1138,'flexparticle_setup_initialize',1)]:
 bind_new(a,n,'thug_'+name+'_draft',argc,'void',True,True)
bind(0x41da00,'thug_flexparticle_construct_draft',0,'word')
bind(0x41d1d0,'thug_object_reference_assign',1,'void')
bind(0x461a00,'thug_object_manager_add',1,heap=True)
exports.append([0x645fe4,'thug_flexparticle_methods_draft'])
global_default('thug_cutscene_context_draft',0x6fa7c0,PM)
glob('thug_particle_parameter_scale_draft',0x67d6d0,0xdeadbeef)
for name,at in [('thug_script_structure_pool_index',0x6f3614),('thug_script_structure_pools',0x6f361c),('thug_script_structure_pools',0x6f3620)]:
 if at not in index:glob(name,at,0,offset=4 if at==0x6f3620 else 0)
COMP=P+0x800
initial=bytes(memory);oracle.initial=initial
class SetupGraph(ParticleGraph):
 def __init__(self):
  super().__init__();self.image[P-BASE:P-BASE+0x138]=bytes([0xa5])*0x138
  self.put(P+0xfc,'<3I',0,0,0);self.put(COMP+12,'<I',OBJ)
  self.symbol(0x0cf3cba1,1,60)
 def programs(self):
  entries=[]
  for key in [0xcd1e6836,0x11223344]:
   body=self.alloc(16);self.image[body-BASE:body-BASE+2]=b'\x01\x24'
   entry=self.alloc(20);self.put(entry,'<5I',key,body,0,0,0);entries.append((key,entry))
  self.put(CACHE+20,'<I',self.table(entries))
 def pool(self,size,count):
  p=self.alloc(92);data=self.alloc(size*count);self.put(p,'<6I',data,data+size*count,0,0,0,data);self.put(p+88,'<I',0)
  for i in range(count):self.put(data+i*size,'<I',data+(i+1)*size if i+1<count else 0)
  return p
 def reusable(self,flags=0xa5a50005):
  self.put(P,'<3I',0x649428,0,0);self.put(P+12,'<5I',0x649424,P,0,LIST,LIST)
  self.put(P+0xf0,'<I',0x55667788);self.put(P+0x120,'<I',flags)
  self.put(LIST+12,'<2I',P+12,P+12);fields.update([P,P+12])
 def init(self,items=(),reuse=True,twice=True):
  self.put(COMP+12,'<I',OBJ)
  defaults_=[(0xa1dc81f9,13,0x55667788),(0x7321a8d6,13,0xf4d8d486),(0xd5928f25,1,int(reuse))]
  s=self.structure(defaults_+list(items));return [call(0x41da00,COMP)]+[call(0x41db00,COMP,[s])]*(2 if twice else 1)
def check_setup(g,calls,label,changes=None):
 try:
  result=case(calls,g.patches(),changes,label)
  if len(labels)%25==0:print('Original particle setup',len(labels),flush=True)
  return result
 except Exception:print('FAILED',label,flush=True);raise
# Exercise creation/reuse, retained and merged parameters, owner references,
# empty clears, script replacement, selected pools and the two shared slots.
for fn in [0x497790,0x497900]:
 for pooled in [False,True]:
  for owner in [0,OBJ]:
   for mode in ['null','empty','values','missing-program']:
    g=SetupGraph();g.programs();args=0 if mode=='null' else g.structure([] if mode=='empty' else [(0x111,1,7),(0x222,13,0x98765432)])
    update=g.structure([(0x111,1,9),(0x333,2,bits(-2.5))]);changes={}
    if pooled:
     changes[0x6f3550]=g.pool(256,4);changes[0x6f361c]=g.pool(16,40)
    key=0x87654321 if mode=='missing-program' else 0xcd1e6836
    calls_=[call(fn,P,[0,0,0]),call(fn,P,[key,args,owner]),call(fn,P,[0x11223344,update,owner]),call(fn,P,[0,args,owner]),call(fn,P,[0,0,0])]
    check_setup(g,calls_,f'script/{fn:x}/{pooled}/{owner}/{mode}',changes)
g=SetupGraph();g.programs();a=g.structure([(1,1,3)]);b=g.structure([(2,2,bits(1.5))])
check_setup(g,[call(0x497790,P,[0xcd1e6836,a,OBJ]),call(0x497900,P,[0x11223344,b,OBJ]),call(0x497790,P,[0,0,0]),call(0x497900,P,[0,0,0])],'two slots share parameters')
for flag in [None,0xa2487cc3,0xbbfa4b06,0x47580c70,0x5446af14,0x9b9381e2,0xde45a90d,'all']:
 g=SetupGraph();g.reusable();keys=[0xa2487cc3,0xbbfa4b06,0x47580c70,0x5446af14,0x9b9381e2,0xde45a90d] if flag=='all' else [] if flag is None else [flag]
 check_setup(g,g.init([(0,13,k) for k in keys]),f'initializer-flag/{flag}')
for count in [0,1,0x7fffffff,0x80000000,0xffffffff]:
 for value in [0,1,255,256,0xffffffff]:
  g=SetupGraph();g.reusable();check_setup(g,g.init([(0x03d4e483,1,count),(0x9d5923d8,1,value)]),f'initializer-bytes/{count:x}/{value:x}')
for raw in [0,0x80000000,1,0x7f812345,0xffc12345,0x7f800000,bits(-3.5)]:
 g=SetupGraph();g.reusable();v=g.vector([raw,raw^0x80000000,0x3f800000])
 stages=check_setup(g,g.init([(0x8e9a640e,2,raw),(0xe4247a6b,6,v),(0x87fa53ed,13,0x12345678)]),f'initializer-raw-vector/{raw:x}')
 # 476fce/476fd4 FLD and476fdb/476fe7 FSTP quiet only Y/Z signaling NaNs.
 # Unicorn preserves that bit; require the physical x87 result, all other bits exact.
 for stage in stages[1:]:stage['quiet_float_fields']=[P+0x44,P+0x48]
for scale in [0,1,0x7fffffff,0x80000000,0xffffffff,0x01000001]:
 g=SetupGraph();g.reusable();g.symbol(0x0cf3cba1,1,scale);check_setup(g,g.init(),f'global-signed-scale/{scale:x}')
for setup,update in [(None,None),(0,None),(0xcd1e6836,None),(None,0x11223344),(0xcd1e6836,0x11223344)]:
 for params in [False,True]:
  g=SetupGraph();g.reusable();g.programs();items=[]
  for k,v in [(0xfc57577f,setup),(0x092276db,update)]:
   if v is not None:items.append((k,13,v))
  if params:items.append((0x7031f10c,10,g.structure([(0x123,1,17)])))
  check_setup(g,g.init(items),f'initializer-scripts/{setup}/{update}/{params}')
# Original global-object lookup and component lookup for nonzero attachment IDs.
for explicit in [False,True]:
 for component_present in [False,True]:
  g=SetupGraph();g.reusable();g.put(OBJ+0x100,'<I',g.component(0x286a8d26 if component_present else 123))
  target=0x100;items=[(0,13,0xbbfa4b06),(0x184197d5,13,0x101 if explicit else target)]
  if explicit:items.append((0x0830ecaf,13,target))
  calls_=[call(0x461a00,MANAGER,[OBJ])]+g.init(items)
  check_setup(g,calls_,f'initializer-attachment/{explicit}/{component_present}')
# Misses create the same point class as the training barrel. Repeated initialization
# covers unlinking an existing component reference and reuse lookup misses.
for reuse in [False,True]:
 for capacity in [0,1,70]:
  g=SetupGraph();g.texture('direct');check_setup(g,g.init([(0x6289dd76,2,bits(capacity))],reuse=reuse),f'initializer-create/{reuse}/{capacity}')
missing={hex(a):[hex(i.address) for i in code if not hits[i.address]] for a,code in coverage.items()};print('MISSING',json.dumps(missing),flush=True)
excluded={**{hex(a):'initialized allocator; cold bootstrap excluded' for a in [0x4977e3,0x49784c,0x497953,0x4979bc]},**{hex(a):'successful initialized allocation contract; failure branches retained but unverified' for a in [0x497815,0x49787b,0x497985,0x4979eb]}}
scope='Retained particle setup/update scripts and complete FlexParticle initializer control flow, using original script allocation, persistent parameter merging, setup, cleanup and reference ownership. Actual point-sprite creation and reused live effects, parameter flags/bytes/raw vectors, signed global conversion, attached-model lookup and selected script/structure pools. Only vector Y/Z FLD/FSTP results require exact x87 quiet-bit normalization for Unicorn signaling NaNs; no NaN classification relaxation. Initialized services, successful allocations and valid graphs; other particle class factories remain unavailable. No particle script execution, full game frame, drawing or playability claimed.'
finish('particle-setup',scope,excluded,extra)
