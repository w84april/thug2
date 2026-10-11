"""Particle script dependencies, including complete nested object-ID lookup."""
from pathlib import Path
source=Path('local/analysis/probe-prop-lifecycle.py').read_text().split('# Constructor/reset fields')[0]
exec(compile(source,'<preserved prop and registry services>','exec'))
functions.clear();coverage.clear();hits.clear();oracle.counts.clear();labels.clear()
specs=[(0x44a380,244,'script_global_exists',2,'byte',False,False,False),
 (0x44be40,127,'script_mangle_checksums',2,'byte',True,False,False),
 (0x44a940,106,'script_structure_contains',2,'byte',False,False,False),
 (0x49a8e0,11,'cutscene_destroy_list_active',0,'word',False,False,True),
 (0x5ae000,11,'script_cutscene_destroy_list_active',2,'word',False,False,False),
 (0x4607e0,32,'ui_object_get_checksum',2,'byte',False,False,True),
 (0x4aa2a0,235,'ui_child',3,'word',False,False,True),
 (0x4aa6d0,50,'ui_child_at',1,'word',False,False,True),
 (0x4ab130,279,'ui_child_named',3,'word',False,False,True),
 (0x462190,61,'object_find_alias',1,'word',False,False,True),
 (0x4ac120,724,'ui_resolve_id',3,'byte',False,False,True),
 (0x462340,64,'script_object_exists',2,'word',False,False,False),
 (0x460940,26,'object_get_id_command',2,'byte',True,False,True),
 (0x449540,92,'script_create_composite',2,'byte',True,True,False)]
for a,n,name,argc,result,heap,diag,this in specs:bind_new(a,n,'thug_'+name+'_draft',argc,result,heap,diag,this)
bind(0x416dd0,'thug_object_reference_destroy',0)
UI=BASE+0xc2000;CUT=BASE+0xc3000
global_default('thug_ui_manager',0x701440,UI);glob('thug_cutscene_context_draft',0x6fa7c0,CUT)
class ParticleGraph(PropGraph):
 def __init__(self):
  super().__init__();self.image[UI-BASE:UI-BASE+0x6a4]=bytes(0x6a4);self.image[CUT-BASE:CUT-BASE+0x100]=bytes(0x100)
  self.image[SCRIPTS-BASE:SCRIPTS-BASE+244]=bytes(244);self.put(SCRIPTS+0x14,'<I',self.structure([]))
 def element(self,name=0,local=None):
  o=self.alloc(0x1b0);self.image[o-BASE:o-BASE+0x1b0]=bytes(0x1b0);self.put(o+0x14,'<I',name)
  if local is not None:self.put(o+0x20,'<I',self.structure([(0x9494a525,13,local)]))
  return o
 def ref(self,r,o):
  previous=self.word(o+4) if o else 0;self.put(r,'<3I',o,0,previous)
  if o:
   if previous:self.put(previous+4,'<I',r)
   self.put(o+4,'<I',r)
 def children(self,parent,children):
  self.ref(parent+0x58,children[0] if children else 0)
  for i,o in enumerate(children):self.ref(o+0x64,children[i+1] if i+1<len(children) else 0)
 def graph(self):
  parent=self.element(0x1234);children=[self.element(0x2000+i,None if i==0 else 0x3000+i) for i in range(4)]
  self.children(parent,children);return parent,children
 def tables(self,primary=(),secondary=()):self.put(EM+8,'<2I',self.table(primary),self.table(secondary))
def check(g,calls,label):
 try:return case(calls,g.patches(),label=label)
 except Exception:print('FAILED',label,flush=True);raise
types={0x21902065:13,0xa1dc81f9:13,0x456d28d1:10,0x90fec815:10,0xa5f054f4:1,0xebae254e:1,0x365aa16a:2,0x5ef31148:12,0x61414d56:3,0xe491b7a4:6,0xf6a5e196:5,0:0,0xdeadbeef:0}
for kind,expected in types.items():
 for stored in [None,expected,(expected+1)&255,255]:
  g=ParticleGraph();s=g.structure([(0xa1dc81f9,13,0x1234),(0x7321a8d6,13,kind)])
  if stored is not None:g.symbol(0x1234,stored,0x9876)
  check(g,[call(0x44a380,args=[s,0])],f'global/type{kind:x}/stored{stored}')
