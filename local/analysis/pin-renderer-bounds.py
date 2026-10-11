"""Freeze original, Node and observed Chromium bounds/initializer evidence."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'renderer-bounds-checkpoint.json';proof_path=p/'renderer-bounds-browser.json'
assert not target.exists() and not proof_path.exists()
prior_path=p/'render-instance-checkpoint.json';assert sha(prior_path)=='b04d9ae4612f31b039f6afa01f03212c98a4108cccfa4e41bfcbb70db6a08f00'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'renderer-bounds-draft.build.json');module=p/'renderer-bounds-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='e86e36bb420d4aa0f62be04671280259c49e044ea01eb892e0f8470efec8af2b'
assert module.stat().st_size==583581
previous=read(p/'render-instance-browser.json')['suites'];names=['renderer-bounds','training-renderer-bounds']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('renderer-bounds-checkpoint-'+n+'-result.json')) for n in names};assert len(suites)==58
for n,s in suites.items():
 assert s['result']=='pass',n
 if n in previous:assert s==previous[n],n
s=suites['renderer_bounds'];assert(s['cases'],s['calls'],s['functions'],s['nan_fields_classification_only'],s['signaling_nan_words_quieted_per_x87'])==(393,573,4,118,52)
s=suites['training_renderer_bounds'];assert(s['cases'],s['calls'],s['functions'],s['nan_fields_classification_only'])==(2,22,8,0)
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
original=read(p/'renderer-bounds-original.json');coverage=original['instruction_coverage']
assert(original['cases'],original['calls'])==(393,573) and len(coverage)==4
assert sum(t['covered'] for t in coverage.values())==214 and sum(t['total'] for t in coverage.values())==214
assert all(not t['missing'] for t in coverage.values())
unit=read(p/'renderer-bounds-fixtures.json');assert unit['float_fields']==[] and len(unit['functions'])==4
assert 'pointer_initializers' not in unit and 'native_callbacks' not in unit
assert sha(p/'renderer-bounds-fixtures.json')==read(p/'renderer-bounds-comparison-refinement.json')['after_sha256']
for label,c in zip(unit['case_labels'],unit['cases']):
 for s in c['steps']:
  assert 'global_bit_masks' not in s
  if label.startswith('cached '):assert not s.get('float_fields') and not s.get('quiet_float_fields')
  if label.startswith('merge raw random') and int(label.split('random')[1])%5==0:
   assert s['quiet_float_fields']==[0x1808800,0x1808804,0x1808808,0x1808034,0x1808038,0x180803c]
   assert s['float_fields']==[0x180880c,0x1808040]
training=read(p/'training-renderer-bounds-original.json');old_training=read(p/'training-render-instance-original.json')
assert(training['cases'],training['calls'])==(2,22)
for part in ['partial_model_load','partial_configuration','partial_geometry_load','partial_mesh_buffer','partial_sector_parser']:
 assert training[part]['complete'] is False and training[part]['boundary'] is None
 assert set(old_training[part]['executed'])<=set(training[part]['executed'])
for k in ['io_calls','gpu_calls','index_calls','crt_calls']:assert training[k]==old_training[k]
for n in training['nodes']:
 assert(n['completed_calls'],n['interrupted_calls'],n['execute_result'],n['final_instruction'],n['first_missing_routine'])==(11,0,0,'0x0',None)
assert [n['node_index'] for n in training['nodes']]==[204,1289]
b=training['nodes'][1];state=b['model_state'];old_state=old_training['nodes'][1]['model_state']
assert {k:v for k,v in state.items() if k not in ['bounds','renderer_flags']}=={k:v for k,v in old_state.items() if k!='renderer_flags'}
assert old_state['renderer_flags']==2 and state['renderer_flags']==3
bounds=state['bounds'];assert bounds['words']==['0xbdc00000','0x0','0x0','0x421f3526'] and bounds['owner_flags']==0 and bounds['cache_valid'] and not bounds['skeleton_cache_branch']
for fn in ['0x4b4760','0x48de90','0x4bae30','0x492f30']:assert b['native_entries'][fn]==1
assert b['native_entries'].get('0x420350',0)==0
assert training['partial_configuration']['covered_instructions']==155 and old_training['partial_configuration']['covered_instructions']==125
asset_dir=r/'local/game-files/Game/Data/models/GameObjects/SKATE/Letter_S'
assert sha(asset_dir/'Letter_S.mdl.xbx')==training['model_file_sha256']==old_training['model_file_sha256']
assert sha(asset_dir/'Letter_S.tex.xbx')==training['texture_file_sha256']==old_training['texture_file_sha256']
fixture=read(p/'training-renderer-bounds-fixtures.json');annotated=[]
for i,c in enumerate(fixture['cases']):
 for j,step in enumerate(c['steps']):
  assert not step.get('expected_trap')
  if 'global_bit_masks' in step:
   actual={}
   for index,mask in step['global_bit_masks'].items():
    name,address,width,offset=fixture['globals'][int(index)]
    assert name=='thug_asset_options_storage_draft' and address==0x691758+offset and width==4;actual[offset]=mask
   assert actual=={0:255,12:0,16:65535,56:255,60:0,64:0,68:0,72:0};annotated.append((i,j))
assert annotated==[(1,10)]
assert all(x[0]!='thug_model_renderer_ready_pending_draft' for x in fixture['pointer_initializers'])
arena=bytearray((p/fixture['memory']).read_bytes());base=fixture['base'];case=fixture['cases'][1]
for address,data in case.get('patches',[]):arena[address-base:address-base+len(data)//2]=bytes.fromhex(data)
for step in case['steps']:
 for address,data in step['outputs']:arena[address-base:address-base+len(data)//2]=bytes.fromhex(data)
word=lambda a:int.from_bytes(arena[a-base:a-base+4],'little')
component=int(state['component'],16);renderer=int(state['renderer'],16)
assert [word(component+0x18+i*4) for i in range(4)]==[int(v,16) for v in bounds['words']]
assert [word(renderer+0x34+i*4) for i in range(4)]==[int(v,16) for v in bounds['words']]
assert arena[renderer+0x44-base]==3 and word(0x100c00c)==0
assert arena[0x100e000-base:0x100e000-base+24]==bytes(24)
model_bytes=(asset_dir/'Letter_S.mdl.xbx').read_bytes()
for key in ['cpu_vertices','gpu_vertices']:
 at=int(state['mesh'][key],16);assert arena[at-base:at-base+3888]==model_bytes[798:4686]
for key in ['cpu_indices','gpu_indices']:
 at=int(state['mesh'][key],16);assert arena[at-base:at-base+272]==model_bytes[503:775]
asset=int(state['model_asset']['asset'],16);assert word(asset+8)==4 and word(asset+0x10)==int(state['model_object']['object'],16)
assert original['specimen_sha256']==training['specimen_sha256']==prior['specimen_sha256']
assert sha(r/'local/build/thug-core.wasm')==prior['main_wasm_sha256']
scope=(
 'Four routines recover PC geometry sphere access, virtual forwarding, multi-part sphere merging '
 'and renderer bounds caching.393 cases573 calls execute all214 original instructions. Exact '
 'x87 operation/spill order, ordered-equality containment, raw cache overlap and geometry getter '
 'quieting are retained.118 arithmetic NaN fields use classification;52 copied signaling words '
 'require the exact quiet bit with original sign/payload. Actual training nodes204 and1289 now '
 'both finish gameobj_add_components with return0 and null instruction:22 completed calls and '
 'zero interruptions. The real Letter S component and renderer bounds match exactly. Text-model '
 'configuration and initializer return and scoped services restore. No configuration breakpoint '
 'is installed. The owner update and skeleton-cache branches are not taken and remain explicit '
 'traps in the partial configuration. Training has zero NaN allowances, and only the same28 '
 'proven option padding bytes are masked. Chromium passes58 suites with all56 inherited summaries '
 'unchanged. Main unchanged. This is not full468cb0 prop creation, finalized scene, drawing or gameplay.'
)
proof={**candidate,'recorded_at':sys.argv[4],'observed_via':'Actual Chromium PASS at '+sys.argv[5]+'; all58 summaries and complete DOM fingerprint inspected',
 'browser_dom_fingerprint':{'algorithm':'FNV-1a-64 over canonical sorted JSON characters','value':sys.argv[1],'characters':len(canonical)},'scope':scope}
files=['renderer-bounds-draft.c','renderer-bounds-component-derived.c','renderer-bounds-initialize-derived.c','renderer-bounds-configuration-derived.c',
 'build-renderer-bounds-draft.py','renderer-bounds-draft.wasm','renderer-bounds-draft.build.json','renderer-bounds-inspection.txt','renderer-bounds-object-creation-inspection.txt',
 'probe-renderer-bounds.py','renderer-bounds-fixtures.json','renderer-bounds-memory.bin','renderer-bounds-original.json','renderer-bounds-probe.log','renderer-bounds-comparison-refinement.json',
 'trace-renderer-bounds-training.py','renderer-bounds-training-trace.log',
 'probe-training-renderer-bounds.py','training-renderer-bounds-fixtures.json','training-renderer-bounds-memory.bin','training-renderer-bounds-original.json','training-renderer-bounds-probe.log',
 'verify-renderer-bounds-checkpoint.mjs','renderer-bounds-full-node.log','renderer-bounds-browser.html','renderer-bounds-worker.mjs','serve-renderer-bounds.py',
 'renderer-bounds-browser.json','pin-renderer-bounds.py','audit-renderer-bounds.py']
files += ['renderer-bounds-checkpoint-'+n+'-result.json' for n in names]
for name in files:
 if name!='renderer-bounds-browser.json':assert(p/name).is_file(),name
proof_path.write_text(json.dumps(proof,indent=2)+'\n')
artifacts=set(prior['artifact_hashes'])|{'local/analysis/render-instance-checkpoint.json','local/analysis/render-instance-audit.json'}|{'local/analysis/'+n for n in files}
pin={'result':'original, Node and actual Chromium comparisons pass; unpromoted','new_functions':4,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':307,'unpromoted_functions_across_separate_experiments':324,
 'specimen_sha256':original['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],
 'browser_suites':58,'new_cases':395,'new_calls_including_existing_dependencies':595,'new_interrupted_calls':0,'actual_training_nodes':training['nodes'],
 'instruction_coverage':coverage,'partial_geometry_load':training['partial_geometry_load'],'partial_sector_parser':training['partial_sector_parser'],'partial_mesh_buffer':training['partial_mesh_buffer'],
 'partial_configuration':training['partial_configuration'],'indeterminate_option_bytes':state['indeterminate_texture_option_bytes'],
 'source_hashes':build['source_hashes'],'artifact_hashes':{n:sha(r/n) for n in sorted(artifacts)},'harness_hashes':prior['harness_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],
 'browser_dom_fingerprint':proof['browser_dom_fingerprint'],'scope':scope}
target.write_text(json.dumps(pin,indent=2)+'\n')
print(json.dumps({'result':'pinned','artifacts':len(pin['artifact_hashes']),'sources':len(pin['source_hashes']),'checkpoint_sha256':sha(target),'main_unchanged':True}))
