"""Original complete floor/ground roots with retained-probe write provenance."""
from pathlib import Path
source=Path('local/analysis/probe-walk-grab.py').read_text().split('for side,fraction,angle,kind')[0]
exec(compile(source,'<preserved full ledge-grab prerequisites>','exec'))
from unicorn import UC_HOOK_MEM_WRITE
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x52b370,1116,'thug_walk_floor_draft',0,'void',True,True,True),(0x52d300,431,'thug_walk_ground_draft',0,'void',True,True,True)]
for row in specs:
 bind_new(*row);oracle.cpu.hook_add(UC_HOOK_CODE,observe_cache,begin=row[0],end=row[0])
# Retained probe identity and uninitialized fields are observed at original
# instructions; later defining writes revoke any copied-word allowance.
source_probe=0;copy_destination=0;source_undefined=set();undefined_words=set();undefined_provenance={};root_records=[];event_writes=[];acceleration_events=[]
def floor_observe(cpu,at,size,user):
 global source_probe,copy_destination,source_undefined
 if at in [0x52b370,0x52d300] and oracle.word(cpu.reg_read(UC_X86_REG_ESP))==oracle.stop:
  source_probe=copy_destination=0;root_records.append({'stack_pointer_fields':[]})
 elif at in [0x52b597,0x52b63c,0x52d4a1,0x52d4ae] and oracle.word(cpu.reg_read(UC_X86_REG_ESP))==oracle.stop:
  root_records[-1]['indeterminate_words']=sorted(undefined_words);root_records[-1]['indeterminate_provenance']=[undefined_provenance[a] for a in sorted(undefined_words)]
 elif at==0x52d31f:
  event=oracle.word(P+0x78);assert event in [0x9b46e749,0xaf895b3f] and event_writes[-1][0] in [0x5289b0,0x5289b9]
  acceleration_events.append({'event':event,'last_write':hex(event_writes[-1][0])})
 elif at==0x52cee2:source_probe=0
 elif at==0x417760 and oracle.word(cpu.reg_read(UC_X86_REG_ESP)) in [0x52b398,0x52c32e]:
  source_probe=cpu.reg_read(UC_X86_REG_ECX);source_undefined={0x70,0xa8}
 elif at==0x43a930:
  source_=oracle.word(cpu.reg_read(UC_X86_REG_ESP)+4);copy_destination=0
  if source_==source_probe:
   destination=cpu.reg_read(UC_X86_REG_ECX);copy_destination=destination;field=destination+0x64;fields.add(field)
   root_records[-1]['stack_pointer_fields'].append({'original':source_,'field':field,'size':0xb0})
 elif at==0x43aa26:copy_destination=0
for at in [0x52b370,0x52d300,0x52b597,0x52b63c,0x52d4a1,0x52d4ae,0x52d31f,0x52cee2,0x417760,0x43a930,0x43aa26]:oracle.cpu.hook_add(UC_HOOK_CODE,floor_observe,begin=at,end=at)
def floor_write(cpu,access,address,size,value,user):
 if address==P+0x78 and size==4:event_writes.append((cpu.reg_read(UC_X86_REG_EIP),value))
 for offset in list(source_undefined):
  if address<source_probe+offset+4 and address+size>source_probe+offset:source_undefined.remove(offset)
 for at in list(undefined_words):
  if address<at+4 and address+size>at:undefined_words.remove(at);undefined_provenance.pop(at)
 pc=cpu.reg_read(UC_X86_REG_EIP);offset=0xa8 if pc==0x43aa0f else 0x70 if pc==0x4f81f1 else None
 if source_probe and copy_destination and offset in source_undefined and address==copy_destination+offset:
  assert size==4
  if offset==0xa8:assert cpu.reg_read(UC_X86_REG_EDI)==source_probe and address==cpu.reg_read(UC_X86_REG_ESI)+0xa8
  undefined_words.add(address);undefined_provenance[address]={'destination':address,'source_probe':source_probe,'source_offset':offset,'copy_instruction':hex(pc),'source_writes_before_copy':0}
