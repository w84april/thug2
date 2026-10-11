"""Original Input component callbacks, real event delivery and modal UI lookup."""
from pathlib import Path
exec(compile(Path('local/analysis/composite-construction-fixture-setup.py').read_text(),'<preserved object/script state>','exec'))
from unicorn.x86_const import UC_X86_REG_FPSW,UC_X86_REG_FPTAG,UC_X86_REG_MXCSR
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x460820,20,'thug_object_copy_parameters_draft',1,'void',True,False,True),
 (0x41ebf0,175,'thug_input_button_event_draft',6,'void',True,True,True),
 (0x41eca0,537,'thug_input_packet_events_draft',1,'void',True,True,True),
 (0x41ef20,356,'thug_input_ui_blocked_draft',0,'byte',True,False,False),
 (0x41f090,102,'thug_input_primary_packet_draft',1,'void',True,True,True),
 (0x41f100,97,'thug_input_secondary_packet_draft',1,'void',True,False,True),
 (0x41f170,17,'thug_input_primary_task_draft',1,'void',True,True,False),
 (0x41f190,17,'thug_input_secondary_task_draft',1,'void',True,False,False)]
for row in specs:bind_new(*row)
bind(0x477d40,'thug_script_set_checksum',2,heap=True)
bind(0x46b940,'thug_input_pad_construct_draft',result='word')
for name,at,value in [('thug_input_network_state_draft',0x6fa7d0,NET),
 ('thug_frame_counter',0x7d1ec8,1000),('thug_frame_rate',0x684fd0,bits(1000)),
 ('thug_timer_origin',0x696d64,0),('thug_time_scale',0x67d7c0,bits(1)),('thug_timer_offset',0x696d60,0),
 ('thug_input_direction_initialized_draft',0x6f22b0,0)]:global_default(name,at,value)
for i in range(16):glob('thug_input_direction_angles_draft',0x6f2270+4*i,0,offset=4*i)
for at in [0x4609f0,0x462f00,0x461140,0x473800,0x460470,0x475750,0x4750b0,0x44e4f0,0x4aae20,0x409030,0x476410,0x460820,0x476950,0x477130,0x409070,0x46bda0,0x46bb50]:
 oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
P,PACKET,RELEASE,TASK=BASE+0xc0000,BASE+0xc1000,BASE+0xc1100,BASE+0xc1200
memory[P-BASE:P-BASE+0x1300]=bytes(0x1300)
initial=bytes(memory);oracle.initial=initial
EVENTS=[(6,0x40,0x5c8faa09,0xb27804a2,0x20),(7,0x80,0xd26adae9,0xaef7dfd3,0x40),
 (5,0x20,0xb4f2adba,0xc86fa880,0x60),(4,0x10,0x0edbbc2b,0xc8abf89c,0x80),
 (9,0x200,0xb069b600,0xe5aae06b,0x160),(11,0x800,0xa93dbbd0,0xfcfeedbb,0x180),
 (8,0x100,0x7f695a77,0x7b684919,0x1a0),(10,0x400,0x42717176,0xbbbef674,0x1c0),
 (12,0x1000,0xc6547217,0x28a3dcbc,0xa0),(14,0x4000,0x5f5d23ad,0xb1aa8d06,0xc0),
 (16,0x10000,0x285a133b,0xc6adbd90,0xe0),(13,0x2000,0x12154dc8,0xfce2e363,0x100),
 (15,0x8000,0x8b1c1c72,0x65ebb2d9,0x120),(17,0x20000,0xfc1b2ce4,0x12ec824f,0x140),
 (22,0x400000,0x33947317,0xf5e437a0,0),(23,0x800000,0xf8de049b,0x3eae402c,0),(24,0x1000000,0xac7f105a,0x55b09758,0)]
