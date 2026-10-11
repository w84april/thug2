"""Original low-speed side collision correction; no gameplay callees are replaced."""
import hashlib,json,math,random,struct,subprocess
from collections import Counter
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EIP,UC_X86_REG_ESP,UC_X86_REG_FPCW,UC_X86_REG_MXCSR
from specimen import ROOT,SHA256,load
out=ROOT/'local/validation/collision';report_path=out.parent/'low-speed.json';report_path.unlink(missing_ok=True)
old=json.loads((out/'skater-fixtures.json').read_text());a=old['addresses'].copy();base=old['loader']
a.update(vector_block=0x2002100,button=0x2002200,input=0x1620000)
DATA,GRID,SCENE,SCENES,RUNTIME,NODES,OWNERS,REFS=[a[k] for k in ('data','grid','scene','scenes','runtime','nodes','owners','refs')]
BODY,PHYSICS,SYMBOLS,HEAP,VECTORS,BUTTON,INPUT=[a[k] for k in ('body','physics','symbols','heap','vector_block','button','input')]
STACK,STOP,QUERY_STATE,STAMP=0x3000000,0x3f00000,0x691968,0x693998
pe=load();cpu=Uc(UC_ARCH_X86,UC_MODE_32)
cpu.mem_map(0x400000,(pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095);cpu.mem_write(0x400000,pe.get_memory_mapped_image())
for at,size in [(0,4096),(DATA,0xa00000),(0x2000000,0x600000),(STACK,0x20000),(STOP,4096)]:cpu.mem_map(at,size)
rng=random.Random(0x503b30);events=Counter();totals=Counter()
fixture={'addresses':a,'loader':base,'vectors':[],'buttons':[],'world':[]}
def raw(at,n):return bytes(cpu.mem_read(at,n))
def put(at,fmt,*values):cpu.mem_write(at,struct.pack(fmt,*values))
def floats(v):return struct.pack('<'+'f'*len(v),*v)
def bits(v):return struct.unpack('<I',struct.pack('<f',v))[0]
def call(fn,this,args=(),cleanup=0):
 sp=STACK+0x18000;put(sp,'<'+'I'*(len(args)+1),STOP,*args)
 cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,this)
 cpu.reg_write(UC_X86_REG_FPCW,0x7f);cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
 cpu.emu_start(fn,STOP,count=5000000)
 assert cpu.reg_read(UC_X86_REG_EIP)==STOP and cpu.reg_read(UC_X86_REG_ESP)==sp+4+cleanup,hex(fn)
 assert cpu.reg_read(UC_X86_REG_FPCW)==0x7f and raw(0,4)==bytes(4)
 return cpu.reg_read(UC_X86_REG_EAX)
def timer(config):
 counter,fps,origin,scale,offset=config
 put(0x7d1ec8,'<2I',counter,0xabadcafe);put(0x684fd0,'<I',fps);put(0x696d64,'<I',origin);put(0x67d7c0,'<I',scale);put(0x696d60,'<I',offset)
special=[[0,0,0,1],[1,0,0,7],[0,1,0,1],[0,0,1,0],[1e-30,2e-30,-1e-30,1],
 [1e30,2e30,-1e30,1],[float('nan'),1,0,1],[float('inf'),0,1,1]]
