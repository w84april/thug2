"""Original image conversion, shared particle dictionary and resident-file loading."""
from pathlib import Path
source=Path('local/analysis/probe-texture-buffer.py').read_text().split('for fill in [0,0xa5,0xff]:')[0]
source=source.replace('count*0x1000','count*0x8000')
exec(compile(source,'<preserved texture comparison setup>','exec'))
functions.clear();hits.clear();code.clear();oracle.counts.clear()
specs=[(0x5f45e0,51,'image_palette_expand',4,'void',False,False),(0x5f5af0,206,'image_unswizzle',5,'word',False,False),
 (0x4e0790,757,'image_file_load',1,'word',True,False),(0x4c7f00,127,'texture_image_load',3,'byte',True,True),
 (0x49f220,223,'texture_image_name_load',3,'void',True,True),(0x4c9b00,147,'texture_image_create',3,'word',True,True),
 (0x4c7360,112,'particle_dictionary_create',1,'word',True,False),(0x640c60,79,'particle_dictionary_initialize',0,'void',True,False),
 (0x49f560,95,'texture_dictionary_find_name',1,'word',False,True),(0x49f9b0,100,'texture_dictionary_load_image',4,'word',True,True),
 (0x5aa7b0,115,'script_load_particle_texture',2,'byte',True,False)]
functions.update({hex(a):{'name':'thug_'+n+'_draft','this':this,'result':result,'cleanup':argc*4 if this else 0,'memory':heap} for a,size,n,argc,result,heap,this in specs})
code.update({a:list(md.disasm(pe.get_data(a-0x400000,n),a)) for a,n,*_ in specs})
for a,n,*_ in specs:oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:hits.update([at]),begin=a,end=a+n-1)
# Canonical table identities now bind the recovered image-load slot.
FILE,NAME,IOCTRL,IOLOG=BASE+0x1000,BASE+0x2000,BASE+0x32000,BASE+0x33000
OUT,PALETTE,INDICES=BASE+0x4000,BASE+0x3000,BASE+0x7000
put(IOCTRL,'<2I',0,1);put(FILE,'<2I',INPUT,INPUT)
memory[0x2c000:0x30000]=bytes(0x4000)
initial=bytes(memory);oracle.initial=initial
# Security-cookie checking and original sprintf execute, with only initialized
# C-locale TLS supplied by the same comparison conventions as earlier probes.
globals_.append(['thug_decal_texture_dictionary',0x700f20,4]);defaults.append(P)
globals_.append(['thug_script_symbol_buckets',0x6f3624,4]);defaults.append(BASE+0x2c000)
from collections import Counter
io_calls=Counter()
def finish_port(result):
 sp=oracle.cpu.reg_read(UC_X86_REG_ESP);oracle.cpu.reg_write(UC_X86_REG_EAX,result);oracle.cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));oracle.cpu.reg_write(UC_X86_REG_ESP,sp+4)
def io_record(op,a=0,b=0,c=0,d=0):
 n=oracle.word(IOCTRL);assert n<100;oracle.setword(IOCTRL,n+1);oracle.cpu.mem_write(IOLOG+n*20,struct.pack('<5I',op,a,b,c,d));io_calls[op]+=1
def files(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);arg=lambda i:oracle.word(sp+4+i*4)
 if at==0x5b9e60:
  name,mode=arg(0),arg(1);expected=bytes(cpu.mem_read(NAME,256)).split(b'\0')[0]+b'\0'
  assert bytes(cpu.mem_read(name,len(expected)))==expected,(hex(at),bytes(cpu.mem_read(name,128)),expected)
  assert bytes(cpu.mem_read(mode,3))==b'rb\0';present=oracle.word(IOCTRL+4);oracle.setword(FILE,INPUT);io_record(1,present);finish_port(FILE if present else 0)
 elif at==0x5b9ee0:
  out,width,count,file=[arg(i) for i in range(4)];assert file==FILE;start=oracle.word(file);n=width*count;assert INPUT<=start<=start+n<=oracle.word(file+4)
  io_record(2,width,count,start,out if BASE<=out<BASE+SIZE else 0);cpu.mem_write(out,bytes(cpu.mem_read(start,n)));oracle.setword(file,start+n);finish_port(count)
 else:assert arg(0)==FILE;io_record(3,FILE);finish_port(1)
for a in [0x5b9e60,0x5b9ee0,0x5b9ea0]:oracle.cpu.hook_add(UC_HOOK_CODE,files,begin=a,end=a)
class ImageGraph(Graph):
 def file(self,data,name='images/particles/test.img.xbx',present=True):
  super().file(data);self.put(FILE,'<2I',INPUT,INPUT+len(data));self.put(IOCTRL,'<2I',0,int(present));self.text(NAME,name)
 def text(self,p,s):
  data=s.encode()+b'\0';self.data[p-BASE:p-BASE+len(data)]=data;return p
 def dictionary(self):
  t=self.table();self.put(P,'<5I',0x64a824,0x1234,1,t,0xa5a5a5a5);fields.add(P);return P
 def params(self,name,reuse=False):
  s=self.alloc(8);c=self.alloc(16);text=self.alloc(len(name)+1);self.text(text,name);self.put(s,'<2I',0,c);self.put(c,'<4I',6,0,text,0)
  if reuse:
   flag=self.alloc(16);self.put(flag,'<4I',26,0,0xd5928f25,0);self.put(c+12,'<I',flag)
  return s
