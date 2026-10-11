"""Actual training node loads its texture and reaches missing model-file handler."""
from pathlib import Path
source=Path('local/analysis/probe-training-prop-components.py').read_text().split('loads=')[0]
exec(compile(source,'<preserved real training component setup>','exec'))
from unicorn.x86_const import *
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
from specimen import load
pe=load()
SCRIPT,BOUNDARY,SYMBOL_AREA,DESCRIPTOR_AREA,PED,PEDNAME=BASE+0xc000,BASE+0xe000,BASE+0xa000,BASE+0xa800,BASE+0xc0000,BASE+0xef000
ped_path=ROOT/'local/game-files/Game/Data/scripts/game/ped.qb';ped=ped_path.read_bytes();assert len(ped)<PEDNAME-PED
memory[PED-BASE:PED-BASE+len(ped)]=ped;pn=b'scripts/game/ped.qb\0';memory[PEDNAME-BASE:PEDNAME-BASE+len(pn)]=pn
memory[SCRIPT-BASE:SCRIPT-BASE+244]=bytes(244);memory[BOUNDARY-BASE:BOUNDARY-BASE+576]=bytes(576)
state=json.loads((out/'script-state-fixtures.json').read_text())
for g in state['globals']:
 if g[1] not in index:glob(g[0],g[1],0,g[2],g[3] if len(g)>3 else 0)
for off in range(0,24,4):glob('thug_model_texture_table_draft',0x700f04+off,0,offset=off)
glob('thug_model_light_factor_count_draft',0x6faae0,0);glob('thug_model_directional_count_draft',0x6faae4,0)
glob('thug_script_cache',0x6f3558,CACHE);glob('thug_script_next_serial',0x6f3540,1)
functions['0x4738e0']={'name':'thug_script_initialize','this':True,'result':'word','cleanup':0,'stack_args':[]}
functions['0x474540']={'name':'thug_script_setup','this':True,'result':'void','cleanup':16,'memory':True,'stack_args':[0,1,2,3]}
functions['0x4750b0']={'name':'thug_script_execute','this':True,'result':'word','cleanup':0,'memory':True,'stack_args':[]}
# Actual native binding addresses and CRT-initialized member descriptors.
native=[('GotParam',0x44bd30,'thug_script_got_parameter_draft'),('ChecksumEquals',0x44a260,'thug_script_checksums_equal_draft'),('StringEquals',0x44a2c0,'thug_script_strings_equal_draft')]
metadata={r['name']:r for r in json.loads((folder/'script-bindings.json').read_text())}
for n,a,_ in native:assert int(metadata[n]['address'],16)==a
members=[(0x406998a5,0x45d810,'thug_composite_create_component_command_draft'),(0x2bffeaa3,0x45dbf0,'thug_composite_contains_command_draft')]
for i,(key,fn,export) in enumerate(members):
 d=DESCRIPTOR_AREA+i*24;put(d,'<6I',key,0x0ada4e74,fn,0,0,0);fields.add(d+8);function_exports.append([fn,export])
rows=[(crc(n.encode()),8,a) for n,a,_ in native]+[(key,9,DESCRIPTOR_AREA+i*24) for i,(key,*_) in enumerate(members)]
for i,(key,kind,value) in enumerate(rows):
 p=SYMBOL_AREA+i*20;bucket=BUCKETS+(key&4095)*4;previous=struct.unpack_from('<I',memory,bucket-BASE)[0]
 put(p,'<BBH4I',0x91,kind,0,key,0,value,previous);put(bucket,'<I',p)
 if kind==8:fields.add(p+12)
function_exports += [[a,e] for _,a,e in native]
exports += [[0x649348,'thug_model_renderer_base_methods_draft'],[0x64a4b4,'thug_model_renderer_methods_draft'],[0x646128,'thug_model_component_methods_draft']]
function_exports.append([0x421490,'thug_model_component_create_draft'])
for a in [0x494c40,0x4bad90,0x420bf0]:oracle.cpu.hook_add(UC_HOOK_CODE,identities,begin=a,end=a)
newtypes=[(0x286a8d26,0x421490),(0x222756d5,0x431f60),(0x7149b753,0x41a5b0),(0xa432dc41,0x41c920),(0x0f1641e3,0x433d90),(0x3618b878,0x4f3550)]
put(OBJECTS+0x44,'<I',4+len(newtypes))
for i,(kind,factory) in enumerate(newtypes,4):put(OBJECTS+0x48+8*i,'<2I',kind,factory);fields.add(OBJECTS+0x4c+8*i)
native_hits=Counter();factory_hit=[];active_model={}
configuration_code=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(0x20d10,1304),0x420d10));configuration_hits=Counter()
def configuration_trace(cpu,at,size,user):configuration_hits[at]+=1
oracle.cpu.hook_add(UC_HOOK_CODE,configuration_trace,begin=0x420d10,end=0x421227)
def observe(cpu,at,size,user):
 if at==0x420d10:
  active_model['component']=cpu.reg_read(UC_X86_REG_ECX);active_model['parameters']=oracle.word(cpu.reg_read(UC_X86_REG_ESP)+4)
 if at==0x48c030:
  sp=cpu.reg_read(UC_X86_REG_ESP);a=[oracle.word(sp+4+i*4) for i in range(8)]
  values=[at,a[0],a[1],1,*a[2:]];cpu.mem_write(BOUNDARY,struct.pack('<10I',*values))
  factory_hit.append(at);cpu.emu_stop()
 elif at in [a for _,a in newtypes if a!=0x421490]:
  cpu.mem_write(BOUNDARY,struct.pack('<4I',at,oracle.word(SCRIPT+0x10),SCRIPT,1));factory_hit.append(at);cpu.emu_stop()
 else:native_hits[hex(at)]+=1
