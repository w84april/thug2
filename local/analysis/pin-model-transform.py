"""Freeze original, Node, and actual Chromium model transform evidence."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'model-transform-checkpoint.json';proof_path=p/'model-transform-browser.json'
assert not target.exists() and not proof_path.exists()
prior_path=p/'renderer-bounds-checkpoint.json';assert sha(prior_path)=='da661901fbea755791e06732e1266f71ece3dfefe75c209037de7c873777c42a'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'model-transform-draft.build.json');module=p/'model-transform-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='2af1a90a3af1edb9f858593e2fbe9e5b3e07f6b3039fec2aa63582d50b01d5a8'
assert module.stat().st_size==588868
previous=read(p/'renderer-bounds-browser.json')['suites'];names=['model-transform','training-model-transform']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('model-transform-checkpoint-'+n+'-result.json')) for n in names};assert len(suites)==60
for n,s in suites.items():
 assert s['result']=='pass',n
 if n in previous:assert s==previous[n],n
s=suites['model_transform'];assert(s['cases'],s['calls'],s['functions'],s['nan_fields_classification_only'],s['signaling_nan_words_quieted_per_x87'])==(390,498,11,27,16)
s=suites['training_model_transform'];assert(s['cases'],s['calls'],s['functions'],s['nan_fields_classification_only'])==(2,16,5,0)
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
original=read(p/'model-transform-original.json');coverage=original['instruction_coverage']
assert(original['cases'],original['calls'])==(390,498) and len(coverage)==10
assert sum(t['covered'] for t in coverage.values())==484 and sum(t['total'] for t in coverage.values())==484
assert all(not t['missing'] for t in coverage.values())
assert original['partial_coverage']['0x493090']['complete'] is False
unit=read(p/'model-transform-fixtures.json');assert unit['float_fields']==[] and len(unit['functions'])==11
assert 'pointer_initializers' not in unit and 'native_callbacks' not in unit
for label,c in zip(unit['case_labels'],unit['cases']):
 for s in c['steps']:
  assert 'global_bit_masks' not in s
  if label.startswith('geometry transform'):assert not s.get('float_fields') and not s.get('quiet_float_fields')
training=read(p/'training-model-transform-original.json');old=read(p/'training-renderer-bounds-original.json')
assert(training['cases'],training['calls'])==(2,16)
for k in ['io_calls','gpu_calls','index_calls','crt_calls']:assert training[k]==old[k],k
assert [n['node_index'] for n in training['nodes']]==[204,1289]
for n in training['nodes']:
 assert(n['completed_calls'],n['interrupted_calls'],n['execute_result'],n['first_missing_routine'])==(8,0,0,None)
 assert n['object_flags']=='0x60' and n['manual_script_unused']
 assert(n['owned_script']!='0x0')==(n['node_index']==204)
 for fn in ['0x41f500','0x41aad0','0x45db30','0x475790']:assert n['native_entries'][fn]==1
b=training['nodes'][1];state=b['model_state'];matrix=[0x3f800000 if i%5==0 else 0 for i in range(12)]+[0xbb27f801,0x42efffe3,0xc1f008dc,0x3f800000]
assert state['transform']['matrix_words']==[hex(v) for v in matrix] and state['transform']['enabled']==1 and state['transform']['updates']==2
assert state['owner_components']==['0xce0ca665','0xa015e17','0x1d5b1ae6','0x7713c7b','0x5cb5cb7e','0x286a8d26','0xb87c8e43']
assert state['bounds']==old['nodes'][1]['model_state']['bounds']
for fn in ['0x420480','0x4219f0','0x4215f0','0x493090','0x48de60','0x4b4630','0x48df30','0x4b47b0']:assert b['native_entries'][fn]==2
assert b['native_entries']['0x4204b0']==1
fixture=read(p/'training-model-transform-fixtures.json');annotated=[]
for i,c in enumerate(fixture['cases']):
 arena=bytearray((p/fixture['memory']).read_bytes());base=fixture['base']
 for address,data in c.get('patches',[]):arena[address-base:address-base+len(data)//2]=bytes.fromhex(data)
 for j,step in enumerate(c['steps']):
  assert not step.get('expected_trap')
  for address,data in step['outputs']:arena[address-base:address-base+len(data)//2]=bytes.fromhex(data)
  if 'global_bit_masks' in step:
   actual={}
   for index,mask in step['global_bit_masks'].items():
    name,address,width,offset=fixture['globals'][int(index)]
    assert name=='thug_asset_options_storage_draft' and address==0x691758+offset and width==4;actual[offset]=mask
   assert actual=={0:255,12:0,16:65535,56:255,60:0,64:0,68:0,72:0};annotated.append((i,j))
 assert arena[0x100e000-base:0x100e000-base+24]==bytes(24)
 assert arena[0x100c000-base:0x100c000-base+244]==bytes(244)
 word=lambda a:int.from_bytes(arena[a-base:a-base+4],'little')
 n=training['nodes'][i];obj=int(n['object'],16)
 assert word(obj+0x104)==0x60 and hex(word(obj+0x10))==n['owned_script']
 if i==1:
  component=int(state['component'],16);renderer=int(state['renderer'],16);instance=int(state['render_instance']['instance'],16)
  assert [word(instance+4+j*4) for j in range(16)]==matrix and arena[instance+0x4c-base]==1
  assert word(component+0x20c)==word(component+0x210)==0 and word(component+0x214)==word(obj+0x100)
  asset_dir=r/'local/game-files/Game/Data/models/GameObjects/SKATE/Letter_S';model_bytes=(asset_dir/'Letter_S.mdl.xbx').read_bytes()
  assert sha(asset_dir/'Letter_S.mdl.xbx')==training['model_file_sha256']==old['model_file_sha256']
  assert sha(asset_dir/'Letter_S.tex.xbx')==training['texture_file_sha256']==old['texture_file_sha256']
  for key in ['cpu_vertices','gpu_vertices']:
   at=int(state['mesh'][key],16);assert arena[at-base:at-base+3888]==model_bytes[798:4686]
  for key in ['cpu_indices','gpu_indices']:
   at=int(state['mesh'][key],16);assert arena[at-base:at-base+272]==model_bytes[503:775]
assert annotated==[(1,7)]
assert original['specimen_sha256']==training['specimen_sha256']==prior['specimen_sha256']
assert sha(r/'local/build/thug-core.wasm')==prior['main_wasm_sha256']
scope=('Ten complete original functions recover identity, timed rotation channels, pivot/mirror/offset model transforms, '
 'component finalization, animation visibility, PC geometry enable/transform and actual bone-map virtual.390 cases498 calls '
 'cover all484 instructions, plus198/273 instructions in partial493090 normal renderer transforms.27 arithmetic NaN '
 'classifications and16 exact quiet-bit corrections; raw bone copies remain exact. Both real training nodes204/1289 '
 'now complete full468cb0 creation, including synchronous script allocation/execution/destruction, added LockObj and '
 'b87c8e43 components, finalization and (node204) installed TriggerScript. The Letter S instance receives its exact '
 'owner position and enabled byte through two model updates. Complete arenas, heap, globals and file/GPU fixture '
 'records match. Training has no NaN allowances and only28 previously proven option-padding bytes are masked. '
 'All60 Chromium and Node suites pass;58 inherited summaries unchanged. General attachment, lighting, model branches, '
 'real GPU rendering, full level construction and gameplay remain incomplete. Main unchanged; not playable.')
proof={**candidate,'recorded_at':sys.argv[4],'observed_via':'Actual Chromium PASS at '+sys.argv[5]+'; all60 summaries and complete DOM fingerprint inspected',
 'browser_dom_fingerprint':{'algorithm':'FNV-1a-64 over canonical sorted JSON characters','value':sys.argv[1],'characters':len(canonical)},'scope':scope}
proof_path.write_text(json.dumps(proof,indent=2)+'\n')
files=set()
for pattern in ['model-transform-*','training-model-transform-*','*model-transform*.py','verify-model-transform-checkpoint.mjs']:
 files.update(f for f in p.glob(pattern) if f.is_file() and f not in {target,p/'model-transform-audit.json',p/'model-transform-next.txt'})
files.update(f for f in (p/'model-transform-ghidra').rglob('*') if f.is_file())
assert p/'audit-model-transform.py' in files and p/'pin-model-transform.py' in files
artifacts=set(prior['artifact_hashes'])|{'local/analysis/renderer-bounds-checkpoint.json','local/analysis/renderer-bounds-audit.json'}|{str(f.relative_to(r)) for f in files}
pin={'result':'original, Node and actual Chromium comparisons pass; unpromoted','new_functions':10,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':317,'unpromoted_functions_across_separate_experiments':334,
 'specimen_sha256':original['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],
 'browser_suites':60,'new_cases':392,'new_calls_including_existing_dependencies':514,'new_interrupted_calls':0,'actual_training_nodes':training['nodes'],
 'instruction_coverage':coverage,'partial_renderer_update':original['partial_coverage'],'partial_object_flow':training['partial_object_flow'],
 'indeterminate_option_bytes':state['indeterminate_texture_option_bytes'],'source_hashes':build['source_hashes'],
 'artifact_hashes':{n:sha(r/n) for n in sorted(artifacts)},'harness_hashes':prior['harness_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],
 'browser_dom_fingerprint':proof['browser_dom_fingerprint'],'scope':scope}
target.write_text(json.dumps(pin,indent=2)+'\n')
print(json.dumps({'result':'pinned','artifacts':len(pin['artifact_hashes']),'sources':len(pin['source_hashes']),'checkpoint_sha256':sha(target),'main_unchanged':True}))
