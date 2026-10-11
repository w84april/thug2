"""Freeze combined original/Node/Chromium prefix evidence; preserve every prior pin."""
import hashlib,json,subprocess,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'level-object-startup-checkpoint.json';proof=p/'level-object-startup-browser.json';assert not target.exists() and not proof.exists()
prior_path=p/'geometry-clone-checkpoint.json';assert sha(prior_path)=='0f0639abd7afe21db1277b5dc1bc5abed7d82232d61bab926f08b7802bdd8479';prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'level-object-startup-draft.build.json');module=p/'level-object-startup-draft.wasm';assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='3e9624629b8ba2bcc18c46828be9bbb9f3e7da4f7c700df612a3949869838dec' and module.stat().st_size==604162
assert 'level-object-startup-alternate-candidate.c' not in '\n'.join(build['command'])
ports=read(p/'level-object-startup-ports.build.json');assert ports['sha256']==sha(p/'level-object-startup-ports.wasm') and ports['source_sha256']==sha(p/'level-object-startup-ports.c')
previous=read(p/'geometry-clone-browser.json')['suites'];names=['level-object-startup']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('level-object-startup-checkpoint-'+n+'-result.json')) for n in names};assert len(suites)==75
for name,suite in suites.items():
 assert suite['result']=='pass',name
 if name in previous:assert suite==previous[name],name
s=suites['level_object_startup'];assert(s['cases'],s['calls'],s['functions'],s['nan_fields_classification_only'])==(1,11,8,0)
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}'=='26b830c8a44c2aff' and int(sys.argv[2])==len(canonical)==80178 and int(sys.argv[3])==len(candidate)==5
subprocess.run([sys.executable,'-B',str(p/'check-level-object-startup-graph.py')],check=True)
proof.write_text(json.dumps({**candidate,'browser':'Codex in-app Chromium','url':'http://127.0.0.1:54948/','tab':'153','dom_fingerprint':{'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':5}},indent=2)+'\n')
artifacts=dict(prior['artifact_hashes']);paths=set(p.glob('level-object-startup-*'))
paths.update(p.glob('*level-object-startup*.py'));paths.update(p.glob('*level-object-startup*.mjs'))
for directory in ['rigidbody-startup-ghidra','level-object-collision-ghidra']:paths.update(f for f in (p/directory).rglob('*') if f.is_file())
paths.add(p/'rigidbody-startup-inspection.txt')
for f in paths:
 if f.is_file() and f not in [target,p/'level-object-startup-next.txt']:artifacts[str(f.relative_to(r))]=sha(f)
harnesses=dict(prior['harness_hashes'])
for f in paths:
 if f.is_file() and f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
t=read(p/'level-object-startup-original.json')
checkpoint={'result':'original, Node and actual Chromium prefix/boundary comparisons pass; unpromoted','prior_checkpoint_sha256':sha(prior_path),'new_functions':0,'original_addresses':[],
 'partial_original_addresses':['0x468ec0','0x5a2e50'],'unpromoted_functions_in_this_module':prior['unpromoted_functions_in_this_module'],'unpromoted_functions_across_separate_experiments':prior['unpromoted_functions_across_separate_experiments'],
 'specimen_sha256':t['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':sha(r/'local/build/thug-core.wasm'),'browser_suites':75,'new_cases':1,'new_calls_including_existing_dependencies':11,'new_interrupted_calls':1,
 'actual_training':{k:v for k,v in t.items() if k not in ['resources','buffers','scope','instruction_coverage']},'instruction_coverage':t['instruction_coverage'],
 'source_hashes':prior['source_hashes'],'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),'checker_dependency_hashes':prior['checker_dependency_hashes'],'browser_dom_fingerprint':candidate and read(proof)['dom_fingerprint'],
 'playable':False,'scope':t['scope']}
assert checkpoint['main_wasm_sha256']==prior['main_wasm_sha256']
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