for a in [0x48c030,0x4935e0,0x420d10,0x494ba0,0x487b00,0x492ee0,0x487a70,0x402080,0x4214f0,0x532eb0,0x492e90,0x420bf0,0x48bfa0,0x4b29c0,0x4bad90,0x494c40]+[a for _,a in newtypes]+[a for _,a,_ in native]+[0x45d810,0x45d850,0x45ee20,0x45f2a0]:oracle.cpu.hook_add(UC_HOOK_CODE,observe,begin=a,end=a)
def prepared(cpu,at,size,user):
 value=cpu.reg_read(UC_X86_REG_EAX)
 if value in [a for _,a,_ in native]:fields.add(cpu.reg_read(UC_X86_REG_ESI)-4)
oracle.cpu.hook_add(UC_HOOK_CODE,prepared,begin=0x46ff81,end=0x46ff81)
def identity_script(cpu,at,size,user):fields.add(cpu.reg_read(UC_X86_REG_ECX)+0xec)
oracle.cpu.hook_add(UC_HOOK_CODE,identity_script,begin=0x4738e0,end=0x4738e0)
exec(compile(Path('local/analysis/training-model-file-ports-setup.py').read_text(),'<explicit texture platform ports>','exec'))
initial=bytes(memory);oracle.initial=initial
ped_asset={'member':'scripts/game/ped.qb','address':PED,'filename':PEDNAME,'size':len(ped),'sha256':hashlib.sha256(ped).hexdigest()}
loads=[(0x472420,0,[a['filename'],a['address'],0,1,0]) for a in [*extra_assets,ped_asset,asset]]
prefix=loads+[(0x45d370,TABLE,[]),(0x45d520,TABLE,[crc(b'TR_NodeArray'),1]),(0x479070,0,[0x735a20ba,0])]
# Each case restarts from the same untouched files and explicit service state.
steps=oracle.case(prefix);array=steps[-1]['result'];nodes=oracle.word(TABLE+0x1000c);items=oracle.word(nodes+8)
selected=[(i,oracle.word(items+i*4)) for i in [204,1289]]
oracle.cases.clear();details=[];all_steps=[]
regs=[UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP]
for node_index,node in selected:
 assert node
 calls=prefix+[(0x45f3a0,OBJECTS,[array,node,0,0]),(0x4738e0,SCRIPT,[])]
 prepared_steps=oracle.case(calls);obj=prepared_steps[-2]['result'];oracle.cases.pop()
 calls += [(0x474540,SCRIPT,[0xf3b84da6,0,node,obj,0])]
 native_hits.clear();factory_hit.clear()
 steps=oracle.case(calls)
 before=bytes(oracle.cpu.mem_read(BASE,len(initial)));sp=oracle.stack+0x18000;cpu=oracle.cpu
 saved_regs=[cpu.reg_read(r) for r in regs]
 cpu.mem_write(sp,word(oracle.stop));cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,SCRIPT);cpu.reg_write(UC_X86_REG_FPCW,0x7f)
 cpu.emu_start(0x4750b0,oracle.stop,count=5000000)
 trapped=bool(factory_hit)
 if node_index==204:
  assert not trapped and cpu.reg_read(UC_X86_REG_EIP)==oracle.stop
  assert cpu.reg_read(UC_X86_REG_EAX)==0 and oracle.word(SCRIPT+12)==0
  assert cpu.reg_read(UC_X86_REG_ESP)==sp+4 and [cpu.reg_read(r) for r in regs]==saved_regs
 else:
  assert factory_hit==[0x48c030] and cpu.reg_read(UC_X86_REG_EIP)==factory_hit[0],(factory_hit,hex(cpu.reg_read(UC_X86_REG_EIP)))
 after=bytes(cpu.mem_read(BASE,len(initial)));outputs=[]
 for page in range(0,len(initial),4096):
  if before[page:page+4096]!=after[page:page+4096]:
   for i in range(page,min(page+4096,len(initial)),4):
    if before[i:i+4]!=after[i:i+4]:outputs.append([BASE+i,after[i:i+4].hex()])
 steps.append({'fn':'0x4750b0','this':SCRIPT,'args':[0],'result':None if trapped else cpu.reg_read(UC_X86_REG_EAX),'outputs':outputs,'globals':[oracle.global_read(g) for g in globals_],'callbacks':0,'expected_trap':trapped})
 fields_in_params=[]
 if trapped:
  params=active_model['parameters'];item=oracle.word(params+4)
  while item:
   fields_in_params.append({'name':hex(oracle.word(item+4)),'type':cpu.mem_read(item,1)[0]>>1,'value':hex(oracle.word(item+8))});item=oracle.word(item+12)
 model_state=None
 if trapped:
  component=active_model['component'];renderer=oracle.word(component+0x208);head=oracle.word(renderer+0x10)
  assert oracle.word(component)==0x646128 and oracle.word(component+4)==0x286a8d26 and oracle.word(component+12)==obj
  assert oracle.word(renderer)==0x64a4b4 and oracle.word(head+4)==head and oracle.word(head+8)==head
  chain=[];c=oracle.word(obj+0x100)
  while c:chain.append(oracle.word(c+4));c=oracle.word(c+16)
  assert len(chain)==5 and chain[-1]==0x286a8d26
  model_state={'component':hex(component),'renderer':hex(renderer),'sentinel':hex(head),'owner_components':[hex(v) for v in chain],'renderer_flags':cpu.mem_read(renderer+0x44,1)[0],'lights':hex(oracle.word(renderer+0x2c)),'skeleton_data':hex(oracle.word(renderer+12))}
 if trapped:
  texture_asset=oracle.word(AM+0x20);asset_ptr=oracle.word(oracle.word(texture_asset+0x48)+4);dictionary=oracle.word(texture_asset+0x10)
  assert oracle.word(asset_ptr)==0x645888 and oracle.word(asset_ptr+8)==1
  assert oracle.word(texture_asset)==0x6459a8 and oracle.word(texture_asset+8)==4
  assert oracle.word(ATABLE+8)==1 and oracle.word(AM+0x20)==texture_asset
  assert oracle.word(texture_asset+0x20)==0 and oracle.word(texture_asset+0x4c)==0 and oracle.word(0x6918d8)==1
  assert oracle.word(dictionary)==0x64a824 and oracle.word(dictionary+8)&0xffff==1
  assert oracle.word(oracle.word(dictionary+12)+8)==1
  dependency_link=oracle.word(texture_asset+0x48);assert oracle.word(dependency_link+4)==asset_ptr
  assert bytes(cpu.mem_read(oracle.word(texture_asset+0x24),len(texture_bytes)))==texture_bytes
  assert bytes(cpu.mem_read(TEXTURES+0x100,32))==texture_bytes[44:76] and bytes(cpu.mem_read(TEXTURES+0x200,8))==texture_bytes[80:88]
  assert oracle.word(CONTROL+4)==1 and oracle.word(IOC+12)==7
  model_state['texture_asset']={'asset':hex(texture_asset),'dictionary':hex(dictionary),'buffer':hex(oracle.word(texture_asset+0x24)),'state':4,'key':hex(oracle.word(texture_asset+4)),'dependent_model_asset':hex(asset_ptr),'mip_bytes':[32,8]}
  assert oracle.word(asset_ptr+0x20)==MODELFILE and oracle.word(asset_ptr+0x28)==len(model_bytes) and oracle.word(asset_ptr+0x5c)==0
  assert bytes(cpu.mem_read(oracle.word(asset_ptr+0x24),len(model_bytes)))==model_bytes
  model_state['model_asset']={'asset':hex(asset_ptr),'buffer':hex(oracle.word(asset_ptr+0x24)),'bytes':len(model_bytes),'state':1,'pending_reads':0}
  texname=b'models\\gameobjects\\skate\\letter_s\\letter_s.tex'
  defined={0,*range(4,12),16,17,*range(20,10+len(texname)+1)}
  undefined=sorted(set(range(76))-defined)
  masks={}
  for off in range(0,76,4):
   mask=sum(255<<(8*j) for j in range(4) if off+j in defined)
   if mask!=0xffffffff:masks[str(index[0x691758+off])]=mask
  steps[-1]['global_bit_masks']=masks
  model_state['indeterminate_texture_option_bytes']=undefined
 details.append({'model_state':model_state,'node_index':node_index,'node_name':hex(oracle.word(obj+0x14)),'completed_calls':len(calls)+(not trapped),'interrupted_calls':int(trapped),
                 'first_missing_routine':hex(factory_hit[0]) if trapped else None,'execute_result':None if trapped else 0,'final_instruction':hex(oracle.word(SCRIPT+12)),
                 'native_entries':dict(native_hits),'component_parameters':fields_in_params,'model_buffer_request':{'key':hex(oracle.word(BOUNDARY+4)),'data':hex(oracle.word(BOUNDARY+8)),'arguments':list(struct.unpack('<6I',cpu.mem_read(BOUNDARY+16,24)))} if trapped else None})
 all_steps.extend(steps)
 print('SCRIPT TRACE',details[-1],flush=True)
