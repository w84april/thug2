"""Pin two complete helpers and the completed ground-state Walk paths."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
prior_path=p/'walk-frame-speed-checkpoint.json';assert sha(prior_path)=='e3b9d3df78d4f85fa6925bff5b591a65e2c8256a061b4b0c4314a196d637addf'
prior=read(prior_path);target=p/'walk-ground-frame-checkpoint.json';assert not target.exists()
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
b=read(p/'walk-ground-frame-draft.build.json');module=p/'walk-ground-frame-draft.wasm'
assert sha(module)==b['sha256']=='05a91568a80ddba9e4e1127ddfdf7f1f8c1bbae9d04720d455b134451a13c89e'
assert module.stat().st_size==903163 and b['source_hashes']==prior['source_hashes']
for name,digest in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==digest,name
previous=read(p/'walk-frame-speed-browser.json')['observed']['suites']
suites={name:read(p/('walk-ground-frame-checkpoint-'+name.replace('_','-')+'-result.json')) for name in ['walk_transfer','walk_ground_validation','walk_ground_frame',*previous]}
assert len(suites)==164
for name,result in suites.items():
 assert result['result']=='pass',name
 if name in previous:assert result==previous[name],name
routines={};coverage={}
for name,address,cases,calls,covered,total in [('walk-transfer','0x527600',134,162,78,78),('walk-ground-validation','0x527080',132,180,207,209)]:
 new=read(p/(name+'-routines.json'));assert set(new)=={address};routines.update(new)
 original=read(p/(name+'-original.json'));fixture=read(p/(name+'-fixtures.json'));unit=suites[name.replace('-','_')]
 assert original['cases']==unit['cases']==cases and original['calls']==unit['calls']==calls and original['counts']==unit['counts']
 assert unit['nan_fields_classification_only']==unit['indeterminate_word_comparisons']==0 and not fixture['float_fields']
 row=original['instruction_coverage'][address];assert (row['covered'],row['total'])==(covered,total) and not row['excluded'];coverage[address]=row
 extents=read(p/(name+'-extents.json'));assert extents['result']=='pass' and extents['routines_sha256']==sha(p/(name+'-routines.json')) and set(extents['checked'])=={address}
 for case in fixture['cases']:
  for step in case['steps']:
   assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','quiet_double_fields','global_quiet_float_indices','global_bit_masks','float_fields','global_float_indices','indeterminate_words','indeterminate_bytes','compression_records'])
for name in prior['artifact_hashes']:
 if name.endswith('-routines.json'):
  old=read(r/name)
  if isinstance(old,dict):assert not set(routines).intersection(old),name
original=read(p/'walk-ground-frame-original.json');fixture=read(p/'walk-ground-frame-fixtures.json');unit=suites['walk_ground_frame'];frame=original['partial_frame']
assert original['cases']==unit['cases']==82 and original['calls']==unit['calls']==242 and original['counts']==unit['counts']
assert (frame['covered'],frame['total'],frame['completed_calls'],frame['recovered_routine'])==(131,142,242,False)
assert unit['nan_fields_classification_only']==0 and not fixture['float_fields'] and fixture['cache_capture']=='destructor-v1'
assert (unit['indeterminate_word_comparisons'],unit['indeterminate_byte_comparisons'],unit['virtual_wait_callbacks'])==(731,240,14)
assert original['heap_events']['0x5bb0e0']==original['heap_events']['0x5bb110']==32
assert len(original['records'])==82 and sum(x['frames'] for x in original['records'])==242
assert sum(x['frames']>1 for x in original['records'])==56
transfers=[x for x in original['records'] if 'moving_transfer' in x];assert len(transfers)==12 and sum(x['final_state']==1 for x in transfers)==4
cache_records=0
for case in fixture['cases']:
 for step in case['steps']:
  assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','quiet_double_fields','global_quiet_float_indices','global_bit_masks','float_fields','global_float_indices','compression_records'])
  assert len(step['indeterminate_bytes'])==len(step['payload_provenance'])
  assert len(step['indeterminate_words'])==len(step['indeterminate_provenance'])
  cache_records+=len(step['stack_objects'])
  for row in step['payload_provenance']:
   assert row['copy_instruction']=='0x45500e' and row['source_writes_before_copy']==0 and row['source_offset'] in [5,6,7]
   assert row['defined_prefix_writes']==[1]*5 and row['destination']==row['payload']+row['source_offset']
assert cache_records==original['callees']['0x40ab40']==8
for kind,count in [('padding',12),('cache',5)]:
 controls=read(p/('walk-ground-frame-'+kind+'-checks.json'));assert controls['result']=='pass' and controls['checks']==count
 for name,digest in controls['files'].items():assert sha(p/name)==digest,name
boundaries=read(p/'walk-ground-frame-boundaries.json');assert boundaries['result']=='pass' and boundaries['cases']==boundaries['calls']==80
assert boundaries['counts']=={'thug_walk_update_ground_prefix_draft':80}
animation=read(p/'walk-ground-frame-animation-parity.json');assert animation['result']=='pass' and animation['cases']==48 and animation['calls']==336 and animation['counts']['thug_walk_update_ground_prefix_draft']==168
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
proof=read(p/'walk-ground-frame-browser.json');assert proof['observed']==candidate and proof['status'].startswith('PASS')
def fingerprint(value):
 canonical=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
 for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
 return {'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(value)}
assert proof['rendered_dom_fingerprint']==fingerprint(candidate)
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
paths={prior_path,p/'walk-frame-speed-audit.json',*p.glob('walk-ground-frame-checkpoint-*-result.json')}
for name in ['walk-transfer','walk-ground-validation','walk-ground-frame']:
 for suffix in ['-draft.c','-draft.wasm','-draft.build.json','-original.json','-fixtures.json','-memory.bin']:
  paths.add(p/(name+suffix))
 for prefix,suffix in [('build-','-draft.py'),('probe-','.py'),('verify-','-unit.mjs')]:paths.add(p/(prefix+name+suffix))
for name in ['walk-transfer','walk-ground-validation']:
 for suffix in ['-extents.py','-extents.json','-routines.json']:paths.add(p/(name+suffix))
for name in ['audit-walk-ground-frame.py','pin-walk-ground-frame.py','serve-walk-ground-frame.py','verify-walk-ground-frame-checkpoint.mjs','walk-ground-frame-browser.html','walk-ground-frame-browser.json','walk-ground-frame-worker.mjs','walk-ground-frame-cache-capture.c','walk-ground-frame-checks.mjs']:
 paths.add(p/name)
for kind,result in [('cache','cache-checks'),('padding','padding-checks'),('boundaries','boundaries'),('animation','animation-parity')]:
 paths.add(p/('check-walk-ground-frame-'+kind+'.mjs'));paths.add(p/('walk-ground-frame-'+result+'.json'))
for f in paths:
 assert f.is_file(),f
 artifacts[str(f.relative_to(r))]=sha(f)
 if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={**prior,'result':'original comparisons, Node and actual Chromium pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':2,'original_addresses':list(routines),
 'unpromoted_functions_in_this_module':821,'unpromoted_functions_across_separate_experiments':838,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'browser_suites':164,
 'new_cases':348,'new_calls_including_existing_dependencies':584,'new_interrupted_calls':0,'instruction_coverage':coverage,
 'coverage_limit':'Two whole helpers exercise285/287 instructions with no exclusions. The two unexercised paths are ground-validation moving-reference release instructions5273f5/5273fc; both remain implemented and in the denominator. Partial52d4b0 exercises131/142 instructions across242 completed ground-entry frames; the whole dispatcher earns no routine count. An additional Node-only unchanged animation corpus passes168 frames and168 time advances through the new partial export;80 unsupported-state comparisons reach explicit boundaries. These separate checks are not part of584 new completed calls or164 browser suites. Original-write-proven probe fields receive731 word comparisons and message padding240 byte comparisons. No numeric allowances. Cache contents are observed at destruction using a disabled-by-default test-only wrapper that always calls the real destructor;8 live cache observations pass with5 negative/control checks.',
 'scope':original['scope'],
 'unrecovered_lifecycle':'Walking transfer527600 and ground validation527080 are recovered. The new partial52d4b0 completes242 ground-entry frames including connected input/collision, lighting, shadows, pose/events, animation speed, camera and4 successful transfers. The same export separately passes168 original animation-state4 frames. Air52cef0, hanging440bf0 and rail4425b0 entry handlers, full dispatcher recovery, animation checksum/forward dispatch419950/4198d0, original asset startup, renderer creation/rendering and playable training remain unfinished. Focus input stays unpressed in these integrated frames. Constructor277/463 and maintained frame prefix51/142 are unchanged.',
 'walk_ground_frame_evidence':{'completed_calls':584,'interrupted_calls':0,'helper_calls':342,'completed_ground_frames':242,'connected_sequences':56,'integrated_transfer_cases':12,'successful_transfers':4,'partial_frame':frame,'queued_messages':32,'indeterminate_word_comparisons':731,'indeterminate_byte_comparisons':240,'padding_controls':12,'cache_lifetime_controls':5,'live_cache_observations':8,'event_callbacks':22,'unfinished_state_boundaries':80,'additional_animation_frames':168,'additional_time_advances':168,'new_numeric_allowances':0,'unreachable_exclusions':{}},
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':fingerprint(candidate),'playable':False}
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
