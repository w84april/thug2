"""Original decal storage, scene/texture lookup, buffer access and grid queries."""
import hashlib,itertools,json,random,struct,subprocess
from collections import Counter
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EAX,UC_X86_REG_EIP,UC_X86_REG_FPSW,UC_X86_REG_FPTAG,UC_X86_REG_MXCSR
from specimen import ROOT,SHA256,load
from script_heap_oracle import ScriptHeapOracle
from decal_geometry_fixtures import build_geometry,build_lifetime,build_lighting
out=ROOT/'local/validation/collision';report_path=out.parent/'decal-prerequisites.json';report_path.unlink(missing_ok=True)
sdk=ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang'
callback=out/'decal-device-callbacks.wasm'
subprocess.run([str(sdk),'--target=wasm32-unknown-unknown','-O2','-nostdlib','-Wl,--no-entry,--import-memory,--export=fixture_decal_vertex_lock',str(ROOT/'tools/decal_device_callbacks.c'),'-o',str(callback)],check=True)
BASE,SIZE=0x1800000,0x40000
CONTEXT,MANAGER,DEVICE,METHODS,CONTROL=BASE+0x20,BASE+0x100,BASE+0x400,BASE+0x440,BASE+0x600
BUFFER,STACK,MATERIAL,MESH,PROJECTION,GEOMETRY,DICTIONARY,VERTEX,INDEX,OUTPUT,COPY= [BASE+x for x in [0x1000,0x10000,0x15000,0x15400,0x15800,0x15900,0x15a00,0x15b00,0x15c00,0x15d00,0x16000]]
SCENES,NODES,TABLES,BUCKETS,LINKS,LOG,HEAP=[BASE+x for x in [0x18000,0x19000,0x19400,0x1a000,0x1b000,0x1c000,0x20000]]
CALLBACK=0x3f00100
rng=random.Random(0x490d20);memory=bytearray(b'\xad'*SIZE)
def put(at,fmt,*v):struct.pack_into(fmt,memory,at-BASE,*v)
def patch(at,fmt,*v):return [at,struct.pack(fmt,*v).hex()]
def raw(at,data):return [at,bytes(data).hex()]
def bits(f):return int.from_bytes(struct.pack('<f',f),'little')
put(CONTEXT,'<8I',HEAP,BASE+SIZE,0,LOG,BASE,BASE+SIZE,0,0);put(MANAGER+0x124,'<I',MANAGER+0x200)
put(DEVICE,'<2I',METHODS,CONTROL);put(METHODS+0x2c,'<I',CALLBACK)
put(CONTROL,'<8I',0,0x8876086c,0xffffffff,0,0,VERTEX,0,0)
put(VERTEX,'<7I',4096,0xabc,DEVICE,COPY,0,0,0);put(INDEX+16,'<I',COPY+128)
put(GEOMETRY+0x14,'<I',MESH);put(DICTIONARY+12,'<I',TABLES)
for i in range(3):
 put(SCENES+i*0x100+0xd0,'<I',TABLES+i*32)
 put(NODES+i*16,'<4I',0,SCENES+i*0x100,0,NODES+(i+1)*16)
 put(TABLES+i*32,'<6I',2,BUCKETS+i*0x100,0,0,0,0)
 for j in range(4):put(BUCKETS+i*0x100+j*12,'<3I',j,0,0)
put(NODES+48,'<4I',0,0xffffffff,0,NODES+48)
# Same checksum with null payload must continue to collision nodes.
for i in range(3):
 put(BUCKETS+i*0x100+12,'<3I',0x101,0,LINKS+i*64)
 put(LINKS+i*64,'<3I',0x201,COPY+i*64,LINKS+i*64+16)
 put(LINKS+i*64+16,'<3I',0x101,COPY+i*64+16,0)
