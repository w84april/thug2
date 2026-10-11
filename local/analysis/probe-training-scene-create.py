"""Actual native Create builds the startup GameObjects in one live registry."""
from pathlib import Path
source=Path('local/analysis/probe-training-model-transform.py').read_text().split('steps=oracle.case(prefix);array=')[0]
source=source.replace('elif at in [a for _,a in newtypes if a!=0x421490]:','elif at in [a for _,a in newtypes if a not in (0x421490,0x433d90)]:')
exec(compile(source,'<preserved original full training setup>','exec'))
exports.append([0x646594,'thug_simple_sound_methods_draft'])
function_exports.append([0x433d90,'thug_simple_sound_create_draft'])
oracle.cpu.hook_add(UC_HOOK_CODE,identities,begin=0x433d90,end=0x433d90)
GCTX,NETWORK,PARAMS,PARAM_ITEM,PREFIX_TEXT,SCRATCH=BASE+0xe400,BASE+0xe800,BASE+0xea00,BASE+0xea20,BASE+0xea40,BASE+0xeac0
memory[GCTX-BASE:GCTX-BASE+0x3d4]=bytes(0x3d4);memory[NETWORK-BASE:NETWORK-BASE+0x12c]=bytes(0x12c)
# These reached context prefixes are explicit initialized single-player state.
# No absent geometry/rail classes are dispatched in this fixture.
glob('thug_game_context',0x7ce478,GCTX);glob('thug_network_state',0x7cce14,NETWORK)
put(PARAMS,'<2I',0,PARAM_ITEM);put(PARAM_ITEM,'<4I',6,0x6c4e7971,PREFIX_TEXT,0)
prefix_text=b'TRG_SFX_Ghost_PipeBust';memory[PREFIX_TEXT-BASE:PREFIX_TEXT-BASE+len(prefix_text)+1]=prefix_text+b'\0'
for a,name,argc in [(0x5a4ff0,'script_create_prefix',2),(0x5a34d0,'script_create_structure_prefix',2),
 (0x5a5030,'script_kill',2),(0x5b0a40,'flush_dead_objects',2)]:
 functions[hex(a)]={'name':'thug_'+name+'_draft','this':False,'result':'byte','cleanup':0,'stack_args':list(range(argc))}
# The Kill path invokes its actual stored callback; relocate that function identity.
function_exports.append([0x59fb10,'thug_scene_kill_object_draft'])
for a in [0x461ab0,0x5b0a40,0x5a4ff0,0x5a4ef0,0x5a4da0,0x5a32a0,0x5a2e50,0x468eb0,0x5a34d0,0x5a5030,0x5a32c0,0x59fb10,0x45e620]:
 oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:native_hits.update([hex(at)]),begin=a,end=a)
created=[]
def created_object(cpu,at,size,user):created.append(cpu.reg_read(UC_X86_REG_EAX))
oracle.cpu.hook_add(UC_HOOK_CODE,created_object,begin=0x468ea6,end=0x468ea6)
create_code={};create_hits=Counter()
for a,n in [(0x5a4ff0,30),(0x5a4ef0,243),(0x5a4da0,301),(0x5a32a0,24),(0x5a2e50,1097),(0x468eb0,16),(0x5a34d0,14)]:
 create_code[a]=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(a-0x400000,n),a))
 oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:create_hits.update([at]),begin=a,end=a+n-1)
initial=bytes(memory);oracle.initial=initial
steps=oracle.case(prefix);array=steps[-1]['result'];nodes=oracle.word(TABLE+0x1000c);items=oracle.word(nodes+8)
def invoke(fn,this,args,cleanup):
 cpu=oracle.cpu;sp=oracle.stack+0x18000;cpu.mem_write(sp,struct.pack('<'+'I'*(len(args)+1),oracle.stop,*args));cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,this)
 cpu.emu_start(fn,oracle.stop,count=100000);assert cpu.reg_read(UC_X86_REG_EIP)==oracle.stop and cpu.reg_read(UC_X86_REG_ESP)==sp+4+cleanup
 return cpu.reg_read(UC_X86_REG_EAX)
def checksum(node,key):
 oracle.setword(SCRATCH,0);invoke(0x476950,node,[key,SCRATCH,0],12);return oracle.word(SCRATCH)
selected=[]
for i in range(oracle.word(nodes+4)):
 node=oracle.word(items+4*i)
 if checksum(node,0x12b4e660)==0xef59c100 and invoke(0x476b40,node,[0x7c2552b9],4)&255:
  selected.append({'index':i,'node':node,'name':checksum(node,0xa1dc81f9)})
