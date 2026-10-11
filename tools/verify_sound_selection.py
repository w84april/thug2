"""Differential recovery of material/impact sound selection, not sound playback."""
import hashlib,json,random,struct,subprocess
from specimen import ROOT,SHA256
from script_heap_oracle import ScriptHeapOracle

out=ROOT/'local/validation/collision';report_path=out.parent/'sound-selection.json';report_path.unlink(missing_ok=True)
BASE=0x1800000;BUCKETS=BASE+0x1000;OUTPUT=BASE+0xf000;VOLUME=OUTPUT+0x200;CONFIG=BASE+0x5400
memory=bytearray(0x10000);memory[0xf000:]=b'\xa5'*0x1000
struct.pack_into('<2I',memory,CONFIG-BASE,0xadadadad,2)
initial=bytes(memory);(out/'sound-selection-memory.bin').write_bytes(initial)
def bits(f):return struct.unpack('<I',struct.pack('<f',f))[0]
def patch(at,fmt,*v):return [at,struct.pack(fmt,*v).hex()]
globals_=[];defaults=[];index={}
def glob(name,address,value=0,offset=0):
 index[address]=len(globals_);globals_.append([name,address,4,offset]);defaults.append(value)
glob('thug_script_symbol_buckets',0x6f3624,BUCKETS)
for name,at,buckets in [('materials',0x6968d0,BASE+0x5000),('events',0x6968e8,BASE+0x5200)]:
 for j,value in enumerate([2,buckets,0,0x12345678,0,0xababab00]):glob('thug_sound_'+name,at+j*4,value,j*4)
for name,at,value in [('device',0x7d6a38,1),('mode',0x7cefa8,0),('configuration',0x6f85a8,CONFIG),('default_distance',0x67da34,bits(1020)),('asset_count_a',0x6f85b8,0),('asset_count_b',0x6f85b4,0)]:glob('thug_sound_'+name,at,value)
for j,value in enumerate([0x12345678,0xabcdef01,0x87654321]):glob('thug_random_state',0x690fd4+j*4,value,j*4)
# Read-only original asset arenas are initially zero. Track every byte of each
# populated record, including the last slot, plus both counts. Unpopulated slots
# stay zero throughout; this suite does not claim asset loading behavior.
exports=[]
for name,address in [('a',0x6f5e68),('b',0x6f4268)]:
 for i in range(256):exports.append([address+i*28,'thug_sound_assets_'+name,i*28])
 for i in [*range(8),255]:
  for j in range(7):glob('thug_sound_assets_'+name,address+i*28+j*4,0,i*28+j*4)
functions={}
def bind(at,name,argc=0,this=False,result='word',floats=(),cleanup=None,pointer=False):
 functions[hex(at)]={'name':name,'this':this,'result':result,'cleanup':4*argc if this else 0,'float_args':list(floats),'pointer_result':pointer}
 if cleanup is not None:functions[hex(at)]['cleanup']=cleanup
for at,name in [(0x476590,'text'),(0x476860,'array')]:bind(at,'thug_script_get_'+name,3,True,'byte')
bind(0x476a90,'thug_script_find_name_or_flag',1,True)
bind(0x476af0,'thug_script_has_name_or_flag',1,True)
bind(0x444310,'thug_sound_event_parameter',1)
bind(0x444360,'thug_sound_material_name',1)
bind(0x4443b0,'thug_sound_event_id',1,result='byte')
bind(0x444400,'thug_sound_material_settings',3,result='byte')
bind(0x444480,'thug_sound_get_material_settings',3,result='byte')
bind(0x444760,'thug_sound_select_weighted',1)
bind(0x444830,'thug_sound_select_impact',3,floats=[2])
bind(0x4445b0,'thug_sound_build_descriptor',2,result='byte')
bind(0x47b010,'thug_sound_disabled',result='byte')
bind(0x47b030,'thug_sound_volume_initialize',this=True)
bind(0x47ac50,'thug_sound_volume_scale',1,True,'void',floats=[0])
bind(0x47acf0,'thug_sound_volume_silent',this=True,result='byte')
bind(0x47b2c0,'thug_sound_find_asset',1,cleanup=4,pointer=True)
bind(0x47b760,'thug_sound_asset_distance',1,result='double',cleanup=4)
observe=[int(k,16) for k in functions]+[0x588190,0x479020,0x478cf0,0x4764b0,0x4767c0,0x476630,0x4766d0,0x46cc30,0x403de0,0x401b90,0x5480a0]
oracle=ScriptHeapOracle(initial,BASE,BASE+0x20,BASE+0x100,globals_,defaults,functions,observe=observe)
for address in [0x6f4268,0x6f5e68]:
 assert bytes(oracle.cpu.mem_read(address,256*28))==bytes(256*28)

