"""Freeze original, Node and observed Chromium training material evidence."""
import hashlib,json,struct,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'level-material-checkpoint.json';proof_path=p/'level-material-browser.json'
assert not target.exists() and not proof_path.exists()
prior_path=p/'scene-create-checkpoint.json';assert sha(prior_path)=='67762a7475423333e1189bda72df1fc7eef43485f012e24b6397df81bf811276'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'level-material-draft.build.json');module=p/'level-material-draft.wasm';assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='179a775129673c320e32fc626eb5ed54f11c0d2c7381fbe7407c18faac010612'
assert module.stat().st_size==593740
previous=read(p/'scene-create-browser.json')['suites'];names=['level-material','training-level-material']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('level-material-checkpoint-'+n+'-result.json')) for n in names};assert len(suites)==64
for n,s in suites.items():
 assert s['result']=='pass',n
 if n in previous:assert s==previous[n],n
for name,expected in [('level_material',(127,134,4,0)),('training_level_material',(1,2,2,0))]:
 s=suites[name];assert(s['cases'],s['calls'],s['functions'],s['nan_fields_classification_only'])==expected
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
original=read(p/'level-material-original.json');coverage=original['instruction_coverage']['0x4d3390']
assert(original['cases'],original['calls'])==(127,134)
assert(coverage['covered'],coverage['total'])==(669,682) and set(coverage['missing'])==set(coverage['excluded']) and len(coverage['excluded'])==13
assert original['actual_asset']['materials']==1 and original['actual_asset']['cursor_offset']==113
unit=read(p/'level-material-fixtures.json');assert unit['float_fields']==[]
for label in ['level-material','training-level-material']:
 fixture=read(p/(label+'-fixtures.json'));assert fixture['float_fields']==[]
 for c in fixture['cases']:
  for s in c['steps']:assert not s.get('expected_trap') and 'global_bit_masks' not in s and not s.get('float_fields') and not s.get('quiet_float_fields')
 port=read(p/(label+'-ports.build.json'));assert sha(p/(label+'-ports.c'))==port['source_sha256'] and sha(p/(label+'-ports.wasm'))==port['sha256']
