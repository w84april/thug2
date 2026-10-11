"""Original recursive script setup/call/cleanup/command/execution call chains."""
import hashlib,json,random,struct,subprocess
from collections import Counter
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EIP,UC_X86_REG_ESP
from specimen import ROOT,SHA256,load
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'script-execute.json';report_path.unlink(missing_ok=True)
prior=json.loads((out/'script-control-fixtures.json').read_text());memory=bytearray((out/prior['memory']).read_bytes());BASE=prior['base'];SIZE=0x800000
memory.extend(bytes(SIZE-len(memory)))
CONTEXT,ADAPTER,MANAGER=BASE+0x20,BASE+0x50,BASE+0x100
POOL,ENTRY,CACHE,CTABLE,CBUCKETS=BASE+0x1000,BASE+0x2000,BASE+0x5000,BASE+0x5100,BASE+0x5200
SCRIPT,PARAMS,ARGS,RETURNS,FRAMES,OWNER,OTHER=BASE+0x5800,BASE+0x5a00,BASE+0x5a10,BASE+0x5a20,BASE+0x6800,BASE+0x8000,BASE+0x8200
METHODS,COMPONENT,COMPONENT_METHODS,DESC,OBJECTS,OBJECT_TABLE,OBJECT_BUCKETS,EVENTS=BASE+0x8400,BASE+0x8500,BASE+0x8600,BASE+0x8700,BASE+0x9200,BASE+0x9220,BASE+0x9250,BASE+0x9300
TLS,LOCALE=BASE+0x9400,BASE+0x9600
BUCKETS,CALLBACK,DIAGNOSTICS,PRINT,PROGRAM,LOG,HEAP,DEBUG=BASE+0x10000,BASE+0x30000,BASE+0x35000,BASE+0x35f00,BASE+0x40000,BASE+0x60000,BASE+0x80000,BASE+0x200000
NATIVE,OBJECT_FN,MEMBER_FN,COMPONENT_FN=0x3f01000,0x3f01010,0x3f01020,0x3f01030
# The oracle's stop page is extended for modeled platform callbacks.
def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
def word(n):return struct.pack('<I',n&0xffffffff)
def name(n):return b'\x16'+word(n)
def number(n):return b'\x17'+word(n)
def floating(n):return b'\x1a'+word(n)
def text_token(text):return b'\x1b'+word(len(text)+1)+text+b'\0'
def assign(n,v):return name(n)+b'\x07'+v
def argument(n):return b'\x2d'+name(n)
def expression(v):return b'\x0e'+v+b'\x0f'
put(CONTEXT,'<8I',HEAP,BASE+0x100000,0,LOG,BASE,BASE+SIZE,SCRIPT+12,0)
memory[SCRIPT-BASE:SCRIPT-BASE+244]=bytes(244)
put(SCRIPT+12,'<3I',PROGRAM,PARAMS,ARGS);put(SCRIPT+0x2c,'<I',SCRIPT+0x1c);put(SCRIPT+0x94,'<I',SCRIPT+0x34);put(SCRIPT+0xc8,'<I',5)
memory[SCRIPT-BASE+0x34:SCRIPT-BASE+0x94]=b'\xad'*96
put(CALLBACK,'<8I',0,1,0,0,0,0,0,0);put(DIAGNOSTICS,'<I',0);put(PRINT,'<2I',DIAGNOSTICS,0)
for owner in [OWNER,OTHER]:
 memory[owner-BASE:owner-BASE+0x104]=bytes(0x104);put(owner,'<I',METHODS);put(owner+0x100,'<I',COMPONENT)
