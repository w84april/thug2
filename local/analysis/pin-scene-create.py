"""Freeze original, Node and observed Chromium startup-object comparisons."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'scene-create-checkpoint.json';proof_path=p/'scene-create-browser.json'
assert not target.exists() and not proof_path.exists()
prior_path=p/'model-transform-checkpoint.json'
assert sha(prior_path)=='644b1fe34a22f089532b0fe0297111af004b18456d0827f6e75350546cec93c6'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'scene-create-draft.build.json');module=p/'scene-create-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='dbc801dbfb901296a77df7a4940cee1e5e25cb656e86843760e3600779518f76'
assert module.stat().st_size==590545
previous=read(p/'model-transform-browser.json')['suites'];names=['scene-create','training-scene-create']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('scene-create-checkpoint-'+n+'-result.json')) for n in names};assert len(suites)==62
for n,s in suites.items():
 assert s['result']=='pass',n
 if n in previous:assert s==previous[n],n
for name,expected in [('scene_create',(24,46,2,0)),('training_scene_create',(2,49,9,0))]:
 s=suites[name];assert(s['cases'],s['calls'],s['functions'],s['nan_fields_classification_only'])==expected
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
original=read(p/'scene-create-original.json');coverage=original['instruction_coverage']
assert(original['cases'],original['calls'])==(24,46) and set(coverage)=={'0x433d90','0x433900'}
assert sum(t['covered'] for t in coverage.values())==sum(t['total'] for t in coverage.values())==50
assert all(not t['missing'] for t in coverage.values())
unit=read(p/'scene-create-fixtures.json');assert unit['float_fields']==[] and len(unit['functions'])==2
assert 'pointer_initializers' not in unit and 'native_callbacks' not in unit
for c in unit['cases']:
 for s in c['steps']:assert not s.get('expected_trap') and 'global_bit_masks' not in s
port=read(p/'scene-create-memory.build.json')
assert sha(p/'scene-create-memory.c')==port['source_sha256'] and sha(p/'scene-create-memory.wasm')==port['sha256']
training=read(p/'training-scene-create-original.json');assert(training['cases'],training['calls'])==(2,49)
inventory=read(p/'training-scene-node-inventory.json');startup=training['startup_gameobjects']
expected=[n for n in inventory['nodes'] if n['class_text']=='GameObject' and n['created_at_start']]
assert len(startup)==len(expected)==28 and [n['index'] for n in startup]==[n['index'] for n in expected]
assert [hex(n['name']) for n in startup]==[n['name'] for n in expected]
letter=inventory['nodes'][1289];assert letter['index']==1289 and not letter['created_at_start']
a,b=training['case_details'];assert(a['calls'],b['calls'])==(37,12)
assert(a['live_count'],a['component_count'],len(a['created_objects']))==(29,177,29)
assert set(a['created_objects'])=={n['object'] for n in a['live_objects']}
assert {n['name'] for n in a['live_objects']}=={n['name'] for n in expected}|{letter['name']}
assert set(a['simple_sound_objects'])=={'0x77ab27bc','0xabc634f'}
assert sorted(len(n['components']) for n in a['live_objects'])==[6]*26+[7]*3
for fn,count in [('0x5a4ff0',28),('0x5b0a40',28),('0x5a34d0',1),('0x468eb0',29),('0x475790',29),('0x45db30',29),('0x433d90',2)]:assert a['native_entries'][fn]==count
assert(b['live_count'],len(b['created_objects']))==(19,38)
assert {n['object'] for n in b['live_objects']}==set(b['created_objects'][19:])
prefix_names={n['name'] for n in expected if n['text'].startswith('TRG_SFX_Ghost_PipeBust')}
assert len(prefix_names)==19 and {n['name'] for n in b['live_objects']}==prefix_names
assert all(len(n['components'])==6 for n in b['live_objects']) and b['model'] is None
for fn,count in [('0x5a4ff0',2),('0x5a5030',1),('0x5a32c0',19),('0x45e620',19),('0x468eb0',38)]:assert b['native_entries'][fn]==count
assert all(c['complete'] is False for c in training['partial_creation_coverage'].values())
state=a['model'];matrix=[0x3f800000 if i%5==0 else 0 for i in range(12)]+[0xbb27f801,0x42efffe3,0xc1f008dc,0x3f800000]
assert state['matrix']==[hex(v) for v in matrix] and(state['enabled'],state['vertices'],state['indices'])==(1,108,136)
asset_dir=r/'local/game-files/Game/Data/models/GameObjects/SKATE/Letter_S';model_bytes=(asset_dir/'Letter_S.mdl.xbx').read_bytes()
old=read(p/'training-model-transform-original.json')
assert sha(asset_dir/'Letter_S.mdl.xbx')==training['model_file_sha256']==old['model_file_sha256']
assert sha(asset_dir/'Letter_S.tex.xbx')==training['texture_file_sha256']==old['texture_file_sha256']
fixture=read(p/'training-scene-create-fixtures.json');annotated=[];base=fixture['base'];head=base+0xa1000+4
assert not any(c.get('original')==0x433d90 for c in fixture['native_callbacks'])
for i,c in enumerate(fixture['cases']):
 arena=bytearray((p/fixture['memory']).read_bytes())
 for address,data in c.get('patches',[]):arena[address-base:address-base+len(data)//2]=bytes.fromhex(data)
 word=lambda address:int.from_bytes(arena[address-base:address-base+4],'little')
 def live():
  result=[];node=word(head+12)
  while node!=head:
   assert node and len(result)<80;result.append(word(node+4));node=word(node+12)
  return result
 for j,step in enumerate(c['steps']):
  assert not step.get('expected_trap')
  for address,data in step['outputs']:arena[address-base:address-base+len(data)//2]=bytes.fromhex(data)
  if 'global_bit_masks' in step:
   actual={}
   for index,mask in step['global_bit_masks'].items():
    name,address,width,offset=fixture['globals'][int(index)]
    assert name=='thug_asset_options_storage_draft' and address==0x691758+offset and width==4;actual[offset]=mask
   assert actual=={0:255,12:0,16:65535,56:255,60:0,64:0,68:0,72:0};annotated.append((i,j))
  if i==0 and j>=8:assert len(live())==j-7
  if i==1 and j in [8,9,10,11]:assert len(live())=={8:19,9:0,10:0,11:19}[j]
 assert arena[0x100e000-base:0x100e000-base+24]==bytes(24)
 assert arena[0x100c000-base:0x100c000-base+244]!=bytes(244)
 detail=training['case_details'][i];assert [hex(v) for v in live()]==[n['object'] for n in detail['live_objects']]
 for n in detail['live_objects']:
  obj=int(n['object'],16);assert word(obj+0x104)==0x60 and hex(word(obj+0x10))==n['script'] and hex(word(obj+0x14))==n['name']
  component=word(obj+0x100)
  for comp in n['components']:
   assert hex(component)==comp['address'] and hex(word(component+4))==comp['type'];component=word(component+16)
  assert component==0
 if i==0:
  obj=int(state['object'],16);component=int(state['component'],16);instance=int(state['instance'],16)
  assert [word(instance+4+j*4) for j in range(16)]==matrix and arena[instance+0x4c-base]==1
  assert [word(obj+0x4c+j*4) for j in range(4)]==matrix[12:]
  assert word(component+0x20c)==word(component+0x210)==0 and word(component+0x214)==word(obj+0x100)
  for key in ['cpu_vertices','gpu_vertices']:
   at=int(state[key],16);assert arena[at-base:at-base+3888]==model_bytes[798:4686]
  for key in ['cpu_indices','gpu_indices']:
   at=int(state[key],16);assert arena[at-base:at-base+272]==model_bytes[503:775]
assert annotated==[(0,36)]
assert original['specimen_sha256']==training['specimen_sha256']==prior['specimen_sha256']
assert sha(r/'local/build/thug-core.wasm')==prior['main_wasm_sha256']
scope=('Two complete SimpleSound factory/initializer routines cover all50 original instructions in24 cases46 calls, '
 'including allocation failure. Partial original Create orchestration constructs all28 training GameObjects marked '
 'CreatedAtStart in one live registry, including2 SimpleSound components. CreateFromStructure adds dynamic Letter S: '
 '29live objects177 components, exact model/texture payloads and owner transform. A second real prefix Create/Kill '
 'case constructs19 pipe-bust objects, destroys all19, flushes and recreates19. Two training cases49 calls compare '
 'whole arenas/globals/heap and CPU/GPU fixture bytes with no NaN allowances; only28 proven texture-option padding '
 'bytes are masked. All62 Node and actual Chromium suites pass;60 inherited summaries unchanged. Other classes '
 'explicitly trap; full scene boot, sound playback/destruction, real GPU drawing and gameplay remain incomplete. '
 'These are startup GameObjects only, not the full level. Main unchanged; not playable.')
proof={**candidate,'recorded_at':sys.argv[4],'observed_via':'Actual Chromium PASS at '+sys.argv[5]+'; all62 summaries and complete DOM fingerprint inspected',
 'browser_dom_fingerprint':{'algorithm':'FNV-1a-64 over canonical sorted JSON characters','value':sys.argv[1],'characters':len(canonical)},'scope':scope}
proof_path.write_text(json.dumps(proof,indent=2)+'\n')
files=set()
for pattern in ['scene-create-*','training-scene-create-*','*scene-create*.py','verify-scene-create-checkpoint.mjs']:
 files.update(f for f in p.glob(pattern) if f.is_file() and f not in {target,p/'scene-create-audit.json',p/'scene-create-next.txt'})
files.update([p/'trace-training-object-expansion.py',p/'training-object-expansion-trace.log'])
assert p/'audit-scene-create.py' in files and p/'pin-scene-create.py' in files
artifacts=set(prior['artifact_hashes'])|{'local/analysis/model-transform-checkpoint.json','local/analysis/model-transform-audit.json'}|{str(f.relative_to(r)) for f in files}
pin={'result':'original, Node and actual Chromium comparisons pass; unpromoted','new_functions':2,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':319,'unpromoted_functions_across_separate_experiments':336,
 'specimen_sha256':original['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],
 'browser_suites':62,'new_cases':26,'new_calls_including_existing_dependencies':95,'new_interrupted_calls':0,
 'startup_gameobjects':startup,'actual_training_cases':training['case_details'],'instruction_coverage':coverage,
 'partial_creation_coverage':training['partial_creation_coverage'],'indeterminate_option_bytes':28,'source_hashes':build['source_hashes'],
 'artifact_hashes':{n:sha(r/n) for n in sorted(artifacts)},'harness_hashes':prior['harness_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],
 'browser_dom_fingerprint':proof['browser_dom_fingerprint'],'scope':scope}
target.write_text(json.dumps(pin,indent=2)+'\n')
print(json.dumps({'result':'pinned','artifacts':len(pin['artifact_hashes']),'sources':len(pin['source_hashes']),'checkpoint_sha256':sha(target),'main_unchanged':True}))
