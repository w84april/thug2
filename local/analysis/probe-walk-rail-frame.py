"""Original rail climbing, exits and real QB animation completion."""
from pathlib import Path
exec(compile(Path('local/analysis/probe-walk-grounded.py').read_text().split('for moving,height,flags')[0],'<preserved collision and original-write provenance>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x441020,75,'thug_walk_rail_bottom_finish_draft',0,'void',True,True,True),
 (0x441070,75,'thug_walk_rail_top_finish_draft',0,'void',True,True,True),
 (0x441860,79,'thug_walk_rail_air_finish_draft',0,'void',True,True,True),
 (0x441680,466,'thug_walk_rail_bottom_exit_draft',0,'void',False,False,True),
 (0x441b80,601,'thug_walk_rail_top_exit_draft',0,'void',False,False,True),
 (0x442280,806,'thug_walk_rail_climb_draft',0,'void',False,False,True),
 (0x4425b0,178,'thug_walk_rail_frame_draft',0,'void',True,True,True)]
for row in specs:bind_new(*row);oracle.cpu.hook_add(UC_HOOK_CODE,observe_cache,begin=row[0],end=row[0])
extra_roots=[(0x417760,'thug_collision_probe_initialize',0,'word',False,False),
 (0x5298d0,'thug_walk_finish_transition_draft',0,'void',True,True),
 (0x52ad10,'thug_walk_transition_frame_draft',0,'void',True,False),
 (0x4738e0,'thug_script_initialize',0,'word',False,False),
 (0x474540,'thug_script_setup',4,'void',True,True),
 (0x4750b0,'thug_script_execute',0,'word',True,True)]
for row in extra_roots:
 bind(*row)
 if row[0]!=0x417760:oracle.cpu.hook_add(UC_HOOK_CODE,observe_cache,begin=row[0],end=row[0])
for at,name in [(0x441020,'thug_walk_rail_bottom_finish_draft'),(0x441070,'thug_walk_rail_top_finish_draft'),(0x441860,'thug_walk_rail_air_finish_draft'),(0x52a180,'thug_walk_finish_command_draft')]:function_exports.append([at,name])
entries={x[0] for x in specs+extra_roots};returns=set()
for at in entries:
 for ins in Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(at-0x400000,0x3000),at):
  if ins.mnemonic=='int3':break
  if ins.mnemonic=='ret':returns.add(ins.address)
def rail_root(cpu,at,size,user):
 global source_probe,copy_destination,source_undefined
 sp=cpu.reg_read(UC_X86_REG_ESP)
 if at in entries and oracle.word(sp)==oracle.stop:source_probe=copy_destination=0;root_records.append({'stack_pointer_fields':[]})
 elif at in returns and oracle.word(sp)==oracle.stop:
  root_records[-1]['indeterminate_words']=sorted(undefined_words);root_records[-1]['indeterminate_provenance']=[undefined_provenance[a].copy() for a in sorted(undefined_words)]
 elif at==0x417760 and oracle.word(sp)==0x441c4c:source_probe=cpu.reg_read(UC_X86_REG_ECX);source_undefined={0x70,0xa8}
for at in entries|returns:oracle.cpu.hook_add(UC_HOOK_CODE,rail_root,begin=at,end=at)
AP,AS,CH,SCRIPT=P+0x13000,P+0x13100,P+0x13200,P+0x14000
parameters={**required_parameters,0x6da7f696:30,0xaebfa9cd:40,0xcaf2831b:20,0xb620b580:20,0x5296e3fd:12,0x76bf49e0:12,0x35b3bbda:6,0x0ab2db54:100,0x7ee1b95b:45}
class RailFrameGraph(GroundedGraph):
 def __init__(self,fraction=.5,angle=0,dt=.1,backward=False,transform=False):
  super().__init__();self.parameters(overrides=parameters);self.put(P+0x18,'<I',3);self.put(P+0x1c,'<I',1000)
  self.put(P+0x48,'<4f',0,0,1,1);self.put(P+0x1878,'<4f',0,0,1,1);self.put(P+0x94,'<f',1);self.put(P+0x80,'<f',dt)
  self.put(INPUT+0x248,'<f',angle);self.put(GATE+0x18,'<I',0);self.put(P+0x18cc,'<f',fraction)
  nodes=ledge_nodes(self,[(0,0,0),(0,100,0)],[(None,1),(0,None)] if backward else [(1,None),(None,0)],[0x24,0x24]);self.nodes=nodes
  for i,node in enumerate(nodes):self.put(node+0x4c,'<I',0x110+i)
  self.put(P+0x1764,'<I',nodes[0]);self.put(P+0x176c,'<I',RAIL);self.put(PHYSICS+0x22c,'<2I',nodes[0],RAIL)
  self.put(P+0x24,'<4f',0,fraction*100,-6,1);self.put(OBJ+0x4c,'<4f',0,fraction*100,-6,1)
  if transform:self.put(RAIL,'<16f',*IDENTITY[:12],10,20,30,1);self.put(RAIL+0x50,'<B',1)
  self.image[AP-BASE:CH-BASE+0x100]=bytes(CH-AP+0x100);self.put(P+0x1774,'<I',AP)
  self.put(AP+0x34,'<I',AS);self.put(AS+4,'<I',1);self.put(AS+0x20,'<I',CH);self.put(CH+4,'<I',1);self.put(CH+0x14,'<3f',0,.5,1)
 def scripts(self,actors=(),mutation='observe'):
  rows=[(0x110,[(0x2ca8a299,13,6)]),(0x111,[(0x2ca8a299,13,6)])]
  rows.extend((self.word(actor+4),[(0x2ca8a299,13,6)]) for actor in actors)
  rows.extend((self.word(owner+0x14),[]) for owner in self.owners)
  self.level_nodes(rows);self.callback({'observe':[],'cancel':[(CONTROL+0x24,0x10000)],'position':[(P+0x28,bits(77))],'probe':[(P+0x1864,0)]}[mutation])
 def finish_script(self):
  self.put(OBJ+0x100,'<I',P);self.put(P+16,'<I',HANG)
  descriptor=self.alloc(24);self.put(descriptor,'<6I',0x9d3eebe8,0x726e85aa,0x52a180,0,0,0);fields.add(descriptor+8)
  self.symbol(0x9d3eebe8,9,descriptor);self.cached(0x77123456,b'\x01\x16'+struct.pack('<I',0x9d3eebe8)+b'\x01\x24');self.image[SCRIPT-BASE:SCRIPT-BASE+0x150]=bytes(0x150)