put(METHODS,'<4I',0,0,OBJECT_FN,MEMBER_FN);put(COMPONENT,'<5I',COMPONENT_METHODS,0x12345678,0,OWNER,0)
put(COMPONENT_METHODS+44,'<I',COMPONENT_FN);put(DESC,'<2I',0xabcdef01,0x57525413)
put(OBJECTS,'<5I',0,0,OBJECT_TABLE,OBJECT_TABLE,OBJECT_TABLE);put(OBJECT_TABLE,'<6I',2,OBJECT_BUCKETS,2,0xffffffff,0,0)
memory[OBJECT_BUCKETS-BASE:OBJECT_BUCKETS-BASE+48]=bytes(48)
put(OBJECT_BUCKETS+12,'<3I',1,OWNER,0);put(OBJECT_BUCKETS+24,'<3I',2,OTHER,0)
put(EVENTS,'<2I',BASE+0x9340,0)
for at in [TLS,LOCALE]:memory[at-BASE:at-BASE+256]=bytes(256)
put(TLS+0x64,'<I',LOCALE)
put(BASE+0x9700,'<3I',0,0,0)
memory[BUCKETS-BASE:BUCKETS-BASE+16388]=bytes(16388)
memory[DEBUG-BASE:DEBUG-BASE+65536*80]=bytes(65536*80)
# Original symbol values, with explicit runtime relocation for native pointers.
symbol_cursor=BASE+0xa000
symbols={};native_slots=[]
def symbol(n,kind,value):
 global symbol_cursor
 at=symbol_cursor;symbol_cursor+=20;bucket=BUCKETS+(n&0xfff)*4;previous=struct.unpack_from('<I',memory,bucket-BASE)[0]
 put(at,'<BBHIIII',0x91,kind,0x9876,n,0,value,previous);put(bucket,'<I',at);symbols[n]=at
 if kind==8:native_slots.append(at+12)
 return at
N,M,D,F=0xabc01001,0xabc01002,0xabc01003,0xabc01004
symbol(N,8,NATIVE);symbol(M,9,0);symbol(D,9,DESC);symbol(F,1,123)
symbol(0xabc01005,13,N)
# Pre-cached programs are real bytecode, and all cache acquire/release code runs.
programs={5:b'\x01\x24',6:b'\x01'+assign(101,number(17))+b'\x01\x29'+assign(102,number(29))+b'\x01\x24',
 7:b'\x01'+name(6)+b'\x01\x29'+argument(102)+b'\x01\x24',8:b'\x01'+name(N)+b'\x01\x24'}
program_addresses={};cache_patches=[]
put(CACHE+20,'<3IB',CTABLE,0,0,0);put(CTABLE,'<3I',4,CBUCKETS,len(programs));memory[CBUCKETS-BASE:CBUCKETS-BASE+192]=bytes(192)
for i,(n,body) in enumerate(programs.items()):
 p=PROGRAM+0x1000+i*0x1000;program_addresses[n]=p;memory[p-BASE:p-BASE+len(body)]=body
 e=ENTRY+i*20;put(e,'<5I',n,p,1,0,0);put(CBUCKETS+(n&15)*12,'<3I',n,e,0)
 header=BASE+0xb000+i*0x100;put(header,'<3I',0,len(body),len(body));memory[header-BASE+12:header-BASE+12+len(body)]=body;symbol(n,7,header)
put(POOL+16,'<2I',len(programs),ENTRY+len(programs)*20)
for i in range(len(programs),100):put(ENTRY+i*20,'<I',ENTRY+(i+1)*20 if i<99 else 0)
# Arguments include both explicit and anonymous command-name substitutions.
ARG0,ARG1=BASE+0xc000,BASE+0xc010
put(ARGS,'<2I',0xadadadad,ARG0);put(ARG0,'<BBHIII',27,0x75,0x9876,0,N,ARG1);put(ARG1,'<BBHIII',27,0x75,0x9876,99,M,0)
# Readable-name buckets include collisions and a completely full ten-name group.
for i in range(10):
 text=BASE+0xc100+i*32;data=('debug name '+str(i)).encode()+b'\0';memory[text-BASE:text-BASE+len(data)]=data
 put(DEBUG+0x1234*80+i*8,'<2I',(i<<16)|0x1234,text)
memory[0xcf00:0xcf00+12]=b'executor.qb\0'
initial=bytes(memory);(out/'script-execute-memory.bin').write_bytes(initial)
globals_=prior['globals'][:];defaults=prior['cases'][0]['globals'][:]
existing={g[1] for g in globals_}
event=json.loads((out/'script-events-fixtures.json').read_text())
for g,v in zip(event['globals'],event['cases'][0]['globals']):
 if g[1] not in existing:globals_.append(g);defaults.append(v);existing.add(g[1])
