"""Actual QB descriptors and registered training nodes through the shared builder.
This is the four common components, not the complete468cb0 scripted assembly.
"""
from pathlib import Path
source=Path('local/analysis/probe-training-node-registration.py').read_text().split('regs=')[0]
exec(compile(source,'<preserved training loader/registration setup>','exec'))
from unicorn.x86_const import UC_X86_REG_ECX
OBJECTS=BASE+0xa1000;OM=BASE+0xa1900;SERVICES=BASE+0xa1a00;PROX=BASE+0xa1b00
EVENTS=BASE+0xb0000;ETABLES=BASE+0xbc000
memory[OBJECTS-BASE:OBJECTS-BASE+0x1000]=bytes(0x1000)
memory[EVENTS-BASE:EVENTS-BASE+0xc800]=bytes(0xc800)
put(OBJECTS,'<6I',OM,0x647814,0xffffffff,0,OBJECTS+4,OBJECTS+4)
put(OBJECTS+0x28,'<5I',0x6477e4,0xffffffff,0,OBJECTS+0x28,OBJECTS+0x28)
put(OM+4,'<I',0x461a00);put(OM+8,'<I',0x461a50);put(OM+12,'<I',0x4619a0)
put(SERVICES,'<2I',0,ADAPTER);put(MANAGER+0x11c,'<I',MANAGER+0x500);oracle.scope_entries[MANAGER+0x500]=6
tables=[ETABLES+i*128 for i in range(4)]
put(EVENTS,'<5I',0,0,*tables[:3]);put(EVENTS+0xb028,'<I',tables[3])
for t in tables:put(t,'<6I',2,t+32,0,0xffffffff,0,0)
types=[(0xce0ca665,0x434290,'suspend'),(0x0a015e17,0x426650,'motion'),(0x1d5b1ae6,0x4ec420,'object_proximity'),(0x07713c7b,0x433100,'object_sound')]
put(OBJECTS+0x44,'<I',4)
for i,(kind,factory,_) in enumerate(types):put(OBJECTS+0x48+8*i,'<2I',kind,factory)
def glob(name,at,value=0,width=4,offset=0):
 if at in index:defaults[index[at]]=value;return
 index[at]=len(globals_);globals_.append([name,at,width,offset]);defaults.append(value)
for name,at,value in [('thug_component_type_registry',0x6f0fb8,OBJECTS),('thug_object_lookup_manager',0x6f0fc0,EVENTS),
 ('thug_proximity_manager_draft',0x6f2268,PROX),('thug_sound_pending',0x6f85b0,0),('thug_sound_pending_count_draft',0x6f85bc,0),
 ('thug_frame_counter',0x7d1ec8,0),('thug_frame_rate',0x684fd0,0x42700000)]:glob(name,at,value)
for i in range(128):glob('thug_component_type_heads',0x6f0db8+i*4,0,offset=i*4)
for g in json.loads((ROOT/'local/validation/collision/ui-registry-fixtures.json').read_text())['globals']:
 if g[0] in {'thug_script_list','thug_script_count','thug_script_next_serial','thug_current_script','thug_script_pool_index','thug_script_pools','thug_script_branch_first','thug_script_branch_last','thug_script_branch_count','thug_script_listener_pool_index','thug_script_listener_pools'}:
  glob(g[0],g[1],0,g[2],g[3] if len(g)>3 else 0)
oracle.setword(0x684fe4,0x5df4ac)
exports=[[0x6f2364,'thug_script_loading_file'],[0x6efde0,'thug_node_prefix_results_draft'],[0x647814,'thug_ui_reference_list_methods'],
 [0x6477e4,'thug_ui_reference_list_methods'],[0x6477e0,'thug_ui_reference_node_methods'],[0x647650,'thug_composite_methods_draft'],[0x647618,'thug_component_methods']]
# Use exactly the already verified identity names for original object prefixes.
prior=json.loads((folder/'prop-lifecycle-fixtures.json').read_text())
exports=[e for e in exports if e[0] in [0x6f2364,0x6efde0]]+[e for e in prior['pointer_exports'] if e[0] not in [0x6f2364,0x6efde0]]
fields={CONTEXT+24,OBJECTS,OBJECTS+4,OBJECTS+0x28,OM+4,OM+8,OM+12}|{OBJECTS+0x4c+8*i for i in range(4)}
function_exports=[[0x461a00,'thug_object_manager_add'],[0x461a50,'thug_object_manager_remove'],[0x4619a0,'thug_object_manager_rename']]+[[a,'thug_'+n+'_create_draft'] for k,a,n in types]
def identities(cpu,at,size,user):
 p=cpu.reg_read(UC_X86_REG_ECX);fields.add(p)
 if at in [0x460b80,0x4615d0]:fields.update([p+0x28,p+0x40])
for a in [0x460b80,0x4615d0,0x45d730,0x433f50,0x424aa0,0x4ec370,0x432d90]:oracle.cpu.hook_add(UC_HOOK_CODE,identities,begin=a,end=a)
for a,name,argc,this,result,heap,diag in [(0x479070,'thug_script_get_global_array',2,False,'word',False,False),
 (0x45f3a0,'thug_composite_create_from_array_draft',3,True,'word',True,True),
 (0x45d890,'thug_composite_destroy_draft',0,True,'void',True,True)]:
 functions[hex(a)]={'name':name,'this':this,'result':result,'cleanup':argc*4 if this else 0,'stack_args':list(range(argc)),'memory':heap,'diagnostics':diag}
