import hashlib,json,subprocess
from pathlib import Path
root=Path.cwd();folder=root/'local/analysis'
build=json.loads((folder/'physics-script-values-draft.build.json').read_text());command=build['command'][:]
source=folder/'physics-movement-members-draft.c';command.insert(command.index('-o'),str(source))
output=folder/'physics-movement-members-draft.wasm';command[-1]=str(output)
subprocess.run(command,check=True)
drafts=dict(build['draft_source_hashes']);drafts[str(source.relative_to(root))]=hashlib.sha256(source.read_bytes()).hexdigest()
report={'command':command,'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'source_hashes':build['source_hashes'],'draft_source_hashes':drafts}
output.with_suffix('.build.json').write_text(json.dumps(report,indent=2)+'\n')
print(output.name,output.stat().st_size,report['sha256'])
