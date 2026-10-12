"""Actual PC texture clone/destruction in isolated original instructions."""
from pathlib import Path
from unicorn import Uc
from script_heap_oracle import ScriptHeapOracle
old_add=Uc.hook_add;captured=[]
def capture(self,kind,callback,*args,**kwargs):
 h=old_add(self,kind,callback,*args,**kwargs)
 if getattr(callback,'__name__','')=='gpu':captured.append((self,h))
 return h
old_heap=ScriptHeapOracle.heap
def tag_heap(self,cpu,address,size,user):
 requested=self.word(cpu.reg_read(UC_X86_REG_ESP)+4) if address in [0x5bbae0,0x5bafc0] else None
 if requested is not None and self.word(self.context+48):
  left=self.word(self.context+48)-1;self.setword(self.context+48,left)
  if not left:
   sp=cpu.reg_read(UC_X86_REG_ESP);route=int(address==0x5bafc0);self.record(1,requested,route,0);self.heap_events[hex(address)]+=1
   cpu.reg_write(UC_X86_REG_EAX,0);cpu.reg_write(UC_X86_REG_EIP,self.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4+(12 if route else 0));return
 old_heap(self,cpu,address,size,user)
 if requested is not None and self.word(self.context+36) and self.word(self.context+40)==requested:
  self.setword(self.word(self.context+36),self.word(self.context+44));self.setword(self.context+36,0)
ScriptHeapOracle.heap=tag_heap;Uc.hook_add=capture
try:
 source=Path('local/analysis/probe-particle-image.py').read_text().split('# Raw color expansion')[0]
 source=source.replace("source=source.replace('count*0x1000','count*0x8000')","source=source.replace('count*0x1000','count*0x8000').replace('BASE,SIZE=0x1800000,0x200000','BASE,SIZE=0x1800000,0x400000')")
 exec(compile(source,'<preserved image oracle setup>','exec'))
finally:Uc.hook_add=old_add
assert len(captured)==3
for cpu,h in captured:cpu.hook_del(h)
saved_record=oracle.record
def tag_record(kind,a,b,c):
 if kind==1 and not c:return original_record(kind,a,b,c)
 return saved_record(kind,a,b,c)
oracle.record=tag_record
functions.clear();hits.clear();code.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear();labels.clear();assets.clear();gpu_counts.clear();io_calls.clear()
put(CONTEXT+36,'<4I',0,0,0,0);put(CONTROL+8,'<2I',512,0);initial=bytes(memory);oracle.initial=initial
NEW={
0x4c7fb0:(33,'texture_image_width',0,'half',False,True),0x4c7fe0:(33,'texture_image_height',0,'half',False,True),
0x5b9e50:(3,'texture_image_false',0,'byte',False,True),0x49f3b0:(8,'texture_image_flag',0,'byte',False,True),
0x4e0500:(415,'texture_resource_copy',1,'word',False,True),0x4c8450:(592,'texture_image_copy',1,'word',True,True),
0x4c9c80:(123,'texture_dictionary_pc_clone',2,'word',True,True),0x49fbe0:(53,'texture_dictionary_clone_image',2,'word',True,True),
0x49f500:(59,'texture_dictionary_remove_image',1,'byte',True,True),0x4c8090:(19,'texture_dictionary_pc_remove',1,'byte',True,True),
0x4cae60:(33,'texture_image_delete',1,'word',True,True),0x4c9d00:(113,'texture_image_destroy',0,'void',True,True),
0x4c98b0:(153,'texture_image_collapse',0,'byte',True,True),0x4e06a0:(82,'texture_resource_destroy',0,'void',True,True),
0x4e03f0:(78,'texture_resource_unlink',0,'void',True,True),0x4da730:(47,'texture_stage_bind',3,'void',False,False),
0x49f210:(7,'texture_wrapper_base_destroy',0,'void',False,True)}
for a,(size,name,argc,result,heap,this) in NEW.items():
 functions[hex(a)]={'name':'thug_'+name+'_draft','this':this,'result':result,'cleanup':argc*4 if this else 0,'memory':heap}
 code[a]=list(md.disasm(pe.get_data(a-0x400000,size),a));oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:hits.update([at]),begin=a,end=a+size-1)
