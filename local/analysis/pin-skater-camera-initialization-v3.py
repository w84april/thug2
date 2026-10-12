"""Pin complete camera QB comparisons with explicit duplicate accounting."""
import csv,hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';read=lambda f:json.loads(f.read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
previous=p/'skater-camera-factories-v5-checkpoint.json';prior=read(previous)
assert sha(previous)=='28edb42705db106778cdedf1ce9aaf16d1b4d4a20f1e93ff78c77e4752767fd2'
audit=p/'skater-camera-factories-v5-audit.json';assert read(audit)['result']=='pass' and read(audit)['checkpoint_sha256']==sha(previous)
target=p/'skater-camera-initialization-v3-checkpoint.json';assert not target.exists()
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,h in prior[group].items():assert sha(r/name)==h,(group,name)
w=p/'skater-camera-initialization-v2.wasm';b=read(w.with_suffix('.build.json'));assert sha(w)==b['sha256']
for name,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==h,name
expected=read(p/'skater-camera-initialization-v3-node-all.json');proof=read(p/'skater-camera-initialization-v3-browser-full.json');old=read(p/'skater-camera-factories-v1-browser-full.json')['observed']['suites']
assert len(expected['suites'])==206 and len(old)==205
assert proof['observed']==expected and proof['status'].startswith('PASS') and 'Chrome/154.' in proof['user_agent']
assert expected['wasm_sha256']==sha(w) and expected['wasm_bytes']==w.stat().st_size and expected['runtime_imports']==0
for name,value in old.items():assert expected['suites'][name]==value,name
assert all(v['result']=='pass' for v in expected['suites'].values())
canonical=json.dumps(expected,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert proof['rendered_dom_fingerprint']=={'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(expected)}
name='skater-camera-initialization-v3';original=read(p/(name+'-original.json'));unit=expected['suites']['skater_camera_initialization_v3'];fixture=read(p/(name+'-fixtures.json'));routines=read(p/(name+'-routines.json'))
assert original['cases']==unit['cases']==423 and original['calls']==unit['calls']==918 and original['counts']==unit['counts']
assert unit['nan_fields_classification_only']==0 and unit['startup_diagnostic_callbacks']==0 and not fixture['float_fields']
inventory={int(row['address'],16):row for row in csv.DictReader((r/'progress/function-inventory.tsv').open(),delimiter='\t')}
extra=p/(name+'-extra-ranges.tsv');extra_rows=list(csv.DictReader(extra.open(),delimiter='\t'))
assert {int(row['address'],16) for row in extra_rows}=={0x4fa5c0,0x4e3f70,0x524f50}
raw={int(row['address'],16):row for row in csv.DictReader((p/'skater-camera-factories-v2-ranges.tsv').open(),delimiter='\t')}
for row in extra_rows:
 at=int(row['address'],16);assert at not in inventory and row==raw[at];inventory[at]=row
selected={int(row['address'],16):row for row in read(r/'progress/ledger.json')['records']}
reused={};addresses={};covered=total=body=0
for at,row in routines.items():
 inv=inventory[int(at,16)];assert row['bytes']==int(inv['body_bytes']);cov=original['instruction_coverage'][at]
 assert original['counts'][row['name']]>0 and cov['total']==row['instructions'] and not cov['missing'] and not cov['excluded']
 entry={**row,'body_bytes':int(inv['body_bytes']),'ranges':inv['ranges'],'original_evidence':name+'-original.json','node_evidence':name+'-regression-'+name+'-result.json','browser_suite':'skater_camera_initialization_v3'}
 (reused if int(at,16) in selected else addresses)[at]=entry
 covered+=cov['covered'];total+=cov['total'];body+=int(inv['body_bytes'])
assert set(reused)=={'0x4fa3c0','0x524c50'} and len(addresses)==5 and (covered,total,body)==(165,165,551)
assert sum(row['body_bytes'] for row in addresses.values())==384
for case in fixture['cases']:
 for step in case['steps']:assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','quiet_double_fields','global_quiet_float_indices','global_bit_masks','float_fields','global_float_indices','indeterminate_words','indeterminate_bytes','compression_records'])
baseline=p/(name+'-reporting-baseline-report.json');assert not baseline.exists();baseline.write_bytes((r/'progress/report.json').read_bytes())
paths={previous,audit,baseline,extra}
for pattern in ['skater-camera-initialization-v*','build-skater-camera-initialization-v*','probe-skater-camera-initialization-v*','verify-skater-camera-initialization-v*','serve-skater-camera-initialization-v*','pin-skater-camera-initialization-v*','audit-skater-camera-initialization-v*','trace-skater-camera-composite-v*','skater-camera-composite-v*']:
 paths.update(f for f in p.glob(pattern) if f.is_file())
for n in ['skater-camera-initialization-v1-original-run.log','skater-camera-initialization-v2-original-run.log','skater-camera-initialization-v3-original-run.log','skater-camera-initialization-v1-build-run.log','skater-camera-initialization-v1-build-v2-run.log','skater-camera-initialization-v2-build-run.log','skater-camera-initialization-v3-unit.log','skater-camera-initialization-v3-regression-run.log']:
 paths.add(r/'local/build'/n)
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
for f in paths:
 artifacts[str(f.relative_to(r))]=sha(f)
 if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
for suffix in ['-routines.json','-original.json','-fixtures.json','-browser-full.json','-node-all.json','-regression-'+name+'-result.json']:
 assert str((p/(name+suffix)).relative_to(r)) in artifacts,suffix
c={'schema':3,'result':'original comparisons, Node and actual Chromium pass; unpromoted','specimen_sha256':prior['specimen_sha256'],'prior_checkpoint':str(previous.relative_to(r)),'prior_checkpoint_sha256':sha(previous),'prior_engine_checkpoint':str(previous.relative_to(r)),'prior_engine_checkpoint_sha256':sha(previous),'wasm':str(w.relative_to(r)),'wasm_sha256':sha(w),'wasm_bytes':w.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],'source_hashes':b['source_hashes'],'draft_source_hashes':b['draft_source_hashes'],'platform_source_hashes':prior['platform_source_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),'browser_suites':206,'preserved_browser_suites':205,'browser_dom_fingerprint':proof['rendered_dom_fingerprint'],'new_functions':5,'verified_mappings':7,'original_addresses':addresses,'verified_scoped_addresses_from_prior':reused,'selection_policy':'Five new camera QB-initialization/final-link addresses contribute384 bytes. Two existing target-binding addresses4fa3c0/524c50 are independently remapped and tested; their167 bytes receive no repeated credit. Exactly three newly discovered extents are selected; original.text denominator stays fixed. No virtual-table/frame/composite-profile startup or preview credit.','new_complete_body_bytes':384,'new_verified_linear_bytes':551,'new_cases':423,'new_completed_calls':918,'original_covered_instructions':165,'original_linear_instructions':165,'public_report_at_verification':{'path':str(baseline.relative_to(r)),'sha256':sha(baseline)},'unsupported_routes':prior['unsupported_routes']+['Original camera composite pipeline currently stops at generic Camera initialization41b7f0; direct new QB initialization is verified, but full composite assembly/update/profile startup and gameplay remain unfinished.'],'scope':original['scope']+' All206 Node/actualChromium suites pass and all205 predecessor result objects are unchanged. Five new addresses/384bytes; two remapped target bindings/167bytes already selected and uncredited. Complete browser evidence is parsed from full DOM text and independently compared to Node. Failed earlier integer-getter assumptions, probes and module remain private and unselected. No numeric/comparator changes.','publishing':prior['publishing'],'playable':False}
target.write_text(json.dumps(c,indent=2)+'\n');print('Pinned',len(artifacts),'artifacts;206 suites;5 new addresses/384bytes;2 repeated mappings;',sha(target))
