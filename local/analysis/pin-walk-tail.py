"""Pin walking camera and collision recovery after original, Node and Chromium comparisons."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
prior_path=p/'walk-common-checkpoint.json';assert sha(prior_path)=='4613fa86bd247e2332cb5e0bf21f48a990ae529662aeaae2953b312064a09d17'
prior=read(prior_path);target=p/'walk-tail-checkpoint.json';assert not target.exists()
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
b=read(p/'walk-tail-draft.build.json');module=p/'walk-tail-draft.wasm'
assert sha(module)==b['sha256']=='ab43b19073bd5c3a4a4de8121fd87454631e5b0546421ee682f63a73a67ec3d4'
assert module.stat().st_size==897757 and b['source_hashes']==prior['source_hashes']
for name,digest in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==digest,name
previous=read(p/'walk-common-browser.json')['observed']['suites']
suites={name:read(p/('walk-tail-checkpoint-'+name.replace('_','-')+'-result.json')) for name in ['walk_tail','walk_camera','walk_critical',*previous]}
assert len(suites)==158
for name,result in suites.items():
 assert result['result']=='pass',name
 if name in previous:assert result==previous[name],name
families=['walk-tail','walk-camera','walk-critical']
originals={n:read(p/(n+'-original.json')) for n in families};fixtures={n:read(p/(n+'-fixtures.json')) for n in families}
routines=read(p/'walk-tail-routines.json');coverage={}
for address in routines:
 rows=[v['instruction_coverage'][address] for v in originals.values() if address in v['instruction_coverage']]
 assert len({x['total'] for x in rows})==1 and all(not x['excluded'] for x in rows)
 missing=set(rows[0]['missing'])
 for row in rows[1:]:missing.intersection_update(row['missing'])
 total=rows[0]['total'];coverage[address]={'covered':total-len(missing),'total':total,'missing':sorted(missing),'excluded':{}}
assert len(coverage)==3 and (sum(x['covered'] for x in coverage.values()),sum(x['total'] for x in coverage.values()))==(376,376)
assert all(not x['missing'] for x in coverage.values())
new_calls=0
for name in families:
 original=originals[name];fixture=fixtures[name];unit=suites[name.replace('-','_')]
 assert original['cases']==unit['cases'] and original['calls']==unit['calls'] and original['counts']==unit['counts']
 assert unit['nan_fields_classification_only']==unit['indeterminate_word_comparisons']==0 and not fixture['float_fields']
 new_calls+=sum(unit['counts'].get(row['name'],0) for row in routines.values())
 for case in fixture['cases']:
  for step in case['steps']:
   assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','quiet_double_fields','global_quiet_float_indices','global_bit_masks','float_fields','global_float_indices','indeterminate_bytes','indeterminate_words','compression_records'])
assert sum(v['cases'] for v in originals.values())==300 and sum(v['calls'] for v in originals.values())==1896 and new_calls==856
extents=read(p/'walk-tail-extents.json');assert extents['result']=='pass' and extents['routines_sha256']==sha(p/'walk-tail-routines.json') and set(extents['checked'])==set(routines)
flows=originals['walk-tail']['flow_records'];assert len(flows)==56
assert sum(v['kind']=='collision_pose_camera' and v['steps']==3 for v in flows)==48
assert sum(v['kind']=='animation_pose_camera' and v['steps']==4 for v in flows)==8
for name in prior['artifact_hashes']:
 if name.endswith('-routines.json'):
  old=read(r/name)
  if isinstance(old,dict):assert not set(routines).intersection(old),name
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
proof=read(p/'walk-tail-browser.json');assert proof['observed']==candidate and proof['status'].startswith('PASS')
def fingerprint(value):
 canonical=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
 for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
 return {'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(value)}
assert proof['rendered_dom_fingerprint']==fingerprint(candidate)
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
paths=set().union(*(set(p.glob(n+'-*')) for n in families))|{prior_path,p/'walk-common-audit.json'}
for n in families:
 paths.update(p/name for name in ['audit-'+n+'.py','build-'+n+'-draft.py','pin-'+n+'.py','probe-'+n+'.py','serve-'+n+'.py','verify-'+n+'-checkpoint.mjs'])
for f in paths:
 if f.is_file() and f.suffix!='.log' and f!=target and not f.name.endswith('-next.txt') and f!=p/'walk-tail-audit.json':
  artifacts[str(f.relative_to(r))]=sha(f)
  if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={**prior,'result':'original comparisons, Node and actual Chromium pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':3,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':816,'unpromoted_functions_across_separate_experiments':833,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'browser_suites':158,
 'new_cases':300,'new_calls_including_existing_dependencies':1896,'new_interrupted_calls':0,'instruction_coverage':coverage,
 'coverage_limit':'376/376 new instructions exercised across the three original corpora; no exclusions. All1896 calls complete:856 new-root calls and1040 existing dependency calls. Defined arena/global state, preserved registers and diagnostic arguments compare exactly with no numeric or indeterminate-field allowances.48three-step collision/pose/camera sequences and8four-frame animation/pose/camera sequences connect the recovered paths. The complete shared frame still lacks transfer, ground-validation and animation-event helpers. Existing PC24/transcendental contracts remain unchanged.',
 'scope':fixtures['walk-tail']['scope'],
 'unrecovered_lifecycle':'Critical-point displacement/collision and event-driven camera-facing helpers are recovered and integrated with common pose and animation paths. Shared Walk transfer527600, ground/shadow validation527080, animation-speed/event integration52a2c0 and full state dispatch remain unfinished, as do airborne/hanging/rail updates, original asset startup, renderer creation/rendering and the playable training level. Common Walk51/142 and constructor277/463 remain unchanged.',
 'walk_tail_evidence':{'completed_calls':1896,'new_root_calls':856,'existing_dependency_calls':1040,'interrupted_calls':0,'flow_records':flows,'comparison_suites':families,'coverage_by_suite':{n:v['instruction_coverage'] for n,v in originals.items()},'camera_candidate_sequences':originals['walk-camera']['flow_records'],'critical_collision_records':originals['walk-critical']['collision_records'],'new_comparison_allowances':0,'new_unreachable_exclusions':{}},
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':fingerprint(candidate),'playable':False}
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
