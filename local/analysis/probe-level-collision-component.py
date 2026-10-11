"""Original manager construction, collision factories and component lifecycle prefix."""
from pathlib import Path
source=Path('local/analysis/probe-texture-buffer.py').read_text().split('for fill in [0,0xa5,0xff]:')[0]
exec(compile(source,'<preserved initialized comparison heap>','exec'))
functions.clear();code.clear();hits.clear();oracle.counts.clear();fields.clear()
specs=[(0x44f7e0,72,'module_base_construct',0,'word',True,True),(0x406890,82,'task_base_construct',1,'word',True,True),
 (0x407f80,222,'asset_manager_construct',0,'word',True,True),(0x4088e0,74,'asset_manager_acquire',1,'void',True,False),
 (0x411fa0,161,'rigid_collision_base_construct',0,'word',False,True),(0x412550,152,'box_collision_construct',0,'word',False,True),
 (0x4133e0,126,'compound_collision_construct',0,'word',True,True),(0x411be0,72,'compound_collision_append',1,'void',True,True),
 (0x40ae10,10,'compound_collision_set_owner',1,'void',False,True),(0x4177b0,75,'moving_collision_register',2,'void',True,False),
 (0x414990,589,'moving_collision_create',4,'word',True,False),(0x40add0,49,'collision_kind',1,'word',False,False),
 (0x41c920,87,'collision_component_create',0,'word',True,False),(0x41c7b0,210,'collision_component_initialize',1,'void',False,True),
 (0x41c890,144,'collision_component_bind',2,'void',False,True),(0x41c980,214,'collision_component_update_entry',0,'void',False,True),
 (0x493040,70,'model_renderer_collision_geometry',0,'word',False,True),(0x490ab0,7,'model_asset_geometry',0,'word',False,True)]
for a,n,name,argc,result,heap,this in specs:
 functions[hex(a)]={'name':'thug_'+name+'_draft','this':this,'result':result,'cleanup':argc*4 if this else 0,'memory':heap}
 code[a]=list(md.disasm(pe.get_data(a-0x400000,n),a));oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:hits.update([at]),begin=a,end=a+n-1)
functions['0x413000']={'name':'thug_moving_collision_initialize','this':True,'result':'word','cleanup':4,'memory':False}
functions['0x49cbb0']={'name':'thug_collision_load','this':True,'result':'byte','cleanup':24,'memory':True}
# Exact identities, with no fake implementations supplied to original functions.
extra=[(0x691978,'thug_moving_collision_sentinel_draft'),(0x645d34,'thug_collision_sentinel_methods_draft'),(0x645aa0,'thug_collision_node_methods_draft'),(0x645ce0,'thug_moving_collision_methods'),(0x645bc0,'thug_box_collision_methods_draft'),(0x645aa8,'thug_compound_collision_methods_draft'),(0x645b00,'thug_rigid_collision_base_methods_draft'),(0x645eec,'thug_collision_component_methods_draft'),(0x645658,'thug_asset_manager_methods_draft'),(0x64728c,'thug_module_base_methods_draft'),(0x647284,'thug_module_node_methods_draft'),(0x64548c,'thug_task_base_methods_draft'),(0x64549c,'thug_task_node_methods_draft'),(0x6476f0,'thug_asset_task_methods_draft'),(0x645c18,'thug_static_collision_methods'),(0x645568,'thug_asset_base_methods')]
exports += [list(e) for e in extra];function_exports=[[0x407eb0,'thug_asset_task_pending_draft']]
SYMBOLS,SERVICES,AM,SCENEHEAD=BASE+0x1c0000,BASE+0x1d0000,BASE+0x1d0100,BASE+0x1d0200
memory[SYMBOLS-BASE:SYMBOLS-BASE+0x4000]=bytes(0x4000);put(SERVICES,'<3I',0,0,ADAPTER)
# Global references are deterministic fixture starting state, independent of outputs.
for name,a,v in [('thug_asset_manager',0x6918dc,0),('thug_asset_manager_references_draft',0x6918e0,0),('thug_script_symbol_buckets',0x6f3624,SYMBOLS),('thug_component_services',0x354,SERVICES),('thug_collision_scene_list',0x6fa7ec,SCENEHEAD)]:globals_.append([name,a,4]);defaults.append(v)
AMINDEX=next(i for i,e in enumerate(globals_) if e[0]=='thug_asset_manager');REFINDEX=AMINDEX+1
REG=len(globals_)
for i,v in enumerate([0x645d34,0xffffffff,0,0x691978,0x691978]):globals_.append(['thug_moving_collision_sentinel_draft',0x691978+i*4,4,i*4]);defaults.append(v)
HEAD=len(globals_);globals_.append(['thug_moving_collision_list',0x691984,4]);defaults.append(0x691978)
pointer_globals=[REG,REG+3,REG+4,HEAD]
put(SCENEHEAD,'<5I',0,0xffffffff,0,SCENEHEAD,SCENEHEAD)
initial=bytes(memory);oracle.initial=initial;oracle.event_limit=2700;oracle.instruction_limit=20000000;oracle.setword(0x684fe4,0x5df4ac)
# Force the same registered original matrix backend as the earlier model tests.
def unit(g,calls,label,changes=None):
 stages=oracle.case(calls,g.patches(),changes);labels.append(label)
 known={a for a,*_ in exports}|{a for a,*_ in function_exports}
 for step in stages:
  for a,v in step['outputs']:
   if int.from_bytes(bytes.fromhex(v),'little') in known:fields.add(a)
 return stages

