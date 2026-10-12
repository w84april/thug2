"""Pin real component-loop walking integration without adding a routine count."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
prior_path=p/'walk-hanging-checkpoint.json';assert sha(prior_path)=='aeda970143005615d9535b63ff0cedc1419a278123f89b2455b5f81b5fe1ac12'
prior=read(prior_path);target=p/'walk-component-checkpoint.json';assert not target.exists()
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
module=p/'walk-component-frame-draft.wasm';b=read(module.with_suffix('.build.json'))
assert sha(module)==b['sha256']=='fed3cfeec857796461242a0264c5b7664b1903cfd9b29b7d8db0da020d630655'
assert module.stat().st_size==929951 and b['source_hashes']==prior['source_hashes']
for name,digest in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==digest,name
old=p/'walk-animation-component-derived.c';source=p/'walk-component-frame-draft.c'
expected=old.read_text().replace('/* Original Walk lifecycle and common movement-frame setup. State handlers remain pending. */','/* Walk lifecycle wired to the recovered complete movement dispatcher. */').replace('const ThugComponentMethods thug_walk_pending_methods_draft={','extern void thug_walk_update_draft(void *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);\nconst ThugComponentMethods thug_walk_pending_methods_draft={').replace('.update=thug_walk_update_prefix_draft,','.update=thug_walk_update_draft,')
assert source.read_text()==expected
previous=read(p/'walk-hanging-browser.json')['observed']['suites']
suites={name:read(p/('walk-component-checkpoint-'+name.replace('_','-')+'-result.json')) for name in ['walk_component_frame',*previous]}
assert len(suites)==185
for name,result in suites.items():
 assert result['result']=='pass',name
 if name in previous:assert result==previous[name],name
original=read(p/'walk-component-frame-original.json');fixture=read(p/'walk-component-frame-fixtures.json');unit=suites['walk_component_frame']
assert unit==read(p/'walk-component-frame-unit.json')
assert original['cases']==unit['cases']==168 and original['calls']==unit['calls']==797 and original['counts']==unit['counts']
assert unit['counts']['thug_object_update_components']==571
assert not fixture['float_fields'] and unit['nan_fields_classification_only']==0
callbacks=words=padding=0
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
  callbacks+=step.get('callbacks',0);words+=len(w);padding+=len(pad)
assert (callbacks,words,padding)==(27,283,762)
assert (unit['virtual_wait_callbacks'],unit['indeterminate_word_comparisons'],unit['indeterminate_byte_comparisons'])==(callbacks,words,padding)
coverage=original['instruction_coverage'];assert coverage=={'0x45d920':{'covered':41,'total':41,'missing':[],'excluded':{}},'0x52d4b0':{'covered':142,'total':142,'missing':[],'excluded':{}}}
records=original['records'];assert original['completed_component_frames']==sum(len(x['frames']) for x in records)==492
assert all(len(x['frames'])==len(x['virtual_calls']) for x in records)
assert all(c['vtable']==0x64c75c and c['caller_return']==0x45d96c for x in records for c in x['virtual_calls'])
assert len({c['component'] for x in records for c in x['virtual_calls']})==1
flows=[x for x in records if x['label'].startswith('owner loop exit continuation')];assert len(flows)==16
assert sum(x['completion_states']==[0] for x in flows)==4 and sum(x['completion_states']==[1] for x in flows)==4
lifecycle=[x for x in records if x['label'].startswith('construct bind update state')];assert len(lifecycle)==5 and all(len(x['frames'])==4 for x in lifecycle)
assert len([x for x in records if x['label'].startswith('nested collision QB')])==8
assert len([x for x in records if x['label'].startswith('pre-frame QB')])==7
negative=read(p/'walk-component-negative.json');assert negative['result']=='pass' and negative['rejection']=='RuntimeError: unreachable' and negative['tested_cases']==1
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
proof=read(p/'walk-component-browser.json');assert proof['observed']==candidate and proof['status'].startswith('PASS')
def fingerprint(value):
 canonical=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
 for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
 return {'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(value)}
assert proof['rendered_dom_fingerprint']==fingerprint(candidate)
paths={prior_path,p/'walk-hanging-audit.json',*p.glob('walk-component-checkpoint-*-result.json')}
for suffix in ['-draft.c','-draft.wasm','-draft.build.json','-original.json','-fixtures.json','-memory.bin','-unit.json']:paths.add(p/('walk-component-frame'+suffix))
for name in ['build-walk-component-frame-draft.py','probe-walk-component-frame.py','verify-walk-component-frame-unit.mjs','verify-walk-component-negative.mjs','walk-component-negative.json','pin-walk-component.py','audit-walk-component.py','serve-walk-component.py','verify-walk-component-checkpoint.mjs','walk-component-browser.html','walk-component-browser.json','walk-component-worker.mjs']:paths.add(p/name)
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
for f in paths:
 assert f.is_file(),f
 artifacts[str(f.relative_to(r))]=sha(f)
 if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={**prior,'result':'original comparisons, Node and actual Chromium pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':0,'original_addresses':[],
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'browser_suites':185,'new_cases':168,'new_calls_including_existing_dependencies':797,'new_interrupted_calls':0,'instruction_coverage':coverage,
 'coverage_limit':'All 41 existing object-loop instructions and all 142 existing walking-dispatcher instructions execute. This integration adds no routine count. 571 object update calls execute 492 walking frames; suspension and deletion gates account for skipped frames. No numeric allowances or checker changes. 283 retained-probe word and 762 existing network-padding byte comparisons retain original-write provenance.',
 'scope':'Wire the Walk component update slot to the complete recovered dispatcher. All 168 cases and 797 original calls match in Node and Chromium, including 27 actual QB callbacks and eight climb completions inside the owner update loop. Constructor, attachment, initialization and binding precede frames in five state cases. Other component frames remain suspended in these fixtures. Full skater startup, rendering and playable training remain unfinished.',
 'unrecovered_lifecycle':'The experimental Walk vtable now uses the complete dispatcher and passes original component-loop and lifecycle comparisons. Full skater construction remains 277/463, stopping before SkaterLocalNetLogic (type 7cd3e6d5, factory 513630); other component frame updates need connection. Successful standard-wallplant callbacks need connected-airborne-root validation. Animation checksum/forward dispatch 419950/4198d0, original asset startup, renderer creation/rendering and playable training remain unfinished.',
 'walk_component_evidence':{'cases':168,'completed_calls':797,'interrupted_calls':0,'object_loop_calls':571,'walking_frames':492,'qb_callbacks':27,'connected_hang_exit_sequences':16,'ground_climb_completions':4,'air_climb_completions':4,'constructed_bound_state_cases':5,'pre_frame_script_cases':7,'nested_collision_script_cases':8,'numeric_allowances':0,'checker_changes':0,'new_routine_count':0,'indeterminate_probe_word_comparisons':283,'indeterminate_padding_byte_comparisons':762,'prior_module_rejected':True,'other_component_frames':'suspended'},
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':fingerprint(candidate),'playable':False}
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
