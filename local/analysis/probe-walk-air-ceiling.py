"""Original airborne ceiling collision with real fixed/moving geometry."""
from pathlib import Path
exec(compile(Path('local/analysis/probe-walk-transfer.py').read_text().split('\nrecords=[]')[0],'<preserved Walk geometry and events>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x526ba0,603,'thug_walk_air_ceiling_draft',0,'void',True,True,True)]
for row in specs:
 bind_new(*row);oracle.cpu.hook_add(UC_HOOK_CODE,observe_cache,begin=row[0],end=row[0])
branch_hits=Counter()
for address in [0x526c76,0x526cb5,0x526d51,0x526d97,0x526dbd]:
 oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:branch_hits.update([at]),begin=address,end=address)
class CeilingGraph(TransferGraph):
 def __init__(self):
  super().__init__(submode=1);self.parameters(overrides={0x9ea1974a:48})
  self.put(P+0x24,'<4f',0,0,0,1);self.put(P+0x34,'<4f',2,0,3,1);self.put(P+0x44,'<f',10);self.put(GATE+0x18,'<I',0)
  self.put(P+0x18b0,'<B',0);self.put(OBJ+0x14,'<I',0x100);self.put(EM+8,'<I',self.table([(0x100,OBJ)]))
 def overhead(self,height=20,moving=False,tilt=0,reverse=False,flags=0):
  actor,owner=self.plane(height,moving=moving,half=128,flags=flags);geo=self.word(actor+12)
  if tilt:
   self.put(self.word(geo+48),'<9f',-128,height-128*tilt,-128,128,height+128*tilt,-128,0,height,128)
   self.put(geo+16,'<8f',-128,height-128*abs(tilt),-128,1,128,height+128*abs(tilt),128,1)
  if reverse:self.put(self.word(geo+12)+6,'<2H',1,2)
  return actor,owner
records=[]
for enabled,kind,vertical in itertools.product([0,1,255],['empty','ceiling','masked'],[-10,0,10]):
 g=CeilingGraph();g.put(P+0x18b0,'<B',enabled);g.put(P+0x44,'<f',vertical)
 if kind!='empty':g.overhead(flags=0x10 if kind=='masked' else 0)
 g.run([call(0x526ba0,P,[Q])]*2,f'ceiling gates/{enabled}/{kind}/{vertical}')
 records.append({'enabled':enabled,'kind':kind,'vertical':vertical})
for moving,height,vertical,reverse,tilt in itertools.product([False,True],[2,3,20,30,48,49],[-10,10],[False,True],[0,.5]):
 g=CeilingGraph();g.put(P+0x44,'<f',vertical);g.overhead(height,moving,tilt,reverse)
 g.run([call(0x526ba0,P,[Q])]*2,f'ceiling rays/{moving}/{height}/{vertical}/{reverse}/{tilt}')
 records.append({'moving':moving,'height':height,'vertical':vertical,'reverse':reverse,'tilt':tilt})
for moving,floor_moving,tilt in itertools.product([False,True],[False,True],[0,.5]):
 g=CeilingGraph();g.overhead(20,moving,tilt,reverse=True);g.overhead(-2,floor_moving)
 before=branch_hits[0x526d51]
 g.run([call(0x526ba0,P,[Q])]*3,f'ceiling second-surface recheck/{moving}/{floor_moving}/{tilt}')
 assert branch_hits[0x526d51]>before
 records.append({'second_surface':True,'moving':moving,'floor_moving':floor_moving,'tilt':tilt})
scope='Complete candidate overhead collision using original upward probes, velocity projection, corrected-position recheck and object-event dispatch; no whole airborne frame or playable level is claimed.'
extra={**extra,'native_callbacks':[]}
saved=coverage.copy();coverage.clear();finish('walk-air-ceiling',scope,{},extra);coverage.update(saved)
report=json.loads((folder/'walk-air-ceiling-original.json').read_text());report['records']=records;report['branch_hits']={hex(k):v for k,v in branch_hits.items()}
report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
(folder/'walk-air-ceiling-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n')
(folder/'walk-air-ceiling-original.json').write_text(json.dumps(report,indent=2)+'\n');print(report['instruction_coverage'],report['branch_hits'])
