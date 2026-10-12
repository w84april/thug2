"""Original landing/slide handler with retained-probe write provenance."""
from pathlib import Path
exec(compile(Path('local/analysis/probe-walk-grounded.py').read_text().split('for moving,height,flags')[0],'<preserved floor graph and provenance>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x52a700,1165,'thug_walk_air_landing_draft',2,'void',True,True,True)]
for row in specs:
 bind_new(*row);oracle.cpu.hook_add(UC_HOOK_CODE,observe_cache,begin=row[0],end=row[0])
def landing_observe(cpu,at,size,user):
 global source_probe,copy_destination,source_undefined
 sp=cpu.reg_read(UC_X86_REG_ESP)
 if at==0x52a700 and oracle.word(sp)==oracle.stop:source_probe=copy_destination=0;root_records.append({'stack_pointer_fields':[]})
 elif at==0x52ab8a and oracle.word(sp)==oracle.stop:
  root_records[-1]['indeterminate_words']=sorted(undefined_words)
  root_records[-1]['indeterminate_provenance']=[undefined_provenance[a].copy() for a in sorted(undefined_words)]
 elif at==0x417760 and oracle.word(sp)==0x52a728:source_probe=cpu.reg_read(UC_X86_REG_ECX);source_undefined={0x70,0xa8}
for at in [0x52a700,0x52ab8a,0x417760]:oracle.cpu.hook_add(UC_HOOK_CODE,landing_observe,begin=at,end=at)
branch_hits=Counter()
for at in [0x52a7bc,0x52a902,0x52a97e,0x52a9c6,0x52aa33,0x52aaa6,0x52ab0d]:oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:branch_hits.update([at]),begin=at,end=at)
class LandingGraph(GroundedGraph):
 def __init__(self):
  super().__init__();self.parameters(overrides={**required_parameters,0x530dcf34:2})
  self.put(P+0x18,'<I',1);self.put(P+0x1c,'<I',100);self.put(P+0x68,'<4f',0,10,0,1);self.put(P+0x24,'<4f',0,-10,4,1)
  self.put(P+0x34,'<4f',2,0,3,1);self.put(P+0x44,'<f',-5);self.put(P+0x48,'<4f',0,0,1,1);self.put(P+0x94,'<f',1)
  self.put(P+0x71c,'<4f',1,2,3,1);self.put(INPUT+0x1d4,'<B',1);self.put(GATE+0x18,'<I',0)
records=[]
for moving,kind,speed,amount in itertools.product([False,True],['empty','floor','slide'],[-3,0,1,2,3],[0,1]):
 g=LandingGraph();g.put(P+0x34,'<4f',0,0,speed,1);g.put(P+0x94,'<f',amount)
 if kind!='empty':g.plane(0,moving=moving,flags=2 if kind=='slide' else 0,velocity=(1,0,0,0))
 g.run([call(0x52a700,P,[P+0x68,P+0x24,Q])]*2,f'landing/slide/{moving}/{kind}/{speed}/{amount}')
 assert oracle.word(P+0x18)==int(kind!='floor')
 records.append({'moving':moving,'kind':kind,'speed':speed,'amount':amount,'state':oracle.word(P+0x18)})
for moving,mutation in itertools.product([False,True],['observe','cancel','position','owner','velocity']):
 g=LandingGraph();actor,owner=g.plane(0,moving=moving,flags=0x40,velocity=(1,0,2,0));g.trigger(mutation,g.word(actor+4))
 if moving:g.level_nodes([(0x111,[(0x2ca8a299,13,6)]),(g.word(actor+4),[(0x2ca8a299,13,6)]),(g.word(owner+0x14),[])])
 g.run([call(0x52a700,P,[P+0x68,P+0x24,Q])],f'landing callback/{moving}/{mutation}')
 assert oracle.word(CBSTATE)>0
 records.append({'moving':moving,'mutation':mutation,'callbacks':oracle.word(CBSTATE),'state':oracle.word(P+0x18)})
for floor_moving,wall_moving,reverse in itertools.product([False,True],[False,True],[False,True]):
 g=LandingGraph();g.plane(0,moving=floor_moving,flags=2);g.obstacle('z',3,moving=wall_moving,reverse=reverse)
 before=branch_hits[0x52a902]
 g.run([call(0x52a700,P,[P+0x68,P+0x24,Q])]*2,f'slide second collision/{floor_moving}/{wall_moving}/{reverse}')
 records.append({'second_wall':True,'floor_moving':floor_moving,'wall_moving':wall_moving,'reverse':reverse,'second_hits':branch_hits[0x52a902]-before})
assert branch_hits[0x52a902]>0
scope='Candidate complete airborne sweep, slide and landing handler with real geometry, collision scripts and moving contact. Full airborne dispatch and playable training remain unfinished.'
extra={**extra,'indeterminate_word_addresses':[P+0x17b4+x for x in [0x70,0xa8]],'stack_probe_pointer_fields':[P+0x17b4+0x64],
 'native_callbacks':[{'module':'walk-grounded-diagnostics.wasm','export':'fixture_walk_grounded_print','slots':[DIAG+4]},{'module':'trigger-callback.wasm','export':'fixture_trigger_native','original':CBNATIVE}]}
saved=coverage.copy();coverage.clear();finish('walk-air-landing',scope,{},extra);coverage.update(saved)
report=json.loads((folder/'walk-air-landing-original.json').read_text());report['records']=records;report['branch_hits']={hex(k):v for k,v in branch_hits.items()}
report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
(folder/'walk-air-landing-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n')
(folder/'walk-air-landing-original.json').write_text(json.dumps(report,indent=2)+'\n');print(report['instruction_coverage'],report['branch_hits'])
