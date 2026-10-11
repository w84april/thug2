import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
b=json.loads((p/'motion-frame-draft.build.json').read_text())
for n,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/n)==h,n
source=p/'proximity-frame-draft.c';output=p/'proximity-frame-draft.wasm';cmd=b['command'][:];cmd.insert(cmd.index('-o'),str(source));cmd[cmd.index('-o')+1]=str(output)
old=p/'motion-frame-lifecycle-derived.c';updated=p/'proximity-frame-lifecycle-derived.c';assert str(old) in cmd;cmd[cmd.index(str(old))]=str(updated)
subprocess.run(cmd,check=True)
output.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(output),'draft_source_hashes':{**b['draft_source_hashes'],str(source.relative_to(r)):sha(source),str(updated.relative_to(r)):sha(updated)}},indent=2)+'\n')
print(output.name,output.stat().st_size,sha(output))
