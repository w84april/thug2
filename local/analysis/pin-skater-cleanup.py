"""Pin CleanupState only after original, Node and actual Chromium comparisons."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
prior_path=p/'skater-finalize-checkpoint.json';assert sha(prior_path)=='2730145384989cf88ab1df4c8ccd6d4603003b01971c1f0fb215aef1c7ddbe99'
prior=read(prior_path);target=p/'skater-cleanup-checkpoint.json';assert not target.exists()
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
b=read(p/'skater-cleanup-draft.build.json');module=p/'skater-cleanup-draft.wasm'
assert sha(module)==b['sha256']=='10bb968047b351319e7be04b1d612fce57305dd11a30ccdad5e5770954108d64'
assert module.stat().st_size==852513 and b['source_hashes']==prior['source_hashes']
for name,digest in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==digest,name
previous=read(p/'skater-finalize-browser.json')['observed']['suites']
suites={name:read(p/('skater-cleanup-checkpoint-'+name.replace('_','-')+'-result.json')) for name in ['skater_cleanup',*previous]}
assert len(suites)==146
for name,result in suites.items():
 assert result['result']=='pass',name
 if name in previous:assert result==previous[name],name
original=read(p/'skater-cleanup-original.json');fixture=read(p/'skater-cleanup-fixtures.json');coverage=original['instruction_coverage'];routines=read(p/'skater-cleanup-routines.json')
assert (original['cases'],original['calls'],suites['skater_cleanup']['cases'],suites['skater_cleanup']['calls'])==(441,914,441,914)
assert original['counts']==suites['skater_cleanup']['counts'] and suites['skater_cleanup']['nan_fields_classification_only']==0
assert suites['skater_cleanup']['signaling_nan_words_quieted_per_x87']==28
assert len(coverage)==20 and set(coverage)==set(routines)
extents=read(p/'skater-cleanup-extents.json');assert extents['result']=='pass' and extents['routines_sha256']==sha(p/'skater-cleanup-routines.json')
assert set(extents['checked'])==set(routines)
assert (sum(x['covered'] for x in coverage.values()),sum(x['total'] for x in coverage.values()))==(557,557)
assert not any(x['missing'] or x['excluded'] for x in coverage.values()) and not fixture['float_fields']
interrupted=0;quiet_globals=[i for i,g in enumerate(fixture['globals']) if g[1] in [0x701670,0x701674]]
for case in fixture['cases']:
 for step in case['steps']:
  assert not any(step.get(k) for k in ['quiet_float_fields','quiet_double_fields','global_bit_masks','float_fields','global_float_indices','indeterminate_bytes','compression_records'])
  if step.get('global_quiet_float_indices'):
   assert step['fn'] in ['0x48e920','0x4b6ab0'] and step['global_quiet_float_indices']==quiet_globals
  if step.get('expected_trap'):
   assert step['fn']=='0x582d90';interrupted+=1
assert interrupted==32 and suites['skater_cleanup']['virtual_wait_callbacks']==0
assert read(p/'skater-cleanup-checker-guard.json')['result']=='pass' and len(read(p/'skater-cleanup-checker-guard.json')['rejected'])==5
constructor=original['partial_constructor']
assert (constructor['covered'],constructor['total'],constructor['interrupted_calls'])==(265,463,32)
assert prior['skater_constructor_prefix']['covered']==257
for record in constructor['records']:
 local=record['arguments'][2]&255;types=[kind for _,kind in record['components']]
 assert record['next_type']==('0x726e85aa' if local else '0x850eef66')
 assert (0xd8cc3428 in types)==bool(local)
 assert record['boundary'][0]==0x45ee20 and record['boundary'][3]==1
assert len(original['frame_records'])==63
for name in prior['artifact_hashes']:
 if name.endswith('-routines.json'):
  old=read(r/name)
  if isinstance(old,dict):assert not set(routines).intersection(old),name
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
proof=read(p/'skater-cleanup-browser.json');assert proof['observed']==candidate and proof['status'].startswith('PASS')
def fingerprint(value):
 canonical=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
 for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
 return {'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(value)}
assert proof['rendered_dom_fingerprint']==fingerprint(candidate)
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
paths=set(p.glob('skater-cleanup-*'))|{prior_path,p/'skater-finalize-audit.json'}
paths.update(p/name for name in ['audit-skater-cleanup.py','build-skater-cleanup-draft.py','pin-skater-cleanup.py','probe-skater-cleanup.py','serve-skater-cleanup.py','verify-skater-cleanup-checkpoint.mjs'])
for f in paths:
 if f.is_file() and f.suffix!='.log' and f not in [target,p/'skater-cleanup-next.txt',p/'skater-cleanup-audit.json']:
  artifacts[str(f.relative_to(r))]=sha(f)
  if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={**prior,'result':'original comparisons, Node and actual Chromium pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':20,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':753,'unpromoted_functions_across_separate_experiments':770,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'browser_suites':146,
 'new_cases':441,'new_calls_including_existing_dependencies':914,'new_interrupted_calls':32,'instruction_coverage':coverage,
 'coverage_limit':'557/557 new instructions exercised, not exhaustive input or branch coverage. Of914 calls,882 complete and32 stop at the explicit next constructor boundary. Successful allocations and initialized dependencies are contracts. Two explicitly declared global float-store lanes require physical x87 quieting (28 signaling words); sign and payload remain exact, five corruption cases are rejected. No NaN classification, numeric masks or uninitialized-byte allowances. Existing D3DX reciprocal seeds retain the Unicorn2.1.4 model, not physical processor approximation tables.',
 'scope':fixture['scope'],
 'unrecovered_lifecycle':'CleanupState is recovered and local skater construction now stops before Walk726e85aa; remote850eef66 unchanged. Renderer constructors/rendering, remaining startup/frames, later score linkage and original playable training remain unfinished.',
 'prior_skater_constructor_prefix':prior['skater_constructor_prefix'],'skater_constructor_prefix':constructor,
 'cleanup_evidence':{'completed_calls':882,'interrupted_calls':32,'frame_records':original['frame_records'],'shared_startup_records':original['shared_startup_records'],'physical_x87_quieted_words':28,'global_quieting_corruption_cases_rejected':5,'derived_lighting_source':'local/analysis/skater-cleanup-model-derived.c'},
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':fingerprint(candidate),'playable':False}
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
