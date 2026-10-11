"""Original Input members, complete registration and actual named QB calls."""
from pathlib import Path
prefix=Path('local/analysis/probe-input-lifecycle.py').read_text().split('for fill in [0,0xa5,255]:')[0]
exec(compile(prefix,'<preserved Input startup oracle>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x41e7e0,110,'input_suppress_button',3,'void',False,False,True),
 (0x41e8f0,166,'input_command_suppress',2,'word',False,True,True),
 (0x41e9a0,14,'input_disable_player',2,'word',False,False,True),
 (0x41e9b0,15,'input_enable_player',2,'word',False,False,True),
 (0x41e9c0,14,'input_disable_network',2,'word',False,False,True),
 (0x41e9d0,15,'input_enable_network',2,'word',False,False,True),
 (0x41e9e0,51,'input_player_disabled',2,'word',False,False,True),
 (0x41ea20,13,'input_left_pressed',2,'word',False,False,True),
 (0x41ea30,16,'input_right_pressed',2,'word',False,False,True),
 (0x41ea40,13,'input_up_pressed',2,'word',False,False,True),
 (0x41ea50,13,'input_down_pressed',2,'word',False,False,True),
 (0x46c370,251,'input_stick_magnitude',3,'double',False,False,True),
 (0x41ea60,177,'input_read_sticks',2,'word',True,False,True),
 (0x41eb20,195,'input_held_longer',2,'word',False,False,True),
 (0x41e6f0,21,'input_register_commands',0,'void',True,False,False)]
for a,n,name,*rest in specs:bind_new(a,n,'thug_'+name+'_draft',*rest)
functions['0x41e7e0']['float_args']=[1];functions['0x46c370']['float_args']=[0,1,2]
for a,name,argc,result,heap,diag,this in [
 (0x41e850,'thug_input_construct_draft',0,'word',False,False,True),
 (0x41e7c0,'thug_input_enable_events_draft',2,'word',False,False,True),
 (0x41e7d0,'thug_input_disable_events_draft',2,'word',False,False,True),
 (0x41f090,'thug_input_primary_packet_draft',1,'void',True,True,True),
 (0x4738e0,'thug_script_initialize',0,'word',False,False,True),
 (0x474540,'thug_script_setup',4,'void',True,True,True),
 (0x4750b0,'thug_script_execute',0,'word',True,True,True),
 (0x474b40,'thug_script_invoke_command',0,'byte',True,True,True),
 (0x473a80,'thug_script_cleanup',0,'void',True,True,True),
 (0x45e510,'thug_composite_initialize_draft',0,'word',False,False,True),
 (0x45ee20,'thug_composite_add_parameters_draft',2,'void',True,True,True),
 (0x45db30,'thug_composite_finalize_draft',0,'void',True,True,True),
 (0x45d890,'thug_composite_destroy_draft',0,'void',True,True,True),
 (0x406a50,'thug_task_list_construct_draft',0,'word',False,False,True),
 (0x406ac0,'thug_task_list_update_draft',2,'void',True,True,True)]:bind(a,name,argc,result,heap,diag,this)
DIAG,DLOG=BASE+0xc9000,BASE+0xc9100
put(DIAG,'<2I',DLOG,0);put(SERVICES,'<2I',DIAG,ADAPTER)
def call(at,this=0,args=()):return at,this,[v&0xffffffff for v in args]+([DIAG] if functions[hex(at)].get('diagnostics') else [])
def debug_output(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);fmt=oracle.word(sp+4);file=oracle.word(sp+8)
 format_text=bytes(cpu.mem_read(fmt,64)).split(b'\0')[0];file_text=bytes(cpu.mem_read(file,64)).split(b'\0')[0]
 assert format_text==b'D:%s:%i: time = %g\n' and file_text==b'omponents\\InputComponent.cpp'
 count=oracle.word(DLOG);oracle.setword(DLOG,count+1);row=bytearray(128)
 row[:len(format_text)]=format_text;row[32:32+len(file_text)]=file_text
 row[96:100]=cpu.mem_read(sp+12,4);row[104:112]=cpu.mem_read(sp+16,8)
 cpu.mem_write(DLOG+16+128*count,bytes(row))
 target=oracle.word(DLOG+4)
 if target:oracle.setword(target,oracle.word(DLOG+8))
 cpu.reg_write(UC_X86_REG_EAX,0xffffffff);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
oracle.cpu.hook_add(UC_HOOK_CODE,debug_output,begin=0x401c30,end=0x401c30)
extra['native_callbacks']=[{'module':'input-command-diagnostic-fixture.wasm','export':'fixture_input_command_print','slots':[DIAG+4]}]
# Execute the original static initializer and verify every descriptor byte.
initializer_hits=Counter()
oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:initializer_hits.update([at]),begin=0x6445b0,end=0x64475c)
sp=oracle.stack+0x18000;oracle.cpu.mem_write(sp,struct.pack('<I',oracle.stop));oracle.cpu.reg_write(UC_X86_REG_ESP,sp)
oracle.cpu.emu_start(0x6445b0,oracle.stop,count=200)
assert oracle.cpu.reg_read(UC_X86_REG_EIP)==oracle.stop and oracle.cpu.reg_read(UC_X86_REG_ESP)==sp+4
metadata=json.loads((folder/'input-component-descriptor-bindings.json').read_text());rows=metadata['entries']+[metadata['terminator']]
table_bytes=b''.join(struct.pack('<6I',int(row['name_checksum'],16),int(row['component_type'],16),int(row['member'],16),row['receiver_offset'],row['word_10'],row['word_14']) for row in rows)
assert bytes(oracle.cpu.mem_read(0x684c78,360))==table_bytes and len(initializer_hits)==82
for i in range(15):exports.append([0x684c78+24*i,'thug_input_commands_draft',24*i])
for row in metadata['entries']:
 address=int(row['member'],16);name=functions[hex(address)]['name']
 if address==0x41e8f0:name='thug_input_suppress_command_bridge_draft'
 if address==0x41ea60:name='thug_input_read_sticks_bridge_draft'
 function_exports.append([address,name])
 oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=address,end=address)
