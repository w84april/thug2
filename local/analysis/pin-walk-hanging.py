"""Pin hanging and the complete five-state walking dispatcher."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
prior_path=p/'walk-rail-climb-checkpoint.json';assert sha(prior_path)=='aa72d533a4297c153aa93c1e209bf898de33f55bc288b98cf58e460e873a026d'
prior=read(prior_path);target=p/'walk-hanging-checkpoint.json';assert not target.exists()
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
module=p/'walk-complete-update-draft.wasm';b=read(module.with_suffix('.build.json'))
assert sha(module)==b['sha256']=='87828a7feef8fe6d8a26fb4a2b8659a6b872e64dfbbd1f630407dcbd780197f7'
assert module.stat().st_size==929951 and b['source_hashes']==prior['source_hashes']
for name,digest in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==digest,name
new=['walk-hang-pose','walk-hang-motion','walk-hang-exit','walk-hang-frame','walk-complete-update'];previous=read(p/'walk-rail-climb-browser.json')['observed']['suites']
suites={name:read(p/('walk-hanging-checkpoint-'+name.replace('_','-')+'-result.json')) for name in [*[n.replace('-','_') for n in new],*previous]}
assert len(suites)==184
for name,result in suites.items():
 assert result['result']=='pass',name
 if name in previous:assert result==previous[name],name
routines={};coverage={}
for name,addresses in [('walk-hang-pose',{'0x43da20':(20,20),'0x43fc70':(132,132)}),('walk-hang-motion',{'0x5250a0':(14,14),'0x43dfc0':(180,180),'0x440130':(358,358)}),('walk-hang-exit',{'0x43db00':(32,32),'0x43db90':(29,29),'0x43e530':(399,411)}),('walk-hang-frame',{'0x440bf0':(294,297)}),('walk-complete-update',{'0x52d4b0':(142,142)})]:
 claimed=read(p/(name+'-routines.json'));assert set(claimed)==set(addresses);routines.update(claimed)
 original=read(p/(name+'-original.json'))
 for at,(covered,total) in addresses.items():
  row=original['instruction_coverage'][at];assert row['covered']==covered and row['total']==total and not row['excluded'] and len(row['missing'])==total-covered;coverage[at]=row
 extents=read(p/(name+'-extents.json'));assert extents['result']=='pass' and extents['routines_sha256']==sha(p/(name+'-routines.json')) and set(extents['checked'])==set(addresses)
assert len(routines)==10 and sum(x['total'] for x in coverage.values())==1615 and sum(x['covered'] for x in coverage.values())==1600
callbacks=words=padding=0
for name,cases,calls,expected_words,expected_padding in [('walk-hang-pose',153,225,0,0),('walk-hang-motion',308,452,0,0),('walk-hang-exit',92,272,117,0),('walk-hang-frame',252,680,68,0),('walk-complete-update',83,498,118,510)]:
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
assert (callbacks,words,padding)==(38,303,510)
original=read(p/'walk-complete-update-original.json');flows=[x for x in original['records'] if x['label'].startswith('hang exit continued')]
assert len(flows)==16 and sum(x['completion_states']==[0] for x in flows)==4 and sum(x['completion_states']==[1] for x in flows)==4
assert sum(len(x['frames']) for x in original['records'])==original['completed_frames']==391
assert {f['state'] for x in original['records'] for f in x['frames']}=={0,1,2,3,4,5,0xffffffff}
for name in prior['artifact_hashes']:
 if name.endswith('-routines.json'):
  old=read(r/name)
  if isinstance(old,dict):assert not set(routines).intersection(old),name
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
proof=read(p/'walk-hanging-browser.json');assert proof['observed']==candidate and proof['status'].startswith('PASS')
def fingerprint(value):
 canonical=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
 for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
 return {'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(value)}
assert proof['rendered_dom_fingerprint']==fingerprint(candidate)
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
paths={prior_path,p/'walk-rail-climb-audit.json',p/'walk-animation-hang-draft.c',*p.glob('walk-hanging-checkpoint-*-result.json')}
for name in new:
 for suffix in ['-draft.c','-draft.wasm','-draft.build.json','-original.json','-fixtures.json','-memory.bin']:paths.add(p/(name+suffix))
 for prefix,suffix in [('build-','-draft.py'),('probe-','.py'),('verify-','-unit.mjs')]:paths.add(p/(prefix+name+suffix))
for name in new:
 for suffix in ['-extents.py','-extents.json','-routines.json']:paths.add(p/(name+suffix))
for name in ['audit-walk-hanging.py','pin-walk-hanging.py','serve-walk-hanging.py','verify-walk-hanging-checkpoint.mjs','walk-hanging-browser.html','walk-hanging-browser.json','walk-hanging-worker.mjs']:paths.add(p/name)
for f in paths:
 assert f.is_file(),f
 artifacts[str(f.relative_to(r))]=sha(f)
 if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={**prior,'result':'original comparisons, Node and actual Chromium pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':10,'original_addresses':list(routines),
 'unpromoted_functions_in_this_module':853,'unpromoted_functions_across_separate_experiments':870,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'browser_suites':184,
 'new_cases':888,'new_calls_including_existing_dependencies':2127,'new_interrupted_calls':0,'instruction_coverage':coverage,
 'coverage_limit':'1600/1615 original instructions execute across ten complete routines, without exclusions or interrupted calls. All 142 dispatcher instructions execute across 391 completed frames. The 15 unexercised instructions remain included: moving-reference cleanup branches and the contact-update failure branch. No numeric allowances or checker changes. 303 retained-probe word and 510 existing network-padding byte comparisons use original-write provenance.',
 'scope':'Recover hanging input 43da20, pose 43fc70, orientation reset 5250a0, corner 43dfc0, sideways movement 440130, climb 43e530, completion callbacks 43db00/43db90, full hanging frame 440bf0 and full walking dispatcher 52d4b0. 888 cases and 2127 completed calls match in Node and Chromium, including 38 real QB callbacks. All five states and out-of-range fallthrough execute through the full dispatcher. Full engine startup, rendering and playable training remain unfinished.',
 'unrecovered_lifecycle':'The complete five-state walking dispatcher is now separately recovered and validated, including hanging and connected animation completion. Startup component wiring still uses the preserved partial entry. Successful standard-wallplant callbacks need connected-airborne-root validation. Animation checksum/forward dispatch 419950/4198d0, original asset startup, renderer creation/rendering and playable training remain unfinished. Constructor 277/463 and the preserved experimental frame prefix 51/142 are unchanged.',
 'walk_complete_evidence':{'completed_calls':2127,'interrupted_calls':0,'complete_routines':10,'cases':888,'covered_instructions':1600,'total_instructions':1615,'qb_callbacks':38,'connected_hang_exit_sequences':16,'ground_climb_completions':4,'air_climb_completions':4,'common_loop_calls':391,'common_loop_coverage':coverage['0x52d4b0'],'indeterminate_probe_word_comparisons':303,'indeterminate_padding_byte_comparisons':510,'new_numeric_allowances':0,'checker_changes':0,'unreachable_exclusions':{}},
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':fingerprint(candidate),'playable':False}
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
