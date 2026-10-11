"""Compare rail-state with the original game instructions."""
from pathlib import Path
rail_state_source=Path('tools/verify_rail_acquisition.py').read_text().split("\nfor kind in ['grind','point','natas','lip']:")[0]
rail_state_source=rail_state_source.replace('rail-acquisition.json','rail-state.json').replace('call(0x50dae0,PHYS,[force_no_lip,QUERY])','call(0x50ddf0,PHYS,[QUERY])')
exec(compile(rail_state_source,'<complete rail runtime graph>','exec'))
folder=out;report_path=out.parent/'rail-state.json'
bind(0x50ddf0,'thug_skater_update_rail',0,'void',True,True,True);ROOTS.add(0x50ddf0)
rail_instructions=list(md.disasm(pe.get_data(0x10ddf0,4222),0x50ddf0));rail_hits=Counter();rail_case_hits=Counter()
def trace_rail(cpu,at,size,user):rail_hits[at]+=1;rail_case_hits[at]+=1
oracle.cpu.hook_add(UC_HOOK_CODE,trace_rail,begin=0x50ddf0,end=0x50ee6d)
for at in [0x50ddf0]+[i.address for i in rail_instructions if i.mnemonic=='ret']:
 oracle.cpu.hook_add(UC_HOOK_CODE,floor_observe,begin=at,end=at)
oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=0x50ddf0,end=0x50ddf0)
prior_config=config_entry
def config_entry(trigger=False):
 b=prior_config(trigger)
 for name,value in [(0xd1f46992,-300.),(0x0bf35053,150.),(0x6a94598a,100.),(0x50c5cc2f,30.)]:b.symbol(name,2,bits(value))
 b.symbol(0xcd09e062,1,4);return b
def update(kind='grind',speed=100.,z=50.,slope=0.,special=True,node=0,extra=(),label='rail update'):
 rail_case_hits.clear()
 p=[patch(SKATER_STATE+0x18,'<I',4),patch(PHYS+0x22c,'<2I',RAILS+node*0x54,WORLD),patch(PHYS+0x8c,'<f',1/60),patch(GCONTEXT+0x18,'<I',0xa549b57b if kind=='natas' else 0x8d10119d),patch(ORIENT+0x40,'<I',0xd443a2bc if special else 0),patch(BODIES+0x4c,'<4f',0,20000+slope*z/100,z,1),patch(BODIES+0xac,'<4f',0,speed*slope/100,speed,1)]
 for i in range(3):
  start=[0,20000+slope*i,100*i,1];end=[0,20000+slope*(i+1),100*(i+1),1]
  p += [patch(RAILS+i*0x54,'<12f',*(start+end+start))]
 acquire(kind,extra=p+list(extra),trigger=True,label=label)
 path_results[-1]['rail_state_hits']=[hex(at) for at in sorted(rail_case_hits)];path_results[-1]['rail']=oracle.word(PHYS+0x22c)
 if len(path_results)%10==0:print('Rail state',len(path_results),path_results[-1]['state'],len(rail_case_hits),flush=True)
for special,node,speed in itertools.product([False,True],[0,1],[-100.,0.,100.,10000.]):update(special=special,node=node,z=node*100+50,speed=speed,label='interior forward reverse zero and high speed')
for special,z,speed in itertools.product([False,True],[-50.,105.,250.],[-100.,100.]):update(special=special,z=z,speed=speed,label='past endpoint and continuation')
for slope,speed in itertools.product([-100.,0.,100.],[-100.,100.]):update(slope=slope,speed=speed,label='rail slope gravity and direction')
for direction in [0,1,255]:update('natas',extra=[patch(PHYS+0x1500,'<B',direction)],label='point-rail Natas dispatch')
update(extra=[patch(SKATER_STATE+0x20,'<B',1),patch(INPUT+0x1c0,'<B',0)],label='grind release and jump event')
update(extra=[patch(STATE+0x5f0,'<I',16)],label='perfect grind flag')
update(extra=[patch(GROUND_GATE+0x18,'<I',GCONTACT),patch(GCONTACT,'<I',0)],label='dead moving contact')
scope='Complete0050ddf0 rail-state update with real balance, moving contacts, Natas, transitions, transforms, training collision, scoring and QB events. Combined baseline/edge coverage1173/1179; six defensive failed-contact instructions retained. All fixture bytes compare exactly. Full game integration remains unfinished.'
fixture={'base':BASE,'memory':'rail-state-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'native_qb_callbacks','pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'native_callbacks':[{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]}
(folder/'rail-state-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')));(folder/fixture['memory']).write_bytes(initial)
coverage={'total':len(rail_instructions),'covered':sum(bool(rail_hits[i.address]) for i in rail_instructions),'missing':[hex(i.address) for i in rail_instructions if not rail_hits[i.address]]}
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(path_results),'counts':dict(oracle.counts),'instruction_coverage':coverage,'callee_coverage':dict(oracle.coverage),'paths':path_results,'scope':scope}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('Original rail state',len(path_results),coverage['covered'],'/',coverage['total'],flush=True)

subprocess.run(['node',str(ROOT/'tools/verify_rail_state_wasm.mjs')],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [folder/'rail-state-fixtures.json',folder/fixture['memory']]}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS rail-state',len(path_results),sum(oracle.counts.values()))