initial=bytes(memory);globals_=[['thug_collision_scene_list',0x6fa7ec,4]];defaults=[NODES]
functions={}
def bind(at,name,argc=0,result='void',this=True):functions[hex(at)]={'name':name,'this':this,'result':result,'cleanup':argc*4 if this else 0,'memory':False}
bind(0x490cd0,'thug_decal_choose_slot',1,'word')
bind(0x490d20,'thug_geometry_stack_initialize');bind(0x490d50,'thug_geometry_stack_push',1);bind(0x490d80,'thug_geometry_stack_pop',1)
bind(0x490e40,'thug_decal_projection_initialize',result='word')
bind(0x4b7f30,'thug_decal_collapse_triangle',2,this=False)
bind(0x4d1a90,'thug_render_material_initialize',result='word');bind(0x4d4be0,'thug_render_mesh_initialize',result='word')
bind(0x4a2ba0,'thug_render_geometry_mesh',result='word');bind(0x49f540,'thug_texture_dictionary_find',1,'word')
bind(0x4d4090,'thug_vertex_buffer_lock',4,'word');bind(0x4d42f0,'thug_index_buffer_lock',4,'word')
bind(0x528560,'thug_component_copy_direction',1,'word')
bind(0x49cb00,'thug_scene_find_object',1,'word');bind(0x48c510,'thug_scenes_find_object',1,'word',False)
for at,name,n in [(0x4b7fa0,'thug_decal_segments_overlap',8),(0x4b88d0,'thug_decal_triangle_in_square',6)]:
 bind(at,name,n,'byte',False);functions[hex(at)]['float_args']=list(range(n))
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,MANAGER,globals_,defaults,functions,observe=[int(k,16) for k in functions]+[0x462050])
def device_hook(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);device,offset,length,output,flags=struct.unpack('<5I',cpu.mem_read(sp+4,20))
 control=oracle.word(device+4);n=oracle.word(control);oracle.setword(control,n+1);buffer=oracle.word(control+20)
 values=[device,offset,length,output,flags,oracle.word(output),oracle.word(buffer+16),oracle.word(buffer+20),oracle.word(buffer+24),0]
 cpu.mem_write(control+32+n*40,struct.pack('<10I',*values))
 if oracle.word(control+8)!=0xffffffff:oracle.setword(output,oracle.word(control+8))
 if oracle.word(control+12):oracle.setword(oracle.word(control+12),oracle.word(control+16))
 cpu.reg_write(UC_X86_REG_EAX,oracle.word(control+4));cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+24)
oracle.cpu.hook_add(UC_HOOK_CODE,device_hook,begin=CALLBACK,end=CALLBACK)
labels=[]
def call(fn,this=0,args=()):return fn,this,[v&0xffffffff for v in args]
def case(calls,p=(),changes=None,label='decal storage'):
 oracle.cpu.reg_write(UC_X86_REG_FPSW,0);oracle.cpu.reg_write(UC_X86_REG_FPTAG,0xffff);oracle.cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
 stages=oracle.case(calls,p,changes);labels.append(label);previous=0
 for s in stages:
  for at,data in s['outputs']:
   if at==CONTROL:
    current=int.from_bytes(bytes.fromhex(data),'little');s['callbacks']=current-previous;previous=current
  merged=[]
  for at,data in s['outputs']:
   if merged and merged[-1][0]+len(merged[-1][1])//2==at:merged[-1][1]+=data
   else:merged.append([at,data])
  s['outputs']=merged
 return stages
for address,fn,size in [(STACK,0x490d20,0x4008),(MATERIAL,0x4d1a90,0x110),(MESH,0x4d4be0,0xd8),(PROJECTION,0x490e40,0x44)]:
 for shift in range(4):
  for fill in [0,0xff,0xad]:
   case([call(fn,address+shift),call(fn,address+shift)],[raw(address+shift,bytes([fill])*size)],label='constructor selective writes, unaligned storage and repeat')
