import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
b=json.loads((p/'prop-command-draft.build.json').read_text())
for n,h in {**b['source_hashes'],**b['draft_source_hashes']}.items():assert sha(r/n)==h,n
source=p/'model-component-draft.c';output=p/'model-component-draft.wasm';cmd=b['command'][:]
cmd.insert(cmd.index('-o'),str(source));cmd[cmd.index('-o')+1]=str(output)
subprocess.run(cmd,check=True)
drafts={**b['draft_source_hashes'],str(source.relative_to(r)):sha(source)}
output.with_suffix('.build.json').write_text(json.dumps({'command':cmd,'sha256':sha(output),'source_hashes':b['source_hashes'],'draft_source_hashes':drafts},indent=2)+'\n')
print(output.name,output.stat().st_size,sha(output))