for export,address,width,value in [('thug_script_debug_enabled',0x7cefac,1,0),('thug_script_debug_names',0x6f232c,4,DEBUG),('thug_network_state',0x7cce14,4,BASE+0x9700)]:
 globals_.append([export,address,width]);defaults.append(value)
for i in range(20):globals_.append(['thug_script_unknown_name',0x6f22c8+i,1,i]);defaults.append(0xa5)
state=json.loads((out/'script-state-fixtures.json').read_text())
for g,v in zip(state['globals'],state['cases'][0]['globals']):
 if g[1] not in {entry[1] for entry in globals_}:globals_.append(g);defaults.append(v)
index={g[1]:i for i,g in enumerate(globals_)}
defaults[index[0x6f0fc0]]=OBJECTS;defaults[index[0x6f3530]]=0;defaults[index[0x6f3558]]=CACHE
functions={}
def bind(at,n,argc=0,this=True,heap=True,result='void',diag=False):
 f={'name':'thug_script_'+n,'this':this,'memory':heap,'result':result,'cleanup':argc*4 if this else 0}
 if diag:f.update(stack_args=list(range(argc)),diagnostics=True)
 functions[hex(at)]=f
bind(0x46d0c0,'debug_name',1,False,False,'word');bind(0x46d110,'name_text',1,False,False,'word');functions['0x46d110']['pointer_result']=True
bind(0x460ad0,'find_object',1,False,False,'word');bind(0x472950,'read_parameters');bind(0x4729e0,'read_name',heap=False,result='word')
bind(0x472980,'dispatch_descriptor',4,False,False,'byte');bind(0x4731a0,'call_descriptor',2,heap=False,result='byte');bind(0x4731e0,'call_member',2,heap=False,result='byte')
for at,n,argc,result in [(0x473880,'run_deferred',0,'void'),(0x473a80,'cleanup',0,'void'),(0x474540,'setup',4,'void'),(0x4748e0,'push_call',5,'void'),
 (0x475750,'run_immediate',2,'void'),(0x474b40,'invoke_command',0,'byte'),(0x475050,'conditional',0,'void'),(0x4750b0,'execute',0,'word')]:bind(at,n,argc,result=result,diag=True)
functions['0x46fe40']=json.loads((out/'script-cache-fixtures.json').read_text())['functions']['0x46fe40']
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,MANAGER,globals_,defaults,functions,event_limit=(HEAP-LOG)//48,instruction_limit=50000000,
 observe=[int(k,16) for k in functions]+[0x475e80,0x475d60,0x473e70,0x473010,0x401c30,0x6234fe,0x470f30,0x4739d0],scope_entries={BASE+0x6000:1,MANAGER+0x300:2})
oracle.cpu.mem_map(0x3f01000,4096)
for at in [0x6f362c,0x6f3634,0x6f3638,0x6f2578,0x6f2580,0x6f2584]:oracle.cpu.mem_write(at,bytes(4))
# Model initialized Windows TLS/last-error only. Original CRT sprintf executes.
os_calls=Counter();last_error=0x12345678
GET_ERROR,GET_TLS,SET_ERROR=oracle.stop+0x100,oracle.stop+0x110,oracle.stop+0x120
for slot,target in [(0x6450d4,GET_ERROR),(0x7db10c,GET_TLS),(0x64516c,SET_ERROR)]:oracle.setword(slot,target)
oracle.setword(0x68ef14,7);oracle.setword(0x68ecfc,LOCALE)
for at,n in [(GET_ERROR,0),(GET_TLS,4),(SET_ERROR,4)]:oracle.cpu.mem_write(at,b'\xc2'+struct.pack('<H',n))
def os_service(cpu,address,size,user):
 global last_error
 sp=cpu.reg_read(UC_X86_REG_ESP)
 if address==GET_ERROR:cpu.reg_write(UC_X86_REG_EAX,last_error);os_calls['GetLastError']+=1
 elif address==GET_TLS:assert oracle.word(sp+4)==7;cpu.reg_write(UC_X86_REG_EAX,TLS);os_calls['TLS_read']+=1
 else:last_error=oracle.word(sp+4);os_calls['SetLastError']+=1