for at in [0x46f060,0x479110,0x474b40,0x474bd0,0x42bb20,0x46c270,0x46b920]:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
initial=bytes(memory);oracle.initial=initial
BUTTON_NAMES=['UP','DOWN','LEFT','RIGHT','SQUARE','CIRCLE','TRIANGLE','X','L1','L2','L3','R1','R2','R3','START','SELECT']
BUTTON_OFFSETS=[0,0x20,0x40,0x60,0x160,0x140,0x180,0x1a0,0x80,0xa0,0xc0,0xe0,0x100,0x120,0x1c0,0x1e0]
class CommandGraph(LifecycleGraph):
 def __init__(self):
  super().__init__();self.image[DLOG-BASE:DLOG-BASE+0x1000]=bytes(0x1000)
  self.put(P,'<2I',0x64605c,0x27d7cd28);fields.add(P);self.put(OBJ+0x100,'<I',P)
  for name,off in zip(BUTTON_NAMES,BUTTON_OFFSETS):self.put(P+0x20+off+0x18,'<I',crc(name))
  self.script=self.alloc(244);self.image[self.script-BASE:self.script-BASE+244]=bytes(244)
  self.output=self.structure([]);self.put(self.script+0x14,'<I',self.output)
 def program(self,data):
  code=self.alloc(len(data));self.image[code-BASE:code-BASE+len(data)]=data;return code
 def run(self,calls,label,changes=None):
  stages=super().run(calls,label,changes)
  if any(fn==0x41e6f0 for fn,_,_ in calls):
   for row in metadata['entries']:
    name=int(row['name_checksum'],16);symbol=oracle.word(SYMBOLS+(name&4095)*4)
    while symbol and oracle.word(symbol+4)!=name:symbol=oracle.word(symbol+16)
    assert symbol and oracle.cpu.mem_read(symbol+1,1)[0]==9
    assert oracle.word(symbol+12)==0x684c78+row['index']*24
  return stages
def command(g,fn,s=None):return call(fn,P,[s if s is not None else g.structure([]),g.script])
for a,b in itertools.product([0,1,2,255],[0,1,255]):
 g=CommandGraph();g.put(P+0x498,'<2B',a,b)
 g.run([command(g,0x41e9e0)]+[command(g,fn) for fn in [0x41e9a0,0x41e9e0,0x41e9b0,0x41e9e0,0x41e9c0,0x41e9e0,0x41e9d0,0x41e9e0]],f'disable flags/{a}/{b}')
