"""Pin original, Node and observed Chromium material parser comparisons."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'material-buffer-checkpoint.json';proof_path=p/'material-buffer-browser.json'
assert not target.exists() and not proof_path.exists()
prior_path=p/'model-asset-checkpoint.json'
assert sha(prior_path)=='b2aec22700216e69de4a09470de7272b7cb65ce2d7f5cd021bd0e95a02e4cc80'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
assert sha(p/'model-asset-browser-time-correction.json')=='70cfe9365cd0b213e4cc0211c7e04663a031b25d9334889bc9dd740863148603'
build=read(p/'material-buffer-draft.build.json');module=p/'material-buffer-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='8d9b504f041f00ba63c0d7db6ba33f66203ce42635dc81d99dcd7e20ca5cb4e5'
assert module.stat().st_size==561818
port='training-material-buffer-boundary';meta=read(p/(port+'.build.json'))
assert sha(p/(port+'.c'))==meta['source_sha256'] and sha(p/(port+'.wasm'))==meta['sha256']
previous=read(p/'model-asset-browser.json')['suites'];names=['material-buffer','training-material-buffer']+[name.replace('_','-') for name in previous]
suites={name.replace('-','_'):read(p/('material-buffer-checkpoint-'+name+'-result.json')) for name in names}
assert len(suites)==42
for name,summary in suites.items():
 assert summary['result']=='pass',name
 if name in previous:assert summary==previous[name],name
s=suites['material_buffer'];assert(s['cases'],s['calls'],s['functions'],s['nan_fields_classification_only'])==(127,134,4,0)
s=suites['training_material_buffer'];assert(s['cases'],s['calls'],s['functions'],s['nan_fields_classification_only'])==(2,22,8,0)
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
original=read(p/'material-buffer-original.json');all_coverage=original['instruction_coverage']
assert(original['cases'],original['calls'])==(127,134)
assert original['existing_dependency_addresses']==['0x4d1a90']
assert all_coverage['0x4d1a90']=={'total':40,'covered':40,'missing':[],'excluded':{}}
coverage={a:c for a,c in all_coverage.items() if a not in original['existing_dependency_addresses']}
assert set(coverage)=={'0x4d2cb0','0x4de300'}
assert sum(t['covered'] for t in coverage.values())==554 and sum(t['total'] for t in coverage.values())==566
expected={'0x4d2d05','0x4d2d35','0x4d2d5c','0x4d2d84','0x4d2f4d','0x4d2f7d','0x4d2fc3','0x4d2fed','0x4d3029','0x4d3058','0x4d30de','0x4d3146'}
for address,t in coverage.items():assert set(t['missing'])==set(t['excluded'])==(expected if address=='0x4d2cb0' else set())
asset=original['actual_asset']
assert(asset['materials'],asset['material_key'],asset['passes'],asset['flags'],asset['cursor_offset'],asset['next_geometry_count'])==(1,'0x2c56e03d',1,'0x10000024',113,1)
assert asset['gpu_calls']=={'1':1,'2':2,'3':2}
training=read(p/'training-material-buffer-original.json')
assert(training['cases'],training['calls'])==(2,22)
for part in ['partial_model_load','partial_configuration','partial_geometry_load']:
 assert training[part]['complete'] is False and training[part]['boundary']=='0x4c6130'
assert(training['partial_geometry_load']['covered_instructions'],training['partial_geometry_load']['total_instructions'])==(68,178)
assert training['io_calls']=={'0x5b6c60':2,'0x5b63a0':2,'0x5b6740':2,'0x5b68a0':1}
assert training['gpu_calls']=={'4':1,'1':1,'2':2,'3':2}
a,b=training['nodes'];assert(a['node_index'],a['completed_calls'],a['interrupted_calls'],a['execute_result'])==(204,11,0,0)
assert(b['node_index'],b['completed_calls'],b['interrupted_calls'],b['first_missing_routine'])==(1289,10,1,'0x4c6130')
state=b['model_state'];assert(state['texture_asset']['state'],state['model_asset']['state'],state['model_asset']['pending_reads'])==(4,1,0)
assert state['model_asset']['bytes']==4710 and state['texture_asset']['mip_bytes']==[32,8]
assert state['materials']=={'scene_header':'0x22bf1dc','table':'0x22bf270','material':'0x22bf2d8','key':'0x2c56e03d','count':1,'passes':1,'flags':'0x10000024','texture_resource':'0x22bde60'}
assert b['scene_constructor_request']=={'receiver':'0x22bf3f8','shift':1}
indeterminate=[1,2,3,12,13,14,15,18,19]+list(range(57,76));assert state['indeterminate_texture_option_bytes']==indeterminate
asset_dir=r/'local/game-files/Game/Data/models/GameObjects/SKATE/Letter_S'
assert sha(asset_dir/'Letter_S.mdl.xbx')==training['model_file_sha256']==asset['model_sha256']=='6411a0aecbf3cf64068fea5cf04ebe971aaeb898bff6beb33d894eebe30c6dcf'
assert sha(asset_dir/'Letter_S.tex.xbx')==training['texture_file_sha256']==asset['texture_sha256']=='66bc9d8ac9cf881dbe381764e02fb4cd86976de99ae2fecfc5842d62a10406b3'
fixture=read(p/'training-material-buffer-fixtures.json');annotated=[]
for i,c in enumerate(fixture['cases']):
 for j,step in enumerate(c['steps']):
  if 'global_bit_masks' in step:
   actual={}
   for index,mask in step['global_bit_masks'].items():
    name,address,width,offset=fixture['globals'][int(index)]
    assert name=='thug_asset_options_storage_draft' and address==0x691758+offset and width==4
    actual[offset]=mask
   assert actual=={0:255,12:0,16:65535,56:255,60:0,64:0,68:0,72:0} and step['expected_trap']
   annotated.append((i,j))
assert annotated==[(1,10)]
unit=read(p/'material-buffer-fixtures.json');assert all('global_bit_masks' not in s for c in unit['cases'] for s in c['steps'])
assert original['specimen_sha256']==training['specimen_sha256']==prior['specimen_sha256']
assert sha(r/'local/build/thug-core.wasm')==prior['main_wasm_sha256']
scope=(
 'Two complete routines recover the original material parser and scene-data header constructor. '
 '127 unit cases and134 calls cover554/566 new instructions. Twelve exclusions comprise eight heap '
 'bootstrap calls, three allocation-failure branches and one unreachable alignment instruction; '
 'the internal contract requires initialized heap, successful allocations, bounded complete data '
 'and at most four passes. The existing material constructor is reused and covered40/40, not counted new. '
 'Tests include duplicates, table growth through its cap, direct/indirect/missing texture resources, '
 'UV/channel/texture animations, retained bytes, unsigned alpha and exact floating-point edge cases. '
 'Two unchanged training cases22 calls include one interrupted call. Node204 completes; node1289 '
 'loads the real Letter S texture/model, parses its material and binds the texture resource. '
 'Partial48c030/4b3ad0/4b3490 advance to scene construction at4c6130 without fabricating geometry. '
 'The complete arena, heap, cursor, I/O, GPU and material bytes compare after pointer relocation. '
 'Only28 previously proven uninitialized option bytes are masked in one interrupted training call; '
 'unit suites compare all bytes and both new suites have zero NaN allowances. Actual Chromium '
 'passes42 suites and all40 inherited summaries are identical. Original bootstrap, production '
 'browser file/GPU providers, complete scene geometry/rendering and playable gameplay remain '
 'pending. Main and separate physics builds remain unchanged.'
)
proof={**candidate,'recorded_at':sys.argv[4],'observed_via':'Actual Chromium PASS at '+sys.argv[5]+'; all42 summaries and complete DOM fingerprint inspected',
 'browser_dom_fingerprint':{'algorithm':'FNV-1a-64 over canonical sorted JSON characters','value':sys.argv[1],'characters':len(canonical)},'scope':scope}
files=['material-buffer-draft.c','material-model-asset-derived.c','material-texture-derived.c','material-factory-derived.c',
 'build-material-buffer-draft.py','material-buffer-draft.wasm','material-buffer-draft.build.json','material-buffer-instructions.txt',
 'probe-material-buffer.py','material-buffer-fixtures.json','material-buffer-memory.bin','material-buffer-original.json','material-buffer-probe.log',
 'probe-training-material-buffer.py','training-material-buffer-fixtures.json','training-material-buffer-memory.bin','training-material-buffer-original.json','training-material-buffer-probe.log',
 'verify-material-buffer-checkpoint.mjs','material-buffer-full-node.log','material-buffer-browser.html','material-buffer-worker.mjs','serve-material-buffer.py',
 'material-buffer-browser.json','pin-material-buffer.py','audit-material-buffer.py']
files += [port+suffix for suffix in ['.c','.wasm','.build.json']]
files += ['material-buffer-checkpoint-'+name+'-result.json' for name in names]
for name in files:
 if name!='material-buffer-browser.json':assert(p/name).is_file(),name
proof_path.write_text(json.dumps(proof,indent=2)+'\n')
artifacts=set(prior['artifact_hashes'])|{'local/analysis/model-asset-checkpoint.json','local/analysis/model-asset-audit.json','local/analysis/model-asset-browser-time-correction.json'}|{'local/analysis/'+n for n in files}
pin={'result':'original, Node and actual Chromium comparisons pass; unpromoted','new_functions':2,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':254,'unpromoted_functions_across_separate_experiments':271,
 'specimen_sha256':original['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],
 'browser_suites':42,'new_cases':129,'new_calls_including_existing_dependencies':156,'new_interrupted_calls':1,'actual_training_nodes':training['nodes'],
 'instruction_coverage':coverage,'existing_dependency_coverage':{'0x4d1a90':all_coverage['0x4d1a90']},
 'partial_geometry_load':training['partial_geometry_load'],'indeterminate_option_bytes':indeterminate,
 'source_hashes':build['source_hashes'],'artifact_hashes':{n:sha(r/n) for n in sorted(artifacts)},'harness_hashes':prior['harness_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],
 'browser_dom_fingerprint':proof['browser_dom_fingerprint'],'scope':scope}
target.write_text(json.dumps(pin,indent=2)+'\n')
print(json.dumps({'result':'pinned','artifacts':len(pin['artifact_hashes']),'sources':len(pin['source_hashes']),'checkpoint_sha256':sha(target),'main_unchanged':True}))