for at in [GET_ERROR,GET_TLS,SET_ERROR]:oracle.cpu.hook_add(UC_HOOK_CODE,os_service,begin=at,end=at)
pe=load();fmt='WARNING: script %s not found, ignoring in default level.\n';data=pe.get_memory_mapped_image();fmt_address=0x400000+data.index(fmt.encode()+b'\0')
pointer_symbols=prior['pointer_symbols']+[[fmt_address,'thug_script_missing_format',fmt]]
def callback(cpu,address,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP)
 if address==0x401c30:
  count=oracle.word(DIAGNOSTICS);text=oracle.word(sp+8);raw=bytes(cpu.mem_read(text,128)).split(b'\0',1)[0];assert len(raw)<24
  cpu.mem_write(DIAGNOSTICS+16+count*32,struct.pack('<2I',oracle.word(sp+4),text)+raw.ljust(24,b'\0'));oracle.setword(DIAGNOSTICS,count+1);cleanup=0;result=0xffffffff
 else:
  kind=[NATIVE,OBJECT_FN,MEMBER_FN,COMPONENT_FN].index(address);owner=cpu.reg_read(UC_X86_REG_ECX) if kind else 0
  n=oracle.word(sp+4) if kind else 0;params=oracle.word(sp+8 if kind else sp+4);script=oracle.word(sp+12 if kind else sp+8)
  first=oracle.word(params+4) if params else 0;count=oracle.word(CALLBACK)
  assert count<400
  cpu.mem_write(CALLBACK+32+count*40,struct.pack('<10I',kind,owner,n,params,script,first,oracle.word(first+4) if first else 0,oracle.word(first+8) if first else 0,oracle.word(script+12),oracle.word(script+200)))
  oracle.setword(CALLBACK,count+1);mode=oracle.word(CALLBACK+8);v=oracle.word(CALLBACK+12)
  if mode==1:oracle.setword(script+164,1);oracle.setword(script+152,v)
  if mode==2:oracle.setword(script+12,0)
  if mode==3 and first:oracle.setword(first+8,oracle.word(first+8)^v)
  if mode==4:oracle.setword(script+232,v)
  if mode==5:oracle.setword(script+12,v)
  cleanup=12 if kind else 0;result=oracle.word(CALLBACK+4)
 cpu.reg_write(UC_X86_REG_EAX,result);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4+cleanup)
for at in [NATIVE,OBJECT_FN,MEMBER_FN,COMPONENT_FN,0x401c30]:oracle.cpu.hook_add(UC_HOOK_CODE,callback,begin=at,end=at)
labels=[];pointer_fields=set(native_slots)
def call(at,*args,this=SCRIPT):
 return (at,this,list(args)+([PRINT] if functions[hex(at)].get('diagnostics') else []))
def case(calls,patches=(),changes=None,label='synthetic'):
 labels.append(label)
 stages=oracle.case(calls,patches,{index[k]:v for k,v in (changes or {}).items()})
 assert last_error==0x12345678
 previous_commands=0;previous_diagnostics=0
 for step in stages:
  commands=previous_commands;diagnostic_count=previous_diagnostics
  for at,data in step['outputs']:
   if at==CALLBACK:commands=int.from_bytes(bytes.fromhex(data),'little')
   if at==DIAGNOSTICS:diagnostic_count=int.from_bytes(bytes.fromhex(data),'little')
  step['callbacks']=commands-previous_commands+diagnostic_count-previous_diagnostics
  previous_commands=commands;previous_diagnostics=diagnostic_count
  step['global_float_indices']=[]
  for base in [0x6f2348,0x6f2568,*range(0x6f2370,0x6f24b0,16)]:
   if step['globals'][index[base]]&0xfe==4:step['global_float_indices'].append(index[base+8])
 return stages
