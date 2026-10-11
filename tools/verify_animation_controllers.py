"""Compare five concrete animation controller lifecycles/configuration/commands."""
from pathlib import Path
prefix=Path(__file__).with_name('verify_animation_assets.py').read_text().split('rng=random.Random(0x4a4af0)')[0]
exec(compile(prefix.replace("'animation-assets.json'","'animation-controllers.json'"),str(Path(__file__).with_name('verify_animation_assets.py')),'exec'))
NEW=[
 (0x481640,'thug_animation_update_time',0,'void',False,False,True),
 (0x4813f0,'thug_animation_timeline_finished',0,'byte',False,False,True),
 (0x476fb0,'thug_script_get_vector',3,'byte',False,False,True),
 (0x405ef0,'thug_vector_degrees_to_radians',0,'void',False,False,True),
 (0x47d620,'thug_animation_state_duration',1,'double',False,True,True),
 (0x419af0,'thug_animation_component_duration',1,'double',False,True,True),
 (0x487770,'thug_animation_parse_loop',2,'byte',False,False,False),
 (0x4877e0,'thug_animation_parse_range',6,'byte',False,False,False),
 (0x4a5350,'thug_timed_animation_initialize',1,'word',True,True,True),
 (0x4a4d50,'thug_timed_animation_destroy',0,'void',True,False,True),
 (0x4a5400,'thug_timed_animation_delete',1,'word',True,False,True),
 (0x4a4dd0,'thug_timed_animation_configure',1,'void',True,True,True),
 (0x4a54a0,'thug_timed_animation_command',3,'word',True,True,True),
 (0x4a5010,'thug_weighted_animation_initialize',2,'word',True,True,True),
 (0x4a4820,'thug_weighted_animation_destroy',0,'void',True,False,True),
 (0x4a50b0,'thug_weighted_animation_delete',1,'word',True,False,True),
 (0x4a4890,'thug_weighted_animation_command',3,'word',True,True,True),
 (0x4e2c50,'thug_flag_animation_initialize',1,'word',False,False,True),
 (0x4e2c80,'thug_flag_animation_destroy',0,'void',False,False,True),
 (0x4e2cf0,'thug_flag_animation_delete',1,'word',True,False,True),
 (0x4e2c90,'thug_flag_animation_configure',1,'void',True,True,True),
 (0x4a5730,'thug_pose_animation_initialize',1,'word',False,False,True),
 (0x4a4d20,'thug_pose_animation_destroy',0,'void',False,False,True),
 (0x4a5320,'thug_pose_animation_delete',1,'word',True,False,True),
 (0x51adc0,'thug_animation_unhandled_command',3,'word',True,True,True),
 (0x488300,'thug_bone_animation_initialize',2,'word',False,False,True),
 (0x487d40,'thug_bone_animation_destroy',0,'void',False,False,True),
 (0x4880d0,'thug_bone_animation_delete',1,'word',True,False,True),
 (0x487d60,'thug_bone_animation_find',1,'word',False,False,True),
 (0x487d90,'thug_bone_animation_all_enabled',0,'byte',False,False,True),
 (0x487dc0,'thug_bone_animation_enable_all',0,'void',False,False,True),
 (0x487de0,'thug_bone_animation_disable_all',0,'void',False,False,True),
 (0x488170,'thug_bone_animation_set_rotation',1,'void',False,False,True),
 (0x488220,'thug_bone_animation_set_velocity',1,'void',False,False,True),
 (0x488950,'thug_bone_animation_setup',3,'void',False,False,True),
 (0x488b20,'thug_bone_animation_configure',1,'void',True,True,True),
 (0x488b40,'thug_bone_animation_command',3,'word',True,True,True)]
assert len(NEW)==37
for row in NEW:
 bind(*row)
 if row[0] not in observe:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=row[0],end=row[0]);observe.append(row[0])
