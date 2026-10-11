"""Complete balance display and concrete sprite data paths against original x86."""
from pathlib import Path
prefix=Path(__file__).with_name('verify_score_display.py').read_text().split('rng=random.Random(0x561890)')[0]
prefix=prefix.replace("'score-display.json'","'balance-display.json'")
prefix=prefix.replace('oracle=ScriptHeapOracle(', 'observe=list(dict.fromkeys(observe))\noracle=ScriptHeapOracle(')
exec(compile(prefix,str(Path(__file__).with_name('verify_score_display.py')),'exec'))
from unicorn.x86_const import UC_X86_REG_EIP
NEW=[(0x49ed60,'thug_sprite_style_initialize',1,'word',False,False,True),
 (0x4dfc50,'thug_sprite_drawable_initialize',1,'word',False,False,True),
 (0x4c70e0,'thug_sprite_draw_style_initialize',0,'word',True,False,True),
 (0x4b2a80,'thug_sprite_draw_style_allocate',1,'word',True,False,False),
 (0x48bf30,'thug_create_sprite_style',1,'word',True,False,False),
 (0x4af1a0,'thug_ui_sprite_initialize',0,'word',True,False,True),
 (0x4c71b0,'thug_sprite_draw_style_data',0,'void',False,False,True),
 (0x4c70b0,'thug_sprite_draw_style_visibility',0,'void',False,False,True),
 (0x4c70c0,'thug_sprite_draw_style_order',0,'void',False,False,True),
 (0x4b3d80,'thug_sprite_draw_style_update',0,'void',False,False,True),
 (0x49ec90,'thug_sprite_draw_style_set_rotation',1,'void',False,False,True),
 (0x4af240,'thug_ui_sprite_set_rotation',2,'void',False,False,True),
 (0x563080,'thug_score_display_balance',3,'void',True,True,True),
 (0x563370,'thug_score_display_balance_normal',2,'void',True,True,True),
 (0x563390,'thug_score_display_balance_manual',2,'void',True,True,True)]
for row in NEW:
 bind(*row)
 if row[0] not in observe:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=row[0],end=row[0]);observe.append(row[0])
for at in [0x49ec90,0x4af240]:functions[hex(at)]['float_args']=[0]
for at in [0x563080,0x563370,0x563390]:functions[hex(at)]['float_args']=[1]
bind(0x4a92d0,'thug_ui_set_size',3);functions['0x4a92d0']['float_args']=[0,1]
for at in [0x49ed60,0x4dfc50,0x4c70e0,0x4af1a0]:oracle.cpu.hook_add(UC_HOOK_CODE,identities,begin=at,end=at)
exports=exports+[[0x649a80,'thug_sprite_style_base_methods'],[0x64a744,'thug_sprite_style_methods'],[0x64ad28,'thug_sprite_drawable_methods'],[0x64a228,'thug_ui_sprite_methods']]
METER,CHILD,STYLE,STYLE2,DRAW,DRAW2,TEXTURE,ALTERNATE,STYLE3,DRAW3=[GRAPH+x for x in [0xa000,0xa200,0xa400,0xa480,0xa500,0xa580,0xa600,0xa700,0xa900,0xa980]]
CONTROL,NATIVE,ATTR=METER+0xc00,oracle.stop+0x400,METER+0x1100
assert CONTROL==0x18fac00
memory[METER-BASE:METER-BASE+0x2000]=bytes(0x2000)
for j,(widget,style,draw) in enumerate([(METER,STYLE,DRAW),(CHILD,STYLE2,DRAW2),(ALTERNATE,STYLE3,DRAW3)]):
 memory[widget-BASE:widget-BASE+0x178]=memory[NUMERIC-BASE:NUMERIC-BASE+0x178]
 put(widget,'<I',0x64a228);put(widget+0x14,'<3I',0xa4db8a4b if not j else 0xabc00+j,0xb12b510a,0)
 put(widget+0x20,'<I',ATTR+j*64)
 put(widget+0x28,'<5I',0x6477e4,widget,0,widget+0x28,widget+0x28);put(widget+0x40,'<3I',0x6477e0,0,widget)
 put(widget+0x160,'<2f',160,60);put(widget+0x180,'<I',style)
 put(ATTR+j*64,'<2I',0,ATTR+j*64+8);put(ATTR+j*64+8,'<BBHIII',2,0,0,0xc22eb9a0,0,0)
 put(style,'<3I',0x64a744,TEXTURE,0x54628ed7)
 put(style+0xc,'<8f',12,23,1,1,0,0,0,0)
 put(style+0x30,'<HH5B4B',160,60,1,0,0x73,0,0,128,129,130,131)
 put(style+0x44,'<I',draw);put(draw,'<II4B2f',0x64ad28,0,1,0x61,0x62,0x63,0,0)
 fields.update([widget,widget+0x28,widget+0x40,style,draw])
