"""Add original score insertion and compression to the pinned linked-gap module."""
import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
b=json.loads((p/'gap-links-draft.build.json').read_text())
for name,digest in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==digest,name
source=p/'score-insert-draft.c';output=p/'score-insert-draft.wasm';cmd=b['command'][:]
cmd.insert(cmd.index('-o'),str(source));cmd[cmd.index('-o')+1]=str(output)
subprocess.run(cmd,check=True)
draft={**b['draft_source_hashes'],str(source.relative_to(r)):sha(source)}
output.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(output),'draft_source_hashes':draft},indent=2)+'\n')
print(output.name,output.stat().st_size,sha(output))
