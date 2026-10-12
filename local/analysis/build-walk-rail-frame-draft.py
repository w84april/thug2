import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();b=json.loads((p/'walk-exit-floor-draft.build.json').read_text())
for n,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/n)==h,n
source=p/'walk-rail-frame-draft.c';animation=p/'walk-animation-rail-draft.c';old=p/'walk-animation-draft.c';cmd=b['command'][:];output=p/'walk-rail-frame-draft.wasm'
assert str(old) in cmd;cmd[cmd.index(str(old))]=str(animation);cmd.insert(cmd.index('-o'),str(source));cmd[cmd.index('-o')+1]=str(output)
subprocess.run(cmd,check=True)
hashes={k:v for k,v in b['draft_source_hashes'].items() if k!=str(old.relative_to(r))}
for f in [source,animation]:hashes[str(f.relative_to(r))]=sha(f)
output.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(output),'draft_source_hashes':hashes,'derived_from':{**b['derived_from'],str(old.relative_to(r)):sha(old)}},indent=2)+'\n')
print(output.name,output.stat().st_size,sha(output))
