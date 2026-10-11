"""Combine whole original QB startup state and complete TR scene; trace LevelObjects."""
from pathlib import Path
import types,sys
folder=Path('local/analysis')
# A separate larger comparison arena, never overlapping the original stack/stop.
raw=Path('tools/script_heap_oracle.py').read_text().replace('self.stack=0x3000000;self.stop=0x3f00000','self.stack=0x7000000;self.stop=0x7f00000')
module=types.ModuleType('level_object_oracle');exec(compile(raw,'<relocated comparison stack>','exec'),module.__dict__);sys.modules[module.__name__]=module
source=Path('tools/verify_script_load.py').read_text().split('labels=[];max_heap=HEAP')[0]
source=source.replace(';report_path.unlink(missing_ok=True)','').replace(";(out/'script-load-memory.bin').write_bytes(initial)",'')
source=source.replace('from script_heap_oracle import ScriptHeapOracle','from level_object_oracle import ScriptHeapOracle').replace('BASE,SIZE=0x1000000,0x1e00000','BASE,SIZE=0x800000,0x5800000').replace('BASE+0xb00000','BASE+0x1c00000')
source=source.replace("put(CONTEXT,'<9I',HEAP,BASE+SIZE", "put(CONTEXT,'<9I',HEAP,0x4000000")
source=source.replace('event_limit=(HEAP-LOG)//48','event_limit=180000')
assert '.write_' not in source and '.unlink(' not in source
exec(compile(source,'<original QB loader setup>','exec'))
for name,marker in [('probe-training-node-registration.py','regs='),('probe-training-prop-components.py','loads=')]:
 src=(folder/name).read_text().split(marker)[0];src=src.split("exec(compile(source,")[1].split('\n',1)[1]
 exec(compile(src,'<original '+name+' setup>','exec'))