for n in [0,1,2,16,255,256]:
 for free in [-1,0,1,15,254,255]:
  for mode in range(4):
   remaining=[0xffffffff if mode==0 else (i+1 if mode==1 else rng.getrandbits(32)|1) for i in range(256)]
   starts=[(v+(i%7 if mode!=3 else 0x80000000+i))&0xffffffff for i,v in enumerate(remaining)]
   if free>=0:remaining[free]=0
   case([call(0x490cd0,BUFFER,[n])],[patch(BUFFER,'<512I',*remaining,*starts)],label='free slots, signed wrapping ages, counts and ties')
for slot in range(256):
 data=bytes(rng.getrandbits(8) for _ in range(72))
 case([call(0x4b7f30,args=[BUFFER,slot])],[raw(BUFFER+0x3410+slot*72,data)],label='all triangle slots copy exact raw vertex words')
for width in [0,1,2,3,4,5,7,12,16,24,31,32,127,128]:
 data=bytes(rng.getrandbits(8) for _ in range(256))
 for count in [0,1,3,7]:
  p=[patch(STACK,'<2I',0,width),raw(COPY,data)]
  calls=[call(0x490d50,STACK,[COPY+i]) for i in range(count)]+[call(0x490d80,STACK,[OUTPUT+i]) for i in range(count)]
  case(calls,p,label='stack LIFO, byte tails and retained popped storage')
for width,delta in itertools.product([1,3,4,5,7,12,31,128],[-16,-5,-4,-3,-1,0,1,3,4,5,16]):
 p=[patch(STACK,'<2I',256,width),raw(STACK+8,bytes(rng.getrandbits(8) for _ in range(1024)))]
 case([call(0x490d50,STACK,[STACK+8+256+delta])],p,label='push forward word/byte overlap propagation')
 p=[patch(STACK,'<2I',256+width,width),raw(STACK+8,bytes(rng.getrandbits(8) for _ in range(1024)))]
 case([call(0x490d80,STACK,[STACK+8+256+delta])],p,label='pop forward word/byte overlap propagation')
for target in [STACK,STACK+4]:
 for value in [0,1,4,128]:
  p=[patch(STACK,'<2I',8,4),patch(STACK+12,'<I',value)]
  case([call(0x490d80,STACK,[target])],p,label='pop output aliases cursor or width after initial decrement')
for delta,shift in itertools.product(range(-19,20),range(4)):
 src=COPY+128+shift;dest=src+delta
 case([call(0x528560,src-0x48,[dest])],[raw(COPY,bytes(rng.getrandbits(8) for _ in range(512)))],label='direction words, all overlaps and byte alignments')
for value in [0,MESH,0xffffffff,0x7f812345]:case([call(0x4a2ba0,GEOMETRY)],[patch(GEOMETRY+0x14,'<I',value)],label='mesh pointer accessor raw words')
for key in [0,1,0x101,0x201,0x301,2,3,0xffffffff]:
 for shift in [0,1,2,32,33,34]:
  p=[patch(TABLES+i*32,'<I',shift) for i in range(3)]
  calls=[call(0x49cb00,SCENES+i*0x100,[key]) for i in range(3)]+[call(0x48c510,args=[key]),call(0x49f540,DICTIONARY,[key])]
  case(calls,p,label='scene and texture lookup collisions, null values and masked shift')
for found in [-1,0,1,2]:
 p=[patch(LINKS+i*64+20,'<I',COPY if i==found else 0) for i in range(3)]
 case([call(0x48c510,args=[0x101])],p,label='ordered scene fallback')
case([call(0x48c510,args=[0x101])],changes={0:NODES+48},label='empty sentinel scene list')
case([call(0x49f540,DICTIONARY,[0x101])],[patch(DICTIONARY+12,'<I',0)],label='optional missing texture table')
case([call(0x49cb00,SCENES,[0])],[patch(TABLES,'<2I',0,0)],label='null first bucket address')
for offset,size,flags in itertools.product([0,1,4096,0xffffffff],[0,1,128,0xffffffff],[0,0x10,0x2000,0x2010,0xffffffff]):
 for output in [OUTPUT,VERTEX,VERTEX+0x10,VERTEX+0x14,VERTEX+0x18]:
  case([call(0x4d4090,VERTEX,[offset,size,output,flags])],label='vertex lock bookkeeping and output aliases')