training=read(p/'training-level-material-original.json')
assert(training['cases'],training['calls'],training['textures'],training['mips'],training['materials'],training['bound_texture_resources'],training['scene_material_end'])==(1,2,596,2486,870,576,110338)
assert training['gpu_calls']=={'1':596,'2':2486,'3':2486} and training['file_calls']=={'1':25909,'2':7}
asset_dir=r/'local/game-files/Game/Data/levels/TR';tex=(asset_dir/'TR.tex.xbx').read_bytes();scn=(asset_dir/'TR.scn.xbx').read_bytes()
assert len(tex)==3915744 and len(scn)==2770439
assert sha(asset_dir/'TR.tex.xbx')==training['texture_sha256']=='13c28cf820dd4bb989579915ab533b7651ea178ef664d44ad9ec1fc754fa6d21'
assert sha(asset_dir/'TR.scn.xbx')==training['scene_sha256']=='a4e185b0f050e181850c341a3378b54f1b37adce3099d3568600bf2e02e61332'
fixture=read(p/'training-level-material-fixtures.json');base=fixture['base'];arena=bytearray((p/fixture['memory']).read_bytes())
assert len(arena)==0x1e00000 and len(fixture['cases'])==1
case=fixture['cases'][0];assert not case['patches'] and len(case['steps'])==2
for s in case['steps']:
 for address,data in s['outputs']:arena[address-base:address-base+len(data)//2]=bytes.fromhex(data)
word=lambda a:struct.unpack_from('<I',arena,a-base)[0]
assert arena[0x100000:0x100000+len(tex)]==tex and arena[0x500000:0x500000+len(scn)]==scn
assert word(base+0x2000)==base+0x500000+110338 and word(base+0x1100)==25916
assert word(base+0x1004)==596 and word(base+0x1008)==5568
def entries(table):
 result=[];buckets=word(table+4)
 for i in range(1<<word(table)):
  entry=buckets+i*12;seen=set()
  while entry:
   assert entry not in seen;seen.add(entry)
   if word(entry+4):result.append((word(entry),word(entry+4)))
   entry=word(entry+8)
 return result
dictionary=int(training['texture_dictionary'],16);material_table=int(training['material_table'],16)
texture_rows=entries(word(dictionary+12));material_rows=entries(material_table)
assert len(texture_rows)==596 and len(material_rows)==870
resources={word(wrapper+16) for _,wrapper in texture_rows};bound=set()
assert material_rows==[(int(m['key'],16),int(m['pointer'],16)) for m in training['material_records']]
for m in training['material_records']:
 at=int(m['pointer'],16);assert word(at+8)==m['passes'];refs=[word(at+0x30+i*4) for i in range(m['passes'])]
 assert [hex(v) for v in refs]==m['resources'];bound.update(v for v in refs if v)
assert len(bound)==576 and bound<=resources
cursor=8;mips=0;assert len(training['resources'])==596
for resource in training['resources']:
 key,w,height,levels,depth,palette_depth,compression,palette_bytes=struct.unpack_from('<8I',tex,cursor);cursor+=32
 assert(resource['width'],resource['height'],len(resource['surfaces']))==(w,height,levels)
 gpu=resource['pointer'];assert word(gpu+4)==levels
 for level,(address,capacity,pitch) in enumerate(resource['surfaces']):
  assert [word(gpu+16+level*12+j*4) for j in range(3)]==[address,capacity,pitch]
  n=struct.unpack_from('<I',tex,cursor)[0];cursor+=4;assert n<=capacity
  assert arena[address-base:address-base+n]==tex[cursor:cursor+n];cursor+=n;mips+=1
assert cursor==len(tex) and mips==2486
for name,boundary,position,reads in [('level-scene-trace', '0x4c6b10',110342,25913),('level-mesh-entry-trace','0x4d6100',110486,25928)]:
 trace=read(p/(name+'.json'));assert trace['boundary']==boundary and trace['materials']==870 and trace['textures']==596
 assert trace['scene_file_position']==position and trace['io_calls']=={'open':1,'read':reads,'seek':7}
 assert trace['texture_sha256']==training['texture_sha256'] and trace['scene_sha256']==training['scene_sha256']
assert original['specimen_sha256']==training['specimen_sha256']==prior['specimen_sha256']
assert sha(r/'local/build/thug-core.wasm')==prior['main_wasm_sha256']
scope=('Recovered4d3390 streamed material parsing, including exact read grouping/seeks, duplicates, animation '
 'channels and texture indirection.127 cases134 calls cover669/682 instructions;13 exclusions are8 allocator '
 'bootstrap calls,3 allocation-failure instructions and2 bypassed alignment instructions under the stated '
 'initialized/successful-allocation contract. Existing constructors are not counted new. An actual training '
 'case loads596 textures, verifies2486 mip payloads and constructs870 materials referencing576 real texture '
 'resources. Complete30MiB arena, heap, globals and25909 reads7 seeks match, without float/padding allowances. '
 'All64 Node/Chromium suites pass;62 inherited summaries unchanged. Separate original whole-scene trace reaches '
 'first streamed mesh routine4d6100. Mesh streaming, full scene startup and production drawing remain unfinished. '
 'Main unchanged; not playable.')
proof={**candidate,'recorded_at':sys.argv[4],'observed_via':'Actual Chromium PASS at '+sys.argv[5]+'; all64 summaries and complete DOM fingerprint inspected',
 'browser_dom_fingerprint':{'algorithm':'FNV-1a-64 over canonical sorted JSON characters','value':sys.argv[1],'characters':len(canonical)},'scope':scope}
proof_path.write_text(json.dumps(proof,indent=2)+'\n')
files=set()
for pattern in ['level-material-*','training-level-material-*','*level-material*.py','verify-level-material-checkpoint.mjs','level-scene-*','level-mesh-entry-*','trace-level-*.py']:
 files.update(f for f in p.glob(pattern) if f.is_file() and f not in {target,p/'level-material-audit.json',p/'level-material-next.txt'})
files.update(f for f in (p/'level-scene-ghidra').rglob('*') if f.is_file())
assert p/'audit-level-material.py' in files and p/'pin-level-material.py' in files
artifacts=set(prior['artifact_hashes'])|{'local/analysis/scene-create-checkpoint.json','local/analysis/scene-create-audit.json'}|{str(f.relative_to(r)) for f in files}
pin={'result':'original, Node and actual Chromium comparisons pass; unpromoted','new_functions':1,'original_addresses':['0x4d3390'],
 'unpromoted_functions_in_this_module':320,'unpromoted_functions_across_separate_experiments':337,
 'specimen_sha256':original['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],
 'browser_suites':64,'new_cases':128,'new_calls_including_existing_dependencies':136,'new_interrupted_calls':0,
 'actual_training':{k:v for k,v in training.items() if k not in ['resources','material_records','scope']},'instruction_coverage':{'0x4d3390':coverage},
 'source_hashes':build['source_hashes'],'artifact_hashes':{n:sha(r/n) for n in sorted(artifacts)},'harness_hashes':prior['harness_hashes'],
 'checker_dependency_hashes':prior['checker_dependency_hashes'],'browser_dom_fingerprint':proof['browser_dom_fingerprint'],'scope':scope}
target.write_text(json.dumps(pin,indent=2)+'\n')
print(json.dumps({'result':'pinned','artifacts':len(pin['artifact_hashes']),'sources':len(pin['source_hashes']),'checkpoint_sha256':sha(target),'main_unchanged':True}))