src=(folder/'probe-training-model-transform.py').read_text().split('steps=oracle.case(prefix);array=')[0]
src=src.split("exec(compile(source,")[1].split('\n',1)[1]
src=src.replace('elif at in [a for _,a in newtypes if a!=0x421490]:','elif at in [a for _,a in newtypes if a not in (0x421490,0x433d90,0x41c920)]:')
src=src.replace("exec(compile(Path('local/analysis/asset-ready-training-ports-setup.py').read_text(),'<explicit texture platform ports>','exec'))",'')
src=src.replace("exec(compile((folder/'vertex-upload-ports-setup.py').read_text(),'<separate CRT and index GPU providers>','exec'))",'')
exec(compile(src,'<original component and interpreter setup>','exec'))
src=(folder/'probe-training-scene-create.py').read_text().split('initial=bytes(memory);oracle.initial=initial')[0]
src=src.split("exec(compile(source,")[1].split('\n',1)[1]
exec(compile(src,'<original single-player creation setup>','exec'))
# Metadata occupies the former isolated asset-port area. Script cache remains CACHE.
DEVICE,DVT,TVT,CONTROL,FILE,NAME,IOCTRL,MESHCTL,BVT,MTABLE,TEXCACHE,OWNER_HEADER=[BASE+n for n in [0xf1000,0xf1100,0xf1200,0xf1300,0xf2000,0xf2100,0xf2200,0xf2300,0xf2400,0xf2500,0xf2600,0xf2800]]
TEXDATA,SCNDATA,IOLOG,GPULOG=[BASE+n for n in [0x1000000,0x1400000,0x1700000,0x1a00000]]
memory[BASE+0xf1000-BASE:BASE+0xf3000-BASE]=bytes(0x2000)
put(DEVICE,'<I',DVT);put(CONTROL,'<4I',0x5000000,0,0,0);put(MESHCTL,'<9I',0x4000000,0x4800000,0,0,0,0,0,0,0);put(OWNER_HEADER,'<I',HSTATE)
data_root=ROOT/'local/game-files/Game/Data/levels/TR';tex=(data_root/'TR.tex.xbx').read_bytes();scn=(data_root/'TR.scn.xbx').read_bytes()
memory[TEXDATA-BASE:TEXDATA-BASE+len(tex)]=tex;memory[SCNDATA-BASE:SCNDATA-BASE+len(scn)]=scn
filename=b'levels\\TR\\TR.scn.Xbx\0';memory[NAME-BASE:NAME-BASE+len(filename)]=filename
SHORTNAME=NAME+0x80;memory[SHORTNAME-BASE:SHORTNAME-BASE+3]=b'TR\0';put(FILE,'<2I',SCNDATA,SCNDATA+len(scn))
for n,a,v in [('thug_texture_resource_registry_draft',0x7cc254,0),('thug_mesh_device',0x7d69e0,DEVICE),('thug_scene_file_read_draft',0x340,0x5b9ee0),('thug_scene_file_seek_draft',0x344,0x5b9fa0),('thug_scene_file_open_draft',0x348,0x5b9e60),('thug_scene_file_close_draft',0x34c,0x5b9ea0)]:glob(n,a,v)
for i,v in enumerate([4,TEXCACHE,0,0xffffffff,0,0]):glob('thug_model_texture_table_draft',0x700f04+i*4,v,offset=i*4)
TABLE_INDEX=len(globals_)
for i in range(33):glob('thug_mesh_material_table',0x775b80+i*4,0,offset=i*4)
# Use the original existing script locale; registry setup must not replace it.
src=(folder/'level-register-oracle-setup.py').read_text().split('# Ordinary narrow-string')[0];exec(compile(src,'<original scene registry setup>','exec'))
oracle.scope_entries[HSTATE]=1;oracle.instruction_limit=200000000;cpu=oracle.cpu
CREATE,LOCK,UNLOCK=oracle.stop+0x300,oracle.stop+0x310,oracle.stop+0x320
put(DVT+0x5c,'<I',CREATE);put(TVT+0x4c,'<2I',LOCK,UNLOCK)
src=(folder/'probe-training-level-material.py').read_text().split('\nresources=[];')[1].split('oracle.scope_entries[MANAGER+0x200]')[0]
saved_fields=fields.copy();saved_exports=exports[:]
src=src.replace('assert SCNDATA<=start<=start+n<=oracle.word(file+4)',"assert SCNDATA<=start<=start+n<=oracle.word(file+4),(hex(file),hex(start),width,count,hex(oracle.word(file+4)),hex(SCNDATA),dict(io_calls))")
exec(compile('resources=[];'+src.replace('i<70000','i<125000'),'<original recorded texture and scene file ports>','exec'))
fields.update(saved_fields);exports+=saved_exports
src=(folder/'probe-training-level-mesh.py').read_text().split('BCREATE,BLOCK,BUNLOCK=')[1].split("functions['0x4d4be0']")[0]
# The shader globals were already initialized by the component setup.
src=src[:src.index('for name,at,value,width,off in')]+src[src.index('buffers=[]'):]
src=src.replace('0x2400000','0x4800000').replace('0x2800000','0x5000000')
exec(compile('BCREATE,BLOCK,BUNLOCK='+src,'<original recorded CRT and buffer ports>','exec'))
def file_lifetime(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP)
 if at==0x5b9e60:
  name,mode=oracle.word(sp+4),oracle.word(sp+8);assert bytes(cpu.mem_read(name,len(filename)))==filename and bytes(cpu.mem_read(mode,3))==b'rb\0'
  oracle.setword(FILE,SCNDATA);oracle.setword(MESHCTL+24,oracle.word(MESHCTL+24)+1);finish(FILE)
 else:assert oracle.word(sp+4)==FILE;oracle.setword(MESHCTL+28,oracle.word(MESHCTL+28)+1);finish(1)
for a in [0x5b9e60,0x5b9ea0]:cpu.hook_add(UC_HOOK_CODE,file_lifetime,begin=a,end=a)
def owner_query(cpu,at,size,user):
 p=oracle.word(cpu.reg_read(UC_X86_REG_ESP)+4);assert HEAP<=p<0x4000000
 oracle.setword(CONTROL+12,oracle.word(CONTROL+12)+1);finish(OWNER_HEADER)
cpu.hook_add(UC_HOOK_CODE,owner_query,begin=0x5ba090,end=0x5ba090)
for name in ['training-geometry-clone-fixtures.json','training-scene-create-fixtures.json']:
 for e in json.loads((folder/name).read_text())['pointer_exports']:
  if e not in exports:exports.append(e)
functions.update({'0x49f050':{'name':'thug_texture_dictionary_get_buffer_draft','this':False,'result':'word','cleanup':0,'memory':True},'0x48ccb0':{'name':'thug_level_scene_load_draft','this':False,'result':'word','cleanup':0,'memory':True},'0x468ec0':{'name':'thug_level_object_create_prefix_draft','this':False,'result':'void','cleanup':0,'stack_args':[0]}})
# Independent arena-capacity assertions. These are platform state, not game data.
assert STRINGS<LOG and LOG+oracle.event_limit*48<TEXDATA
assert TEXDATA+len(tex)<SCNDATA and SCNDATA+len(scn)<IOLOG and IOLOG+125000*24<GPULOG and GPULOG+7000*64<HEAP
oracle.initial=initial=bytes(memory)
trace_hits=Counter();trace=[]
from collections import deque
from unicorn import UC_HOOK_BLOCK
recent_blocks=deque(maxlen=80)
def block_trace(cpu,at,size,user):
 if trace:recent_blocks.append(hex(at))