oracle.cpu.hook_add(UC_HOOK_MEM_WRITE,floor_write)
grounded_base_case=case
def case(calls,patches=(),changes=None,label='Walk floor'):
 root_records.clear();event_writes.clear();undefined_words.clear();undefined_provenance.clear();stages=grounded_base_case(calls,patches,changes,label)
 assert len(stages)==len(root_records)
 for stage,metadata in zip(stages,root_records):
  assert 'indeterminate_words' in metadata;stage.update(metadata)
 return stages
def grounded_debug(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);fmt=bytes(cpu.mem_read(oracle.word(sp+4),64)).split(b'\0')[0]
 count=oracle.word(DLOG);assert count<32;oracle.setword(DLOG,count+1);row=bytearray(192);row[:len(fmt)]=fmt
 if fmt==b'Tracking%d %.2f,%.2f,%.2f,%.2f,%.2f,%.2f\n':
  row[64:68]=cpu.mem_read(sp+8,4);row[72:120]=cpu.mem_read(sp+12,48)
 else:
  assert fmt==b'M:%s:%i: %s\n',fmt
  file=bytes(cpu.mem_read(oracle.word(sp+8),32)).split(b'\0')[0];message=bytes(cpu.mem_read(oracle.word(sp+16),64)).split(b'\0')[0]
  assert (file==b'omponents\\WalkHangUtil.cpp' and message in [b'BAD ANGLE ON COINCIDENT RAIL',b'FOUND COINCIDENT RAIL']) or (file==b'mponents\\WalkComponent.cpp' and message==b'WALKING_GROUND, within moving object'),(file,message)
  row[64:64+len(file)]=file;row[96:96+len(message)]=message;row[188:192]=cpu.mem_read(sp+12,4)
 cpu.mem_write(DLOG+16+192*count,bytes(row))
 if oracle.word(DLOG+4):oracle.setword(oracle.word(DLOG+4),oracle.word(DLOG+8))
 cpu.reg_write(UC_X86_REG_EAX,0xffffffff);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
debug.__code__=grounded_debug.__code__
# Collect only literal required parameter defaults in the prerequisite constructors.
import ast
required_parameters={0xd3193d8e:2}
for filename,classname in [('probe-walk-transition.py','TransitionGraph'),('probe-walk-floor.py','FloorGraph'),('probe-walk-grab.py','GrabGraph'),('probe-walk-ledge.py','LedgeGraph')]:
 tree=ast.parse((folder/filename).read_text());cls=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name==classname)
 constructor=next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=='__init__')
 for node in ast.walk(constructor):
  if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=='parameters':
   for keyword in node.keywords:
    if keyword.arg=='overrides':required_parameters.update(ast.literal_eval(keyword.value))
class GroundedGraph(GrabGraph):
 def __init__(self):
  super().__init__();self.put(OBJ+0x14,'<I',0x100);self.put(EM+8,'<I',self.table([(0x100,OBJ),(0x101,ALTOWNER)]));self.put(P+0x1788,'<I',STATE);self.put(P+0x24,'<4f',0,0,0,1);self.put(P+0x68,'<4f',0,0,0,1)
  self.put(P+0x1864,'<B',0);self.put(P+0x18,'<I',0);self.put(P+0x34,'<4f',0,0,0,1)
  self.put(ALTOWNER+0x14,'<I',0x101);self.put(P+0x1794,'<4f',0,1,0,1);self.put(P+0x84,'<4f',0,0,1,1);self.put(P+0x704,'<f',20);self.put(OBJ+0x4c,'<4f',0,0,0,1)
  self.parameters(overrides=required_parameters)
  self.image[DLOG-BASE:DLOG-BASE+16+32*192]=bytes(16+32*192)
 def plane(self,height,moving=True,up=True,x=0,half=32,flags=0,velocity=(0,0,0,0),owner=None):
  if moving and owner is None:
   owner=self.alloc(0x120);self.image[owner-BASE:owner-BASE+0x120]=bytes(0x120)
   self.put(owner+0x14,'<I',0x18100000+len(self.owners));self.put(owner+0xac,'<4f',*velocity)
   self.put(owner+0x6c,'<16f',*IDENTITY);self.put(owner+0x4c,'<4f',0,0,0,1);self.owners.append(owner)
  return super().plane(height,moving,up,x,half,flags,velocity,owner)
 def trigger(self,mutation='observe',current=None):
  self.put(P+0x1864,'<B',1);self.put(P+0x17b4+0x6d,'<B',1);self.put(P+0x17b4+0x58,'<I',0x111)
  rows=[(0x111,[(0x2ca8a299,13,6)])]
  if current is not None:rows.append((current,[(0x2ca8a299,13,6)]))
  self.level_nodes(rows)
  writes={'observe':[],'cancel':[(CONTROL+0x24,0x10000)],'position':[(P+0x28,bits(50))],'owner':[(P+12,ALTOWNER)],'velocity':[(P+0x34,bits(7)),(P+0x44,bits(99))]}[mutation]
  self.callback(writes)