for fn,off in [(0x41ea20,0x60),(0x41ea30,0x80),(0x41ea40,0x20),(0x41ea50,0x40)]:
 for held,edge in itertools.product([0,1,2,255],[0,1,255]):
  g=CommandGraph();g.put(P+off,'<B',held);g.put(P+off+0x10,'<B',edge)
  stages=g.run([command(g,fn)],f'held rather than edge/{fn:x}/{held}/{edge}');assert stages[0]['result']==bool(held)
for index_,name in enumerate(BUTTON_NAMES):
 for clear in [0,1,256,257,0xffffffff]:
  g=CommandGraph();button=P+0x20+BUTTON_OFFSETS[index_];g.put(button,'<B',1);g.put(button+0x10,'<2I',0xa5a50101,0x5555)
  g.run([call(0x41e7e0,P,[crc(name),bits(.25),clear])],f'all named suppression/{name}/{clear}')
for now,seconds in itertools.product([0,1000,0x7fffffff,0x80000000,0xffffffff],[0,0x80000000,bits(-1),bits(.0005),bits(1.25),bits(2147484),0x7f800000,0xff800000,0x7fc00000]):
 g=CommandGraph();g.run([call(0x41e7e0,P,[crc('UP'),seconds,1])],f'suppression arithmetic/{now}/{seconds:x}',{0x7d1ec8:now})
for have_name,seconds,clear in itertools.product([False,True],[None,bits(0),bits(.125),bits(-2),bits(123.75)],[None,0,1,256,0xffffffff]):
 g=CommandGraph();items=[(0,13,crc('X'))] if have_name else []
 if seconds is not None:items.append((0x906b67ba,2,seconds))
 if clear is not None:items.append((0x1a4e0ef9,1,clear))
 g.run([command(g,0x41e8f0,g.structure(items))],f'suppression command defaults/{have_name}/{seconds}/{clear}')
# The diagnostic service may mutate a later parameter; original getters reload it.
g=CommandGraph();params=g.structure([(0,13,crc('UP')),(0x1a4e0ef9,1,0)])
member=g.word(g.word(params+4)+12);g.put(DLOG+4,'<2I',member+8,1);g.put(P+0x20,'<B',1)
g.run([command(g,0x41e8f0,params)],'diagnostic callback mutates later clear parameter')
units=[[],[0xd029f619],[0x49e0ee96],[0x019176c5],[0x4a07c332],[0x019176c5,0xd029f619],[0x123]]
for unit,elapsed,duration,held in itertools.product(units,[0,999,1000,1001,0xffffffff],[bits(0),bits(1),bits(1000),bits(-1)],[0,1]):
 g=CommandGraph();g.put(P+0x20,'<BI',held,0);g.put(P+0x24,'<I',(1000-elapsed)&0xffffffff)
 params=g.structure([(0xc5f953c2,13,crc('UP')),(0,2,duration)]+[(0,13,u) for u in unit])
 g.run([command(g,0x41eb20,params)],f'held strict unsigned threshold/{unit}/{elapsed}/{duration:x}/{held}')
for name in BUTTON_NAMES+['unknown']:
 g=CommandGraph()
 for off in BUTTON_OFFSETS:g.put(P+0x20+off,'<B',1)
 g.run([command(g,0x41eb20,g.structure([(0xc5f953c2,13,crc(name)),(0,2,bits(0))]))],'held button lookup/'+name)
angles=[-4,-3.1415927,-2.3561945,-1.5707964,-.7853982,-.7853981,-.1,0,.1,.7853981,.7853982,1.5707964,2.3561945,3.1415927,4]
for x,y,angle in itertools.product([-128,-64,0,64,127],[-128,0,127],angles):
 g=CommandGraph();g.run([call(0x46c370,P,[bits(x),bits(y),bits(angle)])],f'stick magnitude/{x}/{y}/{angle}')
rng=random.Random(0x41ea60)
for i in range(80):
 g=CommandGraph()
 for off in [0x220,0x224,0x228,0x22c]:g.put(P+off,'<f',rng.uniform(-128,127))
 for off in [0x240,0x248]:g.put(P+off,'<f',rng.uniform(-3.1416,3.1416))
 g.put(g.script+0x14,'<I',g.structure([(0x737f15cf,1,17),(0x686ad1c2,2,bits(3)),(0xd6030cea,3,g.text('replace'))]))
 g.run([command(g,0x41ea60)]*2,f'stick output replacement/{i}')
