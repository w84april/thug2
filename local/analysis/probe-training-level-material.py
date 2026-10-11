"""All actual TR textures followed by its complete streamed material table."""
from pathlib import Path
setup=Path('local/analysis/trace-level-scene.py').read_text().split('\ntry:\n')[0]
# Reuse bounded arena/allocator setup only. The training comparison records
# texture storage and file cursors in shared memory, instead of Python state.
setup=setup.split('resources=[];')[0]
exec(compile(setup,'<preserved isolated training arena>','exec'))
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
import subprocess
folder=ROOT/'local/analysis';IOCTRL,IOLOG,GPULOG=BASE+0x1100,BASE+0x800000,BASE+0x90000
put(FILE,'<2I',SCNDATA+12,SCNDATA+len(scn));put(IOCTRL,'<I',0)
functions={'0x49f050':{'name':'thug_texture_dictionary_get_buffer_draft','this':False,'result':'word','cleanup':0,'memory':True},
 '0x4d3390':{'name':'thug_material_file_parse_draft','this':False,'result':'word','cleanup':0,'memory':True}}
oracle.functions=functions;oracle.event_limit=10000
globals_ += [['thug_scene_file_read_draft',0x340,4],['thug_scene_file_seek_draft',0x344,4]];defaults += [0x5b9ee0,0x5b9fa0]
resources=[];gpu_calls=Counter();io_calls=Counter();fields=set()
exports=[[0x649bb4,'thug_texture_dictionary_base_methods_draft'],[0x64a824,'thug_texture_dictionary_pc_methods_draft'],[0x649af0,'thug_texture_wrapper_base_methods_draft'],[0x64a770,'thug_texture_wrapper_pc_methods_draft']]
def finish(result,argc=0):
 sp=cpu.reg_read(UC_X86_REG_ESP);cpu.reg_write(UC_X86_REG_EAX,result);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4+argc*4)
def gpu_port(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);args=lambda n:[oracle.word(sp+4+i*4) for i in range(n)]
 if at==CREATE:
  values=args(9);device,w,h,levels,usage,fmt,pool,out,shared=values;assert device==DEVICE and 0<levels<=16
  p=oracle.word(CONTROL);next_=p+0x100;surfaces=[];oracle.setword(p,TVT);oracle.setword(p+4,levels)
  for level in range(levels):
   a,b=max(1,w>>level),max(1,h>>level)
   if fmt in [0x31545844,0x35545844]:pitch=max(1,(a+3)//4)*(8 if fmt==0x31545844 else 16);n=pitch*max(1,(b+3)//4)
   else:pitch=a*{0x29:1,0x19:2,0x15:4}[fmt];n=pitch*b
   surfaces.append((next_,n,pitch));cpu.mem_write(p+16+level*12,struct.pack('<3I',next_,n,pitch));next_=(next_+n+15)&~15
  assert next_<BASE+SIZE;oracle.setword(CONTROL,next_);oracle.setword(CONTROL+4,oracle.word(CONTROL+4)+1);oracle.setword(out,p)
  resources.append({'pointer':p,'width':w,'height':h,'format':fmt,'surfaces':surfaces});values.append(p);op=1;argc=9
 elif at==LOCK:
  p,level,out,rect,flags=args(5);assert level<oracle.word(p+4);data,n,pitch=struct.unpack('<3I',cpu.mem_read(p+16+level*12,12))
  oracle.setword(out,pitch);oracle.setword(out+4,data);values=[p,level,rect,flags,data,n,pitch];op=2;argc=5
 else:values=args(2);op=3;argc=2
 i=oracle.word(CONTROL+8);assert i<7000;oracle.setword(CONTROL+8,i+1)
 cpu.mem_write(GPULOG+i*64,struct.pack('<16I',op,*values,*([0]*(15-len(values)))));gpu_calls[op]+=1;finish(0,argc)
for at in [CREATE,LOCK,UNLOCK]:cpu.hook_add(UC_HOOK_CODE,gpu_port,begin=at,end=at)
def file_port(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);arg=lambda i:oracle.word(sp+4+i*4)
 if at==0x5b9ee0:
  out,width,count,file=[arg(i) for i in range(4)];start=oracle.word(file);n=width*count;assert SCNDATA<=start<=start+n<=oracle.word(file+4)
  cpu.mem_write(out,bytes(cpu.mem_read(start,n)));oracle.setword(file,start+n);kind=1;result=n
 else:
  file,width,count=[arg(i) for i in range(3)];assert count==1;start=oracle.word(file);oracle.setword(file,start+width);kind=2;result=start+width
 i=oracle.word(IOCTRL);assert i<70000;oracle.setword(IOCTRL,i+1);cpu.mem_write(IOLOG+i*24,struct.pack('<6I',kind,file,width,count,start,oracle.word(file)))
 io_calls[kind]+=1;finish(result)
for at in [0x5b9ee0,0x5b9fa0]:cpu.hook_add(UC_HOOK_CODE,file_port,begin=at,end=at)
oracle.scope_entries[MANAGER+0x200]=1;oracle.initial=initial=bytes(memory)
code=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(load().get_data(0x4d3390-0x400000,2086),0x4d3390));hits=Counter()
cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:hits.update([at]),begin=0x4d3390,end=0x4d3bb5)
get=(0x49f050,0,[0x12345678,TEXDATA,len(tex),0,0,0,0])
steps=oracle.case([get]);dictionary=steps[-1]['result'];texture_table=oracle.word(dictionary+12)
oracle.cases.clear();oracle.counts.clear();resources.clear();gpu_calls.clear();io_calls.clear()
regs=[UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP];before=[cpu.reg_read(r) for r in regs]
steps=oracle.case([get,(0x4d3390,0,[FILE,texture_table])]);assert before==[cpu.reg_read(r) for r in regs]
table=steps[-1]['result'];assert oracle.word(table+8)==870 and oracle.word(texture_table+8)==596 and len(resources)==596
assert oracle.word(FILE)-SCNDATA==110338
# Independently check every original mip upload against untouched file bytes.
cursor=8;mip_count=0
for resource in resources:
 key,w,h,levels,depth,palette_depth,compression,palette_bytes=struct.unpack_from('<8I',tex,cursor);cursor+=32
 assert(resource['width'],resource['height'],len(resource['surfaces']))==(w,h,levels)
 for address,capacity,pitch in resource['surfaces']:
  n=struct.unpack_from('<I',tex,cursor)[0];cursor+=4;assert n<=capacity
  assert bytes(cpu.mem_read(address,n))==tex[cursor:cursor+n];cursor+=n;mip_count+=1
