import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
b=json.loads((p/'model-configuration-draft.build.json').read_text())
for n,h in {**b['source_hashes'],**b['draft_source_hashes']}.items():assert sha(r/n)==h,n
source=p/'texture-buffer-draft.c';output=p/'texture-buffer-draft.wasm';cmd=b['command'][:]
cmd.insert(cmd.index('-o'),str(source));cmd[cmd.index('-o')+1]=str(output)
subprocess.run(cmd,check=True)
output.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(output),
 'draft_source_hashes':{**b['draft_source_hashes'],str(source.relative_to(r)):sha(source)}},indent=2)+'\n')
print(output.name,output.stat().st_size,sha(output))
