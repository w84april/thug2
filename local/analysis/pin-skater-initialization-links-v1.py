"""Pin four additional selected routines; older selections remain independent."""
import hashlib,json,csv
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';read=lambda f:json.loads(f.read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
previous=p/'skater-full-startup-checkpoint.json';prior=read(previous);assert sha(previous)=='54626e56a2fd2b8f3c98c89a2dc86e5f5a3ec56fe7d82655722d6cc73615bc62'
target=p/'skater-initialization-links-v1-checkpoint.json';assert not target.exists()
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,h in prior[group].items():assert sha(r/name)==h,(group,name)
w=p/'skater-initialization-links-v1.wasm';b=read(w.with_suffix('.build.json'));assert sha(w)==b['sha256']
for name,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==h,name
expected=read(p/'skater-initialization-links-v1-node-all.json');proof=read(p/'skater-initialization-links-v1-browser.json');old=read(p/'skater-full-startup-browser.json')['observed']['suites'];assert len(expected['suites'])==199 and len(old)==198
assert proof['observed']==expected and proof['status'].startswith('PASS') and 'Chrome/154.' in proof['user_agent']
assert expected['wasm_sha256']==sha(w) and expected['wasm_bytes']==w.stat().st_size and expected['runtime_imports']==0
for name,value in old.items():assert expected['suites'][name]==value,name
assert all(v['result']=='pass' for v in expected['suites'].values())
canonical=json.dumps(expected,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert proof['rendered_dom_fingerprint']=={'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(expected)}
name='skater-initialization-links-v1';original=read(p/(name+'-original.json'));unit=expected['suites']['skater_initialization_links_v1'];fixture=read(p/(name+'-fixtures.json'));routines=read(p/(name+'-routines.json'))
assert original['cases']==unit['cases']==55 and original['calls']==unit['calls']==131 and original['counts']==unit['counts']
assert unit['nan_fields_classification_only']==0 and unit['startup_diagnostic_callbacks']==10 and not fixture['float_fields']
inventory={int(row['address'],16):row for row in csv.DictReader((r/'progress/function-inventory.tsv').open(),delimiter='\t')}
addresses={};covered=total=body=0
for at,row in routines.items():
 inv=inventory[int(at,16)];assert row['bytes']==int(inv['body_bytes']);cov=original['instruction_coverage'][at]
 assert original['counts'][row['name']]>0 and cov['total']==row['instructions'] and set(cov['missing'])==set(cov['excluded'])
 addresses[at]={**row,'body_bytes':int(inv['body_bytes']),'ranges':inv['ranges'],'original_evidence':name+'-original.json','node_evidence':name+'-regression-'+name+'-result.json','browser_suite':'skater_initialization_links_v1'}
 covered+=cov['covered'];total+=cov['total'];body+=int(inv['body_bytes'])
assert len(addresses)==4 and (covered,total,body)==(127,132,451)
for case in fixture['cases']:
 for step in case['steps']:assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','quiet_double_fields','global_quiet_float_indices','global_bit_masks','float_fields','global_float_indices','indeterminate_words','indeterminate_bytes','compression_records'])
baseline=p/'initialization-links-v1-reporting-baseline-report.json';assert not baseline.exists();baseline.write_bytes((r/'progress/report.json').read_bytes());assert sha(baseline)=='f471d18b6b309f4d3c8a9349b44ecdf7d79449f564a7555669c9ac306b92de5b'
paths={previous,p/'skater-full-startup-audit.json',baseline}
for pattern in ['skater-initialization-links-v1*','build-skater-initialization-links-v1*','probe-skater-initialization-links-v1*','verify-skater-initialization-links-v1*','serve-skater-initialization-links-v1*','pin-skater-initialization-links-v1*','audit-skater-initialization-links-v1*','trace-skater-initialization-v1*','skater-initialization-v1-trace*','inspect-skater-camera-qb-v1*','skater-camera-qb-v1*']:
 paths.update(f for f in p.glob(pattern) if f.is_file())
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
for f in paths:
 artifacts[str(f.relative_to(r))]=sha(f)
 if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
c={'schema':3,'result':'original comparisons, Node and actual Chromium pass; unpromoted','specimen_sha256':prior['specimen_sha256'],'prior_checkpoint':str(previous.relative_to(r)),'prior_checkpoint_sha256':sha(previous),'wasm':str(w.relative_to(r)),'wasm_sha256':sha(w),'wasm_bytes':w.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],'source_hashes':b['source_hashes'],'draft_source_hashes':b['draft_source_hashes'],'platform_source_hashes':prior['platform_source_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),'browser_suites':199,'preserved_browser_suites':198,'browser_dom_fingerprint':proof['rendered_dom_fingerprint'],'new_functions':4,'verified_mappings':4,'original_addresses':addresses,'verified_scoped_addresses_from_prior':{},'selection_policy':'This additional independent update selects only four new addresses. Existing full-startup update remains selected separately, preserving its historical582d90 resolution and all previous completion credit. No repeated credit for existing constructors/searches.','new_complete_body_bytes':451,'new_verified_linear_bytes':451,'new_cases':55,'new_completed_calls':131,'original_covered_instructions':127,'original_linear_instructions':132,'public_report_at_verification':{'path':str(baseline.relative_to(r)),'sha256':sha(baseline)},'unsupported_routes':prior['unsupported_routes']+['581850 profile initializer, camera factories and Light virtual methods remain unfinished; originalQB/entry traces are discovery only'],'scope':original['scope']+' All199 Node/actualChromium suites pass and all198 predecessor objects are unchanged. Four additional unique addresses contribute451 conservative body bytes; five allocation-fault exclusions retain their bytes. This independent selection does not replace earlier updates. Original QB camera asset discovery receives no completion credit.','publishing':prior['publishing'],'playable':False}
target.write_text(json.dumps(c,indent=2)+'\n');print('Pinned',len(artifacts),'artifacts;199 suites;4 new unique addresses;',sha(target))
