import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();b=json.loads((p/'walk-hang-motion-draft.build.json').read_text())
for n,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/n)==h,n
source=p/'walk-hang-exit-draft.c';cmd=b['command'][:];output=p/'walk-hang-exit-draft.wasm'
cmd.insert(cmd.index('-o'),str(source));cmd[cmd.index('-o')+1]=str(output)
old=p/'walk-animation-rail-draft.c';new=p/'walk-animation-hang-draft.c';assert str(old) in cmd;cmd[cmd.index(str(old))]=str(new)
drafts=dict(b['draft_source_hashes']);old_hash=drafts.pop(str(old.relative_to(r)));drafts[str(new.relative_to(r))]=sha(new);b['draft_source_hashes']=drafts;b['derived_from']={**b['derived_from'],str(old.relative_to(r)):old_hash}
subprocess.run(cmd,check=True)
output.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(output),'draft_source_hashes':{**b['draft_source_hashes'],str(source.relative_to(r)):sha(source)}},indent=2)+'\n')
print(output.name,output.stat().st_size,sha(output))
