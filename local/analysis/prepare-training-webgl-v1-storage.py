"""Hash original mesh storage and untouched texture payloads, never geometry inputs."""
import hashlib,json,struct
from pathlib import Path
root=Path(__file__).resolve().parents[2];folder=root/'local/analysis'
reference=json.loads((folder/'training-webgl-v1-original-reference.json').read_text());hashes=[]
for mesh in reference['meshes']:
 hashes.append(mesh['vertex_sha256']);hashes.extend(strip['sha256'] for strip in mesh['strips'])
mesh_buffers=len(hashes)
texture=root/'local/game-files/Game/Data/levels/TR/TR.tex.xbx';data=texture.read_bytes();cursor=8;mips=0
for index in range(596):
 key,width,height,levels,depth,palette_depth,compression,palette_bytes=struct.unpack_from('<8I',data,cursor);cursor+=32
 # The preserved original loader maps both file codes 1 and 2 to DXT1.
 assert compression in (1,2,5) and palette_bytes==0
 for level in range(levels):
  n=struct.unpack_from('<I',data,cursor)[0];cursor+=4
  expected=((max(1,width>>level)+3)//4)*((max(1,height>>level)+3)//4)*(16 if compression==5 else 8)
  assert n==expected and cursor+n<=len(data)
  hashes.append(hashlib.sha256(data[cursor:cursor+n]).hexdigest());cursor+=n;mips+=1
assert cursor==len(data) and mips==2486
proof={'schema':2,'scope':'Original vertex/index storage followed by untouched texture mip digests, in original order; no decoded rendering inputs or frame equivalence',
 'original_fixture_sha256':reference['original_fixture_sha256'],'runtime_sha256':reference['runtime_sha256'],'texture_sha256':hashlib.sha256(data).hexdigest(),
 'mesh_buffers':mesh_buffers,'texture_mips':mips,'ordered_storage_buffers':len(hashes),'ordered_storage_sha256':hashlib.sha256('\n'.join(hashes).encode()).hexdigest()}
out=folder/'training-webgl-v1-storage-proof-v2.json';assert not out.exists();out.write_text(json.dumps(proof,indent=2)+'\n');print(proof)