class InputGraph(CompositeGraph):
 def __init__(self,fill=0):
  super().__init__();self.image[P-BASE:P-BASE+0x4a0]=bytes([fill])*0x4a0
  self.put(P+12,'<I',OBJ);self.put(P+0x18,'<2I',0,0)
  self.put(P+0x498,'<3B',0,0,1);self.put(OBJ,'<I',0x64a290);self.put(OBJ+0x104,'<I',0)
  self.put(EM+8,'<I',self.table([(0x100,OBJ)]));self.ui=[]
  for pad in [0x20,0x258]:
   for off in range(0,0x200,0x20):self.put(P+pad+off+0x1c,'<I',0)
   self.put(P+pad+0x230,'<2I',0,0)
  self.packet(PACKET);self.packet(RELEASE)
  self.put(TASK+0x18,'<I',PACKET);self.put(TASK+0x28,'<I',P)
 def packet(self,p=PACKET,buttons=(),axes=(128,128,128,128),flags=0):
  b=bytearray(32);b[:4]=bytes(axes);b[0x12:0x16]=bytes(axes)
  for i,v in buttons:b[i]=v
  struct.pack_into('<I',b,28,flags);self.image[p-BASE:p-BASE+32]=b
 def gate(self,mode,network=True):
  connection=self.alloc(0x1e88);self.put(connection+0x1e84,'<I',0)
  self.put(NET,'<3I',4 if network else 0,connection,0)
  entries=[(0x100,OBJ)]
  names={'first':[0x2edb780f],'modal match':[0x56a1eae3],'modal other':[0x56a1eae3],
   'third':[0x31631b98],'modal then third':[0x56a1eae3,0x31631b98],
   'all':[0x2edb780f,0x56a1eae3,0x31631b98]}.get(mode,[])
  for i,name in enumerate(names):
   o=OBJ+(i+1)*512;self.put(o+0x14,'<I',name);entries.append((name,o));self.ui.append(o)
   if name==0x56a1eae3:
    self.put(o+0x20,'<I',self.structure([(0xcdc00e63,13,0xf649d637 if mode=='modal match' else 123),
     (0x100,3,self.text('copied menu state')),(0x101,12,self.array(1,[5,7,9]))]))
  self.put(EM+8,'<I',self.table(entries))
 def run(self,calls,label,changes=None):
  for reg,value in [(UC_X86_REG_FPSW,0),(UC_X86_REG_FPTAG,0xffff),(UC_X86_REG_MXCSR,0x1f80)]:oracle.cpu.reg_write(reg,value)
  try:s=case(calls,self.patches(),changes,label)
  except Exception:print('FAILED',label,flush=True);raise
  if len(labels)%50==0:print('Input callback cases',len(labels),flush=True)
  return s
def update(fn=0x41f090,packet=PACKET):return call(fn,P,[packet])
def event(byte=6,mask=0x40,button=P+0x20,packet=PACKET):return call(0x41ebf0,P,[packet,byte,mask,0x5c8faa09,0xb27804a2,button])
for source in [False,True]:
 for destination in [False,True]:
  g=InputGraph();dest=g.structure([(0x100,13,9),(0x101,1,88)] if destination else [])
  g.put(OBJ+0x20,'<I',g.structure([(0x100,13,4),(0x102,3,g.text('copied'))]) if source else 0)
  g.run([call(0x460820,OBJ,[dest])]*2,f'parameter merge/{source}/{destination}')
for active in [False,True]:
 for mode in ['absent','first','modal match','modal other','third','modal then third','all']:
  g=InputGraph();g.gate(mode,active);s=g.run([call(0x41ef20)]*2,f'UI gate/{active}/{mode}')
  assert s[0]['result']==int(active and mode not in ['absent','modal other']),(active,mode,s[0]['result'])
# First and second connection, disabled flags, references already linked.
for flags,connections in itertools.product([0,1,4,8,12,0xffffffff],[(None,None),(8,None),(None,0),(8,0),(8,8),(0,8)]):
 g=InputGraph();g.gate('first');cs=[]
 for value in connections:
  c=g.alloc(0x1e88) if value is not None else 0
  if c:g.put(c+0x1e84,'<I',value)
  cs.append(c)
 g.put(NET,'<3I',flags,*cs);g.run([call(0x41ef20)],f'connection predicate/{flags}/{connections}')
for enabled,disabled,secondary,old,pressed in itertools.product([0,1,255],[0,1],[0,1],[0,0x40],[0,1,255]):
 g=InputGraph();g.put(P+0x498,'<3B',disabled,secondary,enabled);g.put(P+0x18,'<2I',old,0xa5a50000)
 g.packet(buttons=[(6,pressed)]);g.run([event()]*2,f'button event flags/{enabled}/{disabled}/{secondary}/{old}/{pressed}')
for raw in [0,0x80000000,bits(-1),bits(.75),bits(999.75),bits(1000),bits(1000.75),bits(1001),
 bits(2147483648),bits(4294967296),0x7f800000,0xff800000,0x7fc12345]:
 for now in [0,1000,1001,0x80000000,0xffffffff]:
  for pressed in [0,255]:
   g=InputGraph();g.put(P+0x18,'<I',0x40 if not pressed else 0);g.put(P+0x3c,'<I',raw)
   g.packet(buttons=[(6,pressed)]);g.run([event()],f'integer suppression/{raw:x}/{now}/{pressed}',{0x7d1ec8:now})
for button in [0,P+0x20]:
 for mask in [0,1,0x40,0x80000000,0xffffffff]:
  g=InputGraph();g.packet(buttons=[(6,1)]);g.run([event(mask=mask,button=button)],f'null button and arbitrary mask/{button}/{mask}')
for i,(byte,mask,press,release,offset) in enumerate(EVENTS):
 for value in [1,255]:
  g=InputGraph();g.packet(buttons=[(byte,value)])
  g.run([update(0x41eca0)]*2+[update(0x41eca0,RELEASE)]*2,f'aggregate ordered edge/{i}/{value}')
