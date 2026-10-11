"""Compare complete frame speed/revert/focus routines with original instructions."""
from pathlib import Path
from unicorn import Uc
# Initialize the established skater/stat/QB graph without executing its cases.
# Observers are attached once to the final oracle; old diagnostic boundaries are
# omitted because this corpus supplies its own exact formatted-output boundary.
original_add=Uc.hook_add;observers={}
def setup_hook(cpu,kind,callback,*args,**kw):
 begin=kw.get('begin',args[1] if len(args)>1 else 1);end=kw.get('end',args[2] if len(args)>2 else 0)
 if getattr(callback,'__name__','')=='observe':observers[begin,end]=(kind,args,kw);return 0
 if begin==end==0x401c30:return 0
 return original_add(cpu,kind,callback,*args,**kw)
source=Path(__file__).with_name('verify_grounded_update.py').read_text().split('\nfor speed in [0,100]:')[0]
Uc.hook_add=setup_hook
try:exec(compile(source.replace("'grounded-update.json'","'frame-prerequisites.json'"),'<initialized frame graph>','exec'))
finally:Uc.hook_add=original_add
for kind,args,kw in observers.values():oracle.cpu.hook_add(kind,oracle.observe,*args,**kw)
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
from specimen import load
FRAME_PRINT,FRAME_OBS=0x1677000,0x1677100
copy(FRAME_PRINT,bytes(0x2000));put(FRAME_PRINT,'<I',FRAME_OBS);put(FRAME_OBS+4,'<I',PHYS)
PRINT=FRAME_PRINT
bind(0x501850,'thug_skater_update_speed_limits')
bind(0x500710,'thug_skater_update_revert_count',diag=True)
bind(0x5007a0,'thug_skater_update_focus_input',heap=True,diag=True)
for at in [0x501850,0x500710,0x5007a0,0x580790,0x42bbf0,0x4fe1f0,0x6236fc]:
 if at not in {a for a,b in observers}:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
exports += [[0x7d1ec8,'thug_frame_counter'],[0x696d60,'thug_timer_offset']]
fields.add(FRAME_OBS+8)
for i in range(64):fields.add(FRAME_OBS+32+i*32+24)
expected_text={0x6466b0:b'M:%s:%i: %s\n',0x64bce0:b'mponents\\SkaterCorePhysicsComponent.cpp',0x64bd08:b'You earned a free revert!!!!'}
def text_hash(data):
 h=0
 for c in data:h=(h*33+c)&0xffffffff
 return h
diagnostics=0
def print_boundary(cpu,at,size,user):
 global diagnostics
 sp=cpu.reg_read(UC_X86_REG_ESP);fmt,file,line,message=struct.unpack('<4I',cpu.mem_read(sp+4,16))
 assert (fmt,file,line,message)==(0x6466b0,0x64bce0,0x293f,0x64bd08)
 for ptr in [fmt,file,message]:assert bytes(cpu.mem_read(ptr,len(expected_text[ptr])+1))==expected_text[ptr]+b'\0'
 n=oracle.word(FRAME_OBS);assert n<64
 target,value=oracle.word(FRAME_OBS+8),oracle.word(FRAME_OBS+12)
 row=[text_hash(expected_text[fmt]),text_hash(expected_text[file]),line,text_hash(expected_text[message]),oracle.word(PHYS+0x318),oracle.word(PHYS+0x31c),target,value]
 cpu.mem_write(FRAME_OBS+32+n*32,struct.pack('<8I',*row));oracle.setword(FRAME_OBS,n+1);diagnostics+=1
 if target:oracle.setword(target,value)
 cpu.reg_write(UC_X86_REG_EAX,0);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
oracle.cpu.hook_add(UC_HOOK_CODE,print_boundary,begin=0x401c30,end=0x401c30)
instruction_hits=Counter();ranges={0x500710:140,0x5007a0:114,0x501850:399}
def parent_trace(cpu,at,size,user):instruction_hits[at]+=1
for at,length in ranges.items():oracle.cpu.hook_add(UC_HOOK_CODE,parent_trace,begin=at,end=at+length-1)
initial=bytes(memory);oracle.initial=initial
labels=[];oracle.cases.clear();oracle.counts.clear();oracle.coverage.clear()
def config_frame(hard=300,soft=100,drag=.001,friction=17,delay=1,threshold=100):
 b=grounded_config(numbers={0x850eb87a:drag,0x78f80ec4:friction})
 for name,value in [(0xcc5f87aa,hard),(0x2eacddb3,soft)]:
  pair=b.alloc(struct.pack('<I2f',0,value,value));b.symbol(name,10,b.structure([(0,5,pair)]))
 b.symbol(0xf4813ad5,2,bits(delay));b.symbol(0xd7e8d8de,1,threshold&0xffffffff)
 # Actual synchronous QB, with a terminal native observer that can change state.
 name=0xd7196d01;code=b.alloc(b'\x01\x43'+struct.pack('<I',NATIVE)+b'\x01\x24');fields.add(code+2)
 entry=b.alloc(struct.pack('<5I',name,code,1,0,0));slot=CACHETABLE+32+(name&3)*12
 previous=next((bytes.fromhex(data) for at,data in reversed(b.extra) if at==slot),initial[slot-BASE:slot-BASE+12]);link=b.alloc(previous)
 b.extra.append(patch(slot,'<3I',name,entry,link));b.symbol(name,7,code)
 return b