for result,output_word,mutation in itertools.product([0,1,0x80004005,0xffffffff],[0xffffffff,0,COPY+24],[0,VERTEX+16,VERTEX+20,VERTEX+24]):
 p=[patch(CONTROL+4,'<4I',result,output_word,mutation,0x87654321)]
 case([call(0x4d4090,VERTEX,[17,0,OUTPUT,0x2000])]*2,p,label='device result/output and callback mutations, repeated lock')
for offset,size,flags,output in itertools.product([0,0xffffffff],[0,0xffffffff],[0,0x2000],[OUTPUT,INDEX+16]):
 case([call(0x4d42f0,INDEX,[offset,size,output,flags])],label='index buffer returns stored pointer and ignores range/flags')

# Include degeneracies which conventional intersection replacements get wrong.
predicate_results=Counter()
def predicate(at,values,label):
 s=case([call(at,args=values)],label=label)[0];predicate_results[f'{at:x}:{s["result"]}']+=1
for points in [(-2,0,2,0,0,-2,0,2),(0,0,1,0,2,0,3,0),(0,0,0,0,1,1,1,1),
               (0,0,1,1,1,1,2,0),(-3,2,3,2,-1,-1,1,-1)]:
 for order in [(0,1,2,3),(1,0,2,3),(0,1,3,2),(2,3,0,1)]:
  predicate(0x4b7fa0,[bits(points[j*2+k]) for j in order for k in range(2)],'segment crossing, endpoint, degenerate and collinear behavior')
for points in [(-4,-4,4,-4,0,4),(-.5,-.5,.5,-.5,0,.5),(2,2,3,2,2,3),
               (-2,0,2,0,0,0),(-1,-1,-1,-1,-1,-1),(-2,1,2,1,0,2),(-3,2,3,2,0,3)]:
 for order in itertools.permutations(range(3)):
  predicate(0x4b88d0,[bits(points[j*2+k]) for j in order for k in range(2)],'triangle containment, winding, edges and degenerate points')
special=[0,0x80000000,1,0x80000001,0x007fffff,0x00800000,bits(-1)-1,bits(-1),bits(-1)+1,
         bits(1)-1,bits(1),bits(1)+1,0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc12345,0x7f812345]
for at,n in [(0x4b7fa0,8),(0x4b88d0,6)]:
 for i in range(n):
  for word in special:
   values=[bits(x) for x in [-2,-2,2,-2,0,2,0,-3][:n]];values[i]=word
   predicate(at,values,'ordered numeric boundary, nonfinite and raw NaN arguments')
 for i in range(400):
  values=[bits(rng.uniform(-5,5)) for _ in range(n)] if i<300 else [rng.getrandbits(32) for _ in range(n)]
  predicate(at,values,'seeded finite and full exponent predicates')
assert all(predicate_results[f'{at:x}:{result}'] for at in [0x4b7fa0,0x4b88d0] for result in [0,1])

scope_storage='Seventeen complete routines: decal slot selection, record-stack initialization/push/pop, projection/material/mesh initialization, triangle collapse, direction copy, original segment/triangle-square predicates, mesh access, scene/global/texture lookup and vertex/index-buffer access. Full arena/global/result comparison covers signed age wrap, all 256 triangle slots, overlapping word/byte copies, untouched fields, masked shifts, sentinel order, optional tables and buffer-output aliases. Only external GPU Lock is a diagnostic callback; original wrapper ordering, arguments, HRESULT and callback mutations are compared. Valid capacities/list/member storage remain internal contracts. No renderer, wallplant parent or playable level is established.'
storage={'base':BASE,'memory':'decal-storage-memory.bin','globals':globals_,'functions':functions,'float_fields':[],
 'cases':oracle.cases,'case_labels':labels,'scope':scope_storage,'callback_counter':'device_callbacks',
 'native_callbacks':[{'module':'decal-device-callbacks.wasm','export':'fixture_decal_vertex_lock','slots':[METHODS+0x2c]}]}
