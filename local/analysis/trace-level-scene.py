"""Original TR scene file path with explicit resident-file and GPU test ports.
No Windows code is run natively. Stop at the first sector streaming parser.
"""
import hashlib,json,struct
from collections import Counter
from pathlib import Path
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import *
from specimen import ROOT,SHA256,load
from script_heap_oracle import ScriptHeapOracle
BASE,SIZE=0x1000000,0x1e00000
ADAPTER,CONTEXT,MANAGER,DEVICE,DVT,TVT,CACHE,CONTROL= [BASE+n for n in [0x100,0x200,0x400,0x800,0x900,0xa00,0xc00,0x1000]]
FILE,NAME,LOG,TEXDATA,SCNDATA,HEAP,GPU= [BASE+n for n in [0x2000,0x2100,0x10000,0x100000,0x500000,0xa00000,0x1800000]]
memory=bytearray(SIZE);put=lambda a,f,*v:struct.pack_into(f,memory,a-BASE,*v)
put(CONTEXT,'<8I',HEAP,GPU,0,LOG,BASE,BASE+SIZE,0,0);put(ADAPTER,'<4I',CONTEXT,0,0,0)
put(DEVICE,'<I',DVT);put(CONTROL,'<2I',GPU,0)
data_root=ROOT/'local/game-files/Game/Data/levels/TR'
tex=(data_root/'TR.tex.xbx').read_bytes();scn=(data_root/'TR.scn.xbx').read_bytes()
memory[TEXDATA-BASE:TEXDATA-BASE+len(tex)]=tex;memory[SCNDATA-BASE:SCNDATA-BASE+len(scn)]=scn
filename=b'levels\\TR\\TR.scn.xbx\0';memory[NAME-BASE:NAME-BASE+len(filename)]=filename
globals_=[['thug_texture_resource_registry_draft',0x7cc254,4],['thug_mesh_device',0x7d69e0,4],['thug_lookup_node_pool',0x7d1808,4]]
defaults=[0,DEVICE,0]
for i,v in enumerate([4,CACHE,0,0xffffffff,0,0]):globals_.append(['thug_model_texture_table_draft',0x700f04+i*4,4,i*4]);defaults.append(v)
functions={'0x49f050':{'name':'texture','this':False,'result':'word','cleanup':0,'memory':True},'0x4b36d0':{'name':'scene','this':False,'result':'word','cleanup':0}}
oracle=ScriptHeapOracle(memory,BASE,CONTEXT,MANAGER,globals_,defaults,functions,event_limit=11000,instruction_limit=15000000)
original_record=oracle.record
def record(kind,a,b,c):
 if kind==1:oracle.setword(c-16,MANAGER+0x200)
 original_record(kind,a,b,c)
oracle.record=record
put(MANAGER+0x110,'<I',MANAGER+0x700);oracle.scope_entries[MANAGER+0x700]=2
cpu=oracle.cpu;CREATE,LOCK,UNLOCK=oracle.stop+0x100,oracle.stop+0x110,oracle.stop+0x120
put(DVT+0x5c,'<I',CREATE);put(TVT+0x4c,'<2I',LOCK,UNLOCK)
resources=[];gpu_calls=Counter();io_calls=Counter();trace=[];position=0
def finish(result,argc=0):
 sp=cpu.reg_read(UC_X86_REG_ESP);cpu.reg_write(UC_X86_REG_EAX,result);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4+argc*4)
