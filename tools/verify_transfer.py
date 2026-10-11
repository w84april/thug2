"""Original-instruction comparisons for the complete transfer candidate search."""
from pathlib import Path
# Reuse the already validated training collision and required script fixture.
# Stop before any side-contact test executes; never overwrite its evidence.
prefix=Path(__file__).with_name('verify_side_contact.py').read_text().split('# Writable checksum')[0]
exec(compile(prefix.replace("'side-contact.json'","'transfer.json'"),str(Path(__file__).with_name('verify_side_contact.py')),'exec'))
import math
CACHE_A,CACHE_B,BOUNDS,MODE,MOTION,FROM,ORIGIN,VELOCITY,RESULT=0x1632000,0x1633000,0x1634000,0x1634100,0x1635000,0x1637000,0x1637010,0x1637020,0x1637040
NEW=[(0x402600,'thug_collision_segment_copy',2,'word',False,False,True),(0x40aa00,'thug_collision_cache_register',1,'void',False,False,False),(0x40aa40,'thug_collision_cache_unregister',1,'void',False,False,False),(0x40ab40,'thug_collision_cache_destroy',0,'void',False,False,True),(0x40ab50,'thug_collision_cache_initialize',0,'word',False,False,True),(0x40aba0,'thug_collision_cache_build',1,'void',False,False,True),(0x412fc0,'thug_moving_collision_bounds',0,'word',False,False,True),(0x43daa0,'thug_skater_transfer_speed',0,'double',False,False,True),(0x502240,'thug_skater_find_transfer',5,'byte',False,False,True)]
for row in NEW:
 bind(*row);oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=row[0],end=row[0])
for j in range(8):glob('thug_collision_cache_registry',0x6918ec+4*j,0,offset=4*j)
glob('thug_collision_cache_mask',0x69190c)
stack_objects=[];root_active=False

def transfer_observe(cpu,address,size,user):
 global root_active
 sp=cpu.reg_read(UC_X86_REG_ESP)
 if address==0x502240:
  if oracle.word(sp)==oracle.stop:root_active=True;cpu.mem_write(0x691968,bytes(cpu.mem_read(QUERY,12)))
 elif address==0x502f1d:
  if oracle.word(sp)==oracle.stop:cpu.mem_write(QUERY,bytes(cpu.mem_read(0x691968,12)));root_active=False
 elif root_active:
  ptr=cpu.reg_read(UC_X86_REG_ECX);count=oracle.word(ptr+0xfc0)
  assert count<=500,count
  slot=next(i for i in range(8) if oracle.word(0x6918ec+i*4)==ptr and oracle.word(0x69190c)&(1<<i))
  stack_objects.append({'original':ptr,'global':['thug_collision_cache_registry',4*slot],'mask':['thug_collision_cache_mask',slot,0],'size':0xfcc,'blocks':[[0,bytes(cpu.mem_read(ptr,32)).hex()],[0xfc0,bytes(cpu.mem_read(ptr+0xfc0,12)).hex()],[32,bytes(cpu.mem_read(ptr+32,count*8)).hex(),list(range(0,count*8,4))]]})
for at in [0x502240,0x502f1d,0x40ab40]:oracle.cpu.hook_add(UC_HOOK_CODE,transfer_observe,begin=at,end=at)
for at,name in {0x5022b5:'zero_horizontal_speed',0x5023af:'raised_scan',0x5023b9:'backed_scan',0x502619:'scan_result',0x502649:'wall_candidate',0x50275a:'accepted_candidate',0x502873:'project_velocity',0x5028d3:'minimum_speed',0x50291c:'minimum_vertical',0x50296b:'maximum_vertical',0x5029b8:'gravity',0x502a9f:'apex_prediction',0x502ab6:'restore_failed_height_or_time',0x502b6b:'negative_discriminant',0x502bf0:'arc_attempt',0x502d83:'second_arc',0x502e01:'blocked_arc_raise',0x502e1e:'restore_blocked_arc',0x502e77:'transfer_success',0x40ad00:'static_cache_candidate',0x40ad8a:'moving_cache_candidate'}.items():
 branch_at[at]=name;oracle.cpu.hook_add(UC_HOOK_CODE,branch,begin=at,end=at)
base_case=case