records=[]
def run(g,calls,label,changes=None):
 stages=run_grab(g,[call(0x417760,P+0x17b4),*calls],label,{0x7d1ec8:0,0x696d60:1000,**(changes or {})})
 records.append({'label':label,'calls':len(stages),'state':oracle.word(P+0x18),'event':oracle.word(P+0x78),'callback':oracle.word(P+0x1948),'callbacks':oracle.word(CBSTATE),'position':bytes(oracle.cpu.mem_read(P+0x24,16)).hex()})
 return stages
for at,moving,height,facing in itertools.product([0x441680,0x441b80],[False,True],[-100,0,40,60,100],[(0,0,1,1),(.6,0,.8,0)]):
 g=RailFrameGraph();g.plane(height,moving=moving,half=256);g.put(P+0x48,'<4f',*facing)
 run(g,[call(at,P,[Q]),call(0x5298d0,P)],f'exit and complete {at:x}/{moving}/{height}/{facing}')
 assert oracle.word(P+0x18) in [0,1]
for fraction,dt,angle,amount in itertools.product([0,.1,.5,.9,1],[0,.1,1],[0,.8,1.57079637,3.14159274],[0,1]):
 g=RailFrameGraph(fraction,angle,dt);g.put(P+0x94,'<f',amount)
 run(g,[call(0x442280,P,[Q])],f'climb fraction {fraction}/{dt}/{angle}/{amount}')
for fraction,margin in itertools.product([-.2,0,.5,1,1.2],[-50,0]):
 g=RailFrameGraph(fraction,dt=0);g.parameters(overrides={**parameters,0x5296e3fd:margin,0x76bf49e0:margin})
 run(g,[call(0x442280,P,[Q])],f'rail endpoint clamp {fraction}/{margin}')
for angle,age,backward,transform in itertools.product([0,.8,1.57079637,3.14159274],[0,24,25,0xffffffff],[False,True],[False,True]):
 g=RailFrameGraph(angle=angle,backward=backward,transform=transform);g.put(P+0x1c,'<I',(1000-age)&0xffffffff)
 run(g,[call(0x4425b0,P,[Q])]*2,f'rail frame cone age {angle}/{age}/{backward}/{transform}')
for at,moving,mutation in itertools.product([0x441680,0x441b80],[False,True],['observe','cancel','position','probe']):
 g=RailFrameGraph();actor,owner=g.plane(40,moving=moving,half=256,flags=0x40);g.scripts([actor],mutation);g.finish_script()
 calls=[call(at,P,[Q]),call(0x52ad10,P),call(0x4738e0,SCRIPT),call(0x474540,SCRIPT,[0x77123456,0,0,OBJ]),call(0x4750b0,SCRIPT)]
 run(g,calls,f'rail exit animation QB {at:x}/{moving}/{mutation}')
 assert oracle.word(CBSTATE)>0
scope='Candidate complete rail climbing442280/frame4425b0, lower/upper exits441680/441b80 and ground/air completion callbacks441020/441070/441860, with real collision and QB animation-completion paths. Common-frame rail integration and playable training remain unfinished.'
extra={**extra,'cache_capture':'destructor-v1','pointer_globals':sorted(set(extra.get('pointer_globals',[])+[index[0x6918ec+i*4] for i in range(8)])),
 'indeterminate_word_addresses':[a+x for a in [P+0x17b4,*[P+0xbc+i*0xcc for i in range(8)]] for x in [0x70,0xa8]],
 'stack_probe_pointer_fields':[a+0x64 for a in [P+0x17b4,*[P+0xbc+i*0xcc for i in range(8)]]],
 'native_callbacks':[{'module':'walk-grounded-diagnostics.wasm','export':'fixture_walk_grounded_print','slots':[DIAG+4]},{'module':'trigger-callback.wasm','export':'fixture_trigger_native','original':CBNATIVE}]}
saved=coverage.copy();coverage.clear();finish('walk-rail-frame',scope,{},extra);coverage.update(saved)
report=json.loads((folder/'walk-rail-frame-original.json').read_text());report['records']=records
report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
(folder/'walk-rail-frame-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n')
(folder/'walk-rail-frame-original.json').write_text(json.dumps(report,indent=2)+'\n');print(report['instruction_coverage'])
