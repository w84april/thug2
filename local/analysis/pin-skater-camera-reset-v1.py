"""Pin original camera reset/FOV routines and preserve all preceding evidence."""
import csv,hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';read=lambda f:json.loads(f.read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
previous=p/'animation-state-storage-v3-checkpoint.json';prior=read(previous)
assert sha(previous)=='b25d1215c1d4f460d7821eb457b368fb2b201bdd804fa84d4f8657f4323003c2'
engine=p/'animation-state-storage-v3-checkpoint.json';semantic=read(engine)
assert sha(engine)=='b25d1215c1d4f460d7821eb457b368fb2b201bdd804fa84d4f8657f4323003c2'
target=p/'skater-camera-reset-v1-checkpoint.json';assert not target.exists()
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,h in prior[group].items():assert sha(r/name)==h,(group,name)
w=p/'skater-camera-reset-v1.wasm';b=read(w.with_suffix('.build.json'));assert sha(w)==b['sha256']
for name,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==h,name
expected=read(p/'skater-camera-reset-v1-node-all.json');proof=read(p/'skater-camera-reset-v1-browser-full.json');old=read(p/'animation-state-storage-v3-browser-full.json')['observed']['suites']
assert len(expected['suites'])==204 and len(old)==203
assert proof['observed']==expected and proof['status'].startswith('PASS') and 'Chrome/154.' in proof['user_agent']
assert expected['wasm_sha256']==sha(w) and expected['wasm_bytes']==w.stat().st_size and expected['runtime_imports']==0
for name,value in old.items():assert expected['suites'][name]==value,name
assert all(v['result']=='pass' for v in expected['suites'].values())
canonical=json.dumps(expected,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert proof['rendered_dom_fingerprint']=={'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(expected)}
name='skater-camera-reset-v1';original=read(p/(name+'-original.json'));unit=expected['suites']['skater_camera_reset_v1'];fixture=read(p/(name+'-fixtures.json'));routines=read(p/(name+'-routines.json'))
assert original['cases']==unit['cases']==333 and original['calls']==unit['calls']==924 and original['counts']==unit['counts']
assert unit['nan_fields_classification_only']==0 and unit['startup_diagnostic_callbacks']==0 and not fixture['float_fields']
inventory={int(row['address'],16):row for row in csv.DictReader((r/'progress/function-inventory.tsv').open(),delimiter='\t')}
addresses={};covered=total=body=0
for at,row in routines.items():
 inv=inventory[int(at,16)];assert row['bytes']==int(inv['body_bytes']);cov=original['instruction_coverage'][at]
 assert original['counts'][row['name']]>0 and cov['total']==row['instructions'] and set(cov['missing'])==set(cov['excluded'])
 assert not cov['excluded']
 addresses[at]={**row,'body_bytes':int(inv['body_bytes']),'ranges':inv['ranges'],'original_evidence':name+'-original.json','node_evidence':name+'-regression-'+name+'-result.json','browser_suite':'skater_camera_reset_v1'}
 covered+=cov['covered'];total+=cov['total'];body+=int(inv['body_bytes'])
assert len(addresses)==2 and (covered,total,body)==(276,276,947)
for case in fixture['cases']:
 for step in case['steps']:assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','quiet_double_fields','global_quiet_float_indices','global_bit_masks','float_fields','global_float_indices','indeterminate_words','indeterminate_bytes','compression_records'])
baseline=p/'skater-camera-reset-v1-reporting-baseline-report.json';assert not baseline.exists();baseline.write_bytes((r/'progress/report.json').read_bytes())
assert sha(baseline)=='d4ae71291102361013c65123f6d322cf4ed8b30a82fb1a7934f22a5d68c227f1'
paths={previous,p/'animation-state-storage-v3-audit.json',baseline}
for pattern in ['skater-camera-reset-v*','build-skater-camera-reset-v*','probe-skater-camera-reset-v*','verify-skater-camera-reset-v*','serve-skater-camera-reset-v*','pin-skater-camera-reset-v*','audit-skater-camera-reset-v*','skater-camera-config-v*','inspect-skater-camera-config-v*']:
 paths.update(f for f in p.glob(pattern) if f.is_file())

config=read(p/'skater-camera-config-v2-original.json');asset=r/config['path'];assert sha(asset)==config['sha256'];paths.add(asset)
for name in ['skater-camera-reset-v1-unit.log','skater-camera-reset-v1-original-run.log','skater-camera-reset-v1-build-run.log','skater-camera-reset-v1-regression-run.log','skater-camera-config-v1-original-run.log','skater-camera-config-v2-original-run.log']:
 paths.add(r/'local/build'/name)
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
for f in paths:
 artifacts[str(f.relative_to(r))]=sha(f)
 if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
c={'schema':3,'result':'original comparisons, Node and actual Chromium pass; unpromoted','specimen_sha256':prior['specimen_sha256'],'prior_checkpoint':str(previous.relative_to(r)),'prior_checkpoint_sha256':sha(previous),'prior_engine_checkpoint':str(engine.relative_to(r)),'prior_engine_checkpoint_sha256':sha(engine),'wasm':str(w.relative_to(r)),'wasm_sha256':sha(w),'wasm_bytes':w.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],'source_hashes':b['source_hashes'],'draft_source_hashes':b['draft_source_hashes'],'platform_source_hashes':prior['platform_source_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),'browser_suites':204,'preserved_browser_suites':203,'browser_dom_fingerprint':proof['rendered_dom_fingerprint'],'new_functions':2,'verified_mappings':2,'original_addresses':addresses,'verified_scoped_addresses_from_prior':{},'selection_policy':'Additional independent selection of two new camera reset/FOV addresses only. Earlier viewport/camera and historical582d90 completion remain selected separately. Existing component base and generic allocator callees receive no repeated credit. Identity tables and rendering preview earn no virtual-method or extra completion credit.','new_complete_body_bytes':947,'new_verified_linear_bytes':947,'new_cases':333,'new_completed_calls':924,'original_covered_instructions':276,'original_linear_instructions':276,'public_report_at_verification':{'path':str(baseline.relative_to(r)),'sha256':sha(baseline)},'unsupported_routes':[v.replace('SkaterCamera reset','full SkaterCamera initialization/update') for v in semantic['unsupported_routes']]+['Full581850 profile startup and full SkaterCamera initialization/update remain unfinished; Animation candidate startup traces are discovery only; Animation virtual lifecycle is unverified'],'scope':original['scope']+' All204 Node/actualChromium suites pass and all203 predecessor result objects are unchanged. Two additional unique addresses contribute947 original body bytes;276/276 instructions exercised with no exclusions. Complete browser evidence is parsed from full DOM text and independently compared to Node; no structured-object truncation. Previous constructor callees earn no repeated bytes. Physics QB source and original-loader preset discovery are immutable private inputs. No checker or numeric allowance changes, no full SkaterCamera initialization/update, full581850 startup, frame or gameplay claim.','publishing':semantic['publishing'],'playable':False}
target.write_text(json.dumps(c,indent=2)+'\n');print('Pinned',len(artifacts),'artifacts;204 suites;2 new addresses;',sha(target))