def case(calls,patches=(),changes=None,label='transfer'):
 stack_objects.clear()
 result=base_case(calls,patches,changes,label)
 roots=[s for s in result if s['fn']=='0x502240']
 assert len(roots)<=1
 if roots:roots[0]['stack_objects']=stack_objects[:]
 return result

def config(high=500,low=100,gravity=-800,min_vertical=150,max_distance=500,min_time=0):
 b=Build();b.symbol(0x6775e538,10,b.structure([(0x7213ef07,2,bits(high)),(0xcc461b87,2,bits(low))]))
 b.symbol(0x8cbc89dd,10,b.structure([(0xfaa40754,2,bits(gravity)),(0x95a79c32,2,bits(min_vertical))]))
 for key,val in [(0xc31ca696,1),(0x441c38a0,1),(0xbe33a41e,0),(0xe50a9d56,max_distance),(0x32c20f7e,min_time)]:b.symbol(key,2,bits(val))
 b.symbol(0x9c8c6df1,1,0)
 b.extra += [raw(MODE,bytes(0x11c)),raw(MOTION,bytes(0x186c)),patch(GATE+0x2c,'<I',MODE),patch(PHYS+0x1534,'<I',MOTION),patch(BODIES+0x100,'<I',MOTION),patch(MOTION+4,'<I',0x726e85aa),patch(MOTION+12,'<I',BODIES),patch(MOTION+0x1868,'<f',.5)]
 return b

# Raw forward copies include overlapping sources and every float bit pattern.
for dst,first,last in [(0,32,48),(0,0,16),(4,0,16),(0,4,20),(12,0,4),(16,0,8)]:
 case([call(0x402600,VECTORS+dst,[VECTORS+first,VECTORS+last])],[patch(VECTORS,'<16I',0,0x80000000,0x7f800001,0xffc12345,*range(12))],label='segment raw bits and forward overlap')
for mask in [0,1,0x55,0xaa,0xff,0xffffffff,0x80000080]:
 for cache in [CACHE_A,CACHE_B,0]:
  changes={0x69190c:mask,**{0x6918ec+4*i:CACHE_A if i%2 else CACHE_B for i in range(8)}}
  case([call(0x40aa00,args=[cache]),call(0x40aa00,args=[cache]),call(0x40aa40,args=[cache]),call(0x40aa40,args=[cache]),call(0x40aa40,args=[cache])],changes=changes,label='registry duplicate/full/live mask order')
for mask in [0,0x55,255]:
 case([call(0x40ab50,CACHE_A),call(0x40ab40,CACHE_A)],changes={0x69190c:mask},label='cache construction and destruction')
for dirty in [0,1,255]:
 for radius in [0,1,123,math.inf,math.nan]:
  stages=case([call(0x412fc0,RUNTIME)]*2,[patch(RUNTIME+0xa8,'<B',dirty),patch(RUNTIME+0xa4,'<f',radius)],label='moving bounds dirty lifecycle')
  for s in stages:s['float_fields']=[RUNTIME+off for off in range(0xac,0xcc,4)]
for high,low in [(500,100),(0,0),(-100,300),(1e38,-1e38),(math.inf,0),(math.nan,1)]:
 for factor in [-2,0,.3,1,2,math.nan]:
  b=config(high=high,low=low)
  case([call(0x43daa0,MOTION)],b.patches()+[patch(MOTION+0x1868,'<f',factor)],label='typed transfer speed interpolation')
selected=[0,1,2,3,13,24,26,30,34,39,57,70,98,129,278,400,488,510,521,545]
for i in selected:
 q=loader['queries'][i];segment=struct.unpack('<8f',bytes.fromhex(q['segment']));point=struct.unpack_from('<4f',bytes.fromhex(q['result']),16)
 bounds=[min(segment[j],segment[j+4])-1 for j in range(3)]+[1]+[max(segment[j],segment[j+4])+1 for j in range(3)]+[1]
 for moving in [False,True]:
  links=[]
  if moving:
   links=[patch(COLL_NODES+j*16,'<4I',0,RUNTIME+j*256,0,COLL_NODES+(j+1)*16) for j in range(3)]+[patch(COLL_NODES+48,'<4I',0,0xffffffff,0,COLL_NODES+48)]
  case([call(0x40ab50,CACHE_A),call(0x40aba0,CACHE_A,[BOUNDS]),call(0x40ab40,CACHE_A)],[patch(BOUNDS,'<8f',*bounds)]+links,label=f'cache training {i} moving {moving}')
