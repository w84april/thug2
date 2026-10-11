"""Pin level-link and score dependency recovery only after original, Node and rendered Chromium agree."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
prior_path=p/'gap-start-checkpoint.json';assert sha(prior_path)=='aec98f7c8eae810ae53fab7a994f42c4404cbff7f7165911bb5375977ff8fe79'
prior=read(prior_path);target=p/'gap-links-checkpoint.json';assert not target.exists()
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
b=read(p/'gap-links-draft.build.json');module=p/'gap-links-draft.wasm'
assert sha(module)==b['sha256']=='91e2a4f68495a813717d1fbc153578bb92550e474ec4b54a4f3e3031620b0890'
assert module.stat().st_size==835142 and b['source_hashes']==prior['source_hashes']
for name,digest in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==digest,name
previous=read(p/'gap-start-browser.json')['observed']['suites']
suites={name:read(p/('gap-links-checkpoint-'+name.replace('_','-')+'-result.json')) for name in ['gap_links',*previous]}
assert len(suites)==141
for name,result in suites.items():
 assert result['result']=='pass',name
 if name in previous:assert result==previous[name],name
unit=read(p/'gap-links-original.json');fixture=read(p/'gap-links-fixtures.json');routines=read(p/'gap-links-routines.json')
assert (unit['cases'],unit['calls'],suites['gap_links']['cases'],suites['gap_links']['calls'])==(360,998,360,998)
assert unit['counts']==suites['gap_links']['counts'] and suites['gap_links']['nan_fields_classification_only']==0
coverage=unit['instruction_coverage'];assert set(coverage)==set(routines) and len(coverage)==16
assert (sum(x['covered'] for x in coverage.values()),sum(x['total'] for x in coverage.values()))==(508,520)
assert {a:x['missing'] for a,x in coverage.items() if x['missing']}=={'0x5628b0':['0x5628bc','0x5628e6'],'0x5638a0':['0x5638d6','0x563907'],'0x578bc0':['0x578c2c','0x578c2d','0x578c2e','0x578c2f'],'0x578c70':['0x578cdc','0x578cdd','0x578cde','0x578cdf']}
assert unit['partial_command_dispatch']['covered']==71 and unit['partial_command_dispatch']['total']==126 and not unit['partial_command_dispatch']['counted_as_complete']
assert not any(x['excluded'] for x in coverage.values()) and not fixture['float_fields']
for case in fixture['cases']:
 for step in case['steps']:assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','quiet_double_fields','global_bit_masks','float_fields','global_float_indices'])
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
proof=read(p/'gap-links-browser.json');assert proof['observed']==candidate and proof['status'].startswith('PASS')
def fingerprint(value):
 canonical=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
 for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
 return {'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(value)}
assert proof['rendered_dom_fingerprint']==fingerprint(candidate)
old_command=read(p/'gap-start-original.json')['partial_command_dispatch']
combined_missing=sorted(set(old_command['missing'])&set(unit['partial_command_dispatch']['missing']))
assert combined_missing==['0x512e09','0x512e0d','0x512e11','0x512e12','0x512e13']
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
paths=set(p.glob('*gap-links*'))|{prior_path,p/'gap-start-audit.json'}
for parent in list(paths):
 if parent.is_dir():paths.update(f for f in parent.rglob('*') if f.is_file())
for f in paths:
 if f.is_file() and f not in [target,p/'gap-links-next.txt',p/'gap-links-audit.json']:
  artifacts[str(f.relative_to(r))]=sha(f)
  if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={**prior,'result':'original comparisons, Node and actual Chromium pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':16,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':714,'unpromoted_functions_across_separate_experiments':731,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'browser_suites':141,
 'new_cases':360,'new_calls_including_existing_dependencies':998,'new_interrupted_calls':0,
 'instruction_coverage':coverage,'partial_command_dispatch':unit['partial_command_dispatch'],"combined_command_coverage":{"covered":121,"total":126,"missing":["0x512e09","0x512e0d","0x512e11","0x512e12","0x512e13"],"source_suites":["gap-start","gap-links"],"counted_as_complete":False},
 'coverage_limit':'508/520 instructions exercised. Two platform heap-initialization calls, two allocation-failure branches before unchecked use, and eight null-successor exit instructions unexercised. Valid gap-history lists terminate at sentinels, not null pointers. No exclusions or numeric allowances. Required allocation success, valid signed indices, terminating graphs and loaded QB are caller contracts.',
 'scope':fixture['scope'],
 'unrecovered_lifecycle':'Five Gap routes now execute, including linked-node script dispatch. EndGap remains unavailable and the partial dispatcher is not counted complete. Score insertion and history compression, remaining skater construction/frames, camera/rendering and original playable training remain unfinished. Skater construction remains at Trigger.',

 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':fingerprint(candidate),'playable':False}
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
