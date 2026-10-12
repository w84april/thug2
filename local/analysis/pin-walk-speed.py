"""Pin original animation-speed comparisons, populated queues and Chromium proof."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
prior_path=p/'walk-tail-checkpoint.json';assert sha(prior_path)=='4299f5cf5f08b4582e03fbebab0b59203ae9ef9a72accf13e7a00c28c4d81831'
prior=read(prior_path);target=p/'walk-speed-checkpoint.json';assert not target.exists()
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
b=read(p/'walk-speed-draft.build.json');module=p/'walk-speed-draft.wasm'
assert sha(module)==b['sha256']=='6bd18ec992651d35eb3b053fd87488908454a02bc05954df080e7b978f1a01da'
assert module.stat().st_size==898518 and b['source_hashes']==prior['source_hashes']
for name,digest in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==digest,name
previous=read(p/'walk-tail-browser.json')['observed']['suites']
suites={name:read(p/('walk-speed-checkpoint-'+name.replace('_','-')+'-result.json')) for name in ['walk_speed',*previous]}
assert len(suites)==159
for name,result in suites.items():
 assert result['result']=='pass',name
 if name in previous:assert result==previous[name],name
original=read(p/'walk-speed-original.json');fixture=read(p/'walk-speed-fixtures.json');unit=suites['walk_speed'];routines=read(p/'walk-speed-routines.json');coverage=original['instruction_coverage']
assert set(coverage)==set(routines) and len(routines)==2
assert (sum(x['covered'] for x in coverage.values()),sum(x['total'] for x in coverage.values()))==(157,171)
assert all(not x['excluded'] for x in coverage.values())
assert original['cases']==unit['cases']==267 and original['calls']==unit['calls']==547 and original['counts']==unit['counts']
assert unit['nan_fields_classification_only']==unit['indeterminate_word_comparisons']==0 and not fixture['float_fields']
assert unit['indeterminate_byte_comparisons']==240
assert len(original['queue_records'])==32 and sum(len(x['messages']) for x in original['queue_records'])==40
assert original['heap_events']=={'0x5bb0e0':40,'0x5bafc0':120,'0x5bb110':40}
for case in fixture['cases']:
 for step in case['steps']:
  assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','quiet_double_fields','global_quiet_float_indices','global_bit_masks','float_fields','global_float_indices','indeterminate_words','compression_records'])
  assert len(step['indeterminate_bytes'])==len(step['payload_provenance'])
  for row in step['payload_provenance']:
   assert row['copy_instruction']=='0x45500e' and row['source_writes_before_copy']==0 and row['source_offset'] in [5,6,7]
   assert row['defined_prefix_writes']==[1]*5 and row['destination']==row['payload']+row['source_offset']
parent=read(p/'walk-speed-parent-discovery.json');assert parent['cases']==120 and parent['checksum_entry']=='0x419950'
assert sum(len(x['commands']) for x in parent['records'])==60 and all(c['return']==2 for x in parent['records'] for c in x['commands'])
negative=read(p/'walk-speed-padding-checks.json');assert negative['result']=='pass' and negative['checks']==12
for name,digest in negative['files'].items():assert sha(p/name)==digest,name
extents=read(p/'walk-speed-extents.json');assert extents['result']=='pass' and extents['routines_sha256']==sha(p/'walk-speed-routines.json') and set(extents['checked'])==set(routines)
for name in prior['artifact_hashes']:
 if name.endswith('-routines.json'):
  old=read(r/name)
  if isinstance(old,dict):assert not set(routines).intersection(old),name
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
proof=read(p/'walk-speed-browser.json');assert proof['observed']==candidate and proof['status'].startswith('PASS')
def fingerprint(value):
 canonical=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
 for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
 return {'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(value)}
assert proof['rendered_dom_fingerprint']==fingerprint(candidate)
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
paths=set(p.glob('walk-speed-*'))|{prior_path,p/'walk-tail-audit.json'}
paths.update(p/name for name in ['audit-walk-speed.py','build-walk-speed-draft.py','pin-walk-speed.py','probe-walk-speed.py','probe-walk-speed-parent.py','serve-walk-speed.py','verify-walk-speed-checkpoint.mjs','check-walk-speed-padding.mjs'])
for f in paths:
 if f.is_file() and f.suffix!='.log' and f!=target and not f.name.endswith('-next.txt') and f!=p/'walk-speed-audit.json':
  artifacts[str(f.relative_to(r))]=sha(f)
  if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={**prior,'result':'original comparisons, Node and actual Chromium pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':2,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':818,'unpromoted_functions_across_separate_experiments':835,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'browser_suites':159,
 'new_cases':267,'new_calls_including_existing_dependencies':547,'new_interrupted_calls':0,'instruction_coverage':coverage,
 'coverage_limit':'157/171 instructions exercised; no exclusions. Fourteen unexercised instructions remain in the denominator: two alignment LEAs and twelve null-link return instructions after a preceding dereference in the observed live-sentinel graphs. Finite nonzero relative timeline spans and valid allocated list sentinels are fixture contracts. All547 root calls complete; defined arena, globals, registers, queue links and payload bytes compare. Only three original-write-proven undefined payload bytes per message receive byte-specific allowances, checked240 times across steps. Twelve negative/control tests protect that boundary. No numeric allowances.',
 'scope':fixture['scope'],
 'unrecovered_lifecycle':'Animation channel speed and component forwarding are recovered, including real populated local network queues. Walking parent52a2c0 and animation checksum/forward dispatch419950/4198d0 remain unrecovered. Original discovery shows its bd4edd44 legacy command returns2 from419950; do not replace it with controller-level forwarding. Shared Walk transfer527600, ground/shadow validation527080, full state dispatch, airborne/hanging/rail updates, original asset startup, renderer creation/rendering and playable training remain unfinished. Common Walk51/142 and constructor277/463 remain unchanged.',
 'walk_speed_evidence':{'completed_calls':547,'interrupted_calls':0,'queue_cases':32,'queued_messages':40,'queue_records':original['queue_records'],'heap_events':original['heap_events'],'indeterminate_byte_comparisons':240,'padding_controls':12,'new_numeric_allowances':0,'unreachable_exclusions':{}},
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':fingerprint(candidate),'playable':False}
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
