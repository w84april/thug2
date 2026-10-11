import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
for old,new,source in [('mesh-index-ports','vertex-upload-ports','vertex-upload-ports.c'),('training-mesh-index-ports','training-vertex-upload-ports','vertex-upload-ports.c'),('training-mesh-index-boundary','training-vertex-upload-boundary','training-vertex-upload-boundary.c')]:
 b=json.loads((p/(old+'.build.json')).read_text());cmd=b['command'][:];cmd[cmd.index('-o')-1]=str(p/source);cmd[cmd.index('-o')+1]=str(p/(new+'.wasm'))
 subprocess.run(cmd,check=True);meta={'command':cmd,'source_sha256':sha(p/source),'sha256':sha(p/(new+'.wasm'))}
 if 'included_source_sha256' in b:meta['included_source_sha256']=sha(r/'tools/script_values_memory.c')
 (p/(new+'.build.json')).write_text(json.dumps(meta,indent=2)+'\n')
 print(new,meta['sha256'])