for alias in [False,True]:
 case([call(0x40ab50,CACHE_A),call(0x40aba0,CACHE_A,[CACHE_A if alias else BOUNDS]),call(0x40ab40,CACHE_A)],[patch(BOUNDS,'<8f',20000,20000,20000,1,21000,21000,21000,1)]+([patch(SCENES+4,'<I',0xffffffff)] if alias else []),label='cache bounds alias or scene miss')

def parent(b=None,p=(),force=0,label='transfer parent',changes=None):
 b=b or config()
 return case([call(0x502240,PHYS,[force,FROM,ORIGIN,VELOCITY,RESULT,QUERY])],b.patches()+list(p),changes,label)[0]
for velocity in [[0,0,0,0],[.001,100,0,0],[100,0,0,0],[0,200,100,0],[math.nan,1,0,0]]:
 parent(p=[patch(FROM,'<4f',20000,20000,20000,1),patch(ORIGIN,'<4f',20000,20000,20000,1),patch(VELOCITY,'<4f',*velocity)],label='low speed or complete empty-space search')
for i in selected:
 q=loader['queries'][i];data=bytes.fromhex(q['result']);normal=struct.unpack_from('<4f',data);point=struct.unpack_from('<4f',data,16)
 length=math.hypot(normal[0],normal[2]);direction=[normal[0]/length if length else 1,0,normal[2]/length if length else 0,0]
 for mode,submode in [(0,0),(1,0),(1,1),(2,0)]:
  for sign in [1,-1]:
   d=[v*sign for v in direction];origin=[point[0]-d[0]*.01,point[1]+100,point[2]-d[2]*.01,1]
   from_=[point[0]-d[0]*100,point[1]+100,point[2]-d[2]*100,1]
   s=parent(p=[patch(FROM,'<4f',*from_),patch(ORIGIN,'<4f',*origin),patch(VELOCITY,'<4f',d[0]*500,200,d[2]*500,0),patch(MOTION+0x48,'<4f',*d),patch(MODE+0x1c,'<I',mode),patch(MOTION+0x18,'<I',submode)],force=1,label=f'training transfer {i} mode {mode}/{submode} sign {sign}')

# Vary actual accepted contacts to cover velocity restoration, the apex branch,
# minimum-speed interpolation, both vertical limits and the second arc probe.
q=loader['queries'][34];data=bytes.fromhex(q['result'])
normal=struct.unpack_from('<4f',data);point=struct.unpack_from('<4f',data,16)
length=math.hypot(normal[0],normal[2]);direction=[normal[0]/length,0,normal[2]/length,0]
def target_patches(mode=1,submode=0,speed=500,vy=200,height=100,alternate=0,dx=100):
 return [patch(FROM,'<4f',point[0]-direction[0]*dx,point[1]+height,point[2]-direction[2]*dx,1),patch(ORIGIN,'<4f',point[0]-direction[0]*.01,point[1]+100,point[2]-direction[2]*.01,1),patch(VELOCITY,'<4f',direction[0]*speed,vy,direction[2]*speed,0),patch(MOTION+0x48,'<4f',*direction),patch(MODE+0x1c,'<I',mode),patch(MODE+0x118,'<B',alternate),patch(MOTION+0x18,'<I',submode)]
for speed in [0,.00001,10,299,300,301,1000]:
 for force in [0,1]:
  parent(p=target_patches(speed=speed),force=force,label=f'accepted contact minimum speed {speed} vertical {force}')
for gravity,vy,height,minimum in [(-800,-2000,100,150),(-800,2000,-50,150),(800,0,100,0),(0,200,100,150),(-800,200,100,math.nan),(-800,math.nan,100,150)]:
 for submode in [0,1]:
  s=parent(b=config(gravity=gravity,min_vertical=minimum),p=target_patches(vy=vy,height=height,submode=submode),label=f'gravity/height/vertical {gravity}/{vy}/{height}/{minimum} mode {submode}')
  s['float_fields']=[VELOCITY+4*i for i in range(4)]+[RESULT+4*i for i in range(9)]
for minimum in [-1,0,.5,1,10,math.nan]:
 parent(b=config(min_time=minimum),p=target_patches(),label=f'minimum flight time {minimum}')