for a,n,argc,result,heap,this in [(0x49f9b0,'texture_dictionary_load_image',4,'word',True,True),(0x4e0790,'image_file_load',1,'word',True,False)]:functions[hex(a)]={'name':'thug_'+n+'_draft','this':this,'result':result,'cleanup':argc*4 if this else 0,'memory':heap}
for i in range(4):globals_.append(['thug_texture_stage_bindings_draft',0x786e94+4*i,4,4*i]);defaults.append(0)
MORE=[oracle.stop+0x340+i*0x10 for i in range(4)];LEVELS,DESC,RELEASE,BIND=MORE
OPS={CREATE:1,LOCK:2,UNLOCK:3,LEVELS:4,DESC:5,RELEASE:6,BIND:7}
def gpu_tag(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);arg=lambda i:oracle.word(sp+4+i*4);op=OPS[at];index=oracle.word(CONTROL);assert index<200
 oracle.setword(CONTROL,index+1);row=[op]+[0]*14+[oracle.word(CONTEXT+8)]
 if op==1:
  args=[arg(i) for i in range(9)];n=oracle.word(CONTROL+4);assert n<6;p=TEXTURES+n*0x20000;oracle.setword(CONTROL+4,n+1);oracle.setword(p,TVT);oracle.setword(p+4,args[3]);oracle.setword(p+8,oracle.word(CONTROL+12));oracle.setword(p+12,0)
  for level in range(4):cpu.mem_write(p+0x20+level*32,struct.pack('<8I',args[5],0,0,0,0,0,args[1]>>level,args[2]>>level))
  oracle.setword(args[7],p);row[1:11]=args+[p];argc=9;result=0
 elif op==2:
  p,level,out,rect,flags=[arg(i) for i in range(5)];assert level<4;data=p+0x100+level*0x4000;pitch=oracle.word(p+8) or oracle.word(CONTROL+8)
  oracle.setword(out,pitch);oracle.setword(out+4,data);row[1:7]=[p,level,rect,flags,pitch,data];argc=5;result=0
 elif op==3:row[1:3]=[arg(0),arg(1)];argc=2;result=0
 elif op==4:p=arg(0);result=oracle.word(p+4);row[1:3]=[p,result];argc=1
 elif op==5:
  p,level,out=[arg(i) for i in range(3)];assert level<4;d=list(struct.unpack('<8I',cpu.mem_read(p+0x20+level*32,32)));cpu.mem_write(out,struct.pack('<8I',*d));row[1:11]=[p,level]+d;argc=3;result=0
 elif op==6:p=arg(0);row[1]=p;oracle.setword(p+12,oracle.word(p+12)+1);argc=1;result=0
 else:row[1:4]=[arg(0),arg(1),arg(2)];argc=3;result=0
 cpu.mem_write(GLOG+index*64,struct.pack('<16I',*row));gpu_counts[op]+=1
 cpu.reg_write(UC_X86_REG_EAX,result);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4+argc*4)
for at in OPS:oracle.cpu.hook_add(UC_HOOK_CODE,gpu_tag,begin=at,end=at)
base_run=run
def run(*args,**kwargs):
 result=base_run(*args,**kwargs)
 if len(labels)%40==0:print('Texture cases',len(labels),flush=True)
 return result