def begin_blocks(cpu,at,size,user):
 if not trace:cpu.hook_add(UC_HOOK_BLOCK,block_trace)
cpu.hook_add(UC_HOOK_CODE,begin_blocks,begin=0x468ec0,end=0x468ec0)
for a in [0x468ec0,0x468b60,0x468cb0,0x45f330,0x45dad0,0x475790,0x420d10,0x41ffa0,0x420480,0x48e660]:
 def track(cpu,at,size,user):
  trace_hits[hex(at)]+=1
  if len(trace)<2000:trace.append([hex(at),hex(cpu.reg_read(UC_X86_REG_ECX)),hex(oracle.word(cpu.reg_read(UC_X86_REG_ESP)+4))])
 cpu.hook_add(UC_HOOK_CODE,track,begin=a,end=a)
cpu.hook_add(UC_HOOK_CODE,created_object,begin=0x468ee1,end=0x468ee1)
wrapper_code={a:list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(a-0x400000,n),a)) for a,n in [(0x468ec0,85),(0x468b60,333)]};wrapper_hits=Counter()
for a,c in wrapper_code.items():cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:wrapper_hits.update([at]),begin=a,end=c[-1].address)
# Original file resident at a distinct, bounded address; game parser relocates it.
from collision_file import layout
COLLDATA=BASE+0x1b00000;collision=(data_root/'TR.col.xbx').read_bytes();collision_layout=layout(collision)
assert GPULOG+7000*64<COLLDATA and COLLDATA+len(collision)<HEAP
memory[COLLDATA-BASE:COLLDATA-BASE+len(collision)]=collision
oracle.initial=initial=bytes(memory)
glob('thug_collision_load_observer_draft',0x6fa7c8,0)
exports.append([0x645c18,'thug_static_collision_methods'])
functions['0x49d590']={'name':'thug_scene_collision_load_draft','this':True,'result':'byte','cleanup':8,'memory':True}
collision_code={a:list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(a-0x400000,n),a)) for a,n in [(0x49d590,483),(0x49e890,15),(0x49eaa0,40),(0x48df10,10)]};collision_hits=Counter()
for a,c in collision_code.items():cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:collision_hits.update([at]),begin=a,end=c[-1].address)

glob('thug_asset_manager',0x6918dc,0);glob('thug_asset_manager_references_draft',0x6918e0,0)
functions['0x4088e0']={'name':'thug_asset_manager_acquire_draft','this':False,'result':'void','cleanup':0,'memory':True}
extra=[]
def collision_trace(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);extra.append([hex(at),hex(cpu.reg_read(UC_X86_REG_ECX)),[hex(oracle.word(sp+4+i*4)) for i in range(4)]])
for a in [0x4088e0,0x407f80,0x44f7e0,0x406890,0x41c920,0x41c7b0,0x41c890,0x414990,0x41c980,0x4177b0]:cpu.hook_add(UC_HOOK_CODE,collision_trace,begin=a,end=a)
f=json.loads((folder/'level-collision-load-fixtures.json').read_text());old=f['cases'][0]['steps'];calls=[(int(s['fn'],16),s['this'],s['args']) for s in old[:10]]+[(0x4088e0,0,[1]),(0x4738e0,SCRIPT,[])]+[(0x5a4ff0,0,old[11]['args'])]
try:
 steps=oracle.case(calls);print('COMPLETED',len(steps),'lastresult',steps[-1]['result'],'manager',hex(oracle.word(0x6918dc)),flush=True)
except Exception as error:
 print('STOP',repr(error),'EIP',hex(cpu.reg_read(UC_X86_REG_EIP)),flush=True)
finally:
 print('TRACE',json.dumps(extra),'FACTORY',factory_hit,'created',created,flush=True)
 (folder/'level-collision-component-exploration.json').write_text(json.dumps({'trace':extra,'factory_hit':factory_hit,'created':created,'eip':hex(cpu.reg_read(UC_X86_REG_EIP))},indent=2)+'\n')
