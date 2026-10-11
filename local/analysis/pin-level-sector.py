"""Freeze full original/Node/Chromium training-scene load evidence."""
import hashlib,json,struct,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'level-sector-checkpoint.json';proof_path=p/'level-sector-browser.json';assert not target.exists() and not proof_path.exists()
prior_path=p/'level-mesh-checkpoint.json';assert sha(prior_path)=='77ae4c8797a7b48f33351b6b015c79fca00d902c9432e561c8e3ed9f34d6507d';prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'level-sector-draft.build.json');module=p/'level-sector-draft.wasm';assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='fb626eda76ee726480a0357a4b9b56baad13682e2d2f50b217230694a1085359' and module.stat().st_size==599848
previous=read(p/'level-mesh-browser.json')['suites'];names=['level-sector','training-level-sector']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('level-sector-checkpoint-'+n+'-result.json')) for n in names};assert len(suites)==68
for n,s in suites.items():
 assert s['result']=='pass',n
 if n in previous:assert s==previous[n],n
for name,expected in [('level_sector',(213,351,2,112)),('training_level_sector',(1,2,2,0))]:
 s=suites[name];assert(s['cases'],s['calls'],s['functions'],s['nan_fields_classification_only'])==expected
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
original=read(p/'level-sector-original.json');coverage=original['instruction_coverage'];assert(original['cases'],original['calls'])==(213,351)
for at,expected in [('0x4d7580',(431,433)),('0x4cebe0',(63,65))]:
 c=coverage[at];assert(c['covered'],c['total'])==expected and set(c['missing'])==set(c['excluded']) and len(c['excluded'])==2
