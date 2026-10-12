"""Pin complete hanging/rail helpers after original, Node and Chromium checks."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
prior_path=p/'walk-ledge-checkpoint.json';assert sha(prior_path)=='bd34c53b3c1c8c473954c1e6ecbe041203314e73fe2e1866a9a45c33ac939872'
prior=read(prior_path);target=p/'walk-floor-checkpoint.json';assert not target.exists()
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
b=read(p/'walk-floor-draft.build.json');module=p/'walk-floor-draft.wasm'
assert sha(module)==b['sha256']=='13367604f555ea2d5b74b36be2df6087561a4214fc8b592dfadac5e91e25c321'
assert module.stat().st_size==881906 and b['source_hashes']==prior['source_hashes']
for name,digest in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==digest,name
previous=read(p/'walk-ledge-browser.json')['observed']['suites']
suites={name:read(p/('walk-floor-checkpoint-'+name.replace('_','-')+'-result.json')) for name in ['walk_floor',*previous]}
assert len(suites)==151
for name,result in suites.items():
 assert result['result']=='pass',name
 if name in previous:assert result==previous[name],name
original=read(p/'walk-floor-original.json');fixture=read(p/'walk-floor-fixtures.json');coverage=original['instruction_coverage'];routines=read(p/'walk-floor-routines.json');unit=suites['walk_floor']
assert (original['cases'],original['calls'],unit['cases'],unit['calls'])==(559,811,559,811)
assert original['counts']==unit['counts'] and unit['nan_fields_classification_only']==0
assert sum(unit['counts'].values())==811 and unit['counts']['thug_collision_probe_initialize']==60
assert len(coverage)==12 and set(coverage)==set(routines)
assert (sum(x['covered'] for x in coverage.values()),sum(x['total'] for x in coverage.values()))==(1145,1145)
assert all(not row['missing'] and not row['excluded'] for row in coverage.values()) and not fixture['float_fields']
extents=read(p/'walk-floor-extents.json');assert extents['result']=='pass' and extents['routines_sha256']==sha(p/'walk-floor-routines.json') and set(extents['checked'])==set(routines)
for case in fixture['cases']:
 for step in case['steps']:
  assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','quiet_double_fields','global_quiet_float_indices','global_bit_masks','float_fields','global_float_indices','indeterminate_bytes','indeterminate_words','compression_records'])
callbacks=original['callback_records'];assert len(callbacks)==12 and sum(x['callbacks'] for x in callbacks)==4
assert len(original['rail_records'])==2 and all(x['state']==3 for x in original['rail_records'])
assert len(original['grind_records'])==40
for row in original['collision_records']:assert row['result']==int(row['height']<=6)
assert len(original['collision_records'])==14 and len(original['vertical_records'])==40
assert {x['result'] for x in original['vertical_records']}=={0,1}
assert len(original['coincident_records'])==96 and {x['result'] for x in original['coincident_records']}=={0,1}
assert len(original['follow_records'])==72
assert {(x['result'],x['diagnostics']) for x in original['follow_records']}=={(0,0),(0,1),(1,0),(1,1)}
for name in prior['artifact_hashes']:
 if name.endswith('-routines.json'):
  old=read(r/name)
  if isinstance(old,dict):assert not set(routines).intersection(old),name
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
proof=read(p/'walk-floor-browser.json');assert proof['observed']==candidate and proof['status'].startswith('PASS')
def fingerprint(value):
 canonical=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
 for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
 return {'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(value)}
assert proof['rendered_dom_fingerprint']==fingerprint(candidate)
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
paths=set(p.glob('walk-floor-*'))|{prior_path,p/'walk-ledge-audit.json'}
paths.update(p/name for name in ['audit-walk-floor.py','build-walk-floor-draft.py','pin-walk-floor.py','probe-walk-floor.py','serve-walk-floor.py','verify-walk-floor-checkpoint.mjs'])
for f in paths:
 if f.is_file() and f.suffix!='.log' and f not in [target,p/'walk-floor-next.txt',p/'walk-floor-audit.json']:
  artifacts[str(f.relative_to(r))]=sha(f)
  if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={**prior,'result':'original comparisons, Node and actual Chromium pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':12,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':796,'unpromoted_functions_across_separate_experiments':813,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'browser_suites':151,
 'new_cases':559,'new_calls_including_existing_dependencies':811,'new_interrupted_calls':0,'instruction_coverage':coverage,
 'coverage_limit':'1145/1145 new instructions exercised without exclusions; not exhaustive inputs or branches. All811 comparison calls complete, including60 already recovered probe initializations. Whole defined arena/global state and preserved registers compare; no new numeric masks, NaN classification, quieting or indeterminate-field allowances. Initialized finite graphs and valid capacities are contracts. Existing PC24/transcendental emulation contracts remain unchanged.',
 'scope':fixture['scope'],
 'unrecovered_lifecycle':'Hanging entry, vertical clearance, connected/coincident ledge continuation, upper rail entry and fixed/moving grind selection are recovered. Full ledge selection43ec40 still needs57dda0,440690,43fe30 and43f3a0. Floor52b370, full ground/Walk and intervening rail animation frames, remaining startup, renderer creation/rendering and original playable training remain unfinished. Ground63/134, common Walk51/142 and constructor277/463 are unchanged.',
 'walk_floor_evidence':{'completed_calls':811,'new_routine_calls':751,'existing_probe_initializations':60,'interrupted_calls':0,
  'callback_records':callbacks,'upper_rail_callback_records':original['rail_records'],'grind_records':original['grind_records'],
  'collision_distance_records':original['collision_records'],'vertical_clearance_records':original['vertical_records'],
  'coincident_records':original['coincident_records'],'ledge_continuation_records':original['follow_records'],
  'new_comparison_allowances':0,'new_unreachable_exclusions':{},'ground_parent_unchanged':'63/134'},
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':fingerprint(candidate),'playable':False}
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