def stream(at,code,extra=(),changes=None,label='synthetic'):
 return case([call(at)],[[PROGRAM,code.hex()],*extra],changes,label)
# Debug-name collision bounds and exact shared formatting bytes.
for enabled in [0,1]:
 for n in [0,1,0xffffffff,0x80000000,0x1234,0x91234,0xa1234,0x12345678]:
  case([call(0x46d0c0,n,this=0),call(0x46d110,n,this=0)],changes={0x7cefac:enabled})
for n in [0,1,2,3,0xffffffff]:case([call(0x460ad0,n,this=0)])
for code in [name(N),b'\x2c',argument(99),argument(100),b'\x01',b'\x29']:
 stream(0x4729e0,code)
for code in [assign(1,number(7)),assign(2,text_token(b'parameter')),argument(99),b'\x2c']:
 stream(0x472950,code+b'\x01')
# Virtual dispatch return width, owner fallback, component selection and args.
for result in [0,1,255,256,257,0xffffffff]:
 for component in [0x57525413,0xada4e74,0x12345678]:
  patches=[patch(CALLBACK+4,'<I',result),patch(DESC+4,'<I',component)]
  case([call(0x472980,DESC,PARAMS,OWNER,SCRIPT,this=0)],patches)
  for owner in [0,OWNER,OTHER]:
   for fallback in [0,OWNER]:
    extras=patches+[patch(SCRIPT+0xbc,'<I',fallback)]
    case([call(0x4731a0,DESC,owner),call(0x4731e0,0x1234,owner)],extras)
# Direct command invocation: native/member/descriptor, aliases, expressions,
# assignments, missing names and object-qualified commands.
commands=[name(N),name(M),name(D),name(F),name(0xabc01005),name(0xeeeeeeee),b'\x2c',argument(99),
 expression(number(0)),expression(number(256)),expression(floating(0x80000000)),expression(name(N)),
 assign(111,number(7)),assign(111,text_token(b'owned')),assign(111,expression(number(2)+b'\x0b'+number(3))),assign(111,b'\x04'),
 name(1)+b'\x42'+name(M),name(2)+b'\x42'+name(D),name(3)+b'\x42'+name(M),name(1)+b'\x42'+b'\x44'+word(M),
 name(1)+b'\x42'+name(6),name(6),name(7),b'\x43'+word(NATIVE),b'\x44'+word(M),b'\x46'+word(DESC)]
pointer_fields.add(PROGRAM+1)
for code in commands:
 for owner in [0,OWNER]:
  for result in [0,256,257]:
   stream(0x474b40,code+b'\x01\x24',[patch(SCRIPT+0xbc,'<I',owner),patch(CALLBACK+4,'<I',result)])
# A missing object member is defined only for the default-level script.
stream(0x474b40,name(1)+b'\x42'+name(0xeeeeeeee)+b'\x01',[patch(SCRIPT+0xc8,'<I',0xfb11e6cd)])
for inv in [b'',b'\x39']:
 for result in [0,1,256,257]:
  for mode in [0,2,5]:
   code=b'\x47'+struct.pack('<H',40)+inv+name(N)+b'\x01'+bytes(40)
   stream(0x475050,code,[patch(CALLBACK+4,'<3I',result,mode,PROGRAM+30)])
# Complete setup, nested calls and cleanup, including aliased argument snapshots.
for program in [0,program_addresses[5],program_addresses[6]]:
 for n in [5,6,0xeeeeeeee]:
  for args in [0,PARAMS,ARGS,RETURNS]:
   for owner in [0,OWNER]:
    case([call(0x474540,n,program,args,owner),call(0x473a80)],label='setup and cleanup')
for depth in [0,1,2,3,15]:
 for wait in [0,1,3,15,0x12345678]:
  patches=[patch(SCRIPT+0x30,'<I',depth),patch(SCRIPT+0x94,'<I',SCRIPT+0x34 if depth<=2 else FRAMES),patch(SCRIPT+0xa4,'<I',wait),patch(SCRIPT+0xa0,'<I',0x7f812345)]
  case([call(0x4748e0,6,program_addresses[6],PARAMS,OTHER,0x101)],patches,label='call frame save')