steps=all_steps
for i in range(oracle.word(CONTEXT+8)):
 for j in [4,5,6,7,9,10]:fields.add(LOG+i*48+j*4)
for step in steps:
 for at,data in step['outputs']:
  if int.from_bytes(bytes.fromhex(data),'little') in {e[0] for e in exports}:fields.add(at)
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
scope='Untouched training scripts register1917 nodes. Node204 completes; node1289 loads the real Letter S texture and all4710 model-file bytes through the recovered manager and file loader. Execution stops explicitly before48c030 model parsing, after validating the dependency texture and all eight parser arguments. Complete arena, heap, I/O and mip bytes compare; only proven uninitialized option padding is masked. File/GPU providers remain comparison fixtures. Model geometry, rendering and a playable level remain unavailable.'
used={s['fn'] for s in steps}
fixture={'base':BASE,'memory':'training-model-file-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-loader-memory.wasm','memory_exports':['fixture_loader_allocate','fixture_loader_release','fixture_values_scope'],
 'globals':globals_,'functions':{k:v for k,v in functions.items() if k in used},'float_fields':[],'cases':oracle.cases,'case_labels':['training node204 complete gameobj_add_components','training node1289 gameobj_add_components through text-model configuration prefix'],
 'pointer_symbols':parser['pointer_symbols'],'pointer_globals':[index[0x6f2560]],'pointer_exports':exports,'pointer_fields':sorted(fields),'function_exports':function_exports,
 'scoped_event_services':{'symbol':'thug_event_services','pointer':SERVICES},'native_callbacks':[{'module':'training-model-file-boundary.wasm','export':'fixture_factory_'+hex(a)[2:],'original':a} for _,a in newtypes if a!=0x421490]+[{'module':'training-model-file-boundary.wasm','export':'fixture_model_buffer','original':0x48c030}],
 'pointer_initializers':[['thug_model_buffer_pending_draft',0x48c030,0],['thug_texture_allocation_scope_draft',oracle.stop+0x330,0]],
 'component_initializer_boundary':True,'boundary_address':BOUNDARY,'boundary_factory':0x48c030,'scope':scope}
