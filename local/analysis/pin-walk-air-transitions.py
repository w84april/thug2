"""Pin landing, wallplant qualification and the immediate airborne ledge catch."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
prior_path=p/'walk-air-motion-checkpoint.json';assert sha(prior_path)=='dfb62b373d0397a7fd2f57d4d2c47b0d0a9a662f6c9c88d3a79e7831577dcb90'
prior=read(prior_path);target=p/'walk-air-transitions-checkpoint.json';assert not target.exists()
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
module=p/'walk-air-ledge-draft.wasm';b=read(module.with_suffix('.build.json'))
assert sha(module)==b['sha256']=='35d9794aaf13eaa689d02258ca15dfbca0f49aef98a9117724aedd960bf5766f'
assert module.stat().st_size==909721 and b['source_hashes']==prior['source_hashes']
for name,digest in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==digest,name
new=['walk-air-landing','walk-air-wallplant','walk-air-ledge'];previous=read(p/'walk-air-motion-browser.json')['observed']['suites']
suites={name:read(p/('walk-air-transitions-checkpoint-'+name.replace('_','-')+'-result.json')) for name in [*[n.replace('-','_') for n in new],*previous]}
assert len(suites)==171
for name,result in suites.items():
 assert result['result']=='pass',name
 if name in previous:assert result==previous[name],name
routines={};coverage={};cache_records=0;callback_count=0
for name,address,cases,calls,covered,total in [('walk-air-landing','0x52a700',78,146,269,275),('walk-air-wallplant','0x526e00',110,116,155,163),('walk-air-ledge','0x43f030',86,120,235,236)]:
 claimed=read(p/(name+'-routines.json'));assert set(claimed)=={address};routines.update(claimed)
 original=read(p/(name+'-original.json'));fixture=read(p/(name+'-fixtures.json'));unit=suites[name.replace('-','_')]
 assert original['cases']==unit['cases']==cases and original['calls']==unit['calls']==calls and original['counts']==unit['counts']
 assert unit['nan_fields_classification_only']==0 and not fixture['float_fields']
 assert unit.get('indeterminate_byte_comparisons',0)==0
 assert unit.get('indeterminate_word_comparisons',0)==(75 if name=='walk-air-landing' else 0)
 row=original['instruction_coverage'][address];assert (row['covered'],row['total'])==(covered,total) and not row['excluded'] and len(row['missing'])==total-covered;coverage[address]=row
 extents=read(p/(name+'-extents.json'));assert extents['result']=='pass' and extents['routines_sha256']==sha(p/(name+'-routines.json')) and set(extents['checked'])=={address}
 for case in fixture['cases']:
  for step in case['steps']:
   assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','quiet_double_fields','global_quiet_float_indices','global_bit_masks','float_fields','global_float_indices','indeterminate_bytes','compression_records'])
   if name!='walk-air-landing':assert not step.get('indeterminate_words')
   cache_records+=len(step.get('stack_objects',[]));callback_count+=step.get('callbacks',0)
 if name=='walk-air-ledge':assert fixture['cache_capture']=='destructor-v1'
assert cache_records==114 and callback_count==108
wall=read(p/'walk-air-wallplant-original.json');assert wall['zeroed_packet_padding_entries']==0 and wall['qb_calls']=={'0x7243098f':62}
assert all(a==[0,1,0] for a in wall['wallplant_args']) and all(q['moving']==q['farthest']==0 for q in wall['query_inputs'])
for name in prior['artifact_hashes']:
 if name.endswith('-routines.json'):
  old=read(r/name)
  if isinstance(old,dict):assert not set(routines).intersection(old),name
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
proof=read(p/'walk-air-transitions-browser.json');assert proof['observed']==candidate and proof['status'].startswith('PASS')
def fingerprint(value):
 canonical=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
 for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
 return {'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(value)}
assert proof['rendered_dom_fingerprint']==fingerprint(candidate)
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
paths={prior_path,p/'walk-air-motion-audit.json',*p.glob('walk-air-transitions-checkpoint-*-result.json')}
for name in new:
 for suffix in ['-draft.c','-draft.wasm','-draft.build.json','-original.json','-fixtures.json','-memory.bin','-extents.py','-extents.json','-routines.json']:paths.add(p/(name+suffix))
 for prefix,suffix in [('build-','-draft.py'),('probe-','.py'),('verify-','-unit.mjs')]:paths.add(p/(prefix+name+suffix))
for name in ['audit-walk-air-transitions.py','pin-walk-air-transitions.py','serve-walk-air-transitions.py','verify-walk-air-transitions-checkpoint.mjs','walk-air-transitions-browser.html','walk-air-transitions-browser.json','walk-air-transitions-worker.mjs']:paths.add(p/name)
for f in paths:
 assert f.is_file(),f
 artifacts[str(f.relative_to(r))]=sha(f)
 if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={**prior,'result':'original comparisons, Node and actual Chromium pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':3,'original_addresses':list(routines),
 'unpromoted_functions_in_this_module':828,'unpromoted_functions_across_separate_experiments':845,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'browser_suites':171,
 'new_cases':274,'new_calls_including_existing_dependencies':382,'new_interrupted_calls':0,'instruction_coverage':coverage,
 'coverage_limit':'659/674 original instructions execute with no exclusions or interrupted calls. The fifteen unexercised instructions are six landing reference-release instructions, eight wallplant miss/reference-release instructions and one ledge alignment instruction. All stay in the denominator. No numeric or padding-byte allowances are added. Landing has75 comparisons of original-write-proven indeterminate probe words using the unchanged checker.114 ledge collision caches compare at destruction.108 real QB callbacks execute:10 collision landing,62 synchronous wallplant and36 rail ledge callbacks. Full airborne frames remain unfinished.',
 'scope':'Three complete airborne transition helpers recover swept landing/sliding52a700, wallplant qualification and synchronous script526e00, and fixed/moving ledge catch43f030.274 cases and382 completed original calls match in Node and Chromium, exercising659/674 instructions with no exclusions. The game is not playable.',
 'unrecovered_lifecycle':'Ground and animation partial Walk updates remain preserved. Airborne landing, wallplant qualification and ledge entry are recovered, but contact jump5293f0 including529160, rail entry442170 including57da20, and full52cef0 integration remain unfinished. Hanging440bf0, rail4425b0, full dispatcher recovery, animation checksum/forward dispatch419950/4198d0, original asset startup, renderer creation/rendering and playable training also remain unfinished. Constructor277/463 and maintained frame prefix51/142 are unchanged.',
 'walk_air_transitions_evidence':{'completed_calls':382,'interrupted_calls':0,'complete_helpers':3,'cases':274,'covered_instructions':659,'total_instructions':674,'live_cache_observations':114,'landing_callbacks':10,'wallplant_callbacks':62,'ledge_callbacks':36,'indeterminate_probe_word_comparisons':75,'new_numeric_allowances':0,'new_padding_allowances':0,'unreachable_exclusions':{}},
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':fingerprint(candidate),'playable':False}
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
