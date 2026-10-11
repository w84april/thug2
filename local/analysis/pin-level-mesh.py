"""Freeze original, Node and observed Chromium training mesh evidence."""
import hashlib,json,struct,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'level-mesh-checkpoint.json';proof_path=p/'level-mesh-browser.json'
assert not target.exists() and not proof_path.exists()
prior_path=p/'level-material-checkpoint.json';assert sha(prior_path)=='d0575e5ac892ee62cc1a1c2ac9fd2e0c8e798271e664b2a03575ec4702d2a4d9'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'level-mesh-draft.build.json');module=p/'level-mesh-draft.wasm';assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='f1e8c0201db6fbf0348d17124e1a0c99303a6769be81686ee1cb8d279145ca6a'
assert module.stat().st_size==595659
previous=read(p/'level-material-browser.json')['suites'];names=['level-mesh','training-level-mesh']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('level-mesh-checkpoint-'+n+'-result.json')) for n in names};assert len(suites)==66
for n,s in suites.items():
 assert s['result']=='pass',n
 if n in previous:assert s==previous[n],n
for name,expected in [('level_mesh',(156,156,2,0)),('training_level_mesh',(1,4540,4,0))]:
 s=suites[name];assert(s['cases'],s['calls'],s['functions'],s['nan_fields_classification_only'])==expected
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
original=read(p/'level-mesh-original.json');coverage=original['instruction_coverage']
assert(original['cases'],original['calls'])==(156,156)
assert(coverage['0x4da6d0']['covered'],coverage['0x4da6d0']['total'],coverage['0x4da6d0']['missing'])==(25,25,[])
assert(coverage['0x4d6100']['covered'],coverage['0x4d6100']['total'])==(334,359)
for label in ['level-mesh','training-level-mesh']:
 fixture=read(p/(label+'-fixtures.json'));assert fixture['float_fields']==[]
 for c in fixture['cases']:
  for s in c['steps']:assert not s.get('expected_trap') and 'global_bit_masks' not in s and not s.get('float_fields') and not s.get('quiet_float_fields')
 port=read(p/(label+'-ports.build.json'));assert sha(p/(label+'-ports.c'))==port['source_sha256'] and sha(p/(label+'-ports.wasm'))==port['sha256']