assert cursor==len(tex) and mip_count==2486
materials=[];bound_resources=set();buckets=oracle.word(table+4)
for bucket in range(1<<oracle.word(table)):
 entry=buckets+bucket*12
 while entry:
  material=oracle.word(entry+4)
  if material:
   passes=oracle.word(material+8);assert passes<=4
   refs=[oracle.word(material+0x30+j*4) for j in range(passes)];bound_resources.update(v for v in refs if v)
   materials.append({'key':hex(oracle.word(material)),'pointer':hex(material),'passes':passes,'resources':[hex(v) for v in refs]})
  entry=oracle.word(entry+8)
assert len(materials)==870
for case in oracle.cases:
 for step in case['steps']:
  for at,data in step['outputs']:
   if int.from_bytes(bytes.fromhex(data),'little') in {e[0] for e in exports}:fields.add(at)
  merged=[];chunks=[];start=end=0
  for at,data in step['outputs']:
   if chunks and at!=end:merged.append([start,''.join(chunks)]);chunks=[]
   if not chunks:start=at
   chunks.append(data);end=at+len(data)//2
  if chunks:merged.append([start,''.join(chunks)])
  step['outputs']=merged
clang=ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang';port=folder/'training-level-material-ports.c';output=folder/'training-level-material-ports.wasm'
cmd=[str(clang),'--target=wasm32-unknown-unknown','-O2','-nostdlib','-Wl,--no-entry,--export-all,--import-memory',str(port),'-o',str(output)];subprocess.run(cmd,check=True)
output.with_suffix('.build.json').write_text(json.dumps({'command':cmd,'source_sha256':hashlib.sha256(port.read_bytes()).hexdigest(),'sha256':hashlib.sha256(output.read_bytes()).hexdigest()},indent=2)+'\n')
scope='Untouched3915744-byte TR.tex.xbx parses into596 textures and2486 exact mip uploads, then the original streamed TR.scn.xbx material reader builds870 materials and resolves their real texture resources. All read/seek groups, cursor110338, whole30MiB arena, heap, globals and GPU comparison storage match. This completes the material-loading prerequisite; sector/mesh streaming, scene boot and real rendering remain incomplete.'
fixture={'base':BASE,'memory':'training-level-material-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'training-level-material-ports.wasm','memory_exports':['fixture_training_allocate','fixture_values_release','fixture_values_scope'],
 'globals':globals_,'pointer_globals':[len(globals_)-2,len(globals_)-1],'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':['all training textures and streamed materials'],
 'pointer_fields':sorted(fields),'pointer_exports':exports,'pointer_initializers':[['thug_texture_allocation_scope_draft',oracle.stop+0x330],['thug_scene_file_read_draft',0x5b9ee0],['thug_scene_file_seek_draft',0x5b9fa0]],
 'native_callbacks':[{'module':'training-level-material-ports.wasm','export':'fixture_training_'+name,**options} for name,options in [('create',{'slots':[DVT+0x5c]}),('lock',{'slots':[TVT+0x4c]}),('unlock',{'slots':[TVT+0x50]}),('scope',{'original':oracle.stop+0x330}),('read',{'original':0x5b9ee0}),('seek',{'original':0x5b9fa0})]],'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'training-level-material-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':1,'calls':2,'texture_sha256':hashlib.sha256(tex).hexdigest(),'scene_sha256':hashlib.sha256(scn).hexdigest(),
 'textures':596,'mips':mip_count,'materials':870,'bound_texture_resources':len(bound_resources),'scene_material_end':110338,'texture_dictionary':hex(dictionary),'material_table':hex(table),
 'gpu_calls':dict(gpu_calls),'file_calls':dict(io_calls),'material_records':materials,'resources':resources,'instruction_coverage':{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code)},'scope':scope}
(folder/'training-level-material-original.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['material_records','resources']}),flush=True)
