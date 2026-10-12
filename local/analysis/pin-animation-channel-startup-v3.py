"""Pin bounded original channel creation and its complete browser regression."""
import csv,hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';read=lambda f:json.loads(f.read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
name='animation-channel-startup-v3';previous=p/'camera-composite-startup-v4-checkpoint.json';prior=read(previous)
assert sha(previous)=='8c382ec405914b04f7493ea39ae251e578573f8e2ca6caed44374b5a91c455eb'
audit=p/'camera-composite-startup-v4-audit.json';assert read(audit)['result']=='pass' and read(audit)['checkpoint_sha256']==sha(previous)
target=p/(name+'-checkpoint.json');assert not target.exists()
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for n,h in prior[group].items():assert sha(r/n)==h,(group,n)
w=p/'animation-channel-startup-v2.wasm';b=read(w.with_suffix('.build.json'));assert sha(w)==b['sha256']=='d327df30dad485725bf4ffe36e9e95511b0459f838342ff1c45725a391a26ece'
for n,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/n)==h,n
expected=read(p/(name+'-node-all.json'));proof=read(p/(name+'-browser-full.json'));old=read(p/'camera-composite-startup-v3-browser-full.json')['observed']['suites']
assert len(expected['suites'])==208 and len(old)==207
assert proof['observed']==expected and proof['status'].startswith('PASS') and 'Chrome/154.' in proof['user_agent']
assert expected['wasm_sha256']==sha(w) and expected['wasm_bytes']==w.stat().st_size and expected['runtime_imports']==0
for n,v in old.items():assert expected['suites'][n]==v,n
assert all(v['result']=='pass' for v in expected['suites'].values())
canonical=json.dumps(expected,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert proof['rendered_dom_fingerprint']=={'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(expected)}
original=read(p/(name+'-original.json'));unit=expected['suites']['animation_channel_startup_v3'];fixture=read(p/(name+'-fixtures.json'));routines=read(p/(name+'-routines.json'))
assert original['cases']==unit['cases']==295 and original['calls']==unit['calls']==828 and original['counts']==unit['counts']
assert unit['nan_fields_classification_only']==0 and unit['startup_diagnostic_callbacks']==0 and not fixture['float_fields']
spec={'0x481ee0':(56,16,15,'0x481efe'),'0x481990':(12,5,5,None),'0x481b40':(55,16,16,None),'0x47de20':(293,117,116,'0x47df29')};assert set(routines)==set(spec)
for a,(size,total,covered,excluded) in spec.items():
 assert (routines[a]['bytes'],routines[a]['instructions'])==(size,total)
 cov=original['instruction_coverage'][a];assert (cov['covered'],cov['total'])==(covered,total)
 assert cov['missing']==([excluded] if excluded else []) and set(cov['excluded'])==({excluded} if excluded else set())
selected={int(row['address'],16) for row in read(r/'progress/ledger.json')['records']};assert not selected&{int(a,16) for a in spec}
extra=p/'animation-channel-startup-v2-ranges.tsv';rows={hex(int(row['address'],16)):row for row in csv.DictReader(extra.open(),delimiter='\t')};assert set(rows)==set(spec)
for a,v in rows.items():assert int(v['body_bytes'])==spec[a][0]
for case in fixture['cases']:
 for step in case['steps']:assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','quiet_double_fields','global_quiet_float_indices','global_bit_masks','float_fields','global_float_indices','indeterminate_words','indeterminate_bytes','compression_records'])
baseline=p/(name+'-reporting-baseline-report.json');behavior=p/(name+'-reporting-baseline-behavioral.json');assert not baseline.exists() and not behavior.exists()
baseline.write_bytes((r/'progress/report.json').read_bytes());behavior.write_bytes((r/'progress/behavioral-recovery.json').read_bytes())
assert int(read(baseline)['measures']['complete_code'])==0 and int(read(baseline)['measures']['matched_code'])==406
paths={previous,audit,baseline,behavior}
for pattern in ['animation-channel-startup-v*','build-animation-channel-startup-v*','probe-animation-channel-startup-v*','verify-animation-channel-startup-v*','serve-animation-channel-startup-v*','pin-animation-channel-startup-v*','audit-animation-channel-startup-v*']:
 paths.update(f for f in p.glob(pattern) if f.is_file())
paths.update(f for f in r.glob('local/build/animation-channel-startup-v*.log') if f.is_file())
for dirname in ['animation-channel-startup-v1-ghidra','animation-channel-startup-v2-ghidra']:
 paths.update(f for f in (p/dirname).rglob('*') if f.is_file())
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
for f in paths:
 artifacts[str(f.relative_to(r))]=sha(f)
 if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
for suffix in ['-routines.json','-original.json','-fixtures.json','-browser-full.json','-node-all.json','-regression-'+name+'-result.json']:
 assert str((p/(name+suffix)).relative_to(r)) in artifacts,suffix
addresses={a:{**row,'body_bytes':row['bytes'],'ranges':rows[a]['ranges'],'original_evidence':name+'-original.json','node_evidence':name+'-regression-'+name+'-result.json','browser_suite':'animation_channel_startup_v3'} for a,row in routines.items()}
c={'schema':3,'result':'original comparisons, Node and actual Chromium pass; unpromoted','specimen_sha256':prior['specimen_sha256'],'prior_checkpoint':str(previous.relative_to(r)),'prior_checkpoint_sha256':sha(previous),'prior_engine_checkpoint':str(previous.relative_to(r)),'prior_engine_checkpoint_sha256':sha(previous),'wasm':str(w.relative_to(r)),'wasm_sha256':sha(w),'wasm_bytes':w.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],'source_hashes':b['source_hashes'],'draft_source_hashes':b['draft_source_hashes'],'derived_from':b['derived_from'],'platform_source_hashes':prior['platform_source_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),'browser_suites':208,'preserved_browser_suites':207,'browser_dom_fingerprint':proof['rendered_dom_fingerprint'],'new_functions':4,'verified_mappings':4,'tested_direct_exports':4,'original_addresses':addresses,'verified_scoped_addresses_from_prior':{},'selection_policy':'Four complete routines contribute416 unique original body bytes under initialized allocator and valid channel graph contracts. Only literal cold allocator bootstrap481efe and the internal allocation-null instruction47df29 whose unchecked subsequent write faults are excluded. Direct allocation-wrapper failure compares. Reused channel constructor/destructor/free/event callees receive no repeated credit. No clip, full Animation/profile startup or gameplay claim.','new_complete_body_bytes':416,'new_verified_linear_bytes':416,'new_cases':295,'new_completed_calls':828,'original_covered_instructions':152,'original_linear_instructions':154,'public_report_at_verification':{'path':str(baseline.relative_to(r)),'sha256':sha(baseline)},'behavioral_report_at_verification':{'path':str(behavior.relative_to(r)),'sha256':sha(behavior)},'unsupported_routes':['Clip startup4823c0, full Animation419dd0/480410/47f260, profile581850, full camera frame, gameplay controls and rendered skater remain unfinished.','Root internal allocation failure is unchecked and faults in the original; only the standalone allocator failure route is supported.'],'scope':original['scope']+' All208 Node/actualChromium suites pass and all207 predecessor result objects remain unchanged. Four unique addresses416bytes;152/154instructions with two explicit scoped exclusions. Failed sentinel fixture and header-offset draft remain private and unselected; corrected source follows original+5c duration/+60 weight. No fixture/checker/numeric changes to make a failed port pass.','publishing':prior['publishing'],'playable':False}
target.write_text(json.dumps(c,indent=2)+'\n');print('Pinned',len(artifacts),'artifacts;208 suites;4 new addresses/416bytes;',sha(target))
