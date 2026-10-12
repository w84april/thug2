"""Pin thirteen additional selected camera routines; older selections remain independent."""
import hashlib,json,csv
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';read=lambda f:json.loads(f.read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
previous=p/'skater-initialization-links-v1-checkpoint.json';prior=read(previous);assert sha(previous)=='00f8b62d01b16b1ee0ce3c57c11c698821f90784c74881a552f13668a28cca3f'
target=p/'camera-startup-v2-checkpoint.json';assert not target.exists()
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,h in prior[group].items():assert sha(r/name)==h,(group,name)
w=p/'camera-startup-v2.wasm';b=read(w.with_suffix('.build.json'));assert sha(w)==b['sha256']
for name,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==h,name
expected=read(p/'camera-startup-v2-node-all.json');proof=read(p/'camera-startup-v2-browser.json');old=read(p/'skater-initialization-links-v1-browser.json')['observed']['suites'];assert len(expected['suites'])==200 and len(old)==199
assert proof['observed']==expected and proof['status'].startswith('PASS') and 'Chrome/154.' in proof['user_agent']
assert expected['wasm_sha256']==sha(w) and expected['wasm_bytes']==w.stat().st_size and expected['runtime_imports']==0
for name,value in old.items():assert expected['suites'][name]==value,name
assert all(v['result']=='pass' for v in expected['suites'].values())
canonical=json.dumps(expected,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert proof['rendered_dom_fingerprint']=={'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(expected)}
name='camera-startup-v2';original=read(p/(name+'-original.json'));unit=expected['suites']['camera_startup_v2'];fixture=read(p/(name+'-fixtures.json'));routines=read(p/(name+'-routines.json'))
assert original['cases']==unit['cases']==97 and original['calls']==unit['calls']==271 and original['counts']==unit['counts']
assert unit['nan_fields_classification_only']==0 and unit['startup_diagnostic_callbacks']==0 and not fixture['float_fields']
inventory={int(row['address'],16):row for row in csv.DictReader((r/'progress/function-inventory.tsv').open(),delimiter='\t')}
addresses={};covered=total=body=0
for at,row in routines.items():
 inv=inventory[int(at,16)];assert row['bytes']==int(inv['body_bytes']);cov=original['instruction_coverage'][at]
 assert original['counts'][row['name']]>0 and cov['total']==row['instructions'] and set(cov['missing'])==set(cov['excluded'])
 addresses[at]={**row,'body_bytes':int(inv['body_bytes']),'ranges':inv['ranges'],'original_evidence':name+'-original.json','node_evidence':name+'-regression-'+name+'-result.json','browser_suite':'camera_startup_v2'}
 covered+=cov['covered'];total+=cov['total'];body+=int(inv['body_bytes'])
assert len(addresses)==13 and (covered,total,body)==(276,276,988)
for case in fixture['cases']:
 for step in case['steps']:assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','quiet_double_fields','global_quiet_float_indices','global_bit_masks','float_fields','global_float_indices','indeterminate_words','indeterminate_bytes','compression_records'])
baseline=p/'camera-startup-v2-reporting-baseline-report.json';assert not baseline.exists();baseline.write_bytes((r/'progress/report.json').read_bytes());assert sha(baseline)=='cf32480b00d825c446e9efc265012eff681e744f5ff86aa3f7e2a5e07009b7ef'
paths={previous,p/'skater-initialization-links-v1-audit.json',baseline}
for pattern in ['camera-startup-v2*','build-camera-startup-v2*','probe-camera-startup-v2*','verify-camera-startup-v2*','serve-camera-startup-v2*','pin-camera-startup-v2*','audit-camera-startup-v2*','trace-skater-initialization-v2*','skater-initialization-v2-trace*','trace-skater-initialization-v3*','skater-initialization-v3-trace*']:
 paths.update(f for f in p.glob(pattern) if f.is_file())
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
for f in paths:
 artifacts[str(f.relative_to(r))]=sha(f)
 if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
c={'schema':3,'result':'original comparisons, Node and actual Chromium pass; unpromoted','specimen_sha256':prior['specimen_sha256'],'prior_checkpoint':str(previous.relative_to(r)),'prior_checkpoint_sha256':sha(previous),'wasm':str(w.relative_to(r)),'wasm_sha256':sha(w),'wasm_bytes':w.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],'source_hashes':b['source_hashes'],'draft_source_hashes':b['draft_source_hashes'],'platform_source_hashes':prior['platform_source_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),'browser_suites':200,'preserved_browser_suites':199,'browser_dom_fingerprint':proof['rendered_dom_fingerprint'],'new_functions':13,'verified_mappings':13,'original_addresses':addresses,'verified_scoped_addresses_from_prior':{},'selection_policy':'This additional independent update selects only thirteen new camera addresses. Existing full-startup update remains selected separately, preserving its historical582d90 resolution and all previous completion credit. No repeated credit for existing constructors/searches.','new_complete_body_bytes':988,'new_verified_linear_bytes':988,'new_cases':97,'new_completed_calls':271,'original_covered_instructions':276,'original_linear_instructions':276,'public_report_at_verification':{'path':str(baseline.relative_to(r)),'sha256':sha(baseline)},'unsupported_routes':prior['unsupported_routes']+['581850 profile initialization, SkaterCamera/WalkCamera factories, Camera component-specific QB initialization/commands and viewport registration remain unfinished; originalQB/entry traces are discovery only'],'scope':original['scope']+' All200 Node/actualChromium suites pass and all199 predecessor objects are unchanged. Thirteen additional unique addresses contribute988 original body bytes; all276 instructions exercised. No new numeric allowance or checker change. This independent selection does not replace earlier updates. Original QB camera asset discovery receives no completion credit.','publishing':prior['publishing'],'playable':False}
target.write_text(json.dumps(c,indent=2)+'\n');print('Pinned',len(artifacts),'artifacts;200 suites;13 new unique addresses;',sha(target))
