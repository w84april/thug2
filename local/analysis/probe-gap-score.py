"""Original profile/trick history queries needed by real gap start and finish."""
from pathlib import Path
exec(compile(Path('local/analysis/probe-skater-gap.py').read_text().split('# Selective constructor')[0],'<preserved Gap setup>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x586130,26,'profile_specials',0,True),(0x561360,152,'score_trick_checksum',2,False),
 (0x562080,193,'score_profile_checksum',2,False),(0x562150,242,'score_profile_special',1,False),
 (0x5622c0,170,'score_count_history',3,True),(0x5624c0,74,'score_count_named',4,True),
 (0x562510,134,'score_count_bound',4,True),(0x5625a0,120,'score_preceding_named',3,True),
 (0x562620,192,'score_preceding_bound',3,True)]
for a,n,name,argc,this in specs:bind_new(a,n,'thug_'+name+'_draft',argc,'word',False,False,this)
PM,PROFILE,SCORE=P+0x8000,P+0x9000,P+0xa000
assert 0x7ce4b4 not in index
glob('thug_profile_manager',0x7ce4b4,PM)
initial=bytes(memory);oracle.initial=initial
KEY,OTHER=0x12345678,0x87654321
# Existing CRC implementation used only to prepare names; original lookups execute.
def crc(text):
 import zlib
 return zlib.crc32(text.lower().replace('/','\\').encode())^0xffffffff
NAMES=['Kickflip','Double Kickflip','Triple Kickflip','Created Test']
CHECKS=[crc(s) for s in NAMES]
class HistoryGraph(GapGraph):
 def __init__(self,mode='direct',selected=0):
  super().__init__()
  self.image[PM-BASE:PM-BASE+0x24]=bytes(0x24);self.put(PM+0x14,'<3I',PROFILE,PROFILE+0x100,selected)
  self.image[PROFILE-BASE:PROFILE-BASE+0x200]=bytes(0x200)
  self.image[SCORE-BASE:SCORE-BASE+0x80]=bytes(0x80)
  for i,name in enumerate(NAMES[:3]):
   params=self.structure([(0xa1dc81f9,3,self.text(name)),(0x6e855102,13,0x81110000+i)])
   definition=self.structure([(0x7031f10c,10,params)])
   self.symbol(0x81100000+i,10,definition)
   if i:self.symbol(0x81110000+i-1,12,self.array(10,[definition]))
  entries=[];bindings=[]
  if mode=='direct':bindings=[(KEY,13,0x81100000)]
  if mode=='zero':bindings=[(KEY,13,0)]
  if mode in ['integer','no local']:bindings=[(KEY,1,0)]
  if mode in ['array','special','duplicates','disabled']:
   entries=[self.structure([(0xa92a2280,13,OTHER),(0x5b077ce1,13,0x81100001),(0xb56a8816,1,1)])]
   entries += [self.structure([(0xa92a2280,13,KEY),(0x5b077ce1,13,0 if mode in ['special','disabled'] else 0x81100000),(0xb56a8816,1,0 if mode=='disabled' else 1)])]
   if mode=='duplicates':entries += [self.structure([(0xa92a2280,13,KEY),(0x5b077ce1,13,0x81100002),(0xb56a8816,1,1)])]
  b=self.structure(bindings);a=self.array(10,entries);special=self.structure([(0,12,a)])
  s=self.structure([(0xd544aa2d,10,b),(0xddbee809,10,special)])
  for at in [PROFILE,PROFILE+0x100]:self.put(at+0x5c,'<2I',0,self.word(s+4))
  node=self.alloc(16);sentinel=self.alloc(16);self.put(node,'<4I',0,OBJ,0,sentinel);self.put(sentinel,'<4I',0,0xffffffff,0,sentinel)
  self.put(GAME+0x34,'<I',sentinel if mode=='no local' else node);self.put(OBJ+0xbc,'<B',1)
  created=self.alloc(8);self.put(created+4,'<I',self.structure([(0xa1dc81f9,3,self.text(NAMES[3]))]));self.put(OBJ+0x17c,'<I',created)
  self.symbol(0xfcfacab8,1,10)
 def history(self,values,count=None):
  entries=[]
  for key,spin,angle,flags in values:
   entry=self.alloc(0x20);self.put(entry,'<8I',0,0,spin&0xffffffff,angle&0xffffffff,key,0,flags,0);entries.append(entry)
  storage=self.alloc(max(4,len(entries)*4));self.put(storage,'<'+'I'*len(entries),*entries)
  self.put(SCORE+0x4c,'<I',storage);self.put(SCORE+0x5c,'<I',(len(entries) if count is None else count)&0xffffffff)
 def run(self,calls,label,changes=None):
  result=super().run(calls,label,changes)
  if len(labels)%50==0:print('Gap score cases',len(labels),flush=True)
  return result
# Seeded missing output and both selected profiles; global lookups include variants.
for selected in [0,1]:
 for mode in ['direct','zero','integer','array','special','duplicates','disabled','missing','no local']:
  for key in [KEY,OTHER,0]:
   g=HistoryGraph(mode,selected)
   g.run([call(0x586130,PROFILE+selected*0x100),call(0x562150,args=[key]),call(0x562080,args=[key,1])],f'bindings/{mode}/{selected}/{key:x}')
for missing in [False,True]:
 g=HistoryGraph()
 if missing:g.put(PROFILE+0x60,'<I',0)
 g.run([call(0x586130,PROFILE)],f'special structure seeded output/{missing}')
for taps in [-2,0,1,2,3]:
 g=HistoryGraph();g.run([call(0x561360,args=[0x81100000,taps]),call(0x562080,args=[KEY,taps])],f'tap chain/{taps}')
# Ordered history, matching/mismatching spins, continuation flags and wrap edges.
rng=random.Random(0x5622c0)
for i in range(360):
 length=rng.randrange(0,19);values=[(rng.choice(CHECKS+[0,KEY]),rng.choice([0,1,2,3,0xffffffff]),rng.choice([0,179,180,189,190,360,-180,-190,0x7fffffff,0x80000000]),rng.choice([0,2,0x10,0x12,0xffffffff])) for _ in range(length)]
 g=HistoryGraph();g.history(values);key=rng.choice(CHECKS+[0,KEY]);spin=rng.choice([0,1,2,3,0xffffffff,0x80000000]);exact=rng.choice([0,1,255,256,257])
 tolerance=rng.choice([0,1,10,180,0x7fffffff,0x80000000,0xffffffff]);g.symbol(0xfcfacab8,1,tolerance)
 g.run([call(0x5622c0,SCORE,[key,spin,exact]),call(0x5624c0,SCORE,[key,spin,exact,1]),call(0x5625a0,SCORE,[key,spin,1])],f'history randomized/{i}')
for mode,taps,spin in itertools.product(['direct','array','integer','special','missing','no local'],[0,1,2,3],[0,1,2]):
 g=HistoryGraph(mode);g.history([(key,j%3,180*(j%3),[0,2,0x10][j%3]) for j,key in enumerate(CHECKS*2+[0,CHECKS[0]])])
 g.run([call(0x562510,SCORE,[KEY,spin,1,taps]),call(0x562620,SCORE,[KEY,spin,taps])],f'bound history/{mode}/{taps}/{spin}')
for taps in [2,3]:
 g=HistoryGraph();g.history([(CHECKS[2],2,360,0),(CHECKS[1],1,180,0),(CHECKS[1],2,360,0)])
 g.run([call(0x5624c0,SCORE,[0x81100000,0,0,taps]),call(0x5625a0,SCORE,[0x81100000,0,taps])],f'named variant/{taps}')
for count in [0,-1,-2147483648]:
 g=HistoryGraph();g.history([],count)
 g.run([call(0x5622c0,SCORE,[KEY,1,1]),call(0x5625a0,SCORE,[KEY,1,1])],f'nonpositive history/{count}')
scope='Nine original profile and score-history routines used by StartGap and EndGap, including named/profile/created-trick resolution, tap chains, exact spin tolerance and trailing-match subtraction. Whole arena/globals and preserved registers compare. Required QB data, valid created-trick indices and terminating arrays/lists are caller contracts. Gap commands and playable training remain unfinished.'
saved=coverage.copy();coverage.clear();finish('gap-score',scope,{},extra);coverage.update(saved)
report_path=folder/'gap-score-original.json';report=json.loads(report_path.read_text())
report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
report_path.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k in ['cases','calls','instruction_coverage']}),flush=True)
