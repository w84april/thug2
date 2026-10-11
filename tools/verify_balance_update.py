"""Complete balance frame, real animation forwarding, events, meter and network queues."""
from pathlib import Path
prefix=Path(__file__).with_name('verify_animation_controllers.py').read_text().split('rng=random.Random(0x488b40)')[0]
exec(compile(prefix.replace("'animation-controllers.json'","'balance-update.json'"),str(Path(__file__).with_name('verify_animation_controllers.py')),'exec'))
from unicorn.x86_const import UC_X86_REG_EIP,UC_X86_REG_FPSW,UC_X86_REG_FPTAG
NEW=[(0x47e280,'thug_animation_set_balance',2,'void',True,True,True),(0x419bd0,'thug_animation_component_set_balance',2,'void',True,True,True),(0x579cc0,'thug_balance_update',0,'void',True,True,True)]
for row in NEW:
 bind(*row);oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=row[0],end=row[0])
for a in [0x47e280,0x419bd0]:functions[hex(a)]['float_args']=[0]
for a,name in [(0x481ac0,'thug_animation_channel_update'),(0x4a52e0,'thug_balance_animation_update')]:bind(a,name,0,'void',True,True,True)
for a in [0x481ac0,0x482200,0x4a4af0,0x4a52e0,0x4a5180,0x532ea0,0x4549f0,0x459e50,0x458360,0x564270,0x563370,0x563390,0x51d6a0,0x51ce80,0x4609f0,0x4f90a0,0x403de0,0x449970,0x4738e0]:
 if a not in observe:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=a,end=a);observe.append(a)
# Reuse the real sprite graph and its cached QB visibility programs, not callbacks
# replacing the display routines. Our terminal native observer is shared below.
asset_control=CONTROL
source=Path(__file__).with_name('verify_balance_display.py').read_text()
exec(compile(source[source.index('METER,CHILD,STYLE,'):source.index('initial=bytes(memory);oracle.initial=initial')].replace('oracle.stop+0x400','oracle.stop+0x500'),'<existing balance sprite graph>','exec'))
CONTROL=asset_control
exports += [[0x649a80,'thug_sprite_style_base_methods'],[0x64a744,'thug_sprite_style_methods'],[0x64ad28,'thug_sprite_drawable_methods'],[0x64a228,'thug_ui_sprite_methods']]
exports += [[base+4*i,'thug_'+kind+'_'+suffix+'_methods'] for base,suffix in [(0x6474cc,'queue'),(0x647578,'node')] for i,kind in enumerate(['plain','reliable','sequenced']) if base+4*i not in dict(exports)]
# The asset oracle replaces the earlier CPU instance. Restore read-only identity
# tracking for concrete UI and network objects allocated by these full frames.
for at in [0x460b80,0x4615d0,0x463870,0x460b20,0x460b40,0x4dfa70,0x48d220,0x4555f0,0x455620,0x455650]:
 oracle.cpu.hook_add(UC_HOOK_CODE,identities,begin=at,end=at)
