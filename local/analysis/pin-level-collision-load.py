"""Freeze verified collision scene integration and preserve every earlier artifact."""
import hashlib,json,subprocess,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'level-collision-load-checkpoint.json';proof=p/'level-collision-load-browser.json';assert not target.exists() and not proof.exists()
prior_path=p/'level-object-startup-checkpoint.json';assert sha(prior_path)=='28f5e625bbccda5f172d50134e01c85d348dc15b25aeeadc91fb1be1bc2712bd';prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'level-collision-load-draft.build.json');module=p/'level-collision-load-draft.wasm';assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='7aa0439f67212e25c64d6a60eb55112f7019146d5569b83f3dc9d9f55752b87c' and module.stat().st_size==605047
assert str(r/'src/collision/load.c') not in build['command'] and str(p/'level-collision-load-load-derived.c') in build['command']
for n in ['level-collision-load-ports','level-collision-load-unit-ports']:
 ports=read(p/(n+'.build.json'));assert ports['sha256']==sha(p/(n+'.wasm')) and ports['source_sha256']==sha(p/(n+'.c'))
previous=read(p/'level-object-startup-browser.json')['suites'];names=['level-collision-load','level-collision-load-unit']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('level-collision-load-checkpoint-'+n+'-result.json')) for n in names};assert len(suites)==77
for name,suite in suites.items():
 assert suite['result']=='pass',name
 if name in previous:assert suite==previous[name],name
for name,expected in [('level_collision_load',(1,12,9,0)),('level_collision_load_unit',(16,28,4,0))]:
 s=suites[name];assert (s['cases'],s['calls'],s['functions'],s['nan_fields_classification_only'])==expected
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
subprocess.run([sys.executable,'-B',str(p/'check-level-collision-load-graph.py')],check=True)
proof.write_text(json.dumps({**candidate,'browser':'Codex in-app Chromium','url':'http://127.0.0.1:58463/','tab':'154','dom_fingerprint':{'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':5}},indent=2)+'\n')
artifacts=dict(prior['artifact_hashes']);paths=set(p.glob('level-collision-load-*'));paths.update(p.glob('*level-collision-load*.py'));paths.update(p.glob('*level-collision-load*.mjs'));paths.add(prior_path)
for directory in ['level-collision-load-ghidra','level-collision-load-component-ghidra']:paths.update(f for f in (p/directory).rglob('*') if f.is_file())
for f in paths:
 if f.is_file() and f not in [target,p/'level-collision-load-next.txt']:artifacts[str(f.relative_to(r))]=sha(f)
harnesses=dict(prior['harness_hashes'])
for f in paths:
 if f.is_file() and f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
t=read(p/'level-collision-load-original.json');unit=read(p/'level-collision-load-unit-original.json');coverage=unit['instruction_coverage']
assert coverage['0x49d590']['missing']==['0x49d5f8'];assert all(not v['missing'] for k,v in coverage.items() if k!='0x49d590')
coverage['0x49d590']['excluded']={'0x49d5f8':'allocator is initialized by the platform contract'}
checkpoint={'result':'original, Node and actual Chromium comparisons pass; unpromoted','prior_checkpoint_sha256':sha(prior_path),'new_functions':4,'original_addresses':['0x49d590','0x49e890','0x49eaa0','0x48df10'],
 'corrected_existing_address':'0x418bd0: temporary offset buffer selects manager+0x110 (adapter scope2), not manager+0x124 (scope1); main source remains immutable until integration',
 'partial_original_addresses':['0x468ec0','0x5a2e50'],'unpromoted_functions_in_this_module':prior['unpromoted_functions_in_this_module']+4,'unpromoted_functions_across_separate_experiments':prior['unpromoted_functions_across_separate_experiments']+4,
 'specimen_sha256':t['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':sha(r/'local/build/thug-core.wasm'),'browser_suites':77,'new_cases':17,'new_calls_including_existing_dependencies':40,'new_interrupted_calls':1,
 'actual_training':{k:v for k,v in t.items() if k not in ['resources','buffers','scope','instruction_coverage']},'instruction_coverage':coverage,
 'source_hashes':prior['source_hashes'],'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),'checker_dependency_hashes':prior['checker_dependency_hashes'],'browser_dom_fingerprint':read(proof)['dom_fingerprint'],
 'playable':False,'scope':t['scope']}
assert checkpoint['main_wasm_sha256']==prior['main_wasm_sha256']
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
