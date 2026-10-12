"""Pin rail climbing, exits and connected common-loop frames."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
prior_path=p/'walk-air-flight-checkpoint.json';assert sha(prior_path)=='f3777abf1b4e0be756481a31ca5590d3577bc9077a1eae869ed244b083c68c09'
prior=read(prior_path);target=p/'walk-rail-climb-checkpoint.json';assert not target.exists()
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
module=p/'walk-rail-update-draft.wasm';b=read(module.with_suffix('.build.json'))
assert sha(module)==b['sha256']=='f9c2f3f998b8c8be47c68eb2f221dac714709d2f8ee132a181ae2b5b320663d3'
assert module.stat().st_size==921911 and b['source_hashes']==prior['source_hashes']
for name,digest in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==digest,name
new=['walk-exit-floor','walk-rail-frame','walk-rail-update'];previous=read(p/'walk-air-flight-browser.json')['observed']['suites']
suites={name:read(p/('walk-rail-climb-checkpoint-'+name.replace('_','-')+'-result.json')) for name in [*[n.replace('-','_') for n in new],*previous]}
assert len(suites)==179
for name,result in suites.items():
 assert result['result']=='pass',name
 if name in previous:assert result==previous[name],name
routines={};coverage={}
for name,addresses in [('walk-exit-floor',{'0x528280':81}),('walk-rail-frame',{'0x441020':22,'0x441070':22,'0x441860':23,'0x441680':126,'0x441b80':153,'0x442280':236,'0x4425b0':53})]:
 claimed=read(p/(name+'-routines.json'));assert set(claimed)==set(addresses);routines.update(claimed)
 original=read(p/(name+'-original.json'))
 for at,total in addresses.items():
  row=original['instruction_coverage'][at];assert row=={'covered':total,'total':total,'missing':[],'excluded':{}};coverage[at]=row
 extents=read(p/(name+'-extents.json'));assert extents['result']=='pass' and extents['routines_sha256']==sha(p/(name+'-routines.json')) and set(extents['checked'])==set(addresses)
assert len(routines)==8 and sum(x['total'] for x in coverage.values())==716
callbacks=words=padding=0
for name,cases,calls,expected_words,expected_padding in [('walk-exit-floor',75,150,0,0),('walk-rail-frame',250,668,96,0),('walk-rail-update',44,468,81,324)]:
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
assert (callbacks,words,padding)==(48,177,324)
original=read(p/'walk-rail-update-original.json');flows=[x for x in original['records'] if x['label'].startswith('common rail exit QB continue')]
assert len(flows)==8 and sum(x['completion_states']==[0] for x in flows)==6 and sum(x['completion_states']==[1] for x in flows)==2
assert sum(x['state']==0 for x in flows)==4 and sum(x['state']==4 for x in flows)==4
partial=original['partial_frame'];assert (partial['covered'],partial['total'],partial['completed_calls'],partial['recovered_routine'])==(133,142,400,False)
for name in prior['artifact_hashes']:
 if name.endswith('-routines.json'):
  old=read(r/name)
  if isinstance(old,dict):assert not set(routines).intersection(old),name
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
proof=read(p/'walk-rail-climb-browser.json');assert proof['observed']==candidate and proof['status'].startswith('PASS')
def fingerprint(value):
 canonical=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
 for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
 return {'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(value)}
assert proof['rendered_dom_fingerprint']==fingerprint(candidate)
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
paths={prior_path,p/'walk-air-flight-audit.json',p/'walk-animation-rail-draft.c',*p.glob('walk-rail-climb-checkpoint-*-result.json')}
for name in new:
 for suffix in ['-draft.c','-draft.wasm','-draft.build.json','-original.json','-fixtures.json','-memory.bin']:paths.add(p/(name+suffix))
 for prefix,suffix in [('build-','-draft.py'),('probe-','.py'),('verify-','-unit.mjs')]:paths.add(p/(prefix+name+suffix))
for name in ['walk-exit-floor','walk-rail-frame']:
 for suffix in ['-extents.py','-extents.json','-routines.json']:paths.add(p/(name+suffix))
for name in ['audit-walk-rail-climb.py','pin-walk-rail-climb.py','serve-walk-rail-climb.py','verify-walk-rail-climb-checkpoint.mjs','walk-rail-climb-browser.html','walk-rail-climb-browser.json','walk-rail-climb-worker.mjs']:paths.add(p/name)
for f in paths:
 assert f.is_file(),f
 artifacts[str(f.relative_to(r))]=sha(f)
 if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={**prior,'result':'original comparisons, Node and actual Chromium pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':8,'original_addresses':list(routines),
 'unpromoted_functions_in_this_module':843,'unpromoted_functions_across_separate_experiments':860,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'browser_suites':179,
 'new_cases':369,'new_calls_including_existing_dependencies':1286,'new_interrupted_calls':0,'instruction_coverage':coverage,
 'coverage_limit':'716/716 original instructions execute across eight complete routines, without exclusions or interrupted calls. The partial common loop executes133/142 instructions across400 frames and earns no routine count. No numeric allowances or checker changes.177 retained-probe word and324 existing network-padding byte comparisons use original-write provenance.',
 'scope':'Recover exit-floor query528280, rail exit callbacks441020/441070/441860, lower/upper exits441680/441b80, climbing442280 and rail frame4425b0. Connect rail and animation completion through a partial common loop.369 cases and1286 completed calls match in Node and Chromium, including48 real QB callbacks. Four no-floor continuation cases preserve the original rail re-entry. Hanging and playable training remain unfinished.',
 'unrecovered_lifecycle':'Ground, airborne, rail and animation paths now connect through a partial common Walk loop. Hanging440bf0 and full dispatcher recovery remain unfinished. Successful standard-wallplant callbacks still need connected-airborne-root validation. Animation checksum/forward dispatch419950/4198d0, original asset startup, renderer creation/rendering and playable training remain unfinished. Constructor277/463 and maintained frame prefix51/142 are unchanged.',
 'walk_rail_climb_evidence':{'completed_calls':1286,'interrupted_calls':0,'complete_helpers':8,'cases':369,'covered_instructions':716,'total_instructions':716,'qb_callbacks':48,'connected_exit_sequences':8,'ground_completions':6,'air_completions':2,'original_rail_reentries':4,'common_loop_calls':400,'common_loop_coverage':partial,'indeterminate_probe_word_comparisons':177,'indeterminate_padding_byte_comparisons':324,'new_numeric_allowances':0,'checker_changes':0,'unreachable_exclusions':{}},
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':fingerprint(candidate),'playable':False}
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