def gpu_port(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);args=lambda n:[oracle.word(sp+4+i*4) for i in range(n)]
 if at==CREATE:
  device,w,h,levels,usage,fmt,pool,out,shared=args(9);assert device==DEVICE and 0<levels<=16
  p=oracle.word(CONTROL);next_=p+0x100;surfaces=[]
  for level in range(levels):
   a,b=max(1,w>>level),max(1,h>>level)
   if fmt in [0x31545844,0x35545844]:pitch=max(1,(a+3)//4)*(8 if fmt==0x31545844 else 16);n=pitch*max(1,(b+3)//4)
   else:pitch=a*{0x29:1,0x19:2,0x15:4}[fmt];n=pitch*b
   surfaces.append((next_,n,pitch));next_=(next_+n+15)&~15
  assert next_<BASE+SIZE
  oracle.setword(CONTROL,next_);oracle.setword(p,TVT);oracle.setword(out,p)
  resources.append({'pointer':p,'width':w,'height':h,'format':fmt,'surfaces':surfaces});gpu_calls['create']+=1;finish(0,9)
 elif at==LOCK:
  p,level,out,rect,flags=args(5);resource=next(r for r in resources if r['pointer']==p);data,n,pitch=resource['surfaces'][level]
  oracle.setword(out,pitch);oracle.setword(out+4,data);gpu_calls['lock']+=1;finish(0,5)
 else:gpu_calls['unlock']+=1;finish(0,2)
for at in [CREATE,LOCK,UNLOCK]:cpu.hook_add(UC_HOOK_CODE,gpu_port,begin=at,end=at)
def file_port(cpu,at,size,user):
 global position
 sp=cpu.reg_read(UC_X86_REG_ESP);arg=lambda i:oracle.word(sp+4+i*4)
 if at==0x5b9e60:
  assert bytes(cpu.mem_read(arg(0),len(filename)))==filename
  position=0;result=FILE;label='open'
 elif at==0x5b9ee0:
  out,width,count,file=arg(0),arg(1),arg(2),arg(3);assert file==FILE;n=width*count;assert position+n<=len(scn)
  cpu.mem_write(out,scn[position:position+n]);position+=n;result=n;label='read'
 elif at==0x5b9fa0:
  assert arg(0)==FILE and arg(2)==1;position+=arg(1);assert position<=len(scn);result=position;label='seek'
 else:assert at==0x5b9ea0 and arg(0)==FILE;result=1;label='close'
 io_calls[label]+=1;finish(result)
for at in [0x5b9e60,0x5b9ee0,0x5b9fa0,0x5b9ea0]:cpu.hook_add(UC_HOOK_CODE,file_port,begin=at,end=at)
def observe(cpu,at,size,user):
 trace.append({'address':hex(at),'this':hex(cpu.reg_read(UC_X86_REG_ECX)),'position':position})
 if at==0x4c6b10:cpu.emu_stop()
for at in [0x4de300,0x4d3390,0x4c6130,0x4c6b10]:cpu.hook_add(UC_HOOK_CODE,observe,begin=at,end=at)
oracle.scope_entries[MANAGER+0x200]=1
oracle.initial=bytes(memory)
try:
 steps=oracle.case([(0x49f050,0,[0x12345678,TEXDATA,len(tex),0,0,0,0])]);dictionary=steps[-1]['result']
 print('TEXTURES',len(resources),'entries',oracle.word(oracle.word(dictionary+12)+8),'GPU',dict(gpu_calls),'heap',hex(oracle.word(CONTEXT)),flush=True)
 sp=oracle.stack+0x18000;cpu.mem_write(sp,struct.pack('<7I',oracle.stop,NAME,dictionary,1,0,0,0));cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_FPCW,0x7f)
 cpu.emu_start(0x4b36d0,oracle.stop,count=15000000)
 assert cpu.reg_read(UC_X86_REG_EIP)==0x4c6b10,hex(cpu.reg_read(UC_X86_REG_EIP))
 header=int(next(t['this'] for t in trace if t['address']=='0x4de300'),16);table=oracle.word(header+0x18)
 report={'specimen_sha256':SHA256,'texture_sha256':hashlib.sha256(tex).hexdigest(),'scene_sha256':hashlib.sha256(scn).hexdigest(),
  'textures':len(resources),'materials':oracle.word(table+8),'scene_file_position':position,'trace':trace,'gpu_calls':dict(gpu_calls),'io_calls':dict(io_calls),'boundary':'0x4c6b10','playable':False}
 print(json.dumps(report,indent=2),flush=True)
 (ROOT/'local/analysis/level-scene-trace.json').write_text(json.dumps(report,indent=2)+'\n')
except Exception:
 print('STOP',hex(cpu.reg_read(UC_X86_REG_EIP)),'position',position,'trace',trace[-10:],'gpu',dict(gpu_calls),'io',dict(io_calls),flush=True);raise
