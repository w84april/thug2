"""Pin successful original/Node/actual-Chromium texture-buffer comparisons."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'texture-buffer-checkpoint.json';proof_path=p/'texture-buffer-browser.json'
assert not target.exists() and not proof_path.exists()
prior_path=p/'model-configuration-checkpoint.json'
assert sha(prior_path)=='b740ab501df130f5fb13b5f451e8d8a1bda336f8ee0e66025be63af824256bb7'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'texture-buffer-draft.build.json');module=p/'texture-buffer-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='9774e060bd4cb4fa57ff2dfc0c4f6b1b1b4b44e623c32d0045b8cdc46a786000'
assert module.stat().st_size==552696
previous=read(p/'model-configuration-browser.json')['suites'];names=['texture-buffer']+[name.replace('_','-') for name in previous]
suites={name.replace('-','_'):read(p/('texture-buffer-checkpoint-'+name+'-result.json')) for name in names}
assert len(suites)==36
for name,summary in suites.items():
 assert summary['result']=='pass',name
 if name in previous:assert summary==previous[name],name
s=suites['texture_buffer'];assert(s['cases'],s['calls'],s['functions'],s['nan_fields_classification_only'])==(120,161,10,0)
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
original=read(p/'texture-buffer-original.json');coverage=original['instruction_coverage']
assert(original['cases'],original['calls'],original['new_functions'])==(120,161,9)
assert original['existing_dependency_addresses']==['0x49fd30']
new_coverage={a:t for a,t in coverage.items() if a not in original['existing_dependency_addresses']}
assert len(new_coverage)==9 and sum(t['covered'] for t in new_coverage.values())==503 and sum(t['total'] for t in new_coverage.values())==522
for t in coverage.values():assert set(t['missing'])==set(t['excluded'])
assert original['gpu_calls']=={'1':138,'2':183,'3':183}
assert len(original['assets'])==6
for asset in original['assets']:
 f=r/asset['path'];assert sha(f)==asset['sha256']=='66bc9d8ac9cf881dbe381764e02fb4cd86976de99ae2fecfc5842d62a10406b3'
 assert f.stat().st_size==asset['bytes']==88
 assert asset['textures_created']==(2 if asset['mode']=='extend' else 1)
 assert asset['gpu_events']==5*asset['textures_created']
assert original['specimen_sha256']==prior['specimen_sha256']
assert sha(r/'local/build/thug-core.wasm')==prior['main_wasm_sha256']
scope=(
 'Nine additional routines recover texture dictionary/resource/wrapper construction, the original PC texture '
 'buffer parser, dictionary loading, create-on-cache-miss and cache lookup. The previously recovered49fd30 '
 'table clearer is reused and tested, not counted again.120 cases161 complete calls compare the entire arena, '
 'globals, heap effects, GPU call arguments and uploaded bytes, with zero NaN allowances. Nine new routines '
 'cover503/522 instructions;19 explicit exclusions are allocator bootstrap, allocation failure and one '
 'unreachable alignment instruction. An initialized successful heap and complete bounded data are the '
 'internal contract. Heap-owner lookup maps to the existing memory-scope port. A comparison GPU provides '
 'create/lock/unlock storage and logs; it is not a renderer or a production browser GPU adapter. The original '
 '88-byte Letter S texture runs through six direct/dictionary/cache paths, producing8x8 DXT1 and two mip '
 'uploads of exactly32 and8 bytes. Synthetic unsupported formats test retained scratch arguments only, '
 'not hardware support. Actual Chromium passes36 suites and all35 previous summaries remain identical. '
 'Original4935e0 model load and40a5a0 texture-asset integration remain pending; the training script has '
 'not yet reached this parser through that path. No model is drawn and the level is not playable. '
 'Main and separate physics builds remain unchanged.'
)
proof={**candidate,'recorded_at':sys.argv[4],'observed_via':'Actual Chromium PASS at '+sys.argv[5]+'; all36 suite summaries and complete DOM fingerprint inspected',
 'browser_dom_fingerprint':{'algorithm':'FNV-1a-64 over canonical sorted JSON characters','value':sys.argv[1],'characters':len(canonical)},'scope':scope}
files=['texture-buffer-draft.c','build-texture-buffer-draft.py','texture-buffer-draft.wasm','texture-buffer-draft.build.json',
 'probe-texture-buffer.py','texture-buffer-fixtures.json','texture-buffer-memory.bin','texture-buffer-original.json','texture-buffer-probe.log',
 'texture-buffer-ports.c','texture-buffer-ports.wasm','texture-buffer-ports.build.json','texture-buffer-instructions.txt',
 'verify-texture-buffer-checkpoint.mjs','texture-buffer-full-node.log','texture-buffer-browser.html','texture-buffer-worker.mjs',
 'serve-texture-buffer.py','texture-buffer-browser.json','pin-texture-buffer.py','audit-texture-buffer.py',
 'model-assets-focus.tsv','model-assets-ghidra.log','texture-buffer-ghidra.log','texture-parser-ghidra.log','texture-parser-instructions.txt']
files += ['texture-buffer-checkpoint-'+name+'-result.json' for name in names]
for directory in ['model-assets-ghidra','texture-buffer-ghidra','texture-parser-ghidra']:
 files += [str(f.relative_to(p)) for f in sorted((p/directory).rglob('*')) if f.is_file()]
for name in files:
 if name!='texture-buffer-browser.json':assert(p/name).is_file(),name
proof_path.write_text(json.dumps(proof,indent=2)+'\n')
artifacts=set(prior['artifact_hashes'])|{'local/analysis/model-configuration-checkpoint.json','local/analysis/model-configuration-audit.json'}|{'local/analysis/'+n for n in files}
pin={'result':'original, Node and actual Chromium comparisons pass; unpromoted','new_functions':9,'original_addresses':list(new_coverage),
 'unpromoted_functions_in_this_module':238,'unpromoted_functions_across_separate_experiments':255,
 'specimen_sha256':original['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,
 'main_wasm_sha256':prior['main_wasm_sha256'],'browser_suites':36,'new_cases':120,'new_calls_including_existing_dependencies':161,
 'new_interrupted_calls':0,'actual_texture_asset_paths':original['assets'],'instruction_coverage':new_coverage,
 'existing_dependency_instruction_coverage':{'0x49fd30':coverage['0x49fd30']},
 'source_hashes':build['source_hashes'],'artifact_hashes':{n:sha(r/n) for n in sorted(artifacts)},
 'harness_hashes':prior['harness_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],
 'browser_dom_fingerprint':proof['browser_dom_fingerprint'],'scope':scope}
target.write_text(json.dumps(pin,indent=2)+'\n')
print(json.dumps({'result':'pinned','artifacts':len(pin['artifact_hashes']),'sources':len(pin['source_hashes']),'checkpoint_sha256':sha(target),'main_unchanged':True}))
