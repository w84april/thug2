"""Pin two initialized Animation state storage routines and preserve all preceding evidence."""
import csv,hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';read=lambda f:json.loads(f.read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
previous=p/'training-warehouse-v3-checkpoint.json';prior=read(previous)
assert sha(previous)=='c14f3b1901ad88b3a4f62d4ad374b575123f69fc774f8e8f90aaa9c94f5b12f3'
engine=p/'animation-component-storage-v3-checkpoint.json';semantic=read(engine)
assert sha(engine)=='4539ac1e1bf455980713e4e51ad56b599c0abf7e6cd8b9ce4dd4196a2ec0e459'
target=p/'animation-state-storage-v3-checkpoint.json';assert not target.exists()
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,h in prior[group].items():assert sha(r/name)==h,(group,name)
w=p/'animation-state-storage-v1.wasm';b=read(w.with_suffix('.build.json'));assert sha(w)==b['sha256']
for name,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==h,name
expected=read(p/'animation-state-storage-v3-node-all.json');proof=read(p/'animation-state-storage-v3-browser-full.json');old=read(p/'animation-component-storage-v3-browser.json')['observed']['suites']
assert len(expected['suites'])==203 and len(old)==202
assert proof['observed']==expected and proof['status'].startswith('PASS') and 'Chrome/154.' in proof['user_agent']
assert expected['wasm_sha256']==sha(w) and expected['wasm_bytes']==w.stat().st_size and expected['runtime_imports']==0
for name,value in old.items():assert expected['suites'][name]==value,name
assert all(v['result']=='pass' for v in expected['suites'].values())
canonical=json.dumps(expected,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert proof['rendered_dom_fingerprint']=={'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(expected)}
name='animation-state-storage-v3';original=read(p/(name+'-original.json'));unit=expected['suites']['animation_state_storage_v3'];fixture=read(p/(name+'-fixtures.json'));routines=read(p/(name+'-routines.json'))
assert original['cases']==unit['cases']==504 and original['calls']==unit['calls']==1008 and original['counts']==unit['counts']
assert unit['nan_fields_classification_only']==0 and unit['startup_diagnostic_callbacks']==0 and not fixture['float_fields']
inventory={int(row['address'],16):row for row in csv.DictReader((r/'progress/function-inventory.tsv').open(),delimiter='\t')}
addresses={};covered=total=body=0
for at,row in routines.items():
 inv=inventory[int(at,16)];assert row['bytes']==int(inv['body_bytes']);cov=original['instruction_coverage'][at]
 assert original['counts'][row['name']]>0 and cov['total']==row['instructions'] and set(cov['missing'])==set(cov['excluded'])
 assert not cov['excluded']
 addresses[at]={**row,'body_bytes':int(inv['body_bytes']),'ranges':inv['ranges'],'original_evidence':name+'-original.json','node_evidence':name+'-regression-'+name+'-result.json','browser_suite':'animation_state_storage_v3'}
 covered+=cov['covered'];total+=cov['total'];body+=int(inv['body_bytes'])
assert len(addresses)==2 and (covered,total,body)==(77,77,244)
for case in fixture['cases']:
 for step in case['steps']:assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','quiet_double_fields','global_quiet_float_indices','global_bit_masks','float_fields','global_float_indices','indeterminate_words','indeterminate_bytes','compression_records'])
baseline=p/'animation-state-storage-v3-reporting-baseline-report.json';assert not baseline.exists();baseline.write_bytes((r/'progress/report.json').read_bytes())
assert sha(baseline)=='76e3f29d9b3b2ce50d3e5aec97fa99cab974b98f4f885761da1e35af92989716'
paths={previous,p/'training-warehouse-v3-audit.json',baseline}
for pattern in ['animation-state-storage-v*','build-animation-state-storage-v*','probe-animation-state-storage-v*','verify-animation-state-storage-v*','serve-animation-state-storage-v*','pin-animation-state-storage-v*','audit-animation-state-storage-v*','trace-skater-initialization-v6*','skater-initialization-v6-trace*','trace-skater-initialization-v7*','skater-initialization-v7-trace*','animation-warehouse-hosted-upload.json','animation-warehouse-public-clone-verification.json']:
 paths.update(f for f in p.glob(pattern) if f.is_file())

for name in ['animation-state-storage-v1-unit.log','animation-state-storage-v2-unit.log','animation-state-storage-v3-unit.log','animation-state-storage-v2-original-run.log','animation-state-storage-v3-original-run.log','animation-state-storage-v3-regression-run.log','skater-initialization-v6-trace-run.log','skater-initialization-v7-trace-run.log']:
 paths.add(r/'local/build'/name)
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
for f in paths:
 artifacts[str(f.relative_to(r))]=sha(f)
 if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
c={'schema':3,'result':'original comparisons, Node and actual Chromium pass; unpromoted','specimen_sha256':prior['specimen_sha256'],'prior_checkpoint':str(previous.relative_to(r)),'prior_checkpoint_sha256':sha(previous),'prior_engine_checkpoint':str(engine.relative_to(r)),'prior_engine_checkpoint_sha256':sha(engine),'wasm':str(w.relative_to(r)),'wasm_sha256':sha(w),'wasm_bytes':w.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],'source_hashes':b['source_hashes'],'draft_source_hashes':b['draft_source_hashes'],'platform_source_hashes':prior['platform_source_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),'browser_suites':203,'preserved_browser_suites':202,'browser_dom_fingerprint':proof['rendered_dom_fingerprint'],'new_functions':2,'verified_mappings':2,'original_addresses':addresses,'verified_scoped_addresses_from_prior':{},'selection_policy':'Additional independent selection of two new Animation state storage addresses only. Earlier viewport/camera and historical582d90 completion remain selected separately. Existing component base and generic allocator callees receive no repeated credit. Identity tables and rendering preview earn no virtual-method or extra completion credit.','new_complete_body_bytes':244,'new_verified_linear_bytes':244,'new_cases':504,'new_completed_calls':1008,'original_covered_instructions':77,'original_linear_instructions':77,'public_report_at_verification':{'path':str(baseline.relative_to(r)),'sha256':sha(baseline)},'unsupported_routes':semantic['unsupported_routes']+['Full581850 profile startup, SkaterCamera reset, camera-specific QB initialization and commands remain unfinished; Animation candidate startup traces are discovery only; Animation virtual lifecycle is unverified'],'scope':original['scope']+' All203 Node/actualChromium suites pass and all202 predecessor result objects are unchanged. Two additional unique addresses contribute244 original body bytes;77/77 instructions exercised with no exclusions. Pointer arguments and unaligned owner/component identities are explicitly declared; failedv1/v2 fixtures and unit logs remain preserved. The first browser object capture was truncated at200 keys; full DOM text is separately preserved and all203 result objects compare exactly. No checker or numeric allowance changes. All earlier Warehouse preview, rendering and engine artifacts remain immutable. Startupv6/v7 traces are discovery only; the Animation heap-context slot is caller-initialized and no full419dd0/configuration/profile credit is claimed.','publishing':semantic['publishing'],'playable':False}
target.write_text(json.dumps(c,indent=2)+'\n');print('Pinned',len(artifacts),'artifacts;203 suites;2 new addresses;',sha(target))