# Raw color expansion includes signed-empty counts and observable aliases.
for count in [0,1,2,17,256,0xffffffff]:
 for alias in [False,True]:
  g=ImageGraph();g.put(INDICES,'<256B',*range(256));g.put(PALETTE,'<256I',*[((i*0x1020304)^0x7f812345)&0xffffffff for i in range(256)])
  run(g,[call(0x5f45e0,args=[PALETTE+4 if alias else OUT,INDICES,count,PALETTE])],f'palette/{count}/{alias}')
for w,h in [(0,1),(1,0),(1,1),(2,1),(1,8),(8,2),(2,8),(4,4),(32,32)]:
 for bpp in [0,1,2,3,4,5,8]:
  g=ImageGraph();size=w*h*bpp;assert size<0x6000;g.data[INPUT-BASE:INPUT-BASE+size]=bytes((i*37+19)&255 for i in range(size))
  run(g,[call(0x5f5af0,args=[OUT,INPUT,w,h,bpp])],f'unswizzle/{w}/{h}/{bpp}')
for w,h,bpp,offset in [(4,4,1,0),(2,2,4,0),(4,2,5,4),(2,4,3,-4)]:
 g=ImageGraph();run(g,[call(0x5f5af0,args=[INPUT+offset,INPUT,w,h,bpp])],f'unswizzle-alias/{w}/{h}/{bpp}/{offset}')
def image_bytes(w,h,kind,logical=None):
 logical=logical or (w,h);depth={0:32,2:16,0x13:8}.get(kind,kind);palette=kind==0x13 or kind not in [0,2] and kind<16
 n=(logical[0]*logical[1]*(depth>>3)+3)&~3
 header=struct.pack('<8I',2,8,w,h,kind,0,logical[0]|logical[1]<<16,1024 if palette else 0)
 colors=struct.pack('<256I',*[(i*0x1020304)&0xffffffff for i in range(256)]) if palette else b''
 return header+colors+bytes((i*37+19)&255 for i in range(n))
for w,h in [(1,1),(4,4),(8,2),(3,5),(0,4),(4,0)]:
 for kind in [0,2,0x13,8,16,24,32]:
  g=ImageGraph();data=image_bytes(w,h,kind);g.file(data);run(g,[call(0x4e0790,args=[NAME])],f'image/{w}/{h}/{kind}')
g=ImageGraph();g.file(b'',present=False);run(g,[call(0x4e0790,args=[NAME])],'file-missing')
flame=ROOT/'local/game-files/Game/Data/images/particles/apm_flameQUAD_01.img.xbx';flame_bytes=flame.read_bytes();assert hashlib.sha256(flame_bytes).hexdigest()=='95fc1e0fadf8bde5012ad18fabd8056953a858a8a9afee65662523003b36f2bf'
for mode in ['file','wrapper','name','create','dictionary','native','native-reuse']:
 g=ImageGraph();g.file(flame_bytes,'images/particles/apm_flameQUAD_01.img.xbx');g.dictionary()
 text=g.alloc(128);g.text(text,'particles/apm_flameQUAD_01');g.put(P+64,'<I',0x64a770);fields.add(P+64)
 if mode=='file':calls=[call(0x4e0790,args=[NAME])]
 elif mode=='wrapper':g.text(text,'images/particles/apm_flameQUAD_01');calls=[call(0x4c7f00,P+64,[text,0,0])]
 elif mode=='name':calls=[call(0x49f220,P+64,[text,1,1])]
 elif mode=='create':calls=[call(0x4c9b00,P,[text,1,1])]
 elif mode=='dictionary':calls=[call(0x49f9b0,P,[text,1,1,0]),call(0x49f560,P,[text])]
 else:s=g.params('particles/apm_flameQUAD_01',mode=='native-reuse');calls=[call(0x5aa7b0,args=[s,0])]*2
 run(g,calls,'actual-flame/'+mode)
 pixels=bytes(oracle.cpu.mem_read(TEXTURES+0x100,4096));assets.append({'mode':mode,'path':str(flame.relative_to(ROOT)),'sha256':hashlib.sha256(flame_bytes).hexdigest(),'rgba_sha256':hashlib.sha256(pixels).hexdigest(),'gpu_calls':oracle.word(CONTROL),'file_calls':oracle.word(IOCTRL)})