def run(at,p=(),b=None,changes=None,label='frame prerequisite',repeat=1,before=(),floats=()):
 b=b or config_frame();cpu=oracle.cpu
 cpu.reg_write(UC_X86_REG_FPSW,0);cpu.reg_write(UC_X86_REG_FPTAG,0xffff);cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
 stages=oracle.case(list(before)+[call(at,PHYS)]*repeat,b.patches()+list(p),{index[k]:v for k,v in (changes or {}).items()})
 labels.append(label);previous=0;previous_qb=0
 for step in stages:
  step['float_fields']=list(floats);count=previous;qb=previous_qb
  for at,data in step['outputs']:
   if at<=FRAME_OBS<at+len(data)//2:count=int.from_bytes(bytes.fromhex(data)[FRAME_OBS-at:FRAME_OBS-at+4],'little')
   if at<=GOBS<at+len(data)//2:qb=int.from_bytes(bytes.fromhex(data)[GOBS-at:GOBS-at+4],'little')
  step['callbacks']=count-previous+qb-previous_qb;previous=count;previous_qb=qb
 if len(labels)%50==0:print('Frame prerequisite cases',len(labels),flush=True)
 return stages

computed=[BODIES+0xac,BODIES+0xb4,BODIES+0xb8,PHYS+0x350,PHYS+0x320,PHYS+0x314]
for speed in [0,.00001,.001,10,99,100,101,299,300,301,1000,-1000,1e-30,1e30]:
 for override in [0,-0.,-1,-2,.01,1,math.nan]:
  p=[patch(BODIES+0xac,'<4f',speed,37,speed/2,9),patch(PHYS+0x350,'<3f',override,80,200)]
  run(0x501850,p,label=f'horizontal speed {speed} override {override}',floats=computed)
for override in [-3,-2,-1,-.001,0,.001,1e-40,1e30,math.inf,-math.inf,math.nan]:
 for dt in [-.1,0,.001,.1,1e30]:
  p=[patch(PHYS+0x350,'<3f',override,100,300),patch(PHYS+0x320,'<f',override),patch(PHYS+0x314,'<f',999),patch(PHYS+0x8c,'<f',dt),patch(BODIES+0xac,'<4f',0,37,50,9)]
  run(0x501850,p,label=f'override timer {override} dt {dt}',repeat=2,floats=computed)
for hard,soft in [(300,100),(100,300),(0,0),(-100,-200),(math.nan,100),(300,math.nan),(math.inf,100),(300,-math.inf)]:
 for x,z in [(0,0),(100,0),(300,0),(3,4)]:
  run(0x501850,[patch(BODIES+0xac,'<4f',x,123,z,0)],config_frame(hard,soft),label='hard/soft strict thresholds',floats=computed)
for raw_y in [0,0x80000000,0x7f800001,0xff800001,0x7fc12345,0xffc12345,0x7f800000,0xff800000]:
 run(0x501850,[patch(BODIES+0xac,'<4I',bits(1000),raw_y,bits(10),bits(4))],label='raw vertical bits survive horizontal drag',floats=computed)
for value in [math.nan,math.inf,-math.inf]:
 run(0x501850,[patch(BODIES+0xac,'<4f',value,99,value,1)],label='nonfinite horizontal speed',floats=computed)
for count in [0,1,2,0x80000000,0xffffffff]:
 for elapsed in [0,999,1000,1001,1666,1667,0x7fffffff,0x80000000,0xffffffff]:
  run(0x500710,[patch(PHYS+0x318,'<2I',count,(1666-elapsed)&0xffffffff)],label=f'revert count {count} unsigned elapsed {elapsed}',repeat=2)