functions['0x4877e0']['float_args']=[2,3]
for at in [0x4818b0,0x481a30,0x481a80]:
 f=json.loads((out/'animation-events-fixtures.json').read_text())['functions'][hex(at)];functions[hex(at)]=f
 if at not in observe:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at);observe.append(at)
for at in [0x4814b0,0x4816b0,0x48d000,0x4645e0,0x477b80,0x477c60,0x477d40,0x476af0,0x476b40]:
 if at not in observe:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at);observe.append(at)
TIMED,WEIGHTED,FLAGS,POSE,BONE,TIME,VEC,OUTPUT,CSCRIPT,CARGS=[BASE+x for x in [0x1d0000,0x1d0100,0x1d0200,0x1d1000,0x1d2000,0x1d3000,0x1d4000,0x1d4100,0x1d4200,0x1d4400]]
memory[TIMED-BASE:CARGS+0x100-BASE]=bytes(CARGS+0x100-TIMED)
put(TIMED,'<5I',0x649fb0,CHANNEL,0,0,0);put(TIMED+0x14,'<4I',TIME,READER,BASE+0x1c1000,0)
put(WEIGHTED,'<5I',0x649f68,CHANNEL,BODIES,0,0);put(WEIGHTED+0x14,'<4I',BASE+0x1c1000,READER,0,0)
put(FLAGS,'<2I',0x64b1d4,CHANNEL);put(POSE,'<2I',0x649f98,CHANNEL);put(BONE,'<3I',0x6488d8,CHANNEL,BODIES)
for i in range(4):
 r=BONE+0x14+i*0x64;put(r,'<IIfI',0xabc000+i,0xdef000+i,1,0)
 for off in [0x10,0x20,0x30,0x40,0x50]:put(r+off,'<4f',i+1,i+2,i+3,1)
 put(r+0x60,'<4B',1,1,1,0xac)
put(TIME,'<5I',0x648768,TIME,0,TIME,TIME);put(TIME+0x14,'<4f',0,0,2,1/60);put(TIME+0x24,'<4I',0,0,0,0x123)
put(VEC,'<5I',0xcccccccc,bits(30),bits(60),bits(90),0xadadadad)
put(CSCRIPT+0x14,'<I',CARGS);put(CARGS,'<2I',0,0)
put(ASTATE+0x50,'<I',0);put(BASE+0x1c1000,'<f',2)
put(CHANNEL,'<I',0x648794);put(CHANNEL+0x54,'<I',0)
fields.update([TIMED,WEIGHTED,FLAGS,POSE,BONE,TIME,CHANNEL])
exports += [[0x6486cc,'thug_animation_link_methods'],[0x649fb0,'thug_timed_animation_methods'],[0x649f68,'thug_weighted_animation_methods'],[0x64b1d4,'thug_flag_animation_methods'],[0x649f98,'thug_pose_animation_methods'],[0x6488d8,'thug_bone_animation_methods'],[0x648794,'thug_animation_channel_methods']]
for at in [0x4a5350,0x4a4d50,0x4a5010,0x4a4820,0x4e2c50,0x4e2c80,0x4a5730,0x4a4d20,0x488300,0x487d40]:oracle.cpu.hook_add(UC_HOOK_CODE,identity,begin=at,end=at)
if 0x684fc8 not in index:addglobal('thug_frame_length_scale',0x684fc8,0x3f800000)
else:defaults[index[0x684fc8]]=0x3f800000
initial=bytes(memory);oracle.initial=initial
base_case=old_case
def case(calls,patches=(),changes=None,label='animation controllers',float_fields=(),quiet_fields=()):
 stages=base_case(calls,patches,changes,label)
 for s in stages:
  if float_fields:s['float_fields']=sorted(set(float_fields))
  if quiet_fields:s['quiet_float_fields']=sorted(set(quiet_fields))
 return stages