for dx in [-100,0,100]:
 for alternate in [0,1]:
  s=parent(p=target_patches(dx=dx,alternate=alternate),label=f'signed distance {dx} alternate {alternate}')
  if dx==0 and not alternate and s['result']:s['float_fields']=[VELOCITY,VELOCITY+8,VELOCITY+12]
for initial_flag in [0,1,2,255]:
 parent(p=target_patches()+[patch(SKATER_STATE+0x78,'<B',initial_flag),patch(SKATER_STATE+0x7c,'<I',0xdeadbeef)],changes={0x7d1ec8:0xffffffff,0x696d60:0x7fffffff},label='temporary gravity flag timestamp and timer wrap')
for distance in [-1,0,.005,.01,3,math.nan]:
 parent(b=config(max_distance=distance),p=target_patches(),label=f'scan distance boundary {distance}')
# Inputs may share velocity storage; output may replace any caller vector.
for output in [FROM,ORIGIN,VELOCITY]:
 b=config();case([call(0x502240,PHYS,[1,FROM,ORIGIN,VELOCITY,output,QUERY])],b.patches()+target_patches(),label='result aliases caller vector')
for source in [FROM,ORIGIN]:
 b=config();case([call(0x502240,PHYS,[1,FROM,ORIGIN,source,RESULT,QUERY])],b.patches()+target_patches(),label='velocity aliases input vector')
# Instantiate the accepted training mesh as a real rigid moving object; disable
# its static twin and retain normal moving-reference construction/release.
static=struct.unpack_from('<I',data,0x30)[0];geometry=struct.unpack_from('<I',initial,static+12-BASE)[0]
bind(0x413000,'thug_moving_collision_initialize',1,'word');bind(0x40ae40,'thug_moving_collision_set_owner',1)
for at in [0x413000,0x40ae40,0x417210,0x4ff470,0x40b390]:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
for disabled in [0,2,4,6]:
 b=config();p=target_patches()+[patch(static+8,'<H',6),patch(OWNERS+4,'<I',0),patch(COLL_NODES,'<8I',0,RUNTIME,0,COLL_NODES+16,0,0xffffffff,0,COLL_NODES+16)]
 calls=[call(0x413000,RUNTIME,[geometry]),call(0x40ae40,RUNTIME,[OWNERS])]
 if disabled:
  # Patches precede constructor, so set flags through the real initialized
  # geometry fixture only for independent cache filtering below.
  p[-1]=patch(COLL_NODES,'<8I',0,0,0,COLL_NODES+16,0,0xffffffff,0,COLL_NODES+16)
 calls.append(call(0x502240,PHYS,[1,FROM,ORIGIN,VELOCITY,RESULT,QUERY]))
 case(calls,b.patches()+p,label='real moving training mesh and owner reference' if not disabled else 'null moving list entry')
for flags in [0,2,4,6]:
 case([call(0x40ab50,CACHE_A),call(0x40aba0,CACHE_A,[BOUNDS]),call(0x40ab40,CACHE_A)],[patch(BOUNDS,'<8f',point[0]-10,point[1]-10,point[2]-10,1,point[0]+10,point[1]+10,point[2]+10,1),patch(COLL_NODES,'<8I',0,RUNTIME,0,COLL_NODES+16,0,0xffffffff,0,COLL_NODES+16),patch(RUNTIME+8,'<H',flags)],changes={0x693998:255},label=f'moving cache flags {flags} and stamp wrap')
for key in ['transfer_success','minimum_speed','restore_failed_height_or_time','negative_discriminant','apex_prediction','blocked_arc_raise']:
 assert branches[key]>0,key

scope='Nine recovered functions including complete 502240 transfer scan/trajectory parent. Real training static/moving geometry, collision cache, gravity and typed script lookup run unchanged. Automatic cache identity, registry lifetime and all defined cache fields are checked separately within the Wasm stack; no gameplay query substitution. Required typed configuration and valid fixed-capacity object/list storage are contracts. Training remains unplayable.'
fixture={'base':BASE,'memory':'transfer-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'pointer_globals':[index[0x6918ec+4*i] for i in range(8)]}
path=out/'transfer-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
print('x86 complete:',len(labels),dict(oracle.counts),dict(branches),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_transfer_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'branches':dict(branches),'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory']]},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
