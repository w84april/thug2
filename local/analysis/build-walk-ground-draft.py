import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();b=json.loads((p/'skater-walk-draft.build.json').read_text())
for n,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/n)==h,n
sources=[p/'walk-ground-draft.c'];cmd=b['command'][:];output=p/'walk-ground-draft.wasm'
for f in sources:cmd.insert(cmd.index('-o'),str(f))
cmd[cmd.index('-o')+1]=str(output);subprocess.run(cmd,check=True)
output.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(output),'draft_source_hashes':{**b['draft_source_hashes'],**{str(f.relative_to(r)):sha(f) for f in sources}}},indent=2)+'\n')
print(output.name,output.stat().st_size,sha(output))