g=ParticleGraph();g.symbol(0,0,0);check(g,[call(0x44a380,args=[g.structure([]),0])],'global-omitted-defaults')
for ka,kb in [(1,1),(1,13),(13,1),(13,13)]:
 for a,b in [(0,0),(1,2),(0xffffffff,1),(0x80000000,0x80000000),(0xfffffffe,0x87654321)]:
  g=ParticleGraph();s=g.structure([(0x174841bc,ka,a),(0x8e411006,kb,b)])
  check(g,[call(0x44be40,args=[s,SCRIPTS])]*2,f'mangle{ka}/{kb}/{a:x}/{b:x}')
for kind in ['missing','empty','named','flag','inclusion','different','unnamed-default']:
 g=ParticleGraph();items=[]
 if kind!='missing':
  target=[]
  if kind=='named':target=[(123,1,9)]
  if kind=='flag':target=[(0,13,123)]
  if kind=='inclusion':g.symbol(0x3456,10,g.structure([(0,13,123)]));target=[(0,13,0x3456)]
  if kind=='different':target=[(124,1,9)]
  if kind=='unnamed-default':target=[(0,1,9)]
  items=[(0x90fec815,10,g.structure(target))]
 if kind!='unnamed-default':items.append((0,13,123))
 check(g,[call(0x44a940,args=[g.structure(items),0])],f'structure-contains/{kind}')
for value in [0,1,0xffffffff,0x80000000]:
 g=ParticleGraph();g.put(CUT+0x10,'<I',value)
 check(g,[call(0x49a8e0,CUT),call(0x5ae000,args=[0,0])],f'cutscene-list{value:x}')
for parameter in [None,[],[(123,13,456)],[(123,1,456)],[(0,13,123)]]:
 g=ParticleGraph();o=g.element();out=g.alloc(4);g.put(out,'<I',0xabababab)
 if parameter is not None:g.put(o+0x20,'<I',g.structure(parameter))
 check(g,[call(0x4607e0,o,[123,out])],f'object-checksum/{parameter}')
for count in [0,1,4]:
 for name,index_value,has_index in [(0,0,True),(0,3,True),(0,4,True),(0,0xffffffff,True),(0x2000,99,False),(0x2003,99,True),(0x9999,99,True)]:
  g=ParticleGraph();parent=g.element();children=[g.element(0x2000+i) for i in range(count)];g.children(parent,children)
  out=g.alloc(12);idx=g.alloc(4);g.put(idx,'<I',index_value)
  check(g,[call(0x4aa2a0,parent,[out,name,idx if has_index else 0]),call(0x416dd0,out)],f'child/count{count}/name{name:x}/index{index_value}/{has_index}')
for index_value in [0,1,3,4,0xffffffff]:
 g=ParticleGraph();parent,children=g.graph();check(g,[call(0x4aa6d0,parent,[index_value])],f'child-at{index_value}')
for count in [0,4]:
 for name in [0,0x3001,0x3003,0x9999]:
  g=ParticleGraph();parent=g.element();children=[g.element(0x2000+i,None if i==0 else 0x3000+i) for i in range(count)];g.children(parent,children)
  ref=g.alloc(12);g.ref(ref,parent);out=g.alloc(12)
  check(g,[call(0x4ab130,UI,[out,ref,name]),call(0x416dd0,out)],f'child-named/count{count}/{name:x}')
for name in [0,1,5,9,13,0xffffffff]:
 g=ParticleGraph();o=g.element(777);g.tables([(name,o)],[(1,0),(5,o),(9,o)])
 check(g,[call(0x462190,EM,[name])],f'alias{name:x}')