training=read(p/'training-level-sector-original.json');trace=read(p/'level-sector-flow-trace.json')
assert(training['cases'],training['calls'],training['textures'],training['materials'],len(training['sectors']),len(training['meshes']),len(training['billboards']),training['material_groups'])==(1,2,596,870,790,2269,56,7)
assert training['buffer_calls']==[4538,4594,4594] and training['crt_calls']==13614 and training['heap_events']==46061
assert training['gpu_calls']=={'1':596,'2':2486,'3':2486} and training['file_calls']=={'1':104652,'2':542} and training['file_position']==2770439
assert len(trace['billboards'])==56 and trace['material_tables']==[{'address':'0x775b80','count':7}] and trace['header_tail_records']==0 and trace['position']==2770439
assets=r/'local/game-files/Game/Data/levels/TR';tex=(assets/'TR.tex.xbx').read_bytes();scn=(assets/'TR.scn.xbx').read_bytes()
assert len(tex)==3915744 and len(scn)==2770439
assert sha(assets/'TR.tex.xbx')==training['texture_sha256']=='13c28cf820dd4bb989579915ab533b7651ea178ef664d44ad9ec1fc754fa6d21'
assert sha(assets/'TR.scn.xbx')==training['scene_sha256']==trace['scene_sha256']=='a4e185b0f050e181850c341a3378b54f1b37adce3099d3568600bf2e02e61332'
fixture=read(p/'training-level-sector-fixtures.json');base=fixture['base'];arena=bytearray((p/fixture['memory']).read_bytes());assert base==0x800000 and len(arena)==0x2600000
assert arena[0x100000:0x100000+len(tex)]==tex and arena[0x500000:0x500000+len(scn)]==scn
assert fixture['float_fields']==[] and fixture['indirect_globals']==['thug_mesh_material_table']
assert len(fixture['cases'])==1;case=fixture['cases'][0];assert not case['patches'] and len(case['steps'])==2
assert [s['fn'] for s in case['steps']]==['0x49f050','0x4b36d0']
for s in case['steps']:
 assert not s.get('expected_trap') and 'global_bit_masks' not in s and not s.get('float_fields') and not s.get('quiet_float_fields')
 for address,data in s['outputs']:arena[address-base:address-base+len(data)//2]=bytes.fromhex(data)
w=lambda a:struct.unpack_from('<I',arena,a-base)[0];bytes_at=lambda a,n:arena[a-base:a-base+n]
assert w(base+0x2000)==base+0x500000+len(scn) and w(base+0x1100)==105194
assert [w(base+0x1200+o) for o in [8,12,16,20,24,28]]==[13614,4538,4594,4594,1,1]
assert w(base+0x1004)==596 and w(base+0x1008)==5568 and w(base+0x208)==46061
scene=training['scene'];header=training['header'];assert w(scene+0x280)==header and w(w(scene+0xd0)+8)==790 and w(w(header+0x18)+8)==870
assert list(struct.unpack('<12I',bytes_at(header+0x44,48)))==training['bounds'] and w(header+0x78)==0
mesh_by_ptr={m['mesh']:m for m in training['meshes']};assert len(mesh_by_ptr)==2269
seen=[]
for s in training['sectors']:
 assert w(s['sector']+4)==s['key'] and w(s['sector']+0x14)==s['geometry'] and w(s['geometry']+0x34)==scene
 assert w(s['geometry']+0x40)==len(s['meshes']);sentinel=w(s['geometry']+0x38);node=w(sentinel+12);members=[]
 while node!=sentinel:
  members.append(w(node+4));node=w(node+12);assert len(members)<=2269
 assert members==s['meshes'];seen+=members
assert len(seen)==2269 and set(seen)==set(mesh_by_ptr)
assert sum(m['vertices'] for m in mesh_by_ptr.values())==50814 and sum(sum(m['index_counts']) for m in mesh_by_ptr.values())==77029
billboards={b['mesh']:b['record'] for b in training['billboards']};assert len(billboards)==56
for at,m in mesh_by_ptr.items():
 assert w(at)==m['flags'] and w(at+0x14)==m['material'] and w(m['material'])==m['key'] and w(at+0xcc)==m['vertex_buffer']
 assert struct.unpack('<H',bytes_at(at+0x22,2))[0]==m['vertices'] and list(struct.unpack('<8H',bytes_at(at+0x24,16)))==m['index_counts']
 v=m['vertex_buffer'];n=w(v)
 if at not in billboards:assert bytes_at(w(v+12),n)==bytes_at(w(v+8)+256,n)
 else:assert list(struct.unpack('<9I',bytes_at(w(at+0x4c),36)))==billboards[at]
 for slot,count in enumerate(m['index_counts']):
  if count:
   v=w(at+0x54+slot*4);assert bytes_at(w(v+16),count*2)==bytes_at(w(v+12)+256,count*2)
# Verify every billboard belongs to exactly one of the seven material groups.
assert w(base+0x4000)==7;registered=[]
for i in range(7):
 group=w(base+0x4004+i*4);material=w(group+4)
 for kind in range(3):
  head=w(group+8+kind*4);node=w(head+16);members=[]
  while node!=head:
   entry=w(node+4);mesh=w(entry+4);assert w(entry)==kind and w(mesh+0x14)==material and billboards[mesh][0]==kind
   members.append(mesh);node=w(node+16);assert len(members)<=56
  registered+=members
assert len(registered)==56 and set(registered)==set(billboards)
port=read(p/'training-level-sector-ports.build.json');assert sha(p/'training-level-sector-ports.c')==port['source_sha256'] and sha(p/'training-level-sector-ports.wasm')==port['sha256']
assert original['specimen_sha256']==training['specimen_sha256']==trace['specimen_sha256']==prior['specimen_sha256']
assert sha(r/'local/build/thug-core.wasm')==prior['main_wasm_sha256']
scope=('Recovered billboard preparation4d7580 and material-table registration4cebe0 under valid serialized '
 'kind1/2 and initialized/successful-allocator contracts,213 cases351 calls. Only112 resulting NaN '
 'vertex-coordinate comparisons use classification; all actual training bytes compare exactly. Partial '
 'streamed sector4c6b10 and scene-file wrapper4b36d0 now complete the untouched training scene path: '
 '596 textures870 materials790 registered sectors2269 meshes56 billboard objects7 material groups. '
 'Full38MiB arena, scene bounds, file operations, heap, CRT and GPU storage match. Additional material '
 'layers and optional80byte tail records still trap.68 Node/Chromium suites pass with66 inherited '
 'summaries unchanged. Scene finalization/global registration, production drawing, node startup and '
 'gameplay remain unfinished. Main unchanged; not playable.')
proof={**candidate,'recorded_at':sys.argv[4],'observed_via':'Actual Chromium PASS at '+sys.argv[5]+'; all68 summaries and complete DOM fingerprint inspected',
 'browser_dom_fingerprint':{'algorithm':'FNV-1a-64 over canonical sorted JSON characters','value':sys.argv[1],'characters':len(canonical)},'scope':scope}
proof_path.write_text(json.dumps(proof,indent=2)+'\n')
files=set()
for pattern in ['level-sector-*','training-level-sector-*','*level-sector*.py','verify-level-sector-checkpoint.mjs']:
 files.update(f for f in p.glob(pattern) if f.is_file() and f not in {target,p/'level-sector-audit.json',p/'level-sector-next.txt'})
assert p/'audit-level-sector.py' in files and p/'pin-level-sector.py' in files
artifacts=set(prior['artifact_hashes'])|{'local/analysis/level-mesh-checkpoint.json','local/analysis/level-mesh-audit.json'}|{str(f.relative_to(r)) for f in files}
pin={'result':'original, Node and actual Chromium comparisons pass; unpromoted','new_functions':2,'original_addresses':['0x4d7580','0x4cebe0'],'partial_original_addresses':['0x4c6b10','0x4b36d0'],
 'unpromoted_functions_in_this_module':323,'unpromoted_functions_across_separate_experiments':340,
 'specimen_sha256':original['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],
 'browser_suites':68,'new_cases':214,'new_calls_including_existing_dependencies':353,'new_interrupted_calls':0,
 'actual_training':{k:v if k not in ['sectors','meshes','billboards','buffers'] else len(v) for k,v in training.items() if k!='scope'},'instruction_coverage':coverage,
 'source_hashes':build['source_hashes'],'artifact_hashes':{n:sha(r/n) for n in sorted(artifacts)},'harness_hashes':prior['harness_hashes'],
 'checker_dependency_hashes':prior['checker_dependency_hashes'],'browser_dom_fingerprint':proof['browser_dom_fingerprint'],'scope':scope}
target.write_text(json.dumps(pin,indent=2)+'\n')
print(json.dumps({'result':'pinned','artifacts':len(pin['artifact_hashes']),'sources':len(pin['source_hashes']),'checkpoint_sha256':sha(target),'main_unchanged':True}))