put(METER+4,'<I',CHILD+0x4c);put(CHILD+0x4c,'<3I',METER,0,0)
put(METER+0x58,'<3I',CHILD,0,0);put(CHILD+4,'<I',METER+0x58)
put(TEXTURE+0x10,'<I',0xdeadbeef);put(TEXTURE+0x20,'<I',0x12345678)
put(SCORE+0x184,'<f',.125)
for i in range(20):put(SCORE+0x94+i*12,'<3f',i*.125,i*12,-i*i*.25)
put(SCORE+0x19c,'<2f',100,200);put(SCORE+0x1a8,'<2f',321,123)
put(CONTROL,'<8I',0,0,0,1,SCORE,METER,BODIES,CHILD)
# Cached original QB instructions invoke one instrumented native command.
slots={}
for i,name in enumerate([0xba95da16,0x58783b40]):
 at=METER+0xa00+i*128;program=at+64;bucket=SYMBOLS+(name&0xfff)*4
 old=struct.unpack_from('<I',memory,bucket-BASE)[0]
 put(at,'<BBHIIII',0,7,0,name,0,program,old);put(bucket,'<I',at)
 put(at+32,'<5I',name,program,1,0,0)
 memory[program-BASE:program-BASE+8]=b'\x01\x43'+struct.pack('<I',NATIVE)+b'\x01\x24';fields.add(program+2)
 slot=CACHETABLE+32+(name&3)*12;old=bytes(memory[slot-BASE:slot-BASE+12]);occupied=struct.unpack_from('<I',old,4)[0]
 if occupied:memory[at+80-BASE:at+92-BASE]=old
 put(slot,'<3I',name,at+32,at+80 if occupied else 0)
put(CACHETABLE+8,'<I',4)
initial=bytes(memory);oracle.initial=initial
def display_native(cpu,address,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);params=oracle.word(sp+4);script=oracle.word(sp+8)
 first=oracle.word(params+4) if params else 0;n=oracle.word(CONTROL);assert n<16
 oracle.setword(CONTROL,n+1)
 row=[oracle.word(script+0xc8),oracle.word(first+4) if first else 0,oracle.word(first+8) if first else 0,bytes(cpu.mem_read(first,1))[0] if first else 0,
      oracle.word(METER+0x14),oracle.word(METER+8),oracle.word(METER+0x58),oracle.word(BODIES+0x2b8),
      oracle.word(SCORE+0x184),oracle.word(SCORE+0x18c),oracle.word(SCORE+0x190),oracle.word(SCORE+0x194)]
 cpu.mem_write(CONTROL+64+n*48,struct.pack('<12I',*row))
 if oracle.word(CONTROL+4) and (not oracle.word(CONTROL+12) or not n):oracle.setword(oracle.word(CONTROL+4),oracle.word(CONTROL+8))
 cpu.reg_write(UC_X86_REG_EAX,1);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
oracle.cpu.hook_add(UC_HOOK_CODE,display_native,begin=NATIVE,end=NATIVE)
def case(calls,patches=(),changes=None,label='balance display',float_fields=()):
 stages=oracle.case(calls,patches,{index[k]:v for k,v in (changes or {}).items()});labels.append(label);previous=0
 for s in stages:
  merged=[]
  for at,data in s['outputs']:
   if at==CONTROL:
    current=int.from_bytes(bytes.fromhex(data),'little');s['callbacks']=current-previous;previous=current
   if merged and merged[-1][0]+len(merged[-1][1])//2==at:merged[-1][1]+=data
   else:merged.append([at,data])
  s['outputs']=merged
  if float_fields:s['float_fields']=list(float_fields)
 if len(labels)%50==0:print('Original balance display cases:',len(labels),flush=True)
 return stages
new_branches={0x563114:'visibility_notification',0x56318f:'show_script',0x563196:'hide_script',0x56325f:'manual_meter',0x5632d0:'normal_meter',0x563332:'negative_offset',
 0x4af266:'current_rotation_changed',0x4af292:'target_rotation_changed',0x4c71c1:'indirect_texture',0x4c71c3:'texture_assigned'}
