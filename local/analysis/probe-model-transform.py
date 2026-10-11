"""Original-instruction comparisons for Model transform helpers and normal update."""
from pathlib import Path
source=Path('local/analysis/probe-texture-buffer.py').read_text().split('for fill in [0,0xa5,0xff]:')[0]
exec(compile(source,'<preserved initialized comparison arena>','exec'))
import random
functions.clear();code.clear();hits.clear();oracle.counts.clear();oracle.coverage.clear()
specs=[(0x41a640,57,'model_matrix_identity',0,'word'),(0x420590,209,'model_transform_channel',0,'double'),
 (0x4213e0,90,'model_transform_channels',0,'double'),(0x4215f0,872,'model_transform_matrix',1,'word'),
 (0x4204b0,62,'model_component_finalize',0,'void'),(0x4b4630,83,'model_geometry_enabled',1,'void'),
 (0x4b47b0,62,'model_geometry_transform_pc',5,'byte'),(0x48df30,5,'model_geometry_transform',5,'byte'),
 (0x419ca0,33,'model_animation_active',0,'word'),(0x49f4a0,5,'model_renderer_bone_map',1,'word')]
for a,n,name,argc,result in specs:
 functions[hex(a)]={'name':'thug_'+name+'_draft','this':True,'result':result,'cleanup':argc*4,'memory':False}
 code[a]=list(md.disasm(pe.get_data(a-0x400000,n),a));oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:hits.update([at]),begin=a,end=a+n-1)
partials=[(0x493090,859,'model_renderer_update_prefix',3,'byte')]
partial_code={};partial_hits=Counter()
for a,n,name,argc,result in partials:
 functions[hex(a)]={'name':'thug_'+name+'_draft','this':True,'result':result,'cleanup':argc*4,'memory':False}
 partial_code[a]=list(md.disasm(pe.get_data(a-0x400000,n),a));oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:partial_hits.update([at]),begin=a,end=a+n-1)
exports += [[0x64a368,'thug_model_geometry_lights_methods_draft'],[0x64a4b4,'thug_model_renderer_methods_draft']]
for name,at,value in [('thug_frame_counter',0x7d1ec8,250),('thug_frame_rate',0x684fd0,0x447a0000),
 ('thug_timer_origin',0x696d64,0),('thug_time_scale',0x67d7c0,0x3f800000),('thug_timer_offset',0x696d60,0)]:
 globals_.append([name,at,4]);defaults.append(value)
oracle.setword(0x684fe4,0x5df4ac)
OUT=P+0x1800
IDENTITY=[0x3f800000 if i%5==0 else 0 for i in range(16)]
def check(g,calls,label,arithmetic=(),quiet=(),timer=None):
 changes={} if timer is None else {len(defaults)-5:timer}
 regs=[UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP]
 before=[oracle.cpu.reg_read(r) for r in regs]
 try:steps=oracle.case(calls,g.patches(),changes)
 except Exception:print('FAILED',label,flush=True);raise
 assert before==[oracle.cpu.reg_read(r) for r in regs],label
 labels.append(label)
 for s in steps:
  if arithmetic:s['float_fields']=list(arithmetic)
  if quiet:s['quiet_float_fields']=list(quiet)
 return steps
def zero(g,at,n):g.data[at-BASE:at-BASE+n]=bytes(n)
def channel(g,at,duration=1000,start=0,base=10,amplitude=20,curve=0,flags=1):
 g.put(at,'<fIffiB',duration,start,base,amplitude,curve,flags)
def component(g):
 owner=g.alloc(0x140);zero(g,P,0x238);zero(g,owner,0x140);g.put(P+12,'<I',owner)
 g.put(owner+0xc0,'<16I',*IDENTITY);g.put(owner+0x4c,'<4f',1.25,-3.5,81,1)
 g.put(P+0x34,'<f',1);g.put(P+0x204,'<f',1)
 return owner
def geometry(g,instanced=True,count=0):
 geom=g.alloc(100);instance=g.alloc(100);zero(g,geom,100);zero(g,instance,100)
 g.put(geom,'<I',0x64a368);g.put(geom+0x4c,'<I',instance if instanced else 0)
 dest=g.alloc(max(64,count*64));g.put(instance+0x44,'<I',dest)
 return geom,instance,dest
for off in [0,4,12]:
 g=Graph();check(g,[call(0x41a640,OUT+off)]*2,f'identity offset{off}')
for flags in [0,2,4,0x80,1,3,5,7,255]:
 for t in [0,250,1000,1001,0xffffffff]:
  g=Graph();channel(g,P,flags=flags);check(g,[call(0x420590,P)]*2,f'channel flags{flags}/time{t}',timer=t)
for curve in [-2147483648,-2,-1,0,1,2,3,5]:
 for t in [0,1,123,500,999,1000,1001]:
  g=Graph();channel(g,P,curve=curve);check(g,[call(0x420590,P)],f'channel curve{curve}/time{t}',timer=t)
