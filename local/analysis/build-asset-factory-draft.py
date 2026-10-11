import hashlib,json,subprocess
from pathlib import Path
root=Path.cwd();folder=root/'local/analysis'
build=json.loads((folder/'skeleton-asset-draft.build.json').read_text())
for name,digest in {**build['source_hashes'],**build['draft_source_hashes']}.items():
    assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest,name
source=folder/'asset-factory-draft.c';output=folder/'asset-factory-draft.wasm'
command=build['command'][:];old=str(folder/'skeleton-asset-draft.c')
command[command.index(old)]=str(source);command[command.index('-o')+1]=str(output)
subprocess.run(command,check=True)
drafts={n:h for n,h in build['draft_source_hashes'].items() if n!='local/analysis/skeleton-asset-draft.c'}
drafts[str(source.relative_to(root))]=hashlib.sha256(source.read_bytes()).hexdigest()
report={'command':command,'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'source_hashes':build['source_hashes'],'draft_source_hashes':drafts}
output.with_suffix('.build.json').write_text(json.dumps(report,indent=2)+'\n')
print(output.name,output.stat().st_size,report['sha256'])
