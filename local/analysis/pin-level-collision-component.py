"""Freeze completed ordinary prop startup without changing earlier artifacts."""
import hashlib,json,subprocess,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'level-collision-component-checkpoint.json';proof=p/'level-collision-component-browser.json';assert not target.exists() and not proof.exists()
prior_path=p/'level-collision-load-checkpoint.json';assert sha(prior_path)=='77bc65e1f88fbf94a8632b1f0b8c959f2f6a6bc6d7e9eeaae355eb1d7a764266';prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'level-collision-component-draft.build.json');module=p/'level-collision-component-draft.wasm';assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='bd0aabbdf1b6bb41e2a65a283c3adddc322632d1e8de24af51bac2d39a3b25d1' and module.stat().st_size==611481
for original,derived in [('src/collision/load.c','level-collision-load-load-derived.c'),('src/collision/moving.c','level-collision-component-moving-derived.c')]:
 assert str(r/original) not in build['command'] and str(p/derived) in build['command']
previous=read(p/'level-collision-load-browser.json')['suites'];names=['level-collision-component','level-collision-component-unit']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('level-collision-component-checkpoint-'+n+'-result.json')) for n in names};assert len(suites)==79
for name,suite in suites.items():
 assert suite['result']=='pass',name
 if name in previous:assert suite==previous[name],name
for name,expected in [('level_collision_component',(1,24,10,0)),('level_collision_component_unit',(88,115,20,0))]:
 s=suites[name];assert (s['cases'],s['calls'],s['functions'],s['nan_fields_classification_only'])==expected
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
subprocess.run([sys.executable,'-B',str(p/'check-level-collision-component-graph.py')],check=True)
t=read(p/'level-collision-component-original.json');unit=read(p/'level-collision-component-unit-original.json');coverage=unit['instruction_coverage']
addresses=['0x44f7e0','0x406890','0x407f80','0x4088e0','0x411fa0','0x412550','0x4133e0','0x411be0','0x40ae10','0x4177b0','0x414990','0x40add0','0x41c920','0x41c7b0','0x41c890','0x41c980','0x493040','0x490ab0']
assert set(addresses)==set(coverage) and len(addresses)==18
bootstrap={'0x407fba','0x41343f','0x411c0d','0x4177da','0x4149d1','0x414a70','0x414add'}
failure={'0x44f81f','0x44f821','0x44f824','0x44f826','0x44f827','0x4068d6','0x4068d8','0x4068db','0x4068dc','0x4068de','0x4068df','0x407fe7','0x408047','0x40804b','0x40804e','0x40804f','0x408051','0x408052','0x408053','0x40805a','0x40805d','0x40891c','0x40891e','0x414a15','0x414a17','0x414a1f','0x414a21','0x414a51','0x414aa3','0x414b11'}
invalid_list={'0x49306d','0x49306f','0x493071','0x493074','0x493076','0x493077','0x49307c','0x49307e'}
assert {a for c in coverage.values() for a in c['missing']}==bootstrap|failure|invalid_list
for c in coverage.values():
 c['excluded']={a:('initialized allocator contract' if a in bootstrap else 'successful allocation contract; allocation-failure behavior unverified' if a in failure else 'invalid count==1 with null part-list; original dereferences address zero') for a in c['missing']}
assert (t['completed_calls'],t['interrupted_calls'],t['completed_objects'])==(24,0,12)
assert sum(bool(o['collision']) for o in t['objects'])==10 and sum(len(o['components']) for o in t['objects'])==96
proof.write_text(json.dumps({**candidate,'browser':'Codex in-app Chromium','url':'http://127.0.0.1:62696/','tab':'155','dom_fingerprint':{'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':5}},indent=2)+'\n')
artifacts=dict(prior['artifact_hashes']);paths=set(p.glob('level-collision-component-*'));paths.update(p.glob('*level-collision-component*.py'));paths.update(p.glob('*level-collision-component*.mjs'));paths.add(prior_path)
paths.update(f for f in (p/'level-collision-component-ghidra').rglob('*') if f.is_file())
for f in paths:
 if f.is_file() and f not in [target,p/'level-collision-component-next.txt']:artifacts[str(f.relative_to(r))]=sha(f)
harnesses=dict(prior['harness_hashes'])
for f in paths:
 if f.is_file() and f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={'result':'original, Node and actual Chromium comparisons pass; unpromoted','prior_checkpoint_sha256':sha(prior_path),'new_functions':18,'original_addresses':addresses,
 'carried_correction':prior['corrected_existing_address'],'partial_original_addresses':['0x468ec0','0x5a2e50'],'unpromoted_functions_in_this_module':prior['unpromoted_functions_in_this_module']+18,'unpromoted_functions_across_separate_experiments':prior['unpromoted_functions_across_separate_experiments']+18,
 'specimen_sha256':t['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':sha(r/'local/build/thug-core.wasm'),'browser_suites':79,'new_cases':89,'new_calls_including_existing_dependencies':139,'new_interrupted_calls':0,
 'actual_training':{k:v for k,v in t.items() if k not in ['resources','buffers','scope','instruction_coverage']},'instruction_coverage':coverage,
 'unrecovered_lifecycle':'Collision component destructor; box/compound query and lifecycle methods; asset-manager update task callback and lifecycle remain unavailable. Constructor identities do not implement these bodies.',
 'source_hashes':prior['source_hashes'],'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),'checker_dependency_hashes':prior['checker_dependency_hashes'],'browser_dom_fingerprint':read(proof)['dom_fingerprint'],
 'playable':False,'scope':t['scope']}
assert checkpoint['main_wasm_sha256']==prior['main_wasm_sha256']
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