class Build:
 def __init__(self):self.data=bytearray();self.buckets={};self.changes={};self.extra=[]
 def alloc(self,data):
  at=BASE+0x6000+len(self.data);self.data.extend(data);self.data.extend(bytes((-len(self.data))%4));assert len(self.data)<0x8000;return at
 def words(self,*values):return self.alloc(struct.pack('<'+'I'*len(values),*values))
 def text(self,value):return self.alloc(value+b'\0')
 def structure(self,components):
  entries=[]
  for name,kind,value in components:entries.append(self.alloc(struct.pack('<BBHIII',kind*2+(len(entries)&1),0xa5,0xa5a5,name,value,0)))
  for a,b in zip(entries,entries[1:]):struct.pack_into('<I',self.data,a-(BASE+0x6000)+12,b)
  return self.words(0xadadadad,entries[0] if entries else 0)
 def symbol(self,name,kind,value):
  bucket=BUCKETS+(name&4095)*4
  at=self.alloc(struct.pack('<BBHIIII',0xa5,kind,0xabab,name,0xcccccccc,value,self.buckets.get(bucket,0)))
  self.buckets[bucket]=at;return at
 def array(self,values):return self.words(0x1400,len(values),values[0] if len(values)==1 else self.words(*values))
 def table(self,which,shift,entries):
  count=1<<(shift&31);buckets=self.alloc(bytes(count*12));tails={}
  for key,value in entries:
   slot=buckets+(key&(count-1))*12
   if slot not in tails:at=slot
   else:
    at=self.words(0,0,0);struct.pack_into('<I',self.data,tails[slot]-(BASE+0x6000)+8,at)
   struct.pack_into('<3I',self.data,at-(BASE+0x6000),key,value,0);tails[slot]=at
  address=0x6968d0 if which=='materials' else 0x6968e8
  self.changes.update({address:shift,address+4:buckets,address+8:len(entries),address+12:0xdeadbeef,address+16:buckets})
 def patches(self):return [[BASE+0x6000,self.data.hex()]]+[patch(k,'<I',v) for k,v in self.buckets.items()]+self.extra

labels=[];rng=random.Random(0x444830)
def call(at,*args,this=0):return at,this,list(args)
def case(calls,b=None,p=(),changes=None,label='synthetic',float_fields=()):
 if len(labels)%200==0:print('Original sound cases:',len(labels),label,flush=True)
 c=dict(b.changes) if b else {};c.update(changes or {})
 stages=oracle.case(calls,(b.patches() if b else [])+list(p),{index[k]:v for k,v in c.items()});labels.append(label)
 for s in stages:s['float_fields']=list(float_fields)
 return stages

# Accessors: aliases, nested inclusions, localized-string precedence, duplicates,
# literal flags and name zero. Poisoned output words must survive a missing read.
for i in range(180):
 b=Build();texts=[b.text(x) for x in [b'normal',b'localized',b'last']];arr=b.array([b.structure([])])
 name=rng.choice([0,0x7713c7b,0x99,0xffffffff]);leaf=b.structure([(name,3,texts[2]),(0x99,12,arr)])
 b.symbol(0xa0001234,10,leaf);b.symbol(0xa0002234,13,0xa0001234);b.symbol(0xa0003234,3,texts[0]);b.symbol(0xa0004234,12,arr)
 possibilities=[(name,3,texts[0]),(name,4,texts[1]),(name,13,0xa0003234),(name,12,arr),(name,13,0xa0004234),
  (0,13,0xa0002234),(0,13,name),(name,1,123),(0x555,3,texts[0])]
 s=b.structure([rng.choice(possibilities) for _ in range(i%9)])
 for key in [name,0,0x99,0x9876]:
  case([call(0x476590,key,OUTPUT,i%2,this=s),call(0x476860,key,OUTPUT+4,i%2,this=s),call(0x476a90,key,this=s),call(0x476af0,key,this=s)],b,label='typed text array and first name-or-flag')

# Iterate tables independently of record ID; test collisions, duplicate IDs,
# empty inline buckets and null-valued collision nodes that stop iteration.
for i in range(120):
 b=Build();shift=rng.choice([0,1,2,3,32,33,35]);entries=[];evententries=[];ids=[];names=[]
 for j in range(i%9):
  ident=rng.choice([0,1,3,7,255]);name=rng.randrange(2**32);ids.append(ident);names.append(name)
  entries.append((rng.randrange(32),b.words(ident|0xa5a5a500,name)))
  evententries.append((rng.randrange(32),b.words(ident|0xa5a5a500,name,0x12340000+j)))
 if i%5==0:
  entries.insert(0,(1,0));evententries.insert(0,(1,0))
 b.table('materials',shift,entries);b.table('events',shift,evententries)
 case([*[call(0x444360,k) for k in [0,1,255,0xffffff03]],*[call(0x4443b0,k) for k in names[:3]+[0xabcdef01]]],b,label='material event iteration and truncation')
