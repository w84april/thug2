import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
b=json.loads((p/'scene-construction-draft.build.json').read_text())
for n,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/n)==h,n
old=p/'scene-construction-draft.c';new=p/'mesh-index-scene-derived.c';s=old.read_text()
needle='void (*thug_model_sector_parse_pending_draft)(void *,const uint8_t **,const ThugMemory *);';assert s.count(needle)==1
s=s.replace(needle,'void thug_model_sector_mesh_prefix_draft(void *,const uint8_t **,const ThugMemory *);\n'+needle[:-1]+'=thug_model_sector_mesh_prefix_draft;');new.write_text(s)
source=p/'mesh-index-draft.c';output=p/'mesh-index-draft.wasm';cmd=b['command'][:];cmd[cmd.index(str(old))]=str(new);cmd.insert(cmd.index('-o'),str(source));cmd[cmd.index('-o')+1]=str(output)
subprocess.run(cmd,check=True)
drafts={n:h for n,h in b['draft_source_hashes'].items() if n!=str(old.relative_to(r))};drafts.update({str(f.relative_to(r)):sha(f) for f in [new,source]})
output.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(output),'draft_source_hashes':drafts,'derived_from':{**b['derived_from'],str(old.relative_to(r)):sha(old)}},indent=2)+'\n')
print(output.name,output.stat().st_size,sha(output))
