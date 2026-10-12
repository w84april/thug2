"""Original CleanupState, real lighting virtuals and projected-shadow math."""
from pathlib import Path
source=Path('local/analysis/probe-skater-adjust.py').read_text().split('# Exact lifecycle')[0]
source=source.replace('0xe594f0a2','0x726e85aa')
exec(compile(source,'<preserved startup oracle; Walk boundary>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear();prefix_hits.clear()
specs=[(0x4fbe20,87,'thug_skater_cleanup_create_draft',0,'word',True,False,False),
 (0x4fbd90,11,'thug_skater_cleanup_destroy_draft',0,'void',False,False,True),
 (0x4fbdb0,33,'thug_skater_cleanup_delete_draft',1,'word',True,False,True),
 (0x4fbda0,10,'thug_skater_cleanup_initialize_draft',1,'void',False,False,True),
 (0x4fbde0,21,'thug_skater_cleanup_bind_draft',0,'void',False,False,True),
 (0x4fbe00,17,'thug_skater_cleanup_update_draft',0,'void',True,True,True),
 (0x5809c0,539,'thug_skater_update_shadow_direction_draft',2,'void',False,False,True),
 (0x456b30,5,'thug_light_direction_draft',1,'word',False,False,True),
 (0x4b6180,47,'thug_light_direction_pc_draft',1,'word',False,False,True),
 (0x4b6250,29,'thug_light_direction_enabled_draft',1,'word',False,False,True),
 (0x48e920,5,'thug_light_global_direction_draft',1,'word',False,False,False),
 (0x4b6ab0,81,'thug_light_global_direction_pc_draft',1,'word',False,False,False),
 (0x431360,17,'thug_shadow_set_direction_draft',1,'void',False,False,True),
 (0x4a1ba0,292,'thug_shadow_projected_direction_draft',1,'void',False,False,True),
 (0x4a21a0,276,'thug_shadow_dynamic_direction_draft',1,'void',False,False,True),
 (0x485a70,30,'thug_camera_set_position_draft',1,'void',False,False,True),
 (0x485a90,8,'thug_camera_set_orientation_draft',1,'word',False,False,True),
 (0x48bf60,5,'thug_shadow_camera_projection_draft',2,'void',False,False,False),
 (0x4b2c50,184,'thug_shadow_camera_projection_pc_draft',2,'void',False,False,False),
 (0x4db100,242,'thug_shadow_projection_matrices_draft',3,'void',False,False,False)]
for row in specs:bind_new(*row)
for at in [0x456b30,0x4b6180,0x48e920,0x4b6ab0]:functions[hex(at)]['pointer_result']=True
for args in [(0x45e510,'thug_composite_initialize_draft',0,'word',False,False),
 (0x45ee20,'thug_composite_add_parameters_draft',2,'void',True,True),
 (0x45db30,'thug_composite_finalize_draft',0,'void',True,True),
 (0x45d890,'thug_composite_destroy_draft',0,'void',True,True),
 (0x45d920,'thug_object_update_components',0,'void',True,True),
 (0x45d720,'thug_component_descriptor_base',3,'word',False,False),
 (0x582d90,'thug_skater_construct_cleanup_prefix_draft',6,'void',True,True)]:bind(*args)
exports.extend([[0x64bb48,'thug_skater_cleanup_methods_draft'],[0x64bdec,'thug_skater_finalize_methods_draft'],[0x646648,'thug_trigger_methods_draft'],
 [0x64a440,'thug_model_light_methods_draft'],[0x70166c,'thug_light_shared_direction_draft'],
 [0x649eb8,'thug_shadow_blob_direction_methods_draft'],[0x649e98,'thug_shadow_projected_direction_methods_draft'],[0x649ed8,'thug_shadow_dynamic_direction_methods_draft']])
function_exports.extend([[0x4fbe20,'thug_skater_cleanup_create_draft'],[0x511280,'thug_skater_finalize_create_draft'],[0x434b90,'thug_trigger_create_draft'],[0x5e17ed,'thug_d3dx_normalize3_sse']])
PH,STATE,CTRL,WALK,MODEL,RENDER,LIGHT,DIRS,SHADOW,TARGET,CAMERA,TEXTURE,TABLE,ENTRY,EYE,LOOK=[P+x for x in [0x2000,0x4000,0x4200,0x4400,0x4600,0x4a00,0x4c00,0x5000,0x5400,0x5600,0x5800,0x5c00,0x5e00,0x6000,0x6200,0x6240]]
def setting(name,at,value=0,offset=0):
 if at in index:defaults[index[at]]=value
 else:glob(name,at,value,4,offset)
for name,at,val in [('thug_light_global_directions_draft',0x67dc9c,DIRS),('thug_light_shared_flags_draft',0x70167c,0),('thug_skater_shadow_flags_draft',0x7ce4e4,0),('thug_shadow_projection_table_draft',0x7ca970,TABLE),('thug_d3dx_normalize3',0x684ff4,0x5e17ed)]:setting(name,at,val)
for name,at in [('thug_light_shared_direction_draft',0x70166c),('thug_skater_shadow_vertical_draft',0x7ce4c4),('thug_skater_shadow_light_draft',0x7ce4d4)]:
 for i in range(4):setting(name,at+i*4,0,i*4)
extra={**extra,'pointer_globals':sorted(set(extra.get('pointer_globals',[])+[index[0x67dc9c],index[0x684ff4]]))}
for at in [0x532eb0,0x43d990,0x4023f0,0x404090,0x485a00,0x485a10,0x5c0985,0x5c0b39,0x5e17ed]:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
class CleanupGraph(AdjustGraph):
 def __init__(self):
  super().__init__()
  for at,n in [(P,0x80),(PH,0x1540),(STATE,0x128),(CTRL,0x30),(WALK,0x20),(MODEL,0x210),(RENDER,0x50),(LIGHT,0x30),(DIRS,0x400),(SHADOW,0x40),(TARGET,0x80),(CAMERA,0x100),(TEXTURE,0x20),(TABLE,0x80),(ENTRY,0x100)]:self.image[at-BASE:at-BASE+n]=bytes(n)
  self.put(OBJ,'<I',0x647650);fields.add(OBJ)
  self.put(P,'<7I',0x64bb48,0xd8cc3428,0,OBJ,0,0,STATE);fields.add(P)
  for at,kind,next_,methods in [(MODEL,0x286a8d26,STATE,0x647618),(STATE,0x43686585,0,0x64c140)]:self.put(at,'<6I',methods,kind,1,OBJ,next_,0);fields.add(at)
  self.put(OBJ+0x100,'<I',MODEL);self.put(OBJ+0x254,'<I',SHADOW);self.put(OBJ+0x280,'<3I',PH,CTRL,WALK)
  self.put(OBJ+0x174,'<I',8);self.put(PH+0x1528,'<I',STATE);self.put(CTRL+0x2c,'<I',STATE)
  self.put(MODEL+0x208,'<I',RENDER);self.put(RENDER+0x2c,'<I',LIGHT);self.put(LIGHT,'<I',0x64a440);fields.add(LIGHT);self.put(LIGHT+0x1c,'<I',2);self.put(LIGHT+0x2c,'<I',DIRS)
  for i in range(64):self.put(DIRS+i*16,'<4f',1+i,.5,2,1)
  self.put(SHADOW+0x18,'<I',TARGET);self.put(TARGET,'<4I',0x649e98,0,CAMERA,TEXTURE);fields.add(TARGET)
  self.put(CAMERA+0x5c,'<4f',10,20,30,1);self.put(CAMERA+0x6c,'<16f',*IDENTITY)
  self.put(TEXTURE+0x10,'<I',0x42);self.put(TABLE,'<2I',0,TABLE+16);self.put(TABLE+16,'<3I',0x42,ENTRY,0)
  self.put(EYE,'<4f',10,20,30,1);self.put(LOOK,'<4f',11,19,32,1)
 def run(self,calls,label,changes=None):
  result=super().run(calls,label,changes)
  if len(labels)%40==0:print('Cleanup cases',len(labels),flush=True)
  return result
# Lifecycle and actual dependency search, including non-zero and unaligned data.
for flags in [0,1,2,3,255,256,257,0xffffffff]:
 g=CleanupGraph();g.run([call(0x4fbe20),call(0x4fbdb0,HEAP,[flags])],f'factory/delete/{flags}')
for fill,offset in itertools.product([0,0xa5,255],[0,1,4]):
 g=CleanupGraph();g.image[P-BASE:P-BASE+0x80]=bytes([fill])*0x80;fields.add(P+offset)
 g.run([call(0x4fbda0,P+offset,[0])]*2+[call(0x4fbd90,P+offset)]*2,f'initialize/destroy/{fill}/{offset}')
for shape in ['empty','all','reversed','duplicate','missing state']:
 g=CleanupGraph();types=[] if shape=='empty' else [0x43686585,0x286a8d26] if shape=='reversed' else [0x43686585]*2 if shape=='duplicate' else [0x286a8d26] if shape=='missing state' else [0x286a8d26,0x43686585]
 nodes=[g.component(t) for t in types]
 for i,node in enumerate(nodes):g.put(node+16,'<I',nodes[i+1] if i+1<len(nodes) else 0)
 g.put(OBJ+0x100,'<I',nodes[0] if nodes else 0);g.run([call(0x4fbde0,P)]*2,f'bind/{shape}')
# Original light selection, masked shift and 32-bit address wrap.
for flags,i in itertools.product([0,1,2,4,0x80000000,0xffffffff],[0,1,2,30,31,32,33,0x10000000]):
 g=CleanupGraph();g.put(LIGHT+0x1c,'<I',flags)
 g.run([call(0x4b6250,LIGHT,[i]),call(0x4b6180,LIGHT,[i]),call(0x456b30,LIGHT,[i])],f'direction selection/{flags:x}/{i:x}')
for fn,raw,lane in itertools.product([0x48e920,0x4b6ab0],[0,0x80000000,1,0x80000001,0x7f800000,0xff800000,0x7fc12345,0x7f812345],range(4)):
 g=CleanupGraph();g.put(DIRS+lane*4,'<I',raw);g.run([call(fn,0,[0])]*2,f'global raw direction/{fn:x}/{raw:x}/{lane}')
for flags in [0,1,2,0xfffffffe,0xffffffff]:
 g=CleanupGraph();g.run([call(0x48e920,0,[0])]*2,f'global alias/{flags:x}',{0x67dc9c:0x70166c,0x70167c:flags,0x70166c:0x7f812345,0x701670:0x7f812346,0x701674:0x7f812347})
# Camera forward copies retain overlapping and unaligned source semantics.
for fn,start,length in [(0x485a70,0x5c,16),(0x485a90,0x6c,64)]:
 for off in [-16,-4,0,1,4,8,12,16]:
  g=CleanupGraph();g.put(CAMERA+0x40,'<40I',*[0x7f812300+i for i in range(40)])
  g.run([call(fn,CAMERA,[CAMERA+start+off])],f'camera copy/{fn:x}/{off}')
# Real table search: missing key, null value, collision chain, null bucket and
# both key encodings; all three D3DX matrices run for a found entry.
for kind in ['found','absent','null value','collision','null bucket']:
 for eye,target in [((10,20,30),(11,19,32)),((0,0,0),(0,1,0)),((0,0,0),(0,0,0)),((0,0,0),(1,0,0)),((0,0,0),(0,0,1))]:
  g=CleanupGraph();g.put(EYE,'<3f',*eye);g.put(LOOK,'<3f',*target)
  if kind=='absent':g.put(TABLE+16,'<I',0x43)
  if kind=='null value':g.put(TABLE+20,'<I',0)
  if kind=='collision':g.put(TABLE+16,'<3I',0x43,ENTRY,TABLE+32);g.put(TABLE+32,'<3I',0x42,0,TABLE+48);g.put(TABLE+48,'<3I',0x42,ENTRY,0)
  if kind=='null bucket':g.put(TABLE+4,'<I',0)
  g.run([call(0x4db100,0,[0x42,EYE,LOOK])]*2,f'projection table/{kind}/{eye}/{target}')
for encoded,fn in itertools.product([False,True],[0x48bf60,0x4b2c50]):
 g=CleanupGraph()
 if encoded:g.put(TEXTURE+8,'<I',1);g.put(TEXTURE+0x10,'<I',TEXTURE+0x1c);g.put(TEXTURE+0x1c,'<I',0x42)
 g.run([call(fn,0,[TEXTURE,CAMERA])]*2,f'camera projection/{encoded}/{fn:x}')
# Full concrete renderer direction receivers, never a fabricated no-op.
for fn,offset in [(0x4a1ba0,0x10),(0x4a21a0,0x50)]:
 for direction in [(1,-1,2,1),(0,0,0,1),(0,-1,0,1),(1e-30,2e-30,3e-30,1),(1e20,2e20,3e20,1)]:
  for delta in [None,-4,0,4,8,12]:
   g=CleanupGraph();at=DIRS if delta is None else TARGET+offset+delta;g.put(at,'<4f',*direction)
   # -4 on projected direction would overwrite its texture pointer.
   if offset==0x10 and delta==-4:continue
   g.run([call(fn,TARGET,[at])]*2,f'shadow concrete/{fn:x}/{direction}/{delta}')
# State selection, signed counter bounds, all lazy-init flag combinations and
# optional light/renderer branches. Projected path writes real camera matrices.
frame_records=[]
for mode,counter in itertools.product(['skate ground','skate air','vehicle','walk ground','walk air','no control','no walk'],[-0x80000000,-1,0,1,8,15,16,17,0x7fffffff]):
 g=CleanupGraph()
 if mode=='skate air':g.put(STATE+0x18,'<I',1)
 if mode=='vehicle':g.put(STATE+0x118,'<B',1);g.put(WALK+0x18,'<I',1)
 if mode.startswith('walk'):g.put(STATE+0x1c,'<I',1);g.put(WALK+0x18,'<I',1 if mode=='walk air' else 0)
 if mode in ['no control','no walk']:g.put(OBJ+0x284,'<I',0)
 if mode=='no walk':g.put(OBJ+0x288,'<I',0)
 g.put(OBJ+0x174,'<i',counter);g.run([call(0x4fbe00,P,[Q])]*2,f'frame state/{mode}/{counter}')
 frame_records.append({'mode':mode,'initial_counter':counter,'counter':oracle.word(OBJ+0x174)})
for flags,missing in itertools.product([0,1,2,3,0x80000000,0xfffffffe,0xffffffff],['none','model','renderer','light','shadow','blob','dynamic']):
 g=CleanupGraph()
 if missing=='model':g.put(OBJ+0x100,'<I',STATE)
 if missing=='renderer':g.put(MODEL+0x208,'<I',0)
 if missing=='light':g.put(RENDER+0x2c,'<I',0)
 if missing=='shadow':g.put(SHADOW+0x18,'<I',0)
 if missing in ['blob','dynamic']:g.put(TARGET,'<I',0x649eb8 if missing=='blob' else 0x649ed8)
 g.run([call(0x5809c0,OBJ,[0,0])]*2,f'frame flags/optional/{flags:x}/{missing}',{0x7ce4e4:flags})
for enabled,y,x,z in [(enabled,y,x,z) for enabled in [0,2] for y in [bits(.65)-1,bits(.65),bits(.65)+1,bits(-1),bits(0),bits(1)] for x,z in [(0,0),(bits(1),bits(2)),(bits(1e-30),bits(1e-30)),(bits(1e20),bits(-1e20))]]:
 g=CleanupGraph();g.put(LIGHT+0x1c,'<I',enabled);g.put(DIRS,'<4I',x,y,z,bits(1));g.run([call(0x5809c0,OBJ,[0,0])]*2,f'slope clamp/{enabled}/{x:x}/{y:x}/{z:x}')
for table in [0x649eb8,0x649e98,0x649ed8,0]:
 g=CleanupGraph()
 if table:g.put(TARGET,'<I',table)
 else:g.put(SHADOW+0x18,'<I',0)
 g.run([call(0x431360,SHADOW,[DIRS])]*2,f'outer direction/{table:x}')
for reverse in [False,True]:
 g=CleanupGraph();g.put(OBJ+0x100,'<I',P);g.put(P+16,'<I',STATE if reverse else MODEL)
 g.put(STATE+16,'<I',MODEL if reverse else 0);g.put(MODEL+16,'<I',0 if reverse else STATE)
 g.run([call(0x45d920,OBJ,[Q])]*2,f'owner dispatch/{reverse}')
shared_records=[]
for reverse in [False,True]:
 g=CleanupGraph();registry=[(0xd8cc3428,0x4fbe20),(0x43686585,0x519740)];g.registry(registry)
 order=registry[::-1] if reverse else registry;descriptors=[g.structure([(0xb6015ea8,13,t)]) for t,_ in order]
 calls=[call(0x45e510,OBJ)]+[call(0x45ee20,OBJ,[s,0]) for s in descriptors]+[call(0x45db30,OBJ)]
 g.run(calls,f'shared startup/{reverse}');components={};node=oracle.word(OBJ+0x100)
 while node:components[oracle.word(node+4)]=node;node=oracle.word(node+16)
 component=components[0xd8cc3428];assert oracle.word(component+0x18)==components[0x43686585]
 desc=g.alloc(16);g.put(desc,'<4I',0x12345678,0,0,0)
 g.run(calls+[call(0x4fbe00,component,[Q]),call(0x45d720,component,[desc,0,0]),call(0x45d890,OBJ)],f'shared frame/disposal/{reverse}')
 shared_records.append({'reverse':reverse,'components':{hex(k):v for k,v in components.items()}})

prefix_records=[]
for heap_index,local,id_ in itertools.product([0,1,2,0xffffffff],[0,1,256,257],[0,0xffffffff]):
 g=ScoreGraph();g.symbol(0x78f80ec4,2,bits(.125));g.registry([(0xce0ca665,0),(0xb87c8e43,0),(0x43686585,0x519740),(0xf27a294d,0x51bd80),(0x27d7cd28,0x41eec0),(0xd262802f,0x518b60),(0xbf518e27,0x514430),(0x270f56e1,0x523490),(0xd9151d4d,0x517830),(0x5bd63b29,0x505440),(0x52d61a0d,0x517d40),(0x11b4c67f,0x512c60),(0x9f9cc949,0x4f80e0),(0xe594f0a2,0x434b90),(0x9b373e58,0x511280),(0xd8cc3428,0x4fbe20)])
 mutate=bool(len(prefix_records)%2)
 if mutate:g.put(DLOG+4,'<2I',OBJ+0x14,0x77700000+len(prefix_records))
 stages=g.run([],f'skater through CleanupState/{heap_index}/{local}/{id_}',{0x690fa0:0xfffffffe})
 before=bytes(oracle.cpu.mem_read(BASE,len(initial)));cpu=oracle.cpu;sp=oracle.stack+0x18000
 args=[17,MANAGER,local,id_,heap_index,0x12345678]
 cpu.mem_write(sp,struct.pack('<7I',oracle.stop,*args));cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,OBJ);cpu.reg_write(UC_X86_REG_FPCW,0x7f)
 try:cpu.emu_start(0x582d90,oracle.stop,count=500000)
 except Exception:print('PREFIX FAILED',hex(cpu.reg_read(UC_X86_REG_EIP)),args,flush=True);raise
 assert cpu.reg_read(UC_X86_REG_EIP)==0x45ee20 and oracle.word(BOUNDARY+8)==OBJ
 chain=[];c=oracle.word(OBJ+0x100)
 while c:chain.append((c,oracle.word(c+4)));c=oracle.word(c+16)
 assert [t for _,t in chain]==[0xce0ca665,0xb87c8e43,0x43686585,0xf27a294d]+([0x27d7cd28] if local&255 else [])+[0xd262802f]+([0xbf518e27,0x270f56e1,0xd9151d4d,0x5bd63b29,0x52d61a0d,0x11b4c67f,0x9f9cc949,0xe594f0a2,0x9b373e58,0xd8cc3428] if local&255 else [])
 component=next(c for c,t in chain if t==0xd262802f);score=oracle.word(component+0x18);player=int.from_bytes(cpu.mem_read(score+8,2),'little')
 assert oracle.word(OBJ+0x278)==component and player==(oracle.word(OBJ+0x14)&65535)
 params=oracle.word(BOUNDARY+4);next_type=oracle.word(oracle.word(params+4)+8)
 assert next_type==(0x726e85aa if local&255 else 0x850eef66)
 if local&255:
  links={t:c for c,t in chain}
  assert oracle.word(OBJ+0x258)==links[0x270f56e1] and oracle.word(OBJ+0x284)==links[0xd9151d4d] and oracle.word(OBJ+0x280)==links[0x5bd63b29]
  assert oracle.cpu.mem_read(links[0xd9151d4d]+0x18,1)==b'\x00'
  assert oracle.word(OBJ+0x270)==links[0x11b4c67f]
 after=bytes(cpu.mem_read(BASE,len(initial)));outputs=[];known={row[0] for row in exports}
 for page in range(0,len(initial),4096):
  if before[page:page+4096]!=after[page:page+4096]:
   for j in range(page,min(page+4096,len(initial)),4):
    if before[j:j+4]!=after[j:j+4]:
     outputs.append([BASE+j,after[j:j+4].hex()])
     if int.from_bytes(after[j:j+4],'little') in known:fields.add(BASE+j)
 stages.append({'fn':'0x582d90','this':OBJ,'args':args+[DIAG],'result':None,'outputs':outputs,'globals':[oracle.global_read(x) for x in globals_],'callbacks':0,'expected_trap':True})
 oracle.counts['thug_skater_construct_cleanup_prefix_draft']+=1
 prefix_records.append({'arguments':args,'components':chain,'boundary':list(struct.unpack('<4I',cpu.mem_read(BOUNDARY,16))),
  'next_type':hex(next_type),'score':{'component':component,'state':score,'player_id':player},'diagnostics_mutate_id':mutate})

scope='Twenty complete original routines recover CleanupState lifecycle and full frame, light direction virtuals and global fallback, camera setters, all three shadow direction receivers and real projected-shadow camera/table/D3DX calculations. Existing camera accessors, vector and D3DX helpers are reused and not recounted. Whole arena/globals/heap and completed-call preserved registers compare. Initialized dependency graphs and successful allocation are contracts. Actual owner dispatch, shared construction/frame/disposal and original skater construction through CleanupState execute; partial construction stops before Walk726e85aa and is not a completed routine. Renderer creation, rendering, remaining startup/frames and one original playable training level remain unfinished.'
extra={**extra,'direct_initializer_prefix':True,'boundary_address':BOUNDARY,'boundary_factory':0x45ee20,
 'native_callbacks':[{'module':'skater-construction-diagnostic-fixture.wasm','export':'fixture_skater_print','slots':[DIAG+4]}]}
saved=coverage.copy();coverage.clear();finish('skater-cleanup',scope,{},extra);coverage.update(saved)
# Unicorn2.1.4 retains signaling payloads in bare FLD/FSTP; physical x87
# sets the quiet bit. Declare only the two exact shared-vector store lanes.
fixture_path=folder/'skater-cleanup-fixtures.json';f=json.loads(fixture_path.read_text())
for c in f['cases']:
 for step in c['steps']:
  if step['fn'] in ['0x48e920','0x4b6ab0']:
   step['global_quiet_float_indices']=[index[0x701670],index[0x701674]]
fixture_path.write_text(json.dumps(f,separators=(',',':')))
p=folder/'skater-cleanup-original.json';report=json.loads(p.read_text())
report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
code=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(0x182d90,1639),0x582d90))
report['partial_constructor']={'address':'0x582d90','covered':sum(bool(prefix_hits[i.address]) for i in code),'total':len(code),'boundary':'0x45ee20','interrupted_calls':len(prefix_records),'records':prefix_records}
report['shared_startup_records']=shared_records;report['frame_records']=frame_records
p.write_text(json.dumps(report,indent=2)+'\n')
(folder/'skater-cleanup-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k in ['cases','calls','instruction_coverage']}),flush=True)
