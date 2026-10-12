"""Pin complete airborne steering, plane correction, transfer and ceiling helpers."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
prior_path=p/'walk-ground-frame-checkpoint.json';assert sha(prior_path)=='a8f5ca50d375061d22be900fba7afce20405a0d81d71416b2b91199de5af1c3e'
prior=read(prior_path);target=p/'walk-air-motion-checkpoint.json';assert not target.exists()
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
module=p/'walk-air-ceiling-draft.wasm';b=read(module.with_suffix('.build.json'))
assert sha(module)==b['sha256']=='72d1d86ff1504ac13a3abad182185162c7c5afc9e33d446f56c86d14d7f0bd71'
assert module.stat().st_size==906415 and b['source_hashes']==prior['source_hashes']
for name,digest in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==digest,name
new=['walk-air-plane','walk-air-transfer','walk-air-steering','walk-air-ceiling']
previous=read(p/'walk-ground-frame-browser.json')['observed']['suites']
suites={name:read(p/('walk-air-motion-checkpoint-'+name.replace('_','-')+'-result.json')) for name in [*[n.replace('-','_') for n in new],*previous]}
assert len(suites)==168
for name,result in suites.items():
 assert result['result']=='pass',name
 if name in previous:assert result==previous[name],name
routines={};coverage={};cache_records=0
for name,address,cases,calls,instructions in [('walk-air-plane','0x527c50',154,372,115),('walk-air-transfer','0x527510',74,94,62),('walk-air-steering','0x526850',192,468,222),('walk-air-ceiling','0x526ba0',131,270,147)]:
 claimed=read(p/(name+'-routines.json'));assert set(claimed)=={address};routines.update(claimed)
 original=read(p/(name+'-original.json'));fixture=read(p/(name+'-fixtures.json'));unit=suites[name.replace('-','_')]
 assert original['cases']==unit['cases']==cases and original['calls']==unit['calls']==calls and original['counts']==unit['counts']
 assert unit['nan_fields_classification_only']==unit['indeterminate_word_comparisons']==unit['indeterminate_byte_comparisons']==0 and not fixture['float_fields']
 assert unit['virtual_wait_callbacks']==0
 row=original['instruction_coverage'][address];assert row['covered']==row['total']==instructions and not row['excluded'] and not row['missing'];coverage[address]=row
 extents=read(p/(name+'-extents.json'));assert extents['result']=='pass' and extents['routines_sha256']==sha(p/(name+'-routines.json')) and set(extents['checked'])=={address}
 for case in fixture['cases']:
  for step in case['steps']:
   assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','quiet_double_fields','global_quiet_float_indices','global_bit_masks','float_fields','global_float_indices','indeterminate_words','indeterminate_bytes','compression_records'])
   cache_records+=len(step.get('stack_objects',[]))
 if name=='walk-air-transfer':assert fixture['cache_capture']=='destructor-v1' and original['callees']['0x40ab40']==64
assert cache_records==64
ceiling=read(p/'walk-air-ceiling-original.json');assert ceiling['branch_hits']=={'0x526c76':80,'0x526d97':56,'0x526dbd':80,'0x526cb5':36,'0x526d51':24}
for name in prior['artifact_hashes']:
 if name.endswith('-routines.json'):
  old=read(r/name)
  if isinstance(old,dict):assert not set(routines).intersection(old),name
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
proof=read(p/'walk-air-motion-browser.json');assert proof['observed']==candidate and proof['status'].startswith('PASS')
def fingerprint(value):
 canonical=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
 for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
 return {'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(value)}
assert proof['rendered_dom_fingerprint']==fingerprint(candidate)
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
paths={prior_path,p/'walk-ground-frame-audit.json',*p.glob('walk-air-motion-checkpoint-*-result.json')}
for name in new:
 for suffix in ['-draft.c','-draft.wasm','-draft.build.json','-original.json','-fixtures.json','-memory.bin','-extents.py','-extents.json','-routines.json']:paths.add(p/(name+suffix))
 for prefix,suffix in [('build-','-draft.py'),('probe-','.py'),('verify-','-unit.mjs')]:paths.add(p/(prefix+name+suffix))
for name in ['audit-walk-air-motion.py','pin-walk-air-motion.py','serve-walk-air-motion.py','verify-walk-air-motion-checkpoint.mjs','walk-air-motion-browser.html','walk-air-motion-browser.json','walk-air-motion-worker.mjs']:paths.add(p/name)
for f in paths:
 assert f.is_file(),f
 artifacts[str(f.relative_to(r))]=sha(f)
 if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={**prior,'result':'original comparisons, Node and actual Chromium pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':4,'original_addresses':list(routines),
 'unpromoted_functions_in_this_module':825,'unpromoted_functions_across_separate_experiments':842,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'browser_suites':168,
 'new_cases':551,'new_calls_including_existing_dependencies':1204,'new_interrupted_calls':0,'instruction_coverage':coverage,
 'coverage_limit':'All546 original helper instructions execute with no exclusions, numeric allowances, indeterminate-field allowances or interrupted calls. Tests exercise finite parameter/vector state, repeated calls, time-lock boundaries, input/trajectory gates, live/dead/replaced moving contacts, ceiling-hit velocity projection and second-query hit/miss geometry.64 automatic caches compare at destruction using the unchanged test-only observer. The80 ceiling object events execute without subscribed script callbacks. These are four complete helpers, not complete airborne frames; no airborne dispatcher routine count is claimed.',
 'scope':'Four complete airborne helpers: plane displacement/velocity projection527c50, transfer527510, steering526850 and overhead collision526ba0.551 cases and1204 original calls compare in Node and Chromium, with546/546 instructions exercised. The full airborne update and playable training remain unfinished.',
 'unrecovered_lifecycle':'The ground-entry and animation-entry partial Walk updates remain preserved. Airborne plane correction, transfer, steering and ceiling collisions are now recovered, but airborne landing52a700,526e00,5293f0,43f030/442170 entry wrappers and full52cef0 integration remain unfinished in this checkpoint. Hanging440bf0, rail4425b0, full dispatcher recovery, animation checksum/forward dispatch419950/4198d0, original asset startup, renderer creation/rendering and playable training also remain unfinished. Constructor277/463 and maintained frame prefix51/142 are unchanged.',
 'walk_air_motion_evidence':{'completed_calls':1204,'interrupted_calls':0,'complete_helpers':4,'cases':551,'instructions':546,'live_cache_observations':64,'ceiling_hits':80,'ceiling_velocity_projections':36,'ceiling_second_query_hits':24,'ceiling_second_query_misses':56,'ceiling_object_events':80,'subscribed_event_callbacks':0,'new_numeric_allowances':0,'new_indeterminate_allowances':0,'unreachable_exclusions':{}},
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':fingerprint(candidate),'playable':False}
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
