"""Original looping sound lifecycle; reuse complete voice helpers and COM boundary."""
from pathlib import Path
source=Path('local/analysis/probe-skater-walk.py').read_text().split('# Real original CRT')[0]
exec(compile(source,'<preserved isolated component oracle>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x47b4e0,57,'thug_sound_stop_draft',1,'byte',False,False,True),
 (0x5138e0,135,'thug_looping_sound_construct_draft',0,'word',False,False,True),
 (0x513ad0,89,'thug_looping_sound_create_draft',0,'word',True,False,False),
 (0x513b30,113,'thug_looping_sound_destroy_draft',0,'void',False,False,True),
 (0x513fa0,33,'thug_looping_sound_delete_draft',1,'word',True,False,True),
 (0x513880,40,'thug_looping_sound_initialize_draft',1,'void',False,False,True),
 (0x513970,21,'thug_looping_sound_bind_draft',0,'void',False,False,True),
 (0x513f60,61,'thug_looping_sound_suspend_draft',1,'void',False,False,True)]
for row in specs:bind_new(*row)
for row in [(0x47ad80,'thug_sound_find_voice_draft',1,'word',False,False,True),
 (0x47c7a0,'thug_audio_stop_slot_draft',1,'void',False,False,False),
 (0x45e510,'thug_composite_initialize_draft',0,'word',False,False,True),
 (0x45ee20,'thug_composite_add_parameters_draft',2,'void',True,True,True),
 (0x45db30,'thug_composite_finalize_draft',0,'void',True,True,True),
 (0x45d890,'thug_composite_destroy_draft',0,'void',True,True,True)]:bind(*row)
exports.extend([[0x64bf38,'thug_looping_sound_pending_methods_draft'],[0x7d6a38,'thug_sound_device']]);function_exports.append([0x513ad0,'thug_looping_sound_create_draft'])
STATE,LIVE,VT,CFG=BASE+0x222000,BASE+0x221000,BASE+0x221100,BASE+0x221800;STOPNATIVE=oracle.stop+0x600
assert STATE==0x1a22000
def addglobal(name,at,value=0,offset=0):
 if at not in index:glob(name,at,value,4,offset)
 else:assert globals_[index[at]][0]==name;defaults[index[at]]=value
for name,at in [('thug_sound_device',0x7d6a38),('thug_sound_mode',0x7cefa8),('thug_sound_configuration',0x6f85a8)]:addglobal(name,at,CFG if at==0x6f85a8 else 0)
for i in range(48):
 for j in range(15):addglobal('thug_sound_voices',0x6f7a68+i*60+j*4,0,i*60+j*4)
 for j in range(6):addglobal('thug_audio_slots',0x6f85c8+i*24+j*4,0,i*24+j*4)
oracle.globals=globals_;oracle.defaults=defaults
for at in [0x47ad80,0x47c7a0,0x47c7e0,0x47b030,0x47b040]:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
def native(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);buffer=oracle.word(sp+4);n=oracle.word(STATE);assert n<32
 target=oracle.word(STATE+12);oracle.setword(STATE,n+1)
 cpu.mem_write(STATE+128+n*32,struct.pack('<8I',buffer,target,oracle.word(target+24),oracle.word(target),oracle.word(target+8),cpu.mem_read(target+0xfd,1)[0],oracle.word(STATE+4),n))
 for i in range(oracle.word(STATE+8)):oracle.setword(oracle.word(STATE+16+i*8),oracle.word(STATE+20+i*8))
 cpu.reg_write(UC_X86_REG_EAX,oracle.word(STATE+4));cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+8)
oracle.cpu.hook_add(UC_HOOK_CODE,native,begin=STOPNATIVE,end=STOPNATIVE)
old_case=case
def case(calls,patches=(),changes=None,label='looping sound'):
 stages=old_case(calls,patches,changes,label);n=0
 for s in stages:
  new=next((int.from_bytes(bytes.fromhex(data),'little') for at,data in s['outputs'] if at==STATE),n);s['callbacks']=new-n;n=new
 return stages
