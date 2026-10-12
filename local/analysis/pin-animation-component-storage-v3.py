"""Pin two initialized-heap Animation storage routines and preserve all preceding evidence."""
import csv,hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';read=lambda f:json.loads(f.read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
previous=p/'camera-viewport-v1-checkpoint.json';prior=read(previous)
assert sha(previous)=='fd7fedf3544d67bff84babd59fa4c71e51e2c3895a73faf505ee4b3a80674bbc'
engine=p/'camera-viewport-v1-checkpoint.json';semantic=read(engine)
assert sha(engine)=='fd7fedf3544d67bff84babd59fa4c71e51e2c3895a73faf505ee4b3a80674bbc'
target=p/'animation-component-storage-v3-checkpoint.json';assert not target.exists()
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,h in prior[group].items():assert sha(r/name)==h,(group,name)
w=p/'animation-component-storage-v1.wasm';b=read(w.with_suffix('.build.json'));assert sha(w)==b['sha256']
for name,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==h,name
expected=read(p/'animation-component-storage-v3-node-all.json');proof=read(p/'animation-component-storage-v3-browser.json');old=read(p/'camera-viewport-v1-browser.json')['observed']['suites']
assert len(expected['suites'])==202 and len(old)==201
assert proof['observed']==expected and proof['status'].startswith('PASS') and 'Chrome/154.' in proof['user_agent']
assert expected['wasm_sha256']==sha(w) and expected['wasm_bytes']==w.stat().st_size and expected['runtime_imports']==0
for name,value in old.items():assert expected['suites'][name]==value,name
assert all(v['result']=='pass' for v in expected['suites'].values())
canonical=json.dumps(expected,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert proof['rendered_dom_fingerprint']=={'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(expected)}
name='animation-component-storage-v3';original=read(p/(name+'-original.json'));unit=expected['suites']['animation_component_storage_v3'];fixture=read(p/(name+'-fixtures.json'));routines=read(p/(name+'-routines.json'))
assert original['cases']==unit['cases']==24 and original['calls']==unit['calls']==42 and original['counts']==unit['counts']
assert unit['nan_fields_classification_only']==0 and unit['startup_diagnostic_callbacks']==0 and not fixture['float_fields']
inventory={int(row['address'],16):row for row in csv.DictReader((r/'progress/function-inventory.tsv').open(),delimiter='\t')}
addresses={};covered=total=body=0
for at,row in routines.items():
 inv=inventory[int(at,16)];assert row['bytes']==int(inv['body_bytes']);cov=original['instruction_coverage'][at]
 assert original['counts'][row['name']]>0 and cov['total']==row['instructions'] and set(cov['missing'])==set(cov['excluded'])
 assert set(cov['excluded'])<= {'0x41a472'}
 addresses[at]={**row,'body_bytes':int(inv['body_bytes']),'ranges':inv['ranges'],'original_evidence':name+'-original.json','node_evidence':name+'-regression-'+name+'-result.json','browser_suite':'animation_component_storage_v3'}
 covered+=cov['covered'];total+=cov['total'];body+=int(inv['body_bytes'])
assert len(addresses)==2 and (covered,total,body)==(66,67,248)
for case in fixture['cases']:
 for step in case['steps']:assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','quiet_double_fields','global_quiet_float_indices','global_bit_masks','float_fields','global_float_indices','indeterminate_words','indeterminate_bytes','compression_records'])
baseline=p/'animation-component-storage-v3-reporting-baseline-report.json';assert not baseline.exists();baseline.write_bytes((r/'progress/report.json').read_bytes())
assert sha(baseline)=='06cd639f7777578acc372a8f5435adfbe5ebdd6755a55eee68738e56c96619bb'
paths={previous,p/'camera-viewport-v1-audit.json',baseline}
for pattern in ['animation-component-storage-v*','build-animation-component-storage-v*','probe-animation-component-storage-v*','verify-animation-component-storage-v*','serve-animation-component-storage-v*','pin-animation-component-storage-v*','audit-animation-component-storage-v*','trace-skater-initialization-v5*','skater-initialization-v5-trace*','camera-viewport-v1-hosted-upload.json','camera-viewport-v1-public-clone-verification.json','camera-viewport-v1-decomp-import*']:
 paths.update(f for f in p.glob(pattern) if f.is_file())

artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
for f in paths:
 artifacts[str(f.relative_to(r))]=sha(f)
 if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
c={'schema':3,'result':'original comparisons, Node and actual Chromium pass; unpromoted','specimen_sha256':prior['specimen_sha256'],'prior_checkpoint':str(previous.relative_to(r)),'prior_checkpoint_sha256':sha(previous),'prior_engine_checkpoint':str(engine.relative_to(r)),'prior_engine_checkpoint_sha256':sha(engine),'wasm':str(w.relative_to(r)),'wasm_sha256':sha(w),'wasm_bytes':w.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],'source_hashes':b['source_hashes'],'draft_source_hashes':b['draft_source_hashes'],'platform_source_hashes':prior['platform_source_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),'browser_suites':202,'preserved_browser_suites':201,'browser_dom_fingerprint':proof['rendered_dom_fingerprint'],'new_functions':2,'verified_mappings':2,'original_addresses':addresses,'verified_scoped_addresses_from_prior':{},'selection_policy':'Additional independent selection of two new Animation storage addresses only. Earlier viewport/camera and historical582d90 completion remain selected separately. Existing component base and generic allocator callees receive no repeated credit. Identity tables and rendering preview earn no virtual-method or extra completion credit.','new_complete_body_bytes':248,'new_verified_linear_bytes':248,'new_cases':24,'new_completed_calls':42,'original_covered_instructions':66,'original_linear_instructions':67,'public_report_at_verification':{'path':str(baseline.relative_to(r)),'sha256':sha(baseline)},'unsupported_routes':semantic['unsupported_routes']+['Full581850 profile startup, SkaterCamera reset, camera-specific QB initialization and commands remain unfinished; Animation candidate startup traces are discovery only; Animation virtual lifecycle is unverified'],'scope':original['scope']+' All202 Node/actualChromium suites pass and all201 predecessor result objects are unchanged. Two additional unique addresses contribute248 original body bytes;66/67 instructions exercised, with only the reviewed41a472 cold allocator bootstrap call excluded by the initialized-service contract. Embedded unaligned vtable relocation is explicitly declared; failedv2 unit and earlier dynamic-exclusion harness are retained. No checker or numeric allowance changes. All earlier rendering/engine artifacts remain immutable.','publishing':semantic['publishing'],'playable':False}
target.write_text(json.dumps(c,indent=2)+'\n');print('Pinned',len(artifacts),'artifacts;202 suites;2 new addresses;',sha(target))