BAL,PARAMS,BINPUT,BTRICKS,OBS,PROGRAMS,MOD_OWNER,MODIFIER=[BASE+x for x in [0x1f0000,0x1f0100,0x1f0200,0x1f0800,0x1f2000,0x1f4000,0x1f5000,0x1f5040]]
memory[BAL-BASE:BASE+0x1f6000-BASE]=bytes(0x6000)
put(BAL,'<5I',0,BODIES,PARAMS,SCORE_COMPONENTS,BINPUT)
put(BAL+0x24,'<6f',0,0,0,100,2,1)
put(BAL+0x3c,'<B',1);put(BAL+0x40,'<5I',0,0xbc6b118f,0x11112222,3,0);put(BAL+0x54,'<4B',1,0,1,0)
put(BINPUT+0x38,'<I',0xbc6b118f);put(BINPUT+0x58,'<I',0x11112222)
put(BODIES+0x100,'<I',ACOMP);put(ACOMP+0x10,'<I',BTRICKS)
put(BTRICKS+4,'<I',0x4ff8dac6);put(BTRICKS+12,'<2I',BODIES,PHYS)
put(PHYS+4,'<I',0x5bd63b29);put(PHYS+16,'<I',PARAMS)
put(PARAMS+4,'<I',0x12345678);put(PARAMS+12,'<3I',BODIES,SCORE_COMPONENTS,0);put(PARAMS+0x18,'<I',0x8d10119d)
put(SCORE_COMPONENTS+16,'<I',0)
put(BODIES+0x278,'<I',MOD_OWNER);put(MOD_OWNER+0x18,'<I',MODIFIER);put(BODIES+0x280,'<I',PHYS)
put(ASTATE+0x20,'<I',CHANNEL);put(ASTATE+0x68,'<I',BODIES)
put(CHANNEL+0x3c,'<I',CONTROLLER);put(CHANNEL+0x54,'<I',1)
put(CHANNEL+0x38,'<I',2);put(CHANNEL+0x68,'<2I',0,0)
put(CONTROLLER+0x14,'<5f',.1,.05,.001,.002,1);put(CONTROLLER+0x28,'<f',0)
put(BODIES+0x2bc,'<I',0);put(PLAYERS+0x1d0,'<I',1)
put(BODIES,'<I',0x64a264);put(BODIES+8,'<I',0x14400);put(BODIES+0x10,'<I',SCRIPTS)
fields.add(BODIES)
# Real registered UI event method on a test owner with skater fields. Skater
# construction itself is not claimed by this fixture.
put(PRIMARY+8,'<I',1);put(PRIMARY+32,'<3I',0x100,BODIES,0)
script=bytearray(244)
for off,v in [(0x2c,SCRIPTS+0x1c),(0x94,SCRIPTS+0x34),(0xe0,EVENTS),(0xec,0x6478e4)]:struct.pack_into('<I',script,off,v)
memory[SCRIPTS-BASE:SCRIPTS-BASE+244]=script;fields.add(SCRIPTS+0xec)
put(EVENTS,'<IIBBHI',ENTRIES,2,1,0,0,0)
for i,name in enumerate([0xd77b6ff9,0x47d44b84]):put(ENTRIES+i*20,'<5I',name,name,0,0,1)
for i in range(70):put(BTRICKS+0x1c+i*36+0x10,'<I',1)
put(BTRICKS+0x9f4,'<B',1);put(BTRICKS+0xa90,'<I',1)
# Additional notifications include score text, timed tricks and actual events.
for i,name in enumerate([0xd77b6ff9,0x47d44b84,0x55e516c8,0x41b03551,0xd4491be1,0xa611bb15]):
 at=PROGRAMS+i*128;program=at+64;bucket=SYMBOLS+(name&0xfff)*4
 old=struct.unpack_from('<I',memory,bucket-BASE)[0];put(at,'<BBHIIII',0,7,0,name,0,program,old);put(bucket,'<I',at)
 put(at+32,'<5I',name,program,1,0,0)
 memory[program-BASE:program-BASE+8]=b'\x01\x43'+struct.pack('<I',NATIVE)+b'\x01\x24';fields.add(program+2)
 slot=CACHETABLE+32+(name&3)*12;old=bytes(memory[slot-BASE:slot-BASE+12]);occupied=struct.unpack_from('<I',old,4)[0]
 if occupied:memory[at+80-BASE:at+92-BASE]=old
 put(slot,'<3I',name,at+32,at+80 if occupied else 0)
