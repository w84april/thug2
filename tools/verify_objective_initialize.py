"""Complete original objective initialization, including archived training flags."""
import hashlib,json,struct,subprocess
from collections import Counter
from unicorn import UC_HOOK_CODE
from specimen import ROOT,SHA256
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'objective-initialize.json';report_path.unlink(missing_ok=True)
prior=json.loads((out/'script-schedule-fixtures.json').read_text());BASE=prior['base'];SIZE=0x1c0000
memory=bytearray((out/prior['memory']).read_bytes());memory.extend(b'\xad'*(SIZE-len(memory)))
CONTEXT,ADAPTER,ALLOCATOR=BASE+0x20,BASE+0x50,BASE+0x100
BUCKETS,PRINT,LOG,HEAP=BASE+0x10000,BASE+0x35f00,BASE+0x60000,BASE+0x80000
OBJECT,GAME,MANAGER,PROFILES,PROFILE,SKATERS,BODY,ARRAY,CODE,GRAPH=[BASE+x for x in [0x180000,0x181000,0x182000,0x183000,0x184000,0x185000,0x186000,0x187000,0x188000,0x190000]]
def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
def raw(at,data):return [at,bytes(data).hex()]
put(CONTEXT,'<8I',HEAP,BASE+0x100000,0,LOG,BASE,BASE+SIZE,OBJECT+0x6c,0)
put(ALLOCATOR+0x114,'<I',ALLOCATOR+0x500)
put(GAME+0x38c,'<I',MANAGER);put(GAME+0x34,'<I',SKATERS)
put(PROFILES+0x14,'<3I',PROFILE,PROFILE,0)
put(SKATERS,'<4I',0,BODY,0,SKATERS+16);put(SKATERS+16,'<4I',0,0xffffffff,0,SKATERS+16);put(BODY+0xbc,'<B',1)
put(ARRAY,'<3I',0,0,0)
initial=bytes(memory)
globals_=prior['globals'][:];defaults=prior['cases'][0]['globals'][:];index={g[1]:i for i,g in enumerate(globals_)}
for name,at,value in [('thug_game_context',0x7ce478,GAME),('thug_profile_manager',0x7ce4b4,PROFILES)]:
 index[at]=len(globals_);globals_.append([name,at,4]);defaults.append(value)
functions={
 '0x557270':{'name':'thug_objective_initialize','this':True,'result':'void','cleanup':0,'memory':True,'stack_args':[],'diagnostics':True},
 '0x471b00':{'name':'thug_script_parse_array','this':False,'result':'word','cleanup':0,'memory':True},
}
observe=[0x557270,0x559050,0x478540,0x5566d0,0x475790,0x4750b0,0x474540,0x474420,0x556a00,0x555b50,0x554890,0x471b00,0x476af0,0x476630]
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,ALLOCATOR,globals_,defaults,functions,observe=observe,event_limit=(HEAP-LOG)//48,
 scope_entries={BASE+0x6000:1,ALLOCATOR+0x300:2,ALLOCATOR+0x400:4,ALLOCATOR+0x500:5})
for at in [0x6f362c,0x6f3634,0x6f3638,0x6f2578,0x6f2580,0x6f2584]:oracle.cpu.mem_write(at,bytes(4))
# Real CRT sprintf uses the initialized locale; this suite never needs an OS call.
oracle.setword(0x68ecfc,BASE+0x9600)
labels=[];outcomes=Counter();fields=set();exports=dict(prior['pointer_exports'])
branches={0x5572a0:'difficulty_merge',0x5572e4:'initialization_script',0x5572fb:'text_update',0x55732f:'untimed_bit_set',0x557344:'flag_40_cleared',0x556ce6:'text_success',0x556ca8:'text_failure_cleanup'}
def branch(cpu,address,size,user):outcomes[branches[address]]+=1
for at in branches:oracle.cpu.hook_add(UC_HOOK_CODE,branch,begin=at,end=at)
class Build:
 def __init__(self):self.data=bytearray();self.buckets={};self.extra=[]
 def alloc(self,data):
  at=GRAPH+len(self.data);self.data.extend(data);self.data.extend(bytes((-len(self.data))%4));assert GRAPH+len(self.data)<BASE+SIZE;return at
 def text(self,s):return self.alloc(s+b'\0')
 def structure(self,entries):
  nodes=[self.alloc(struct.pack('<BBHIII',kind*2+(i&1),0x5a,0,name,value&0xffffffff,0)) for i,(name,kind,value) in enumerate(entries)]
  for a,b in zip(nodes,nodes[1:]):struct.pack_into('<I',self.data,a-GRAPH+12,b)
  return self.alloc(struct.pack('<II',0xabcdef01,nodes[0] if nodes else 0))
 def array(self,kind,items):
  value=items[0] if len(items)==1 else self.alloc(struct.pack('<'+'I'*len(items),*items)) if items else 0
  return self.alloc(struct.pack('<BBHII',0x91,kind,0x2345,len(items),value))
 def header(self,at,source):self.extra.append(raw(at,self.data[source-GRAPH:source-GRAPH+8]))
 def symbol(self,name,kind,value):
  bucket=BUCKETS+(name&4095)*4;old=self.buckets.get(bucket,struct.unpack_from('<I',initial,bucket-BASE)[0])
  self.buckets[bucket]=self.alloc(struct.pack('<BBHIIII',0,kind,0,name,0,value,old))
 def patches(self):return [raw(GRAPH,self.data)]+[patch(at,'<I',v) for at,v in self.buckets.items()]+self.extra

