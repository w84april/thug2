import hashlib,json,subprocess
from pathlib import Path
root=Path.cwd();folder=root/'local/analysis'
build=json.loads((root/'local/build/thug-core.json').read_text());command=build['command'][:]
source=folder/'physics-parameter-flags-draft.c';command.insert(command.index('-o'),str(source))
output=folder/'physics-parameter-flags-draft.wasm';command[-1]=str(output)
subprocess.run(command,check=True)
report={'command':command,'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'source_hashes':build['source_hashes'],
 'draft_source_hashes':{str(source.relative_to(root)):hashlib.sha256(source.read_bytes()).hexdigest()}}
output.with_suffix('.build.json').write_text(json.dumps(report,indent=2)+'\n')
print(output.name,output.stat().st_size,report['sha256'])
