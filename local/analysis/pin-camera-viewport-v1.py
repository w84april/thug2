"""Pin three additional viewport routines, preserving camera and rendering evidence."""
import csv,hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';read=lambda f:json.loads(f.read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
previous=p/'training-webgl-v1-checkpoint.json';prior=read(previous)
assert sha(previous)=='79107e8f4a0734e54d7749331a05d9c7ed49c35a37423211dfe014448d98d4d8'
engine=p/'camera-startup-v2-checkpoint.json';semantic=read(engine)
assert sha(engine)=='63a639d3ea500f7009f9c0b692a9be15417d541cf2ad5b2ca5a5d00bb83c52f6'
target=p/'camera-viewport-v1-checkpoint.json';assert not target.exists()
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,h in prior[group].items():assert sha(r/name)==h,(group,name)
w=p/'camera-viewport-v1.wasm';b=read(w.with_suffix('.build.json'));assert sha(w)==b['sha256']
for name,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==h,name
expected=read(p/'camera-viewport-v1-node-all.json');proof=read(p/'camera-viewport-v1-browser.json');old=read(p/'camera-startup-v2-browser.json')['observed']['suites']
assert len(expected['suites'])==201 and len(old)==200
assert proof['observed']==expected and proof['status'].startswith('PASS') and 'Chrome/154.' in proof['user_agent']
assert expected['wasm_sha256']==sha(w) and expected['wasm_bytes']==w.stat().st_size and expected['runtime_imports']==0
for name,value in old.items():assert expected['suites'][name]==value,name
assert all(v['result']=='pass' for v in expected['suites'].values())
canonical=json.dumps(expected,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert proof['rendered_dom_fingerprint']=={'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(expected)}
name='camera-viewport-v1';original=read(p/(name+'-original.json'));unit=expected['suites']['camera_viewport_v1'];fixture=read(p/(name+'-fixtures.json'));routines=read(p/(name+'-routines.json'))
assert original['cases']==unit['cases']==75 and original['calls']==unit['calls']==344 and original['counts']==unit['counts']
assert unit['nan_fields_classification_only']==0 and unit['startup_diagnostic_callbacks']==0 and not fixture['float_fields']
inventory={int(row['address'],16):row for row in csv.DictReader((r/'progress/function-inventory.tsv').open(),delimiter='\t')}
addresses={};covered=total=body=0
for at,row in routines.items():
 inv=inventory[int(at,16)];assert row['bytes']==int(inv['body_bytes']);cov=original['instruction_coverage'][at]
 assert original['counts'][row['name']]>0 and cov['total']==row['instructions'] and not cov['missing'] and not cov['excluded']
 addresses[at]={**row,'body_bytes':int(inv['body_bytes']),'ranges':inv['ranges'],'original_evidence':name+'-original.json','node_evidence':name+'-regression-'+name+'-result.json','browser_suite':'camera_viewport_v1'}
 covered+=cov['covered'];total+=cov['total'];body+=int(inv['body_bytes'])
assert len(addresses)==3 and (covered,total,body)==(104,104,279)
for case in fixture['cases']:
 for step in case['steps']:assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','quiet_double_fields','global_quiet_float_indices','global_bit_masks','float_fields','global_float_indices','indeterminate_words','indeterminate_bytes','compression_records'])
baseline=p/'camera-viewport-v1-reporting-baseline-report.json';assert not baseline.exists();baseline.write_bytes((r/'progress/report.json').read_bytes())
assert sha(baseline)=='39712589a7b0b1f0b300316eefc9a895562621035bac416175f3828a8e8860c4'
paths={previous,p/'training-webgl-v1-audit.json',baseline}
for pattern in ['camera-viewport-v1*','build-camera-viewport-v1*','probe-camera-viewport-v1*','verify-camera-viewport-v1*','serve-camera-viewport-v1*','pin-camera-viewport-v1*','audit-camera-viewport-v1*','trace-skater-initialization-v4*','skater-initialization-v4-trace*']:
 paths.update(f for f in p.glob(pattern) if f.is_file())
paths.update(f for f in (p/'camera-viewport-v1-ghidra').rglob('*') if f.is_file())
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
for f in paths:
 artifacts[str(f.relative_to(r))]=sha(f)
 if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
c={'schema':3,'result':'original comparisons, Node and actual Chromium pass; unpromoted','specimen_sha256':prior['specimen_sha256'],'prior_checkpoint':str(previous.relative_to(r)),'prior_checkpoint_sha256':sha(previous),'prior_engine_checkpoint':str(engine.relative_to(r)),'prior_engine_checkpoint_sha256':sha(engine),'wasm':str(w.relative_to(r)),'wasm_sha256':sha(w),'wasm_bytes':w.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],'source_hashes':b['source_hashes'],'draft_source_hashes':b['draft_source_hashes'],'platform_source_hashes':prior['platform_source_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),'browser_suites':201,'preserved_browser_suites':200,'browser_dom_fingerprint':proof['rendered_dom_fingerprint'],'new_functions':3,'verified_mappings':3,'original_addresses':addresses,'verified_scoped_addresses_from_prior':{},'selection_policy':'Additional independent selection of three new viewport addresses only. Earlier camera and historical582d90 completion remain selected separately. Existing camera constructors, lookup, copy and intrusive reference callees receive no repeated credit. Rendering preview remains zero-credit.','new_complete_body_bytes':279,'new_verified_linear_bytes':279,'new_cases':75,'new_completed_calls':344,'original_covered_instructions':104,'original_linear_instructions':104,'public_report_at_verification':{'path':str(baseline.relative_to(r)),'sha256':sha(baseline)},'unsupported_routes':semantic['unsupported_routes']+['Full581850 profile startup, SkaterCamera reset, camera-specific QB initialization and commands remain unfinished; viewport candidate startup traces are discovery only'],'scope':original['scope']+' All201 Node/actualChromium suites pass and all200 predecessor result objects are unchanged. Three additional unique addresses contribute279 original body bytes; all104 instructions exercised. Original59f890 takes three cdecl arguments: owner key, viewport index and low-byte force. No checker or numeric allowance changes. Preserves the zero-credit original-training rendering preview and every preceding pinned artifact.','publishing':semantic['publishing'],'playable':False}
target.write_text(json.dumps(c,indent=2)+'\n');print('Pinned',len(artifacts),'artifacts;201 suites;3 new addresses;',sha(target))
