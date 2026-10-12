import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();b=json.loads((p/'walk-complete-update-draft.build.json').read_text())
for n,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/n)==h,n
old=p/'walk-animation-component-derived.c';source=p/'walk-component-frame-draft.c';output=p/'walk-component-frame-draft.wasm';cmd=b['command'][:]
assert cmd.count(str(old))==1;cmd[cmd.index(str(old))]=str(source);cmd[cmd.index('-o')+1]=str(output)
b['draft_source_hashes'].pop(str(old.relative_to(r)));b['derived_from']={**b['derived_from'],str(old.relative_to(r)):sha(old)}
subprocess.run(cmd,check=True)
output.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(output),'draft_source_hashes':{**b['draft_source_hashes'],str(source.relative_to(r)):sha(source)}},indent=2)+'\n')
print(output.name,output.stat().st_size,sha(output))
