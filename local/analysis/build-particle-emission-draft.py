import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
b=json.loads((p/'particle-frame-draft.build.json').read_text())
for n,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/n)==h,n
source=p/'particle-emission-draft.c';output=p/'particle-emission-draft.wasm';cmd=b['command'][:];cmd.insert(cmd.index('-o'),str(source));cmd[cmd.index('-o')+1]=str(output)
old=p/'particle-create-draft.c';updated=p/'particle-emission-create-derived.c';assert str(old) in cmd;cmd[cmd.index(str(old))]=str(updated)
extra_sources=[]
for before,after in [('src/collision/segment.c','local/analysis/particle-emission-static-derived.c'),('local/analysis/level-collision-component-moving-derived.c','local/analysis/particle-emission-moving-derived.c')]:
 old_path=str(r/before);new_path=r/after;assert old_path in cmd;cmd[cmd.index(old_path)]=str(new_path);extra_sources.append(new_path)
subprocess.run(cmd,check=True)
output.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(output),'draft_source_hashes':{**b['draft_source_hashes'],str(source.relative_to(r)):sha(source),str(updated.relative_to(r)):sha(updated),**{str(f.relative_to(r)):sha(f) for f in extra_sources}}},indent=2)+'\n')
print(output.name,output.stat().st_size,sha(output))