for delay in [0,-1,.0005,.9999,1.0001,1e-30,1e10,1e30,math.inf,math.nan]:
 for elapsed in [0,1,1000,0xffffffff]:
  run(0x500710,[patch(PHYS+0x318,'<2I',2,(1666-elapsed)&0xffffffff)],config_frame(delay=delay),label=f'revert threshold conversion {delay}/{elapsed}')
for delay in [-0x80000000,-1,0,1,16777217,0x7fffffff]:
 for elapsed in [0,1000,1001,0xffffffff]:
  b=config_frame();b.symbol(0xf4813ad5,1,delay&0xffffffff)
  run(0x500710,[patch(PHYS+0x318,'<2I',2,(1666-elapsed)&0xffffffff)],b,label=f'exact integer delay product {delay}/{elapsed}')
run(0x500710,[patch(PHYS+0x318,'<2I',2,0),patch(SYMBOLS+(0xf4813ad5&0xfff)*4,'<I',0)],label='missing optional revert delay')
for target,value in [(PHYS+0x318,0),(PHYS+0x318,7),(PHYS+0x31c,123),(0x7d1ec8,101),(0x696d60,0x80000000),(0x696d60,0xffffffff)]:
 run(0x500710,[patch(PHYS+0x318,'<2I',2,0),patch(FRAME_OBS+8,'<2I',target,value)],label='diagnostics mutate count/time before reload')
for held in [0,1,255]:
 for latch in [0,1,255]:
  for elapsed in [0,99,100,101,1666,0x7fffffff,0x80000000,0xffffffff]:
   run(0x5007a0,[patch(PHYS+0x14c1,'<B',latch),patch(INPUT+0xe0,'<B3sI',held,b'xyz',(1666-elapsed)&0xffffffff)],label=f'focus hold {held} latch {latch} age {elapsed}',repeat=2)
for threshold in [-1,0,0x7fffffff,0x80000000,0xffffffff]:
 for elapsed in [0,1,100,0x7fffffff,0x80000000,0xffffffff]:
  run(0x5007a0,[patch(INPUT+0xe0,'<B3xI',1,(1666-elapsed)&0xffffffff)],config_frame(threshold=threshold),label='focus signed threshold')
for target,value,width in [(PHYS+0x14c1,0,1),(PHYS+0x14c1,255,1),(INPUT+0xe0,0,1),(PHYS+0x150c,INPUT+0x200,4)]:
 run(0x5007a0,[patch(INPUT+0xe0,'<B3xI',1,0),raw(INPUT+0x200,bytes(0x200)),patch(GOBS+4,'<4I',target,value,width,0xd7196d01)],label='focus QB mutates live latch/input',repeat=2)
pe=load();md=Cs(CS_ARCH_X86,CS_MODE_32);coverage={}
for at,length in ranges.items():
 ins=list(md.disasm(pe.get_data(at-0x400000,length),at));missing=[hex(i.address) for i in ins if not instruction_hits[i.address]]
 coverage[hex(at)]={'total':len(ins),'covered':len(ins)-len(missing),'missing':missing}
 assert not missing,(hex(at),missing)
assert diagnostics>0 and qb_calls['0xd7196d01']>0
scope='Complete frame speed limiting501850, revert recovery500710 and focus input5007a0. Original stats, parameter access, timing, vector/drag operations and synchronous QB execute unchanged. Raw vertical words, signed/unsigned expiry, special override bit patterns, callbacks changing count/clock/input/latch, repeated updates, finite/nonfinite arithmetic and exact arena/global/heap bytes compare. Only declared computed NaNs classify. Diagnostics/heap/OS and terminal native QB remain explicit host/test boundaries; required stat configuration, valid components and successful allocation remain contracts. Not the complete movement dispatcher or a playable level.'
fixture={'base':BASE,'memory':'frame-prerequisites-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'diagnostic_and_native_qb_callbacks','pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'native_callbacks':[{'module':'frame-prerequisites-callbacks.wasm','export':'fixture_frame_print','slots':[FRAME_PRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]}
callback=out/'frame-prerequisites-callbacks.wasm'
subprocess.run([str(ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang'),'--target=wasm32-unknown-unknown','-O2','-nostdlib','-Wl,--no-entry,--export-all,--import-memory',str(ROOT/'tools/frame_prerequisites_callbacks.c'),'-o',str(callback)],check=True)
path=out/'frame-prerequisites-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
print('Original frame prerequisites',len(labels),dict(oracle.counts),coverage,flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_frame_prerequisites_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'instruction_coverage':coverage,'diagnostic_callbacks':diagnostics,'native_qb_calls':dict(qb_calls),'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory'],callback]},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS frame prerequisites',len(labels),sum(oracle.counts.values()))