for repeats in [1,2,4]:
 g=CommandGraph();g.run([call(0x41e6f0)]*repeats,'complete registration/'+str(repeats))
def token(kind,value):return bytes([kind])+struct.pack('<I',value)
def qb_parameters(fn):
 if fn==0x41e8f0:return token(0x16,crc('UP'))+token(0x16,0x906b67ba)+b'\x07'+token(0x1a,bits(.25))
 if fn==0x41eb20:return token(0x16,0xc5f953c2)+b'\x07'+token(0x16,crc('UP'))+token(0x1a,bits(1))+token(0x16,0xd029f619)
 return b''
named_dispatches={}
for row in metadata['entries']:
 g=CommandGraph();fn=int(row['member'],16);name=int(row['name_checksum'],16)
 program=g.program(b'\x01'+token(0x16,name)+qb_parameters(fn)+b'\x01\x24')
 before=oracle.coverage[hex(fn)]
 g.run([call(0x41e6f0),call(0x4738e0,g.script),call(0x474540,g.script,[0,program,0,OBJ]),call(0x4750b0,g.script)],'real named QB command/'+row['name_checksum'])
 named_dispatches[row['name_checksum']]=oracle.coverage[hex(fn)]-before
 assert named_dispatches[row['name_checksum']]>0
# Full shared Input creation, named script execution and device task updates.
g=CommandGraph();g.registry([(0x27d7cd28,0x41eec0)]);descriptor=g.structure([(0xb6015ea8,13,0x27d7cd28),(0xb30d9965,1,0)])
program=g.program(b'\x01'+b''.join(token(0x16,int(row['name_checksum'],16))+qb_parameters(int(row['member'],16))+b'\x01' for row in metadata['entries'])+b'\x24')
g.run(g.lists()+[call(0x45e510,OBJ),call(0x45ee20,OBJ,[descriptor,0]),call(0x45db30,OBJ),call(0x41e6f0),
 call(0x4738e0,g.script),call(0x474540,g.script,[0,program,0,OBJ]),call(0x4750b0,g.script),
 call(0x406ac0,L0,[0,0]),call(0x406ac0,L1,[0,0]),call(0x473a80,g.script),call(0x45d890,OBJ)],'shared Input startup/all named QB commands/tasks/cleanup')
scope='15 original routines complete all14 Input command descriptors: disable/enable flags, held directions, suppression deadlines and optional clearing, stick output and its magnitude helper, held duration predicates and full registration. Original6445b0 initializer establishes all360 descriptor bytes; every registered symbol identity is checked. Real named QB scripts invoke all14 members, including shared Input startup, both task lists and cleanup. Debug formatter401c30 is an explicit platform boundary retaining format, source, line, double arguments and ordering, including mutation of a later parameter. Required HeldLongerThan arguments and valid suppression button names are original contracts. Whole arena,globals,heap,returns compare. Existing SDK trigonometric adapter is not a claim of physical x87 accuracy. Full skater startup and playable rendering remain unfinished.'
report_coverage={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
used={s['fn'] for c in oracle.cases for s in c['steps']}
fixture={'base':BASE,'memory':'input-command-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm',
 'memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,
 'functions':{k:v for k,v in functions.items() if k in used},'float_fields':[],'cases':oracle.cases,'case_labels':labels,
 'scope':scope,'pointer_exports':exports,'pointer_fields':sorted(fields),
 'descriptor_rows':[{'words':list(struct.unpack_from('<6I',table_bytes,24*i)),
 'member':next((name for original,name in function_exports if original==int(row['member'],16)),None)} for i,row in enumerate(rows)],**extra}
(folder/fixture['memory']).write_bytes(initial);(folder/'input-command-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(oracle.counts.values()),
 'instruction_coverage':report_coverage,'counts':dict(oracle.counts),'callees':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),
 'initializer_instructions':len(initializer_hits),'table_bytes':len(table_bytes),'table_sha256':hashlib.sha256(table_bytes).hexdigest(),
 'named_qb_member_dispatches':named_dispatches,'scope':scope}
(folder/'input-command-original.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['callees','counts','scope']}),flush=True)
