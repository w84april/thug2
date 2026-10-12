"""Read-only audit of bounded channel startup and the unchanged predecessor."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';read=lambda f:json.loads(f.read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
f=p/'animation-clip-startup-v4-checkpoint.json';c=read(f);prior=read(r/c['prior_checkpoint']);assert sha(r/c['prior_checkpoint'])==c['prior_checkpoint_sha256']
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for n,h in c[group].items():assert sha(r/n)==h,(group,n)
 for n,h in prior[group].items():assert c[group][n]==h,(group,n)
for n,h in {**c['draft_source_hashes'],**c['derived_from']}.items():assert sha(r/n)==h,n
assert sha(r/c['wasm'])==c['wasm_sha256'] and sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']
assert (c['new_functions'],c['verified_mappings'],c['new_complete_body_bytes'],c['browser_suites'],c['preserved_browser_suites'])==(2,2,1467,209,208) and not c['playable'] and c['verified_scoped_addresses_from_prior']=={}
expected=read(p/'animation-clip-startup-v4-node-all.json');proof=read(p/'animation-clip-startup-v4-browser-full.json');assert proof['observed']==expected and proof['status'].startswith('PASS')
for n,v in read(p/'animation-channel-startup-v3-browser-full.json')['observed']['suites'].items():assert expected['suites'][n]==v,n
original=read(p/'animation-clip-startup-v4-original.json');coverage=original['instruction_coverage'];assert sum(v['covered'] for v in coverage.values())==433 and sum(v['total'] for v in coverage.values())==450
assert sum(len(v['excluded']) for v in coverage.values())==17
report={'result':'pass','checkpoint_sha256':sha(f),'preserved_checkpoint_sha256':c['prior_checkpoint_sha256'],'artifacts':len(c['artifact_hashes']),'preserved_artifacts':len(prior['artifact_hashes']),'new_unique_addresses':2,'selected_mappings':2,'new_complete_body_bytes':1467,'cases':256,'calls':2264,'covered_instructions':433,'linear_instructions':450,'allocation_fault_exclusions':9,'cold_bootstrap_exclusions':7,'unreachable_stable_pool_membership_exclusions':1,'browser_suites':209,'preserved_browser_suites':208,'numeric_allowances':0,'checker_changes':0,'resolved_partial_addresses':[],'selection_is_additional':True,'rendering_preview_credit':0,'main_wasm_unchanged':True,'playable':False}
target=p/'animation-clip-startup-v4-audit.json';assert not target.exists();target.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
