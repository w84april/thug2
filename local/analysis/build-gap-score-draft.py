"""Add gap score queries without changing any pinned source or build artifact."""
import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
b=json.loads((p/'skater-ground-draft.build.json').read_text())
for name,digest in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==digest,name
source=p/'gap-score-draft.c';output=p/'gap-score-draft.wasm';cmd=b['command'][:]
cmd.insert(cmd.index('-o'),str(source));cmd[cmd.index('-o')+1]=str(output)
subprocess.run(cmd,check=True)
output.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(output),'draft_source_hashes':{**b['draft_source_hashes'],str(source.relative_to(r)):sha(source)}},indent=2)+'\n')
print(output.name,output.stat().st_size,sha(output))
