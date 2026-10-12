"""Original EndRun lifecycle and flag commands; unverified frame/settings stay out."""
from pathlib import Path
source=Path('local/analysis/probe-skater-walk.py').read_text().split('# Real original CRT')[0]
exec(compile(source,'<preserved isolated component oracle>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[
 (0x510f90,114,'thug_end_run_create_draft',0,'word',True,False,False),
 (0x510d20,11,'thug_end_run_destroy_draft',0,'void',False,False,True),
 (0x510d40,33,'thug_end_run_delete_draft',1,'word',True,False,True),
 (0x510d30,12,'thug_end_run_copy_flags_draft',1,'word',False,False,True),
 (0x510dc0,223,'thug_end_run_command_draft',3,'word',False,False,True),
 (0x510f30,9,'thug_end_run_flag_2_draft',0,'word',False,False,True),
 (0x510f40,10,'thug_end_run_flag_16_draft',0,'word',False,False,True),
 (0x510f50,7,'thug_end_run_flag_1_draft',0,'word',False,False,True),
 (0x510f60,5,'thug_end_run_clear_1_draft',0,'void',False,False,True),
 (0x510f70,5,'thug_end_run_clear_8_draft',0,'void',False,False,True),
 (0x510f80,5,'thug_end_run_clear_4_draft',0,'void',False,False,True)]
for row in specs:bind_new(*row)
functions['0x510d30']['pointer_result']=True
for row in [(0x45e510,'thug_composite_initialize_draft',0,'word',False,False),
 (0x45ee20,'thug_composite_add_parameters_draft',2,'void',True,True),
 (0x45db30,'thug_composite_finalize_draft',0,'void',True,True),
 (0x45d890,'thug_composite_destroy_draft',0,'void',True,True)]:bind(*row)
exports.append([0x64bdb8,'thug_end_run_methods_draft']);function_exports.append([0x510f90,'thug_end_run_create_draft'])
for flags in [0,1,2,3,255,256,257,0xffffffff]:
 g=WalkGraph();g.run([call(0x510f90),call(0x510d40,HEAP,[flags])],f'EndRun factory/delete {flags}')
g=WalkGraph();g.put(CONTEXT+32,'<I',1);g.run([call(0x510f90)]*2,'EndRun allocation failure')
for fill,offset in itertools.product([0,0xa5,255],[0,1,4]):
 g=WalkGraph();g.image[P-BASE:P-BASE+0x80]=bytes([fill])*0x80;fields.add(P+offset)
 g.run([call(0x510d20,P+offset)]*2,f'EndRun destructor raw {fill}/{offset}')
commands=[0x95bdcfcd,0x69a9e37f,0x4c58771e,0xafc6a7,0x962dea01,0xea77e667,0xb866bf9b,0,0xffffffff]
for flags in [*range(64),0x80000000,0x12345678,0xffffffc0,0xffffffff]:
 for order in [commands,commands[::-1]]:
  g=WalkGraph();g.put(P+24,'<I',flags)
  calls=[]
  for name in order:
   calls += [call(0x510dc0,P,[name,0,0]),call(0x510f30,P),call(0x510f40,P),call(0x510f50,P)]
  calls += [call(0x510f60,P),call(0x510f70,P),call(0x510f80,P)]*2
  g.run(calls,f'EndRun command/flags {flags:x}/{order[0]:x}')
for flags,offset in itertools.product([0,1,2,16,0x12345678,0xffffffff],[-4,-1,0,1,4,16]):
 g=WalkGraph();g.put(P+24,'<I',flags)
 g.run([call(0x510d30,P,[P+24+offset])]*2,f'EndRun flag copy alias {flags:x}/{offset}')
for reverse in [False,True]:
 g=WalkGraph();registry=[(0xb1d5a3e1,0x510f90),(0x43686585,0x519740)];g.registry(registry)
 order=registry[::-1] if reverse else registry;params=[g.structure([(0xb6015ea8,13,t)]) for t,_ in order]
 g.run([call(0x45e510,OBJ)]+[call(0x45ee20,OBJ,[s,0]) for s in params]+[call(0x45db30,OBJ),call(0x45d890,OBJ)],f'EndRun shared lifecycle {reverse}')
scope='Eleven complete EndRun lifecycle and flag routines. Original heap, base virtual lifecycle, complete command branches, all six low flags and high-bit preservation, unaligned destruction and overlapping copies execute. Whole arena/globals/heap and completed-call registers compare. Frame, settings gate/deferred helper, network send, event/script requests and full skater startup are excluded and remain unverified. No playable-game or binary-matching claim.'
finish('skater-end-run-lifecycle',scope,{}, {**extra,'function_exports':function_exports,'memory_fixture':'skater-walk-memory.wasm'})
(folder/'skater-end-run-lifecycle-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n')