def geometry(g,n=1):
 a=g.alloc(n*64)
 for i in range(n):
  at=a+i*64;g.data[at-BASE:at-BASE+64]=bytes(64);vertices=g.alloc(24)
  g.put(at,'<IHH',123+i,0,2);g.put(at+16,'<8f',-3-i,-4,-5,1,3,4+i,5,1);g.put(at+48,'<I',vertices);g.put(at+60,'<f',0.5)
  g.put(vertices,'<6f',3,4,0,1,2,3)
 return a
for fill in [0,0xa5,0xff]:
 for fn in [0x44f7e0,0x407f80,0x411fa0,0x412550,0x4133e0,0x41c920]:
  g=Graph();g.data[P-BASE:P-BASE+0x300]=bytes([fill])*0x300;unit(g,[call(fn,P if functions[hex(fn)]['this'] else 0)],f'constructor{fn:x}/fill{fill}')
 for priority in [0,0x80000000,0xffffffff]:
  g=Graph();g.data[P-BASE:P-BASE+32]=bytes([fill])*32;unit(g,[call(0x406890,P,[priority])],f'taskfill{fill}/priority{priority:x}')
for create in [0,1,255,256,257]:
 for refs in [0,0xffffffff]:
  unit(Graph(),[call(0x4088e0,0,[create]),call(0x4088e0,0,[create])],f'manageracquire{create}/refs{refs:x}',{REFINDEX:refs})
for n in [0,1,3]:
 g=Graph();calls=[call(0x4133e0,P)]
 calls += [call(0x411be0,P,[P+0x300+i*16]) for i in range(n)];calls += [call(0x40ae10,P,[0x12345678])]
 calls += [call(0x4177b0,0,[P+0x300+i*16,0x76543210]) for i in range(n)];unit(g,calls,f'compoundandregistry{n}')
for kind in [0,1,2,4,0xffffffff]:
 for count in [-1,0,1,3]:
  g=Graph();a=geometry(g,max(count,1));unit(g,[call(0x414990,0,[kind,a,count&0xffffffff,P+0x800])],f'factorykind{kind}/count{count}')
for value in [0,0xdd42aa66,0x2ba71070,0xe460abde,0x6aadf154,0xffffffff]:unit(Graph(),[call(0x40add0,0,[value])],f'kind{value:x}')
# Real relocated training geometry exercises radius calculations and raw layouts.
raw=(ROOT/'local/game-files/Game/Data/levels/TR/TR.col.xbx').read_bytes()
for count in [1,3]:
 g=Graph();g.data[TEXTURES-BASE:TEXTURES-BASE+len(raw)]=raw;g.put(P+0x100,'<8f',1e7,1e7,1e7,1,-1e7,-1e7,-1e7,1)
 unit(g,[call(0x49cbb0,P,[TEXTURES,P+0x80,P+0x84,P+0x88,P+0x100,0]),call(0x414990,0,[4,TEXTURES+32,count,P+0x800])],f'actualTRfirst{count}')

def component_graph(g,asset_count=None,metadata=False):
 owner=g.alloc(0x108);model=g.alloc(0x238);renderer=g.alloc(0x60);inner=g.alloc(0xd4)
 for a,n in [(P,28),(owner,0x108),(model,0x238),(renderer,0x60)]:g.data[a-BASE:a-BASE+n]=bytes(n)
 g.put(P,'<I',0x645eec);g.put(P+12,'<I',owner);g.put(owner+0x100,'<I',model);g.put(model+4,'<I',0x286a8d26);g.put(model+16,'<I',0);g.put(model+0x208,'<I',renderer)
 g.put(owner+0x4c,'<4f',10,20,30,1);g.put(owner+0xc0,'<16f',*[1 if i%5==0 else 0 for i in range(16)])
 rows=[];data=geometry(g,3)
 if asset_count is not None:
  asset=g.alloc(80);modeldata=g.alloc(0xc0);geo=g.alloc(0x50);g.data[asset-BASE:asset-BASE+80]=bytes(80);g.put(asset,'<I',0x645568);g.put(asset+8,'<I',4);g.put(asset+16,'<I',modeldata)
  g.put(modeldata+0x88,'<2I',asset_count,data);g.put(modeldata+0xb4,'<I',geo);rows=[(77,asset)];g.put(renderer+0x30,'<I',77)
  g.put(geo+16,'<16f',*[1 if i%5==0 else 0 for i in range(16)]);g.put(geo+0x40,'<3f',1,2,3)
  if metadata:
   sentinel=g.alloc(12);link=g.alloc(12);part=g.alloc(24);g.put(sentinel+4,'<I',link);g.put(link,'<I',part);g.put(part+16,'<I',77);g.put(renderer+16,'<I',sentinel);g.put(renderer+0x4a,'<H',1)
 g.put(AM+0x1c,'<I',g.table(rows));return owner,model,renderer,inner,data
