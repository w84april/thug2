"""Pin full floor/ground recovery after original, Node and Chromium comparisons."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
prior_path=p/'walk-grab-checkpoint.json';assert sha(prior_path)=='acf120b089af957c7c28d61c8185e0c5122551e17ac82cba01de0a98015cd895'
prior=read(prior_path);target=p/'walk-grounded-checkpoint.json';assert not target.exists()
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
b=read(p/'walk-grounded-draft.build.json');module=p/'walk-grounded-draft.wasm'
assert sha(module)==b['sha256']=='617995ad16193b0c108adcfead1dd81ddfbd80c5115c8b2417c9fa5bb81851f4'
assert module.stat().st_size==891551 and b['source_hashes']==prior['source_hashes']
for name,digest in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==digest,name
previous=read(p/'walk-grab-browser.json')['observed']['suites']
suites={name:read(p/('walk-grounded-checkpoint-'+name.replace('_','-')+'-result.json')) for name in ['walk_grounded',*previous]}
assert len(suites)==153
for name,result in suites.items():
 assert result['result']=='pass',name
 if name in previous:assert result==previous[name],name
original=read(p/'walk-grounded-original.json');fixture=read(p/'walk-grounded-fixtures.json');coverage=original['instruction_coverage'];routines=read(p/'walk-grounded-routines.json');unit=suites['walk_grounded']
assert (original['cases'],original['calls'],unit['cases'],unit['calls'])==(164,262,164,262)
assert original['counts']==unit['counts']=={'thug_walk_floor_draft':88,'thug_walk_ground_draft':174}
assert unit['nan_fields_classification_only']==0 and unit['indeterminate_word_comparisons']==512
assert len(coverage)==2 and set(coverage)==set(routines)
assert (sum(x['covered'] for x in coverage.values()),sum(x['total'] for x in coverage.values()))==(394,410)
assert not coverage['0x52b370']['missing'] and all(not row['excluded'] for row in coverage.values()) and not fixture['float_fields']
event=read(p/'walk-grounded-event-evidence.json');assert event['result']=='pass' and event['original_sha256']==sha(p/'walk-grounded-original.json')
assert event['missing_instructions']==coverage['0x52d300']['missing'] and event['observations']==174 and not event['exclusions']
extents=read(p/'walk-grounded-extents.json');assert extents['result']=='pass' and extents['routines_sha256']==sha(p/'walk-grounded-routines.json') and set(extents['checked'])==set(routines)
undefined=0
for case in fixture['cases']:
 for step in case['steps']:
  assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','quiet_double_fields','global_quiet_float_indices','global_bit_masks','float_fields','global_float_indices','indeterminate_bytes','compression_records'])
  words=step.get('indeterminate_words',[]);provenance=step.get('indeterminate_provenance',[])
  assert len(words)==len(provenance) and set(words)=={v['destination'] for v in provenance}
  assert all(v['source_offset'] in [0x70,0xa8] and v['source_writes_before_copy']==0 for v in provenance)
  undefined+=len(words)
assert undefined==512
negative=read(p/'walk-grounded-negative.json');assert negative['result']=='pass' and negative['corruptions_rejected']==6 and negative['undefined_word_mutation_accepted']
assert len(original['floor_records'])==30 and sum(v['callbacks'] for v in original['floor_records'])==38
assert len(original['escape_records'])==8 and all(v['diagnostics']==1 and v['state']==0 for v in original['escape_records'])
assert len(original['exit_records'])==10 and all(v['cache']==0 for v in original['exit_records'])
for name in prior['artifact_hashes']:
 if name.endswith('-routines.json'):
  old=read(r/name)
  if isinstance(old,dict):assert not set(routines).intersection(old),name
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
proof=read(p/'walk-grounded-browser.json');assert proof['observed']==candidate and proof['status'].startswith('PASS')
def fingerprint(value):
 canonical=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
 for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
 return {'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(value)}
assert proof['rendered_dom_fingerprint']==fingerprint(candidate)
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
paths=set(p.glob('walk-grounded-*'))|{prior_path,p/'walk-grab-audit.json'}
paths.update(p/name for name in ['audit-walk-grounded.py','build-walk-grounded-draft.py','pin-walk-grounded.py','probe-walk-grounded.py','serve-walk-grounded.py','verify-walk-grounded-checkpoint.mjs'])
for f in paths:
 if f.is_file() and f.suffix!='.log' and f not in [target,p/'walk-grounded-next.txt',p/'walk-grounded-audit.json']:
  artifacts[str(f.relative_to(r))]=sha(f)
  if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={**prior,'result':'original comparisons, Node and actual Chromium pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':2,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':803,'unpromoted_functions_across_separate_experiments':820,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'browser_suites':153,
 'new_cases':164,'new_calls_including_existing_dependencies':262,'new_interrupted_calls':0,'instruction_coverage':coverage,
 'coverage_limit':'394/410 new instructions exercised without exclusions, floor276/276 and ground118/134. Sixteen translated ground-event instructions are unexercised: all174 observed acceleration calls overwrite the event before the branch. This is evidence for initialized finite graphs, not a universal unreachable proof. All262 calls complete. Defined arena/global state and preserved registers compare, including retained stack probe/cache identities.512 four-byte comparisons use original-write-proven uninitialized probe fields70/a8 with later-write revocation; six checker corruptions are rejected. No numeric masks or NaN classification. Existing PC24/transcendental contracts remain unchanged.',
 'scope':fixture['scope'],
 'unrecovered_lifecycle':'Full floor52b370 and ground52d300 are recovered. Shared Walk dispatcher/tail, other movement states and intervening animations, remaining startup, renderer creation/rendering and original playable training remain unfinished. Common Walk51/142 and constructor277/463 remain unchanged.',
 'walk_grounded_evidence':{'completed_calls':262,'floor_calls':88,'ground_calls':174,'interrupted_calls':0,'floor_callbacks':38,'escape_records':original['escape_records'],'exit_records':original['exit_records'],'indeterminate_word_comparisons':512,'numeric_comparison_allowances':0,'new_unreachable_exclusions':{},'event_branch_evidence':event},
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':fingerprint(candidate),'playable':False}
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