branch_at.update(new_branches)
for at in new_branches:oracle.cpu.hook_add(UC_HOOK_CODE,branch,begin=at,end=at)
rng=random.Random(0x563080)
special=[0,0x80000000,1,0x007fffff,bits(1),bits(-1),0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc12345,0x7f812345]
for owner in [0,1,0x80000000,0xffffffff]:
 p=[raw(STYLE,bytes(rng.getrandbits(8) for _ in range(0x48))),raw(DRAW,bytes(rng.getrandbits(8) for _ in range(0x40)))]
 case([call(0x49ed60,STYLE,[owner]),call(0x4dfc50,DRAW,[owner]),call(0x4c70e0,STYLE2),call(0x4b2a80,args=[owner]),call(0x48bf30,args=[owner]),call(0x4af1a0,ALTERNATE)],p,label='constructors preserve padding, raw depth and original allocation order')
for depth in special:case([call(0x4dfc50,DRAW,[depth])],label='sprite drawable raw depth bits')
case([call(0x49ed60,STYLE,[123]),call(0x49ec90,STYLE,[0x7f812345])],label='base style rotation uses the actual original return-only data method')
for i in range(180):
 p=[patch(STYLE+off,'<I',rng.getrandbits(32)) for off in [0xc,0x10,0x14,0x18,0x24]]
 p += [patch(STYLE+0x1c,'<2I',rng.choice(special),rng.choice(special)),patch(STYLE+0x30,'<2H',rng.randrange(65536),rng.randrange(65536)),
       patch(STYLE+0x37,'<6B',rng.randrange(256),rng.randrange(256),1,2,3,4),patch(STYLE+4,'<I',0 if i%3==0 else TEXTURE),
       patch(TEXTURE+8,'<I',i%2),patch(TEXTURE+0x10,'<I',TEXTURE+0x20 if i%2 else 0xdeadbeef),patch(DRAW+0x14,'<I',0x12345678)]
 case([call(0x4c71b0,STYLE)]*2+[call(0x49ec90,STYLE,[rng.choice(special)])],p,label='concrete sprite transfer, null/direct/indirect texture and raw signaling-NaN copies',float_fields=[DRAW+0x2c,DRAW+0x30])
for depth in special:
 for hidden in [0,1,255]:
  p=[patch(STYLE+0x28,'<I',depth),patch(STYLE+0x34,'<B',hidden),patch(STYLE+0x2c,'<I',0xffffffff)]
  case([call(0x4c70c0,STYLE),call(0x4c70b0,STYLE),call(0x4b3d80,STYLE)]*2,p,label='sprite depth/list order, visibility bytes and actual virtual dispatch')
case([call(0x4c70c0,STYLE)],[patch(STYLE+0x44,'<I',0)],label='null drawable ordering gate')
for angle in special+[bits(x) for x in [-360,-180,-90,-.001,0,.001,1,45,90,180,360]]:
 for target in [0,1,256]:
  case([call(0x4af240,METER,[angle,target])]*2,label='UI rotation units, epsilon, target independence and repeated comparisons',
       float_fields=[METER+0xf8,METER+0xb4,STYLE+0x24,DRAW+0x34,DRAW+0x2c,DRAW+0x30])

def parent_setup():return [call(0x461a00,UM,[METER])]
# Computed child coordinates and copies of earlier arithmetic NaNs in the
# native observation log retain NaN classification, not a backend-specific sign.
meter_float_fields=[CHILD+off for off in [0x90,0x94,0xd4,0xd8]]+[CONTROL+64+n*48+off for n in range(16) for off in [36,40,44]]+[SCORE+off for off in [0x18c,0x190,0x194]]+[widget+off for widget in [METER,CHILD] for off in [0xe0,0xe4,0xf8,0xb4]]+[style+0x24 for style in [STYLE,STYLE2,STYLE3]]+[draw+off for draw in [DRAW,DRAW2,DRAW3] for off in [0x2c,0x30,0x34]]
for manual in [0,1,255,256]:
 for enabled in [0,1,255,256,257]:
  for active in [0,1,0xffffffff]:
   values=[0,-0.,.01,-.01,.125,-.125,.5,-.5,2.25,-2.25]
   p=[patch(ATTR+16,'<I',active)]
   case(parent_setup()+[call(0x563080,SCORE,[enabled,bits(value),manual]) for value in values],p,
        label='complete meter visibility, raw byte flags, interpolation, signed values and both orientations',float_fields=meter_float_fields)
