"""Original font metrics, button labels and text helpers through real CRT paths."""
import hashlib,json,random,struct,subprocess,zlib
from collections import Counter
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EAX
from specimen import ROOT,SHA256
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'font-text.json';report_path.unlink(missing_ok=True)
BASE,SIZE=0x1800000,0x60000
PLATFORM,CONTEXT,LOG,LOCALE,MANAGER,BUCKETS,UI,PEER,FONT,METRICS,BUTTON,GLYPHS,BGLYPHS,INPUT,OUTPUT,CURSOR,WIDGET=[BASE+x for x in [0x100,0x1000,0x2000,0x9000,0x9200,0x9300,0x9500,0x9800,0xa000,0xa200,0xa600,0xb000,0xd000,0x20000,0x40000,0x41000,0x42000]]
STOP,TLS,CALLBACK=0x3f00000,0x3f00800,0x3f00100
ADAPTER,HEAP_CONTEXT,ALLOCATOR,HEAP_LOG,HEAP=BASE+0x300,BASE+0x500,BASE+0x600,BASE+0x44000,BASE+0x50000
memory=bytearray(b'\xad'*SIZE)
def put(at,fmt,*v):struct.pack_into(fmt,memory,at-BASE,*v)
def patch(at,fmt,*v):return [at,struct.pack(fmt,*v).hex()]
def raw(at,data):return [at,bytes(data).hex()]
def crc(s):return (zlib.crc32(s.encode())^0xffffffff)&0xffffffff
def bits(f):return int.from_bytes(struct.pack('<f',f),'little')
for at,n in [(CONTEXT,64),(LOCALE,256),(MANAGER,128),(BUCKETS,128),(UI,768)]:memory[at-BASE:at-BASE+n]=bytes(n)
put(PLATFORM,'<3I',CALLBACK,CALLBACK+16,CALLBACK+32);put(CONTEXT,'<5I',0,0,0x12345678,0,13)
put(LOCALE+4,'<I',1252);put(MANAGER,'<4I',0,0,MANAGER+32,MANAGER+64)
put(MANAGER+32,'<2I',0,BUCKETS);put(MANAGER+64,'<2I',0,BUCKETS+64)
for i in range(3):put(UI+i*256+0x14,'<I',0xabc+i)
put(PEER,'<3I',UI,0,0);put(FONT,'<3I',0x64a328,0xaabbccdd,METRICS)
for at,glyphs,seed in [(METRICS,GLYPHS,1),(BUTTON,BGLYPHS,3)]:
 put(at,'<3I',39,0x12345678,glyphs)
 for i in range(296):put(at+12+i,'<B',(i*13+seed)&255)
 put(at+0x134,'<hh',-2,5)
 for i in range(256):put(glyphs+i*24+16,'<H',(i*113+seed*37)&65535)
put(CURSOR,'<I',INPUT)
put(ADAPTER,'<4I',HEAP_CONTEXT,0,0,0)
put(HEAP_CONTEXT,'<8I',HEAP,BASE+SIZE,0,HEAP_LOG,BASE,BASE+SIZE,WIDGET+0x178,0)
put(ALLOCATOR+0x11c,'<I',ALLOCATOR+0x200)
initial=bytes(memory)
globals_,defaults,index=[],[],{}
def glob(name,at,value=0,width=4,offset=0):
 index[at]=len(globals_);globals_.append([name,at,width,offset]);defaults.append(value&((1<<(width*8))-1))
glob('thug_text_platform',STOP+0x40,PLATFORM);glob('thug_text_locale',0x68ecfc,LOCALE)
glob('thug_text_mb_max',0x68f4f4,1);glob('thug_math_errno',TLS+8,0x76543210)
glob('thug_button_font',0x780fdc,BUTTON);glob('thug_object_lookup_manager',0x6f0fc0,MANAGER)
glob('thug_key_menu_override',0x7d6a2c,0,1);glob('thug_text_language',0x7cefa0,0)
for i in range(4):glob('thug_key_label_flags',0x7ce46c+i,0,1,i)
for i in range(11):glob('thug_key_bindings',0x7d6790+i*4,70+i,4,i*4)
for i in range(32):glob('thug_button_glyphs',0x6fa808+i,ord('0')+i if i<10 else ord('a')+i-10,1,i)
def block(name,at,data):
 for i in range(0,len(data)-len(data)%4,4):glob(name,at+i,int.from_bytes(data[i:i+4],'little'),4,i)
 for i in range(len(data)-len(data)%4,len(data)):glob(name,at+i,data[i],1,i)
