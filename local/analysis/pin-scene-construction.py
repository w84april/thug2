"""Pin scene construction after original, Node and actual Chromium comparisons."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'scene-construction-checkpoint.json';proof_path=p/'scene-construction-browser.json'
assert not target.exists() and not proof_path.exists()
prior_path=p/'material-buffer-checkpoint.json';assert sha(prior_path)=='6bf5797dc2f41fe9bcb25fa5964472ef2eb84fa74e2c78c44a9af0a45c1dc3a9'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'scene-construction-draft.build.json');module=p/'scene-construction-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='f6c7b78b9f5b2152c04f0a68bc7034d5bdf3df58f6c015c3841ee69ec0881731'
assert module.stat().st_size==564290
for port in ['scene-construction-ports','training-scene-construction-boundary']:
 meta=read(p/(port+'.build.json'));assert sha(p/(port+'.c'))==meta['source_sha256'] and sha(p/(port+'.wasm'))==meta['sha256']
 if port=='scene-construction-ports':assert meta['included_source_sha256']==sha(p/'texture-buffer-ports.c')
previous=read(p/'material-buffer-browser.json')['suites'];names=['scene-construction','training-scene-construction']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('scene-construction-checkpoint-'+n+'-result.json')) for n in names};assert len(suites)==44
for n,s in suites.items():
 assert s['result']=='pass',n
 if n in previous:assert s==previous[n],n
s=suites['scene_construction'];assert(s['cases'],s['calls'],s['functions'],s['nan_fields_classification_only'])==(89,199,10,0)
s=suites['training_scene_construction'];assert(s['cases'],s['calls'],s['functions'],s['nan_fields_classification_only'])==(2,22,8,0)
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
original=read(p/'scene-construction-original.json');coverage=original['instruction_coverage']
assert(original['cases'],original['calls'])==(89,199)
assert set(coverage)=={'0x49d390','0x4c6130','0x49e900','0x4c6550','0x4c6190','0x49ca10','0x49e660','0x4b5f60','0x49d4e0'}
assert sum(t['covered'] for t in coverage.values())==178 and sum(t['total'] for t in coverage.values())==193
excluded={'0x49d390':{'0x49d3d6','0x49d405','0x49d486','0x49d4b4'},
 '0x4c6190':{'0x4c61af','0x4c61ea','0x4c61ee','0x4c61f0','0x4c61f7','0x4c61fa'},
 '0x4b5f60':{'0x4b5fac','0x4b5fae','0x4b5fb1','0x4b5fb7','0x4b5fb8'}}
for a,c in coverage.items():assert set(c['missing'])==set(c['excluded'])==excluded.get(a,set())
training=read(p/'training-scene-construction-original.json');old_training=read(p/'training-material-buffer-original.json')
assert(training['cases'],training['calls'])==(2,22)
for part in ['partial_model_load','partial_configuration','partial_geometry_load']:
 assert training[part]['complete'] is False and training[part]['boundary']=='0x4c6650'
assert(training['partial_geometry_load']['covered_instructions'],training['partial_geometry_load']['total_instructions'])==(103,178)
assert training['io_calls']==old_training['io_calls'] and training['gpu_calls']==old_training['gpu_calls']
a,b=training['nodes'];assert(a['node_index'],a['completed_calls'],a['interrupted_calls'],a['execute_result'])==(204,11,0,0)
assert(b['node_index'],b['completed_calls'],b['interrupted_calls'],b['first_missing_routine'])==(1289,10,1,'0x4c6650')
state=b['model_state'];assert {k:v for k,v in state.items() if k!='scene'}==old_training['nodes'][1]['model_state']
assert state['scene']=={'scene':'0x22bf3f8','table':'0x22bf68c','sector':'0x22bf724','geometry':'0x22bf768','mesh_head':'0x22bf7dc','registered_sectors':0,'model_cursor_offset':117}
assert b['geometry_parser_request']=={'receiver':'0x22bf724','cursor':'0x22bdfd9'}
asset_dir=r/'local/game-files/Game/Data/models/GameObjects/SKATE/Letter_S'
assert sha(asset_dir/'Letter_S.mdl.xbx')==training['model_file_sha256']==old_training['model_file_sha256']
assert sha(asset_dir/'Letter_S.tex.xbx')==training['texture_file_sha256']==old_training['texture_file_sha256']
fixture=read(p/'training-scene-construction-fixtures.json');annotated=[]
for i,c in enumerate(fixture['cases']):
 for j,step in enumerate(c['steps']):
  if 'global_bit_masks' in step:
   actual={}
   for index,mask in step['global_bit_masks'].items():
    name,address,width,offset=fixture['globals'][int(index)]
    assert name=='thug_asset_options_storage_draft' and address==0x691758+offset and width==4;actual[offset]=mask
   assert actual=={0:255,12:0,16:65535,56:255,60:0,64:0,68:0,72:0} and step['expected_trap'];annotated.append((i,j))
assert annotated==[(1,10)]
unit=read(p/'scene-construction-fixtures.json');assert all('global_bit_masks' not in s for c in unit['cases'] for s in c['steps'])
assert len([n for n in unit['case_labels'] if n.startswith('alternate scene virtual')])==3
assert original['specimen_sha256']==training['specimen_sha256']==prior['specimen_sha256']
assert sha(r/'local/build/thug-core.wasm')==prior['main_wasm_sha256']
scope=(
 'Nine complete scene/sector routines recover base/PC constructors, virtual sector allocation, '
 'geometry binding, scoped mesh-list initialization and sector registration.89 unit cases199 calls '
 'cover178/193 instructions; fifteen exclusions are two heap bootstrap calls and thirteen '
 'allocation-failure instructions under initialized-heap/successful-allocation contracts. '
 'Tests compare retained storage, bounds, method identities, allocation/scoping order, table shifts '
 'through12, duplicate/colliding registration, repeated initialization and alternate virtual dispatch. '
 'The existing geometry constructor is reused and not counted new. Two unchanged training cases '
 '22 calls include one interruption. Node204 completes; node1289 loads its original texture/model '
 'and material, then constructs the real scene, sector, geometry and empty mesh list. '
 'Partial4b3490 advances from68 to103 of178 instructions, stopping before4c6650 mesh parsing. '
 'No scene success, mesh data or drawing is fabricated. Complete arena/heap/globals/I/O compare '
 'after pointer relocation; only28 previously proved uninitialized option bytes remain masked '
 'in one interrupted training call. New suites have zero NaN allowances. Actual Chromium passes '
 '44 suites; all42 inherited summaries are identical. Complete geometry, production browser '
 'file/GPU providers, rendering and playable gameplay remain pending. Main build unchanged.'
)
proof={**candidate,'recorded_at':sys.argv[4],'observed_via':'Actual Chromium PASS at '+sys.argv[5]+'; all44 summaries and complete DOM fingerprint inspected',
 'browser_dom_fingerprint':{'algorithm':'FNV-1a-64 over canonical sorted JSON characters','value':sys.argv[1],'characters':len(canonical)},'scope':scope}
files=['scene-construction-draft.c','scene-construction-material-derived.c','build-scene-construction-draft.py','scene-construction-draft.wasm','scene-construction-draft.build.json',
 'scene-construction-instructions.txt','probe-scene-construction.py','scene-construction-fixtures.json','scene-construction-memory.bin','scene-construction-original.json','scene-construction-probe.log',
 'probe-training-scene-construction.py','training-scene-construction-fixtures.json','training-scene-construction-memory.bin','training-scene-construction-original.json','training-scene-construction-probe.log',
 'verify-scene-construction-checkpoint.mjs','scene-construction-full-node.log','scene-construction-browser.html','scene-construction-worker.mjs','serve-scene-construction.py',
 'scene-construction-browser.json','pin-scene-construction.py','audit-scene-construction.py']
files += [port+suffix for port in ['scene-construction-ports','training-scene-construction-boundary'] for suffix in ['.c','.wasm','.build.json']]
files += ['scene-construction-checkpoint-'+n+'-result.json' for n in names]
files += ['mesh-buffer-ghidra.log']+[str(f.relative_to(p)) for f in sorted((p/'mesh-buffer-ghidra').rglob('*')) if f.is_file()]
for name in files:
 if name!='scene-construction-browser.json':assert(p/name).is_file(),name
proof_path.write_text(json.dumps(proof,indent=2)+'\n')
artifacts=set(prior['artifact_hashes'])|{'local/analysis/material-buffer-checkpoint.json','local/analysis/material-buffer-audit.json'}|{'local/analysis/'+n for n in files}
pin={'result':'original, Node and actual Chromium comparisons pass; unpromoted','new_functions':9,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':263,'unpromoted_functions_across_separate_experiments':280,
 'specimen_sha256':original['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],
 'browser_suites':44,'new_cases':91,'new_calls_including_existing_dependencies':221,'new_interrupted_calls':1,'actual_training_nodes':training['nodes'],
 'instruction_coverage':coverage,'partial_geometry_load':training['partial_geometry_load'],'indeterminate_option_bytes':state['indeterminate_texture_option_bytes'],
 'source_hashes':build['source_hashes'],'artifact_hashes':{n:sha(r/n) for n in sorted(artifacts)},'harness_hashes':prior['harness_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],
 'browser_dom_fingerprint':proof['browser_dom_fingerprint'],'scope':scope}
target.write_text(json.dumps(pin,indent=2)+'\n')
print(json.dumps({'result':'pinned','artifacts':len(pin['artifact_hashes']),'sources':len(pin['source_hashes']),'checkpoint_sha256':sha(target),'main_unchanged':True}))
