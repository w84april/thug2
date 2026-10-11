import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
b=json.loads((p/'sphere-contact-draft.build.json').read_text())
for n,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/n)==h,n
source=p/'sphere-query-draft.c';output=p/'sphere-query-draft.wasm';cmd=b['command'][:]
old=p/'particle-emission-static-derived.c';derived=p/'sphere-query-static-derived.c'
cmd[cmd.index(str(old))]=str(derived)
cmd.insert(cmd.index('-o'),str(source));cmd[cmd.index('-o')+1]=str(output)
subprocess.run(cmd,check=True)
output.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(output),
 'draft_source_hashes':{**{n:h for n,h in b['draft_source_hashes'].items() if n!=str(old.relative_to(r))},str(source.relative_to(r)):sha(source),str(derived.relative_to(r)):sha(derived),'local/analysis/sphere-query-draft.h':sha(p/'sphere-query-draft.h')},'derived_from':{**b['derived_from'],str(old.relative_to(r)):sha(old)}},indent=2)+'\n')
print(output.name,output.stat().st_size,sha(output))
