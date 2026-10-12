"""Pin complete BalanceTrick lifecycle and partial startup; preserve all predecessors."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';read=lambda f:json.loads(f.read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
previous=p/'skater-descriptor-checkpoint.json';prior=read(previous);target=p/'skater-balance-startup-checkpoint.json';assert not target.exists()
assert sha(previous)=='c70bc9171a993e557ae353f7feae08721295111f88cf7e2ac8f644aae349df32'
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
w=p/'skater-balance-startup-draft.wasm';b=read(w.with_suffix('.build.json'));assert sha(w)==b['sha256']=='ebd901c3889d6aeb9da3f9f103d77221a345e64cbd3fa8bdd57f7af57a5f9068'
for name,digest in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==digest,name
assert b['source_hashes']==prior['source_hashes']
expected=read(p/'skater-balance-node-all.json');proof=read(p/'skater-balance-browser.json');old=read(p/'skater-descriptor-browser.json')['observed']['suites'];suites=expected['suites']
assert expected['wasm_sha256']==sha(w) and expected['wasm_bytes']==w.stat().st_size and expected['runtime_imports']==0
assert len(suites)==191 and len(old)==189 and all(v['result']=='pass' for v in suites.values())
for name,value in old.items():assert suites[name]==value,name
assert proof['observed']==expected and proof['status'].startswith('PASS') and 'Chrome/154.' in proof['user_agent']
canonical=json.dumps(expected,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert proof['rendered_dom_fingerprint']=={'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(expected)}
original=read(p/'skater-balance-lifecycle-original.json');unit=suites['skater_balance_lifecycle'];fixture=read(p/'skater-balance-lifecycle-fixtures.json');routines=read(p/'skater-balance-lifecycle-routines.json');extents=read(p/'skater-balance-lifecycle-extents.json')
assert original['cases']==unit['cases']==115 and original['calls']==unit['calls']==328 and original['counts']==unit['counts']
assert unit['virtual_wait_callbacks']==28 and unit['nan_fields_classification_only']==0 and not fixture['float_fields']
assert extents['result']=='pass' and extents['routines_sha256']==sha(p/'skater-balance-lifecycle-routines.json')
addresses={}
for at,row in routines.items():
 cov=original['instruction_coverage'][at];assert cov['covered']==cov['total']==row['instructions'] and not cov['missing'] and not cov['excluded']
 assert original['counts'][row['name']]>0
 addresses[at]={**row,'original_evidence':'skater-balance-lifecycle-original.json','node_evidence':'skater-balance-lifecycle-unit.json','browser_suite':'skater_balance_lifecycle'}
assert len(addresses)==10 and sum(x['bytes'] for x in addresses.values())==657 and sum(x['total'] for x in original['instruction_coverage'].values())==185
for case in fixture['cases']:
 for step in case['steps']:assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','quiet_double_fields','global_quiet_float_indices','global_bit_masks','float_fields','global_float_indices','indeterminate_words','indeterminate_bytes','compression_records'])
partial=read(p/'skater-balance-startup-original.json')['partial_constructor'];assert (partial['covered'],partial['total'],partial['interrupted_calls'],partial['counted_complete'])==(301,463,32,False)
assert all(row['next_type']==('0xb5f1e9d2' if row['arguments'][2]&255 else '0x850eef66') for row in partial['records'])
negative=read(p/'skater-balance-lifecycle-negative.json');assert negative['result']=='pass' and negative['missing_conditional_qb_rejected']
base_report=p/'reporting-baseline-report.json';assert not base_report.exists();base_report.write_bytes((r/'progress/report.json').read_bytes());assert sha(base_report)==prior['public_report_sha256']
paths={previous,p/'skater-descriptor-audit.json',base_report,p/'balance-construction-callback.c',p/'balance-construction-callback.wasm'}
for pattern in ['skater-balance*','balance-lifecycle-extra-*','end-run-report-extra-*','build-skater-balance*','probe-skater-balance*','verify-skater-balance*']:
 paths.update(f for f in p.glob(pattern) if f.is_file() and f.name not in ['skater-balance-startup-pin.log','skater-balance-startup-audit.log'])
for name in ['serve-skater-balance.py','pin-skater-balance-startup.py','audit-skater-balance-startup.py']:paths.add(p/name)
for name in ['skater-base-descriptor','skater-local-net','skater-end-run-lifecycle','skater-end-run-startup']:paths.add(p/(name+'-balance-candidate-unit.json'))
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
for f in paths:
 assert f.is_file(),f
 artifacts[str(f.relative_to(r))]=sha(f)
 if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
c={'schema':3,'result':'original comparisons, Node and actual Chromium pass; unpromoted','specimen_sha256':original['specimen_sha256'],'prior_checkpoint':str(previous.relative_to(r)),'prior_checkpoint_sha256':sha(previous),'wasm':str(w.relative_to(r)),'wasm_sha256':sha(w),'wasm_bytes':w.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],'source_hashes':b['source_hashes'],'draft_source_hashes':b['draft_source_hashes'],'platform_source_hashes':prior['platform_source_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),'browser_suites':191,'preserved_browser_suites':189,'browser_dom_fingerprint':proof['rendered_dom_fingerprint'],'new_functions':10,'original_addresses':addresses,'verified_scoped_addresses_from_prior':prior['verified_scoped_addresses_from_prior'],'new_verified_linear_bytes':657,'instruction_coverage':original['instruction_coverage'],'new_cases':115,'new_completed_calls':328,'new_script_callbacks':28,'constructor_prefix':{'address':'0x582d90','covered':301,'total':463,'interrupted_calls':32,'next_local_type':'0xb5f1e9d2','next_remote_type':'0x850eef66','counted_complete':False},'unsupported_routes':prior['unsupported_routes']+['BalanceTrick checksum4f9420 explicitly traps; later constructor components remain unfinished'],'public_report_at_verification':{'path':str(base_report.relative_to(r)),'sha256':sha(base_report)},'scope':'Ten complete original routines recover BalanceTrick and embedded record lifecycle and dependency binding. Conditional real QB runs before selected zero writes; 28 native fixture callbacks test mutation and order. 115 cases/328 completed calls cover all185 original instructions with no added comparison allowances. Missing-QB control rejected. All189 prior Node/Chromium results unchanged. Shared update51b970 receives no additional credit. Constructor582d90 advances301/463 and remains partial with zero credit. Rendering and playable level remain unfinished.','publishing':'Direct publication of verified source and metadata authorized; retired chat and its publishing automation remain paused. Original specimen, assets, raw fixtures and compiled game modules remain private.','playable':False}
target.write_text(json.dumps(c,indent=2)+'\n');print('Pinned BalanceTrick:',len(artifacts),'artifacts;191 suites;10 verified routines;',sha(target))
