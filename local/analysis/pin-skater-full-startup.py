"""Immutable pin for texture cloning and the scoped complete skater constructor."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';read=lambda f:json.loads(f.read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
previous=p/'skater-startup-tail-checkpoint.json';prior=read(previous);target=p/'skater-full-startup-checkpoint.json';assert not target.exists();assert sha(previous)=='d0f1582b51698813701109db92a1cba04ac82e9c80285f6e79a1f661911ae1cf'
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,h in prior[group].items():assert sha(r/name)==h,(group,name)
w=p/'skater-full-startup-draft.wasm';b=read(w.with_suffix('.build.json'));assert sha(w)==b['sha256'];assert b['source_hashes']==prior['source_hashes']
for name,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==h,name
expected=read(p/'skater-full-startup-node-all.json');proof=read(p/'skater-full-startup-browser.json');old=read(p/'skater-startup-tail-browser.json')['observed']['suites'];suites=expected['suites'];assert len(suites)==198 and len(old)==195
assert expected['wasm_sha256']==sha(w) and expected['runtime_imports']==0 and expected['wasm_bytes']==w.stat().st_size
assert all(v['result']=='pass' for v in suites.values())
for name,value in old.items():assert suites[name]==value,name
assert proof['observed']==expected and proof['status'].startswith('PASS') and 'Chrome/154.' in proof['user_agent']
canonical=json.dumps(expected,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert proof['rendered_dom_fingerprint']=={'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(expected)}
addresses={};cases=calls=covered=total=0
for name in ['skater-tag-texture','skater-final-startup','skater-full-startup']:
 original=read(p/(name+'-original.json'));unit=suites[name.replace('-','_')];fixture=read(p/(name+'-fixtures.json'));routines=read(p/(name+'-routines.json'))
 assert original['cases']==unit['cases'] and original['calls']==unit['calls'] and original['counts']==unit['counts']
 assert unit['nan_fields_classification_only']==0 and not fixture['float_fields']
 cases+=unit['cases'];calls+=unit['calls']
 for at,row in routines.items():
  cov=original['instruction_coverage'][at];assert cov['total']==row['instructions'];assert set(cov['missing'])==set(cov['excluded']);assert original['counts'][row['name']]>0
  addresses[at]={**row,'original_evidence':name+'-original.json','node_evidence':'skater-full-startup-regression-'+name+'-result.json','browser_suite':name.replace('-','_')};covered+=cov['covered'];total+=cov['total']
 for case in fixture['cases']:
  for step in case['steps']:assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','quiet_double_fields','global_quiet_float_indices','global_bit_masks','float_fields','global_float_indices','indeterminate_words','indeterminate_bytes','compression_records'])
extents=read(p/'skater-full-startup-extents.json');assert extents['result']=='pass' and extents['selected_mappings']==22 and extents['new_unique_addresses']==21 and extents['new_complete_body_bytes']==4093
assert (cases,calls,covered,total)==(332,412,1280,1296)
root=read(p/'skater-full-startup-original.json')['complete_constructor'];assert root['returned_calls']==80
assert all(x['returned_this'] and x['texture_copies_equal'] and x['temporary_scope_restored'] for x in root['records'])
assert sum(x['structure_pool_selected'] for x in root['records'])==40
assert suites['skater_full_startup']['startup_diagnostic_callbacks']==200
negative=read(p/'skater-tag-texture-negative.json');assert negative['result']=='pass' and len(negative['controls'])==2 and all(v['rejected'] for v in negative['controls'].values())
base=p/'full-startup-reporting-baseline-report.json';assert not base.exists();base.write_bytes((r/'progress/report.json').read_bytes());assert sha(base)=='709608f73af0c37b343635e647dcfdb9c0757d451d9e98a35b9552c45034ad35'
paths={previous,p/'skater-startup-tail-audit.json',base}
for pattern in ['skater-tag-*','skater-final-startup*','skater-full-startup*','skater-full-constructor*','build-skater-tag-*','build-skater-full-startup*','probe-skater-tag-*','probe-skater-final-startup*','probe-skater-full-startup*','verify-skater-tag-*','verify-skater-final-startup*','verify-skater-full-startup*']:
 paths.update(f for f in p.glob(pattern) if f.is_file() and f.suffix!='.log')
for name in ['serve-skater-full-startup.py','pin-skater-full-startup.py','audit-skater-full-startup.py']:paths.add(p/name)
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
for f in paths:
 assert f.is_file(),f;artifacts[str(f.relative_to(r))]=sha(f)
 if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
resolution={'completed_calls':80,'expected_traps':0,'returned_this':True,'temporary_cleanup_verified':True}
unsupported=['LocalNet network frame5136c0 and serializer5131a0 remain unverified','EndRun frame/network/events/settings deferred paths remain unverified','EndRun gate553460 missing required boolean traps explicitly','BalanceTrick checksum4f9420 remains unverified','SkaterLoopingSound frame513bb0, command5139e0 and registration513860 remain unverified','Other component finalization, frames, destruction and commands retain explicit unknown-method traps','Tag/sticker component disposal/commands and d1515392 disposal/checksum remain unverified','Cold process startup, integrated level/frame/rendering and original playable level remain unfinished; GPU fixtures only record storage operations']
c={'schema':3,'result':'original comparisons, Node and actual Chromium pass; unpromoted','specimen_sha256':prior['specimen_sha256'],'prior_checkpoint':str(previous.relative_to(r)),'prior_checkpoint_sha256':sha(previous),'wasm':str(w.relative_to(r)),'wasm_sha256':sha(w),'wasm_bytes':w.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],'source_hashes':b['source_hashes'],'draft_source_hashes':b['draft_source_hashes'],'platform_source_hashes':prior['platform_source_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),'browser_suites':198,'preserved_browser_suites':195,'browser_dom_fingerprint':proof['rendered_dom_fingerprint'],'verified_mappings':22,'new_functions':21,'shared_original_addresses':['0x49f3b0'],'original_addresses':addresses,'verified_scoped_addresses_from_prior':{**prior['verified_scoped_addresses_from_prior'],**prior['original_addresses']},'new_verified_linear_bytes':4110,'selected_complete_body_bytes':4101,'new_complete_body_bytes':4093,'new_cases':332,'new_completed_calls':412,'original_covered_instructions':1280,'original_linear_instructions':1296,'partial_resolutions':{'0x582d90':resolution},'unsupported_routes':unsupported,'public_report_at_verification':{'path':str(base.relative_to(r)),'sha256':sha(base)},'scope':'Twenty-one new unique original addresses (4093 conservative body bytes), plus shared49f3b0 with zero additional credit. 332 cases/412 calls compare1280/1296 scoped instructions. Sixteen exclusions cover initialized allocator bootstrap, unchecked allocation-fault paths and nine-byte unreachable alignment. Two wrong controls are rejected. All198 Node/actual Chromium suites pass and all195 predecessor result objects are unchanged. Complete582d90 returnsTHIS in80 original local/remote calls (40 pooled), verifies actual tag/sticker RGBA copies and temporary structure cleanup. Historical partial status is explicitly resolved by this audited proof; old checkpoints remain immutable. Complete component finalization/frames, cold startup, integrated rendering and a playable level remain unfinished.','publishing':prior['publishing'],'playable':False}
target.write_text(json.dumps(c,indent=2)+'\n');print('Pinned',len(artifacts),'artifacts;198 suites;21 new unique addresses;',sha(target))
