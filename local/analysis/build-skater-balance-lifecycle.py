import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();b=json.loads((p/'skater-descriptor-corrected.build.json').read_text())
for n,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/n)==h,n
source=p/'skater-balance-lifecycle-draft.c';out=p/'skater-balance-lifecycle-draft.wasm';cmd=b['command'][:];cmd.insert(cmd.index('-o'),str(source));cmd[cmd.index('-o')+1]=str(out)
subprocess.run(cmd,check=True);out.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(out),'draft_source_hashes':{**b['draft_source_hashes'],str(source.relative_to(r)):sha(source)}},indent=2)+'\n');print(out.name,out.stat().st_size,sha(out))
