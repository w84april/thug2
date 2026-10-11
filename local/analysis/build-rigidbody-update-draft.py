import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
b=json.loads((p/'rigidbody-kick-draft.build.json').read_text())
for n,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/n)==h,n
core=p/'lock-frame-rigidbody-core-derived.c';init=p/'lock-frame-rigidbody-initialize-derived.c'
newcore=p/'rigidbody-update-core-derived.c';newinit=p/'rigidbody-update-initialize-derived.c'
newcore.write_text(core.read_text().replace(init.name,newinit.name))
newinit.write_text(init.read_text().replace('thug_lock_rigidbody_boundary_draft','thug_rigidbody_update_draft'))
source=p/'rigidbody-update-draft.c';output=p/'rigidbody-update-draft.wasm';cmd=b['command'][:]
assert str(core) in cmd;cmd[cmd.index(str(core))]=str(newcore)
cmd.insert(cmd.index('-o'),str(source));cmd[cmd.index('-o')+1]=str(output)
subprocess.run(cmd,check=True)
newfiles=[newcore,newinit,source]
output.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(output),
 'draft_source_hashes':{**b['draft_source_hashes'],**{str(f.relative_to(r)):sha(f) for f in newfiles}},
 'derived_from':{**b['derived_from'],str(core.relative_to(r)):sha(core),str(init.relative_to(r)):sha(init)}},indent=2)+'\n')
print(output.name,output.stat().st_size,sha(output))