for count in [None,0,1,3]:
 g=Graph();owner,model,renderer,inner,data=component_graph(g,count)
 unit(g,[call(0x41c890,P,[4,0])],f'componentfallbackcount{count}',{AMINDEX:AM})
for kind in [1,4]:
 g=Graph();owner,model,renderer,inner,data=component_graph(g)
 unit(g,[call(0x41c890,P,[kind,data])],f'componentdirect{kind}',{AMINDEX:AM})
for mode,cls,attached in [(0,0,False),(0x6aadf154,0,False),(0x6aadf154,0xb7b3bd86,False),(0x6aadf154,0xb7b3bd86,True),(0xdd42aa66,0,False)]:
 g=Graph();owner,model,renderer,inner,data=component_graph(g)
 params=g.alloc(8);nodes=[g.alloc(16) for _ in range(3)];g.put(params,'<2I',0,nodes[0])
 for i,(k,v) in enumerate([(0x2d7e583b,mode),(0x12b4e660,cls),(0xa1dc81f9,123)]):g.put(nodes[i],'<4I',26,k,v,nodes[i+1] if i<2 else 0)
 scene=g.alloc(256);sector=g.alloc(28);g.put(sector+0x18,'<I',inner if attached else 0);g.put(inner+12,'<I',data);g.put(scene+0xd0,'<I',g.table([(123,sector)]));g.put(SCENEHEAD+4,'<I',scene);g.put(SCENEHEAD+12,'<I',0)
 unit(g,[call(0x41c7b0,P,[params])],f'initialize{mode:x}/cls{cls:x}/attached{attached}',{AMINDEX:AM})
for present,model_present,metadata in [(False,False,False),(True,False,False),(True,True,False),(True,True,True)]:
 g=Graph();owner,model,renderer,inner,data=component_graph(g,1,metadata)
 if not model_present:g.put(owner+0x100,'<I',0)
 g.put(P+24,'<I',inner if present else 0)
 unit(g,[call(0x413000,inner,[data]),call(0x41c980,P)],f'updatepresent{present}/model{model_present}/metadata{metadata}',{AMINDEX:AM})
for n in [0,1,2,65535]:
 g=Graph();_,_,renderer,_,_=component_graph(g,1,True);g.put(renderer+0x4a,'<H',n)
 unit(g,[call(0x493040,renderer)],f'renderermetadatacount{n}',{AMINDEX:AM})
g=Graph();g.put(P+0xb4,'<I',0x12345678);unit(g,[call(0x490ab0,P)],'modelgeometrygetter')
known={a for a,*_ in exports}|{a for a,*_ in function_exports}
for case in oracle.cases:
 for a,v in case['patches']:
  if int.from_bytes(bytes.fromhex(v),'little') in known:fields.add(a)
coverage={hex(a):{'total':len(c),'covered':sum(bool(hits[i.address]) for i in c),'missing':[hex(i.address) for i in c if not hits[i.address]]} for a,c in code.items()}
scope='Original asset manager/task initialization and reference acquisition; collision base/box/compound construction, registry append, all414990 factory branches, checksum-to-kind selection, component factory/bind/initialize/update, renderer metadata access. Real training geometry plus valid synthetic internal graphs, initialized successful heap, actual virtual dispatch and actual ready asset lookup. Engine lifecycle/query methods not reached by these entrypoints remain unavailable; no playable claim.'
fixture={'base':BASE,'memory':'level-collision-component-unit-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'texture-buffer-ports.wasm','memory_exports':['fixture_texture_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'pointer_fields':sorted(fields),'pointer_exports':exports,'function_exports':function_exports,'pointer_globals':pointer_globals,'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'level-collision-component-unit-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(len(c['steps']) for c in oracle.cases),'instruction_coverage':coverage,'scope':scope};(folder/'level-collision-component-unit-original.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