for i in range(512):
 v=special[i%8] if i<64 else [rng.uniform(-100,100) for _ in range(4)]
 n=special[(i//8)%8] if i<64 else [rng.uniform(-1,1) for _ in range(4)]
 for offset in [-8,0,4,16]:
  block=bytearray(b'\xad'*128);struct.pack_into('<4f',block,48,*v);struct.pack_into('<4f',block,48+offset,*n)
  cpu.mem_write(VECTORS,bytes(block));assert call(0x406200,VECTORS+48,[VECTORS+48+offset],4)==VECTORS+48
  fixture['vectors'].append({'offset':offset,'input':block.hex(),'output':raw(VECTORS,128).hex()})
for i in range(1536):
 config=[rng.randrange(2**32),bits(rng.choice([.5,30,59.94,60,144,1000])),rng.randrange(2**32),bits(rng.choice([0,1,.5,1.5])),rng.randrange(2**32)];timer(config)
 b=bytes(rng.randrange(256) for _ in range(24));cpu.mem_write(BUTTON,b)
 result=call(0x46b920,BUTTON+8);assert raw(BUTTON,24)==b
 fixture['buttons'].append({'timer':config,'input':b.hex(),'result':result})
script=bytearray(0x4100)
names=[0x3eede4d3,0xbc33d268,0x435f0653,0x4b8bab12,0xbfbbd0af]
for i,name in enumerate(names):
 entry=SYMBOLS+0x4000+i*20;struct.pack_into('<I',script,(name&4095)*4,entry)
 struct.pack_into('<BBHIIII',script,0x4000+i*20,0,2,0,name,0,bits(30),0)
fixture['script_memory']=script.hex();cpu.mem_write(SYMBOLS,bytes(script));put(0x6f3624,'<I',SYMBOLS)
cpu.mem_write(DATA,(out/base['loaded']).read_bytes());cpu.mem_write(GRID,(out/base['grid']).read_bytes());heap=(out/base['heap']).read_bytes()
cpu.mem_write(SCENE,bytes(0xd4)+struct.pack('<I',GRID));put(SCENES,'<8I',0,SCENE,0,SCENES+16,0,0xffffffff,0,SCENES+16)
put(0x6fa7ec,'<I',SCENES);put(0x691984,'<I',NODES);put(0x691974,'<I',0)
cpu.mem_write(0x67c6b8,struct.pack('<2048H',*range(2048)))
for j in range(3):put(NODES+j*16,'<4I',0,RUNTIME+j*0x100,0,NODES+(j+1)*16)
put(NODES+48,'<4I',0,0xffffffff,0,NODES+48)
tail=bytearray(b'\xad'*(0x1520-0x318));struct.pack_into('<I',tail,0x150c-0x318,INPUT);fixture['physics_tail']=tail.hex()
def observe(uc,address,size,user):
 names={0x5003a0:'surface_queries',0x46b920:'button_timers',0x44ece0:'timer_reads',0x406200:'axis_projections',0x4637c0:'attachments',0x4637e0:'unlinks'}
 if address in names:events[names[address]]+=1
 elif address==0x503d30:events['first_hits']+=bool(uc.reg_read(UC_X86_REG_EAX)&255)
 elif address==0x503e59:events['second_hits']+=bool(uc.reg_read(UC_X86_REG_EAX)&255)
 elif address==0x503e5d:events['position_updates']+=1
for address in [0x5003a0,0x46b920,0x44ece0,0x406200,0x4637c0,0x4637e0,0x503d30,0x503e59,0x503e5d]:cpu.hook_add(UC_HOOK_CODE,observe,begin=address,end=address)
cpu.ctl_flush_tb()
def world(test,index,variant,extra=None):
 cpu.mem_write(HEAP,heap);cpu.mem_write(OWNERS,bytes.fromhex(old['owners']));cpu.mem_write(REFS,bytes.fromhex(old['references']));cpu.mem_write(RUNTIME,bytes.fromhex(test['actors']))
 body=bytearray(bytes.fromhex(test['body'])+b'\xad'*16);physics=bytearray(bytes.fromhex(test['physics']))
 side=struct.unpack_from('<3f',body,0x8c);forward=[-v for v in struct.unpack_from('<3f',body,0x6c)]
 up=[forward[1]*side[2]-forward[2]*side[1],forward[2]*side[0]-forward[0]*side[2],forward[0]*side[1]-forward[1]*side[0]]
 if variant in (1,2):side=[-v for v in side];forward=[-v for v in forward]
 struct.pack_into('<12f',body,0x6c,*side,0,*up,0,*forward,0)
 struct.pack_into('<4f',body,0xac,1000 if variant==4 else float('nan') if variant==5 else 0,0,0,1)
 input_=bytearray(b'\xad'*0x190);input_[0x60]=0 if variant in (1,3) else 1;input_[0x80]=128 if variant in (1,2) else 0
 config=[60,bits(60),0,bits(1),0xffffff00 if index%7==0 else 0];timer(config);now=(1000+config[-1])&0xffffffff
 age=[0,1,249,500,999,1000,0x80000001,0xffffffff][index%8]
 struct.pack_into('<I',input_,0x64,(now-age)&0xffffffff);struct.pack_into('<I',input_,0x84,(now-age-250)&0xffffffff)
 values=[50,float('nan') if variant==7 else .5,16 if index%2 else 80,[0,4,-4,20.25][index%4]]
 if variant==6:values[1]=0
 if extra is not None:
  values=extra;struct.pack_into('<4f',body,0xac,0,0,0,1)
 settings=[]
 for j,value in enumerate(values,1):
  kind=1 if isinstance(value,int) else 2;word=value&0xffffffff if kind==1 else bits(value)
  cpu.mem_write(SYMBOLS+0x4001+j*20,bytes([kind]));put(SYMBOLS+0x400c+j*20,'<I',word);settings.append([kind,word])
 cpu.mem_write(BODY,bytes(body));cpu.mem_write(PHYSICS,bytes(physics)+bytes(tail));cpu.mem_write(INPUT,bytes(input_));call(0x417760,PHYSICS+0xa8)
 if index%2:
  put(PHYSICS+0x140,'<3I',OWNERS,0,REFS);put(REFS+4,'<I',PHYSICS+0x140);put(OWNERS+4,'<I',PHYSICS+0x140)
 before=raw(PHYSICS,0x318);owners=raw(OWNERS,96);refs=raw(REFS,48)
 cpu.mem_write(QUERY_STATE,bytes.fromhex(test['initial_state']));cpu.mem_write(STAMP,bytes([test['stamp']]));cpu.mem_write(0x691910,b'\0')
 events.clear();call(0x503b30,PHYSICS)
 assert raw(PHYSICS+0x318,len(tail))==tail and raw(INPUT,len(input_))==input_ and raw(BODY+0xbc,16)==b'\xad'*16
 assert raw(BODY,0x4c)==body[:0x4c] and raw(BODY+0x5c,len(body)-0x5c)==body[0x5c:]
 fixture['world'].append({'object':test['object'],'variant':variant,'actors':test['actors'],'actors_after':raw(RUNTIME,0x300).hex(),
  'body':body.hex(),'body_after':raw(BODY,len(body)).hex(),'physics':before.hex(),'physics_after':raw(PHYSICS,0x318).hex(),
  'input':input_.hex(),'owners':owners.hex(),'owners_after':raw(OWNERS,96).hex(),'refs':refs.hex(),'refs_after':raw(REFS,48).hex(),
  'settings':settings,'timer':config,'initial_state':test['initial_state'],'state':raw(QUERY_STATE,12).hex(),'stamp':test['stamp'],'final_stamp':raw(STAMP,1)[0],
  'stamps':bytes(raw(base['instances']+i*24+10,1)[0] for i in range(base['count'])).hex(),'events':dict(events)})
 totals['updates']+=1;totals.update(events)
for index,test in enumerate(old['world'][::3]):
 for variant in range(8):world(test,index,variant)
 if index%100==0:print(index,'training objects',dict(totals),flush=True)
for index in range(192):
 values=[rng.choice([0.,float('nan'),float('inf')]),rng.choice([1e-40,1e-20,1e20,-.5,float('inf')]),
  rng.choice([2**24+1,2**31-1,-2**31+1,1e-30,-1e30]),rng.choice([0,1e-30,100,-100])]
 world(old['world'][(index%605)*3],index,0,values)
assert totals['first_hits'] and totals['second_hits'] and totals['position_updates'] and totals['attachments']
fixture['totals']=dict(totals);path=out/'low-speed-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
subprocess.run(['node',str(ROOT/'tools/verify_low_speed_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(totals),'vector_cases':len(fixture['vectors']),'button_cases':len(fixture['buttons']),
 'x87_control_word':'0x007f','mxcsr':'0x1f80','scope':'Complete low-speed collision correction using original training collision, input timestamps and numeric parameter callees. Constructed states; no full skating loop.',
 'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
 'artifact_hashes':{str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest()},
 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(totals))