def initialize():return 0x557270,OBJECT,[PRINT]
def case(b,params,calls=None,p=(),label='objective initialization'):
 state=b.structure([(0x1234,1,99),(0x5678,3,b.text(b'old objective state'))])
 patches=b.patches()+[patch(OBJECT+0x1c,'<2I',params,state)]+list(p)
 stages=oracle.case(calls or [initialize(),initialize()],patches);labels.append(label)
 for s in stages:
  merged=[]
  for at,data in s['outputs']:
   if int.from_bytes(bytes.fromhex(data),'little') in exports:fields.add(at)
   if merged and merged[-1][0]+len(merged[-1][1])//2==at:merged[-1][1]+=data
   else:merged.append([at,data])
  s['outputs']=merged
 if len(labels)%50==0:print('Original initialization cases:',len(labels),flush=True)
 return stages

def settings(b,difficulty):
 mode=0x9abcdef0;entries=[] if difficulty is None else [(mode,1,difficulty)]
 d=b.structure(entries);s=b.structure([(0xa1dc81f9,13,mode)])
 b.extra.append(patch(MANAGER+0x398,'<I',d));b.header(defaults[index[0x7ce470]]+4,s)

def text_environment(b,kind):
 combo,trick=0xa000,0xb000
 b.symbol(0x8856c817,10,b.structure([(combo,3,b.text(b'Jump'))]))
 b.symbol(trick,10,b.structure([(0x7031f10c,10,b.structure([(0xa1dc81f9,3,b.text(b'Ollie'))]))]))
 mapping=b.structure([] if kind=='failure' else [(combo,13,trick)])
 b.header(PROFILE+0x5c,b.structure([(0xd544aa2d,10,mapping),(0xac9b9eda,1,0)]))
 fields_=[(0x79704516,12,b.array(13,[combo])),(0x4bc5229d,3,b.text(b'Press \\k1 for \\t1'))]
 if kind=='array':fields_.append((0x0c5d7e6b,12,b.array(3,[b.text(b'Button \\k1'),b.text(b'Trick \\t1')])) )
 else:fields_.append((0x0c5d7e6b,3,b.text(b'Unchanged scalar \\t1')))
 return fields_
# No difficulty array preserves existing state/counts. All branches retain
# unrelated bits and distinguish a named parameter from an unnamed flag.
for flags in [0,1,0x40,0x41,0x80,0xff]:
 for untimed in [None,0,1,2,0xffffffff]:
  for hide in ['absent','flag','named','wrong_named']:
   b=Build();entries=[]
   if untimed is not None:entries.append((0xf0e712d2,1,untimed))
   if hide=='flag':entries.append((0,13,0x79bbffcb))
   elif hide=='named':entries.append((0x79bbffcb,1,0))
   elif hide=='wrong_named':entries.append((0x79bbffcb,3,b.text(b'present')))
   params=b.structure(entries)
   case(b,params,p=[patch(OBJECT+0x6c,'<2B',flags,flags^0xa6)],label='no difficulty: preserved state, flag bits and untimed values')