put(CACHETABLE+8,'<I',10)
addglobal('thug_animation_last_balance',0x67dc10,255,1)
# Existing CRT formatting uses explicit OS TLS/last-error boundaries.
os_source=Path(__file__).with_name('verify_objective_notifications.py').read_text()
exec(compile(os_source[os_source.index('# Real CRT signed'):os_source.index('# Format/output')],'<existing CRT OS services>','exec'))
# Script allocation introduces a reference-target method at +ec.
def script_identity(cpu,at,size,user):fields.add(cpu.reg_read(UC_X86_REG_ECX)+0xec)
oracle.cpu.hook_add(UC_HOOK_CODE,script_identity,begin=0x4738e0,end=0x4738e0)
def native(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);params=oracle.word(sp+4);script=oracle.word(sp+8);n=oracle.word(OBS);assert n<64
 oracle.setword(OBS,n+1);name=oracle.word(script+0xc8);first=oracle.word(params+4) if params else 0
 row=[name,oracle.word(script+0xbc),oracle.word(BAL+0x24),oracle.word(BAL+0x30),oracle.word(BAL+0x34),oracle.word(PARAMS+0x18),oracle.word(CONTROLLER+0x28),oracle.word(SCORE+0x5c),first,oracle.word(first+4) if first else 0,oracle.word(first+8) if first else 0,bytes(cpu.mem_read(BTRICKS+0x28,1))[0]]
 cpu.mem_write(OBS+64+n*48,struct.pack('<12I',*row))
 if not oracle.word(OBS+16) or oracle.word(OBS+16)==name:
  target=oracle.word(OBS+4);width=oracle.word(OBS+12)
  if target:assert width in [1,4];cpu.mem_write(target,oracle.word(OBS+8).to_bytes(4,'little')[:width])
 cpu.reg_write(UC_X86_REG_EAX,1);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
oracle.cpu.hook_add(UC_HOOK_CODE,native,begin=NATIVE,end=NATIVE)
initial=bytes(memory);oracle.initial=initial;labels=[]
new_branches={0x47e303:'network_lower_clamp',0x47e31e:'network_upper_clamp',0x47e34b:'network_change',0x47e3ff:'animation_parameters',0x579d2a:'decay',0x579d69:'decay_zero',0x579e8f:'input_timeout',0x579ebe:'left_integer_ramp',0x579f2c:'right_integer_ramp',0x579ee2:'left_input',0x579f50:'right_input',0x579f89:'random_reset',0x579fc2:'random_increment',0x57a018:'script_creation',0x57a070:'balance_failed',0x57a0a9:'state_reversal',0x57a0e5:'animation_forward',0x57a13a:'normal_meter',0x57a161:'manual_meter'}
branch_at.update(new_branches)
for at in new_branches:oracle.cpu.hook_add(UC_HOOK_CODE,branch,begin=at,end=at)
def case(calls,p=(),changes=None,label='balance update',floats=()):
 oracle.cpu.reg_write(UC_X86_REG_FPSW,0);oracle.cpu.reg_write(UC_X86_REG_FPTAG,0xffff)
 try:stages=oracle.case(calls,p,{index[k]:v for k,v in (changes or {}).items()})
 except Exception:print('FAIL',len(labels),label,flush=True);raise
 labels.append(label);previous=0
 for s in stages:
  for at,data in s['outputs']:
   if at<=OBS<at+len(data)//2:
    current=int.from_bytes(bytes.fromhex(data)[OBS-at:OBS-at+4],'little');s['callbacks']=current-previous;previous=current
  s['float_fields']=list(floats)
 if len(labels)%100==0:print('Original balance update cases:',len(labels),flush=True)
 return stages
# Heap scope/queue graph helper from the existing complete network test.
source=Path(__file__).with_name('verify_objective_notifications.py').read_text()
exec(compile(source[source.index('def queue_node('):source.index('def owned(')],'<existing network graph>','exec'))
rng=random.Random(0x579cc0)
special=[0,0x80000000,1,0x80000001,bits(-1),bits(1),0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc12345,0x7f812345]
# Standalone forwarding covers its independent gates, pools and queue replacement.
for i,value in enumerate(special+[bits(rng.uniform(-2,3)) for _ in range(60)]):
 for send in [0,1,256,257]:
  p=online()+[patch(ASTATE+0x28,'<I',int(i%7==0)),patch(PLAYERS+0x1d0,'<I',0 if i%11==0 else 1)]
  if i%13==0:p.append(patch(CLIENT+0x1e8c+12,'<I',CLIENT+0x1e8c))
  case([call(0x47e280,ASTATE,[value,send]),call(0x419bd0,ACOMP,[value,send])],p,{0x6f361c:POOL if i%2 else 0,0x67dc10:i%256},label='animation forwarding clamps quantizes replaces queue and invokes actual balance controller',floats=[CONTROLLER+0x28])
