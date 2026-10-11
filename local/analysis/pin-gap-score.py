"""Pin gap score recovery only after original, Node and rendered Chromium agree."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
prior_path=p/'skater-ground-checkpoint.json';assert sha(prior_path)=='afdbeeb0f9a8e76f1e6ab0e8ea83811cd0905aeaf09c6ce259e15dab03d3881a'
prior=read(prior_path);target=p/'gap-score-checkpoint.json';assert not target.exists()
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
b=read(p/'gap-score-draft.build.json');module=p/'gap-score-draft.wasm'
assert sha(module)==b['sha256']=='3d5408585967772c59956ed63f4a0847c620fccce4373f6d80b5c95018211991'
assert module.stat().st_size==826489 and b['source_hashes']==prior['source_hashes']
for name,digest in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==digest,name
previous=read(p/'skater-ground-browser.json')['observed']['suites']
suites={name:read(p/('gap-score-checkpoint-'+name.replace('_','-')+'-result.json')) for name in ['gap_score',*previous]}
assert len(suites)==139
for name,result in suites.items():
 assert result['result']=='pass',name
 if name in previous:assert result==previous[name],name
unit=read(p/'gap-score-original.json');fixture=read(p/'gap-score-fixtures.json');routines=read(p/'gap-score-routines.json')
assert (unit['cases'],unit['calls'],suites['gap_score']['cases'],suites['gap_score']['calls'])==(498,1408,498,1408)
assert unit['counts']==suites['gap_score']['counts'] and suites['gap_score']['nan_fields_classification_only']==0
coverage=unit['instruction_coverage'];assert set(coverage)==set(routines) and len(coverage)==9
assert (sum(x['covered'] for x in coverage.values()),sum(x['total'] for x in coverage.values()))==(501,502)
assert {a:x['missing'] for a,x in coverage.items() if x['missing']}=={'0x562620':['0x56269d']}
assert not any(x['excluded'] for x in coverage.values()) and not fixture['float_fields']
for case in fixture['cases']:
 for step in case['steps']:assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','quiet_double_fields','global_bit_masks','float_fields','global_float_indices'])
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
proof=read(p/'gap-score-browser.json');assert proof['observed']==candidate and proof['status'].startswith('PASS')
def fingerprint(value):
 canonical=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
 for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
 return {'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(value)}
assert proof['rendered_dom_fingerprint']==fingerprint(candidate)
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
paths=set(p.glob('*gap-score*'))|set(p.glob('gap-command*'))|{prior_path,p/'skater-ground-audit.json'}
for parent in list(paths):
 if parent.is_dir():paths.update(f for f in parent.rglob('*') if f.is_file())
for f in paths:
 if f.is_file() and f not in [target,p/'gap-score-next.txt',p/'gap-score-audit.json']:
  artifacts[str(f.relative_to(r))]=sha(f)
  if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={**prior,'result':'original comparisons, Node and actual Chromium pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':9,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':683,'unpromoted_functions_across_separate_experiments':700,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'browser_suites':139,
 'new_cases':498,'new_calls_including_existing_dependencies':1408,'new_interrupted_calls':0,
 'instruction_coverage':coverage,'coverage_limit':'501/502 instructions exercised; skipped alignment56269d unexercised, no exclusions or numeric allowances. Required script/profile data, valid created-trick indices and terminating lists are fixture contracts.',
 'scope':fixture['scope'],'unrecovered_lifecycle':'Gap score-history dependencies are recovered. Gap start/end commands and concrete node/string ownership are not yet integrated. Existing constructor remains at Trigger; other skater behavior, camera, rendering and playable training remain unfinished.',
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':fingerprint(candidate),'playable':False}
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
