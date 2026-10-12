"""Preserve original QB camera startup integration and its complete browser proof."""
import csv,hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';read=lambda f:json.loads(f.read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
name='camera-composite-startup-v3';previous=p/'skater-camera-initialization-v3-checkpoint.json';prior=read(previous)
assert sha(previous)=='41cd70cef93e116511e3697e95393db311277a1cd5ef514ba5311a36f549e876'
audit=p/'skater-camera-initialization-v3-audit.json';assert read(audit)['result']=='pass' and read(audit)['checkpoint_sha256']==sha(previous)
target=p/(name+'-checkpoint.json');assert not target.exists()
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for n,h in prior[group].items():assert sha(r/n)==h,(group,n)
w=p/'camera-composite-startup-v2.wasm';b=read(w.with_suffix('.build.json'));assert sha(w)==b['sha256']
for n,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/n)==h,n
expected=read(p/(name+'-node-all.json'));proof=read(p/(name+'-browser-full.json'));old=read(p/'skater-camera-initialization-v3-browser-full.json')['observed']['suites']
assert len(expected['suites'])==207 and len(old)==206
assert proof['observed']==expected and proof['status'].startswith('PASS') and 'Chrome/154.' in proof['user_agent']
assert expected['wasm_sha256']==sha(w) and expected['wasm_bytes']==w.stat().st_size and expected['runtime_imports']==0
for n,v in old.items():assert expected['suites'][n]==v,n
assert all(v['result']=='pass' for v in expected['suites'].values())
canonical=json.dumps(expected,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert proof['rendered_dom_fingerprint']=={'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(expected)}
original=read(p/(name+'-original.json'));unit=expected['suites']['camera_composite_startup_v3'];fixture=read(p/(name+'-fixtures.json'));routines=read(p/(name+'-routines.json'))
assert original['cases']==unit['cases']==72 and original['calls']==unit['calls']==108 and original['counts']==unit['counts']
assert unit['nan_fields_classification_only']==0 and unit['startup_diagnostic_callbacks']==0 and not fixture['float_fields']
assert set(routines)=={'0x41b7f0'} and routines['0x41b7f0']['bytes']==24 and routines['0x41b7f0']['instructions']==8
assert original['instruction_coverage']['0x41b7f0']=={'covered':8,'total':8,'missing':[],'excluded':{}}
assert set(unit['counts'])=={'thug_generic_camera_initialize_priority_v1','thug_composite_create_draft','thug_composite_create_from_array_draft'} and set(unit['counts'].values())=={36}
selected={int(row['address'],16) for row in read(r/'progress/ledger.json')['records']};assert 0x41b7f0 not in selected and {0x45f330,0x45f3a0}<=selected
extra=p/'camera-composite-startup-v1-ranges.tsv';rows=list(csv.DictReader(extra.open(),delimiter='\t'));assert rows==[{'address':'0041b7f0','body_bytes':'24','ranges':'0041b7f0:0041b807'}]
assert 0x41b7f0 not in {int(row['address'],16) for row in csv.DictReader((r/'progress/function-inventory.tsv').open(),delimiter='\t')}
integration=read(p/(name+'-integration.json'));assert len(integration['records'])==36 and integration['no_game_callee_substitution'] and integration['full_create_from_array_root_replayed'] and not integration['playable']
asset=r/integration['descriptor_asset']['path'];assert sha(asset)==integration['descriptor_asset']['sha256']
for case in fixture['cases']:
 for step in case['steps']:assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','quiet_double_fields','global_quiet_float_indices','global_bit_masks','float_fields','global_float_indices','indeterminate_words','indeterminate_bytes','compression_records'])
baseline=p/(name+'-reporting-baseline-report.json');behavior=p/(name+'-reporting-baseline-behavioral.json');assert not baseline.exists() and not behavior.exists()
baseline.write_bytes((r/'progress/report.json').read_bytes());behavior.write_bytes((r/'progress/behavioral-recovery.json').read_bytes())
assert int(read(baseline)['measures']['complete_code'])==0 and int(read(baseline)['measures']['matched_code'])==406
paths={previous,audit,baseline,behavior,asset}
for pattern in ['camera-composite-startup-v*','camera-composite-factories-v*','camera-composite-camera-v*','build-camera-composite-startup-v*','probe-camera-composite-startup-v*','verify-camera-composite-startup-v*','serve-camera-composite-startup-v*','pin-camera-composite-startup-v*','audit-camera-composite-startup-v*']:
 paths.update(f for f in p.glob(pattern) if f.is_file())
paths.update(f for f in r.glob('local/build/camera-composite-startup-v*.log') if f.is_file())
paths.update(f for f in (p/'camera-composite-startup-v1-ghidra').rglob('*') if f.is_file())
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
for f in paths:
 artifacts[str(f.relative_to(r))]=sha(f)
 if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
for suffix in ['-routines.json','-original.json','-fixtures.json','-browser-full.json','-node-all.json','-integration.json','-regression-'+name+'-result.json']:
 assert str((p/(name+suffix)).relative_to(r)) in artifacts,suffix
row=routines['0x41b7f0'];addresses={'0x41b7f0':{**row,'body_bytes':24,'ranges':rows[0]['ranges'],'original_evidence':name+'-original.json','node_evidence':name+'-regression-'+name+'-result.json','browser_suite':'camera_composite_startup_v3'}}
c={'schema':3,'result':'original comparisons, Node and actual Chromium pass; unpromoted','specimen_sha256':prior['specimen_sha256'],'prior_checkpoint':str(previous.relative_to(r)),'prior_checkpoint_sha256':sha(previous),'prior_engine_checkpoint':str(previous.relative_to(r)),'prior_engine_checkpoint_sha256':sha(previous),'wasm':str(w.relative_to(r)),'wasm_sha256':sha(w),'wasm_bytes':w.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],'source_hashes':b['source_hashes'],'draft_source_hashes':b['draft_source_hashes'],'derived_from':b['derived_from'],'platform_source_hashes':prior['platform_source_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),'browser_suites':207,'preserved_browser_suites':206,'browser_dom_fingerprint':proof['rendered_dom_fingerprint'],'new_functions':1,'verified_mappings':1,'tested_direct_exports':3,'original_addresses':addresses,'reused_integration_roots':['0x45f330','0x45f3a0'],'selection_policy':'One new generic Camera initialization contributes24 original bytes. Previously verified shared creation and create-from-array roots are replayed with the five actual QB camera descriptors and earn zero repeated bytes. The new extent is private-export verified; denominator unchanged. Derived lifecycle tables exercise only startup initialize/finalize/moved slots, not unknown frame/command/disposal methods.','new_complete_body_bytes':24,'new_verified_linear_bytes':24,'new_cases':72,'new_completed_calls':108,'original_covered_instructions':8,'original_linear_instructions':8,'public_report_at_verification':{'path':str(baseline.relative_to(r)),'sha256':sha(baseline)},'behavioral_report_at_verification':{'path':str(behavior.relative_to(r)),'sha256':sha(behavior)},'unsupported_routes':['Full profile initialization581850, Animation419dd0/480410/47f260 dependencies, full SkaterCamera frame4fa860, camera commands/disposal/reset integration, gameplay controls and original rendering integration remain unfinished.'],'scope':original['scope']+' All207 Node/actualChromium suites pass and all206 predecessor result objects remain unchanged. One new address24bytes/8instructions;36full original camera assembly cases. Failed first table pointer conversion, test priority offset and missing factory-relocation fixtures remain private and unselected. No checker/numeric changes.','publishing':prior['publishing'],'playable':False}
target.write_text(json.dumps(c,indent=2)+'\n');print('Pinned',len(artifacts),'artifacts;207 suites;1 new address/24bytes;',sha(target))