rng=random.Random(0x488b40)
special=[0,0x80000000,1,0x80000001,bits(1),bits(-1),0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc12345,0x7f812345]
# Source getter reads all lanes before output, including overlap; X is raw.
for i in range(72):
 b=Build();vals=[rng.choice(special) for _ in range(3)];p=b.structure([(0x123,6,VEC)])
 target=rng.choice([OUTPUT,VEC,VEC+4,VEC+8]);fields_=[target+4,target+8]
 case([call(0x476fb0,p,[0x123,target,i&1])],b.patches()+[patch(VEC+4,'<3I',*vals)],label='vector getter overlap and exact X versus quiet Y/Z',quiet_fields=fields_)
for kind in [None,1,2,3,5,10]:
 b=Build();p=b.structure([] if kind is None else [(0x123,kind,VEC)])
 case([call(0x476fb0,p,[0x123,OUTPUT,0])],b.patches(),label='missing or wrong vector type preserves output')
for i in range(80):
 p=[patch(OUTPUT,'<4I',*[rng.choice(special) if i<40 else rng.getrandbits(32) for _ in range(4)])]
 case([call(0x405ef0,OUTPUT)],p,label='degrees conversion preserves fourth lane',float_fields=[OUTPUT+j*4 for j in range(3)])
for value in special+[bits(2.5),bits(-2.5)]:
 case([call(0x47d620,ASTATE,[0x123]),call(0x419af0,ACOMP,[0x123])],[patch(BASE+0x1c1000,'<I',value)],label='actual asset duration lookup')
case([call(0x419af0,ACOMP,[0xdeadbeef])],[patch(ASTATE+4,'<I',0xffffffff)],label='duration sentinel does not query missing asset')
for mask in range(8):
 b=Build();p=b.structure([(0,13,key) for i,key in enumerate([0x4f792e6c,0x3153e314,0x6d941203]) if mask&(1<<i)])
 case([call(0x487770,args=[OUTPUT,p])],b.patches(),label='loop flag precedence')
# Named endpoints, numeric values, seconds/frames and swapped outputs.
for i in range(240):
 b=Build();entries=[]
 for key in [0x46e55e8f,0x28782d3b]:
  mode=rng.randrange(4)
  if mode==1:entries.append((key,13,rng.choice([0x6086aa70,0x230ccbf4,0x617fe530,0xff03cc4e,0x123])))
  elif mode==2:entries.append((key,2,rng.choice(special) if i<80 else bits(rng.uniform(-100,100))))
  elif mode==3:entries.append((key,1,rng.getrandbits(32)))
 if i&1:entries.append((0,13,0xd029f619))
 if i&2:entries.append((0,13,0xf8cfd515))
 p=b.structure(entries);last=OUTPUT if i%5==0 else OUTPUT+4
 case([call(0x4877e0,args=[OUTPUT,last,rng.choice(special),rng.choice(special),p,rng.getrandbits(32)])],b.patches(),label='range endpoints and aliasing',quiet_fields=[OUTPUT,last])
for i in range(60):
 loop=rng.choice([0,1,2,3,256]);direction=rng.choice([0,1,0xffffffff]);a=rng.choice(special);z=rng.choice(special);t=rng.choice([a,z,rng.choice(special)])
 case([call(0x4813f0,TIME)],[patch(TIME+0x14,'<3I',a,t,z),patch(TIME+0x24,'<2I',direction,loop)],label='endpoint completion ordered equality and low byte return')
for i in range(32):
 p=[patch(TIME+0x14,'<4f',0,rng.uniform(-5,5),2,rng.uniform(-3,3)),patch(TIME+0x24,'<2I',0 if i&1 else 0xffffffff,i%4)]
 case([call(0x481640,TIME)],p,label='concrete base timeline update stores current')
