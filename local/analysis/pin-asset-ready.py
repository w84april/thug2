"""Freeze original, Node and actual Chromium model asset comparisons."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'asset-ready-checkpoint.json';proof_path=p/'asset-ready-browser.json'
assert not target.exists() and not proof_path.exists()
prior_path=p/'scene-finalize-checkpoint.json';assert sha(prior_path)=='ebb57510cd9b0a88f158e433852d6a46b1176923a1330f4d13cbb255ba766ac2'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'asset-ready-draft.build.json');module=p/'asset-ready-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='0713dbd552e2e2c7dd07f3beb42961bd943bc16a3fd1d179b6e66ea6c55cb390'
assert module.stat().st_size==580205
meta=read(p/'training-asset-ready-boundary.build.json')
assert sha(p/'training-asset-ready-boundary.c')==meta['source_sha256'] and sha(p/'training-asset-ready-boundary.wasm')==meta['sha256']
previous=read(p/'scene-finalize-browser.json')['suites'];names=['asset-ready','training-asset-ready']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('asset-ready-checkpoint-'+n+'-result.json')) for n in names};assert len(suites)==54
for n,s in suites.items():
 assert s['result']=='pass',n
 if n in previous:assert s==previous[n],n
s=suites['asset_ready'];assert(s['cases'],s['calls'],s['functions'],s['nan_fields_classification_only'])==(142,184,5,0)
s=suites['training_asset_ready'];assert(s['cases'],s['calls'],s['functions'],s['nan_fields_classification_only'])==(2,22,8,0)
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
original=read(p/'asset-ready-original.json');coverage=original['instruction_coverage']
assert(original['cases'],original['calls'])==(142,184) and len(coverage)==4
assert sum(t['covered'] for t in coverage.values())==185 and sum(t['total'] for t in coverage.values())==186
for a,c in coverage.items():
 c['excluded']={'0x4b7ca3':'initialized heap contract'} if a=='0x4b7c60' else {}
 assert set(c['missing'])==set(c['excluded']),(a,c)
training=read(p/'training-asset-ready-original.json');old_training=read(p/'training-scene-finalize-original.json')
assert(training['cases'],training['calls'])==(2,22)
for part in ['partial_model_load','partial_configuration','partial_geometry_load','partial_mesh_buffer','partial_sector_parser']:
 assert training[part]['complete'] is False and training[part]['boundary']=='0x493798'
 assert set(old_training[part]['executed'])<=set(training[part]['executed'])
for k in ['gpu_calls','index_calls','crt_calls']:assert training[k]==old_training[k]
assert training['io_calls']=={**old_training['io_calls'],'0x5b68a0':2}
a,b=training['nodes'];assert(a['node_index'],a['completed_calls'],a['interrupted_calls'],a['execute_result'])==(204,11,0,0)
assert(b['node_index'],b['completed_calls'],b['interrupted_calls'],b['first_missing_routine'])==(1289,10,1,'0x493798')
state=b['model_state'];old_state=old_training['nodes'][1]['model_state']
assert {k:v for k,v in state.items() if k!='model_asset'}=={k:v for k,v in old_state.items() if k!='model_asset'}
asset=state['model_asset'];model=state['model_object'];mesh=state['mesh'];scene=state['scene']
assert asset=={**old_state['model_asset'],'state':4,'data':model['object']}
assert b['asset_continuation']=={'model':model['object'],'instruction':'0x493798','renderer':state['renderer'],'part':'0x22bdcfc'}
for fn in ['0x409c70','0x4b7eb0','0x409cb0']:assert b['native_entries'][fn]==1
for fn in ['0x4076e0','0x407630']:assert b['native_entries'][fn]==2
asset_dir=r/'local/game-files/Game/Data/models/GameObjects/SKATE/Letter_S'
assert sha(asset_dir/'Letter_S.mdl.xbx')==training['model_file_sha256']==old_training['model_file_sha256']
assert sha(asset_dir/'Letter_S.tex.xbx')==training['texture_file_sha256']==old_training['texture_file_sha256']
fixture=read(p/'training-asset-ready-fixtures.json');annotated=[]
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
model_bytes=(asset_dir/'Letter_S.mdl.xbx').read_bytes()
for key in ['cpu_vertices','gpu_vertices']:
 at=int(mesh[key],16);assert arena[at-base:at-base+3888]==model_bytes[798:4686]
at=int(asset['asset'],16);texture=int(state['texture_asset']['asset'],16);model_at=int(model['object'],16)
assert word(at+8)==4 and word(at+0x10)==model_at and word(at+0x24)==int(asset['buffer'],16)
assert all(word(at+o)==0 for o in [0x20,0x50,0x54,0x58,0x5c])
assert word(model_at)==0x64a490 and word(model_at+4)==int(model['dictionary'],16) and word(model_at+0xc4)==int(scene['scene'],16)
manager=0x10f0000;table=word(manager+0x1c);assert word(table+8)==2 and word(manager+0x20)==texture
buckets=word(table+4);values={word(buckets+i*12+4) for i in range(1<<word(table)) if word(buckets+i*12+4)}
assert values=={at,texture}
assert [word(at+0x2c),word(at+0x30),word(texture+0x2c),word(texture+0x30)]==[texture,texture,at,at]
mask_index=next(i for i,g in enumerate(fixture['globals']) if g[0]=='thug_asset_options_mask_draft');assert case['steps'][-1]['globals'][mask_index]==0
assert [word(0x100e000+i*4) for i in range(6)]==[0x493798,model_at,int(state['renderer'],16),1,0x22bdcfc,0]
io=0x10f0600;assert word(io+12)==8
last=word(io+16)+7*32;assert word(last)==4 and word(last+4)==0x10f4080
unit=read(p/'asset-ready-fixtures.json');assert unit['float_fields']==[] and len(unit['functions'])==6
assert 'pointer_initializers' not in unit and len(unit['native_callbacks'])==7
assert all('global_bit_masks' not in s for c in unit['cases'] for s in c['steps'])
assert original['specimen_sha256']==training['specimen_sha256']==prior['specimen_sha256']
assert sha(r/'local/build/thug-core.wasm')==prior['main_wasm_sha256']
scope=(
 'Four routines recover companion record comparison, parsing and loading, and the full model asset '
 'parse/finalization routine409c70. Actual original model wrappers run on zero-sector model files '
 'in142 cases184 calls, covering185/186 instructions with one initialized-heap bootstrap exclusion. '
 'No parser success is substituted; every cleanup branch, ordinary file close and cached release '
 'is exercised. The returned model now flows through the original asset code. Two actual training '
 'cases22 calls include one interruption: node204 completes; node1289 attaches the Letter S model '
 'to its asset, closes the input file, releases options, reaches state4 and registers the asset '
 'in the manager. It reaches493798 after the manager returns, before renderer association. '
 'All uploaded mesh bytes, scene/model state and GPU/CRT calls are preserved; I/O gains one '
 'model-file close. New comparisons have zero NaN allowances and only the same28 proven option '
 'padding bytes are masked. Chromium passes54 suites with all52 inherited summaries unchanged. '
 'The main build is unchanged. General geometry paths, rendering and playable gameplay remain incomplete.'
)
proof={**candidate,'recorded_at':sys.argv[4],'observed_via':'Actual Chromium PASS at '+sys.argv[5]+'; all54 summaries and complete DOM fingerprint inspected',
 'browser_dom_fingerprint':{'algorithm':'FNV-1a-64 over canonical sorted JSON characters','value':sys.argv[1],'characters':len(canonical)},'scope':scope}
files=['asset-ready-draft.c','asset-ready-factory-derived.c','asset-ready-texture-derived.c','asset-ready-model-derived.c','asset-ready-material-derived.c','asset-ready-load-derived.c',
 'build-asset-ready-draft.py','asset-ready-draft.wasm','asset-ready-draft.build.json','asset-ready-inspection.txt','asset-ready-renderer-inspection.txt','asset-ready-renderer-ghidra.log',
 'probe-asset-ready.py','asset-ready-fixtures.json','asset-ready-memory.bin','asset-ready-original.json','asset-ready-probe.log',
 'probe-training-asset-ready.py','training-asset-ready-fixtures.json','training-asset-ready-memory.bin','training-asset-ready-original.json','training-asset-ready-probe.log','asset-ready-training-ports-setup.py',
 'training-asset-ready-boundary.c','training-asset-ready-boundary.wasm','training-asset-ready-boundary.build.json',
 'verify-asset-ready-checkpoint.mjs','asset-ready-full-node.log','asset-ready-browser.html','asset-ready-worker.mjs','serve-asset-ready.py',
 'asset-ready-browser.json','pin-asset-ready.py','audit-asset-ready.py']
files += ['asset-ready-checkpoint-'+n+'-result.json' for n in names]
files += [str(f.relative_to(p)) for f in sorted((p/'asset-ready-renderer-ghidra').rglob('*')) if f.is_file()]
for name in files:
 if name!='asset-ready-browser.json':assert(p/name).is_file(),name
proof_path.write_text(json.dumps(proof,indent=2)+'\n')
artifacts=set(prior['artifact_hashes'])|{'local/analysis/scene-finalize-checkpoint.json','local/analysis/scene-finalize-audit.json'}|{'local/analysis/'+n for n in files}
pin={'result':'original, Node and actual Chromium comparisons pass; unpromoted','new_functions':4,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':297,'unpromoted_functions_across_separate_experiments':314,
 'specimen_sha256':original['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],
 'browser_suites':54,'new_cases':144,'new_calls_including_existing_dependencies':206,'new_interrupted_calls':1,'actual_training_nodes':training['nodes'],
 'instruction_coverage':coverage,'partial_geometry_load':training['partial_geometry_load'],'partial_sector_parser':training['partial_sector_parser'],'partial_mesh_buffer':training['partial_mesh_buffer'],'indeterminate_option_bytes':state['indeterminate_texture_option_bytes'],
 'source_hashes':build['source_hashes'],'artifact_hashes':{n:sha(r/n) for n in sorted(artifacts)},'harness_hashes':prior['harness_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],
 'browser_dom_fingerprint':proof['browser_dom_fingerprint'],'scope':scope}
target.write_text(json.dumps(pin,indent=2)+'\n')
print(json.dumps({'result':'pinned','artifacts':len(pin['artifact_hashes']),'sources':len(pin['source_hashes']),'checkpoint_sha256':sha(target),'main_unchanged':True}))
