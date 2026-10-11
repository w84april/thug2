"""Original model reset, geometry construction and model-path preparation."""
from pathlib import Path
source=Path('local/analysis/probe-model-initialize.py').read_text().split('for count,directional in')[0]
exec(compile(source,'<preserved model initialization fixture>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.coverage.clear()
specs=[(0x48dd60,23,'model_geometry_base_construct',0,'word',False,True),
 (0x48e130,26,'model_geometry_base_destroy',0,'void',True,True),
 (0x48e220,53,'model_geometry_base_delete',1,'word',True,True),
 (0x4b4460,111,'model_geometry_construct',0,'word',False,True),
 (0x4b2a20,86,'model_geometry_create',0,'word',True,False),
 (0x4ecc30,79,'model_list_erase',3,'void',True,True),
 (0x48c3c0,10,'model_geometry_release',1,'byte',True,False),
 (0x49efd0,55,'model_texture_release',1,'byte',True,False),
 (0x494ba0,151,'model_renderer_reset',0,'void',True,True),
 (0x492ee0,76,'model_renderer_scale',1,'byte',False,True),
 (0x476d50,67,'model_parameter_float',3,'byte',False,True),
 (0x487b00,200,'model_parse_scale',2,'byte',False,False),
 (0x402080,39,'model_path_lower',1,'void',False,False),
 (0x487a70,89,'model_path',3,'void',False,False)]
for a,n,name,argc,result,heap,this in specs:bind_new(a,n,'thug_'+name+'_draft',argc,result,heap,this=this)
exports.append([0x648ec8,'thug_model_geometry_base_methods_draft'])
for a in [0x48dd60,0x48e130,0x4b4460]:oracle.cpu.hook_add(UC_HOOK_CODE,identities,begin=a,end=a)
for off in range(0,24,4):glob('thug_model_texture_table_draft',0x700f04+off,0,offset=off)
class ConfigGraph(LightGraph):
 def base_geometry(self,key=0,refs=0,payload=False):
  at=self.alloc(32);self.put(at,'<5I',0x648ec8,key,refs,self.alloc(24) if payload else 0,0);fields.add(at);return at
 def parts(self,count,owned=False):
  if count is None:self.put(P+0x10,'<2I',0,0);return
  head=self.alloc(12);nodes=[self.alloc(12) for _ in range(count)];self.put(P+0x10,'<2I',head,count)
  self.put(head,'<3I',0,nodes[0] if nodes else head,nodes[-1] if nodes else head)
  texture=self.base_geometry(0x12345678,max(count,1),True)
  for i,node in enumerate(nodes):
   part=self.alloc(24);model=self.base_geometry(texture,0,True) if owned and i%2==0 else 0
   self.put(part,'<6I',self.base_geometry(payload=i%2==0),0,0,model,0,0)
   self.put(node,'<3I',part,nodes[i+1] if i+1<len(nodes) else head,nodes[i-1] if i else head)
  return head,nodes
def run(g,calls,label,changes=None,quiet_fields=()):
 try:stages=case(calls,g.patches(),changes,label)
 except Exception:print('FAILED configuration:',label,flush=True);raise
 for s in stages:
  if quiet_fields:s['quiet_float_fields']=list(quiet_fields)
 return stages
for fill in [0,0xa5,0xff]:
 for ctor in [0x48dd60,0x4b4460]:
  g=ConfigGraph();g.image[P-BASE:P-BASE+0x64]=bytes([fill])*0x64
  run(g,[call(ctor,P)]*2,f'geometry ctor{ctor:x}/poison{fill}')
for payload in [False,True]:
 for flags in [0,1,2,255,256,257,0xffffffff]:
  g=ConfigGraph();at=g.base_geometry(payload=payload)
  run(g,[call(0x48e220,at,[flags])],f'base geometry delete payload{payload}/flags{flags}')
 g=ConfigGraph();at=g.base_geometry(payload=payload)
 run(g,[call(0x48e130,at)],f'base geometry destructor payload{payload}')
 g=ConfigGraph();at=g.base_geometry(payload=payload)
 run(g,[call(0x48c3c0,args=[at]),call(0x48c3c0,args=[0])],f'actual virtual geometry disposal payload{payload}')
g=ConfigGraph();run(g,[call(0x4b2a20)]*2,'actual PC geometry zeroed factory')
for count in [0,1,4]:
 for first,last in [(0,count),(0,0),(count,count),(0,min(count,2))]:
  g=ConfigGraph();head,nodes=g.parts(count);seq=nodes+[head]
  run(g,[call(0x4ecc30,P+0x10,[P+0x300,seq[first],seq[last]])],f'list erase {count}/{first}:{last}')
g=ConfigGraph();head,nodes=g.parts(3)
run(g,[call(0x4ecc30,P+0x10,[P+0x300,head,nodes[1]])],'list range traverses sentinel without deleting it')
g=ConfigGraph();g.parts(None);run(g,[call(0x4ecc30,P+0x10,[P+0x300,0,0])],'null empty list range')
for count in [0,1,2,65535]:
 for shape in ['absent','missing','head','collision']:
  g=ConfigGraph();at=g.base_geometry(7,count,True)
  t=g.table([] if shape=='missing' else [(7,at)] if shape=='head' else [(3,at),(7,at)])
  changes={0x700f04+i*4:g.word(t+i*4) for i in range(6)}
  if shape=='absent':changes[0x700f08]=0
  run(g,[call(0x49efd0,args=[at])],f'texture ref{count}/{shape}',changes)
for count in [None,0,1,3]:
 for owned in [False,True]:
  g=ConfigGraph();g.parts(count,owned);g.put(P+0x44,'<2I',0x12345678,0x9abcdef0)
  run(g,[call(0x494ba0,P)]*2,f'reset parts{count}/owned{owned}')
for source_offset in [-4,0,4,8,12,16,20]:
 for values in [(0x3f800000,)*4,(0x3f800000,0x3f800000,0x3f800000,0xffffffff),(0x7f812345,0x80000000,0,1),(1,2,3,4)]:
  g=ConfigGraph();at=P+0x1c+source_offset;g.put(at,'<4I',*values);g.put(P+0x44,'<I',0xabcdefa5)
  run(g,[call(0x492ee0,P,[at])]*2,f'scale raw copy/overlap{source_offset}/{values}')
special=[0,0x80000000,1,0x7f7fffff,0xff7fffff,0x3f800000,0x7f800000,0xff800000,0x7fc12345,0x7f812345]
for value in special:
 for kind in [1,2,13]:
  g=ConfigGraph();v=value
  if kind==13:g.symbol(0x12345678,2,value);v=0x12345678
  s=g.structure([(0x13b9da7b,kind,v)])
  run(g,[call(0x487b00,args=[P,s])],f'uniform Scale kind{kind}/{value:x}',quiet_fields=[P])
  run(g,[call(0x476d50,s,[0x13b9da7b,P,1])],f'quiet scalar getter kind{kind}/{value:x}',quiet_fields=[P])
for required in [0,1,256,257]:
 g=ConfigGraph();s=g.structure([]);run(g,[call(0x476d50,s,[0x1234,P,required])],f'quiet scalar missing required{required}')
for mask in range(8):
 for prefix in ['none','flag','wrong','vector']:
  g=ConfigGraph();items=[]
  if prefix=='flag':items=[(0,13,0x13b9da7b)]
  if prefix=='wrong':items=[(0x13b9da7b,3,g.text('wrong'))]
  if prefix=='vector':items=[(0x13b9da7b,6,g.vector([0x40000000,0x40400000,0x40800000]))]
  items += [(key,2,value) for i,(key,value) in enumerate(zip([0x7323e97c,0x0424d9ea,0x9d2d8850],[0x80000000,0x40200000,0x7f812345])) if mask&(1<<i)]
  s=g.structure(items);run(g,[call(0x487b00,args=[P,s])],f'axis fallback mask{mask}/{prefix}',quiet_fields=([P+4,P+8] if prefix=='vector' else [P+i*4 for i in range(3) if mask&(1<<i)]))
for name in ['', 'Letter_S', 'gameobjects/skate/letter_s/letter_s.mdl','gameobjects\\SKATE\\S','a/b\\c','/', '\\','a'*180,'A\xffZ']:
 for extension in ['.mdl','.skin','']:
  g=ConfigGraph();n=g.text(name);e=g.text(extension)
  run(g,[call(0x487a70,args=[n,e,P]),call(0x402080,args=[P])],f'original model path {name!r}/{extension}')
g=ConfigGraph();at=g.text(''.join(chr(i) for i in range(1,256)))
run(g,[call(0x402080,args=[at])]*2,'lowercase all nonzero byte values')
g=ConfigGraph();at=g.text('');run(g,[call(0x402080,args=[at])],'empty path lower')
missing={hex(a):[hex(i.address) for i in code if not hits[i.address]] for a,code in coverage.items()}
print('MISSING',json.dumps(missing),flush=True)
excluded={hex(a):'successful geometry allocation contract' for a in [0x4b2a65,0x4b2a69,0x4b2a6b,0x4b2a72,0x4b2a75]}
scope='Fourteen original dependencies recover base and PC geometry construction, base geometry ownership and deletion, list range erasure, renderer reset with virtual object/texture release,16-bit texture references, scale parsing and exact flags, quieting float getter, ASCII lowercase and original model-path formatting. Reset fixtures use real base geometry destructors as concrete virtual objects; PC mesh destruction and loading remain unavailable. Real script lookups, table removal, bounds initializer and original CRT formatting execute. Full arena/globals/heap and preserved registers compare; only specified FLD/FSTP output quiet bits are normalized with sign/payload retained. Successful allocation, initialized services and bounded non-overlapping formatting buffers are contracts. Model configuration remains partial; no loaded/rendered model or playable level is claimed.'
finish('model-configuration',scope,excluded,extra)