# Concrete constructors preserve all other bytes and support explicit-owner paths.
for i in range(16):
 p=[raw(at,bytes(rng.getrandbits(8) for _ in range(size))) for at,size in [(TIMED,0x24),(WEIGHTED,0x24),(FLAGS,0x18),(POSE,0x854),(BONE,0x1a4)]]
 calls=[call(0x4a5350,TIMED,[CHANNEL]),call(0x4a5010,WEIGHTED,[CHANNEL if i&1 else 0,BODIES]),call(0x4e2c50,FLAGS,[CHANNEL]),call(0x4a5730,POSE,[CHANNEL]),call(0x488300,BONE,[CHANNEL if i&1 else 0,BODIES])]
 case(calls,p,{0x6fa7f4:i&1,0x6fa7fc+4*(i&1):APOOL if i%3 else 0},label='all five constructors preserve padding and owned allocation order')
for flag in [0,1,2,3,256,257]:
 for root,at in [(0x4a5400,TIMED),(0x4a50b0,WEIGHTED),(0x4e2cf0,FLAGS),(0x4a5320,POSE),(0x4880d0,BONE)]:case([call(root,at,[flag])],label='concrete scalar deleting destructor')
for root,at in [(0x4a4d50,TIMED),(0x4a4820,WEIGHTED),(0x4e2c80,FLAGS),(0x4a4d20,POSE),(0x487d40,BONE)]:case([call(root,at)],label='concrete standalone destructor')
for reader,timeline in [(0,0),(READER,0),(0,TIME)]:
 case([call(0x4a4d50,TIMED)],[patch(TIMED+0x14,'<2I',timeline,reader)],label='timed cleanup null owned fields')
for i in range(24):
 b=Build();entries=[]
 for j,key in enumerate([0x0c7a712c,0x6ea3704a]):
  if i&(1<<j):entries.append((key,1,rng.choice([0,1,256,0x80000000,0xffffffff])))
 if i&4:entries.append((0x40c698af,13,0x777))
 p=b.structure(entries)
 case([call(0x4e2c90,FLAGS,[p]),call(0x51adc0,FLAGS,[rng.getrandbits(32),0xffffffff,0xffffffff])],b.patches()+[patch(FLAGS+0x14,'<I',0xaabbccdd)],label='optional integer flags coerce bool and unhandled command')
# Full timed configuration and commands with real asset lookup.
for i in range(120):
 b=Build();entries=[(0x6c2bfb7f,13,0x123),(0x40c698af,13,i)]
 if i%2:entries += [(0x46e55e8f,2,bits(rng.uniform(0,20))),(0x28782d3b,2,bits(rng.uniform(40,100)))]
 if i%3:entries.append((0xf0d90109,2,bits(rng.uniform(-3,3))))
 if i%4:entries.append((0x230ccbf4,2,bits(rng.uniform(-1,1))))
 entries.append((0,13,[0x4f792e6c,0x3153e314,0x6d941203,0x123][i%4]))
 p=b.structure(entries)
 case([call(0x4a4dd0,TIMED,[p]),call(0x4a54a0,TIMED,[0xd63a1b81,p,CSCRIPT]),call(0x4a54a0,TIMED,[0x5f495ae0,p,CSCRIPT])],b.patches(),label='complete timed configure output query and refresh')
for command,key in [(0xbd4edd44,0xf0d90109),(0x6aaeb76f,0x06c9f278)]:
 for i in range(60):
  b=Build();val=rng.choice(special) if command==0xbd4edd44 else bits(rng.uniform(-5,5));p=b.structure([(key,2,val)])
  case([call(0x4a54a0,TIMED,[command,p,CSCRIPT])],b.patches(),label='timed speed or offset command',float_fields=[TIME+0x18,TIME+0x20])
