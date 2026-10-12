"""Pin new scoped recovery without changing any prior checkpoint or public report."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';read=lambda f:json.loads(f.read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
prior_path=p/'walk-component-checkpoint.json';prior=read(prior_path);target=p/'skater-end-run-startup-checkpoint.json';assert not target.exists()
assert sha(prior_path)=='2beff342b621607878f1d968136ffb27ff84d5f220c7bb56f1dc7e42081acf27'
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
w=p/'skater-end-run-startup-draft.wasm';b=read(w.with_suffix('.build.json'))
assert sha(w)==b['sha256']=='98cd1c796e8650226bfe534755b2baf3eaabda02876c89c7b953b9178aad5245'
assert b['source_hashes']==prior['source_hashes']
for name,digest in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==digest,name
old_suites=read(p/'walk-component-browser.json')['observed']['suites']
suites={name:read(p/('skater-end-run-regression-'+name.replace('_','-')+'-result.json')) for name in old_suites}
assert suites==old_suites and len(suites)==185
for name,file in [('skater_local_net','skater-local-net-end-run-candidate-unit.json'),('skater_end_run_lifecycle','skater-end-run-lifecycle-startup-candidate-unit.json'),('skater_end_run_startup','skater-end-run-startup-unit.json')]:suites[name]=read(p/file)
assert len(suites)==188 and all(v['result']=='pass' for v in suites.values())
expected={'result':'pass','wasm_sha256':sha(w),'wasm_bytes':w.stat().st_size,'runtime_imports':0,'suites':suites}
proof=read(p/'skater-end-run-browser.json');assert proof['observed']==expected and proof['status'].startswith('PASS')
canonical=json.dumps(expected,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert proof['rendered_dom_fingerprint']=={'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(expected)}
assert 'Chrome/154.' in proof['user_agent']
addresses={};coverage={}
for name,unitfile,expected_cases,expected_calls,count in [('skater-local-net','skater-local-net-end-run-candidate-unit.json',29,79,4),('skater-end-run-lifecycle','skater-end-run-lifecycle-startup-candidate-unit.json',192,5830,11)]:
 original=read(p/(name+'-original.json'));unit=read(p/unitfile);fixture=read(p/(name+'-fixtures.json'));routines=read(p/(name+'-routines.json'));extents=read(p/(name+'-extents.json'))
 assert original['cases']==unit['cases']==expected_cases and original['calls']==unit['calls']==expected_calls and original['counts']==unit['counts']
 assert unit['nan_fields_classification_only']==0 and not fixture['float_fields'] and len(routines)==count
 assert extents['result']=='pass' and extents['routines_sha256']==sha(p/(name+'-routines.json'))
 for at,row in routines.items():
  assert at not in addresses and original['instruction_coverage'][at]['covered']==original['instruction_coverage'][at]['total']==row['instructions']
  assert not original['instruction_coverage'][at]['missing'] and not original['instruction_coverage'][at]['excluded']
  assert original['counts'][row['name']]>0
  addresses[at]={**row,'original_evidence':name+'-original.json','node_evidence':unitfile,'browser_suite':name.replace('-','_')}
  coverage[at]=original['instruction_coverage'][at]
 for case in fixture['cases']:
  for step in case['steps']:
   assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','quiet_double_fields','global_quiet_float_indices','global_bit_masks','float_fields','global_float_indices','indeterminate_words','indeterminate_bytes','compression_records'])
assert len(addresses)==15 and sum(row['bytes'] for row in addresses.values())==655
partial=read(p/'skater-end-run-startup-original.json')['partial_constructor'];assert (partial['covered'],partial['total'],partial['interrupted_calls'],partial['counted_complete'])==(293,463,32,False)
assert all(row['next_type']==('0x589e5fb3' if row['arguments'][2]&255 else '0x850eef66') for row in partial['records'])
negative=read(p/'skater-end-run-negative.json');assert negative['result']=='pass' and len(negative['controls'])==3 and all(x['rejected'] for x in negative['controls'])
assert negative['missing_required_boolean']['counted_complete'] is False
paths={prior_path,p/'reporting-checkpoint-integrity.json'}
for pattern in ['skater-local-net*','skater-end-run*','skater-local-net-regression-*-result.json','skater-end-run-regression-*-result.json']:
 paths.update(f for f in p.glob(pattern) if f.is_file())
for name in ['probe-skater-local-net.py','build-skater-local-net-draft.py','verify-skater-local-net-unit.mjs','reverify-skater-local-net-unit.mjs','verify-skater-local-net-regression.mjs','serve-skater-local-net.py','probe-skater-end-run-lifecycle.py','probe-skater-end-run-startup.py','build-skater-end-run-draft.py','build-skater-end-run-startup.py','verify-skater-end-run-lifecycle.mjs','verify-skater-end-run-startup.mjs','verify-skater-end-run-regression.mjs','verify-local-net-end-run-candidate.mjs','verify-end-run-lifecycle-startup-candidate.mjs','verify-end-run-negative.mjs','serve-skater-end-run.py','pin-skater-end-run-startup.py']:
 paths.add(p/name)
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
for path in paths:
 assert path.is_file(),path
 artifacts[str(path.relative_to(r))]=sha(path)
 if path.suffix in ['.py','.mjs']:harnesses[str(path.relative_to(r))]=sha(path)
c={'schema':3,'result':'original comparisons, Node and actual Chromium pass; unpromoted','prior_checkpoint':str(prior_path.relative_to(r)),'prior_checkpoint_sha256':sha(prior_path),'wasm':str(w.relative_to(r)),'wasm_sha256':sha(w),'wasm_bytes':w.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],'source_hashes':b['source_hashes'],'draft_source_hashes':b['draft_source_hashes'],'platform_source_hashes':prior['platform_source_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),'browser_suites':188,'preserved_browser_suites':185,'browser_dom_fingerprint':proof['rendered_dom_fingerprint'],'new_functions':15,'original_addresses':addresses,'new_verified_linear_bytes':655,'instruction_coverage':coverage,'new_cases':221,'new_completed_calls':5909,'constructor_prefix':{'covered':293,'total':463,'interrupted_calls':32,'next_local_type':'0x589e5fb3','next_remote_type':'0x850eef66','counted_complete':False},'unsupported_routes':['LocalNet network frame5136c0 and serializer5131a0','EndRun frame/network/events/settings deferred paths are unverified','EndRun gate553460 missing required boolean stops explicitly instead of reading an uninitialized C variable'],'scope':'Four LocalNet lifecycle routines and eleven EndRun lifecycle/flag routines verified against original complete-unit behavior. Constructor progresses through both factories and stops before BalanceTrick. No new comparison allowances or checker changes. All 185 prior suite result objects unchanged. Public reporting baseline is not changed by this private checkpoint.','historical_totals':'Do not increment the old 2026/11637 bookkeeping or use it as objdiff completion. Reconcile these fifteen addresses into the byte ledger only after source publication is authorized.','publishing':'Old goal and publish-thug2-progress automation remain paused; no commit or push in this session.','playable':False}
target.write_text(json.dumps(c,indent=2)+'\n');print('Pinned scoped checkpoint:',len(artifacts),'artifacts;15 new verified routines;188 browser suites;',sha(target))