g=ParticleGraph();g.put(SECONDARY,'<2I',0,0);check(g,[call(0x462190,EM,[0])],'alias-null-bucket')
# Shared hierarchy/alias resolver: direct checksums, integer children, nested
# global/local names, nested index selection, failure cleanup and output retention.
def resolve_case(mode,selected,tail=0):
 g=ParticleGraph();parent,children=g.graph();grand=[g.element(0x4000+i,0x5000+i) for i in range(2)];g.children(children[1],grand)
 if selected:g.ref(UI+0x50,parent)
 g.tables([(0x1234,parent)]+[(0x2000+i,o) for i,o in enumerate(children)]+[(0x4000+i,o) for i,o in enumerate(grand)],[(0x7654,children[2])])
 if mode=='name':items=[(0x40c698af,13,tail)]
 elif mode=='index':items=[(0x40c698af,1,tail)]
 elif mode=='empty':items=[]
 elif mode=='invalid':items=[(0x40c698af,2,bits(1.5))]
 elif mode=='nested':
  root=0x3001 if selected else 0x1234;inside=[(0,13,root)]
  if tail==0:inside.append((0xdd4cabd6,13,0x5001 if selected else 0x3003))
  elif tail==1:inside.append((0xdd4cabd6,1,1))
  elif tail==2:inside.append((0xdd4cabd6,13,0x9999))
  elif tail==3:inside=[(0,13,0x9999)]
  elif tail==4:inside.append((0xdd4cabd6,10,g.structure([(0,13,0x3001),(0xdd4cabd6,1,0)])))
  elif tail==5:inside.append((0xdd4cabd6,10,g.structure([(0,1,1),(0xdd4cabd6,13,0x5001)])))
  items=[(0x40c698af,10,g.structure(inside))]
 elif mode=='nested-index':items=[(0x40c698af,10,g.structure([(0,1,tail),(0xdd4cabd6,1,0)]))]
 elif mode=='nested-empty':items=[(0x40c698af,10,g.structure([(0xdd4cabd6,13,tail)]))]
 s=g.structure(items);out=g.alloc(4);g.put(out,'<I',0xabababab)
 calls=[call(0x4ac120,UI,[s,0x40c698af,out])]
 # Nested integer roots require the current selection; the resolver consumes it.
 if mode!='nested-index':calls.append(call(0x462340,args=[s,0]))
 check(g,calls,f'resolve/{mode}/selected{selected}/tail{tail:x}')
for selected in [False,True]:
 for name in [0,0x1234,0x7654,0x2001,0x3001,0x9999]:resolve_case('name',selected,name)
 for idx in [0,1,4,0xffffffff]:resolve_case('index',selected,idx)
 for mode in ['empty','invalid']:resolve_case(mode,selected)
 for tail in range(5):resolve_case('nested',selected,tail)
 for name in [0x3001,0x9999]:resolve_case('nested-empty',selected,name)
for idx in [1,4]:resolve_case('nested-index',True,idx)
resolve_case('nested',False,5)
for value in [0,1,0xffffffff]:
 g=ParticleGraph();o=g.element(value);check(g,[call(0x460940,o,[0,SCRIPTS])]*2,f'get-id{value:x}')
for n in [0,1,2,4]:
 for params in [False,True]:
  g=ParticleGraph();g.registry([(kind,factory) for _,kind,_,_,_,factory,_,_ in classes[:4]])
  array=g.array(10,[g.structure([(0xb6015ea8,13,kind)]) for _,kind,*_ in classes[:n]])
  items=[(0x11b70a02,12,array)]
  if params:items.append((0x7031f10c,10,g.structure([(0xa1dc81f9,13,0x12345678),(0xb9d31b0a,6,g.vector([bits(10),bits(20),bits(30)]))])))
  check(g,[call(0x449540,args=[g.structure(items),0])],f'create-composite/components{n}/params{params}')
scope='Fourteen original particle-script prerequisites, including all native GlobalExists/MangleChecksums/StructureContains/ObjectExists/CreateCompositeObject paths, cutscene-list query+wrapper, Obj_GetId, object checksum getter, child traversal/index/local-name lookup, alias-only lookup and complete recursive ID resolution. Real QB getters, reference lists, object registries, actual common-component factories and finalizers run. Valid acyclic internal graphs and unlinked output references; required Mangle operands and creation array, selected parent for nested index paths, initialized successful heap. Full arena/globals/heap and preserved registers compare. Particle component creation/rendering and a complete training frame remain unfinished.'
missing={hex(i.address) for code in coverage.values() for i in code if not hits[i.address]}
print('MISSING',sorted(missing),flush=True)
excluded={'0x4ab18a':'unreachable alignment padding',
 '0x4ab1f2':'unreachable nonnull cleanup after exhausted child traversal; successful search jumps directly to 4ab1f7',
 '0x4ab1f6':'unreachable nonnull cleanup after exhausted child traversal; successful search jumps directly to 4ab1f7',
 **{hex(a):'unreachable redundant cleanup: every recursive resolver return clears its selection' for a in [0x4ac24a,0x4ac24b,0x4ac250,0x4ac254]}}
finish('particle-startup',scope,excluded,extra)