for direction in [0,1,2,0xffffffff]:case([call(0x4a54a0,TIMED,[0xf5e2b871,0,0])]*2,[patch(TIME+0x24,'<I',direction)],label='timed direction toggles zero and minus one')
for command in [0,0x5f495adf,0x5f495ae1,0xffffffff]:case([call(0x4a54a0,TIMED,[command,0,0]),call(0x4a4890,WEIGHTED,[command,0,0])],label='unknown commands do not read parameters')
# Weighted setup, refresh, weight update, and reader replacement.
for i in range(80):
 b=Build();command=[0xaf2fae19,0x5e3f0f17,0x5f495ae0,0xc68365eb][i%4]
 entries=[(0x98549ba4,13,0x123)] if command==0xc68365eb else [(0xd697a799 if i&4 else 0x6c2bfb7f,13,0x123)]
 if i%3 or command==0x5e3f0f17:entries.append((0xc6ae16ac,2,rng.choice(special)))
 p=b.structure(entries)
 case([call(0x4a4890,WEIGHTED,[command,p,CSCRIPT])],b.patches(),label='complete weighted command including reader replacement')
# Complete allocated lifecycle: constructors, configuration, virtual timeline
# update, output setters and owned cleanup through actual channel removal.
for pool_index in [0,1]:
 for pooled in [False,True]:
  b=Build();p=b.structure([(0x6c2bfb7f,13,0x123),(0x06c9f278,2,bits(.5)),(0x40c698af,13,0x321)])
  calls=[call(0x4a5350,TIMED,[CHANNEL]),call(0x4a4dd0,TIMED,[p]),call(0x4a54a0,TIMED,[0x6aaeb76f,p,CSCRIPT]),call(0x4a54a0,TIMED,[0xd63a1b81,p,CSCRIPT]),call(0x481a30,CHANNEL,[TIMED,10]),call(0x4818b0,CHANNEL,[TIMED])]
  case(calls,b.patches(),{0x6fa7f4:pool_index,0x6fa7fc+pool_index*4:APOOL if pooled else 0},label='complete allocated timed controller lifecycle with concrete virtual cleanup')
for mode in ['absent','zero','first','fallback','precedence']:
 for command in [0x5e3f0f17,0xaf2fae19]:
  if mode=='absent' and command==0xaf2fae19:continue
  b=Build();entries=[(0xc6ae16ac,2,bits(.5))]
  if mode in ['zero','first','precedence']:entries.append((0xd697a799,13,0 if mode=='zero' else 0x123))
  if mode in ['fallback','precedence']:entries.append((0x6c2bfb7f,13,0x124))
  p=b.structure(entries)
  case([call(0x4a4890,WEIGHTED,[command,p,CSCRIPT])],b.patches()+[patch(AB+48,'<3I',0x124,ASSET2,0)],label='weighted name selection '+mode)
# Bone helper flags, missing sentinels, raw overlap copies and selection.
for mask in range(16):
 p=[patch(BONE+0x14+i*0x64,'<I',0xabc000+i if mask&(1<<i) else 0xffffffff) for i in range(4)]
 p += [patch(BONE+0x74+i*0x64,'<B',rng.choice([0,1,255])) for i in range(4)]
 calls=[call(0x487d60,BONE,[0xabc002]),call(0x487d60,BONE,[0xffffffff]),call(0x487d60,BONE,[0x777]),call(0x487d90,BONE),call(0x487dc0,BONE),call(0x487d90,BONE),call(0x487de0,BONE),call(0x487d90,BONE)]
 case(calls,p,label='four bone records and inactive name sentinel')
 for source in [VEC,BONE+0x20,BONE+0x28,BONE+0x38]:case([call(0x488170,BONE,[source]),call(0x488220,BONE,[source])],p,label='raw word vector propagation with overlap')