SRC_TEXTURE=TEXTURES+6*0x20000
class TagGraph(ImageGraph):
 def __init__(self,fill=0xa5):
  super().__init__();self.data[P-BASE:P-BASE+0x1000]=bytes([fill])*0x1000
  self.put(TVT+8,'<I',RELEASE);self.put(TVT+0x34,'<I',LEVELS);self.put(TVT+0x44,'<I',DESC);self.put(DVT+0x104,'<I',BIND)
 def texture(self,p=SRC_TEXTURE,w=8,h=5,mips=2,format_=0x15,pitch=97):
  self.put(p,'<4I',TVT,mips,pitch,0)
  for level in range(4):
   self.put(p+0x20+level*32,'<8I',format_,1,2,3,4,5,w>>level,h>>level)
   start=p+0x100+level*0x4000;self.data[start-BASE:start-BASE+0x3000]=bytes((i*37+level*17+19)&255 for i in range(0x3000))
  return p
 def resource(self,p=None,w=8,h=5,mips=2,format_=0x15,texture=None):
  p=p or self.alloc(32);t=texture if texture is not None else self.texture(w=w,h=h,mips=mips,format_=format_)
  self.put(p,'<8I',0x12345678,8|5<<16,w|h<<16,mips|32<<8,t,0xabcdef12,0,0x76543210);return p
 def wrapper(self,p=P+64,flags=0,**kwargs):
  r=self.resource(**kwargs);pack=r
  if flags&1:
   pack=self.alloc(16);b=self.alloc(512);c=self.alloc(512);extra=self.resource(texture=self.texture(SRC_TEXTURE+0x20000,w=3,h=4,mips=1))
   self.put(pack,'<4I',r,b,c,extra);self.data[b-BASE:b-BASE+512]=bytes(range(256))*2;self.data[c-BASE:c-BASE+512]=bytes(range(255,-1,-1))*2
  self.put(p,'<5I',0x64a770,0x34567890,flags,0xabcdef19,pack);fields.add(p);return p
 def chain(self,values):
  nodes=[self.alloc(12) for _ in values]
  for i,(n,val) in enumerate(zip(nodes,values)):self.put(n,'<3I',val,nodes[i-1] if i else 0,nodes[i+1] if i+1<len(nodes) else 0)
  return nodes[0] if nodes else 0
# Width/height, low-word returns and original PC false flag.
for flags in [0,1,2,0xffffffff]:
 for dimensions in [(0,0),(1,65535),(65535,1),(0x1234,0xabcd)]:
  g=TagGraph();s=g.wrapper(flags=flags,w=dimensions[0],h=dimensions[1]);run(g,[call(0x4c7fb0,s),call(0x4c7fe0,s),call(0x5b9e50,s),call(0x49f3b0,s)],f'dimensions/{flags}/{dimensions}')
for flags in [0,1]:
 g=TagGraph();g.put(P,'<5I',0x64a770,0,flags,0,0);fields.add(P);run(g,[call(0x4c7fb0,P),call(0x4c7fe0,P)],f'null dimensions/{flags}')
# Real mip/format branches, unequal pitches, zero row and retained poisoned fields.
for fmt in [0x15,0x31545844,0x35545844,0x29]:
 for w,h,mips in [(0,0,0),(0,3,1),(3,0,1),(1,1,1),(8,5,2),(7,7,3)]:
  for fill in [0,0xa5,255]:
   g=TagGraph(fill);r=g.resource(w=w,h=h,mips=mips,format_=fmt);run(g,[call(0x4e0500,P,[r])],f'resource copy/{fmt:x}/{w}/{h}/{mips}/{fill}')
for flags in [0,1,0x10000,0x10001]:
 for mask in range(4):
  g=TagGraph();s=g.wrapper(flags=flags,w=3,h=4,mips=2)
  if flags&1:
   pack=g.word(s+16)
   if not mask&1:g.put(pack+4,'<I',0)
   if not mask&2:g.put(pack+12,'<I',0)
  run(g,[call(0x4c8450,P,[s])],f'wrapper copy/{flags}/{mask}')
# The allocator can observe and mutate live ownership storage. This reaches the
# original destination+8 branch rather than silently replacing it with source+8.
g=TagGraph();s=g.wrapper(flags=1,w=3,h=4,mips=1);g.put(CONTEXT+36,'<3I',HEAP+48+8,48,1);run(g,[call(0x4c8450,P,[s])],'indirect destination+8 mutation')
for flags in [0,1,0x10000,0x10001]:
 for key in [0,1,0xffffffff,0x12345678]:
  g=TagGraph();dictionary=g.dictionary();s=g.wrapper(flags=flags,w=3,h=4,mips=1)
  run(g,[call(0x49fbe0,dictionary,[key,s])],f'PC dictionary clone/{flags}/{key:x}')