for state_id in [0,0xffffffff]:
 for channel_id in [0,0xffffffff]:
  case([call(0x419bd0,ACOMP,[bits(.5),0])],[patch(ASTATE+4,'<I',state_id),patch(CHANNEL+4,'<I',channel_id)],label='allocated state and channel sentinels')

params_defaults={0x1231ae3c:.2,0xa4362662:2,0x06851748:.01,0xa9fef5ab:.1,0xb6a634f3:1,0xef27e8ff:1,0x32eb3308:13,0x61ad5596:.25,0xf81ab0e9:8192}
def config(overrides=None,mode=0x8d10119d,career=0):
 b=Build();values={**params_defaults,**(overrides or {})};entries=[]
 for name,value in values.items():
  pair=b.alloc(struct.pack('<I2f',5,value,value));entries.append((name,10,b.structure([(0,5,pair)])))
 p=b.structure(entries);b.extra += [patch(PARAMS+0x18,'<I',mode),patch(PARAMS+0x20,'<I',p)]
 b.header(SETTINGS+4,b.structure([(0xa1dc81f9,13,0x12345),(0x1ded1ea4,1,career),(0x5a2c589a,1,0)]))
 b.extra += [patch(MANAGER+0x398,'<I',b.structure([(0x12345,1,1)]))]
 b.header(PROFILE+0x5c,b.structure([(0xa1dc81f9,13,0x0a7be964)]))
 b.symbol(0x8cc8f176,1,2000);b.symbol(0x07da1621,1,1000)
 return b
float_fields=[BAL+off for off in [0x24,0x28,0x30,0x34,0x38]]+[CONTROLLER+0x28,CHANNEL+0x18]+[OBS+64+n*48+off for n in range(64) for off in [8,12,16,24]]
for i in range(220):
 b=config(mode=[0x8d10119d,0x0ac90769,0x3506ce64,0xa549b57b][i%4]);position=rng.uniform(-2000,2000);velocity=rng.uniform(-3,3)
 p=b.patches()+online()+[patch(BAL+0x24,'<6f',rng.uniform(0,10),rng.uniform(0,10),0,position,velocity,rng.choice([0,.001,.5,10])),patch(BAL+0x3c,'<B',i%2),patch(BAL+0x40,'<I',rng.choice([0,1000,0xffffffff])),patch(BINPUT+0x20,'<B',i%3==0),patch(BINPUT+0x40,'<B',i%5==0),patch(BAL+0x54,'<4B',i%3!=0,0,i%2,i%4),patch(SKATER_STATE+0x28,'<B',i%2)]
 if i%2:p += [patch(BAL+0x48,'<I',0xe3006fc4),patch(BINPUT+0x58,'<I',0xe3006fc4)]
 if i%7==0:p.append(patch(BODIES+0x10,'<I',0))
 case([call(0x461a00,UM,[METER]),call(0x579cc0,BAL),call(0x481ac0,CHANNEL)],p,{0x7d1ec8:rng.choice([0,30,60,100,1000,0xffffff00]),0x696d60:rng.choice([0,1000,0xffffffff])},label='full balance frame input timers animation queue and actual meter graph',floats=float_fields)
# Nonfinite arithmetic runs with the meter disabled, because its original curve
# lookup requires a valid finite index. This does not bypass the balance math.
for i in range(96):
 b=config();p=b.patches()+online()+[patch(BAL+0x24,'<6I',*[rng.choice(special) for _ in range(6)]),patch(BAL+0x54,'<4B',1,1,0,0)]
 case([call(0x579cc0,BAL)],p,label='balance nonfinite arithmetic without invalid meter indices',floats=float_fields)