fixture['native_callbacks'] += [{'module':'training-texture-gpu.wasm','export':'fixture_texture_'+n,'slots':slots,**({'original':oracle.stop+0x330} if n=='scope' else {})} for n,slots in [('create',[DVT+0x5c]),('lock',[TVT+0x4c]),('unlock',[TVT+0x50]),('scope',[])]]
fixture['native_callbacks'] += [{'module':'training-model-file-io.wasm','export':'fixture_training_'+n,'slots':[IO+(i+1)*4]} for i,n in enumerate(['open','size','read','close'])]
(folder/fixture['memory']).write_bytes(initial);(folder/'training-model-file-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original script completes one node and loads the Letter S texture before missing model-buffer48c030 on another; Wasm pending','specimen_sha256':SHA256,'cases':len(details),'calls':len(steps),
 'partial_model_load':{'address':'0x4935e0','boundary':'0x48c030','complete':False,'covered_instructions':sum(bool(model_load_hits[i.address]) for i in model_load_code),'total_instructions':len(model_load_code),'executed':[hex(i.address) for i in model_load_code if model_load_hits[i.address]]},'io_calls':dict(io_calls),'gpu_calls':dict(gpu_calls),'model_file_coverage':{'covered':sum(bool(model_file_hits[i.address]) for i in model_file_code),'total':len(model_file_code),'executed':[hex(i.address) for i in model_file_code if model_file_hits[i.address]]},'model_file_sha256':hashlib.sha256(model_bytes).hexdigest(),'model_file_bytes':len(model_bytes),'texture_file_sha256':hashlib.sha256(texture_bytes).hexdigest(),'partial_configuration':{'address':'0x420d10','boundary':'0x48c030','covered_instructions':sum(bool(configuration_hits[i.address]) for i in configuration_code),'total_instructions':len(configuration_code),'executed':[hex(i.address) for i in configuration_code if configuration_hits[i.address]],'complete':False},'nodes':details,'assets':[{k:a[k] for k in ['member','size','sha256']} for a in [*extra_assets,ped_asset,asset]],'scope':scope}
(folder/'training-model-file-original.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
