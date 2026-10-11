"""Freeze mesh registration after original, Node and actual Chromium comparisons."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'mesh-register-checkpoint.json';proof_path=p/'mesh-register-browser.json'
assert not target.exists() and not proof_path.exists()
prior_path=p/'vertex-upload-checkpoint.json';assert sha(prior_path)=='66b5e0e9da7b584cd4a28ac6c40ee1b6c4cffd7c37e38b86e754e3e88e7c6ebd'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'mesh-register-draft.build.json');module=p/'mesh-register-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='7d379db66ae5ce612237cfd760c0c546e50fd07f0ec1e319d93657316bd2379d'
assert module.stat().st_size==573020
meta=read(p/'training-mesh-register-boundary.build.json')
assert sha(p/'training-mesh-register-boundary.c')==meta['source_sha256'] and sha(p/'training-mesh-register-boundary.wasm')==meta['sha256']
previous=read(p/'vertex-upload-browser.json')['suites'];names=['mesh-register','training-mesh-register']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('mesh-register-checkpoint-'+n+'-result.json')) for n in names};assert len(suites)==50
for n,s in suites.items():
 assert s['result']=='pass',n
 if n in previous:assert s==previous[n],n
s=suites['mesh_register'];assert(s['cases'],s['calls'],s['functions'],s['nan_fields_classification_only'])==(349,529,3,194)
s=suites['training_mesh_register'];assert(s['cases'],s['calls'],s['functions'],s['nan_fields_classification_only'])==(2,22,8,0)
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
original=read(p/'mesh-register-original.json');coverage=original['instruction_coverage']
assert(original['cases'],original['calls'])==(349,529)
assert set(coverage)=={'0x4d5900','0x4b52f0','0x4de340'}
assert sum(t['covered'] for t in coverage.values())==95 and sum(t['total'] for t in coverage.values())==96
for a,c in coverage.items():
 assert set(c['missing'])==set(c['excluded'])==({'0x4b532f'} if a=='0x4b52f0' else set())
training=read(p/'training-mesh-register-original.json');old_training=read(p/'training-vertex-upload-original.json')
assert(training['cases'],training['calls'])==(2,22)
for part in ['partial_model_load','partial_configuration','partial_geometry_load','partial_mesh_buffer','partial_sector_parser']:
 assert training[part]['complete'] is False and training[part]['boundary']=='0x4b3b1c'
 assert set(old_training[part]['executed'])<=set(training[part]['executed'])
for part,wanted in [('partial_mesh_buffer',(248,347)),('partial_sector_parser',(298,346)),('partial_geometry_load',(127,178))]:
 assert (training[part]['covered_instructions'],training[part]['total_instructions'])==wanted
for k in ['io_calls','gpu_calls','index_calls','crt_calls']:assert training[k]==old_training[k]
a,b=training['nodes'];assert(a['node_index'],a['completed_calls'],a['interrupted_calls'],a['execute_result'])==(204,11,0,0)
assert(b['node_index'],b['completed_calls'],b['interrupted_calls'],b['first_missing_routine'])==(1289,10,1,'0x4b3b1c')
state=b['model_state'];old_state=old_training['nodes'][1]['model_state']
assert {k:v for k,v in state.items() if k not in ['mesh','scene']}=={k:v for k,v in old_state.items() if k not in ['mesh','scene']}
mesh=state['mesh'];assert all(mesh[k]==v for k,v in old_state['mesh'].items())
scene=state['scene'];assert all(scene[k]==v for k,v in old_state['scene'].items() if k!='registered_sectors')
assert scene['registered_sectors']==1 and mesh['bone']==255 and mesh['list_node']=='0x22bfa08'
assert mesh['bounds_bits']==['0x3ebe6237','0xbbc46e6c','0x0','0x41800649']
assert scene['bounds_bits']==['0xc1490000','0xc1640000','0xc0c40000','0x3f800000','0x41460000','0x41640000','0x40c40000','0x3f800000','0xbdc00000','0x0','0x0','0x419f3526']
assert b['wrapper_continuation']=={'scene':scene['scene'],'instruction':'0x4b3b1c'}
for fn in ['0x4d5900','0x4b52f0','0x4d0d30','0x49d4e0','0x4de340']:assert b['native_entries'][fn]==1
asset_dir=r/'local/game-files/Game/Data/models/GameObjects/SKATE/Letter_S'
assert sha(asset_dir/'Letter_S.mdl.xbx')==training['model_file_sha256']==old_training['model_file_sha256']
assert sha(asset_dir/'Letter_S.tex.xbx')==training['texture_file_sha256']==old_training['texture_file_sha256']
fixture=read(p/'training-mesh-register-fixtures.json');annotated=[]
for i,c in enumerate(fixture['cases']):
 for j,step in enumerate(c['steps']):
  if 'global_bit_masks' in step:
   actual={}
   for index,mask in step['global_bit_masks'].items():
    name,address,width,offset=fixture['globals'][int(index)]
    assert name=='thug_asset_options_storage_draft' and address==0x691758+offset and width==4;actual[offset]=mask
   assert actual=={0:255,12:0,16:65535,56:255,60:0,64:0,68:0,72:0} and step['expected_trap'];annotated.append((i,j))
assert annotated==[(1,10)]
arena=bytearray((p/fixture['memory']).read_bytes());base=fixture['base'];case=fixture['cases'][1]
for address,data in case.get('patches',[]):arena[address-base:address-base+len(data)//2]=bytes.fromhex(data)
for step in case['steps']:
 for address,data in step['outputs']:arena[address-base:address-base+len(data)//2]=bytes.fromhex(data)
word=lambda a:int.from_bytes(arena[a-base:a-base+4],'little')
model=(asset_dir/'Letter_S.mdl.xbx').read_bytes()
for key in ['cpu_vertices','gpu_vertices']:
 at=int(mesh[key],16);assert arena[at-base:at-base+3888]==model[798:4686]
mesh_at=int(mesh['mesh'],16);node=int(mesh['list_node'],16);head=int(scene['mesh_head'],16);sector=int(scene['sector'],16);table=int(scene['table'],16)
assert word(head+12)==word(head+16)==node and word(node+12)==word(node+16)==head
assert word(node)==0x64a434 and word(node+4)==mesh_at and word(node+8)==0
assert word(int(scene['geometry'],16)+0x40)==1 and word(table+8)==1
buckets=word(table+4);found=[word(buckets+i*12+4) for i in range(1<<word(table)) if word(buckets+i*12+4)]
assert found==[sector] and word(sector+4)==0x432eb0df
context=0x1000020;events=[tuple(word(word(context+12)+i*48+j*4) for j in range(4)) for i in range(word(context+8))]
releases=[e[1] for e in events if e[0]==2]
assert releases[-8:]==[0x22bf8e8]+[0]*7 and int(mesh['vertex_data'],16) in releases
unit=read(p/'mesh-register-fixtures.json');assert unit['float_fields']==[0x1808064,0x1808068,0x180806c,0x1808070]
assert all('global_bit_masks' not in s for c in unit['cases'] for s in c['steps'])
assert original['specimen_sha256']==training['specimen_sha256']==prior['specimen_sha256']
assert sha(r/'local/build/thug-core.wasm')==prior['main_wasm_sha256']
scope=(
 'Three complete routines recover raw mesh bounds, scoped mesh-node insertion and scene bounds '
 'with original x87 rounding/spill order.349 cases529 calls cover95/96 original instructions; '
 'one null-allocation instruction is excluded by the original successful-allocation contract. '
 '194 resulting center/radius NaNs compare by classification; finite outputs and all other '
 'memory compare exactly after pointer relocation. Two training cases22 calls include one '
 'interruption: node204 completes; node1289 uploads its original mesh, assigns bounds, links '
 'the mesh, frees all eight outer index slots, registers the sector and calculates scene bounds. '
 'Original4b3490 returns and stops at4b3b1c, the4b3ad0 model-wrapper continuation. Standard '
 '4c6650 and4d5cc0 paths return; transforms, layered effects and optional scene records remain '
 'explicit missing paths, so those functions are not claimed complete. Actual training has '
 'zero NaN allowances and only the same28 proven uninitialized option bytes masked. Actual '
 'Chromium passes50 suites; all48 inherited summaries are identical. Host GPU/CRT remain '
 'comparison providers. Main build unchanged; no drawing or playable gameplay yet.'
)
proof={**candidate,'recorded_at':sys.argv[4],'observed_via':'Actual Chromium PASS at '+sys.argv[5]+'; all50 summaries and complete DOM fingerprint inspected',
 'browser_dom_fingerprint':{'algorithm':'FNV-1a-64 over canonical sorted JSON characters','value':sys.argv[1],'characters':len(canonical)},'scope':scope}
files=['mesh-register-draft.c','mesh-register-sector.c','mesh-register-mesh-derived.c','mesh-register-scene-derived.c','mesh-register-material-derived.c',
 'build-mesh-register-draft.py','mesh-register-draft.wasm','mesh-register-draft.build.json','mesh-register-instructions.txt','mesh-register-inspection.txt',
 'probe-mesh-register.py','mesh-register-fixtures.json','mesh-register-memory.bin','mesh-register-original.json','mesh-register-probe.log',
 'probe-training-mesh-register.py','training-mesh-register-fixtures.json','training-mesh-register-memory.bin','training-mesh-register-original.json','training-mesh-register-probe.log',
 'training-mesh-register-boundary.c','training-mesh-register-boundary.wasm','training-mesh-register-boundary.build.json',
 'verify-mesh-register-checkpoint.mjs','mesh-register-full-node.log','mesh-register-browser.html','mesh-register-worker.mjs','serve-mesh-register.py',
 'mesh-register-browser.json','pin-mesh-register.py','audit-mesh-register.py','model-wrapper-ghidra.log']
files += ['mesh-register-checkpoint-'+n+'-result.json' for n in names]
files += [str(f.relative_to(p)) for f in sorted((p/'model-wrapper-ghidra').rglob('*')) if f.is_file()]
for name in files:
 if name!='mesh-register-browser.json':assert(p/name).is_file(),name
proof_path.write_text(json.dumps(proof,indent=2)+'\n')
artifacts=set(prior['artifact_hashes'])|{'local/analysis/vertex-upload-checkpoint.json','local/analysis/vertex-upload-audit.json'}|{'local/analysis/'+n for n in files}
pin={'result':'original, Node and actual Chromium comparisons pass; unpromoted','new_functions':3,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':275,'unpromoted_functions_across_separate_experiments':292,
 'specimen_sha256':original['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],
 'browser_suites':50,'new_cases':351,'new_calls_including_existing_dependencies':551,'new_interrupted_calls':1,'actual_training_nodes':training['nodes'],
 'instruction_coverage':coverage,'partial_geometry_load':training['partial_geometry_load'],'partial_sector_parser':training['partial_sector_parser'],'partial_mesh_buffer':training['partial_mesh_buffer'],'indeterminate_option_bytes':state['indeterminate_texture_option_bytes'],
 'source_hashes':build['source_hashes'],'artifact_hashes':{n:sha(r/n) for n in sorted(artifacts)},'harness_hashes':prior['harness_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],
 'browser_dom_fingerprint':proof['browser_dom_fingerprint'],'scope':scope}
target.write_text(json.dumps(pin,indent=2)+'\n')
print(json.dumps({'result':'pinned','artifacts':len(pin['artifact_hashes']),'sources':len(pin['source_hashes']),'checkpoint_sha256':sha(target),'main_unchanged':True}))