g=ImageGraph();g.dictionary();params=g.params('');run(g,[call(0x5aa7b0,args=[params,0])],'native-empty')
g=ImageGraph();g.dictionary();g.file(b'','images/missing.img.xbx',False);params=g.params('missing');run(g,[call(0x5aa7b0,args=[params,0])]*2,'native-missing-file-still-caches-wrapper')
# Filename handling reaches the real parser; failed file opens remain observable.
for text,prefix,path in [('thing',0,'thing'),('../thing',1,'thing'),('..\\thing',1,'images/..\\thing'),('folder/name',256,'folder/name'),('folder\\name',255,'images/folder\\name'),('',0,''),('.',1,'images/.'),('..',1,'images/..')]:
 g=ImageGraph();g.file(b'',path+'.img.xbx',False);name=g.alloc(128);g.text(name,text);g.put(P,'<I',0x64a770);fields.add(P)
 run(g,[call(0x49f220,P,[name,prefix,0xabcdef12])],f'filename/{text}/{prefix}')
for key in [0,0xffffffff,0x12345678]:
 g=ImageGraph();run(g,[call(0x4c7360,args=[key])],f'dictionary-create/{key}')
for existing in [False,True]:
 for refcount in [1,0xffff]:
  g=ImageGraph();cache=g.table([(0xa9db601e,P)] if existing else []);g.put(P+8,'<I',0xa5a50000|refcount)
  run(g,[call(0x640c60)]*2,f'dictionary-initialize/{existing}/{refcount}',cache=cache)
# Null dictionary table and basename delimiter variants, real table lookup.
for text in ['','name','x/name','x\\name','x/','x\\','x/name.ext']:
 g=ImageGraph();g.dictionary();name=g.alloc(128);g.text(name,text);run(g,[call(0x49f560,P,[name])],f'name-missing/{text}')
g=ImageGraph();g.put(P+12,'<I',0);g.text(NAME,'name');run(g,[call(0x49f560,P,[NAME])],'name-no-table')
missing={hex(a):[hex(i.address) for i in c if not hits[i.address]] for a,c in code.items()};print('MISSING',json.dumps(missing),flush=True)
excluded={**{hex(a):'initialized allocator; cold process bootstrap excluded' for a in [0x4e0821,0x4e0980,0x4c9b23,0x4c737f]},**{hex(a):'successful internal allocation contract; failure branch retained but unverified' for a in [0x4e0860,0x4c9b61,0x4c73bf,0x4c73c3,0x4c73c5,0x4c73cc,0x4c73cf]}}
assert {a for group in missing.values() for a in group}==set(excluded)
coverage={hex(a):{'total':len(c),'covered':sum(bool(hits[i.address]) for i in c),'missing':missing[hex(a)],'excluded':{s:excluded[s] for s in missing[hex(a)]}} for a,c in code.items()}
clang=ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang';port=folder/'particle-image-ports.c';output=folder/'particle-image-ports.wasm'
cmd=[str(clang),'--target=wasm32-unknown-unknown','-O2','-nostdlib','-Wl,--no-entry,--export-all,--import-memory',str(port),'-o',str(output)];subprocess.run(cmd,check=True)
output.with_suffix('.build.json').write_text(json.dumps({'command':cmd,'source_sha256':hashlib.sha256(port.read_bytes()).hexdigest(),'sha256':hashlib.sha256(output.read_bytes()).hexdigest()},indent=2)+'\n')
scope='Original image swizzle conversion, indexed color expansion, filename/dictionary wrappers and shared particle dictionary creation with explicit bounded file/GPU/heap ports. Actual1120-byte training flame image loads through file, wrapper, dictionary and native paths; uploaded4096-byte RGBA output compares. Successful initialized allocations and GPU calls, valid complete bounded files and paths are the contract. GPU storage records exact bytes and is not a renderer. No completed effect script, frame or playable game.'
fixture={'base':BASE,'memory':'particle-image-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'particle-image-ports.wasm','memory_exports':['fixture_texture_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'pointer_fields':sorted(fields),'pointer_exports':exports,'pointer_initializers':[['thug_scene_file_open_draft',0x5b9e60],['thug_scene_file_read_draft',0x5b9ee0],['thug_scene_file_close_draft',0x5b9ea0]],'native_callbacks':[{'module':'particle-image-ports.wasm','export':'fixture_texture_'+name,'slots':slots} for name,slots in [('create',[DVT+0x5c]),('lock',[TVT+0x4c]),('unlock',[TVT+0x50])]]+[{'module':'particle-image-ports.wasm','export':'fixture_image_'+name,'slots':[],'original':at} for name,at in [('open',0x5b9e60),('read',0x5b9ee0),('close',0x5b9ea0)]],'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'particle-image-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(oracle.counts.values()),'instruction_coverage':coverage,'assets':assets,'gpu_calls':dict(gpu_counts),'file_calls':dict(io_calls),'scope':scope,'playable':False}
(folder/'particle-image-original.json').write_text(json.dumps(report,indent=2)+'\n');print('SAVED',len(labels),report['calls'],flush=True)