# Every difficulty choice, default/invalid values and single-element inline
# indexing. Selected fields replace old values before state/text/script work.
for difficulty in [None,0,1,2,3,0xffffffff]:
 for inline in [False,True]:
  for grouped in [False,True]:
   b=Build();settings(b,difficulty);levels=[]
   for i in range(1 if inline else 3):
    names=[0x701+j for j in range(i+1)];flags=b.array(13,names)
    if grouped:flags=b.array(10,[b.structure([(0x5b8ab877,13,0x300+i),(0xcc3c4cc4,12,flags)])])
    levels.append(b.structure([(0xcc3c4cc4,12,flags),(0xf0e712d2,1,i),(0x398b1b8b,13,6 if i&1 else 7)]))
   params=b.structure([(0x85104ab3,12,b.array(10,levels)),(0xf0e712d2,1,0)])
   case(b,params,label='difficulty merge then original state builder and synchronous QB execution')
# Execute original cached bytecode, nested calls and aliases. Missing/irrelevant
# symbols follow the real scheduler's no-op path, with no substituted callbacks.
for script in [5,6,7,0x12340007,0xeeeeeeee,0xabc01004]:
 for text in ['absent','scalar','array','failure']:
  b=Build();entries=[(0x398b1b8b,13,script)]
  if text!='absent':entries+=text_environment(b,text)
  params=b.structure(entries);case(b,params,label='real synchronous scripts followed by successful or failed text conversion')
# Parse the exact hash-verified bytes of all thirty archived training goal_flags
# arrays, then merge their structures and initialize/reinitialize the objective.
token_fixture=json.loads((out/'script-tokens-fixtures.json').read_text())
token_report=json.loads((out.parent/'script-tokens.json').read_text())
token_memory=(out/token_fixture['memory']).read_bytes()
arrays=json.loads((ROOT/'local/analysis/training-objective-arrays.json').read_text());assets=[]
for entry in arrays:
 asset=next(a for a in token_report['assets'] if a['member']==entry['member'])
 data=token_memory[asset['address']-token_fixture['base']:asset['address']-token_fixture['base']+asset['size']]
 assert hashlib.sha256(data).hexdigest()==asset['sha256']==entry['asset_sha256']
 data=data[entry['offset']:entry['offset']+entry['bytes']];assert data[0]==5 and data[-1]==6
 b=Build();settings(b,0);level=b.structure([(0xcc3c4cc4,12,ARRAY)])
 params=b.structure([(0x85104ab3,12,b.array(10,[level])),(0x398b1b8b,13,6)])
 stages=case(b,params,calls=[(0x471b00,0,[ARRAY,CODE,0]),initialize(),initialize()],p=[raw(CODE,data)],label='archived '+entry['script']+' goal_flags @'+str(entry['offset']))
 assert stages[0]['result']==CODE+len(data)
 assets.append({k:entry[k] for k in ['member','asset_sha256','script','offset','bytes']})
fields.update(at for at in range(BASE,BASE+SIZE,4) if int.from_bytes(initial[at-BASE:at-BASE+4],'little') in exports)
scope='Complete objective initialization557270 executes difficulty selection/parameter merge, actual state builder5566d0, synchronous bytecode scheduling/execution and complete text update556a00 before the original flag mutations. No native gameplay callbacks are substituted. Tests include repeated initialization, all relevant flag branches, flat/grouped difficulty states, missing/invalid difficulty, inline arrays, nested QB calls/aliases, missing script symbols and text-failure cleanup. All thirty goal_flags arrays from hash-verified archived training scripts are parsed by the recovered original parser and used by the full parent. Only heap/scope services are adapted; successful allocation, valid difficulty entries, terminating synchronous scripts and the documented text-buffer contracts remain. Full goal activation, skating and rendering are not yet complete.'
fixture={'base':BASE,'memory':'objective-initialize-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'pointer_exports':prior['pointer_exports'],'pointer_fields':sorted(fields),'pointer_globals':prior['pointer_globals']}
path=out/'objective-initialize-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
print('x86 complete:',len(labels),dict(oracle.counts),dict(outcomes),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_objective_initialize_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'outcomes':dict(outcomes),'callee_coverage':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'training_arrays':assets,'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory'],out/prior['memory'],out/'script-schedule-fixtures.json',out/token_fixture['memory'],out/'script-tokens-fixtures.json',out.parent/'script-tokens.json',ROOT/'local/analysis/training-objective-arrays.json']},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
