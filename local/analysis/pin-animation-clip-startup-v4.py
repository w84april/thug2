"""Pin bounded original channel creation and its complete browser regression."""
import csv,hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';read=lambda f:json.loads(f.read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
name='animation-clip-startup-v4';previous=p/'animation-channel-startup-v3-checkpoint.json';prior=read(previous)
assert sha(previous)=='6788149d9d5e5d69d692ae3d8138de9c8b60d9f64b25adcb2521260273a71474'
audit=p/'animation-channel-startup-v3-audit.json';assert read(audit)['result']=='pass' and read(audit)['checkpoint_sha256']==sha(previous)
target=p/(name+'-checkpoint.json');assert not target.exists()
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for n,h in prior[group].items():assert sha(r/n)==h,(group,n)
w=p/'animation-clip-startup-v3.wasm';b=read(w.with_suffix('.build.json'));assert sha(w)==b['sha256']=='d7cab34f4ab96a68deb3907dc36e9c282aabcadd2d5b1a8c0a3428fed9b567f8'
for n,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/n)==h,n
expected=read(p/(name+'-node-all.json'));proof=read(p/(name+'-browser-full.json'));old=read(p/'animation-channel-startup-v3-browser-full.json')['observed']['suites']
assert len(expected['suites'])==209 and len(old)==208
assert proof['observed']==expected and proof['status'].startswith('PASS') and 'Chrome/154.' in proof['user_agent']
assert expected['wasm_sha256']==sha(w) and expected['wasm_bytes']==w.stat().st_size and expected['runtime_imports']==0
for n,v in old.items():assert expected['suites'][n]==v,n
assert all(v['result']=='pass' for v in expected['suites'].values())
canonical=json.dumps(expected,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert proof['rendered_dom_fingerprint']=={'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(expected)}
original=read(p/(name+'-original.json'));unit=expected['suites']['animation_clip_startup_v4'];fixture=read(p/(name+'-fixtures.json'));routines=read(p/(name+'-routines.json'))
assert original['cases']==unit['cases']==256 and original['calls']==unit['calls']==2264 and original['counts']==unit['counts']
assert unit['nan_fields_classification_only']==0 and unit['instrumented_native_event_callbacks']==0 and not fixture['float_fields']
spec={'0x4823c0':(1442,441,424),'0x4616f0':(25,9,9)};assert set(routines)==set(spec)
for a,(size,total,covered) in spec.items():
 assert (routines[a]['bytes'],routines[a]['instructions'])==(size,total)
 cov=original['instruction_coverage'][a];assert (cov['covered'],cov['total'])==(covered,total)
 assert set(cov['missing'])==set(cov['excluded']) and len(cov['excluded'])==total-covered
assert set(original['instruction_coverage']['0x4823c0']['excluded'])=={'0x482451','0x482482','0x482484','0x482489','0x4824ac','0x4824dc','0x482588','0x4825b8','0x48262e','0x48265e','0x4826c2','0x4826f2','0x48275b','0x48278b','0x4827f5','0x482826','0x482922'}
selected={int(row['address'],16) for row in read(r/'progress/ledger.json')['records']};assert not selected&{int(a,16) for a in spec}
extra=p/'animation-clip-startup-v1-ranges.tsv';rows={hex(int(row['address'],16)):row for row in csv.DictReader(extra.open(),delimiter='\t')};assert set(rows)==set(spec)
for a,v in rows.items():assert int(v['body_bytes'])==spec[a][0]
for case in fixture['cases']:
 for step in case['steps']:assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','quiet_double_fields','global_quiet_float_indices','global_bit_masks','float_fields','global_float_indices','indeterminate_words','indeterminate_bytes','compression_records'])
baseline=p/(name+'-reporting-baseline-report.json');behavior=p/(name+'-reporting-baseline-behavioral.json');assert not baseline.exists() and not behavior.exists()
baseline.write_bytes((r/'progress/report.json').read_bytes());behavior.write_bytes((r/'progress/behavioral-recovery.json').read_bytes())
assert int(read(baseline)['measures']['complete_code'])==0 and int(read(baseline)['measures']['matched_code'])==406
paths={previous,audit,baseline,behavior}
for n,h in original['input_hashes'].items():assert sha(r/n)==h,n;paths.add(r/n)
asset_proof=read(p/'animation-default-asset-v1-verification.json');assert asset_proof['result']=='pass' and asset_proof['decoded_bytes']==400 and asset_proof['archive_decode_equal_extracted']
paths.update(f for f in p.glob('animation-default-asset-v*') if f.is_file())
for pattern in ['animation-clip-startup-v*','build-animation-clip-startup-v*','probe-animation-clip-startup-v*','verify-animation-clip-startup-v*','serve-animation-clip-startup-v*','pin-animation-clip-startup-v*','audit-animation-clip-startup-v*']:
 paths.update(f for f in p.glob(pattern) if f.is_file())
paths.update(f for f in r.glob('local/build/animation-clip-startup-v*.log') if f.is_file())
paths.update(f for f in (p/'animation-clip-startup-v1-ghidra').rglob('*') if f.is_file())
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
for f in paths:
 artifacts[str(f.relative_to(r))]=sha(f)
 if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
for suffix in ['-routines.json','-original.json','-fixtures.json','-browser-full.json','-node-all.json','-regression-'+name+'-result.json']:
 assert str((p/(name+suffix)).relative_to(r)) in artifacts,suffix
addresses={a:{**row,'body_bytes':row['bytes'],'ranges':rows[a]['ranges'],'original_evidence':name+'-original.json','node_evidence':name+'-regression-'+name+'-result.json','browser_suite':'animation_clip_startup_v4'} for a,row in routines.items()}
c={'schema':3,'result':'original comparisons, Node and actual Chromium pass; unpromoted','specimen_sha256':prior['specimen_sha256'],'prior_checkpoint':str(previous.relative_to(r)),'prior_checkpoint_sha256':sha(previous),'prior_engine_checkpoint':str(previous.relative_to(r)),'prior_engine_checkpoint_sha256':sha(previous),'wasm':str(w.relative_to(r)),'wasm_sha256':sha(w),'wasm_bytes':w.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],'source_hashes':b['source_hashes'],'draft_source_hashes':b['draft_source_hashes'],'derived_from':b['derived_from'],'platform_source_hashes':prior['platform_source_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),'browser_suites':209,'preserved_browser_suites':208,'browser_dom_fingerprint':proof['rendered_dom_fingerprint'],'new_functions':2,'verified_mappings':2,'tested_direct_exports':7,'original_addresses':addresses,'verified_scoped_addresses_from_prior':{},'selection_policy':'Two complete bounded routines contribute1467 unique body bytes. Seven literal cold-bootstrap calls, nine required temporary-allocation-null instructions and one unreachable failed selected-pool membership instruction are excluded under initialized successful allocation and stable valid pool ownership. Caller-owned live parameters, assets and up to six controllers required; helpers and native/platform adapters earn no repeated or matching credit.','new_complete_body_bytes':1467,'new_verified_linear_bytes':1467,'new_cases':256,'new_completed_calls':2264,'original_covered_instructions':433,'original_linear_instructions':450,'public_report_at_verification':{'path':str(baseline.relative_to(r)),'sha256':sha(baseline)},'behavioral_report_at_verification':{'path':str(behavior.relative_to(r)),'sha256':sha(behavior)},'unsupported_routes':['Full Animation419dd0/480410/47f260 and preparation47f000, profile581850, pose rendering, controls and gameplay remain unfinished. The real Default clip is loaded and directly invoked; original asset registration/bootstrap scheduling is not verified.','Cold allocators, required temporary-allocation failure, invalid ownership and allocator mutation during controller dispatch are unsupported.'],'scope':original['scope']+' All209 Node/actualChromium suites pass; all208 predecessor result objects unchanged. Two new addresses1467bytes;433/450instructions with17 explicit scoped exclusions. Earlier field-offset draft, optional-secondary error and failed compile remain private/unselected. Original fixture and checker unchanged when correcting source. The earlier dummy label was inaccurate: checksum1ca1ff20 is Default, whose400B archive decode equals the extracted file.','publishing':prior['publishing'],'playable':False}
target.write_text(json.dumps(c,indent=2)+'\n');print('Pinned',len(artifacts),'artifacts;209 suites;2 new addresses/1467bytes;',sha(target))
