import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
b=json.loads((p/'texture-buffer-draft.build.json').read_text())
for n,h in {**b['source_hashes'],**b['draft_source_hashes']}.items():assert sha(r/n)==h,n
old=p/'asset-factory-draft.c';derived=p/'texture-asset-factory-derived.c';extension=p/'texture-asset-extension.c'
s=old.read_text();needle='OTHER_METHODS(thug_texture_asset_methods_draft);';assert s.count(needle)==1
s=s.replace(needle,'#include "texture-asset-extension.c"');needle='OTHER_METHODS(thug_model_asset_methods_draft);';assert s.count(needle)==1
s=s.replace(needle,'/* Model file virtual is an explicit unavailable boundary in texture-asset-extension.c. */')
derived.write_text('/* Derived from pinned asset factory; bind actual texture loading virtuals. */\n'+s)
config=p/'model-configuration-draft.c';config_derived=p/'texture-asset-configuration-derived.c';prefix=p/'model-texture-load-prefix.c'
s=config.read_text();needle='void (*thug_model_load_pending_draft)(void *,const ThugScriptStructure *,void *,const char *,\n    uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);';assert s.count(needle)==1
s=s.replace(needle,'void thug_model_texture_load_prefix_draft(void *,const ThugScriptStructure *,void *,const char *,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);\n'+needle[:-1]+'=thug_model_texture_load_prefix_draft;')
config_derived.write_text('/* Derived from pinned configuration; continue into original texture loading. */\n'+s)
output=p/'texture-asset-draft.wasm';cmd=b['command'][:];cmd[cmd.index(str(old))]=str(derived);cmd[cmd.index(str(config))]=str(config_derived)
cmd.insert(cmd.index('-o'),str(prefix));cmd[cmd.index('-o')+1]=str(output)
subprocess.run(cmd,check=True)
drafts={n:h for n,h in b['draft_source_hashes'].items() if n not in [str(old.relative_to(r)),str(config.relative_to(r))]}
drafts.update({str(f.relative_to(r)):sha(f) for f in [derived,extension,config_derived,prefix]})
output.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(output),'draft_source_hashes':drafts,
 'derived_from':{**b['derived_from'],str(old.relative_to(r)):sha(old),str(config.relative_to(r)):sha(config)}},indent=2)+'\n')
print(output.name,output.stat().st_size,sha(output))