for duration in [-1000,-0.0,0.0,0.125,1,2**31,2**32,float('inf'),float('nan')]:
 for t in [0,1,0x7fffffff,0x80000000,0xffffffff]:
  g=Graph();channel(g,P,duration=duration);check(g,[call(0x420590,P)],f'channel duration{duration}/time{t}',timer=t)
for start in [249,250,251,0x80000000,0xffffffff]:
 g=Graph();channel(g,P,start=start,flags=7);check(g,[call(0x420590,P)],f'channel timestamp{start}')
for value in [0x80000000,1,0x7fffff,0x7f7fffff,0x7f800000,0xff800000,0x7fa12345,0xffa12345]:
 for o in [0,8,12]:
  g=Graph();channel(g,P);g.put(P+o,'<I',value);check(g,[call(0x420590,P)],f'channel bits{value:x}/field{o}')
for active in [0,1,255]:
 for mask in [0,1,2,4,8,16,32,63]:
  g=Graph();zero(g,P,0x94);g.put(P+0x90,'<B',active)
  for i in range(6):channel(g,P+24*i,base=i-3,amplitude=2*i,flags=1 if mask&(1<<i) else 0,curve=i-2)
  check(g,[call(0x4213e0,P)]*2,f'group active{active}/mask{mask}')
g=Graph();zero(g,P,0x94);g.put(P+0x90,'<B',255)
for i in range(6):channel(g,P+24*i,duration=0,flags=1)
check(g,[call(0x4213e0,P)]*3,'group expiry retains active one call')
for mirror in [0,1,255]:
 for outmode in ['separate','owner_matrix','owner_position']:
  g=Graph();owner=component(g);g.put(P+0x1f4,'<B',mirror)
  g.put(P+0x1f8,'<4f',3,4,-2,1)
  out=OUT if outmode=='separate' else owner+(0xc0 if outmode=='owner_matrix' else 0x4c)
  check(g,[call(0x4215f0,P,[out])],f'transform mirror{mirror}/{outmode}',arithmetic=[out+48+i*4 for i in range(3)])
for axis_mask in range(8):
 for pivot in [[0,0,0,1],[1,0,0,1],[0,2,0,1],[0,0,3,1],[2,-3,5,0]]:
  g=Graph();component(g);g.put(P+0x28,'<4f',*pivot)
  for axis in range(3):
   at=P+0x38+axis*0x94;g.put(at+0x90,'<B',bool(axis_mask&(1<<axis)));channel(g,at,base=(axis+1)*20,amplitude=30,curve=axis-1)
  check(g,[call(0x4215f0,P,[OUT])],f'transform axes{axis_mask}/pivot{pivot}',arithmetic=[OUT+i*4 for i in range(16)])
for axis in range(3):
 g=Graph();component(g);at=P+0x38+axis*0x94;g.put(at+0x90,'<B',1);channel(g,at,base=0,amplitude=0)
 check(g,[call(0x4215f0,P,[OUT])],'active zero angle axis'+str(axis))
for value in [0x80000000,1,0x7f7fffff,0x7f800000,0x7fa12345,0xffa12345]:
 for mirror in [0,1]:
  g=Graph();owner=component(g);g.put(P+0x1f4,'<B',mirror);g.put(owner+0xc0,'<12I',*[value]*12);g.put(owner+0x4c,'<3I',value,value,value)
  check(g,[call(0x4215f0,P,[OUT])],f'transform raw{value:x}/mirror{mirror}',arithmetic=[OUT+i*4 for i in [12,13,14]],quiet=[OUT+i*4 for i in [0,1,2,3,8,9,10,11]] if mirror else [])
for kinds in [[],[0x222756d5],[0x7149b753],[0xce0ca665],[1,0x222756d5,0x7149b753,0xce0ca665], [0xce0ca665,0xce0ca665,0x222756d5,0x7149b753]]:
 g=Graph();owner=component(g);nodes=[g.alloc(24) for k in kinds]
 g.put(owner+0x100,'<I',nodes[0] if nodes else 0)
 for i,(node,key) in enumerate(zip(nodes,kinds)):g.put(node+4,'<4I',key,0,owner,nodes[i+1] if i+1<len(nodes) else 0)
 check(g,[call(0x4204b0,P)]*2,'finalize '+str(kinds))
for enabled in [0,1,2,255,256,257,0xffffffff]:
 for count in [-1,0,1,4]:
  g=Graph();geom,instance,_=geometry(g,count==-1)
  if count>=0:
   array=g.alloc(max(4,count*4));g.put(geom+0x3c,'<2I',array if count else 0,count)
   for i in range(count):mesh=g.alloc(8);g.put(mesh,'<I',0xdeadbeef^i*0x40);g.put(array+i*4,'<I',mesh)
  check(g,[call(0x4b4630,geom,[enabled])]*2,f'enabled{enabled}/count{count}')
