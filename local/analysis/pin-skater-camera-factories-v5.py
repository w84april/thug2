"""Pin original camera descriptor storage and binding and preserve all preceding evidence."""
import csv,hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';read=lambda f:json.loads(f.read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
previous=p/'skater-camera-reset-v1-checkpoint.json';prior=read(previous)
assert sha(previous)=='811f7673994b8a3318ef8d89af3a9b3e7301891614c849e6aff4e2205d778c62'
engine=p/'skater-camera-reset-v1-checkpoint.json';semantic=read(engine)
assert sha(engine)=='811f7673994b8a3318ef8d89af3a9b3e7301891614c849e6aff4e2205d778c62'
target=p/'skater-camera-factories-v5-checkpoint.json';assert not target.exists()
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,h in prior[group].items():assert sha(r/name)==h,(group,name)
w=p/'skater-camera-factories-v1.wasm';b=read(w.with_suffix('.build.json'));assert sha(w)==b['sha256']
for name,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==h,name
expected=read(p/'skater-camera-factories-v1-node-all.json');proof=read(p/'skater-camera-factories-v1-browser-full.json');old=read(p/'skater-camera-reset-v1-browser-full.json')['observed']['suites']
assert len(expected['suites'])==205 and len(old)==204
assert proof['observed']==expected and proof['status'].startswith('PASS') and 'Chrome/154.' in proof['user_agent']
assert expected['wasm_sha256']==sha(w) and expected['wasm_bytes']==w.stat().st_size and expected['runtime_imports']==0
for name,value in old.items():assert expected['suites'][name]==value,name
assert all(v['result']=='pass' for v in expected['suites'].values())
canonical=json.dumps(expected,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert proof['rendered_dom_fingerprint']=={'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(expected)}
name='skater-camera-factories-v1';original=read(p/(name+'-original.json'));unit=expected['suites']['skater_camera_factories_v1'];fixture=read(p/(name+'-fixtures.json'));routines=read(p/(name+'-routines.json'))
assert original['cases']==unit['cases']==81 and original['calls']==unit['calls']==165 and original['counts']==unit['counts']
assert unit['nan_fields_classification_only']==0 and unit['startup_diagnostic_callbacks']==0 and not fixture['float_fields']
inventory={int(row['address'],16):row for row in csv.DictReader((r/'progress/function-inventory.tsv').open(),delimiter='\t')}
addresses={};covered=total=body=0
for at,row in routines.items():
 inv=inventory[int(at,16)];assert row['bytes']==int(inv['body_bytes']);cov=original['instruction_coverage'][at]
 assert original['counts'][row['name']]>0 and cov['total']==row['instructions'] and set(cov['missing'])==set(cov['excluded'])
 assert cov['excluded']==({'0x4fa4f3':'initialized allocator contract excludes the literal cold bootstrap call'} if at=='0x4fa4b0' else {})
 addresses[at]={**row,'body_bytes':int(inv['body_bytes']),'ranges':inv['ranges'],'original_evidence':name+'-original.json','node_evidence':name+'-regression-'+name+'-result.json','browser_suite':'skater_camera_factories_v1'}
 covered+=cov['covered'];total+=cov['total'];body+=int(inv['body_bytes'])
assert len(addresses)==6 and (covered,total,body)==(150,151,554)
for case in fixture['cases']:
 for step in case['steps']:assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','quiet_double_fields','global_quiet_float_indices','global_bit_masks','float_fields','global_float_indices','indeterminate_words','indeterminate_bytes','compression_records'])
baseline=p/'skater-camera-factories-v3-reporting-baseline-report.json';assert not baseline.exists();baseline.write_bytes((p/'skater-camera-factories-v2-reporting-baseline-report.json').read_bytes())
assert sha(baseline)=='eb036280ef2f09b3b6b4d7e9d3644b0b31119d62b188c2d4dc6581a0d996bbe8'
paths={previous,p/'skater-camera-reset-v1-audit.json',baseline}
for pattern in ['skater-camera-reset-v*','build-skater-camera-reset-v*','probe-skater-camera-reset-v*','verify-skater-camera-reset-v*','serve-skater-camera-reset-v*','pin-skater-camera-reset-v*','audit-skater-camera-reset-v*','skater-camera-config-v*','inspect-skater-camera-config-v*']:
 paths.update(f for f in p.glob(pattern) if f.is_file())

for pattern in ['skater-camera-factories-v*','build-skater-camera-factories-v*','probe-skater-camera-factories-v*','verify-skater-camera-factories-v*','serve-skater-camera-factories-v*','pin-skater-camera-factories-v*','audit-skater-camera-factories-v*']:
 paths.update(f for f in p.glob(pattern) if f.is_file())
for directory in p.glob('skater-camera-factories-v*-ghidra'):
 paths.update(f for f in directory.rglob('*') if f.is_file())
for name in ['skater-camera-factories-v1-unit.log','skater-camera-factories-v1-original-run.log','skater-camera-factories-v1-build-run.log','skater-camera-factories-v1-regression-run.log']:
 paths.add(r/'local/build'/name)
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
for f in paths:
 artifacts[str(f.relative_to(r))]=sha(f)
 if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
for suffix in ['-routines.json','-original.json','-fixtures.json','-browser-full.json','-node-all.json','-regression-skater-camera-factories-v1-result.json','.build.json','.wasm','.c']:
 assert str((p/('skater-camera-factories-v1'+suffix)).relative_to(r)) in artifacts,suffix
reused={key:addresses.pop(key) for key in ['0x5902e0']}
assert len(addresses)==5 and sum(row['body_bytes'] for row in addresses.values())==551
c={'schema':3,'result':'original comparisons, Node and actual Chromium pass; unpromoted','specimen_sha256':prior['specimen_sha256'],'prior_checkpoint':str(previous.relative_to(r)),'prior_checkpoint_sha256':sha(previous),'prior_engine_checkpoint':str(engine.relative_to(r)),'prior_engine_checkpoint_sha256':sha(engine),'wasm':str(w.relative_to(r)),'wasm_sha256':sha(w),'wasm_bytes':w.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],'source_hashes':b['source_hashes'],'draft_source_hashes':b['draft_source_hashes'],'platform_source_hashes':prior['platform_source_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),'browser_suites':205,'preserved_browser_suites':204,'browser_dom_fingerprint':proof['rendered_dom_fingerprint'],'new_functions':5,'verified_mappings':6,'original_addresses':addresses,'verified_scoped_addresses_from_prior':reused,'selection_policy':'Five new factory/constructor/first-component-binding addresses plus a repeated behavioral mapping of already selected three-byte5902e0; the helper earns no new bytes. Earlier selections remain independent; component base and allocator callees earn no repeated credit. Identity-only tables establish no virtual lifecycle or frame behavior.','new_complete_body_bytes':551,'new_verified_linear_bytes':554,'new_cases':81,'new_completed_calls':165,'original_covered_instructions':150,'original_linear_instructions':151,'public_report_at_verification':{'path':str(baseline.relative_to(r)),'sha256':sha(baseline)},'unsupported_routes':[v.replace('SkaterCamera reset','full SkaterCamera initialization/update') for v in semantic['unsupported_routes']]+['Full581850 profile startup and full SkaterCamera initialization/update remain unfinished; Animation candidate startup traces are discovery only; Animation virtual lifecycle is unverified'],'scope':original['scope']+' All205 Node/actualChromium suites pass and all204 predecessor result objects are unchanged. Five new unique addresses contribute551 original body bytes; the sixth mapped routine5902e0 is already selected and earns no additional3bytes;150/151 instructions exercised with only initialized-allocator coldcall4fa4f3 excluded. Complete browser evidence is parsed from full DOM text and independently compared to Node; no structured-object truncation. Previous constructor callees earn no repeated bytes. No checker or numeric allowance changes, no full SkaterCamera initialization/update, full581850 startup, frame or gameplay claim.','publishing':semantic['publishing'],'playable':False}
target.write_text(json.dumps(c,indent=2)+'\n');print('Pinned',len(artifacts),'artifacts;205 suites;5 new addresses plus1 repeated mapping;',sha(target))