# Trigger real failure delivery and timed-trick notifications, including mutation
# of fields that the parent must read after returning from the native observer.
for event in [0xd77b6ff9,0x47d44b84,0x55e516c8,0x41b03551,0xba95da16]:
 for target,value,width in [(0,0,0),(BAL+0x54,0,1),(PARAMS+0x18,0,4),(BAL+0x34,bits(-2),4),(BAL+0x57,1,1),(BAL+0x30,bits(512),4)]:
  b=config({0xf81ab0e9:1 if event in [0xd77b6ff9,0x47d44b84] else 8192},career=1)
  for j in range(3):
   b.extra.append(patch(BTRICKS+0x1c+j*36,'<2IiB3x3I2I',0xc1336019,0,0,0,0,b.text(b'Balance'),0,0,0))
  p=b.patches()+online()+[patch(BAL+0x30,'<f',-100 if event==0x47d44b84 else 100),patch(OBS+4,'<4I',target,value,width,event)]
  case([call(0x461a00,UM,[METER]),call(0x579cc0,BAL)],p,label='original QB events and notifications mutate the live balance frame',floats=float_fields)
for left,right in [(0,0),(1,0),(0,1)]:case([call(0x579cc0,BAL)],[patch(BAL+0x44,'<2I',left,right)],label='missing button guard precedes all component access')
# Positive balance points exercise real scoring and UI text updates too.
for points in [0,1,100,0xffffffff]:
 b=config();p=b.patches()+online()+[patch(BAL+0x4c,'<I',points),patch(SCORE+0x54,'<4I',1,0,1,bits(1)),patch(TRICKS,'<7I',100,0,0,0,0,0,2),raw(TRICKS+0x1c,b'Balance\0'),raw(TRICKS+0x5c,b'Balance\0')]
 case(setup()+numeric_setup()+[call(0x461a00,UM,[METER]),call(0x579cc0,BAL)],p,label='complete balance frame adds score and updates original combo numeric text',floats=float_fields)


# Exercise guards and the decay-to-zero branch independently of random states.
for missing,blocked,selected in [(True,0,0),(False,1,1),(False,0,1)]:
 p=online()+[patch(BODIES+0x14,'<I',0x999 if missing else 0x100),patch(ASTATE+0x28,'<I',blocked)]
 case([call(0x47e280,ASTATE,[bits(.75),255])],p,{0x6f3614:selected,0x6f361c+selected*4:POOL},label='missing network player blocked network and selected parameter pool')
b=config({0x1231ae3c:10,0xa4362662:1})
case([call(0x461a00,UM,[METER]),call(0x579cc0,BAL)],b.patches()+online()+[patch(BAL+0x38,'<f',.05)],label='decay crosses zero before subsequent balance work',floats=float_fields)
assert all(branches[name]>0 for name in new_branches.values()),dict(branches)

callback=out/'balance-update-callbacks.wasm'
subprocess.run([str(ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang'),'--target=wasm32-unknown-unknown','-O2','-nostdlib','-Wl,--no-entry,--export-all,--import-memory',str(ROOT/'tools/balance_update_callbacks.c'),'-o',str(callback)],check=True)
scope='Three complete routines connect the balance frame to actual animation channel/controller commands and original network queues. Full balance math, named input, timers, random drift, scoring, timed tricks, failure-event QB delivery, script allocation, reversal and concrete sprite meter updates execute original callees. Terminal native QB handlers and OS/heap services are explicit test boundaries. Whole memory, globals, heap events and returns compare; only typed arithmetic NaNs use classification. Owner is a registered UI object with skater fields, not recovered skater construction. Required components/buttons, successful allocations and valid finite meter curve indices are internal contracts; nonfinite balance cases disable the meter only. Full grounded movement, startup/rendering and playable training remain unfinished.'
fixture={'base':BASE,'memory':'balance-update-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'native_balance_notifications','pointer_exports':exports,'pointer_fields':sorted(fields),'native_callbacks':[{'module':'animation-asset-callbacks.wasm','export':'fixture_animation_diagnostics','slots':[PRINT+4]},{'module':callback.name,'export':'fixture_balance_native','original':NATIVE}]}
path=out/'balance-update-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
print('Original complete',len(labels),sum(oracle.counts.values()),dict(branches),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_balance_update_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'branches':dict(branches),'heap_events':dict(oracle.heap_events),'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory'],callback]},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(labels),sum(oracle.counts.values()))
