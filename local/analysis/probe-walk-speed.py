"""Original channel-list speed propagation and component forwarding candidates."""
from pathlib import Path
source=Path('local/analysis/probe-walk-animation.py').read_text().split('for direction,alias')[0]
exec(compile(source,'<preserved animation graph>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x47e850,484,'thug_animation_state_speed_draft',4,'void',True,True,True),(0x419b90,21,'thug_animation_component_speed_draft',4,'void',True,True,True)]
for row in specs:
 bind_new(*row);functions[hex(row[0])]['float_args']=[0]
component_root=False
def speed_entry(cpu,at,size,user):
 global component_root
 if oracle.word(cpu.reg_read(UC_X86_REG_ESP))!=oracle.stop:return
 if at in [0x419ba2,0x47e9ce,0x47ea0a,0x47ea31]:component_root=False;return
 if at==0x419b90:component_root=True;observe_cache(cpu,at,size,user)
 elif not component_root:observe_cache(cpu,at,size,user)
for at in [0x419b90,0x47e850,0x419ba2,0x47e9ce,0x47ea0a,0x47ea31]:oracle.cpu.hook_add(UC_HOOK_CODE,speed_entry,begin=at,end=at)
# Trace the three payload bytes that have no defining write in the caller.
# Only actual copies at the original message constructor receive an allowance;
# subsequent writes revoke it. The speed and object-ID bytes stay exact.
from unicorn import UC_HOOK_MEM_WRITE
payload_source=0;payload_writes={};undefined_bytes={};payload_records=[];payload_destinations=set();queue_records=[]
def payload_entry(cpu,at,size,user):
 global payload_source,payload_writes
 sp=cpu.reg_read(UC_X86_REG_ESP)
 if at in [0x47e850,0x419b90] and oracle.word(sp)==oracle.stop:
  if at==0x419b90 or not component_root:payload_records.append({})
  if at==0x47e850:payload_source=sp-0x28;payload_writes={i:0 for i in range(8)}
 elif at in [0x419ba2,0x47e9ce,0x47ea0a,0x47ea31] and oracle.word(sp)==oracle.stop:
  payload_records[-1]['indeterminate_bytes']=sorted(undefined_bytes)
  payload_records[-1]['payload_provenance']=[undefined_bytes[a].copy() for a in sorted(undefined_bytes)]
  payload_source=0
 elif at==0x47e929:payload_source=0
for at in [0x419b90,0x47e850,0x419ba2,0x47e9ce,0x47ea0a,0x47ea31,0x47e929]:oracle.cpu.hook_add(UC_HOOK_CODE,payload_entry,begin=at,end=at)
def payload_write(cpu,access,address,size,value,user):
 for dest in list(undefined_bytes):
  if address<=dest<address+size:undefined_bytes.pop(dest)
 if payload_source:
  for i in range(8):
   if address<=payload_source+i<address+size:payload_writes[i]+=1
  if cpu.reg_read(UC_X86_REG_EIP)==0x45500e and cpu.reg_read(UC_X86_REG_ESI)==payload_source+4:
   assert size==4 and all(payload_writes[i]==1 for i in range(5)) and all(payload_writes[i]==0 for i in range(5,8))
   assert address==cpu.reg_read(UC_X86_REG_EDI) and HEAP<=address<BASE+len(initial)-4
   for i in range(1,4):
    dest=address+i;payload_destinations.add(dest)
    undefined_bytes[dest]={'destination':dest,'payload':address-4,'source':payload_source,'source_offset':i+4,'copy_instruction':'0x45500e','source_writes_before_copy':0,'defined_prefix_writes':[payload_writes[k] for k in range(5)]}
oracle.cpu.hook_add(UC_HOOK_MEM_WRITE,payload_write)
speed_base_case=case
def case(calls,patches=(),changes=None,label='animation speed'):
 global payload_source,component_root
 payload_source=0;component_root=False;payload_records.clear();undefined_bytes.clear()
 stages=speed_base_case(calls,patches,changes,label);assert len(stages)==len(payload_records),(len(stages),len(payload_records))
 for stage,record in zip(stages,payload_records):
  assert 'indeterminate_bytes' in record;stage.update(record)
 return stages
oracle.scope_entries[ALLOCATOR+0x20c]=4
exports.append([0x647578,'thug_plain_node_methods'])
CHANNELS,SENTINEL,NET,PLAYER,BODY,CLIENT=P+0x19000,P+0x19400,P+0x1c000,P+0x1c200,P+0x1c400,P+0x1d000
class SpeedGraph(AnimationGraph):
 def __init__(self,count=3,direction=0):
  super().__init__();self.image[CHANNELS-BASE:CLIENT-BASE+0x1eb0]=bytes(CLIENT+0x1eb0-CHANNELS)
  self.put(AS+0x20,'<I',CHANNELS if count else SENTINEL);self.put(AS+0x28,'<I',1);self.put(AS+0x68,'<I',BODY)
  self.put(SENTINEL+4,'<I',0xffffffff)
  for i in range(count):
   at=CHANNELS+i*0x100;self.put(at+4,'<I',i+1);self.put(at+0xc,'<I',at+0x100 if i+1<count else SENTINEL)
   self.put(at+0x14,'<4f',2,4,6+i*4,1);self.put(at+0x24,'<I',direction)
  self.put(ALLOCATOR+0x12c,'<I',ALLOCATOR+0x20c);self.put(BODY+0x14,'<I',0x1234);self.put(BODY+0x2bc,'<I',0)
  self.put(NET+0x11c,'<4I',0,0xffffffff,0,NET+0x11c)
 def network(self,kind):
  self.put(AS+0x28,'<I',0)
  if kind=='absent player':return
  node=NET+0x140;self.put(NET+0x128,'<I',node);self.put(node,'<4I',0,PLAYER,0,NET+0x11c)
  self.put(PLAYER+0x14,'<I',BODY);self.put(PLAYER+0x1d0,'<I',0 if kind=='inactive player' else 1)
  if kind=='absent client':return
  self.put(NET+8,'<I',CLIENT);sentinel=CLIENT+0x1e8c
  self.put(sentinel,'<5I',0,0xffffffff,0,sentinel,sentinel)
for count,direction,all_,relative,speed in itertools.product([0,1,3],[0,0xffffffff],[0,1,256],[0,1],[-2,0,1,59.94,60,120]):
 g=SpeedGraph(count,direction)
 g.run([call(0x47e850,AS,[bits(speed),1,all_,relative]),call(0x419b90,AP,[bits(speed),1,all_,relative])],f'channel speed/{count}/{direction}/{all_}/{relative}/{speed}')
for speed in [0,1,60]:
 g=SpeedGraph();g.put(AS+4,'<I',0xffffffff);g.run([call(0x419b90,AP,[bits(speed),1,0,1])],f'component sentinel/{speed}')
for kind,relative,direction in itertools.product(['absent player','inactive player','absent client','empty client'],[0,1],[0,0xffffffff]):
 g=SpeedGraph(direction=direction);g.network(kind)
 g.run([call(0x47e850,AS,[bits(30),1,1,relative])],f'channel speed/network gate/{kind}/{relative}/{direction}',{0x7cce14:NET})
# Real populated plain-message queue, repeated updates, both public roots and
# low-byte gates. No networking function or payload copy is replaced.
PEER,LINK=P+0x1f000,P+0x1f200
for root,all_,relative,send in itertools.product([0x47e850,0x419b90],[0,1],[0,1],[0,1,256,257]):
 g=SpeedGraph();g.network('populated');g.put(CLIENT+8,'<I',0xfffffffa)
 g.put(CLIENT+0x1e8c,'<5I',0,0xffffffff,0,LINK,LINK);g.put(LINK,'<5I',0,PEER,0,CLIENT+0x1e8c,CLIENT+0x1e8c)
 for offset in [0,20,40]:g.put(PEER+offset,'<5I',0,0xffffffff,0,PEER+offset,PEER+offset)
 g.put(PEER+0x3c,'<I',17);g.put(PEER+0x60,'<I',1)
 stages=g.run([call(root,AS if root==0x47e850 else AP,[bits(speed),send,all_,relative]) for speed in [30,30,90]],f'populated queue/{root:x}/{all_}/{relative}/{send}',{0x7cce14:NET})
 messages=[];node=oracle.word(PEER+16)
 while oracle.word(node+4)!=0xffffffff:
  message=oracle.word(node+20);payload=oracle.word(message+4)
  assert oracle.word(message+8)==1 and bytes(oracle.cpu.mem_read(message,1))==b'\x41'
  assert int.from_bytes(oracle.cpu.mem_read(message+2,2),'little')==8
  assert oracle.word(node+24)==0xfffffffa and oracle.word(node+8)==128
  assert oracle.cpu.mem_read(payload+4,1)==b'\x34'
  messages.append({'node':node,'message':message,'payload':payload,'speed_bits':oracle.word(payload)})
  node=oracle.word(node+16)
 expected_messages=(3 if all_ else 2) if send&255 else 0
 assert len(messages)==expected_messages,(root,all_,relative,send,messages)
 queue_records.append({'root':hex(root),'all':all_,'relative':relative,'send':send,'messages':messages})
scope='Original channel-list speed propagation, relative-length scaling and component forwarding, including real populated first-peer message queues and repeated updates. Defined payload bytes, heap, queue links, globals and arena compare exactly; only three original-write-proven uninitialized payload bytes are compared as indeterminate. No complete shared Walk frame or playable level is claimed.'
extra={**extra,'indeterminate_byte_addresses':sorted(payload_destinations),'payload_source_stack':[oracle.stack,oracle.stack+0x20000]}
saved=coverage.copy();coverage.clear();finish('walk-speed',scope,{},extra);coverage.update(saved)
report=json.loads((folder/'walk-speed-original.json').read_text());report['queue_records']=queue_records;report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
(folder/'walk-speed-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n')
(folder/'walk-speed-original.json').write_text(json.dumps(report,indent=2)+'\n');print(report['instruction_coverage'])
