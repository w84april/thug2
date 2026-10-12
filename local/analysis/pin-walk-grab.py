"""Pin the complete ledge-grab graph only after original, Node and Chromium checks."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
prior_path=p/'walk-floor-checkpoint.json';assert sha(prior_path)=='3504690bb4d756240cc4a0129056da8c9e4e575d861a0871f05f507640138b40'
prior=read(prior_path);target=p/'walk-grab-checkpoint.json';assert not target.exists()
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
b=read(p/'walk-grab-draft.build.json');module=p/'walk-grab-draft.wasm'
assert sha(module)==b['sha256']=='e2739efc7299ff7920a4367bd6678efddc2bed3e127b7470c2bf9455f39e6e4a'
assert module.stat().st_size==889495 and b['source_hashes']==prior['source_hashes']
for name,digest in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==digest,name
previous=read(p/'walk-floor-browser.json')['observed']['suites']
suites={name:read(p/('walk-grab-checkpoint-'+name.replace('_','-')+'-result.json')) for name in ['walk_grab',*previous]}
assert len(suites)==152
for name,result in suites.items():
 assert result['result']=='pass',name
 if name in previous:assert result==previous[name],name
original=read(p/'walk-grab-original.json');fixture=read(p/'walk-grab-fixtures.json');coverage=original['instruction_coverage'];routines=read(p/'walk-grab-routines.json');unit=suites['walk_grab']
assert (original['cases'],original['calls'],unit['cases'],unit['calls'])==(894,1256,894,1256)
assert original['counts']==unit['counts'] and unit['nan_fields_classification_only']==unit['indeterminate_word_comparisons']==0
assert sum(unit['counts'].values())==1256 and unit['counts']['thug_collision_probe_initialize']==96 and unit['counts']['thug_walk_enter_hang_draft']==18
assert len(coverage)==5 and set(coverage)==set(routines)
assert (sum(x['covered'] for x in coverage.values()),sum(x['total'] for x in coverage.values()))==(1832,1832)
assert all(not row['missing'] and not row['excluded'] for row in coverage.values()) and not fixture['float_fields']
extents=read(p/'walk-grab-extents.json');assert extents['result']=='pass' and extents['routines_sha256']==sha(p/'walk-grab-routines.json') and set(extents['checked'])==set(routines)
for case in fixture['cases']:
 for step in case['steps']:
  assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','quiet_double_fields','global_quiet_float_indices','global_bit_masks','float_fields','global_float_indices','indeterminate_bytes','indeterminate_words','compression_records'])
callbacks=original['callback_records'];assert len(callbacks)==18 and sum(x['callbacks'] for x in callbacks)==12 and all(x['state']==2 for x in callbacks)
for name in prior['artifact_hashes']:
 if name.endswith('-routines.json'):
  old=read(r/name)
  if isinstance(old,dict):assert not set(routines).intersection(old),name
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
proof=read(p/'walk-grab-browser.json');assert proof['observed']==candidate and proof['status'].startswith('PASS')
def fingerprint(value):
 canonical=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
 for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
 return {'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(value)}
assert proof['rendered_dom_fingerprint']==fingerprint(candidate)
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
paths=set(p.glob('walk-grab-*'))|{prior_path,p/'walk-floor-audit.json'}
paths.update(p/name for name in ['audit-walk-grab.py','build-walk-grab-draft.py','pin-walk-grab.py','probe-walk-grab.py','serve-walk-grab.py','verify-walk-grab-checkpoint.mjs'])
for f in paths:
 if f.is_file() and f.suffix!='.log' and f not in [target,p/'walk-grab-next.txt',p/'walk-grab-audit.json']:
  artifacts[str(f.relative_to(r))]=sha(f)
  if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={**prior,'result':'original comparisons, Node and actual Chromium pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':5,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':801,'unpromoted_functions_across_separate_experiments':818,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'browser_suites':152,
 'new_cases':894,'new_calls_including_existing_dependencies':1256,'new_interrupted_calls':0,'instruction_coverage':coverage,
 'coverage_limit':'1832/1832 new instructions exercised without exclusions; not exhaustive inputs or branches. All1256 calls complete:1142 new-root calls,96 existing probe initializations and18 existing hanging callbacks. Whole defined arena/global state and preserved registers compare, including automatic cache identities/lifetimes. No new numeric masks, NaN classification, quieting or indeterminate-field allowances. Initialized finite graphs and valid capacities are contracts. Existing PC24/transcendental emulation contracts remain unchanged.',
 'scope':fixture['scope'],
 'unrecovered_lifecycle':'Full ledge selection43ec40 and dependencies57dda0,440690,43fe30,43f3a0 are recovered. Floor52b370, full ground/Walk and intervening animation frames, remaining startup, renderer creation/rendering and original playable training remain unfinished. Ground63/134, common Walk51/142 and constructor277/463 remain unchanged.',
 'walk_grab_evidence':{'completed_calls':1256,'new_routine_calls':1142,'existing_probe_initializations':96,'existing_hang_callbacks':18,'interrupted_calls':0,'callback_records':callbacks,'new_comparison_allowances':0,'new_unreachable_exclusions':{},'ground_parent_unchanged':'63/134'},
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':fingerprint(candidate),'playable':False}
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