g=Graph();geom,_,_=geometry(g,False);g.put(geom+0x3c,'<2I',g.alloc(4),0);check(g,[call(0x4b4630,geom,[0])],'enabled nonnull zero array')
for fn in [0x4b47b0,0x48df30]:
 for count in [0,1,3,0x4000000,0x4000001]:
  for overlap in [-4,0,4,None]:
   g=Graph();geom,instance,dest=geometry(g,True,count&3);source=dest+overlap if overlap is not None else g.alloc(256)
   for i in range(32):g.put(source+i*4,'<I',0x7fa12345+i)
   g.put(OUT,'<16I',*[0xdeadbeef+i for i in range(16)])
   check(g,[call(fn,geom,[OUT,source,count,123,321])],f'geometry transform{fn:x}/count{count}/overlap{overlap}')
 g=Graph();geom,_,_=geometry(g,False);check(g,[call(fn,geom,[0,0,0xffffffff,0,0])],'missing instance '+hex(fn))
for flags in [0,1,2,3,4,5,6,7,255]:
 g=Graph();zero(g,P,0x40);model=g.alloc(0x240);renderer=g.alloc(0x50);zero(g,renderer,0x50)
 g.put(P+0x20,'<I',model);g.put(model+0x208,'<I',renderer);g.put(renderer+0x44,'<B',flags)
 check(g,[call(0x419ca0,P)],'animation flags'+str(flags))
g.put(model+0x208,'<I',0);check(g,[call(0x419ca0,P)],'animation absent renderer')
for count in [0,1,32,0xffffffff]:
 g=Graph();check(g,[call(0x49f4a0,0,[count])],'actual PC bone map '+str(count))
# Contextual partial renderer: real geometry methods, no test virtual callbacks.
for count in [0,1,3,33]:
 for provider_enabled in [False,True]:
  for no_bones in [0,1,256,257]:
   g=Graph();zero(g,P,0x50);head=g.alloc(12);nodes=[head]+[g.alloc(12) for _ in range(count)]
   for i,node in enumerate(nodes):
    geom,instance,dest=geometry(g,True,2);part=g.alloc(24);g.put(part,'<I',geom);g.put(node,'<3I',part,nodes[(i+1)%len(nodes)],nodes[i-1])
   g.put(P,'<I',0x64a4b4);g.put(P+0x10,'<I',head);g.put(P+0x18,'<I',0x55555555);g.put(P+0x44,'<B',10)
   g.put(P+0x1c,'<3f',2,-3,.25);g.put(OUT,'<16I',*IDENTITY)
   provider=g.alloc(24);bones=g.alloc(128);g.put(provider+4,'<I',bones);g.put(provider+0x14,'<I',2)
   for i in range(32):g.put(bones+i*4,'<I',0xdeadbeef+i)
   check(g,[call(0x493090,P,[OUT,no_bones,provider if provider_enabled else 0])],f'renderer parts{count}/provider{provider_enabled}/skip{no_bones}')
coverage={hex(a):{'total':len(c),'covered':sum(bool(hits[i.address]) for i in c),'missing':[hex(i.address) for i in c if not hits[i.address]]} for a,c in code.items()}
partial_coverage={hex(a):{'complete':False,'total':len(c),'covered':sum(bool(partial_hits[i.address]) for i in c),'executed':[hex(i.address) for i in c if partial_hits[i.address]]} for a,c in partial_code.items()}
print('COVERAGE',json.dumps(coverage),flush=True)
for case in oracle.cases:
 for at,data in case.get('patches',[]):
  if int.from_bytes(bytes.fromhex(data),'little') in {e[0] for e in exports}:fields.add(at)
scope='Ten complete Model transform/dependency/geometry helpers compared against original instructions, plus contextual ordinary renderer transforms through actual PC virtuals. Frame rate uses positive finite gameplay values and the maintained PC24 arithmetic/SSE matrix backend; transcendental operations retain the existing explicit platform sin adapter. Whole arena/globals/returns/registers compared. NaN classification is limited to arithmetic outputs; raw bone copies and mirrored matrix NaN payload quieting remain exact. Alternate attachments, lighting and skeleton debug drawing remain incomplete; this is not a playable game.'
fixture={'base':BASE,'memory':'model-transform-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'texture-buffer-ports.wasm','memory_exports':['fixture_texture_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'pointer_fields':sorted(fields),'pointer_exports':exports,'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'model-transform-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(len(c['steps']) for c in oracle.cases),'instruction_coverage':coverage,'partial_coverage':partial_coverage,'scope':scope}
(folder/'model-transform-original.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['instruction_coverage','partial_coverage','scope']}),flush=True)