names=bytearray()
for i in range(-1,256):names.extend(('unbound' if i<0 else 'K'+str(i)).encode('utf-16le').ljust(30,b'\0'))
block('thug_key_name_storage',0x7d42f8-30,names)
block('thug_key_label_text',0x7d19d8,b'old output\0'.ljust(256,b'\xa5'))
block('thug_key_label_converted',0x7d1ad8,b'old converted\0'.ljust(256,b'\xa5'))
block('thug_integer_text',0x690fa4,b'\xa5'*32)
exports=[[0x64a328,'thug_font_methods'],[0x7d19d8,'thug_key_label_text'],[0x7d1ad8,'thug_key_label_converted'],[0x690fa4,'thug_integer_text']]
exports += [[0x7d42f8+i*30,'thug_key_name_storage',(i+1)*30] for i in range(-1,256)]
functions={}
def bind(at,name,argc,this=False,result='word',cleanup=None):functions[hex(at)]={'name':name,'this':this,'result':result,'cleanup':(4*argc if this else 0) if cleanup is None else cleanup}
bind(0x402170,'thug_text_word',2);bind(0x402200,'thug_text_integer',1);bind(0x5f3120,'thug_key_name',1)
bind(0x5bcd50,'thug_key_label',1);bind(0x4b2160,'thug_ui_font_name',0,True)
bind(0x4cecb0,'thug_font_metrics_measure',3,True,'void');bind(0x4b3d10,'thug_font_measure_concrete',3,True,'void');bind(0x48d060,'thug_font_measure',3,True,'void')
bind(0x6254eb,'thug_text_convert_wide',4);bind(0x62569c,'thug_text_wcstombs',3)
bind(0x4a92d0,'thug_ui_set_size',3,True,'void');bind(0x4a94a0,'thug_ui_set_scale',4,True,'void')
for a in [0x4a92d0,0x4a94a0]:functions[hex(a)]['float_args']=[0,1]
bind(0x4af8c0,'thug_ui_set_text',1,True,'void');functions['0x4af8c0']['memory']=True
for a in [0x402200,0x5f3120,0x5bcd50]:functions[hex(a)]['pointer_result']=True
observe=[int(k,16) for k in functions]+[0x4020e0,0x48d6a0,0x4aae20,0x4a8f40,0x4637c0,0x4637e0,0x6234fe,0x462120]
oracle=ScriptHeapOracle(initial,BASE,HEAP_CONTEXT,ALLOCATOR,globals_,defaults,functions,observe=observe,instruction_limit=10000000,scope_entries={ALLOCATOR+0x200:6},event_limit=(HEAP-HEAP_LOG)//48)
oracle.cpu.mem_write(TLS,bytes(256));oracle.setword(TLS+0x64,LOCALE);oracle.setword(0x68ef14,7)
GET_ERROR,GET_TLS,SET_ERROR=STOP+0x140,STOP+0x150,STOP+0x160
for slot,target in [(0x645148,CALLBACK),(0x64520c,CALLBACK+32),(0x6450d4,GET_ERROR),(0x7db10c,GET_TLS),(0x64516c,SET_ERROR)]:oracle.setword(slot,target)
for at,n in [(CALLBACK,32),(CALLBACK+16,0),(CALLBACK+32,8),(GET_ERROR,0),(GET_TLS,4),(SET_ERROR,4)]:oracle.cpu.mem_write(at,b'\xc2'+struct.pack('<H',n))
os_calls=Counter()
def record(kind,values=()):
 n=oracle.word(CONTEXT);assert n<400
 at=LOG+n*64;oracle.setword(CONTEXT,n+1);oracle.cpu.mem_write(at,struct.pack('<16I',kind,*values,*([0]*(15-len(values)))))
 return at
def os_service(cpu,address,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);ret=oracle.word(sp)
 if address==GET_TLS:assert oracle.word(sp+4)==7;cpu.reg_write(UC_X86_REG_EAX,TLS);os_calls['TLS_read']+=1;return
 if address==SET_ERROR:oracle.setword(CONTEXT+8,oracle.word(sp+4));os_calls['SetLastError']+=1;return
 if address in [GET_ERROR,CALLBACK+16]:
  value=oracle.word(CONTEXT+8);cpu.reg_write(UC_X86_REG_EAX,value);os_calls['GetLastError']+=1
  if 0x6254eb<=ret<0x62569c or address==CALLBACK+16:record(1,[value])
  return
 if address==CALLBACK+32:
  code,mode=oracle.word(sp+4),oracle.word(sp+8);result=((code+256)&0xffffffff) if mode==1 else ((code*7+oracle.word(CONTEXT+16))&255)|0x80000000
  record(2,[code,mode,result]);cpu.reg_write(UC_X86_REG_EAX,result);os_calls['MapVirtualKeyA']+=1;return
 cp,flags,ptr,count,dest,capacity,fallback,used=struct.unpack('<8I',cpu.mem_read(sp+4,32))
 chars=[];h=0
 while count&0x80000000 or len(chars)<count:
  c=int.from_bytes(cpu.mem_read(ptr+2*len(chars),2),'little');chars.append(c);h=(h*33+c)&0xffffffff
  if count&0x80000000 and not c:break
 mode=oracle.word(CONTEXT+4);data=bytearray();substituted=0
 for c in chars:
  if mode==1 and c>=128:data.extend([(0xc0|(c>>6))&255,0x80|(c&63)])
  else:data.append(c if c<=255 else ord('?'));substituted|=c>255
 oracle.setword(used,substituted);result=len(data)
 if oracle.word(CONTEXT+12):result=0;oracle.setword(CONTEXT+8,87)
 elif dest and (capacity&0x80000000 or capacity<len(data)):result=0;oracle.setword(CONTEXT+8,122)
 elif dest:cpu.mem_write(dest,bytes(data))
 record(0,[cp,flags,count,int(bool(dest)),capacity,int(bool(fallback)),int(bool(used)),h,len(chars),result,substituted,oracle.word(CONTEXT+8)])
 cpu.reg_write(UC_X86_REG_EAX,result);os_calls['WideCharToMultiByte']+=1
for at in [CALLBACK,CALLBACK+16,CALLBACK+32,GET_ERROR,GET_TLS,SET_ERROR]:oracle.cpu.hook_add(UC_HOOK_CODE,os_service,begin=at,end=at)
labels=[]
def call(at,this=0,args=()):return at,this,[v&0xffffffff for v in args]
def case(calls,patches=(),changes=None,label='font/text',float_fields=None):
 stages=oracle.case(calls,patches,{index[k]:v for k,v in (changes or {}).items()});labels.append(label)
 last=0
 for s in stages:
  if float_fields:s['float_fields']=float_fields
  # Count only explicit conversion/mapping OS calls; TLS housekeeping is separate.
  for at,data in s['outputs']:
   if at==CONTEXT:count=int.from_bytes(bytes.fromhex(data),'little');s['callbacks']=count-last;last=count
  merged=[]
  for at,data in s['outputs']:
   if merged and merged[-1][0]+len(merged[-1][1])//2==at:merged[-1][1]+=data
   else:merged.append([at,data])
  s['outputs']=merged
 if len(labels)%100==0:print('Original font/text cases:',len(labels),flush=True)
 return stages
def change_bytes(changes,at,data):
 # The wide-name array starts at an address aligned to two rather than four.
 covered=0
 for _,address,width,*_ in globals_:
  if address+width<=at or address>=at+len(data):continue
  old=bytearray((changes.get(address,defaults[index[address]])).to_bytes(width,'little'))
  for j in range(width):
   if at<=address+j<at+len(data):old[j]=data[address+j-at];covered+=1
  changes[address]=int.from_bytes(old,'little')
 assert covered==len(data)

# Word boundaries, escapes, in-place compaction and repeatedly updated cursors.
texts=[b'',b' ',b'one two three',b'  lead',b'last',b'one\\_two x',b'a\\nb',b'\\n',b'\\N',b'\\\\x',b'\\b0 test',b'abc\0tail',b'\\\0X\0',bytes(range(1,32))+b' end']
rng=random.Random(0x402170)
texts += [bytes(rng.choice(b'abcxyz _n\\') for _ in range(rng.randrange(1,65)))+b' end' for _ in range(64)]
for text in texts:
 for inplace in [False,True]:
  dst=INPUT if inplace else OUTPUT
  case([call(0x402170,args=[dst,CURSOR])]*3,[raw(INPUT,(text+b'\0').ljust(128,b'\0')),patch(CURSOR,'<I',INPUT)],label='word boundary and aliased input/output')
values=[0,1,-1,9,10,99,100,999,1000,9999,10000,999999,1000000,2147483647,-2147483648,-2147483647]+[rng.randrange(-2**31,2**31) for _ in range(16)]
for language in [0,3,4,5,6,7,0xffffffff]:
 for value in values:case([call(0x402200,args=[value])]*2,changes={0x7cefa0:language},label='signed decimal grouping and locale separators')
for code in [0xffffffff,*range(256),0x80000000,0x80000001]:case([call(0x5f3120,args=[code])],label='wide key table raw address and wrap')
for value in [0,1,0xffffffff,0x80000000]:case([call(0x4b2160,WIDGET)],[patch(WIDGET+0x178,'<I',value)],label='font name accessor')

# Every CRT branch, errors after partial output, length-only queries, and
# multibyte fallback after insufficient output space, using real original CRT.
wide=[[0],[65,66,0],[65,255,0],[65,256,66,0],[0x80,0x7ff,0],[0xd800,0],[65]*20+[0]]
for locale in [0,1]:
 for mb in [1,2]:
  for mode in [0,1]:
   for fail in [0,1]:
    for chars in wide:
     for capacity in [0,1,2,3,8,32]:
      p=[patch(LOCALE+0x14,'<I',locale),patch(CONTEXT+4,'<3I',mode,0x12345678,fail),raw(INPUT,struct.pack('<'+'H'*len(chars),*chars))]
      calls=[call(0x6254eb,args=[LOCALE,OUTPUT,INPUT,capacity]),call(0x62569c,args=[OUTPUT+64,INPUT,capacity]),call(0x6254eb,args=[LOCALE,0,INPUT,capacity])]
      case(calls,p,{0x68f4f4:mb},'wide conversion locale/limit/error behavior')

def widgets(piece=0,selected=0,parent_hidden=False):
 p=[patch(UI+4,'<I',PEER),patch(UI+256+4,'<I',0)]
 # One hash bucket, with both IDs as a genuine collision chain.
 p += [patch(MANAGER+4,'<I',0),patch(BUCKETS,'<3I',crc('select_skater_hmenu'),UI if selected else 0,BUCKETS+32),patch(BUCKETS+32,'<3I',crc('piece_menu_hmenu'),UI+256 if piece else 0,0)]
 p += [patch(UI+8,'<I',0x400000 if selected==2 else 0),patch(UI+256+8,'<I',0x400000 if piece==2 else 0),patch(UI+256+0x4c,'<I',UI+512 if parent_hidden else 0),patch(UI+512+8,'<I',0x400000)]
 return p
states=[(a,b,c,0,0,0,False) for a in [0,1] for b in [0,1] for c in [0,1]]
states += [(1,0,0,p,s,o,h) for p,s,o,h in [(1,1,0,False),(2,2,0,False),(1,1,1,False),(1,0,0,True),(0,1,0,False),(0,2,0,False)]]
for a,b,c,piece,selected,override,hidden in states:
 for button in [*range(32),0xffffffff]:
  changes={0x7ce46c:a,0x7ce46e:b,0x7ce46f:c,0x7d6a2c:override}
  case([call(0x5bcd50,args=[button])]*2,widgets(piece,selected,hidden),changes,'button label flags, menus, references and keyboard map')
for chars in [[0],[255,128,65,0],[65,256,0],[0x80,0x7ff,0]]:
 for non_c in [0,1]:
  changes={0x7ce46c:1}
  for i in [0,70,73,78,79]:change_bytes(changes,0x7d42f8+i*30,struct.pack('<'+'H'*len(chars),*chars))
  for button in [0,3,18,19]:case([call(0x5bcd50,args=[button])],widgets(1,1)+[patch(LOCALE+0x14,'<I',non_c),patch(CONTEXT+4,'<I',1)],changes,'wide key labels and conversion failures preserve original buffers')

# Metrics include all character bytes, escapes/button aliases and real labels,
# both concrete dispatch wrappers, overflowing widths and output aliases.
metric_texts=[b'',b' ',b'Hello THUG2']
metric_texts += [bytes([i]) if i!=92 else b'\\\\' for i in range(1,256)]
metric_texts += [(b'\\'+bytes([e])+bytes([d])+b'X') for e in b'sSbBmM' for d in b'0123456789abcdefghijklmnopqrstuv?']
metric_texts += [b'\\c1hello\\C2world',b'\\u0A\\U1B',b'\\LA',b'\\lA',b'\\?X',b'\\s',b'\\b',b'\\m',b'\\\\\\c1A',b'\\c1\\b0\\s5']
for i,text in enumerate(metric_texts):
 changes={0x7ce46c:i&1}
 if i%3==0:
  for j in range(32):changes[0x6fa808+j]=ord('0')+(31-j)%10
 p=widgets(1 if i%5==0 else 0,1)+[raw(INPUT,(text+b'\0').ljust(128,b'\0'))]
 fn=[0x4cecb0,0x4b3d10,0x48d060][i%3]
 case([call(fn,METRICS if fn==0x4cecb0 else FONT,[INPUT,OUTPUT,OUTPUT+4])],p,changes,'font glyphs, escapes, key labels and concrete virtual dispatch')
for height in [0,1,0x7fffffff,0x80000000,0x80000001,0xffffffff]:
 for target in [(OUTPUT,OUTPUT+4),(OUTPUT,OUTPUT),(METRICS,OUTPUT),(METRICS,METRICS)]:
  case([call(0x4cecb0,METRICS,[INPUT,*target])],[raw(INPUT,b'ABC\0'),patch(METRICS,'<I',height)],label='height conversion and aliased final stores')
for length in [1,32769,65537,70000]:
 for spacing in [-32768,0,32767]:
  p=[raw(INPUT,b'A'*length+b'\0'),patch(METRICS+12+65,'<B',0),patch(GLYPHS+16,'<H',65535),patch(METRICS+0x134,'<h',spacing)]
  case([call(0x4cecb0,METRICS,[INPUT,OUTPUT,OUTPUT+4])],p,label='32-bit accumulated width overflow')

# Exact x87 operation ordering, equal signed zeros, extended intermediates,
# relative scale's byte flag, and updates to the optional target scale.
numbers=[bits(v) for v in [0,-0.0,1,-1,0.5,1.000001,123.125,-987.75,1e-30,1e30]]+[0x7f7fffff,0x00000001,0x00800000,0x7f800000,0xff800000,0x7fc12345,0xffc12345]
layout_offsets=[0xa4,0xa8,0xd4,0xd8,0xe0,0xe4,0xe8,0xec,0xf0,0xf4,0x158,0x15c,0x160,0x164]
def layout(values=None):
 if values is None:values=[bits(v) for v in [1,1,320,240,0,0,1.2,0.8,2,3,-1,0,50,20]]
 return [patch(WIDGET+at,'<I',v) for at,v in zip(layout_offsets,values)]
for i in range(320):
 values=[rng.choice(numbers) for _ in layout_offsets];p=layout(values)+[patch(WIDGET+8,'<I',0xa5000000|(0x2000 if i&1 else 0))]
 width,height=(values[-2:] if i%4==0 else [rng.choice(numbers),rng.choice(numbers)])
 case([call(0x4a92d0,WIDGET,[width,height,[0,1,256][i%3]])]*2,p,label='size update x87 rounding and fixed flag',float_fields=[WIDGET+0xe0,WIDGET+0xe4])
 sx,sy=(values[6:8] if i%4==0 else [rng.choice(numbers),rng.choice(numbers)]);relative=[0,1,256,257][i%4]
 fields=[WIDGET+0xe0,WIDGET+0xe4]+([WIDGET+x for x in [0xa4,0xa8,0xe8,0xec]] if relative&255 else [])
 case([call(0x4a94a0,WIDGET,[sx,sy,relative,[0,1,256][i%3]])]*2,p,label='scale update exact operation order and byte flag',float_fields=fields)
text_inputs=[b'',b'A',b'hello world',b'\\\\',b'\\_a\\_b',b'\\m0\\m4\\m9',b'\\M0',b'\\c1red\\u0',b'\\s4',b'\\b0 + \\b1',b'\\m? tail',b'ABC'*20]
for text in text_inputs:
 for old in [None,b'',b'old',b'x'*100]:
  for font in [0,FONT]:
   for fixed in [0,0x2000]:
    p=layout()+widgets(1,1)+[patch(WIDGET+8,'<I',0x20|fixed),patch(WIDGET+0x178,'<I',OUTPUT if old is not None else 0),patch(WIDGET+0x180,'<I',font),raw(INPUT,(text+b'\0').ljust(128,b'\0'))]
    if old is not None:p.append(raw(OUTPUT,old+b'\0'))
    case([call(0x4af8c0,WIDGET,[INPUT])]*2,p,label='full text setter reuse/reallocate, conversion, font dispatch and layout')
for text in text_inputs:
 p=layout()+widgets(1,1)+[patch(WIDGET+8,'<I',0),patch(WIDGET+0x178,'<I',INPUT),patch(WIDGET+0x180,'<I',FONT),raw(INPUT,(text+b'\0').ljust(128,b'\0'))]
 case([call(0x4af8c0,WIDGET,[INPUT])]*2,p,label='text setter in-place alias and repeated shrinking')

scope='Eleven original engine font/UI/text routines plus both legacy CRT wide-conversion entry points, including the complete text setter, owned storage reuse/reallocation, actual font virtual dispatch and x87-ordered widget sizing/scaling. Key/menu/reference logic, character/button escapes, integer formatting and word splitting run their real callees. Original CRT sprintf/wcstombs executes with only Windows TLS, last-error, keyboard mapping and wide conversion services adapted. Full arena/global bytes, returns, heap/scope ordering and semantic OS traces compare. Only typed arithmetic NaNs in position/relative-scale outputs use classification; raw copied fields remain exact. The host supplies the current single-threaded locale and Windows services; test adapters do not implement browser input. No native gameplay callbacks are substituted. Valid mapped storage, successful allocation and initialized locale/font/key tables retain original contracts. Multiline text/score parents, renderer and playable integration remain unfinished.'
fixture={'base':BASE,'memory':'font-text-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'text_platform_calls','pointer_exports':exports,'pointer_fields':[PLATFORM,PLATFORM+4,PLATFORM+8,FONT], 'native_callbacks':[{'module':'font-text-callbacks.wasm','export':'fixture_text_'+name,'original':CALLBACK+i*16} for i,name in enumerate(['wide','last_error','map'])]}
path=out/'font-text-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
adapter=out/'font-text-callbacks.wasm'
subprocess.run([str(ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang'),'--target=wasm32-unknown-unknown','-O2','-Wall','-Wextra','-Werror','-nostdlib','-Wl,--no-entry,--import-memory,--export-all,--global-base=58720256',str(ROOT/'tools/font_text_callbacks.c'),'-o',str(adapter)],check=True)
print('x86 complete:',len(labels),dict(oracle.counts),dict(os_calls),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_font_text_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'os_calls':dict(os_calls),'heap_events':dict(oracle.heap_events),'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory'],adapter,ROOT/'tools/font_text_callbacks.c']},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
