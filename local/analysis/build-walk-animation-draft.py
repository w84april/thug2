import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();b=json.loads((p/'walk-grounded-draft.build.json').read_text())
for n,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/n)==h,n
sources=[p/'walk-animation-draft.c'];cmd=b['command'][:];output=p/'walk-animation-draft.wasm'
old=p/'skater-walk-draft.c';derived=p/'walk-animation-component-derived.c'
text=old.read_text();assert text.count('.descriptor=thug_component_descriptor_base,')==1
derived.write_text(text.replace('.descriptor=thug_component_descriptor_base,','.descriptor=thug_component_descriptor,'))
cmd[cmd.index(str(old))]=str(derived)
drafts=dict(b['draft_source_hashes']);drafts.pop(str(old.relative_to(r)))
drafts[str(derived.relative_to(r))]=sha(derived)
for f in sources:cmd.insert(cmd.index('-o'),str(f))
cmd[cmd.index('-o')+1]=str(output)
result=subprocess.run(cmd)
if result.returncode:raise SystemExit(result.returncode)
output.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(output),'draft_source_hashes':{**drafts,**{str(f.relative_to(r)):sha(f) for f in sources}},'derived_from':{**b['derived_from'],str(old.relative_to(r)):sha(old)}},indent=2)+'\n')
print(output.name,output.stat().st_size,sha(output))