# Event delivery wakes the real recipient's script, including saved call frames.
for byte,mask,press,release,offset in EVENTS:
 for releasing in [False,True]:
  g=InputGraph();s=g.alloc(244);g.image[s-BASE:s-BASE+244]=bytes(244)
  g.put(OBJ+0x10,'<I',s);g.put(s+0xa4,'<2I',3,release if releasing else press)
  g.put(s+0x30,'<I',2);g.put(s+0x94,'<I',s+0x34)
  for i,name in enumerate([press,release]):g.put(s+0x34+48*i+32,'<3I',name,777,0xabc00003)
  g.put(P+0x1c,'<I',mask if releasing else 0);g.packet(buttons=[(byte,0 if releasing else 255)])
  g.run([update()],f'real script waits/{byte}/{releasing}')
  assert oracle.word(s+0xa4)==0
# Real cached QB handler enters and returns through the existing interpreter.
for mode in ['absent','first','modal match','modal other']:
 g=InputGraph();g.gate(mode);s=g.alloc(244);g.image[s-BASE:s-BASE+244]=bytes(244)
 g.put(s+0x10,'<2I',g.structure([]),g.structure([]));g.put(s+0x2c,'<I',s+0x1c);g.put(s+0x94,'<I',s+0x34)
 g.put(s+0xbc,'<3I',OBJ,0,0);g.put(OBJ+4,'<I',s+0xbc);g.put(OBJ+0x10,'<I',s)
 table=g.alloc(16);entries=g.alloc(40);g.put(table,'<2IBBHI',entries,2,1,0,0,0);g.put(s+0xe0,'<I',table)
 key=0x77110000;code=g.alloc(8);g.put(code,'<2B',1,0x24);entry=g.alloc(20);g.put(entry,'<5I',key,code,5,0,0)
 blob=g.alloc(20);g.put(blob,'<3I2B',0,2,2,1,0x24);g.symbol(key,7,blob)
 g.put(CACHE+20,'<4I',g.table([(key,entry)]),0,0,0)
 for i,name in enumerate([0x5c8faa09,0xb27804a2]):g.put(entries+i*20,'<5I',name,key,0,g.structure([(123,1,456)]),0)
 g.packet(buttons=[(6,255)]);g.run([update(),update(packet=RELEASE)],'real QB event handlers/'+mode)
for fill in [0,0xa5,255]:
 for mode in ['absent','first','modal match','modal other','third']:
  g=InputGraph(fill);g.gate(mode);g.packet(buttons=[(i,255) for i,_,_,_,_ in EVENTS],axes=(255,0,15,230),flags=0x700)
  g.run([update(),update(),update(packet=RELEASE),update(packet=RELEASE)],f'primary all edges/{fill}/{mode}')
for ownerflag,disabled,secondary,gate,callback in itertools.product([0,1,2,0xffffffff],[0,1],[0,255],['absent','first'],[False,True]):
 g=InputGraph(0xa5);g.gate(gate);g.put(OBJ+0x104,'<I',ownerflag);g.put(P+0x498,'<2B',disabled,secondary)
 g.packet(buttons=[(6,255),(10,255)],axes=(200,15,33,244),flags=0x700)
 calls=[call(0x41f170,args=[TASK]),call(0x41f190,args=[TASK])] if callback else [update(),update(0x41f100)]
 g.run(calls*2,f'pad callback gates/{ownerflag}/{disabled}/{secondary}/{gate}/{callback}')
# Packet aliases component bytes, making event/decoder read order observable.
rng=random.Random(0x41f090)
for n in range(64):
 g=InputGraph(n%3);data=bytes(rng.randrange(256) for _ in range(32));at=P+rng.choice([0x18,0x20,0x40,0x100,0x258,0x300])
 g.image[at-BASE:at-BASE+32]=data
 g.run([update(packet=at),update(0x41f100,at)],f'overlapping packet/{n}')
scope='Eight complete original bodies: object-parameter merge; single and ordered17-button targeted events; network/menu input gate; primary/secondary packet updates; two device-task callbacks. Real event dispatcher, registered UI recipient, log, references, structure ownership and pad decoding execute. Valid UI modal parameters include checksum cdc00e63; absent value reads an uninitialized original stack slot and is deliberately outside contract. Successful temporary allocations and initialized services required. Exact full arena/globals/heap/returns; no arithmetic masks. Synthetic initialized component/tasks; task registration, component lifecycle and skater startup are not yet recovered here. No playable scene.'
# Preserve unexercised allocation-failure instructions honestly, without exclusions.
report_coverage={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),
 'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
used={s['fn'] for c in oracle.cases for s in c['steps']}
fixture={'base':BASE,'memory':'input-callbacks-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm',
 'memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],
 'globals':globals_,'functions':{k:v for k,v in functions.items() if k in used},'float_fields':[],
 'cases':oracle.cases,'case_labels':labels,'scope':scope,'pointer_exports':exports,'pointer_fields':sorted(fields),**extra}
(folder/fixture['memory']).write_bytes(initial)
(folder/'input-callbacks-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(oracle.counts.values()),
 'instruction_coverage':report_coverage,'counts':dict(oracle.counts),'callees':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'scope':scope}
(folder/'input-callbacks-original.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['callees','counts','scope']}),flush=True)
