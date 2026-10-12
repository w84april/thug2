"""Original full airborne frames, with all gameplay callees executing unchanged."""
from pathlib import Path
exec(compile(Path('local/analysis/probe-walk-grounded.py').read_text().split('for moving,height,flags')[0],'<preserved contacts, geometry and write provenance>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x52cef0,1033,'thug_walk_air_frame_draft',0,'void',True,True,True)]
for row in specs:
 bind_new(*row);oracle.cpu.hook_add(UC_HOOK_CODE,observe_cache,begin=row[0],end=row[0])
def air_root(cpu,at,size,user):
 global source_probe,copy_destination,source_undefined
 sp=cpu.reg_read(UC_X86_REG_ESP)
 if at==0x52cef0 and oracle.word(sp)==oracle.stop:source_probe=copy_destination=0;root_records.append({'stack_pointer_fields':[]})
 elif at==0x52d2f8 and oracle.word(sp)==oracle.stop:
  root_records[-1]['indeterminate_words']=sorted(undefined_words)
  root_records[-1]['indeterminate_provenance']=[undefined_provenance[a].copy() for a in sorted(undefined_words)]
 elif at==0x417760 and oracle.word(sp)==0x52a728:source_probe=cpu.reg_read(UC_X86_REG_ECX);source_undefined={0x70,0xa8}
for at in [0x52cef0,0x52d2f8,0x417760]:oracle.cpu.hook_add(UC_HOOK_CODE,air_root,begin=at,end=at)
source=Path('local/analysis/probe-walk-grounded.py').read_text()
source=source[source.index('def grounded_debug'):source.index('# Collect only literal')].replace("message==b'WALKING_GROUND, within moving object'","message in [b'WALKING_GROUND, within moving object',b'WALKING_AIR, within moving object']")
exec(compile(source,'<air diagnostics terminal observer>','exec'))
air_parameters={**required_parameters,0x896c8888:100,0xf085443b:4,0x530dcf34:2,0xa20c43b7:2,0x4d16f37d:4,0x420d18bc:200,0x12333ebd:1000,0x246d0bf3:.5,0x99510695:100,0x9ea1974a:48,0x48c0ac2a:60,0x06ebbab7:12,0xa5e2da58:900,0xe6e0c0a4:100}
class AirFrameGraph(GroundedGraph):
 def __init__(self):
  super().__init__();self.parameters(overrides=air_parameters)
  self.put(P+0x18,'<I',1);self.put(P+0x24,'<4f',0,100,0,1);self.put(P+0x68,'<4f',0,100,0,1);self.put(OBJ+0x4c,'<4f',0,100,0,1)
  self.put(P+0x34,'<4f',0,0,3,1);self.put(P+0x44,'<f',-10);self.put(P+0x80,'<f',.1)
  self.put(P+0x1878,'<4f',0,0,1,1);self.put(P+0x189c,'<4f',0,0,0,1);self.put(P+0x18ac,'<f',200)
  self.put(P+0x71c,'<4f',0,0,0,1);self.put(P+0x94,'<f',1);self.put(GATE+0x18,'<I',0);self.symbol(0x30ce7f2c,2,bits(80))
  for key in [0xd5349cc6,0x82135dd7,0x4c2b6df3]:self.symbol(key,2,bits(0))
records=[]
def run(g,label,repeats=1,changes=None):
 stages=run_grab(g,[call(0x52cef0,P,[Q])]*repeats,label,changes)
 records.append({'label':label,'calls':len(stages),'state':oracle.word(P+0x18),'event':oracle.word(P+0x78),'position':bytes(oracle.cpu.mem_read(P+0x24,16)).hex(),'callbacks':oracle.word(CBSTATE),'diagnostics':oracle.word(DLOG),'queries':len(trace)})
 return stages
for dt,vertical,amount in itertools.product([0,.016,.1,.5],[-100,0,100],[0,1]):
 g=AirFrameGraph();g.put(P+0x80,'<f',dt);g.put(P+0x44,'<f',vertical);g.put(P+0x94,'<f',amount)
 run(g,f'free trajectory {dt}/{vertical}/{amount}',2)
for threshold,lock,velocity in itertools.product([90,100,110],[0,.2],[(0,0,0,1),(1,2,3,1),(-1,0,-2,0)]):
 g=AirFrameGraph();g.put(P+0x18ac,'<f',threshold);g.put(P+0x1898,'<f',lock);g.put(P+0x189c,'<4f',*velocity)
 run(g,f'lip momentum {threshold}/{lock}/{velocity}',2)
for moving,kind in itertools.product([False,True],['floor','slide','ceiling','wall','cancel']):
 g=AirFrameGraph();g.put(P+0x24,'<4f',0,10,0,1);g.put(P+0x68,'<4f',0,10,0,1);g.put(OBJ+0x4c,'<4f',0,10,0,1);g.put(P+0x44,'<f',-100)
 if kind in ['floor','slide']:g.plane(0,moving=moving,half=128,flags=2 if kind=='slide' else 0)
 if kind=='ceiling':g.plane(20,moving=moving,up=False,half=128);g.put(P+0x44,'<f',100)
 if kind=='wall':g.obstacle('z',2,moving=moving)
 if kind=='cancel':g.put(CONTROL+0x26,'<B',1)
 run(g,f'air geometry {moving}/{kind}')
for moving,mutation in itertools.product([False,True],['observe','cancel','position','owner','velocity']):
 g=AirFrameGraph();g.put(P+0x24,'<4f',0,10,0,1);g.put(P+0x68,'<4f',0,10,0,1);g.put(OBJ+0x4c,'<4f',0,10,0,1);g.put(P+0x44,'<f',-100)
 actor,owner=g.plane(0,moving=moving,half=128,flags=0x40);g.trigger(mutation,g.word(actor+4))
 if moving:g.level_nodes([(0x111,[(0x2ca8a299,13,6)]),(g.word(actor+4),[(0x2ca8a299,13,6)]),(g.word(owner+0x14),[])])
 run(g,f'air landing callback {moving}/{mutation}');assert oracle.word(CBSTATE)>0
for shape,previous,age,suppressed in itertools.product(['empty','ledge','rail'],[0,2,3,4],[100,101,0xffffffff],[0,1]):
 g=AirFrameGraph();g.put(P+0x20,'<I',previous);g.put(P+0x1c,'<I',(1000-age)&0xffffffff);g.put(P+0x9a,'<B',suppressed)
 g.put(INPUT+0x100,'<B',1);g.put(P+0x80,'<f',0);g.put(P+0x44,'<f',0)
 if shape=='ledge':g.rail();height=-60
 else:height=50
 if shape=='rail':
  nodes=ledge_nodes(g,[(0,0,0),(0,100,0)],[(1,None),(None,0)],[0x24,0x24])
  for node in nodes:g.put(node+0x30,'<4f',0,0,0,1)
 g.put(P+0x24,'<4f',0,height,-10,1);g.put(P+0x68,'<4f',0,height,30,1);g.put(OBJ+0x4c,'<4f',0,height,-10,1)
 run(g,f'connected catch {shape}/{previous}/{age}/{suppressed}',changes={0x7d1ec8:0,0x696d60:1000})
 if shape!='empty' and not suppressed and (previous==0 or age>100):assert oracle.word(P+0x18)==(2 if shape=='ledge' else 3)
for kind,blocked in itertools.product(['empty','fixed','moving'],[0,1]):
 g=AirFrameGraph();g.put(INPUT+0x1a0,'<B',1);g.put(CONTROL+0x24,'<B',blocked);g.put(P+0x80,'<f',0)
 g.put(P+0x68,'<4f',-20,0,0,1);g.put(P+0x24,'<4f',20,0,0,1);g.put(OBJ+0x4c,'<4f',20,0,0,1)
 changes={}
 if kind=='fixed':g.grind_nodes()
 if kind=='moving':
  head,component,transform,nodes=g.moving_grind();g.put(g.word(component+12)+4,'<I',0);changes[0x6f0db8]=head
 run(g,f'connected grind {kind}/{blocked}',changes=changes)
for moving,reverse,pressed in itertools.product([False,True],[False,True],[0,1]):
 g=AirFrameGraph();g.put(P+0x24,'<4f',0,0,0,1);g.put(P+0x68,'<4f',0,0,0,1);g.put(OBJ+0x4c,'<4f',0,0,0,1)
 g.put(P+0x80,'<f',0);g.put(INPUT+0x1c0,'<2I',pressed,0);g.obstacle('z',2,moving,reverse)
 name=g.alloc(0x1bc0);g.image[name-BASE:name-BASE+0x1bc0]=bytes(0x1bc0);g.put(name,'<5I',0,0x270f56e1,0,OBJ,g.word(OBJ+0x100));g.put(OBJ+0x100,'<I',name)
 run(g,f'connected contact jump {moving}/{reverse}/{pressed}',changes={0x7d1ec8:0,0x696d60:1000})
for velocity,old,probe_floor in itertools.product([(0,0,0,1),(3,4,0,1),(20,3,-10,1)],[(0,0,0,1),(1000,0,0,1)],['none','static','moving']):
 g=AirFrameGraph();g.put(P+0x24,'<4f',0,0,0,1);g.put(P+0x68,'<4f',*old);g.put(OBJ+0x4c,'<4f',0,0,0,1);g.put(P+0x80,'<f',0);g.put(P+0x44,'<f',0)
 g.plane(40,moving=True,velocity=velocity,half=128)
 if probe_floor!='none':g.plane(-10,moving=probe_floor=='moving',half=128)
 run(g,f'enclosed by moving object {velocity}/{old}/{probe_floor}')
# Successful projectile scripts execute inside the air root, before landing.
# Their native observer can change live state, but no game callee is replaced.
import zlib
for mode,mutation,floor in itertools.product([0,1],['observe','cancel','position','velocity','inventory'],[False,True]):
 g=AirFrameGraph();g.put(P+0x24,'<4f',0,10,0,1);g.put(P+0x68,'<4f',0,10,0,1);g.put(OBJ+0x4c,'<4f',0,10,0,1);g.put(P+0x44,'<f',-100)
 if floor:g.plane(0,moving=False,half=128)
 name=g.alloc(0x1bc0);mark=g.alloc(0x38);walkmode=g.alloc(0x120)
 for address,size in [(name,0x1bc0),(mark,0x38),(walkmode,0x120)]:g.image[address-BASE:address-BASE+size]=bytes(size)
 g.put(PHYSICS+0x1518,'<I',name);g.put(PHYSICS+0x1528,'<I',STATE);g.put(PHYSICS+0x1530,'<I',GATE);g.put(PHYSICS+0x1538,'<I',mark)
 g.put(GATE+0x2c,'<I',walkmode);g.put(walkmode+0x1c,'<I',mode);g.put(PHYSICS+0x2f4,'<B',1);g.put(PHYSICS+0x2f8,'<I',2)
 g.put(name+0x998,'<2H',2,0)
 for slot,kind,time in [(0,2,0),(99,1,0xffffffff)]:g.put(name+0x38+slot*24,'<4IB3sI',time,kind,0x20689278,0xabcdef12,0,b'xyz',0)
 g.symbol(zlib.crc32(b'projectile_control')^0xffffffff,1,0x20689278)
 for script in [0x0ce5b783,0x3f356c63]:g.cached(script,b'\x01\x43'+struct.pack('<I',CBNATIVE)+b'\x01\x24')
 writes={'observe':[],'cancel':[(CONTROL+0x24,0x10000)],'position':[(P+0x28,bits(50))],'velocity':[(P+0x44,bits(200))],'inventory':[(PHYSICS+0x2f8,0)]}[mutation]
 g.callback(writes);run(g,f'projectile inside air frame {mode}/{mutation}/{floor}',changes={0x7d1ec8:0,0x696d60:1000})
 assert oracle.word(CBSTATE)==1 and oracle.word(PHYSICS+0x14c4)==30
 assert oracle.word(P+0x18)==int(not floor or mutation=='position')
# Keep the accepted ramp geometry shared with the existing transfer probe.
node=next(n for n in ast.parse((folder/'probe-walk-transfer.py').read_text()).body if isinstance(n,ast.ClassDef) and n.name=='TransferGraph')
ramp=next(n for n in node.body if isinstance(n,ast.FunctionDef) and n.name=='ramp');ramp.name='transfer_ramp'
exec(compile(ast.Module(body=[ramp],type_ignores=[]),'<preserved accepted transfer geometry>','exec'))
for moving,mode in itertools.product([False,True],[0,1]):
 g=AirFrameGraph();g.parameters(overrides={**air_parameters,0x7213ef07:500,0xcc461b87:100,0xc0491d2e:200});transfer_ramp(g,moving)
 g.symbol(0x8cbc89dd,10,g.structure([(0xfaa40754,2,bits(-800)),(0x95a79c32,2,bits(150))]))
 for key,value in [(0xc31ca696,1),(0x441c38a0,1),(0xbe33a41e,0),(0xe50a9d56,500),(0x32c20f7e,0)]:g.symbol(key,2,bits(value))
 g.symbol(0x9c8c6df1,1,0);walkmode=g.alloc(0x120);g.image[walkmode-BASE:walkmode-BASE+0x120]=bytes(0x120);g.put(walkmode+0x1c,'<I',mode)
 g.put(GATE+0x2c,'<I',walkmode);g.put(PHYSICS+0x1534,'<I',P);g.put(OBJ+0x100,'<I',P);g.put(P+16,'<I',0)
 g.put(P+0x80,'<f',0);g.put(P+0x1898,'<f',1);g.put(P+0x1868,'<f',.5)
 g.put(P+0x24,'<4f',0,100,-100,1);g.put(P+0x68,'<4f',0,100,-110,1);g.put(OBJ+0x4c,'<4f',0,100,-100,1);g.put(P+0x48,'<4f',0,0,1,0)
 g.put(P+0x34,'<4f',0,17,500,0);g.put(P+0x44,'<f',200);g.put(INPUT+0xc0,'<B',1);g.put(INPUT+0x120,'<B',1)
 run(g,f'transfer inside air frame {moving}/{mode}')
 if mode==1:assert oracle.word(P+0x78)==0x2eda83ea and oracle.word(P+0x748)==2,(moving,mode,records[-1],oracle.word(P+0x748))
scope='Complete airborne Walk52cef0 with real steering, contacts, integration, landing callbacks, ledge/rail catches, grind checks, successful transfers, projectile scripts, contact jumps and moving-object escape. The successful nested standard-wallplant callback still has separate helper evidence only. Full browser training remains unfinished.'
extra={**extra,'cache_capture':'destructor-v1','pointer_globals':sorted(set(extra.get('pointer_globals',[])+[index[0x6918ec+i*4] for i in range(8)])),
 'indeterminate_word_addresses':[a+x for a in [P+0x17b4,*[P+0xbc+i*0xcc for i in range(8)]] for x in [0x70,0xa8]],
 'stack_probe_pointer_fields':[a+0x64 for a in [P+0x17b4,*[P+0xbc+i*0xcc for i in range(8)]]],
 'native_callbacks':[{'module':'walk-grounded-diagnostics.wasm','export':'fixture_walk_grounded_print','slots':[DIAG+4]},{'module':'trigger-callback.wasm','export':'fixture_trigger_native','original':CBNATIVE}]}
saved=coverage.copy();coverage.clear();finish('walk-air-frame',scope,{},extra);coverage.update(saved)
report=json.loads((folder/'walk-air-frame-original.json').read_text());report['records']=records
report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
(folder/'walk-air-frame-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n')
(folder/'walk-air-frame-original.json').write_text(json.dumps(report,indent=2)+'\n');print(report['instruction_coverage'])