assert len(selected)==28
inventory=json.loads((folder/'training-scene-node-inventory.json').read_text())['nodes'];expected=[n for n in inventory if n['class_text']=='GameObject' and n['created_at_start']]
assert [n['index'] for n in selected]==[n['index'] for n in expected]
letter_node=oracle.word(items+1289*4)
assert not(invoke(0x476b40,letter_node,[0x7c2552b9],4)&255)
letter_name=checksum(letter_node,0xa1dc81f9)
for row,prior in zip(selected,expected):row['text']=prior['text'];assert hex(row['name'])==prior['name']
print('INITIAL GAMEOBJECTS',[(n['index'],n['text']) for n in selected],flush=True)
def live_objects():
 result=[];head=OBJECTS+4;node=oracle.word(head+12)
 while node!=head:
  obj=oracle.word(node+4);assert obj and len(result)<80;result.append(obj);node=oracle.word(node+12)
 return result
def object_state(obj):
 chain=[];component=oracle.word(obj+0x100)
 while component:
  assert len(chain)<20;chain.append({'address':hex(component),'type':hex(oracle.word(component+4))});component=oracle.word(component+16)
 return {'object':hex(obj),'name':hex(oracle.word(obj+0x14)),'flags':hex(oracle.word(obj+0x104)),'script':hex(oracle.word(obj+0x10)),'components':chain}
plans=[('all28 startup GameObjects, then dynamic Letter S',prefix+[(0x4738e0,SCRIPT,[])]+[(0x5a4ff0,0,[n['node'],SCRIPT]) for n in selected]+[(0x5a34d0,0,[letter_node,SCRIPT])]),
 ('prefix Create19, Kill19, flush and recreate19',prefix+[(0x4738e0,SCRIPT,[]),(0x5a4ff0,0,[PARAMS,SCRIPT]),(0x5a5030,0,[PARAMS,SCRIPT]),(0x5b0a40,0,[0,0]),(0x5a4ff0,0,[PARAMS,SCRIPT])])]
oracle.cases.clear();details=[];all_steps=[];regs=[UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP]
for case_index,(label,calls) in enumerate(plans):
 created.clear();native_hits.clear();factory_hit.clear();active_model.clear();saved=[oracle.cpu.reg_read(r) for r in regs]
 try:steps=oracle.case(calls)
 except Exception:
  print('STOP',label,'pc',hex(oracle.cpu.reg_read(UC_X86_REG_EIP)),'sp',hex(oracle.cpu.reg_read(UC_X86_REG_ESP)),'factories',factory_hit,'created',[object_state(x) for x in created],'native',dict(native_hits),flush=True)
  raise
 assert not factory_hit and saved==[oracle.cpu.reg_read(r) for r in regs]
 assert all(s['result']==1 for s in steps[8:]);live=live_objects();state=[object_state(p) for p in live]
 assert all(n['flags']=='0x60' for n in state)
 detail={'case':label,'calls':len(steps),'created_objects':[hex(p) for p in created],'live_objects':state,'native_entries':dict(native_hits),'model':None}
 if case_index==0:
  assert len(created)==len(live)==29 and set(live)==set(created)
  assert {int(n['name'],16) for n in state}=={n['name'] for n in selected}|{letter_name}
  simple_count=sum(any(c['type']=='0xf1641e3' for c in n['components']) for n in state)
  assert simple_count==native_hits['0x433d90'] and sorted(len(n['components']) for n in state)==[6]*(28-simple_count)+[7]*(1+simple_count)
  detail['simple_sound_objects']=[n['name'] for n in state if any(c['type']=='0xf1641e3' for c in n['components'])]
  detail['component_count']=sum(len(n['components']) for n in state)
  component=active_model['component'];obj=oracle.word(component+12);renderer=oracle.word(component+0x208);instance=active_model['instance']
  matrix=list(struct.unpack('<16I',oracle.cpu.mem_read(instance+4,64)));assert matrix==[0x3f800000 if i%5==0 else 0 for i in range(12)]+[oracle.word(obj+0x4c+i*4) for i in range(4)]
  assert oracle.cpu.mem_read(instance+0x4c,1)==b'\x01'
  mesh=active_model['mesh'];indices=oracle.word(oracle.word(mesh+0x54)+16);vertex=oracle.word(mesh+0xcc);vertices=oracle.word(vertex+12);gpu_vertices=oracle.word(vertex+8)+0x100
  assert bytes(oracle.cpu.mem_read(indices,272))==model_bytes[503:775] and bytes(oracle.cpu.mem_read(INDEXDEV+0x100,272))==model_bytes[503:775]
  assert bytes(oracle.cpu.mem_read(vertices,3888))==model_bytes[798:4686] and bytes(oracle.cpu.mem_read(gpu_vertices,3888))==model_bytes[798:4686]
  detail['model']={'component':hex(component),'object':hex(obj),'renderer':hex(renderer),'instance':hex(instance),'matrix':[hex(v) for v in matrix],
    'mesh':hex(mesh),'cpu_indices':hex(indices),'gpu_indices':hex(INDEXDEV+0x100),'cpu_vertices':hex(vertices),'gpu_vertices':hex(gpu_vertices),'vertices':108,'indices':136,'enabled':1}
  masks={}
  defined={0,*range(4,12),16,17,*range(20,10+len(b'models\\gameobjects\\skate\\letter_s\\letter_s.tex')+1)}
  for off in range(0,76,4):
   mask=sum(255<<(8*j) for j in range(4) if off+j in defined)
   if mask!=0xffffffff:masks[str(index[0x691758+off])]=mask
  steps[-1]['global_bit_masks']=masks
 else:
  assert len(created)==38 and len(live)==19 and set(live)==set(created[19:])
  expected_names={n['name'] for n in selected if n['text'].startswith(prefix_text.decode())};assert len(expected_names)==19
  assert {int(n['name'],16) for n in state}==expected_names and all(len(n['components'])==6 for n in state)
  assert native_hits['0x5a32c0']==19 and native_hits['0x45e620']==19
  assert not active_model
 detail['live_count']=len(live);details.append(detail);all_steps.extend(steps)
 print('COMPLETE',label,'calls',len(steps),'created',len(created),'live',len(live),flush=True)
