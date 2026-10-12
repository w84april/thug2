"""Pin animation frames and QB completion only after original/Node/Chromium checks."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
prior_path=p/'walk-grounded-checkpoint.json';assert sha(prior_path)=='2e1e5af2621da1b753c7a4443e12a7765f284fb0bed057c4e4b8812993711f25'
prior=read(prior_path);target=p/'walk-animation-checkpoint.json';assert not target.exists()
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
b=read(p/'walk-animation-draft.build.json');module=p/'walk-animation-draft.wasm'
assert sha(module)==b['sha256']=='542d4a56ff1e9cc7a9ac71faf1462702ef2dbf804883ec8c6b9c2723f276e36e'
assert module.stat().st_size==893422 and b['source_hashes']==prior['source_hashes']
for name,digest in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==digest,name
old=(p/'skater-walk-draft.c').read_text();derived=(p/'walk-animation-component-derived.c').read_text()
assert derived==old.replace('.descriptor=thug_component_descriptor_base,','.descriptor=thug_component_descriptor,')
previous=read(p/'walk-grounded-browser.json')['observed']['suites']
suites={name:read(p/('walk-animation-checkpoint-'+name.replace('_','-')+'-result.json')) for name in ['walk_animation',*previous]}
assert len(suites)==154
for name,result in suites.items():
 assert result['result']=='pass',name
 if name in previous:assert result==previous[name],name
original=read(p/'walk-animation-original.json');fixture=read(p/'walk-animation-fixtures.json');coverage=original['instruction_coverage'];routines=read(p/'walk-animation-routines.json');unit=suites['walk_animation']
assert (original['cases'],original['calls'],unit['cases'],unit['calls'])==(129,354,129,354)
assert original['counts']==unit['counts'] and sum(unit['counts'].values())==354
assert unit['nan_fields_classification_only']==unit['indeterminate_word_comparisons']==0
assert len(coverage)==5 and set(coverage)==set(routines)
assert sum(unit['counts'][row['name']] for row in routines.values())==228
assert (sum(x['covered'] for x in coverage.values()),sum(x['total'] for x in coverage.values()))==(282,285)
assert coverage['0x52ad10']['missing']==['0x52ad46','0x52ad48','0x52ad4d']
assert all(not row['excluded'] and (address=='0x52ad10' or not row['missing']) for address,row in coverage.items()) and not fixture['float_fields']
extents=read(p/'walk-animation-extents.json');assert extents['result']=='pass' and extents['routines_sha256']==sha(p/'walk-animation-routines.json') and set(extents['checked'])==set(routines)
for case in fixture['cases']:
 for step in case['steps']:
  assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','quiet_double_fields','global_quiet_float_indices','global_bit_masks','float_fields','global_float_indices','indeterminate_bytes','indeterminate_words','compression_records'])
flows=original['flow_records'];assert len(flows)==24 and sum(v['callbacks'] for v in flows)==unit['virtual_wait_callbacks']==5
assert all(v['state']==(2 if v['kind']=='hang' else 3) and v['execute_result']==0 for v in flows)
assert sum(v['mode'] in ['advance','reverse'] for v in flows)==6
for name in prior['artifact_hashes']:
 if name.endswith('-routines.json'):
  old=read(r/name)
  if isinstance(old,dict):assert not set(routines).intersection(old),name
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
proof=read(p/'walk-animation-browser.json');assert proof['observed']==candidate and proof['status'].startswith('PASS')
def fingerprint(value):
 canonical=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
 for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
 return {'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(value)}
assert proof['rendered_dom_fingerprint']==fingerprint(candidate)
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
paths=set(p.glob('walk-animation-*'))|{prior_path,p/'walk-grounded-audit.json'}
paths.update(p/name for name in ['audit-walk-animation.py','build-walk-animation-draft.py','pin-walk-animation.py','probe-walk-animation.py','serve-walk-animation.py','verify-walk-animation-checkpoint.mjs'])
for f in paths:
 if f.is_file() and f.suffix!='.log' and f not in [target,p/'walk-animation-next.txt',p/'walk-animation-audit.json']:
  artifacts[str(f.relative_to(r))]=sha(f)
  if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={**prior,'result':'original comparisons, Node and actual Chromium pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':5,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':808,'unpromoted_functions_across_separate_experiments':825,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'browser_suites':154,
 'new_cases':129,'new_calls_including_existing_dependencies':354,'new_interrupted_calls':0,'instruction_coverage':coverage,
 'coverage_limit':'282/285 new instructions exercised without exclusions. Three retained transition instructions handle a failed contact update after the parent already checked its owner; the recovered update has no callbacks and returns true for these live initialized graphs. All354 calls complete:228 new-root calls and126 existing dependency calls. Defined arena/global state and preserved registers compare, with no numeric or indeterminate-field allowances.24 connected grab/frame/QB completion sequences reach hanging or rail state, including six four-frame forward/reverse timelines and five rail script callbacks. Initialized timelines and valid finite graphs are contracts; full scheduling and asset-driven animation are not established. Existing PC24/transcendental contracts remain unchanged.',
 'scope':fixture['scope'],
 'unrecovered_lifecycle':'Walk animation frame52ad10 and completion5298d0/52a180 are recovered, including real QB descriptor forwarding. Shared Walk dispatcher/tail, airborne/hanging/rail updates, animation scheduling and original asset setup, remaining startup, renderer creation/rendering and original playable training remain unfinished. Common Walk51/142 and constructor277/463 remain unchanged.',
 'walk_animation_evidence':{'completed_calls':354,'new_root_calls':228,'existing_dependency_calls':126,'interrupted_calls':0,'flow_records':flows,'adjusted_callback_receiver_cases':6,'new_comparison_allowances':0,'new_unreachable_exclusions':{},'descriptor_slot':'Original64c788 is42bb20; derived Walk table forwards extended descriptors through the recovered member dispatcher.'},
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':fingerprint(candidate),'playable':False}
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
