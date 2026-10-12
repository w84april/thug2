"""Pin full airborne frames and their partial common-loop integration."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
prior_path=p/'walk-air-catch-checkpoint.json';assert sha(prior_path)=='e3cf026e2db35ae18996c1f74d44f6d9df3d952656e71ea87321d3ae2994c9c2'
prior=read(prior_path);target=p/'walk-air-flight-checkpoint.json';assert not target.exists()
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
module=p/'walk-air-update-draft.wasm';b=read(module.with_suffix('.build.json'))
assert sha(module)==b['sha256']=='f19c829ccec1403690eed63ed91ed3d7a6c599c0eef9904a0fc1abc6b49af73a'
assert module.stat().st_size==917119 and b['source_hashes']==prior['source_hashes']
for name,digest in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==digest,name
new=['walk-air-frame','walk-air-update'];previous=read(p/'walk-air-catch-browser.json')['observed']['suites']
suites={name:read(p/('walk-air-flight-checkpoint-'+name.replace('_','-')+'-result.json')) for name in [*[n.replace('-','_') for n in new],*previous]}
assert len(suites)==176
for name,result in suites.items():
 assert result['result']=='pass',name
 if name in previous:assert result==previous[name],name
routines=read(p/'walk-air-frame-routines.json');assert set(routines)=={'0x52cef0'}
coverage=read(p/'walk-air-frame-original.json')['instruction_coverage'];assert coverage=={'0x52cef0':{'covered':296,'total':296,'missing':[],'excluded':{}}}
extents=read(p/'walk-air-frame-extents.json');assert extents['result']=='pass' and extents['routines_sha256']==sha(p/'walk-air-frame-routines.json') and set(extents['checked'])==set(routines)
callbacks=words=padding=0
for name,cases,calls,expected_words,expected_padding in [('walk-air-frame',190,232,80,0),('walk-air-update',76,768,1244,378)]:
 original=read(p/(name+'-original.json'));fixture=read(p/(name+'-fixtures.json'));unit=suites[name.replace('-','_')]
 assert original['cases']==unit['cases']==cases and original['calls']==unit['calls']==calls and original['counts']==unit['counts']
 assert not fixture['float_fields'] and unit['nan_fields_classification_only']==0
 assert (unit['indeterminate_word_comparisons'],unit['indeterminate_byte_comparisons'])==(expected_words,expected_padding)
 local_callbacks=local_words=local_padding=0
 for case in fixture['cases']:
  for step in case['steps']:
   assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','quiet_double_fields','global_quiet_float_indices','global_bit_masks','float_fields','global_float_indices','compression_records'])
   w=step.get('indeterminate_words',[]);provenance=step.get('indeterminate_provenance',[])
   assert len(w)==len(provenance) and set(w)=={x['destination'] for x in provenance}
   for row in provenance:
    assert row['source_writes_before_copy']==0 and row['copy_instruction']=={0x70:'0x4f81f1',0xa8:'0x43aa0f'}[row['source_offset']]
    assert row['destination'] in fixture['indeterminate_word_addresses']
   pad=step.get('indeterminate_bytes',[]);provenance=step.get('payload_provenance',[])
   assert len(pad)==len(provenance) and set(pad)=={x['destination'] for x in provenance}
   for row in provenance:
    assert row['source_writes_before_copy']==0 and row['copy_instruction']=='0x45500e' and row['source_offset'] in [5,6,7]
    assert row['defined_prefix_writes']==[1]*5 and row['destination'] in fixture['indeterminate_byte_addresses']
   local_callbacks+=step.get('callbacks',0);local_words+=len(w);local_padding+=len(pad)
 assert local_callbacks==unit['virtual_wait_callbacks'] and (local_words,local_padding)==(expected_words,expected_padding)
 callbacks+=local_callbacks;words+=local_words;padding+=local_padding
assert (callbacks,words,padding)==(40,1324,378)
original=read(p/'walk-air-frame-original.json');transfer=[x for x in original['records'] if x['label'].startswith('transfer inside air frame')]
assert len(transfer)==4 and all(x['state']==1 and x['event']==0x2eda83ea for x in transfer)
projectiles=[x for x in original['records'] if x['label'].startswith('projectile inside air frame')]
assert len(projectiles)==20 and all(x['callbacks']==1 for x in projectiles)
partial=read(p/'walk-air-update-original.json')['partial_frame'];assert (partial['covered'],partial['total'],partial['completed_calls'],partial['recovered_routine'])==(129,142,768,False)
for name in prior['artifact_hashes']:
 if name.endswith('-routines.json'):
  old=read(r/name)
  if isinstance(old,dict):assert not set(routines).intersection(old),name
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
proof=read(p/'walk-air-flight-browser.json');assert proof['observed']==candidate and proof['status'].startswith('PASS')
def fingerprint(value):
 canonical=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
 for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
 return {'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(value)}
assert proof['rendered_dom_fingerprint']==fingerprint(candidate)
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
paths={prior_path,p/'walk-air-catch-audit.json',*p.glob('walk-air-flight-checkpoint-*-result.json')}
for name in new:
 for suffix in ['-draft.c','-draft.wasm','-draft.build.json','-original.json','-fixtures.json','-memory.bin']:paths.add(p/(name+suffix))
 for prefix,suffix in [('build-','-draft.py'),('probe-','.py'),('verify-','-unit.mjs')]:paths.add(p/(prefix+name+suffix))
for suffix in ['-extents.py','-extents.json','-routines.json']:paths.add(p/('walk-air-frame'+suffix))
for name in ['audit-walk-air-flight.py','pin-walk-air-flight.py','serve-walk-air-flight.py','verify-walk-air-flight-checkpoint.mjs','walk-air-flight-browser.html','walk-air-flight-browser.json','walk-air-flight-worker.mjs']:paths.add(p/name)
for f in paths:
 assert f.is_file(),f
 artifacts[str(f.relative_to(r))]=sha(f)
 if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={**prior,'result':'original comparisons, Node and actual Chromium pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':1,'original_addresses':list(routines),
 'unpromoted_functions_in_this_module':835,'unpromoted_functions_across_separate_experiments':852,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'browser_suites':176,
 'new_cases':266,'new_calls_including_existing_dependencies':1000,'new_interrupted_calls':0,'instruction_coverage':coverage,
 'coverage_limit':'296/296 original airborne-root instructions execute without exclusions or interrupted calls. The partial common loop executes129/142 instructions and earns no routine count. No numeric allowances.1324 retained-probe word and378 existing network-padding byte comparisons use the unchanged checker and original-write provenance. Successful wallplant callbacks retain separate helper evidence; they are not yet exercised from the full airborne root.',
 'scope':'Recover the complete airborne Walk52cef0 and connect it to ground/air/animation paths of52d4b0.266 cases and1000 completed original calls match in Node and Chromium, including repeated falls, landings, continued ground motion, successful transfers, projectile scripts and40 real QB callbacks. Hanging/rail frame handlers remain explicit boundaries. The game is not playable.',
 'unrecovered_lifecycle':'Complete airborne52cef0 now connects through a partial common Walk loop; hanging440bf0, rail4425b0 and full dispatcher recovery remain unfinished. Successful nested standard-wallplant callbacks need connected-root validation. Animation checksum/forward dispatch419950/4198d0, original asset startup, renderer creation/rendering and playable training remain unfinished. Constructor277/463 and maintained frame prefix51/142 are unchanged.',
 'walk_air_flight_evidence':{'completed_calls':1000,'interrupted_calls':0,'complete_helpers':1,'cases':266,'covered_instructions':296,'total_instructions':296,'qb_callbacks':40,'connected_projectile_callbacks':20,'connected_transfer_cases':4,'common_loop_calls':768,'common_loop_coverage':partial,'indeterminate_probe_word_comparisons':1324,'indeterminate_padding_byte_comparisons':378,'new_numeric_allowances':0,'checker_changes':0,'unreachable_exclusions':{}},
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':fingerprint(candidate),'playable':False}
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
