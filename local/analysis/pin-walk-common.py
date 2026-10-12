"""Pin common Walk pose recovery after original, Node and Chromium comparisons."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
prior_path=p/'walk-animation-checkpoint.json';assert sha(prior_path)=='016b8a2c5f73957196b814ce5cd74555e61db1620f8b3780c9aedff41b776e3c'
prior=read(prior_path);target=p/'walk-common-checkpoint.json';assert not target.exists()
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
b=read(p/'walk-common-draft.build.json');module=p/'walk-common-draft.wasm'
assert sha(module)==b['sha256']=='f4a5471b26af949850393dfa5b702749b79985d88c71665ca73985c38d9ee419'
assert module.stat().st_size==895598 and b['source_hashes']==prior['source_hashes']
for name,digest in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==digest,name
previous=read(p/'walk-animation-browser.json')['observed']['suites']
suites={name:read(p/('walk-common-checkpoint-'+name.replace('_','-')+'-result.json')) for name in ['walk_common',*previous]}
assert len(suites)==155
for name,result in suites.items():
 assert result['result']=='pass',name
 if name in previous:assert result==previous[name],name
original=read(p/'walk-common-original.json');fixture=read(p/'walk-common-fixtures.json');coverage=original['instruction_coverage'];routines=read(p/'walk-common-routines.json');unit=suites['walk_common']
assert (original['cases'],original['calls'],unit['cases'],unit['calls'])==(358,1168,358,1168)
assert original['counts']==unit['counts'] and sum(unit['counts'].values())==1168
assert unit['nan_fields_classification_only']==unit['indeterminate_word_comparisons']==0
assert len(coverage)==5 and set(coverage)==set(routines)
assert sum(unit['counts'][row['name']] for row in routines.values())==1040
assert (sum(x['covered'] for x in coverage.values()),sum(x['total'] for x in coverage.values()))==(402,402)
assert all(not row['excluded'] and not row['missing'] for row in coverage.values()) and not fixture['float_fields']
extents=read(p/'walk-common-extents.json');assert extents['result']=='pass' and extents['routines_sha256']==sha(p/'walk-common-routines.json') and set(extents['checked'])==set(routines)
assert extents['checked']['0x529ce0']['indirect_jumps']['0x529e63']['targets']==['0x529e6a','0x529e6a','0x529e97','0x529ee6']
for case in fixture['cases']:
 for step in case['steps']:
  assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','quiet_double_fields','global_quiet_float_indices','global_bit_masks','float_fields','global_float_indices','indeterminate_bytes','indeterminate_words','compression_records'])
flows=original['flow_records'];assert len(flows)==16 and all(v['frames']==4 and v['state']==4 and v['owner_position_matches'] for v in flows)
assert unit['virtual_wait_callbacks']==0
for name in prior['artifact_hashes']:
 if name.endswith('-routines.json'):
  old=read(r/name)
  if isinstance(old,dict):assert not set(routines).intersection(old),name
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
proof=read(p/'walk-common-browser.json');assert proof['observed']==candidate and proof['status'].startswith('PASS')
def fingerprint(value):
 canonical=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
 for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
 return {'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(value)}
assert proof['rendered_dom_fingerprint']==fingerprint(candidate)
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
paths=set(p.glob('walk-common-*'))|{prior_path,p/'walk-animation-audit.json'}
paths.update(p/name for name in ['audit-walk-common.py','build-walk-common-draft.py','pin-walk-common.py','probe-walk-common.py','serve-walk-common.py','verify-walk-common-checkpoint.mjs'])
for f in paths:
 if f.is_file() and f.suffix!='.log' and f not in [target,p/'walk-common-next.txt',p/'walk-common-audit.json']:
  artifacts[str(f.relative_to(r))]=sha(f)
  if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={**prior,'result':'original comparisons, Node and actual Chromium pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':5,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':813,'unpromoted_functions_across_separate_experiments':830,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'browser_suites':155,
 'new_cases':358,'new_calls_including_existing_dependencies':1168,'new_interrupted_calls':0,'instruction_coverage':coverage,
 'coverage_limit':'402/402 new instructions exercised with no exclusions. All1168 calls complete:1040 new-root calls and128 existing animation calls. Defined arena/global state and preserved registers compare, with no numeric or indeterminate-field allowances. Sixteen four-frame sequences advance forward/reverse animation and publish owner position, orientation, velocity and model offsets with moving contacts, tilted up vectors and temporary rotations. These are connected recovered segments, not the full shared Walk frame. The four-entry indexed pose dispatch is independently extent-checked. Existing PC24/transcendental contracts remain unchanged.',
 'scope':fixture['scope'],
 'unrecovered_lifecycle':'Common Walk model-offset decay, up-vector restoration, speed/event filtering and owner/model pose publication and rotation are recovered. Shared Walk collision/event helpers and dispatcher, airborne/hanging/rail updates, full animation scheduling and original asset setup, remaining startup, renderer creation/rendering and original playable training remain unfinished. Common Walk51/142 and constructor277/463 remain unchanged.',
 'walk_common_evidence':{'completed_calls':1168,'new_root_calls':1040,'existing_dependency_calls':128,'interrupted_calls':0,'flow_records':flows,'new_comparison_allowances':0,'new_unreachable_exclusions':{},'indirect_jump_table':extents['checked']['0x529ce0']['indirect_jumps']},
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':fingerprint(candidate),'playable':False}
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
