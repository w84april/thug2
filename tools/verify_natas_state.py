"""Compare natas-state with the original game instructions."""
from pathlib import Path
prefix=Path('tools/verify_rail_entry_paths.py').read_text().split("for kind in ['point','natas','lip','grind']:enter(kind)")[0]
prefix=prefix.replace('rail-entry-paths.json','natas-state.json').replace('call(0x50a770,PHYS,[POINT,RAILS,WORLD,force_no_lip,walking,QUERY])','call(0x504730,PHYS,[QUERY])')
exec(compile(prefix,'<point-rail prerequisites>','exec'))
folder=out;report_path=out.parent/'natas-state.json'
bind(0x504730,'thug_skater_update_natas',0,'void',True,True,True)
rows=list(md.disasm(pe.get_data(0x104730,472),0x504730));natas_hits=Counter()
def trace_natas(cpu,at,size,user):natas_hits[at]+=1
oracle.cpu.hook_add(UC_HOOK_CODE,trace_natas,begin=0x504730,end=0x504907)
oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=0x504730,end=0x504730)
prior_config=config_entry;maximum=100.;slop=30.
def config_entry(trigger=False):
 b=prior_config(trigger);b.symbol(0x6a94598a,2,bits(maximum));b.symbol(0x50c5cc2f,2,bits(slop));b.symbol(0xcd09e062,1,4);return b
def natas(extra=(),label='point-rail state'):
 enter('natas',extra=[patch(SKATER_STATE+0x18,'<I',4),patch(PHYS+0x2ec,'<B',1),patch(GCONTEXT+0x18,'<I',0xa549b57b),patch(PHYS+0x8c,'<f',1/60)]+list(extra))
 path_results[-1]['label']=label
for cheat,direction,position in itertools.product([0,1],[0,1,255],[-4000.,0.,100.,4000.]):
 natas([patch(STATE+0x5f0,'<I',16 if cheat else 0),patch(PHYS+0x1500,'<B',direction),patch(GCONTEXT+0x104,'<2f',position,2)],label='perfect-rail flag, direction and balance position')
for maximum in [0.,.01,1.,100.,10000.]:
 for dt in [0.,1/120,1/30,-1/60]:
  natas([patch(PHYS+0x8c,'<f',dt)],label='speed and frame duration')
maximum=100.
for flags in [(0,0),(1,0),(1,1),(255,0)]:
 for angle in [0.,329.,330.,360.,-360.]:
  natas([patch(SKATER_STATE+0x30,'<B',flags[0]),patch(SKATER_STATE+0x78,'<B',flags[1]),patch(TRICK+0x13a4,'<f',angle)],label='spin-scoring threshold and state flags')
for mode in [0,0x8d10119d,0x255ed86f,0x0ac90769,0xef24413b,0x3506ce64]:
 natas([patch(GCONTEXT+0x18,'<I',mode)]+[patch(GCONTEXT+0x24+i*0x58+0x30,'<f',100*(i+1)) for i in range(4)],label='balance selector mode')
scope='Complete00504730 point-rail balance/spin state with real balance, flags, matrix, spin scoring and timed-trick callees; all127parentinstructions covered. All fixture bytes compare exactly. Full game integration remains unfinished.'
fixture={'base':BASE,'memory':'natas-state-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'native_qb_callbacks','pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'native_callbacks':[{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]}
(folder/'natas-state-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')));(folder/fixture['memory']).write_bytes(initial)
coverage={'total':len(rows),'covered':sum(bool(natas_hits[i.address]) for i in rows),'missing':[hex(i.address) for i in rows if not natas_hits[i.address]]}
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(path_results),'counts':dict(oracle.counts),'instruction_coverage':coverage,'callee_coverage':dict(oracle.coverage),'paths':path_results,'scope':scope}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('Original Natas',len(path_results),coverage,flush=True)

subprocess.run(['node',str(ROOT/'tools/verify_natas_state_wasm.mjs')],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [folder/'natas-state-fixtures.json',folder/fixture['memory']]}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS natas-state',len(path_results),sum(oracle.counts.values()))
