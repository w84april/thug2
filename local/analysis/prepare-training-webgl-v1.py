"""Derive private rendering inputs and separate original GPU-storage references.

The runtime uses the preserved raw serialized input arena and original mesh
keys; output snapshots are read only to produce the independent check file.
Neither output geometry nor original binaries are browser rendering inputs.
"""
import hashlib,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];folder=ROOT/'local/analysis'
fixture=json.loads((folder/'training-level-mesh-fixtures.json').read_text())
trace=json.loads((folder/'training-level-mesh-flow-trace.json').read_text())
checkpoint=json.loads((folder/'camera-startup-v2-checkpoint.json').read_text())
case=fixture['cases'][0];assert not case['patches'] and len(case['steps'])==4540
assert len(trace['meshes'])==2269
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs={'memory':fixture['memory'],'ports':'training-level-mesh-ports.wasm','wasm':Path(checkpoint['wasm']).name}
assert sha(ROOT/checkpoint['wasm'])==checkpoint['wasm_sha256']
runtime={**inputs,'base':fixture['base'],'memory_adapter':fixture['memory_adapter'],'memory_exports':fixture['memory_exports'],
 'pointer_exports':fixture['pointer_exports'],'pointer_initializers':fixture['pointer_initializers'],
 'callbacks':fixture['native_callbacks'],'pointer_globals':fixture['pointer_globals'],
 'globals':[[name,width,*([offsets[0]] if offsets else [0]),value] for (name,_,width,*offsets),value in zip(fixture['globals'],case['globals'])],
 'texture_data':0x1100000,'texture_bytes':3915744,'header':0x1004000,'file':0x1002000,'mesh_base':0x1a70000,
 'meshes':[{'key':int(m['args'][1],16),'dynamic':int(m['args'][4],16),'stride':m['stride'],'vertices':m['vertices'],'fvf':int(m['formats'][0],16)} for m in trace['meshes']],
 'input_sha256':{name:sha(folder/name) for name in inputs.values()},
 'scope':'Raw serialized TR assets through preserved Wasm loaders and CPU/GPU comparison storage into a new WebGL adapter; isolated input-arena bootstrap, no full scene/sector/skater startup or original frame equivalence; zero additional recovery credit.'}
output=folder/'training-webgl-v1-runtime.json';assert not output.exists();output.write_text(json.dumps(runtime,indent=2)+'\n')
memory=bytearray((folder/fixture['memory']).read_bytes());base=fixture['base']
for step in case['steps']:
 for at,text in step['outputs']:memory[at-base:at-base+len(text)//2]=bytes.fromhex(text)
word=lambda p:struct.unpack_from('<I',memory,p-base)[0]
half=lambda p:struct.unpack_from('<H',memory,p-base)[0]
digest=lambda p,n:hashlib.sha256(memory[p-base:p-base+n]).hexdigest()
meshes=[]
for i in range(2269):
 at=0x1a70000+i*216;vb=word(at+0xcc);strips=[]
 for slot in range(8):
  count=half(at+0x24+slot*2)
  if count:
   ib=word(at+0x54+slot*4);assert digest(word(ib+16),count*2)==digest(word(ib+12)+256,count*2)
   strips.append({'slot':slot,'count':count,'sha256':digest(word(ib+16),count*2)})
 assert digest(word(vb+12),word(vb))==digest(word(vb+8)+256,word(vb))
 material=word(at+0x14)
 meshes.append({'at':at,'stride':memory[at+0x18-base],'vertices':half(at+0x22),'fvf':word(at+0x38),'vertex_sha256':digest(word(vb+12),word(vb)),'strips':strips,'materialKey':word(material),'texture':word(material+0x30),'passes':word(material+8)})
check={'result':'original storage reference; new adapter comparison pending','original_fixture_sha256':sha(folder/'training-level-mesh-fixtures.json'),'runtime_sha256':sha(output),'meshes':meshes,'specimen_sha256':checkpoint['specimen_sha256'],'completion_credit':0,'playable':False}
target=folder/'training-webgl-v1-original-reference.json';assert not target.exists();target.write_text(json.dumps(check,indent=2)+'\n')
print('Prepared runtime raw input manifest and separate original storage reference for',len(meshes),'meshes')
print('Original first texture refs',[hex(m['texture']) for m in meshes[:4]])
