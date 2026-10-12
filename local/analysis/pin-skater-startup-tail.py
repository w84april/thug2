"""Pin verified component startup and the still-partial original constructor."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';read=lambda f:json.loads(f.read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
previous=p/'skater-looping-sound-startup-checkpoint.json';prior=read(previous);target=p/'skater-startup-tail-checkpoint.json';assert not target.exists()
assert sha(previous)=='04d3ca79ae3a694a4e61eb9d80d56e41eef69b31ee6cffa3ebb4941bb2d674b4'
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
w=p/'skater-startup-tail-parent-draft.wasm';b=read(w.with_suffix('.build.json'));assert sha(w)==b['sha256']
for name,digest in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==digest,name
assert b['source_hashes']==prior['source_hashes']
expected=read(p/'skater-startup-tail-node-all.json');proof=read(p/'skater-startup-tail-browser.json');old=read(p/'skater-looping-sound-browser.json')['observed']['suites'];suites=expected['suites']
assert expected['wasm_sha256']==sha(w) and expected['wasm_bytes']==w.stat().st_size and expected['runtime_imports']==0
assert len(suites)==195 and len(old)==193 and all(v['result']=='pass' for v in suites.values())
for name,value in old.items():assert suites[name]==value,name
assert proof['observed']==expected and proof['status'].startswith('PASS') and 'Chrome/154.' in proof['user_agent']
canonical=json.dumps(expected,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert proof['rendered_dom_fingerprint']=={'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(expected)}
original=read(p/'skater-startup-tail-original.json');unit=suites['skater_startup_tail'];fixture=read(p/'skater-startup-tail-fixtures.json');routines=read(p/'skater-startup-tail-routines.json');extents=read(p/'skater-startup-tail-extents.json')
assert original['cases']==unit['cases']==367 and original['calls']==unit['calls']==733 and original['counts']==unit['counts']
assert unit['startup_diagnostic_callbacks']==455 and unit['nan_fields_classification_only']==0 and not fixture['float_fields']
assert extents['result']=='pass' and extents['routines_sha256']==sha(p/'skater-startup-tail-routines.json') and extents['new_complete_body_bytes']==2145
addresses={}
for at,row in routines.items():
 cov=original['instruction_coverage'][at];assert cov['total']==row['instructions']
 if at=='0x51acb0':assert cov['covered']==40 and cov['total']==41 and cov['missing']==['0x51accd'] and extents['unreachable_alignment']['bytes']==3
 else:assert cov['covered']==cov['total'] and not cov['missing'] and not cov['excluded']
 assert original['counts'][row['name']]>0
 addresses[at]={**row,'original_evidence':'skater-startup-tail-original.json','node_evidence':'skater-startup-tail-regression-skater-startup-tail-result.json','browser_suite':'skater_startup_tail'}
assert len(addresses)==17 and sum(x['bytes'] for x in addresses.values())==2225
assert sum(x['covered'] for x in original['instruction_coverage'].values())==607 and sum(x['total'] for x in original['instruction_coverage'].values())==608
for case in fixture['cases']:
 for step in case['steps']:assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','quiet_double_fields','global_quiet_float_indices','global_bit_masks','float_fields','global_float_indices','indeterminate_words','indeterminate_bytes','compression_records'])
partial=read(p/'skater-startup-tail-parent-original.json')['partial_constructor'];assert (partial['covered'],partial['total'],partial['interrupted_calls'],partial['counted_complete'])==(424,463,80,False)
assert all(row['next_type']=='0x5b512edc' and row['overrides'] for row in partial['records'])
assert suites['skater_startup_tail_parent']['startup_diagnostic_callbacks']==200
negative=read(p/'skater-startup-tail-negative.json');assert negative['result']=='pass' and all(x['rejected'] for x in negative['controls'].values())
base_report=p/'startup-tail-reporting-baseline-report.json';assert not base_report.exists();base_report.write_bytes((r/'progress/report.json').read_bytes());assert sha(base_report)=='c5c9991c000e663086afa4bc47347cc8a8002aa777ee7517417d4d19208d75da'
paths={previous,p/'skater-looping-sound-startup-audit.json',base_report}
for pattern in ['skater-startup-tail*','build-skater-startup-tail*','probe-skater-startup-tail*','verify-skater-startup-tail*','skater-final-components*','skater-final-51c670*','skater-final-51d890*','skater-1859f772-next-*','skater-1859f772-extra-*']:
 paths.update(f for f in p.glob(pattern) if f.is_file() and f.name not in ['skater-startup-tail-pin.log','skater-startup-tail-audit.log'])
for name in ['serve-skater-startup-tail.py','pin-skater-startup-tail.py','audit-skater-startup-tail.py','inspect-skater-final-components.py']:paths.add(p/name)
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
for f in paths:
 assert f.is_file(),f;artifacts[str(f.relative_to(r))]=sha(f)
 if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
c={'schema':3,'result':'original comparisons, Node and actual Chromium pass; unpromoted','specimen_sha256':original['specimen_sha256'],'prior_checkpoint':str(previous.relative_to(r)),'prior_checkpoint_sha256':sha(previous),'wasm':str(w.relative_to(r)),'wasm_sha256':sha(w),'wasm_bytes':w.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],'source_hashes':b['source_hashes'],'draft_source_hashes':b['draft_source_hashes'],'platform_source_hashes':prior['platform_source_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),'browser_suites':195,'preserved_browser_suites':193,'browser_dom_fingerprint':proof['rendered_dom_fingerprint'],'new_functions':17,'original_addresses':addresses,'verified_scoped_addresses_from_prior':{**prior['verified_scoped_addresses_from_prior'],**prior['original_addresses']},'new_verified_linear_bytes':2225,'new_complete_body_bytes':2145,'instruction_coverage':original['instruction_coverage'],'new_cases':367,'new_completed_calls':733,'new_diagnostic_callbacks':455,'constructor_prefix':{'address':'0x582d90','covered':424,'total':463,'interrupted_calls':80,'next_local_type':'0x5b512edc','next_remote_type':'0x5b512edc','counted_complete':False},'unsupported_routes':prior['unsupported_routes']+['Nine new component types have startup only; unverified dispose/frame/finalization/commands trap','Tag/sticker5b512edc texture cloning and final d1515392 allocation/lifecycle remain unfinished'],'public_report_at_verification':{'path':str(base_report.relative_to(r)),'sha256':sha(base_report)},'scope':'Seventeen complete original startup routines for nine remaining component types, including StatsManager, StateHistory and nonlocal net logic. 367 cases/733 calls compare607 reachable instructions; the only omitted instruction is a provably unreachable three-byte self-LEA. 455 native diagnostics cover sticky flag and live difficulty reload. Both wrong controls are rejected. The511780 inline ID span98bytes receives only21bytes original Ghidra body credit. Shared functions/adapters receive zero new address credit. All193 prior Node/Chromium result objects remain unchanged. Constructor582d90 reaches424/463 in80 interrupted local/remote calls and receives zero recovery credit. Startup texture cloning, component frames, asset integration, rendering and a playable level remain unfinished.','publishing':prior['publishing'],'playable':False}
target.write_text(json.dumps(c,indent=2)+'\n');print('Pinned startup tail:',len(artifacts),'artifacts;195 suites;17 verified routines;',sha(target))