class SoundGraph(WalkGraph):
 def __init__(self,fmt=2,target=P):
  super().__init__();self.image[STATE-BASE:STATE-BASE+0x500]=bytes(0x500)
  self.put(STATE+12,'<I',target);self.put(LIVE,'<I',VT);self.put(VT,'<19I',*([0]*18+[STOPNATIVE]));self.put(CFG,'<2I',0x12345678,fmt)
  for i in range(32):fields.add(STATE+128+i*32+12)
  self.changes={}
 def voice(self,i,key=7,name=9,active=1,buffer=LIVE):
  self.changes.update({0x6f7a68+i*60:key,0x6f7a6c+i*60:name,0x6f85c8+i*24:buffer,0x6f85d8+i*24:0xa5a5a500|(active&255)})
 def mutations(self,pairs=(),result=0):
  self.put(STATE+4,'<2I',result,len(pairs))
  for i,(at,value) in enumerate(pairs):
   self.put(STATE+16+i*8,'<2I',at,value);fields.add(STATE+16+i*8)
 def run(self,calls,label,changes=None):return super().run(calls,label,{**self.changes,**(changes or {})})
for fill,alignment,fmt in itertools.product([0,0xa5,255],[0,1,4],[0,2,0xffffffff]):
 g=SoundGraph(fmt,P+alignment);g.image[P-BASE:P-BASE+0x130]=bytes([fill])*0x130;fields.add(P+alignment)
 g.run([call(0x5138e0,P+alignment)]*2+[call(0x513b30,P+alignment)]*2,f'looping raw lifetime {fill}/{alignment}/{fmt:x}')
for flags in [0,1,2,3,255,256,257,0xffffffff]:
 g=SoundGraph(target=HEAP);g.run([call(0x513ad0),call(0x513fa0,HEAP,[flags])],f'looping factory/delete {flags:x}')
g=SoundGraph();g.put(CONTEXT+32,'<I',1);g.run([call(0x513ad0)]*2,'looping allocation failure')
for shape in ['missing','first','last','duplicate']:
 g=SoundGraph();types=[] if shape=='missing' else [0xd9151d4d] if shape=='first' else [1,0xd9151d4d] if shape=='last' else [0xd9151d4d]*2
 nodes=[g.component(t) for t in types]
 for i,node in enumerate(nodes):g.put(node+16,'<I',nodes[i+1] if i+1<len(nodes) else 0)
 g.put(OBJ+0x100,'<I',nodes[0] if nodes else 0);g.put(P+12,'<I',OBJ)
 g.run([call(0x513970,P)]*2,f'looping dependency {shape}')
for kind,raw in [(None,0),(2,0),(2,0x80000000),(2,1),(2,0x3f000000),(2,0x7f800000),(2,0xff800000),(2,0x7fc12345),(1,0),(1,0x7fffffff),(1,0x80000000),(3,0x42424242)]:
 g=SoundGraph();s=g.structure([] if kind is None else [(0xf1a99b27,kind,raw)]);g.put(P+0x108,'<I',0x3f123456)
 g.run([call(0x513880,P,[s])]*2,f'optional loop float {kind}/{raw:x}')
for shape in ['absent','id','name','id-before-name','inactive-first','null-buffer','active-byte-zero']:
 for script_gate in [0,1]:
  g=SoundGraph();g.symbol(0x6d2e270e,1,script_gate);g.symbol(0xd7bb618d,1,17)
  if shape=='id':g.voice(47,key=7)
  if shape=='name':g.voice(17,key=99,name=7)
  if shape=='id-before-name':g.voice(0,key=99,name=7);g.voice(47,key=7)
  if shape=='inactive-first':g.voice(0,key=7,active=0);g.voice(47,key=7,active=255)
  if shape=='null-buffer':g.voice(0,key=7,buffer=0)
  if shape=='active-byte-zero':g.voice(0,key=7,active=0)
  g.run([call(0x47ad80,CFG,[7]),call(0x47b4e0,CFG,[7])]*2,f'voice stop/search {shape}/{script_gate}',{0x7d6a38:1})
