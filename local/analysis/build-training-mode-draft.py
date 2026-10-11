import hashlib,json,subprocess
from pathlib import Path
root=Path.cwd();p=root/'local/analysis'
build=json.loads((p/'asset-factory-draft.build.json').read_text())
for name,digest in {**build['source_hashes'],**build['draft_source_hashes']}.items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest,name
source=p/'training-mode-draft.c';output=p/'training-mode-draft.wasm'
command=build['command'][:];command.insert(command.index('-o'),str(source));command[command.index('-o')+1]=str(output)
subprocess.run(command,check=True)
report={'command':command,'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'source_hashes':build['source_hashes'],'draft_source_hashes':{**build['draft_source_hashes'],str(source.relative_to(root)):hashlib.sha256(source.read_bytes()).hexdigest()}}
output.with_suffix('.build.json').write_text(json.dumps(report,indent=2)+'\n');print(output.name,output.stat().st_size,report['sha256'])