for moving,height,flags in itertools.product([False,True],[-4,0,4],[0,2]):
 g=GroundedGraph();g.plane(height,moving=moving,flags=flags);g.run([call(0x52b370,P,[Q])],f'floor/{moving}/{height}/{flags}')
floor_records=[]
for route,mutation,moving in itertools.product(['change','leave','enter'],['observe','cancel','position','owner','velocity'],[False,True]):
 g=GroundedGraph();actor=None
 if route!='leave':actor,owner=g.plane(0,moving=moving,flags=0x40)
 g.trigger(mutation,g.word(actor+4) if actor else None)
 if route=='enter':g.put(P+0x1864,'<B',0)
 if moving and actor:g.level_nodes([(0x111,[(0x2ca8a299,13,6)]),(g.word(actor+4),[(0x2ca8a299,13,6)]),(g.word(owner+0x14),[])])
 stages=g.run([call(0x52b370,P,[Q])],f'floor events/{route}/{mutation}/{moving}')
 floor_records.append({'route':route,'mutation':mutation,'moving':moving,'callbacks':oracle.word(CBSTATE),'state':oracle.word(P+0x18)})
for kind,same,moving in itertools.product(['empty','grind','upper','hang'],[False,True],[False,True]):
 g=GroundedGraph();g.put(INPUT+0x1a0,'<B',1);g.put(P+0x68,'<4f',0,0,0 if same else 20,1)
 if kind=='grind':g.grind_nodes();g.put(P+0x68,'<4f',-20,0,0,1);g.put(P+0x24,'<4f',20,0,0,1)
 elif kind=='upper':g.rail_nodes(1,entering=False);g.put(P+0x24,'<4f',0,100,0,1)
 elif kind=='hang':g.rail();g.put(P+0x24,'<4f',0,-60,20,1);g.put(P+0x68,'<4f',0,-60,30,1)
 if moving:g.plane(-100,moving=True)
 g.run([call(0x52b370,P,[Q])],f'floor rail exit/{kind}/{same}/{moving}')
for moving,height,amount in itertools.product([False,True],[-4,0,4],[0,.4,1]):
 g=GroundedGraph();g.plane(height,moving=moving);g.put(P+0x94,'<f',amount)
 g.run([call(0x52d300,P,[Q])]*2,f'full ground/{moving}/{height}/{amount}')
ground_records=[]
for shape,amount,velocity,event in itertools.product(['empty','wall','moving wall','cancelled','airborne'],[0,.4,1],[(0,0,3,1),(2,0,3,1)],[False,True]):
 g=GroundedGraph();g.plane(0,moving=False);g.put(P+0x34,'<4f',*velocity);g.put(P+0x94,'<f',amount)
 if shape in ['wall','moving wall']:g.obstacle('z',2,shape=='moving wall')
 if shape=='cancelled':g.put(CONTROL+0x26,'<B',1)
 if shape=='airborne':g.put(P+0x18,'<I',1);g.put(P+0x44,'<f',4)
 if event:g.put(P+0x78,'<I',0x1d537eff);g.put(P+0x1870,'<f',.5)
 g.run([call(0x52d300,P,[Q])]*2,f'ground contact/early return/{shape}/{amount}/{velocity}/{event}')
 ground_records.append({'shape':shape,'amount':amount,'event':event,'state':oracle.word(P+0x18),'cache':oracle.word(0x691974)})