for device,mode in itertools.product([0,1,0xffffffff],[0,2,6,7,0xffffffff]):
 g=SoundGraph();g.voice(0,key=7);g.run([call(0x47b4e0,CFG,[7])],f'sound enabled gate {device:x}/{mode:x}',{0x7d6a38:device,0x7cefa8:mode})
for i,buffer,result in itertools.product([0,17,47],[0,LIVE],[0,0xffffffff,0x12345678]):
 g=SoundGraph();g.voice(i,buffer=buffer);g.mutations(result=result)
 g.run([call(0x47c7a0,args=[i])],f'existing device stop {i}/{buffer:x}/{result:x}')
for flags,id in itertools.product([0,1,2,255,256,257,0xffffffff],[0,7]):
 g=SoundGraph();g.voice(0,key=7);g.put(P+24,'<I',id);g.put(P+8,'<I',0xa5a5a501);g.put(P+0xfd,'<B',0)
 g.run([call(0x513f60,P,[flags])]*2,f'looping suspend low-byte {flags:x}/{id}',{0x7d6a38:1})
for fn in [0x513b30,0x513f60,0x513fa0]:
 for result in [0,0xffffffff]:
  g=SoundGraph();g.voice(0,key=7);g.put(P,'<I',0x64bf38);fields.add(P);g.put(P+24,'<I',7);g.put(P+0xfd,'<B',0)
  g.mutations([(P+24,9),(P+8,0x12345678),(P+0x100,0x76543210),(0x7d6a38,0)],result)
  g.run([call(fn,P,[] if fn==0x513b30 else [1])],f'looping stop callback ordering {fn:x}/{result:x}',{0x7d6a38:1})
  assert oracle.word(STATE)==1 and oracle.word(P+24)==0 and oracle.word(P+0x100)==0x76543210
for reverse in [False,True]:
 g=SoundGraph();registry=[(0xb5f1e9d2,0x513ad0),(0x43686585,0x519740)];g.registry(registry)
 order=registry[::-1] if reverse else registry;params=[g.structure([(0xb6015ea8,13,t)]) for t,_ in order]
 g.run([call(0x45e510,OBJ)]+[call(0x45ee20,OBJ,[s,0]) for s in params]+[call(0x45db30,OBJ),call(0x45d890,OBJ)],f'shared looping sound lifecycle {reverse}')
scope='Eight new complete routines: voice-stop47b4e0 and seven SkaterLoopingSound lifecycle routines. Existing original voice search47ad80, device stop47c7a0 and embedded volume initialization47b030 are reused, with zero additional address credit. Whole arena/globals/heap/returns/registers compare exactly; external buffer Stop callbacks test field mutation before the final voice clear. Frame513bb0, command5139e0, registration513860, full startup, actual audio device output and playable level remain unverified. Optional float tests use exact bits, without new numeric allowances.'
extra={**extra,'function_exports':function_exports,'memory_fixture':'skater-walk-memory.wasm','callback_counter':'audio_stop_callbacks','native_callbacks':[{'module':'looping-sound-stop-callback.wasm','export':'fixture_looping_sound_stop','slots':[VT+0x48],'original':STOPNATIVE}]}
subprocess.run([str(ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang'),'--target=wasm32-unknown-unknown','-O2','-nostdlib','-Wl,--no-entry,--import-memory,--export-all,--global-base=58720256',str(folder/'looping-sound-stop-callback.c'),'-o',str(folder/'looping-sound-stop-callback.wasm')],check=True)
finish('skater-looping-sound-lifecycle',scope,{},extra)
(folder/'skater-looping-sound-lifecycle-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n')