storage_path=out/'decal-storage-fixtures.json';storage_path.write_text(json.dumps(storage,separators=(',',':')));(out/storage['memory']).write_bytes(initial)
storage_oracle=oracle
print('Original decal storage:',len(labels),sum(oracle.counts.values()),flush=True)

# Repack the already-pinned real training grid and its original object ordering.
# The new query only reads instance flags/stamps; preserved geometry pointers
# remain exact raw words and are not followed by this bounds-only function.
proof=json.loads((out.parent/'collision-browser.json').read_text())
training_path=out/'scene-training.bin';training=training_path.read_bytes()
assert hashlib.sha256(training).hexdigest()==proof['artifact_hashes'][str(training_path.relative_to(ROOT))]
GRID,OBJECTS,LISTS,BOUNDS=BASE+0x8000,BASE+0x10000,BASE+0x18000,BASE+0x7000
memory=bytearray(b'\xad'*SIZE)
put(CONTEXT,'<8I',HEAP,BASE+SIZE,0,LOG,BASE,BASE+SIZE,0,0);put(MANAGER+0x124,'<I',MANAGER+0x200)
memory[GRID-BASE:GRID-BASE+0x4b30]=training[0x200000:0x204b30]
memory[OBJECTS-BASE:OBJECTS-BASE+605*24]=training[0x100000:0x100000+605*24]
cursor=LISTS
for i in range(400):
 cell=GRID+i*48+0x30;n,old=struct.unpack_from('<I4xI',memory,cell-BASE+0x24)
 pointers=struct.unpack_from('<'+'I'*n,training,old-0x1000000)
 put(cell+0x2c,'<I',cursor)
 for pointer in pointers:put(cursor,'<I',OBJECTS+pointer-0x1100000);cursor+=4
assert cursor<BASE+0x30000
initial=bytes(memory);globals_=[['thug_collision_grid_stamp',0x693998,1]];defaults=[0]
for i in range(2048):globals_.append(['thug_collision_grid_output',0x691998+i*4,4,i*4]);defaults.append(0xadadadad)
functions={'0x418710':{'name':'thug_collision_grid_bounds','this':True,'result':'word','cleanup':4,'memory':False,'pointer_result':True}}
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,MANAGER,globals_,defaults,functions,observe=[0x418710,0x6236fc]);labels=[]
def grid_case(data,p=(),stamp=0,repeat=1,label='training grid'):
 oracle.cpu.reg_write(UC_X86_REG_FPSW,0);oracle.cpu.reg_write(UC_X86_REG_FPTAG,0xffff);oracle.cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
 stages=oracle.case([(0x418710,GRID,[BOUNDS])]*repeat,[raw(BOUNDS,data),*p],{0:stamp});labels.append(label);return stages
def box(lo,hi):return struct.pack('<8f',*lo,1,*hi,1)
header=struct.unpack_from('<8f2f2i',memory,GRID-BASE);lo=header[:3];hi=header[4:7]
for stamp in [0,1,254,255]:
 grid_case(box(lo,hi),stamp=stamp,repeat=3,label='whole actual training grid, repeated byte-stamp wrap')
 grid_case(box(hi,lo),stamp=stamp,label='inverted training box')
 for j in range(0,605,23):
  # Use the geometry object's original bounds from its already-relocated data.
  obj=struct.unpack_from('<I',training,0x100000+j*24+12)[0]
  grid_case(training[obj-0x1000000+16:obj-0x1000000+48],stamp=stamp,label='actual training object bounds')
for i in range(80):
 center=[rng.uniform(lo[j]-1000,hi[j]+1000) for j in range(3)]
 upper=[v+rng.choice([-1,0,0.5,10,500,3000]) for v in center]
 grid_case(box(center,upper),label='training grid clipping and cell boundaries')