# Resource registry positions, release ordering and every live texture binding.
for shape in ['empty','absent','head','middle','tail','only']:
 for secondary in [False,True]:
  for bindingmask in [0,1,5,15]:
   g=TagGraph();r=g.resource(mips=1);g.put(r+24,'<I',g.texture(SRC_TEXTURE+0x20000) if secondary else 0)
   values={'empty':[],'absent':[P+256,P+512],'head':[r,P+256],'middle':[P+256,r,P+512],'tail':[P+256,r],'only':[r]}[shape];registry=g.chain(values)
   changes={len(globals_)-4+i:SRC_TEXTURE if bindingmask&(1<<i) else 0 for i in range(4)}
   # run retains its original typed global mapping; provide registry then patch
   # the four stage defaults for this case only.
   saved=defaults[-4:];defaults[-4:]=[changes[len(globals_)-4+i] for i in range(4)]
   try:run(g,[call(0x4e06a0,r)],f'resource destroy/{shape}/{secondary}/{bindingmask}',registry=registry)
   finally:defaults[-4:]=saved
for mask in range(8):
 g=TagGraph();s=g.wrapper(flags=1,w=3,h=4,mips=1);pack=g.word(s+16)
 for i,o in enumerate([4,8,12]):
  if not mask&(1<<i):g.put(pack+o,'<I',0)
 run(g,[call(0x4c98b0,s)],f'indirect collapse/{mask}')
for flags in [0,1,2,3,255,256,257,0xffffffff]:
 for indirect in [False,True]:
  g=TagGraph();s=g.wrapper(flags=int(indirect),w=3,h=4,mips=1);run(g,[call(0x4cae60,s,[flags])],f'delete/{flags}/{indirect}')
g=TagGraph();g.put(P+16,'<I',0);g.put(P+8,'<I',0);run(g,[call(0x4c9d00,P)],'destroy null resource')
g=TagGraph();run(g,[call(0x4c8090,P,[0])],'PC delete null')
for shape in ['head','chain','absent']:
 g=TagGraph();s=g.wrapper(w=3,h=4,mips=1);dictionary=g.dictionary();key=g.word(s+4);table=g.table([(key,s)] if shape=='head' else [(key^4,P+512),(key,s)] if shape=='chain' else [(key^4,P+512)])
 g.put(dictionary+12,'<I',table);run(g,[call(0x49f500,dictionary,[s])],f'dictionary remove/{shape}')