for active in [0,PROGRAM]:
 for n in [5,6,7]:
  case([call(0x475750,n,RETURNS)],[patch(SCRIPT+12,'<I',active)],label='immediate nested execution')
# The normal executor reaches original return values and cache state transitions.
bodies=[b'\x24',b'\x01\x02'+word(123)+b'\x28\x24',assign(111,number(9))+b'\x01\x29'+assign(112,text_token(b'out'))+b'\x01\x24',
 name(6)+b'\x01\x24',name(7)+b'\x01\x24',b'\x20'+assign(111,number(9))+b'\x01\x21'+number(3)+b'\x01\x24',
 b'\x20\x20\x22\x21'+number(5)+b'\x01\x22\x21'+number(2)+b'\x01\x24',b'\x49\x02\x00\x24',b'\x48\x02\x00\x24']
for body in bodies:
 for flags in [0,1,2,255]:stream(0x4750b0,body,[patch(SCRIPT+0xb4,'<B',flags)],label='complete bytecode execution')
for mode in [0,1,2,3,4]:
 code=name(N)+b'\x01\x24'
 extra=[patch(CALLBACK+8,'<2I',mode,5 if mode==4 else 2)]
 case([call(0x4750b0)]*4,[[PROGRAM,code.hex()],*extra],label='native callback and resume')
for deferred in [5,6,7]:
 for active in [0,PROGRAM]:
  for at in [0x473880,0x473a80,0x4750b0]:
   case([call(at)],[[PROGRAM,b'\x24'.hex()],patch(SCRIPT+12,'<I',active),patch(SCRIPT+0xe8,'<I',deferred)],label='deferred script execution')
# Suspended call frames own independent arguments and deferred script names.
for depth in [1,2,3,8]:
 patches=[patch(SCRIPT+0x30,'<I',depth),patch(SCRIPT+0x94,'<I',FRAMES)]
 for i in range(depth):patches.append(patch(FRAMES+i*48,'<12I',5,0,PROGRAM,0,0,6 if i&1 else 5,0,0,0,0,0,0))
 case([call(0x473880),call(0x473a80)],patches,label='deferred suspended callers')
# Execute compiled switch and if/else branches, including their exit jumps.
for selector in [1,2,3]:
 code=bytearray(b'\x3c'+number(selector)+b'\x01');headers=[];jumps=[]
 for v in [1,2]:
  headers.append(len(code));code+=b'\x3e\x49\0\0'+number(v)+b'\x01'+assign(111,number(v))+b'\x01'
  jumps.append(len(code));code+=b'\x49\0\0'
 default=len(code);code+=b'\x3f\x49\0\0'+assign(111,number(3))+b'\x01';end=len(code);code+=b'\x3d\x24'
 for i,h in enumerate(headers):struct.pack_into('<H',code,h+2,(headers[i+1] if i+1<len(headers) else default)-h-2)
 for j in jumps:struct.pack_into('<H',code,j+1,end-j-1)
 stream(0x4750b0,bytes(code),label='switch complete execution')
for condition in [0,1]:
 code=bytearray(b'\x47\0\0'+expression(number(condition))+b'\x01'+assign(111,number(1))+b'\x01')
 jump=len(code);code+=b'\x48\0\0';otherwise=len(code);code+=assign(111,number(2))+b'\x01';end=len(code);code+=b'\x28\x24'
 struct.pack_into('<H',code,1,otherwise-1);struct.pack_into('<H',code,jump+1,end-jump-1)
 stream(0x4750b0,bytes(code),label='if else complete execution')
stream(0x4750b0,b'\x2e'+word(0)+b'\x24',label='long jump complete execution')
# Resume outcomes include both waiting return codes and real timer/frame updates.
for wait in [1,2,3,4,11,12,15]:
 for remaining in [0,0x3dcccccd,0x453b8000]:
  for waited in [0,1]:
   case([call(0x4750b0)]*4,[[PROGRAM,b'\x24'.hex()],patch(SCRIPT+0xa4,'<I',wait),patch(SCRIPT+0xa0,'<I',remaining),patch(SCRIPT+0x98,'<IB',2,waited)],label='wait and resume result codes')
