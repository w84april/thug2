"""Run actual gameobj_add_components on a real training node until its first
unrecovered factory, plus a complete script path with no optional components.
The breakpoint supplies no component or successful return.
"""
from pathlib import Path
source=Path('local/analysis/probe-training-prop-components.py').read_text().split('loads=')[0]
exec(compile(source,'<preserved real training component setup>','exec'))
from unicorn.x86_const import *
SCRIPT,BOUNDARY,SYMBOL_AREA,DESCRIPTOR_AREA,PED,PEDNAME=BASE+0xc000,BASE+0xe000,BASE+0xa000,BASE+0xa800,BASE+0xc0000,BASE+0xef000
ped_path=ROOT/'local/game-files/Game/Data/scripts/game/ped.qb';ped=ped_path.read_bytes();assert len(ped)<PEDNAME-PED
memory[PED-BASE:PED-BASE+len(ped)]=ped;pn=b'scripts/game/ped.qb\0';memory[PEDNAME-BASE:PEDNAME-BASE+len(pn)]=pn
memory[SCRIPT-BASE:SCRIPT-BASE+244]=bytes(244);memory[BOUNDARY-BASE:BOUNDARY-BASE+16]=bytes(16)
state=json.loads((out/'script-state-fixtures.json').read_text())
for g in state['globals']:
 if g[1] not in index:glob(g[0],g[1],0,g[2],g[3] if len(g)>3 else 0)
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
newtypes=[(0x286a8d26,0x421490),(0x222756d5,0x431f60),(0x7149b753,0x41a5b0),(0xa432dc41,0x41c920),(0x0f1641e3,0x433d90),(0x3618b878,0x4f3550)]
put(OBJECTS+0x44,'<I',4+len(newtypes))
for i,(kind,factory) in enumerate(newtypes,4):put(OBJECTS+0x48+8*i,'<2I',kind,factory);fields.add(OBJECTS+0x4c+8*i)
native_hits=Counter();factory_hit=[]
def observe(cpu,at,size,user):
 if at in [a for _,a in newtypes]:
  params=oracle.word(SCRIPT+0x10);cpu.mem_write(BOUNDARY,struct.pack('<4I',at,params,SCRIPT,1));factory_hit.append(at);cpu.emu_stop()
 else:native_hits[hex(at)]+=1
for a in [a for _,a in newtypes]+[a for _,a,_ in native]+[0x45d810,0x45d850,0x45ee20,0x45f2a0]:oracle.cpu.hook_add(UC_HOOK_CODE,observe,begin=a,end=a)
def prepared(cpu,at,size,user):
 value=cpu.reg_read(UC_X86_REG_EAX)
 if value in [a for _,a,_ in native]:fields.add(cpu.reg_read(UC_X86_REG_ESI)-4)
oracle.cpu.hook_add(UC_HOOK_CODE,prepared,begin=0x46ff81,end=0x46ff81)
def identity_script(cpu,at,size,user):fields.add(cpu.reg_read(UC_X86_REG_ECX)+0xec)
oracle.cpu.hook_add(UC_HOOK_CODE,identity_script,begin=0x4738e0,end=0x4738e0)
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
  assert factory_hit==[0x421490] and cpu.reg_read(UC_X86_REG_EIP)==factory_hit[0],(factory_hit,hex(cpu.reg_read(UC_X86_REG_EIP)))
 after=bytes(cpu.mem_read(BASE,len(initial)));outputs=[]
 for page in range(0,len(initial),4096):
  if before[page:page+4096]!=after[page:page+4096]:
   for i in range(page,min(page+4096,len(initial)),4):
    if before[i:i+4]!=after[i:i+4]:outputs.append([BASE+i,after[i:i+4].hex()])
 steps.append({'fn':'0x4750b0','this':SCRIPT,'args':[0],'result':None if trapped else cpu.reg_read(UC_X86_REG_EAX),'outputs':outputs,'globals':[oracle.global_read(g) for g in globals_],'callbacks':0,'expected_trap':trapped})
 fields_in_params=[]
 if trapped:
  params=oracle.word(BOUNDARY+4);item=oracle.word(params+4)
  while item:
   fields_in_params.append({'name':hex(oracle.word(item+4)),'type':cpu.mem_read(item,1)[0]>>1,'value':hex(oracle.word(item+8))});item=oracle.word(item+12)
 details.append({'node_index':node_index,'node_name':hex(oracle.word(obj+0x14)),'completed_calls':len(calls)+(not trapped),'interrupted_calls':int(trapped),
                 'first_missing_factory':hex(factory_hit[0]) if trapped else None,'execute_result':None if trapped else 0,'final_instruction':hex(oracle.word(SCRIPT+12)),
                 'native_entries':dict(native_hits),'component_parameters':fields_in_params})
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
scope='Untouched object.qb/skutils.qb/ped.qb/TR.qb load and all1917nodes register in each case. Real training nodes204 and1289 drive four common components, then original gameobj_add_components executes with original native predicates and actual member descriptors. Node204 finishes with result0 and no optional component. Node1289 (SKATE letter S) reaches model factory421490 and stops before its first instruction. The test-only trap supplies neither a component nor success. This is verified script execution on real nodes, not full468cb0 construction, completed prop assembly or rendering.'
used={s['fn'] for s in steps}
fixture={'base':BASE,'memory':'training-prop-script-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-loader-memory.wasm','memory_exports':['fixture_loader_allocate','fixture_loader_release','fixture_values_scope'],
 'globals':globals_,'functions':{k:v for k,v in functions.items() if k in used},'float_fields':[],'cases':oracle.cases,'case_labels':['training node204 complete gameobj_add_components','training node1289 gameobj_add_components until model factory'],
 'pointer_symbols':parser['pointer_symbols'],'pointer_globals':[index[0x6f2560]],'pointer_exports':exports,'pointer_fields':sorted(fields),'function_exports':function_exports,
 'scoped_event_services':{'symbol':'thug_event_services','pointer':SERVICES},'native_callbacks':[{'module':'training-prop-script-boundary.wasm','export':'fixture_factory_'+hex(a)[2:],'original':a} for _,a in newtypes],
 'boundary_address':BOUNDARY,'boundary_factory':0x421490,'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'training-prop-script-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original script completes one node and reaches model factory on another; Wasm pending','specimen_sha256':SHA256,'cases':len(details),'calls':len(steps),
 'nodes':details,'assets':[{k:a[k] for k in ['member','size','sha256']} for a in [*extra_assets,ped_asset,asset]],'scope':scope}
(folder/'training-prop-script-original.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