for flags,stamp in itertools.product([0,2,4,6,8,255],[0,255]):
 p=[patch(OBJECTS+i*24+8,'<BBB',flags,0xad,(stamp+1)&255 if i%3==0 else stamp) for i in range(605)]
 grid_case(box(lo,hi),p,stamp,repeat=2,label='object exclusions and stamp equality/wrap')
# Degenerate dimensions and all numeric inputs remain within the valid positive
# grid dimension contract; query coordinates may be unordered/nonfinite.
for size in [1,0x007fffff,0x00800000,bits(1e-20),bits(1),bits(3),bits(1e20),0x7f7fffff]:
 for point in [0,0x80000000,1,bits(0.5),bits(-0.5),0x7f7fffff,0x7f800000,0xff800000,0x7fc12345]:
  p=[patch(GRID+0x20,'<2I',size,size)]
  data=struct.pack('<8I',point,0,point,bits(1),point,0,point,bits(1))
  grid_case(data,p,label='PC24 reciprocal exponent and ordered coordinate conversion')
scope_grid='Complete 418710 bounds query against the pinned training 20 x 20 grid, preserving the 605-instance order and cell membership. All 2048 global output slots, full arena, stamp bytes and return relocation compare exactly. Covers whole/object/random/inverted boxes, repeated stamp wrap, flags, existing stamps, subnormal/wide reciprocal arithmetic and nonfinite coordinates. Required positive dimensions, valid cells and output capacity are contracts. This is query behavior, not rendering or complete wallplant.'
grid={'base':BASE,'memory':'decal-grid-memory.bin','globals':globals_,'functions':functions,'float_fields':[],
 'cases':oracle.cases,'case_labels':labels,'scope':scope_grid,'pointer_exports':[[0x691998,'thug_collision_grid_output']]}
grid_path=out/'decal-grid-fixtures.json';grid_path.write_text(json.dumps(grid,separators=(',',':')));(out/grid['memory']).write_bytes(initial)
print('Original decal grid:',len(labels),sum(oracle.counts.values()),flush=True)
grid_oracle=oracle
geometry,geometry_path,geometry_oracle=build_geometry(out)
lifetime,lifetime_path,lifetime_oracle=build_lifetime(out)
lighting,lighting_path,lighting_oracle=build_lighting(out)
pe=load();pe_bytes=pe.get_memory_mapped_image();image_base=pe.OPTIONAL_HEADER.ImageBase
initial_globals={'thug_decal_reserved_slots':128,'thug_decal_fade_step':8,'thug_decal_area_threshold':0x47a20000}
for name,at in [('thug_decal_reserved_slots',0x67dde0),('thug_decal_fade_step',0x67dde4),('thug_decal_area_threshold',0x67ddf0)]:
 assert struct.unpack_from('<I',pe_bytes,at-image_base)[0]==initial_globals[name]
subprocess.run(['node',str(ROOT/'tools/verify_decal_prerequisites_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'storage_counts':dict(storage_oracle.counts),'grid_counts':dict(oracle.counts),
 'storage_callee_coverage':dict(storage_oracle.coverage),'grid_callee_coverage':dict(oracle.coverage),
 'initial_globals':initial_globals,'lifetime_counts':dict(lifetime_oracle.counts),'lifetime_callee_coverage':dict(lifetime_oracle.coverage),'lighting_counts':dict(lighting_oracle.counts),'lighting_callee_coverage':dict(lighting_oracle.coverage),'predicate_results':dict(predicate_results),'geometry_counts':dict(geometry_oracle.counts),'geometry_callee_coverage':dict(geometry_oracle.coverage),
 'scope':scope_storage+' '+scope_grid+' '+geometry['scope']+' '+lifetime['scope']+' '+lighting['scope'],'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
 'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [storage_path,grid_path,geometry_path,lifetime_path,lighting_path,out/lifetime['memory'],out/lighting['memory'],out/geometry['memory'],out/storage['memory'],out/grid['memory'],callback,training_path]},
 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS decal prerequisites')
