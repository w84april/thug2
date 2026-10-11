import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
b=json.loads((p/'input-command-draft.build.json').read_text())
for n,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/n)==h,n
source=p/'skater-construction-draft.c';output=p/'skater-construction-draft.wasm';cmd=b['command'][:]
cmd.insert(cmd.index('-o'),str(source));cmd[cmd.index('-o')+1]=str(output);subprocess.run(cmd,check=True)
output.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(output),'draft_source_hashes':{**b['draft_source_hashes'],str(source.relative_to(r)):sha(source)}},indent=2)+'\n')
fixture=p/'skater-construction-diagnostic-fixture.c';target=fixture.with_suffix('.wasm')
fc=[cmd[0],'--target=wasm32-unknown-unknown','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,--no-entry,--export-all,--import-memory','-o',str(target),str(fixture)]
subprocess.run(fc,check=True);target.with_suffix('.build.json').write_text(json.dumps({'command':fc,'source_sha256':sha(fixture),'sha256':sha(target)},indent=2)+'\n')
print(output.name,output.stat().st_size,sha(output))