for case in oracle.cases:
 for step in case['steps']:
  for at,data in step['outputs']:
   if int.from_bytes(bytes.fromhex(data),'little') in {e[0] for e in exports}|{e[0] for e in function_exports}:fields.add(at)
  step['global_float_indices']=[]
  for at in [0x6f2348,0x6f2568,*range(0x6f2370,0x6f24b0,16)]:
   if step['globals'][index[at]]&0xfe==4:step['global_float_indices'].append(index[at+8])
  merged=[];chunks=[];start=end=0
  for at,data in step['outputs']:
   if chunks and at!=end:merged.append([start,''.join(chunks)]);chunks=[]
   if not chunks:start=at
   chunks.append(data);end=at+len(data)//2
  if chunks:merged.append([start,''.join(chunks)])
  step['outputs']=merged
scope='Unchanged training QB files register1917 nodes. Actual Class and CreatedAtStart getters select all28 startup GameObjects. Native Create, including real dead-object flush, name lookup, class dispatch and full constructor, creates them in one live registry. Actual CreateFromStructure then adds dynamic Letter S with its real texture/model, exact136 indices108 vertices and transform:29live objects including the actual SimpleSound components. A second case uses native prefix Create for19real pipe-bust nodes, native Kill destroys all19, then Create builds19again. Entire arenas/globals/heap/CPU and GPUfixture payloads compare. Other node classes, general creation branches, complete level boot, production GPUdrawing and gameplay remain unfinished. The startup objects are a subset of the scene, not an empty-scene shortcut or a playable level.'
used={s['fn'] for s in all_steps};prior=json.loads((folder/'training-model-transform-fixtures.json').read_text())
prior['native_callbacks']=[c for c in prior['native_callbacks'] if c.get('original')!=0x433d90]
fixture={**prior,'memory':'training-scene-create-memory.bin','globals':globals_,'functions':{k:v for k,v in functions.items() if k in used},
 'cases':oracle.cases,'case_labels':[p[0] for p in plans],'pointer_fields':sorted(fields),'pointer_exports':exports,'function_exports':function_exports,'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'training-scene-create-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
coverage={hex(a):{'complete':False,'covered':sum(bool(create_hits[i.address]) for i in c),'total':len(c),'executed':[hex(i.address) for i in c if create_hits[i.address]]} for a,c in create_code.items()}
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(details),'calls':len(all_steps),'startup_gameobjects':selected,'case_details':details,
 'partial_creation_coverage':coverage,'model_file_sha256':hashlib.sha256(model_bytes).hexdigest(),'texture_file_sha256':hashlib.sha256(texture_bytes).hexdigest(),
 'io_calls':dict(io_calls),'gpu_calls':dict(gpu_calls),'index_calls':dict(index_calls),'crt_calls':dict(crt_calls),'scope':scope}
(folder/'training-scene-create-original.json').write_text(json.dumps(report,indent=2)+'\n')
print('REPORT',len(details),'cases',len(all_steps),'calls',flush=True)