for i in range(64):
 b=Build();ident=i*4%256;name=rng.randrange(2**32);record=b.words(ident,name,name^0xffffffff)
 b.table('events',rng.choice([0,2,34]),[(ident,0),(ident+256,b.words(5,7,9)),(ident,record)])
 case([call(0x444310,ident),call(0x444310,ident|0xad000000)],b,label='registered event parameter exact hash lookup')

# Material-specific and default properties, alias types, missing values and
# successful null structure pointers; failure must preserve the caller's word.
for i in range(96):
 b=Build();property_=0x5c969c50;target=b.structure([]);specific=b.structure([(property_,[10,1,12][i%3],target if i%4 else 0)])
 fallback=b.structure([] if i%4==0 else [(property_,10,target if i%5 else 0)])
 if i%6:b.symbol(0x5b80cfcb,10 if i%7 else 1,fallback)
 if i%8:b.symbol(0x12345678,10 if i%9 else 1,specific)
 if i%10==0:b.symbol(0,10,specific)
 b.table('materials',2,[(2,b.words(7,0x12345678))] if i%2 else [])
 case([call(0x444400,7,OUTPUT,property_),call(0x444480,OUTPUT+4,0xffffff07,property_)],b,label='material property fallback and null success')

# Required weight and array parameters are always supplied. Malformed missing
# weights leave original stack locals uninitialized and are outside this contract.
for i in range(320):
 b=Build();weights=[rng.choice([0,1,2,100,32767,65536,0xffffffff,0x80000000]) for _ in range(i%9)]
 choices=[b.structure([(0xdbc4c4db,1,w)]) for w in weights]
 s=b.structure([(0x25f654c8,12,b.array(choices))])
 if i%7==0:s=b.structure([(0x25f654c8,10,choices[0] if choices else 0),(0x25f654c8,12,b.array(choices))])
 case([call(0x444760,s),call(0x444760,s)],b,changes={0x690fd4:rng.randrange(2**32),0x690fd8:rng.randrange(2**32),0x690fdc:rng.randrange(2**32)},label='reverse weighted selection and random state')

special=[0,0x80000000,1,0x80000001,bits(-1),bits(1),bits(100),0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc12345,0x7fa12345]
for i in range(220):
 b=Build();eventname=0xdead0001;b.table('events',2,[(3,b.words(3,0x12345678,eventname))]);entries=[]
 for j in range(i%5):
  choices=[b.structure([(0xdbc4c4db,1,j+1)]),b.structure([(0xdbc4c4db,1,7)])]
  components=[(0x25f654c8,12,b.array(choices))]
  if (i+j)%6:components.append((0x9ee9a09a,2,special[(i+j)%len(special)]))
  if i%5==0:components[0]=(0x25f654c8,10,choices[0])
  entries.append(b.structure(components))
 s=b.structure([(eventname,12,b.array(entries))])
 if i%9==0:s=b.structure([(eventname,10,entries[0] if entries else 0),(eventname,12,b.array(entries))])
 case([call(0x444830,s,0xff000003,x) for x in [special[i%len(special)],bits(100)-1,bits(100),bits(100)+1]],b,label='impact threshold equality unordered and absent values')
for threshold in [0,1,16777217,0x7fffffff,0x80000000,0xffffffff]:
 b=Build();eventname=0xdead0001;b.table('events',0,[(3,b.words(3,0x12345678,eventname))]);choice=b.structure([])
 entry=b.structure([(0x25f654c8,10,choice),(0x9ee9a09a,1,threshold)])
 s=b.structure([(eventname,12,b.array([entry]))]);signed=threshold if threshold<2**31 else threshold-2**32;word=bits(signed)
 case([call(0x444830,s,3,x) for x in [(word-1)&0xffffffff,word,(word+1)&0xffffffff]],b,label='integer threshold conversion adjacent floats')

