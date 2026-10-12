"""Compare the original walking transfer check with real trajectory geometry."""
from pathlib import Path
exec(compile(Path('local/analysis/probe-walk-grab.py').read_text().split('for side,fraction,angle,kind')[0],'<preserved Walk collision graph>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x527600,280,'thug_walk_try_transfer_draft',0,'byte',True,True,True)]
for row in specs:
 bind_new(*row);oracle.cpu.hook_add(UC_HOOK_CODE,observe_cache,begin=row[0],end=row[0])
assert struct.unpack('<3I',pe.get_data(0x24c63c,12))==(2,4,0)
MODE=P+0x15000
class TransferGraph(GrabGraph):
 def __init__(self,speed=500,vertical=200,mode=1,submode=0,alternate=0):
  super().__init__();self.parameters(overrides={0x7213ef07:500,0xcc461b87:100,0xc0491d2e:vertical})
  self.symbol(0x8cbc89dd,10,self.structure([(0xfaa40754,2,bits(-800)),(0x95a79c32,2,bits(150))]))
  for key,value in [(0xc31ca696,1),(0x441c38a0,1),(0xbe33a41e,0),(0xe50a9d56,500),(0x32c20f7e,0)]:self.symbol(key,2,bits(value))
  self.symbol(0x9c8c6df1,1,0)
  self.image[MODE-BASE:MODE-BASE+0x120]=bytes(0x120);self.put(MODE+0x1c,'<I',mode);self.put(MODE+0x118,'<B',alternate)
  self.put(GATE+0x2c,'<I',MODE);self.put(PHYSICS+0x1534,'<I',P);self.put(OBJ+0x100,'<I',P);self.put(P+16,'<I',0)
  self.put(P+0x18,'<I',submode);self.put(P+0x1868,'<f',.5);self.put(P+0x1864,'<B',0)
  self.put(P+0x24,'<4f',0,100,-100,1);self.put(P+0x68,'<4f',0,100,-.01,1);self.put(P+0x48,'<4f',0,0,1,0)
  self.put(P+0x34,'<4f',0,17,speed,0);self.put(P+0x44,'<f',-7);self.put(INPUT+0xc0,'<B',1);self.put(INPUT+0x120,'<B',1)
 def ramp(self,moving=False,flags=8):
  actor,owner=self.plane(0,moving=moving,half=512,flags=flags);geo=self.word(actor+12)
  self.put(self.word(geo+48),'<9f',-512,1024,-512,512,1024,-512,0,-1024,512)
  self.put(geo+16,'<8f',-512,-1024,-512,1,512,1024,512,1)
  return actor,owner
 def trigger(self,mutation='observe'):
  self.put(P+0x1864,'<B',1);self.put(P+0x17b4+0x6d,'<B',1);self.put(P+0x17b4+0x58,'<I',0x111)
  self.put(OBJ+0x14,'<I',0x100);self.put(EM+8,'<I',self.table([(0x100,OBJ)]))
  self.level_nodes([(0x111,[(0x2ca8a299,13,6)])])
  writes={'observe':[],'cancel':[(CONTROL+0x24,0x10000)],'position':[(P+0x28,bits(50))],'velocity':[(P+0x34,bits(7)),(P+0x44,bits(99))]}[mutation]
  self.callback(writes)

records=[]
for field,value in itertools.product([P+0x9b,CONTROL+0x24,INPUT+0xc0,INPUT+0x120],[0,1,255]):
 g=TransferGraph();g.ramp();g.put(field,'<B',value)
 expected=(value==0 if field in [P+0x9b,CONTROL+0x24] else value!=0)
 stages=g.run([call(0x527600,P,[Q])]*2,f'transfer eligibility/{field:x}/{value}')
 assert all(x['result']==int(expected) for x in stages)
 records.append({'gate':hex(field),'value':value,'result':stages[0]['result'],'repeated':2})
for shape,mode,speed,vertical in itertools.product(['empty','ramp','missing surface flag'],[0,1],[0,.001,10,500],[-200,0,200,500]):
 g=TransferGraph(speed,vertical,mode)
 if shape!='empty':g.ramp(flags=0 if shape=='missing surface flag' else 8)
 stages=g.run([call(0x527600,P,[Q])],f'transfer search/{shape}/{mode}/{speed}/{vertical}')
 if shape!='ramp':assert stages[0]['result']==0
 records.append({'shape':shape,'mode':mode,'speed':speed,'vertical':vertical,'result':stages[0]['result'],'state':oracle.word(P+0x18)})
for moving,mutation in itertools.product([False,True],['none','observe','cancel','position','velocity']):
 g=TransferGraph();g.ramp(moving)
 if mutation!='none':g.trigger(mutation)
 stages=g.run([call(0x527600,P,[Q])],f'transfer/{moving}/{mutation}')
 records.append({'moving':moving,'mutation':mutation,'result':stages[0]['result'],'state':oracle.word(P+0x18),'callbacks':oracle.word(CBSTATE)})
 assert stages[0]['result']==1 and oracle.word(P+0x18)==int(mutation!='cancel')
 assert oracle.word(CBSTATE)==int(mutation!='none')
 print(records[-1],flush=True)
for previous,alternate,timer in itertools.product([0,1,2,4],[0,1],[(1000,0),(0xffffffff,1)]):
 g=TransferGraph(submode=previous,alternate=alternate);g.ramp()
 stages=g.run([call(0x527600,P,[Q])]*2,f'transfer previous state/alternate/time/{previous}/{alternate}/{timer}',{0x7d1ec8:timer[0],0x696d60:timer[1]})
 records.append({'previous':previous,'alternate':alternate,'timer':timer,'result':stages[0]['result'],'repeated':2})
scope='Candidate full Walk transfer check; real fixed/moving trajectory geometry and event callbacks. Other shared movement paths and playable training remain unfinished.'
# The old hardware-callback fixture overlaps this graph's input button bytes.
# Transfer only reads these buttons; it never calls those hardware methods.
extra={**extra,'pointer_globals':sorted(set(extra.get('pointer_globals',[])+[index[0x6918ec+i*4] for i in range(8)])),
 'native_callbacks':[{'module':'walk-floor-diagnostics.wasm','export':'fixture_walk_floor_print','slots':[DIAG+4]},{'module':'trigger-callback.wasm','export':'fixture_trigger_native','original':CBNATIVE}]}
saved=coverage.copy();coverage.clear();finish('walk-transfer',scope,{},extra);coverage.update(saved)
report=json.loads((folder/'walk-transfer-original.json').read_text());report['records']=records
report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
(folder/'walk-transfer-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n')
(folder/'walk-transfer-original.json').write_text(json.dumps(report,indent=2)+'\n');print(report['instruction_coverage'])
