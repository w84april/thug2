import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
b=json.loads((p/'proximity-frame-draft.build.json').read_text())
for n,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/n)==h,n
source=p/'lock-frame-draft.c';output=p/'lock-frame-draft.wasm';cmd=b['command'][:];cmd.insert(cmd.index('-o'),str(source));cmd[cmd.index('-o')+1]=str(output)
old=p/'proximity-frame-lifecycle-derived.c';updated=p/'lock-frame-lifecycle-derived.c';assert str(old) in cmd;cmd[cmd.index(str(old))]=str(updated)
extra_sources=[p/'lock-frame-rigidbody-initialize-derived.c']
for before,after in [('rigidbody-motion-core-derived.c','lock-frame-rigidbody-core-derived.c'),('particle-setup-draft.c','lock-frame-particle-setup-derived.c')]:
 old_path=str(p/before);new_path=p/after;assert old_path in cmd;cmd[cmd.index(old_path)]=str(new_path);extra_sources.append(new_path)
subprocess.run(cmd,check=True)
output.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(output),'draft_source_hashes':{**b['draft_source_hashes'],str(source.relative_to(r)):sha(source),str(updated.relative_to(r)):sha(updated),**{str(f.relative_to(r)):sha(f) for f in extra_sources}}},indent=2)+'\n')
print(output.name,output.stat().st_size,sha(output))