extra_assets=[];cursor=BASE+0x80000
for member in ['scripts/game/object.qb','scripts/game/skutils.qb']:
 raw=(ROOT/'local/game-files/Game/Data'/member).read_bytes();filename=cursor+len(raw)+16;encoded=member.encode()+b'\0'
 memory[cursor-BASE:cursor-BASE+len(raw)]=raw;memory[filename-BASE:filename-BASE+len(encoded)]=encoded
 extra_assets.append({'member':member,'address':cursor,'filename':filename,'size':len(raw),'sha256':hashlib.sha256(raw).hexdigest()});cursor=(filename+len(encoded)+19)&~3
assert cursor<TABLE
initial=bytes(memory);oracle.initial=initial
loads=[(0x472420,0,[a['filename'],a['address'],0,1,0]) for a in [*extra_assets,asset]]
prefix=loads+[(0x45d370,TABLE,[]),(0x45d520,TABLE,[key,1]),(0x479070,0,[0x735a20ba,0])]
# Preparation uses the actual loader/getters to determine addresses. The final
# comparison reruns all loading and registration before any component creation.
regs=[UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP]
before=[oracle.cpu.reg_read(r) for r in regs]
steps=oracle.case(prefix);array=steps[-1]['result'];assert array and oracle.word(array+4)==4
nodes=oracle.word(TABLE+0x1000c);items=oracle.word(nodes+8);selected=[];OUT=BASE+0xe800
def invoke(fn,this,args,cleanup):
 cpu=oracle.cpu;sp=oracle.stack+0x18000;cpu.mem_write(sp,struct.pack('<'+'I'*(len(args)+1),oracle.stop,*args));cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,this)
 cpu.emu_start(fn,oracle.stop,count=100000);assert cpu.reg_read(UC_X86_REG_EIP)==oracle.stop and cpu.reg_read(UC_X86_REG_ESP)==sp+4+cleanup
 return cpu.reg_read(UC_X86_REG_EAX)
def checksum(node,key):
 oracle.setword(OUT,0);invoke(0x476950,node,[key,OUT,0],12);return oracle.word(OUT)
for i in range(oracle.word(nodes+4)):
 node=oracle.word(items+4*i)
 if checksum(node,crc(b'Class'))==crc(b'GameObject'):selected.append({'index':i,'pointer':node,'name':checksum(node,crc(b'Name'))})
assert selected, 'No actual GameObject nodes selected'
oracle.cases.clear();oracle.counts.clear();oracle.coverage.clear();oracle.heap_events.clear()
calls=prefix[:];details=[]
# Retain the live original preparation state rather than reloading the full QB
# files for each node. The final comparison still replays the complete sequence.
for row in selected:
 obj=invoke(0x45f3a0,OBJECTS,[array,row['pointer'],1],12);assert obj
 invoke(0x45d890,obj,[],0)
 details.append({**row,'object':obj});calls += [(0x45f3a0,OBJECTS,[array,row['pointer'],1,0]),(0x45d890,obj,[0])]
 print('Prepared real training GameObject',row['index'],hex(row['name']),flush=True)
oracle.cases.clear();oracle.counts.clear();oracle.coverage.clear();oracle.heap_events.clear()
steps=oracle.case(calls)
assert [oracle.cpu.reg_read(r) for r in regs]==before
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
scope='Whole extracted object.qb, skutils.qb and TR.qb load; all1917training nodes register with link groups. For every Class=GameObject node, the actual gameobj_composite_structure array and unmodified registered node drive real four-component creation, initialization, finalization/moved and destruction. Script/registry/allocator services, an empty proximity manager and frame clock are explicit starting state. This is the shared four-component assembly, not468cb0: LockObj, gameobj_add_components, model/render components, triggers and complete scene boot remain.'
used={s['fn'] for s in steps};fixture={'base':BASE,'memory':'training-prop-components-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-loader-memory.wasm','memory_exports':['fixture_loader_allocate','fixture_loader_release','fixture_values_scope'],
 'globals':globals_,'functions':{k:v for k,v in functions.items() if k in used},'float_fields':[],'cases':oracle.cases,'case_labels':['actual training GameObject common components'],
 'pointer_symbols':parser['pointer_symbols'],'pointer_globals':[index[0x6f2560]],'pointer_exports':exports,'pointer_fields':sorted(fields),'function_exports':function_exports,'scoped_event_services':{'symbol':'thug_event_services','pointer':SERVICES},'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'training-prop-components-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':1,'calls':len(calls),'assets':[{k:a[k] for k in ['member','size','sha256']} for a in [*extra_assets,asset]],'nodes':1917,'props':details,'counts':dict(oracle.counts),'callees':dict(oracle.coverage),'scope':scope}
(folder/'training-prop-components-original.json').write_text(json.dumps(report,indent=2)+'\n');print('Real training common props:',len(details),'calls',len(calls),flush=True)
