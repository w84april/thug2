import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
b=json.loads((p/'texture-asset-draft.build.json').read_text())
for n,h in {**b['source_hashes'],**b['draft_source_hashes']}.items():assert sha(r/n)==h,n
old=p/'texture-asset-extension.c';texture=p/'model-asset-texture-derived.c';s=old.read_text()
start=s.index('const ThugAssetMethodsDraft thug_model_asset_methods_draft=');end=s.index('/* 0048bfe0',start)
s=s[:start]+s[end:];s+='\n#include "model-asset-extension.c"\n';texture.write_text(s)
factory=p/'texture-asset-factory-derived.c';derived=p/'model-asset-factory-derived.c'
s=factory.read_text();assert s.count('#include "texture-asset-extension.c"')==1
derived.write_text(s.replace('#include "texture-asset-extension.c"','#include "model-asset-texture-derived.c"'))
output=p/'model-asset-draft.wasm';cmd=b['command'][:];cmd[cmd.index(str(factory))]=str(derived);cmd[cmd.index('-o')+1]=str(output)
subprocess.run(cmd,check=True)
drafts={n:h for n,h in b['draft_source_hashes'].items() if n not in [str(old.relative_to(r)),str(factory.relative_to(r))]}
drafts.update({str(f.relative_to(r)):sha(f) for f in [texture,derived,p/'model-asset-extension.c']})
output.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(output),'draft_source_hashes':drafts,
 'derived_from':{**b['derived_from'],str(old.relative_to(r)):sha(old),str(factory.relative_to(r)):sha(factory)}},indent=2)+'\n')
print(output.name,output.stat().st_size,sha(output))
