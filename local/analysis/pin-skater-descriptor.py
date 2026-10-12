"""Pin corrected descriptor virtuals; no new original address credit."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';read=lambda f:json.loads(f.read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
previous=p/'skater-end-run-startup-checkpoint.json';prior=read(previous);target=p/'skater-descriptor-checkpoint.json';assert not target.exists()
assert sha(previous)=='4435a69384b0741f1958938317c7384ad6a2a76e5b46b391215911c232ec667b'
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
w=p/'skater-descriptor-corrected.wasm';b=read(w.with_suffix('.build.json'));assert sha(w)==b['sha256']=='1acf763df9fdb699e72e377b33231b4ee45d6697e37b504d96206fa093647c0f'
for name,digest in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==digest,name
assert b['source_hashes']==prior['source_hashes']
for name in ['skater-local-net','skater-end-run']:
 old=p/(name+'-draft.c');new=p/(name+'-descriptor-corrected.c');assert new.read_text()==old.read_text().replace('.descriptor=thug_component_descriptor,','.descriptor=thug_component_descriptor_base,')
old_suites=read(p/'walk-component-browser.json')['observed']['suites'];suites={name:read(p/('skater-descriptor-regression-'+name.replace('_','-')+'-result.json')) for name in old_suites};assert suites==old_suites
for name,file,oldfile in [('skater_local_net','skater-local-net-descriptor-candidate-unit.json','skater-local-net-end-run-candidate-unit.json'),('skater_end_run_lifecycle','skater-end-run-lifecycle-descriptor-candidate-unit.json','skater-end-run-lifecycle-startup-candidate-unit.json'),('skater_end_run_startup','skater-end-run-startup-descriptor-candidate-unit.json','skater-end-run-startup-unit.json')]:
 suites[name]=read(p/file);assert suites[name]==read(p/oldfile)
suites['skater_base_descriptor']=read(p/'skater-base-descriptor-unit.json');assert len(suites)==189 and all(x['result']=='pass' for x in suites.values())
original=read(p/'skater-base-descriptor-original.json');unit=suites['skater_base_descriptor'];fixture=read(p/'skater-base-descriptor-fixtures.json')
assert original['cases']==unit['cases']==216 and original['calls']==unit['calls']==432 and original['counts']==unit['counts']
assert unit['nan_fields_classification_only']==0 and not fixture['float_fields']
assert not original['instruction_coverage'] # Adapter tests existing base routine; no new recovery claim.
for case in fixture['cases']:
 for step in case['steps']:assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','quiet_double_fields','global_quiet_float_indices','global_bit_masks','float_fields','global_float_indices','indeterminate_words','indeterminate_bytes','compression_records'])
negative=read(p/'skater-base-descriptor-negative.json');assert negative['result']=='pass' and negative['incorrect_virtual_rejected'] and 'RuntimeError' in negative['rejection']
proof=read(p/'skater-descriptor-browser.json');expected={'result':'pass','wasm_sha256':sha(w),'wasm_bytes':w.stat().st_size,'runtime_imports':0,'suites':suites};assert proof['observed']==expected and proof['status'].startswith('PASS') and 'Chrome/154.' in proof['user_agent']
canonical=json.dumps(expected,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert proof['rendered_dom_fingerprint']=={'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(expected)}
paths={previous,p/'skater-end-run-startup-audit.json',p/'component-base-descriptor-probe.c',p/'skater-local-net-descriptor-corrected.c',p/'skater-end-run-descriptor-corrected.c'}
for pattern in ['skater-descriptor*','skater-base-descriptor*']:paths.update(f for f in p.glob(pattern) if f.is_file())
for name in ['build-skater-descriptor-candidate.py','probe-skater-base-descriptors.py','verify-skater-base-descriptor.mjs','verify-skater-descriptor-regression.mjs','serve-skater-descriptor.py','pin-skater-descriptor.py','audit-skater-descriptor.py']:paths.add(p/name)
for pattern in ['skater-local-net-descriptor-candidate-unit.json','skater-end-run-lifecycle-descriptor-candidate-unit.json','skater-end-run-startup-descriptor-candidate-unit.json']:paths.add(p/pattern)
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
for f in paths:
 assert f.is_file(),f
 artifacts[str(f.relative_to(r))]=sha(f)
 if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
report_sha=sha(r/'progress/report.json');assert report_sha=='bc9536003ee770ee309979d754c530cd0f5ff268f2b2722e25271746d0bf24bb'
c={'schema':3,'result':'original comparisons, Node and actual Chromium pass; unpromoted','prior_checkpoint':str(previous.relative_to(r)),'prior_checkpoint_sha256':sha(previous),'wasm':str(w.relative_to(r)),'wasm_sha256':sha(w),'wasm_bytes':w.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],'source_hashes':b['source_hashes'],'draft_source_hashes':b['draft_source_hashes'],'platform_source_hashes':prior['platform_source_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),'browser_suites':189,'preserved_browser_suites':188,'browser_dom_fingerprint':proof['rendered_dom_fingerprint'],'new_functions':0,'original_addresses':[],'verified_scoped_addresses_from_prior':prior['original_addresses'],'new_cases':216,'new_completed_calls':432,'constructor_prefix':prior['constructor_prefix'],'unsupported_routes':prior['unsupported_routes'],'public_report_sha256':report_sha,'scope':'Correct both LocalNet and EndRun descriptor slots to original base45d720 instead of extended42bb20. Actual virtual calls through both tables match ignored trailing descriptor fields. Wrong-virtual control rejected. All 185 original regression suites and three prior candidate suites unchanged. Fifteen prior complete lifecycle/flag routines retain their evidence; this ABI integration earns no new routine count. Constructor stays partial; frame/settings/network paths remain unfinished.','publishing':'Old goal and publishing automation remain paused; hosted upload verification awaits reporting-only push approval. No commit or push in this session.','playable':False}
target.write_text(json.dumps(c,indent=2)+'\n');print('Pinned descriptor correction:',len(artifacts),'artifacts;189 browser suites;zero new routines;',sha(target))
