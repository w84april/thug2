"""Compare airborne transfers using the original trajectory and contact routines."""
from pathlib import Path
exec(compile(Path('local/analysis/probe-walk-transfer.py').read_text().split('\nrecords=[]')[0],'<preserved transfer geometry>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x527510,227,'thug_walk_air_transfer_draft',0,'byte',True,False,True)]
for row in specs:
 bind_new(*row);oracle.cpu.hook_add(UC_HOOK_CODE,observe_cache,begin=row[0],end=row[0])
class AirTransferGraph(TransferGraph):
 def __init__(self,speed=500,vertical=200,mode=1):
  super().__init__(speed,vertical,mode,submode=1);self.put(P+0x44,'<f',vertical)
  self.put(GATE+0x18,'<I',0)
 def retained_surface(self,moving=False):
  actor,owner=self.plane(-100,moving=moving)
  probe=P+0x17b4
  self.image[probe-BASE:probe-BASE+0xb0]=bytes(0xb0)
  if moving:
   self.put(probe+0x98,'<3I',owner,0,0);self.put(owner+4,'<I',probe+0x98)
  return owner
records=[]
for field,value in itertools.product([P+0x9b,CONTROL+0x24,INPUT+0xc0,INPUT+0x120],[0,1,255]):
 g=AirTransferGraph();g.ramp();g.retained_surface();g.put(field,'<B',value)
 expected=(value==0 if field in [P+0x9b,CONTROL+0x24] else value!=0)
 stages=g.run([call(0x527510,P,[Q])]*2,f'air transfer eligibility/{field:x}/{value}')
 assert all(x['result']==int(expected) for x in stages)
 assert oracle.word(P+0x18)==1
 records.append({'gate':hex(field),'value':value,'result':stages[0]['result']})
for shape,mode,speed,vertical in itertools.product(['empty','ramp','missing surface flag'],[0,1],[0,10,500],[-200,0,200]):
 g=AirTransferGraph(speed,vertical,mode)
 if shape!='empty':g.ramp(flags=0 if shape=='missing surface flag' else 8)
 g.retained_surface()
 stages=g.run([call(0x527510,P,[Q])],f'air transfer search/{shape}/{mode}/{speed}/{vertical}')
 if shape!='ramp':assert stages[0]['result']==0
 assert oracle.word(P+0x18)==1
 records.append({'shape':shape,'mode':mode,'speed':speed,'vertical':vertical,'result':stages[0]['result']})
for moving,contact in itertools.product([False,True],['none','matching','other','dead']):
 g=AirTransferGraph();g.ramp(moving);owner=g.retained_surface(moving)
 if contact!='none':
  g.put(GATE+0x18,'<I',CONTACT)
  if contact=='matching' and moving:
   g.put(CONTACT,'<3I',owner,0,P+0x17b4+0x98);g.put(owner+4,'<I',CONTACT);g.put(P+0x17b4+0x9c,'<I',CONTACT)
  elif contact=='dead':g.put(CONTACT,'<I',0);g.put(PLATFORM+4,'<I',0)
 stages=g.run([call(0x527510,P,[Q])]*2,f'air transfer contact/{moving}/{contact}')
 assert all(x['result']==1 for x in stages) and oracle.word(P+0x18)==1
 records.append({'moving':moving,'contact':contact,'result':stages[0]['result'],'retained_owner':oracle.word(oracle.word(GATE+0x18)) if oracle.word(GATE+0x18) else 0})
scope='Complete candidate airborne transfer with original eligibility, trajectory and retained moving-contact transitions; whole airborne frames and playable training remain unfinished.'
extra={**extra,'cache_capture':'destructor-v1','native_callbacks':[], 'pointer_globals':sorted(set(extra.get('pointer_globals',[])+[index[0x6918ec+i*4] for i in range(8)]))}
saved=coverage.copy();coverage.clear();finish('walk-air-transfer',scope,{},extra);coverage.update(saved)
report=json.loads((folder/'walk-air-transfer-original.json').read_text());report['records']=records
report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
(folder/'walk-air-transfer-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n')
(folder/'walk-air-transfer-original.json').write_text(json.dumps(report,indent=2)+'\n');print(report['instruction_coverage'])
