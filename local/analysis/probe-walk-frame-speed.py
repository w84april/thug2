"""Original Walk speed-parent, pooled parameters and populated queues."""
from pathlib import Path
exec(compile(Path('local/analysis/probe-walk-speed.py').read_text().split('for count,direction')[0],'<speed graph>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
bind_new(0x52a2c0,760,'thug_walk_animation_speed_draft',0,'void',True,True,True)
oracle.cpu.hook_add(UC_HOOK_CODE,observe_cache,begin=0x52a2c0,end=0x52a2c0)
exports.append([0x645d8c,'thug_animation_checksum_pending_methods_draft']);fields.add(AP)
commands=[];speed_calls=[];records=[]
def dispatch(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP)
 if at==0x419950:
  params=oracle.word(sp+8);node=oracle.word(params+4)
  commands.append({'method':hex(at),'caller_return':hex(oracle.word(sp)),'command':hex(oracle.word(sp+4)),'script':oracle.word(sp+12),'parameter_name':hex(oracle.word(node+4)),'parameter_bits':oracle.word(node+8)})
  assert oracle.word(sp+4)==0xbd4edd44 and oracle.word(sp+12)==0
 elif at==0x419967:
  assert cpu.reg_read(UC_X86_REG_EAX)==2;commands[-1]['return']=2
 else:
  assert at==0x419b90;speed_calls.append({'speed_bits':oracle.word(sp+4),'send':oracle.word(sp+8),'all':oracle.word(sp+12),'relative':oracle.word(sp+16)})
for at in [0x419950,0x419967,0x419b90]:oracle.cpu.hook_add(UC_HOOK_CODE,dispatch,begin=at,end=at)
# The speed helper is now nested beneath the real walking parent. Preserve its
# byte-write provenance, and snapshot still-undefined destinations at every root
# boundary so later original writes revoke allowances before the next comparison.
def save_payload_record():
 if payload_records:
  payload_records[-1]['indeterminate_bytes']=sorted(undefined_bytes)
  payload_records[-1]['payload_provenance']=[undefined_bytes[a].copy() for a in sorted(undefined_bytes)]
def frame_payload_entry(cpu,at,size,user):
 global payload_source,payload_writes
 sp=cpu.reg_read(UC_X86_REG_ESP)
 if hex(at) in functions and oracle.word(sp)==oracle.stop:
  save_payload_record();payload_records.append({});payload_source=0
 if at==0x47e850:payload_source=sp-0x28;payload_writes={i:0 for i in range(8)}
 elif at in [0x47e929,0x419ba2,0x47e9ce,0x47ea0a,0x47ea31]:payload_source=0
payload_entry.__code__=frame_payload_entry.__code__
oracle.cpu.hook_add(UC_HOOK_CODE,payload_entry,begin=0x52a2c0,end=0x52a2c0)
def case(calls,patches=(),changes=None,label='walking animation speed'):
 global payload_source,component_root
 payload_source=0;component_root=False;payload_records.clear();undefined_bytes.clear()
 stages=speed_base_case(calls,patches,changes,label);save_payload_record()
 assert len(stages)==len(payload_records),(label,len(stages),len(payload_records))
 for stage,record in zip(stages,payload_records):stage.update(record)
 return stages
for name,at,offset in [('thug_script_structure_pool_index',0x6f3614,0),('thug_script_structure_pools',0x6f361c,0),('thug_script_structure_pools',0x6f3620,4)]:
 if at not in index:glob(name,at,0,offset=offset)
 else:defaults[index[at]]=0
PEER,LINK=P+0x1f000,P+0x1f200
class FrameSpeedGraph(SpeedGraph):
 def __init__(self,mode=3,control=1,network=1,speed=30,previous=0,span=2,direction=0):
  super().__init__(direction=direction);self.parameters(overrides={**required_parameters,0x1a47ffab:2,0x0ab2db54:4})
  self.put(AP,'<I',0x645d8c);self.put(P+0x700,'<If',mode,speed);self.put(P+0x17b0,'<f',span);self.put(P+0x18e0,'<f',previous);self.put(CONTROL+0x24,'<B',control)
  self.put(NET,'<3I',4 if network else 0,CLIENT,0);self.put(CLIENT+0x1e84,'<I',0)
 def populated(self):
  self.network('populated');self.put(CLIENT+8,'<I',0xfffffffa)
  self.put(CLIENT+0x1e8c,'<5I',0,0xffffffff,0,LINK,LINK);self.put(LINK,'<5I',0,PEER,0,CLIENT+0x1e8c,CLIENT+0x1e8c)
  for offset in [0,20,40]:self.put(PEER+offset,'<5I',0,0xffffffff,0,PEER+offset,PEER+offset)
  self.put(PEER+0x3c,'<I',17);self.put(PEER+0x60,'<I',1)
 def pool(self,count=4):
  pool=self.alloc(0x5c);blocks=self.alloc(count*16);self.image[pool-BASE:pool-BASE+0x5c]=bytes(0x5c)
  self.put(pool,'<6I',blocks,blocks+count*16,0,0,0,blocks)
  for i in range(count):self.put(blocks+i*16,'<I',blocks+(i+1)*16 if i+1<count else 0)
  return pool
 def run_speed(self,label,steps=2,pool=None):
  commands.clear();speed_calls.clear();changes={0x7cce14:NET}
  if pool is not None:changes.update({0x6f3614:pool,0x6f361c+4*pool:self.pool()})
  stages=self.run([call(0x52a2c0,P)]*steps,label,changes)
  messages=[]
  if self.word(CLIENT+0x1e8c+12)==LINK:
   node=oracle.word(PEER+16)
   while oracle.word(node+4)!=0xffffffff:
    message=oracle.word(node+20);payload=oracle.word(message+4)
    assert oracle.word(message+8)==1 and oracle.cpu.mem_read(message,1)==b'\x41'
    assert int.from_bytes(oracle.cpu.mem_read(message+2,2),'little')==8 and oracle.cpu.mem_read(payload+4,1)==b'\x34'
    messages.append({'node':node,'message':message,'payload':payload,'speed_bits':oracle.word(payload)})
    node=oracle.word(node+16)
  records.append({'label':label,'steps':steps,'mode':self.word(P+0x700),'pool':pool,'commands':list(commands),'speed_calls':list(speed_calls),'messages':messages,'channel_speed_bits':oracle.word(CHANNELS+0x20),'retained_network_speed_bits':oracle.word(P+0x18e0)})
  return stages

for mode,control,network,speed,previous in itertools.product([0,1,2,3,4],[0,1],[0,1],[0,2,30],[0,1]):
 g=FrameSpeedGraph(mode,control,network,speed,previous);g.run_speed(f'parent modes/{mode}/{control}/{network}/{speed}/{previous}',steps=1)
 assert len(commands)==int(mode in [2,3] or (mode==1 and control)) and all(x['return']==2 for x in commands)
 assert len(speed_calls)==int(mode in [1,2,3])
for span,control in itertools.product([-10,-0.0,0,.125,2],[0,1,255]):
 g=FrameSpeedGraph(mode=1,span=span,control=control);g.run_speed(f'mode1 span/control/{span}/{control}')
 assert len(speed_calls)==(2 if span>0 else 0)
for mode,pool,control in itertools.product([1,2,3],[0,1],[0,1]):
 g=FrameSpeedGraph(mode=mode,control=control);g.run_speed(f'selected structure pool/{mode}/{pool}/{control}',steps=3,pool=pool)
# Adjacent binary32 values around the original0.1 send threshold, both signs;
# repeated calls must stop retransmitting after the stored speed is updated.
for raw,negative,network in itertools.product([0x3dcccccb,0x3dcccccc,0x3dcccccd,0x3dccccce,0x3dcccccf],[False,True],[False,True]):
 speed=struct.unpack('<f',struct.pack('<I',raw|(0x80000000 if negative else 0)))[0]
 g=FrameSpeedGraph(speed=speed*4,previous=0,network=network);g.populated();g.run_speed(f'network threshold/{raw:x}/{negative}/{network}',steps=3)
 assert speed_calls[0]['send']==int(network and raw>=0x3dcccccd)
 assert all(x['send']==0 for x in speed_calls[1:])
 assert len(records[-1]['messages'])==int(network and raw>=0x3dcccccd)
for mode,direction,pool in itertools.product([1,2,3],[0,0xffffffff],[None,0,1]):
 g=FrameSpeedGraph(mode=mode,direction=direction,speed=30);g.populated();g.run_speed(f'populated pooled queue/{mode}/{direction}/{pool}',steps=3,pool=pool)
 assert len(records[-1]['messages'])==int(mode==3)
for active,channels in itertools.product([False,True],[False,True]):
 g=FrameSpeedGraph();g.populated()
 if not active:g.put(AS+4,'<I',0xffffffff)
 if not channels:g.put(AS+0x20,'<I',SENTINEL)
 g.run_speed(f'empty animation state/channel/{active}/{channels}',steps=2)
 assert len(records[-1]['messages'])==int(active and channels)
scope='Complete Walk animation-speed parent with exact mode/control, sign/zero and adjacent binary32 network thresholds, repeated updates, both selected parameter pools and populated original queues. The fixed bd4edd44 virtual checksum follows the original unhandled419950 prefix; its two recognized commands remain explicit traps and earn no recovery count. Defined arena/global/heap/payload bytes compare; only original-write-proven three-byte payload padding is indeterminate. Shared Walk frame and playable training remain unfinished.'
extra={**extra,'indeterminate_byte_addresses':sorted(payload_destinations),'payload_source_stack':[oracle.stack,oracle.stack+0x20000]}
saved=coverage.copy();coverage.clear();finish('walk-frame-speed',scope,{},extra);coverage.update(saved)
report=json.loads((folder/'walk-frame-speed-original.json').read_text());report['flow_records']=records;report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
(folder/'walk-frame-speed-original.json').write_text(json.dumps(report,indent=2)+'\n');print('ORIGINAL',len(records),'parent cases',report['instruction_coverage'])
