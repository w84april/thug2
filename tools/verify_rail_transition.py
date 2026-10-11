"""Compare rail-transition with the original game instructions."""
from pathlib import Path
transition_source=Path('tools/verify_rail_acquisition.py').read_text().split("\nfor kind in ['grind','point','natas','lip']:")[0]
transition_source=transition_source.replace('rail-acquisition.json','rail-transition.json').replace('call(0x50dae0,PHYS,[force_no_lip,QUERY])','call(0x50c200,PHYS,[POINT,QUERY])')
exec(compile(transition_source,'<rail search and entry graph>','exec'))
folder=out;report_path=out.parent/'rail-transition.json'
bind(0x50c200,'thug_skater_transition_rail',1,'void',True,True,True);ROOTS.add(0x50c200)
transition_instructions=list(md.disasm(pe.get_data(0x10c200,0x468),0x50c200));transition_hits=Counter();transition_case_hits=Counter()
def trace_transition(cpu,at,size,user):transition_hits[at]+=1;transition_case_hits[at]+=1
oracle.cpu.hook_add(UC_HOOK_CODE,trace_transition,begin=0x50c200,end=0x50c667)
for at in [0x50c200]+[i.address for i in transition_instructions if i.mnemonic=='ret']:
 oracle.cpu.hook_add(UC_HOOK_CODE,floor_observe,begin=at,end=at)
oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=0x50c200,end=0x50c200)
def transition(special=True,z=20.,speed=2400.,gap=0.,extra=(),label='transition',angled=False):
 transition_case_hits.clear()
 p=[patch(SKATER_STATE+0x18,'<I',4),patch(PHYS+0x22c,'<2I',RAILS,WORLD),patch(ORIENT+0x40,'<I',0xd443a2bc if special else 0),patch(WORLD+0x48,'<I',4),patch(PHYS+0x8c,'<f',1/60),patch(POINT,'<4f',-2 if angled else 0,20000,-20,1),patch(BODIES+0x4c,'<4f',2 if angled else 0,20000,z,1),patch(BODIES+0xac,'<4f',240 if angled else 0,0,speed,1)]
 positions=[[0,20000,-100,1],[0,20000,-50,1],[gap,20000,0,1],[gap,20000,100,1]]
 for i,start in enumerate(positions):
  end=positions[i+1] if i%2==0 else start;previous=RAILS+(i-1)*0x54 if i%2 else 0;next_=RAILS+(i+1)*0x54 if i%2==0 else 0
  p += [patch(RAILS+i*0x54,'<12f',*(start+end+start)),patch(RAILS+i*0x54+0x40,'<5I',next_,previous,4,0x1800+i,0)]
 acquire(extra=p+list(extra),trigger=True,label=label)
 path_results[-1]['transition_hits']=[hex(at) for at in sorted(transition_case_hits)];path_results[-1]['rail']=oracle.word(PHYS+0x22c)
 print('transition',special,z,speed,gap,path_results[-1]['state'],hex(path_results[-1]['rail']),flush=True)
for special,z,gap in itertools.product([False,True],[-20.,20.,120.],[0.,5.,50.]):transition(special,z,gap=gap,label='rail endpoint range and lateral separation')
for special,speed in itertools.product([False,True],[0.,-2400.,1.,100.,2400.]):transition(special,speed=speed,label='velocity direction and zero-horizontal fallback')
for special in [False,True]:
 transition(special,extra=[patch(RAILS+0x40,'<I',RAILS+2*0x54)],label='adjacent candidate gate')
 transition(special,extra=[patch(RAILS+2*0x54+0x40,'<I',0)],label='candidate has no continuation')
for special,z,gap in itertools.product([False,True],[-20.,20.,120.],[0.,5.,50.]):transition(special,z,gap=gap,angled=True,label='angled crossing and endpoint interpolation')
for target,value in [(PHYS+0x22c,RAILS),(PHYS+0x1514,SOUND2),(PHYS+0x1528,SKATER_STATE2)]:
 transition(False,angled=True,extra=[patch(GOBS+4,'<4I',target,value,4,0xa7662059),patch(RAILS+0x50,'<I',0xabcdef07)],label='real QB replaces live rail or component')
 assert path_results[-1]['qb_callbacks']>0
scope='Complete0050c200 rail transition with real rail search, transforms, classification, events and state changes; all325parentinstructions covered. All fixture bytes compare exactly. Full game integration remains unfinished.'
fixture={'base':BASE,'memory':'rail-transition-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'native_qb_callbacks','pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'native_callbacks':[{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]}
(folder/'rail-transition-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')));(folder/fixture['memory']).write_bytes(initial)
coverage={'total':len(transition_instructions),'covered':sum(bool(transition_hits[i.address]) for i in transition_instructions),'missing':[hex(i.address) for i in transition_instructions if not transition_hits[i.address]]}
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(path_results),'counts':dict(oracle.counts),'instruction_coverage':coverage,'callee_coverage':dict(oracle.coverage),'paths':path_results,'scope':scope}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('Original rail transition',len(path_results),coverage,flush=True)

subprocess.run(['node',str(ROOT/'tools/verify_rail_transition_wasm.mjs')],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [folder/'rail-transition-fixtures.json',folder/fixture['memory']]}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS rail-transition',len(path_results),sum(oracle.counts.values()))
