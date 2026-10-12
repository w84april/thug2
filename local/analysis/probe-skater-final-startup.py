"""Final component factories and actual original tag/sticker initialization."""
from pathlib import Path
s=Path('local/analysis/probe-skater-startup-tail.py').read_text().split('# Complete-function behavioral cases.')[0]
exec(compile(s,'<preserved verified startup oracle>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear();prefix_hits.clear()
specs=[(0x51da80,117,'thug_tag_texture_create_draft',0,'word',True,False,False),
 (0x4ece10,128,'thug_component_d1515392_construct_draft',0,'word',True,False,True),
 (0x4ecf20,86,'thug_component_d1515392_create_draft',0,'word',True,False,False),
 (0x51d890,289,'thug_tag_texture_initialize_draft',1,'void',True,False,True)]
for row in specs:bind_new(*row)
exports.extend([[0x64c330,'thug_tag_texture_startup_methods_draft'],[0x64b6fc,'thug_component_d1515392_startup_methods_draft'],[0x649bb4,'thug_texture_dictionary_base_methods_draft'],[0x64a824,'thug_texture_dictionary_pc_methods_draft'],[0x649af0,'thug_texture_wrapper_base_methods_draft'],[0x64a770,'thug_texture_wrapper_pc_methods_draft']])
function_exports.extend([[0x51da80,'thug_tag_texture_create_draft'],[0x4ecf20,'thug_component_d1515392_create_draft']])
CONTROL,GLOG,DEVICE,DVT,TVT,FILE,IOCTRL,IOLOG,DATA0,DATA1,TEXTURES,DICT=[BASE+x for x in [0x280000,0x281000,0x285000,0x285100,0x285300,0x286000,0x288000,0x288100,0x290000,0x296000,0x300000,0x289000]]
for name,a,v in [('thug_mesh_device',0x7d69e0,DEVICE),('thug_texture_resource_registry_draft',0x7cc254,0),('thug_decal_texture_dictionary',0x700f20,DICT)]:global_default(name,a,v)
for i in range(4):glob('thug_texture_stage_bindings_draft',0x786e94+4*i,0,offset=4*i)
put(ALLOCATOR+0x110,'<I',ALLOCATOR+0x20c);oracle.scope_entries[ALLOCATOR+0x20c]=2
put(CONTROL,'<4I',0,0,512,0);put(IOCTRL,'<2I',0,1);put(DEVICE,'<I',DVT)
paths=[ROOT/'local/game-files/Game/Data/images/tags'/f'{n}.img.xbx' for n in ['cas_01','sticker']];assets=[]
for at,path in zip([DATA0,DATA1],paths):
 data=path.read_bytes();memory[at-BASE:at-BASE+len(data)]=data;assets.append({'path':str(path.relative_to(ROOT)),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
PORTS=[oracle.stop+0x900+i*0x10 for i in range(7)];CREATE,LOCK,UNLOCK,LEVELS,DESC,RELEASE,BIND=PORTS;OPS={a:i+1 for i,a in enumerate(PORTS)}
def gpu(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);arg=lambda i:oracle.word(sp+4+i*4);op=OPS[at];index=oracle.word(CONTROL);assert index<200
 oracle.setword(CONTROL,index+1);row=[op]+[0]*14+[oracle.word(CONTEXT+8)]
 if op==1:
  args=[arg(i) for i in range(9)];n=oracle.word(CONTROL+4);assert n<6;p=TEXTURES+n*0x20000;oracle.setword(CONTROL+4,n+1);oracle.setword(p,TVT);oracle.setword(p+4,args[3]);oracle.setword(p+8,args[1]*4);oracle.setword(p+12,0)
  for level in range(4):cpu.mem_write(p+0x20+level*32,struct.pack('<8I',args[5],0,0,0,0,0,args[1]>>level,args[2]>>level))
  oracle.setword(args[7],p);row[1:11]=args+[p];argc=9;result=0
 elif op==2:
  p,level,out,rect,flags=[arg(i) for i in range(5)];assert level<4;data=p+0x100+level*0x4000;pitch=oracle.word(p+8) or oracle.word(CONTROL+8)
  oracle.setword(out,pitch);oracle.setword(out+4,data);row[1:7]=[p,level,rect,flags,pitch,data];argc=5;result=0
 elif op==3:row[1:3]=[arg(0),arg(1)];argc=2;result=0
 elif op==4:p=arg(0);result=oracle.word(p+4);row[1:3]=[p,result];argc=1
 elif op==5:
  p,level,out=[arg(i) for i in range(3)];assert level<4;desc=list(struct.unpack('<8I',cpu.mem_read(p+0x20+level*32,32)));cpu.mem_write(out,struct.pack('<8I',*desc));row[1:11]=[p,level]+desc;argc=3;result=0
 elif op==6:p=arg(0);row[1]=p;oracle.setword(p+12,oracle.word(p+12)+1);argc=1;result=0
 else:row[1:4]=[arg(0),arg(1),arg(2)];argc=3;result=0
 cpu.mem_write(GLOG+index*64,struct.pack('<16I',*row));cpu.reg_write(UC_X86_REG_EAX,result);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4+argc*4)
for a in PORTS:oracle.cpu.hook_add(UC_HOOK_CODE,gpu,begin=a,end=a)
def io_record(op,a=0,b=0,c=0,d=0):
 n=oracle.word(IOCTRL);assert n<100;oracle.setword(IOCTRL,n+1);oracle.cpu.mem_write(IOLOG+n*20,struct.pack('<5I',op,a,b,c,d))
def files(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);arg=lambda i:oracle.word(sp+4+i*4)
 if at==0x5b9e60:
  text=bytes(cpu.mem_read(arg(0),128)).split(b'\0')[0];names=[b'images/tags\\cas_01.img.xbx',b'images/tags\\sticker.img.xbx'];assert text in names,text;assert bytes(cpu.mem_read(arg(1),3))==b'rb\0';i=names.index(text);start=[DATA0,DATA1][i];length=assets[i]['bytes'];oracle.setword(FILE,start);oracle.setword(FILE+4,start+length);io_record(1,i,length);result=FILE
 elif at==0x5b9ee0:
  out,width,count,file=[arg(i) for i in range(4)];assert file==FILE;start=oracle.word(file);n=width*count;assert DATA0<=start<=start+n<=oracle.word(file+4)
  io_record(2,width,count,start,out if BASE<=out<BASE+SIZE else 0);cpu.mem_write(out,bytes(cpu.mem_read(start,n)));oracle.setword(FILE,start+n);result=count
 else:assert arg(0)==FILE;io_record(3,FILE);result=1
 cpu.reg_write(UC_X86_REG_EAX,result);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
for a in [0x5b9e60,0x5b9ee0,0x5b9ea0]:oracle.cpu.hook_add(UC_HOOK_CODE,files,begin=a,end=a)
# The allocator and other game routines still execute at the preserved boundary.
# Mark newly constructed texture wrapper identities for exact relocated snapshots.
oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:fields.add(cpu.reg_read(UC_X86_REG_ECX)),begin=0x49f200,end=0x49f200)
initial=bytes(memory);oracle.initial=initial
class FinalGraph(TailGraph):
 def __init__(self,fill=0,difficulty=1,toggle=0):
  super().__init__(fill,difficulty,toggle);self.put(DVT+0x5c,'<I',CREATE);self.put(DVT+0x104,'<I',BIND)
  for offset,callback in [(8,RELEASE),(0x34,LEVELS),(0x44,DESC),(0x4c,LOCK),(0x50,UNLOCK)]:self.put(TVT+offset,'<I',callback)
  self.put(DICT,'<5I',0x64a824,0x12345678,1,self.table([]),0xdeadbeef);fields.add(DICT)
 def run(self,calls,label,changes=None):
  stages=super().run(calls,label,changes);known={r[0] for r in exports}
  for stage in stages:
   for at,text in stage['outputs']:
    if int.from_bytes(bytes.fromhex(text),'little') in known:fields.add(at)
  return stages
port=folder/'skater-final-startup-ports.c';output=folder/'skater-final-startup-ports.wasm';clang=ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang';cmd=[str(clang),'--target=wasm32-unknown-unknown','-O2','-nostdlib','-Wl,--no-entry,--export-all,--import-memory',str(port),'-o',str(output)];subprocess.run(cmd,check=True);output.with_suffix('.build.json').write_text(json.dumps({'command':cmd,'source_sha256':hashlib.sha256(port.read_bytes()).hexdigest(),'sha256':hashlib.sha256(output.read_bytes()).hexdigest()},indent=2)+'\n')
native=[{'module':'skater-final-startup-ports.wasm','export':'fixture_tag_'+name,'slots':[slot]} for name,slot in [('create',DVT+0x5c),('lock',TVT+0x4c),('unlock',TVT+0x50),('levels',TVT+0x34),('description',TVT+0x44),('release',TVT+8),('bind',DVT+0x104)]]+[{'module':'skater-final-startup-ports.wasm','export':'fixture_tag_'+name,'slots':[],'original':at} for name,at in [('open',0x5b9e60),('read',0x5b9ee0),('close',0x5b9ea0)]]
extra={**extra,'memory_fixture':'skater-walk-memory.wasm','pointer_initializers':[['thug_scene_file_open_draft',0x5b9e60],['thug_scene_file_read_draft',0x5b9ee0],['thug_scene_file_close_draft',0x5b9ea0]],'callback_counter':'startup_diagnostic_callbacks','native_callbacks':native+[{'module':'skater-startup-tail-diagnostic-fixture.wasm','export':'fixture_startup_print','slots':[DIAG+4]}]}
# Final complete startup cases.
for fill,alignment in itertools.product([0,0xa5,255],[0,1,4]):
 g=FinalGraph(fill);fields.add(P+alignment);g.run([call(0x4ece10,P+alignment)]*2,f'sentinel constructor/{fill}/{alignment}')
for factory in [0x51da80,0x4ecf20]:
 for count in [1,2,4]:
  g=FinalGraph();g.run([call(factory)]*count,f'factory/{factory:x}/{count}')
 g=FinalGraph();g.put(CONTEXT+32,'<I',1);g.run([call(factory)]*2,f'factory failure/{factory:x}')
g=FinalGraph();g.put(CONTEXT+32,'<I',1);g.run([call(0x4ece10,P)],'null sentinel allocation')
for value in [None,0,1,2,255,0x7fffffff,0x80000000,0xffffffff]:
 for fill in [0,0xa5,255]:
  g=FinalGraph(fill);params=g.structure([] if value is None else [(0xa2b033fd,1,value)]);g.run([call(0x51d890,P,[params])],f'actual tag/sticker initialize/{value}/{fill}')
  for offset,texture,w in [(0x1c,TEXTURES+0x20000,128),(0x20,TEXTURES+0x60000,64)]:
   wrapper=oracle.word(P+offset);resource=oracle.word(wrapper+16);assert oracle.word(resource+16)==texture
   a=bytes(oracle.cpu.mem_read(texture+0x100,w*w*4));b=bytes(oracle.cpu.mem_read(texture-0x20000+0x100,w*w*4));assert a==b
scope='Final tag/sticker factory and initializer plus d1515392 sentinel constructor/factory. Actual original images load through the maintained file/palette/swizzle code, clone pitched GPU resources, delete temporary wrappers and unlink their registry entries. Signed/absent heap-index formatting, compression heap selection/restore, original CRC extensions, retained poisoned bytes and normal allocation failures compare. Frame/finalization/commands remain unverified; no full skater or playable-level credit in this suite.'
finish('skater-final-startup',scope,{'0x4ece50':'initialized allocator contract excludes cold process bootstrap'},extra)
f=folder/'skater-final-startup-original.json';j=json.loads(f.read_text());j['assets']=assets;f.write_text(json.dumps(j,indent=2)+'\n')