# Original tag/sticker asset bytes use the original palette/swizzle pipeline.
for name,w in [('cas_01',128),('sticker',64)]:
 path=ROOT/'local/game-files/Game/Data/images/tags'/f'{name}.img.xbx';data=path.read_bytes()
 g=TagGraph();g.put(CONTROL+12,'<I',w*4);g.file(data,'images/tags\\'+name+'.img.xbx');dictionary=g.dictionary();text=g.alloc(128);g.text(text,'tags\\'+name)
 run(g,[call(0x49f9b0,dictionary,[text,1,1,1]),call(0x49fbe0,dictionary,[0x11223344,HEAP]),call(0x49f500,dictionary,[HEAP])],f'actual tag asset/{name}')
 copied=bytes(oracle.cpu.mem_read(TEXTURES+0x20000+0x100,w*w*4));original=bytes(oracle.cpu.mem_read(TEXTURES+0x100,w*w*4));assert copied==original
 assets.append({'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'rgba_bytes':len(copied),'rgba_sha256':hashlib.sha256(copied).hexdigest(),'copy_equals_original':True})
# Shared base dictionary virtuals execute their original false/null bodies.
g=TagGraph();dictionary=g.dictionary();s=g.wrapper(w=3,h=4,mips=1);g.put(dictionary,'<I',0x649bb4)
run(g,[call(0x49fbe0,dictionary,[0x12345678,s]),call(0x49f500,dictionary,[s])],'base dictionary false/null virtuals')
# Explicit top-level leaf calls retain their own ABI/register verification.
g=TagGraph();s=g.wrapper(w=3,h=4,mips=1);dictionary=g.dictionary();run(g,[call(0x4c9c80,dictionary,[0x12345678,s])],'PC clone direct ABI')
g=TagGraph();r=g.resource();registry=g.chain([P+256,r,P+512]);run(g,[call(0x4e03f0,r)],'unlink direct ABI',registry=registry)
g=TagGraph();run(g,[call(0x4da730,args=[i,0,0]) for i in range(4)]+[call(0x4da730,args=[0,SRC_TEXTURE,0])]*2,'binding direct and cached ABI')
g=TagGraph();run(g,[call(0x49f210,P)]*2,'wrapper base destruction ABI')
# Valid copy constructor allocation failures, including optional secondary copy.
for flags,left in [(0,1),(1,4)]:
 g=TagGraph();s=g.wrapper(flags=flags,w=3,h=4,mips=1);g.put(CONTEXT+48,'<I',left);run(g,[call(0x4c8450,P,[s])],f'copy nullable allocation/{flags}/{left}')
g=TagGraph();pack=g.alloc(16);g.put(pack,'<4I',0,0,0,0);g.put(P,'<5I',0x64a770,0,0,0,pack);fields.add(P);run(g,[call(0x4c98b0,P)],'collapse direct flag branch')
missing={hex(a):[hex(i.address) for i in c if not hits[i.address]] for a,c in code.items()};print('MISSING',json.dumps(missing),flush=True)
excluded={hex(a):'initialized allocator contract excludes cold process bootstrap' for a in [0x4c84b5,0x4c852a,0x4c856f,0x4c85d5,0x4c8636,0x4c863b,0x4c9c9f]}
excluded.update({hex(a):'original unchecked outer/pack allocation failure faults; valid storage contract' for a in [0x4c8553,0x4c9cd2]})
excluded.update({hex(a):'nine-byte unreachable alignment skipped by unconditional4e06c5 jump to4e06d0' for a in [0x4e06c7,0x4e06ce]})
assert {a for group in missing.values() for a in group}==set(excluded)
coverage={hex(a):{'total':len(c),'covered':sum(bool(hits[i.address]) for i in c),'missing':missing[hex(a)],'excluded':{a:excluded[a] for a in missing[hex(a)]}} for a,c in code.items()}
clang=ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang';port=folder/'skater-tag-texture-ports.c';output=folder/'skater-tag-texture-ports.wasm';cmd=[str(clang),'--target=wasm32-unknown-unknown','-O2','-nostdlib','-Wl,--no-entry,--export-all,--import-memory',str(port),'-o',str(output)];subprocess.run(cmd,check=True);output.with_suffix('.build.json').write_text(json.dumps({'command':cmd,'source_sha256':hashlib.sha256(port.read_bytes()).hexdigest(),'sha256':hashlib.sha256(output.read_bytes()).hexdigest()},indent=2)+'\n')
scope='Actual PC texture dimensions, false flag, resource/wrapper/dictionary cloning, mip descriptions and pitched forward copies, registry unlink, release/binding cleanup, indirect ownership and dictionary deletion. Bounded valid storage, initialized successful allocation/GPU operations; Shared base false/null virtuals are also verified. Cold heap bootstrap and unchecked outer/pack allocation faults are outside the valid-storage scope; nullable primary/secondary copy allocation is verified. Original tag/sticker files load and cloned RGBA bytes equal original uploads. Platform GPU storage is not rendering; no full skater/startup/playability credit.'
callbacks=[{'module':'skater-tag-texture-ports.wasm','export':'fixture_tag_'+n,'slots':[at]} for n,at in [('create',DVT+0x5c),('lock',TVT+0x4c),('unlock',TVT+0x50),('levels',TVT+0x34),('description',TVT+0x44),('release',TVT+8),('bind',DVT+0x104)]]+[{'module':'skater-tag-texture-ports.wasm','export':'fixture_tag_'+n,'slots':[],'original':at} for n,at in [('open',0x5b9e60),('read',0x5b9ee0),('close',0x5b9ea0)]]
fixture={'base':BASE,'memory':'skater-tag-texture-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'skater-tag-texture-ports.wasm','memory_exports':['fixture_tag_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'pointer_fields':sorted(fields),'pointer_exports':exports,'pointer_initializers':[['thug_scene_file_open_draft',0x5b9e60],['thug_scene_file_read_draft',0x5b9ee0],['thug_scene_file_close_draft',0x5b9ea0]],'native_callbacks':callbacks,'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'skater-tag-texture-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(oracle.counts.values()),'counts':dict(oracle.counts),'instruction_coverage':coverage,'assets':assets,'gpu_calls':dict(gpu_counts),'file_calls':dict(io_calls),'scope':scope,'playable':False};(folder/'skater-tag-texture-original.json').write_text(json.dumps(report,indent=2)+'\n');print('SAVED',len(labels),report['calls'],flush=True)