escape_records=[]
for velocity,old in itertools.product([(0,0,0,1),(3,4,0,1),(6,7,8,1),(20,3,-10,1)],[(0,0,0,1),(1000,0,0,1)]):
 g=GroundedGraph();g.plane(0,moving=False);_,owner=g.plane(40,velocity=velocity);g.put(P+0x68,'<4f',*old)
 g.run([call(0x52d300,P,[Q])],f'ground enclosing moving object/{velocity}/{old}')
 escape_records.append({'velocity':velocity,'previous':old,'diagnostics':oracle.word(DLOG),'state':oracle.word(P+0x18)})
exit_records=[]
for route,blocked in itertools.product(['fall','grind','upper','hang','ledge jump'],[False,True]):
 g=GroundedGraph()
 if route=='grind':
  g.grind_nodes();g.put(INPUT+0x1a0,'<B',1);g.put(P+0x68,'<4f',-20,0,0,1);g.put(P+0x24,'<4f',20,0,0,1)
 elif route=='upper':g.rail_nodes(1,entering=False);g.put(P+0x24,'<4f',0,100,0,1)
 elif route=='hang':g.rail();g.put(P+0x24,'<4f',0,-60,20,1);g.put(P+0x68,'<4f',0,-60,30,1)
 elif route=='ledge jump':
  g.obstacle('z',2,False,False,low=-32,high=12);g.put(P+0x98,'<B',1);g.put(P+0x17a8,'<B',1);g.put(P+0x17ac,'<I',0)
 if blocked:g.put(STATE+0x70,'<B',1)
 g.run([call(0x52d300,P,[Q])],f'ground full transition/{route}/{blocked}',{0x7d1ec8:1000})
 exit_records.append({'route':route,'blocked':blocked,'state':oracle.word(P+0x18),'event':oracle.word(P+0x78),'cache':oracle.word(0x691974)})
# Repeat complete floor frames on the same initialized object and contacts.
for moving,height in itertools.product([False,True],[-3.0001,-3,-2,.01,3]):
 g=GroundedGraph();g.plane(height,moving=moving);g.run([call(0x52b370,P,[Q])]*3,f'repeated floor/height threshold/{moving}/{height}')
scope='Complete floor and ground routines execute real fixed/moving collision, leave/enter/fall callbacks and cancellation, contact/material changes, escape from enclosing moving objects, and falling/grind/rail/hang transitions. Whole defined arena/global state and preserved registers compare, including retained probe/cache identities and original-write-proven uninitialized copies. The common Walk dispatcher, other movement states, startup, rendering and original browser playability remain unfinished.'
extra={**extra,'pointer_globals':sorted(set(extra.get('pointer_globals',[])+[index[0x6918ec+i*4] for i in range(8)])),
 'indeterminate_word_addresses':[a+x for a in [P+0x17b4,*[P+0xbc+i*0xcc for i in range(8)]] for x in [0x70,0xa8]],'stack_probe_pointer_fields':[a+0x64 for a in [P+0x17b4,*[P+0xbc+i*0xcc for i in range(8)]]],
 'native_callbacks':[*[x for x in extra.get('native_callbacks',[]) if DIAG+4 not in x.get('slots',[])],{'module':'walk-grounded-diagnostics.wasm','export':'fixture_walk_grounded_print','slots':[DIAG+4]},{'module':'trigger-callback.wasm','export':'fixture_trigger_native','original':CBNATIVE}]}
saved=coverage.copy();coverage.clear();finish('walk-grounded',scope,{},extra);coverage.update(saved)
report=json.loads((folder/'walk-grounded-original.json').read_text());report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
report['floor_records']=floor_records;report['ground_records']=ground_records;report['escape_records']=escape_records;report['exit_records']=exit_records;report['acceleration_events']=acceleration_events
(folder/'walk-grounded-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n')
(folder/'walk-grounded-original.json').write_text(json.dumps(report,indent=2)+'\n');print({a:(x['covered'],x['total']) for a,x in report['instruction_coverage'].items()})