training=read(p/'training-level-mesh-original.json');trace=read(p/'training-level-mesh-flow-trace.json');meshes=trace['meshes']
assert(training['cases'],training['calls'],training['textures'],training['materials'],training['meshes'],training['vertices'],training['indices'])==(1,4540,596,870,2269,50814,77029)
assert training['buffer_calls']==[4538]*3 and training['crt_calls']==13614 and training['heap_events']==7730
assert training['gpu_calls']=={'1':596,'2':2486,'3':2486} and training['file_calls']=={'1':79262,'2':542}
assert len(trace['sectors'])==790 and len(meshes)==2269 and trace['position']==2770439
assert trace['branch_hits']=={'0x4de300':1,'0x4c6130':1,'0x4c6b10':790,'0x4d6100':2269,'0x4d5c30':2269,'0x4b52f0':2269,'0x4d0d30':2269,'0x4da6d0':535}
assert all(int(m['args'][3],16)==0 for m in meshes)
asset_dir=r/'local/game-files/Game/Data/levels/TR';tex=(asset_dir/'TR.tex.xbx').read_bytes();scn=(asset_dir/'TR.scn.xbx').read_bytes()
assert len(tex)==3915744 and len(scn)==2770439
assert sha(asset_dir/'TR.tex.xbx')==training['texture_sha256']==trace['texture_sha256']=='13c28cf820dd4bb989579915ab533b7651ea178ef664d44ad9ec1fc754fa6d21'
assert sha(asset_dir/'TR.scn.xbx')==training['scene_sha256']==trace['scene_sha256']=='a4e185b0f050e181850c341a3378b54f1b37adce3099d3568600bf2e02e61332'
blob=scn[12:110338]+b''.join(scn[m['position']:m['end_position']] for m in meshes)
assert len(blob)==2442817 and hashlib.sha256(blob).hexdigest()==training['serialized_input_sha256']=='65f2549b2502ddc517d98f1ea9ad49d0f60d32ae323a1dcdaa5d98b612ca4f15'
fixture=read(p/'training-level-mesh-fixtures.json');base=fixture['base'];arena=bytearray((p/fixture['memory']).read_bytes())
assert len(arena)==0x1e00000 and len(fixture['cases'])==1
assert arena[0x100000:0x100000+len(tex)]==tex and arena[0x500000:0x500000+len(blob)]==blob
case=fixture['cases'][0];assert not case['patches'] and len(case['steps'])==4540
assert [s['fn'] for s in case['steps']]==['0x49f050','0x4d3390']+['0x4d4be0','0x4d6100']*2269
for s in case['steps']:
 for address,data in s['outputs']:arena[address-base:address-base+len(data)//2]=bytes.fromhex(data)
word=lambda a:struct.unpack_from('<I',arena,a-base)[0]
assert word(base+0x2000)==base+0x500000+len(blob) and word(base+0x1100)==79804
assert word(base+0x1004)==596 and word(base+0x1008)==5568
assert [word(base+0x1200+o) for o in [8,12,16,20]]==[13614,4538,4538,4538]
for i,m in enumerate(meshes):
 at=base+0xa70000+i*216;assert word(word(at+0x14))==int(m['args'][1],16)
 assert struct.unpack_from('<H',arena,at-base+0x22)[0]==m['vertices']
 assert list(struct.unpack_from('<8H',arena,at-base+0x24))==m['index_counts']
 assert arena[at-base+0x18]==m['stride'] and hex(word(at+0x38))==m['formats'][0]
 vertex=word(at+0xcc);n=word(vertex);cpu=word(vertex+12);gpu=word(vertex+8)+256
 assert arena[cpu-base:cpu-base+n]==arena[gpu-base:gpu-base+n]
 for slot,count in enumerate(m['index_counts']):
  if count:
   v=word(at+0x54+slot*4);cpu=word(v+16);gpu=word(v+12)+256
   assert arena[cpu-base:cpu-base+count*2]==arena[gpu-base:gpu-base+count*2]
assert original['specimen_sha256']==training['specimen_sha256']==trace['specimen_sha256']==prior['specimen_sha256']
assert sha(r/'local/build/thug-core.wasm')==prior['main_wasm_sha256']
scope=('Recovered complete file-shader skip4da6d0 and partial file-mesh4d6100 standard vertex path, '
 'with correction4d4350, packed vertices4d5940 and shader conversion4ddc00 explicitly trapping. '
 '156 focused cases pass. Original whole-scene trace returns through790 sectors2269 meshes; all '
 'use the standard vertex path. A separate original/Wasm comparison loads all596 textures and870 '
 'materials, then every serialized mesh record through original mesh initialization/file parsing. '
 '50814 vertices77029 indices and full arena/file/heap/CRT/GPU storage match without NaN or padding '
 'allowances.66 Node/Chromium suites pass with64 inherited summaries unchanged. Only4da6d0 is counted '
 'newly complete. Scene assembly, production rendering and gameplay remain unfinished; main unchanged; not playable.')
proof={**candidate,'recorded_at':sys.argv[4],'observed_via':'Actual Chromium PASS at '+sys.argv[5]+'; all66 summaries and complete DOM fingerprint inspected',
 'browser_dom_fingerprint':{'algorithm':'FNV-1a-64 over canonical sorted JSON characters','value':sys.argv[1],'characters':len(canonical)},'scope':scope}
proof_path.write_text(json.dumps(proof,indent=2)+'\n')
files=set()
for pattern in ['level-mesh-*','training-level-mesh-*','*level-mesh*.py','verify-level-mesh-checkpoint.mjs']:
 files.update(f for f in p.glob(pattern) if f.is_file() and f not in {target,p/'level-mesh-audit.json',p/'level-mesh-next.txt'})
files.update(f for f in (p/'level-mesh-ghidra').rglob('*') if f.is_file())
assert p/'audit-level-mesh.py' in files and p/'pin-level-mesh.py' in files
artifacts=set(prior['artifact_hashes'])|{'local/analysis/level-material-checkpoint.json','local/analysis/level-material-audit.json'}|{str(f.relative_to(r)) for f in files}
pin={'result':'original, Node and actual Chromium comparisons pass; unpromoted','new_functions':1,'original_addresses':['0x4da6d0'],'partial_original_addresses':['0x4d6100'],
 'unpromoted_functions_in_this_module':321,'unpromoted_functions_across_separate_experiments':338,
 'specimen_sha256':original['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],
 'browser_suites':66,'new_cases':157,'new_calls_including_existing_dependencies':4696,'new_interrupted_calls':0,
 'actual_training':{k:v for k,v in training.items() if k not in ['buffers','scope']},'instruction_coverage':coverage,
 'source_hashes':build['source_hashes'],'artifact_hashes':{n:sha(r/n) for n in sorted(artifacts)},'harness_hashes':prior['harness_hashes'],
 'checker_dependency_hashes':prior['checker_dependency_hashes'],'browser_dom_fingerprint':proof['browser_dom_fingerprint'],'scope':scope}
target.write_text(json.dumps(pin,indent=2)+'\n')
print(json.dumps({'result':'pinned','artifacts':len(pin['artifact_hashes']),'sources':len(pin['source_hashes']),'checkpoint_sha256':sha(target),'main_unchanged':True}))