for step in [.0625,.1,.125,.2,1,10]:
 for i in [0,1,5,17,18]:
  value=bits(step*i)
  for delta in [-1,0,1]:
   if i==0 and delta==-1:continue
   for sign in [0,0x80000000]:
    p=[patch(SCORE+0x184,'<f',step)]
    p += [patch(SCORE+0x98+j*12,'<2f',rng.uniform(-300,300),rng.uniform(-100,100)) for j in range(20)]
    case(parent_setup()+[call(0x563370,SCORE,[1,(value+delta)|sign]),call(0x563390,SCORE,[1,(value+delta)|sign])],p,
         label='adjacent float curve boundaries with nonuniform control points and both wrapper parents',float_fields=meter_float_fields)
for value in [float('nan'),float('inf'),-float('inf')]:
 # _ftol2 integer-indefinite has low word zero, so both points remain valid.
 case(parent_setup()+[call(0x563080,SCORE,[1,bits(value),manual]) for manual in [0,1]],label='nonfinite meter values with valid converted curve index zero',float_fields=meter_float_fields)
for screen in [0,7,0xffffffff]:
 p=[patch(BODIES+0x2b8,'<I',screen),patch(METER+0x14,'<I',(screen+0xa4db8a4b)&0xffffffff),patch(SCORE+8,'<H',0xffff),patch(BODIES+0x14,'<I',0xffffffff)]
 case(parent_setup()+[call(0x563080,SCORE,[1,bits(.2),0])],p,label='signed player ID and screen-name wrap',float_fields=meter_float_fields)
mutations=[(SCORE+0x184,bits(.25)),(SCORE+0x98,bits(500)),(SCORE+0x19c,bits(-321)),(SCORE+0x1a8,bits(-123)),(METER+0x160,bits(400)),(METER+0x164,bits(100)),(METER+0x180,STYLE3),(METER+8,0xdead0000)]
for manual in [0,1]:
 for target,value in mutations:
  p=[patch(CONTROL+4,'<2I',target,value)]
  case(parent_setup()+[call(0x563080,SCORE,[1,bits(.05),manual])],p,label='actual show QB native mutation before geometry/position/style reads',float_fields=meter_float_fields)
  assert oracle.word(CONTROL)==1
for manual in [0,1]:
 calls=[call(0x4af1a0,METER),call(0x4af1a0,CHILD),call(0x461930,METER,[0xa4db8a4b]),
        call(0x461a00,UM,[METER]),call(0x41d1d0,REF,[METER]),call(0x4aa8e0,CHILD,[REF,1]),
        call(0x4a92d0,METER,[bits(160),bits(60),1]),call(0x4a92d0,CHILD,[bits(8),bits(12),1]),
        call(0x563080,SCORE,[1,bits(.55),manual])]
 case(calls,label='actual sprite construction, allocated styles/drawables, parent linkage and complete meter display')
assert all(branches[name]>0 for name in new_branches.values()),dict(branches)
scope='Fifteen complete routines: sprite style/drawable construction and allocation, UI sprite construction, concrete sprite data/order/visibility/update, style/UI rotation, full balance-meter display and normal/manual wrappers. All gameplay/UI callees and concrete virtual data methods execute unchanged in the oracle. Complete parents include show/hide QB dispatch, owned parameter lifecycle, curve interpolation, layout/rotation and sprite-record writes; sixteen cases mutate live fields through actual QB containing an instrumented native command. All arena/global/heap/return bytes compare, with only typed arithmetic NaNs and their subsequent coordinate/log copies classified; raw input data/color/angle copies remain exact. Derived curve indices must select two of twenty points; object graphs are valid and distinct, scripts terminate, allocations succeed, and the heap service is initialized. Drawable rendering/disposal methods are explicitly unavailable and not invoked. Balance physics, animation dispatch, complete movement/startup and playable browser integration remain unfinished.'
fixture={'base':BASE,'memory':'balance-display-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'instrumented_native_callbacks','pointer_exports':exports,'pointer_fields':sorted(fields),'scoped_event_services':{'symbol':'thug_event_services','pointer':SERVICES},'native_callbacks':[{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},{'module':'balance-display-callbacks.wasm','export':'fixture_balance_display_native','original':NATIVE}]}
path=out/'balance-display-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
sdk=ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang';adapter=out/'balance-display-callbacks.wasm'
subprocess.run([str(sdk),'--target=wasm32-unknown-unknown','-O2','-nostdlib','-Wl,--no-entry,--import-memory,--export-all,--global-base=58720256',str(ROOT/'tools/balance_display_callbacks.c'),'-o',str(adapter)],check=True)
print('x86 complete:',len(labels),dict(oracle.counts),dict(branches),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_balance_display_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'branches':dict(branches),'heap_events':dict(oracle.heap_events),'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory'],adapter]},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
