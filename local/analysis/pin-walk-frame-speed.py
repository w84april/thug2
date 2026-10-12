"""Pin the complete speed parent and completed animation-state Walk frames."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
prior_path=p/'walk-speed-checkpoint.json';assert sha(prior_path)=='f89d239a7dec68640c89ba0870d149859f560a1292ca7b5b74f1114782835fb8'
prior=read(prior_path);target=p/'walk-frame-speed-checkpoint.json';assert not target.exists()
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
b=read(p/'walk-frame-speed-draft.build.json');module=p/'walk-frame-speed-draft.wasm'
assert sha(module)==b['sha256']=='9f5913135c9d464643c9daf8b20a4292d348c65bc1c8a93a83b47c3956fefc54'
assert module.stat().st_size==900195 and b['source_hashes']==prior['source_hashes']
for name,digest in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==digest,name
previous=read(p/'walk-speed-browser.json')['observed']['suites']
suites={name:read(p/('walk-frame-speed-checkpoint-'+name.replace('_','-')+'-result.json')) for name in ['walk_frame_speed','walk_frame_speed_flow',*previous]}
assert len(suites)==161
for name,result in suites.items():
 assert result['result']=='pass',name
 if name in previous:assert result==previous[name],name
routines=read(p/'walk-frame-speed-routines.json');assert set(routines)=={'0x52a2c0'}
messages=0
for name,cases,calls,allowances in [('walk-frame-speed',189,308,114),('walk-frame-speed-flow',48,336,348)]:
 original=read(p/(name+'-original.json'));fixture=read(p/(name+'-fixtures.json'));unit=suites[name.replace('-','_')];coverage=original['instruction_coverage']
 assert set(coverage)==set(routines) and (coverage['0x52a2c0']['covered'],coverage['0x52a2c0']['total'])==(211,216)
 assert not coverage['0x52a2c0']['excluded']
 assert original['cases']==unit['cases']==cases and original['calls']==unit['calls']==calls and original['counts']==unit['counts']
 assert unit['nan_fields_classification_only']==unit['indeterminate_word_comparisons']==0 and not fixture['float_fields']
 assert unit['indeterminate_byte_comparisons']==allowances
 messages+=original['heap_events']['0x5bb0e0']
 for row in original['flow_records']:
  assert all(c['return']==2 for c in row['commands'])
 for case in fixture['cases']:
  for step in case['steps']:
   assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','quiet_double_fields','global_quiet_float_indices','global_bit_masks','float_fields','global_float_indices','indeterminate_words','compression_records'])
   assert len(step['indeterminate_bytes'])==len(step['payload_provenance'])
   for row in step['payload_provenance']:
    assert row['copy_instruction']=='0x45500e' and row['source_writes_before_copy']==0 and row['source_offset'] in [5,6,7]
    assert row['defined_prefix_writes']==[1]*5 and row['destination']==row['payload']+row['source_offset']
assert messages==33
flow=read(p/'walk-frame-speed-flow-original.json');frame=flow['partial_frame']
assert (frame['covered'],frame['total'],frame['completed_calls'],frame['completed_state'],frame['recovered_routine'])==(114,142,168,4,False)
assert len(flow['flow_records'])==48 and sum(x['frames'] for x in flow['flow_records'])==168
assert sum(len(x['speed_calls']) for x in flow['flow_records'])==132
negative=read(p/'walk-frame-speed-padding-checks.json');assert negative['result']=='pass' and negative['checks']==12
for name,digest in negative['files'].items():assert sha(p/name)==digest,name
boundaries=read(p/'walk-frame-speed-boundaries.json');assert boundaries['result']=='pass' and boundaries['cases']==boundaries['calls']==96
assert boundaries['counts']=={'thug_walk_update_animation_prefix_draft':96}
extents=read(p/'walk-frame-speed-extents.json');assert extents['result']=='pass' and extents['routines_sha256']==sha(p/'walk-frame-speed-routines.json') and set(extents['checked'])==set(routines)
assert not extents['partial_frame']['recovered_routine'] and extents['partial_frame']['instructions']==142
for name in prior['artifact_hashes']:
 if name.endswith('-routines.json'):
  old=read(r/name)
  if isinstance(old,dict):assert not set(routines).intersection(old),name
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
proof=read(p/'walk-frame-speed-browser.json');assert proof['observed']==candidate and proof['status'].startswith('PASS')
def fingerprint(value):
 canonical=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
 for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
 return {'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(value)}
assert proof['rendered_dom_fingerprint']==fingerprint(candidate)
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
paths=set(p.glob('walk-frame-speed-*'))|{prior_path,p/'walk-speed-audit.json'}
paths.update(p/name for name in ['audit-walk-frame-speed.py','build-walk-frame-speed-draft.py','pin-walk-frame-speed.py','probe-walk-frame-speed.py','probe-walk-frame-speed-flow.py','serve-walk-frame-speed.py','verify-walk-frame-speed-unit.mjs','verify-walk-frame-speed-checkpoint.mjs','check-walk-frame-speed-padding.mjs','check-walk-frame-boundaries.mjs'])
for f in paths:
 if f.is_file() and f.suffix!='.log' and f!=target and not f.name.endswith('-next.txt') and f!=p/'walk-frame-speed-audit.json':
  artifacts[str(f.relative_to(r))]=sha(f)
  if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={**prior,'result':'original comparisons, Node and actual Chromium pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':1,'original_addresses':list(routines),
 'unpromoted_functions_in_this_module':819,'unpromoted_functions_across_separate_experiments':836,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'browser_suites':161,
 'new_cases':237,'new_calls_including_existing_dependencies':644,'new_interrupted_calls':0,'instruction_coverage':coverage,
 'coverage_limit':'Parent52a2c0 exercises211/216 instructions with no exclusions. Two platform heap-init call instructions and three allocation-failure branches remain unexercised; successful allocation and finite nonzero required parameter spans are fixture contracts. Partial52d4b0 exercises114/142 instructions and completes168 animation-state4 frames; the whole dispatcher and419950 prefix earn no routine count. Defined arena, globals, registers, queue links and payload bytes compare. Original-write-proven three-byte message padding receives462 byte-specific comparisons, guarded by12 controls. No numeric allowances. A separate Node-only corpus checks96 unfinished-state trap boundaries; it is not part of644 completed calls or161 browser suites.',
 'scope':flow['scope'],
 'unrecovered_lifecycle':'Walking animation-speed parent52a2c0 is recovered, and168 original animation-state4 updates of52d4b0 now complete through input, collision, pose/events, speed and camera. Focus input is unpressed in these integrated frames; callback-driven event mutations are not exercised. Animation checksum/forward dispatch419950/4198d0 remain incomplete, with the original fixed bd4edd44 command returning2. Shared Walk transfer527600, ground/shadow validation527080, full state dispatch, airborne/hanging/rail updates, original asset startup, renderer creation/rendering and playable training remain unfinished. The preserved maintained frame prefix is51/142; this new partial candidate is114/142. Constructor277/463 remains unchanged.',
 'walk_frame_speed_evidence':{'completed_calls':644,'interrupted_calls':0,'parent_root_calls':308,'time_advances':168,'completed_animation_frames':168,'connected_sequences':48,'full_tail_frames':132,'cancelled_frames':36,'partial_frame':frame,'queued_messages':33,'indeterminate_byte_comparisons':462,'padding_controls':12,'unfinished_state_boundaries':96,'new_numeric_allowances':0,'unreachable_exclusions':{}},
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':fingerprint(candidate),'playable':False}
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
