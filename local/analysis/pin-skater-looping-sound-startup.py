"""Pin complete SkaterLoopingSound lifecycle and partial startup; preserve all predecessors."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';read=lambda f:json.loads(f.read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
previous=p/'skater-balance-startup-checkpoint.json';prior=read(previous);target=p/'skater-looping-sound-startup-checkpoint.json';assert not target.exists()
assert sha(previous)=='73a6d033ac53530c9ac59d34becc2333b105893121abb7e3a3ab53e9460e09ed'
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
w=p/'skater-looping-sound-startup-draft.wasm';b=read(w.with_suffix('.build.json'));assert sha(w)==b['sha256']=='a7162384658a3875b16c6726f8fb71ad3a4c2cb2f69210bb7221b0ee4f40367f'
for name,digest in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==digest,name
assert b['source_hashes']==prior['source_hashes']
expected=read(p/'skater-looping-sound-node-all.json');proof=read(p/'skater-looping-sound-browser.json');old=read(p/'skater-balance-browser.json')['observed']['suites'];suites=expected['suites']
assert expected['wasm_sha256']==sha(w) and expected['wasm_bytes']==w.stat().st_size and expected['runtime_imports']==0
assert len(suites)==193 and len(old)==191 and all(v['result']=='pass' for v in suites.values())
for name,value in old.items():assert suites[name]==value,name
assert proof['observed']==expected and proof['status'].startswith('PASS') and 'Chrome/154.' in proof['user_agent']
canonical=json.dumps(expected,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert proof['rendered_dom_fingerprint']=={'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(expected)}
original=read(p/'skater-looping-sound-lifecycle-original.json');unit=suites['skater_looping_sound_lifecycle'];fixture=read(p/'skater-looping-sound-lifecycle-fixtures.json');routines=read(p/'skater-looping-sound-lifecycle-routines.json');extents=read(p/'skater-looping-sound-lifecycle-extents.json')
assert original['cases']==unit['cases']==121 and original['calls']==unit['calls']==291 and original['counts']==unit['counts']
assert unit['audio_stop_callbacks']==42 and unit['nan_fields_classification_only']==0 and not fixture['float_fields']
assert extents['result']=='pass' and extents['routines_sha256']==sha(p/'skater-looping-sound-lifecycle-routines.json')
addresses={}
for at,row in routines.items():
 cov=original['instruction_coverage'][at];assert cov['covered']==cov['total']==row['instructions'] and not cov['missing'] and not cov['excluded']
 assert original['counts'][row['name']]>0
 addresses[at]={**row,'original_evidence':'skater-looping-sound-lifecycle-original.json','node_evidence':'skater-looping-sound-lifecycle-looping-sound-candidate-unit.json','browser_suite':'skater_looping_sound_lifecycle'}
assert len(addresses)==8 and sum(x['bytes'] for x in addresses.values())==549 and sum(x['total'] for x in original['instruction_coverage'].values())==156
for case in fixture['cases']:
 for step in case['steps']:assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','quiet_double_fields','global_quiet_float_indices','global_bit_masks','float_fields','global_float_indices','indeterminate_words','indeterminate_bytes','compression_records'])
partial=read(p/'skater-looping-sound-startup-original.json')['partial_constructor'];assert (partial['covered'],partial['total'],partial['interrupted_calls'],partial['counted_complete'])==(309,463,32,False)
assert all(row['next_type']==('0x1859f772' if row['arguments'][2]&255 else '0x850eef66') for row in partial['records'])
negative=read(p/'skater-looping-sound-lifecycle-negative.json');assert negative['result']=='pass' and negative['clear_before_stop_rejected']
base_report=p/'looping-sound-reporting-baseline-report.json';assert not base_report.exists();base_report.write_bytes((r/'progress/report.json').read_bytes());assert sha(base_report)=='181d00495f3d737666e07d59fa4b40cd2c25c68d4f0975ed9171936988f31875'
paths={previous,p/'skater-balance-startup-audit.json',base_report,p/'looping-sound-stop-callback.c',p/'looping-sound-stop-callback.wasm'}
for pattern in ['skater-looping-sound*','skater-looping-sound-extra-*','sound-stop-*','looping-sound-stop*','build-skater-looping-sound*','probe-skater-looping-sound*','verify-skater-looping-sound*']:
 paths.update(f for f in p.glob(pattern) if f.is_file() and f.name not in ['skater-looping-sound-startup-pin.log','skater-looping-sound-startup-audit.log'])
for name in ['serve-skater-looping-sound.py','pin-skater-looping-sound-startup.py','audit-skater-looping-sound-startup.py']:paths.add(p/name)
for name in ['skater-base-descriptor','skater-local-net','skater-end-run-lifecycle','skater-end-run-startup','skater-balance-lifecycle','skater-balance-startup','skater-looping-sound-lifecycle','skater-looping-sound-startup']:paths.add(p/(name+'-looping-sound-candidate-unit.json'))
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
for f in paths:
 assert f.is_file(),f
 artifacts[str(f.relative_to(r))]=sha(f)
 if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
c={'schema':3,'result':'original comparisons, Node and actual Chromium pass; unpromoted','specimen_sha256':original['specimen_sha256'],'prior_checkpoint':str(previous.relative_to(r)),'prior_checkpoint_sha256':sha(previous),'wasm':str(w.relative_to(r)),'wasm_sha256':sha(w),'wasm_bytes':w.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],'source_hashes':b['source_hashes'],'draft_source_hashes':b['draft_source_hashes'],'platform_source_hashes':prior['platform_source_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),'browser_suites':193,'preserved_browser_suites':191,'browser_dom_fingerprint':proof['rendered_dom_fingerprint'],'new_functions':8,'original_addresses':addresses,'verified_scoped_addresses_from_prior':{**prior['verified_scoped_addresses_from_prior'],**prior['original_addresses']},'new_verified_linear_bytes':549,'instruction_coverage':original['instruction_coverage'],'new_cases':121,'new_completed_calls':291,'new_audio_stop_callbacks':42,'constructor_prefix':{'address':'0x582d90','covered':309,'total':463,'interrupted_calls':32,'next_local_type':'0x1859f772','next_remote_type':'0x850eef66','counted_complete':False},'unsupported_routes':prior['unsupported_routes']+['SkaterLoopingSound frame513bb0, command5139e0 and registration513860 remain unverified; later constructor components remain unfinished'],'public_report_at_verification':{'path':str(base_report.relative_to(r)),'sha256':sha(base_report)},'scope':'Eight complete original routines recover SkaterLoopingSound lifecycle and stop wrapper47b4e0. 121 cases/291 completed calls cover156/156 original instructions. 42 native Stop callbacks test owner/global mutation and clear-after-callback order; clear-before-callback control is rejected. All191 predecessor Node/Chromium results remain unchanged. Existing voice-find47ad80, slot-stop47c7a0 and volume-init47b030 receive zero additional credit. Constructor582d90 advances309/463 and remains partial with zero credit. Frame, command, global registration, actual audio device output, rendering and playable level remain unfinished','publishing':'Direct publication of verified source and metadata authorized; retired chat and its publishing automation remain paused. Original specimen, assets, raw fixtures and compiled game modules remain private.','playable':False}
target.write_text(json.dumps(c,indent=2)+'\n');print('Pinned SkaterLoopingSound:',len(artifacts),'artifacts;193 suites;8 verified routines;',sha(target))