names=[0xfa3e14c5,0x1c5ebb24,0x0693daaf,0x4391992d,0xf573682f,0x312ccbcf]
paths=[b'',b'sound.wav',b'Folder/SOUND.WAV',b'a\\b/C\\sound',b'trailing/',b'\\',b'X'*103,b'\x80\xff/\xc0.wav']
for i in range(160):
 b=Build();text=b.text(paths[i%len(paths)]);b.symbol(0xabc00001,3,text)
 components=[] if i%9==0 else [(0x07713c7b,[3,4,13][i%3],0xabc00001 if i%3==2 else text)]
 for j,name in enumerate(names):
  kind=[1,2,3,13][(i+j)%4];value=special[(i+j)%len(special)]
  if kind==13:b.symbol(0xdef00000+j,2,value);value=0xdef00000+j
  if (i+j)%5:components.append((name,kind,value))
 s=b.structure(components)
 case([call(0x47b010),call(0x4445b0,s,OUTPUT)],b,changes={0x7d6a38:0 if i%11==0 else 0xadadadad,0x7cefa8:[0,1,2,6,7,0xffffffff][i%6]},label='sound descriptor defaults path CRC and optional raw floats')

# Channel initialization preserves the following bytes, including spatial data.
for format_ in [0,1,2,3,4,0xffffffff]:
 for config in [0,CONFIG,VOLUME-4]:
  case([call(0x47b030,this=VOLUME),call(0x47acf0,this=VOLUME)],p=[patch(CONFIG+4,'<I',format_),patch(VOLUME,'<I',format_)],changes={0x6f85a8:config},label='volume initialization config alias and untouched suffix')
for i in range(360):
 format_=[0,1,2,3,4,0xffffffff][i%6]
 values=[rng.choice(special) for _ in range(5)] if i%3 else [0,0x80000000,0,0,0]
 if i<65:values=[0]*5;values[i%5]=special[(i//5)%len(special)]
 scale=special[(i//6)%len(special)] if i<156 else rng.randrange(2**32)
 case([call(0x47acf0,this=VOLUME),call(0x47ac50,scale,this=VOLUME),call(0x47acf0,this=VOLUME)],p=[patch(VOLUME,'<6I',*values,format_)],label='channel count silence and wide exponent scale',float_fields=range(VOLUME,VOLUME+20,4))

# Signed counts, array precedence, duplicates, first/last slots, missing assets,
# disabled audio, signed-zero default distances and NaNs.
for i in range(220):
 changes={0x7d6a38:0 if i%13==0 else 1,0x7cefa8:[0,1,2,6,7][i%5],0x67da34:special[i%len(special)],0x6f85b8:[0,1,8,256,0xffffffff][i%5],0x6f85b4:[8,256,0,1,0x80000000][i%5]}
 keys=[]
 for array in [0x6f5e68,0x6f4268]:
  for j in [*range(8),255]:
   key=rng.choice([0,1,2,0x12345678]);keys.append(key);changes[array+j*28]=key;changes[array+j*28+16]=special[(i+j)%len(special)]
 case([call(fn,key) for key in [1,2,0x12345678,0xdeadbeef] for fn in [0x47b2c0,0x47b760]],changes=changes,label='loaded asset precedence count and distance defaults')
for first in [0x6f5e68,0x6f4268]:
 for count in [255,256]:
  for duplicate in [0,1]:
   for distance in [0,0x80000000,bits(123),0x7fc12345]:
    changes={0x6f85b8:count if first==0x6f5e68 else 0,0x6f85b4:count if first==0x6f4268 else 0,first+255*28:0xdead0011,first+255*28+16:distance}
    if duplicate:changes.update({first:0xdead0011,first+16:bits(456)})
    case([call(0x47b2c0,0xdead0011),call(0x47b760,0xdead0011)],changes=changes,label='last asset boundary and duplicate precedence')

scope='Eighteen original routines: text/array and first-name-or-flag access; material/event lookup and fallback; impact-threshold and reverse weighted sound selection; descriptor path/basename CRC and optional settings; audio-disabled predicate; volume initialization/scaling/silence; loaded asset lookup and distance defaults. Original callees execute unchanged, with no configured callbacks or allocations. Full 64-KiB fixture arena, table iterator and PRNG state, configuration globals, populated asset records and return values compare against original x86. Arithmetic NaN outputs/returns compare only by classification; raw descriptor fields remain bit-exact. Valid registered event IDs, acyclic script graphs, required arrays/weights, bounded asset counts and paths fitting the original buffer are caller contracts. This does not recover audio startup, asset loading, spatialization, playback, the parent sound dispatcher or the full wall/movement loop. Training level is not playable.'
fixture={'base':BASE,'memory':'sound-selection-memory.bin','globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'pointer_exports':exports,'pointer_fields':[],'pointer_globals':[]}
path=out/'sound-selection-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
print('x86 complete:',len(oracle.cases),'cases',sum(oracle.counts.values()),'calls',flush=True)
assert not oracle.heap_events
subprocess.run(['node',str(ROOT/'tools/verify_sound_selection_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/'sound-selection-memory.bin']},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
