"""Build the explicit test-only renderer, release and traversal witnesses."""
import hashlib,json,subprocess
from pathlib import Path
p=Path('local/analysis');cc=json.loads((p/'training-mode-draft.build.json').read_text())['command'][0]
reports=[]
for name in ['scene-state-callback','scene-disposal-memory','scene-visitor-callback']:
    source=p/(name+'.c');output=p/(name+'.wasm')
    command=[cc,'--target=wasm32-unknown-unknown','-std=c11','-O2','-Wall','-Wextra','-Werror','-nostdlib',
             '-Wl,--no-entry,--export-all,--import-memory'+(',--allow-undefined' if name=='scene-visitor-callback' else ''),
             '-Wl,-z,stack-size=0',str(source),'-o',str(output)]
    before=output.read_bytes() if output.exists() else None
    subprocess.run(command,check=True)
    if before is not None:assert before==output.read_bytes(),name
    reports.append({'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                    'output':str(output),'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'command':command})
(p/'scene-state-witnesses.build.json').write_text(json.dumps(reports,indent=2)+'\n')
print('Three witnesses rebuilt identically')
