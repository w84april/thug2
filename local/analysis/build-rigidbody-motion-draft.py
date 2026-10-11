import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
b=json.loads((p/'rigidbody-initialize-draft.build.json').read_text())
for n,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/n)==h,n
old=p/'rigidbody-initialize-core-derived.c';source=p/'rigidbody-motion-core-derived.c';addition=p/'rigidbody-motion-draft.c';output=p/'rigidbody-motion-draft.wasm';cmd=b['command'][:]
oldlevel=p/'rigidbody-initialize-draft.c';level=p/'rigidbody-motion-initialize-derived.c'
cmd[cmd.index(str(old))]=str(source);cmd[cmd.index('-o')+1]=str(output);subprocess.run(cmd,check=True)
drafts={k:v for k,v in b['draft_source_hashes'].items() if k not in [str(old.relative_to(r)),str(oldlevel.relative_to(r))]}
drafts.update({str(f.relative_to(r)):sha(f) for f in [source,addition,level]})
output.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(output),'draft_source_hashes':drafts,'derived_from':{**b['derived_from'],str(old.relative_to(r)):sha(old),str(oldlevel.relative_to(r)):sha(oldlevel)}},indent=2)+'\n');print(output.name,output.stat().st_size,sha(output))