for i in range(160):
 b=Build();entries=[]
 for bit,key,kind in [(0,0xcab94088,13),(1,0x4acee3f7,13),(2,0xdc741bad,6),(3,0x1f07cf31,6),(4,0x7af07905,1),(5,0xf832aabe,2),(6,0x0b405328,6),(7,0x0a4cc99c,6)]:
  if rng.randrange(2):entries.append((key,kind,VEC if kind==6 else rng.choice(special)))
 for key in [0x0c5f37cd,0xb0bab2ae,0xd4a8cd5f]:
  if rng.randrange(2):entries.append((0,13,key))
 p=b.structure(entries);record=i%4;all_=rng.choice([0,1,256,257]);extra=[patch(VEC+4,'<3I',*[rng.choice(special) if i<50 else bits(rng.uniform(-500,500)) for _ in range(3)])]
 # Vector getters quiet Y/Z only; conversion outputs classify arithmetic NaNs.
 quiet=[];arithmetic=[]
 if any(k==0xdc741bad for k,_,_ in entries):quiet += [BONE+record*0x64+0x48,BONE+record*0x64+0x4c]
 if any(k==0x1f07cf31 for k,_,_ in entries):quiet += [BONE+record*0x64+0x58,BONE+record*0x64+0x5c]
 for key,off in [(0x0b405328,0x24),(0x0a4cc99c,0x34)]:
  if any(k==key for k,_,_ in entries):arithmetic += [BONE+j*0x64+off+k*4 for j in (range(4) if all_&255 else [record]) for k in range(3)]
 case([call(0x488950,BONE,[all_,record,p])],b.patches()+extra,label='complete bone setup all/index and parameter precedence',float_fields=arithmetic,quiet_fields=quiet)
for i in range(60):
 b=Build();entries=[(0xcab94088,13,0xabc000+i),(0x40c698af,13,0x123),(0x0b405328,6,VEC)]
 p=b.structure(entries)
 case([call(0x488b20,BONE,[p])],b.patches(),label='bone configure changes record zero and base name')
for mode in ['index','name','all','default','precedence']:
 for i in range(4):
  b=Build();entries=[]
  if mode in ['index','precedence']:entries.append((0x7f8c98fe,1,i))
  if mode in ['name','precedence']:entries.append((0x40c698af,13,0xabc000+i))
  if mode in ['all','precedence']:entries.append((0,13,0xc4e78e22))
  entries += [(0x0c5f37cd,1,0),(0x0b405328,6,VEC)]
  p=b.structure(entries)
  case([call(0x488b40,BONE,[command,p,CSCRIPT]) for command in [0x4599fb80,0x027b2b1c,0x20d24e9a,0x027b2b1c,0xb040e943,0]],b.patches(),label='complete bone command selection '+mode)
# Actual channel removal invokes each concrete controller's deleting virtual.
for at in [TIMED,WEIGHTED,FLAGS,POSE,BONE]:
 case([call(0x481a30,CHANNEL,[at,100]),call(0x481a80,CHANNEL,[0]),call(0x4818b0,CHANNEL,[at])],label='channel insertion lookup removal through concrete destructor')

scope='Thirty-seven complete routines cover five animation controller construction/destruction/configuration/command paths, timeline update/completion, duration lookup, range/loop parsing, vector getter and degree conversion. Actual concrete virtual methods, reader pools, asset lookup, owned base timeline and QB output setters execute unchanged. Full memory/globals/heap/returns compare; only documented x87 quiet bits and arithmetic NaNs differ. Valid record indices/names, required command fields, terminating time ranges and successful allocation are internal contracts. Controller update/render virtuals and the standard cache controller remain unavailable. Full factory/channel dispatch, animation parsing, movement/startup and playable browser integration remain unfinished.'
fixture={'base':BASE,'memory':'animation-controllers-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'instrumented_diagnostic_callbacks','pointer_exports':exports,'pointer_fields':sorted(fields),'native_callbacks':[{'module':'animation-asset-callbacks.wasm','export':'fixture_animation_diagnostics','slots':[PRINT+4]}]}
path=out/'animation-controllers-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
print('x86 complete:',len(labels),dict(oracle.counts),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_animation_controllers_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory']]},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