# Save sixteen real owned call frames, then dispose the whole stack.
case([call(0x4748e0,6,program_addresses[6],PARAMS,OTHER,i&1) for i in range(16)]+[call(0x473a80)],label='full call stack spill and cleanup')
# Nested bytecode calls reach the third suspension and spill the inline stack.
case([call(0x4750b0),call(0x473a80)],[[PROGRAM,(name(6)+b'\x01\x24').hex()],
 [program_addresses[6],(b'\x01'+name(7)+b'\x01\x24').hex()],
 [program_addresses[7],(b'\x01'+name(8)+b'\x01\x24').hex()]],label='nested execution through stack spill')
# Registration compresses bytecode; setup then acquires, decodes and executes it.
for repeats in [1,20]:
 body=b'\x01'+(assign(111,expression(number(2)+b'\x0b'+number(3)))+b'\x01')*repeats+b'\x29'+assign(112,number(77))+b'\x01\x24'
 case([call(0x46fe40,PROGRAM,len(body),0x55,0x12345678,BASE+0xcf00,this=0),call(0x474540,0x55,0,RETURNS,OWNER),call(0x4750b0),call(0x473a80)],
 [[PROGRAM,body.hex()]],label='register decompress setup execute cleanup')
# All method fields and diagnostics pointer snapshots are declared relocations.
pointer_fields.update([METHODS+8,METHODS+12,COMPONENT_METHODS+44])
for i in range(32):pointer_fields.update([DIAGNOSTICS+16+i*32,DIAGNOSTICS+20+i*32])
for i in range((HEAP-LOG)//48):pointer_fields.update([LOG+i*48+j for j in [16,20,24,28]])
scope='Sixteen original routines: debug-name lookup/formatting, object lookup, command name/parameter parsing, native/member/component dispatch, recursive setup, call-frame spill/save, deferred scripts, cleanup, conditionals and the complete bytecode executor. All concrete script/cache/parser/event/ownership callees execute; heap/scopes, formatted output and deliberately configured native/virtual commands are instrumented boundaries. Tests exercise registration/compression through cache decoding and execution, nested calls through stack spill, sixteen-frame cleanup, loop control, return values, both wait result codes/resume, owner links, aliases and error paths, with full memory/global/heap comparison. Native gameplay handlers, script scheduling/startup and level rendering are not provided by this executor.'
fixture={'base':BASE,'memory':'script-execute-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],
 'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'command_and_diagnostic_callbacks','pointer_symbols':pointer_symbols,
 'pointer_exports':[[0x6f22c8,'thug_script_unknown_name']],'pointer_fields':sorted(pointer_fields),'pointer_globals':prior['pointer_globals'],
 'native_callbacks':[{'module':'script-execute-callbacks.wasm','export':n,'original':a} for a,n in [(NATIVE,'fixture_execute_native'),(OBJECT_FN,'fixture_execute_object'),(MEMBER_FN,'fixture_execute_member'),(COMPONENT_FN,'fixture_execute_component')]]+
 [{'module':'script-execute-callbacks.wasm','export':'fixture_execute_print','slots':[PRINT+4]}]}
path=out/'script-execute-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
print('x86 complete:',len(oracle.cases),'cases',sum(oracle.counts.values()),'calls',flush=True)
sdk=ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang';adapter=out/'script-execute-callbacks.wasm'
subprocess.run([str(sdk),'--target=wasm32-unknown-unknown','-O2','-nostdlib','-Wl,--no-entry,--import-memory,--export-all,--global-base=58720256',str(ROOT/'tools/script_execute_callbacks.c'),'-o',str(adapter)],check=True)
subprocess.run(['node',str(ROOT/'tools/verify_script_execute_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'os_calls':dict(os_calls),'scope':scope,
 'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
 'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/'script-execute-memory.bin',adapter,out/'script-values-memory.wasm']},
 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
