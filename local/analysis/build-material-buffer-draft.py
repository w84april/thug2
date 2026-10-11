import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
b=json.loads((p/'model-asset-draft.build.json').read_text())
for n,h in {**b['source_hashes'],**b['draft_source_hashes']}.items():assert sha(r/n)==h,n
extension=p/'model-asset-extension.c';new_extension=p/'material-model-asset-derived.c';s=extension.read_text()
needle='void (*thug_model_buffer_pending_draft)(uint32_t,const void *,uint32_t,const void *,void *,uint32_t,uint32_t,uint32_t,const ThugMemory *);';assert s.count(needle)==1
s=s.replace(needle,'void thug_model_geometry_load_prefix_draft(uint32_t,const void *,uint32_t,const void *,void *,uint32_t,uint32_t,uint32_t,const ThugMemory *);\n'+needle[:-1]+'=thug_model_geometry_load_prefix_draft;');new_extension.write_text(s)
texture=p/'model-asset-texture-derived.c';new_texture=p/'material-texture-derived.c';s=texture.read_text();assert s.count('"model-asset-extension.c"')==1
new_texture.write_text(s.replace('"model-asset-extension.c"','"material-model-asset-derived.c"'))
factory=p/'model-asset-factory-derived.c';new_factory=p/'material-factory-derived.c';s=factory.read_text();assert s.count('"model-asset-texture-derived.c"')==1
new_factory.write_text(s.replace('"model-asset-texture-derived.c"','"material-texture-derived.c"'))
source=p/'material-buffer-draft.c';output=p/'material-buffer-draft.wasm';cmd=b['command'][:];cmd[cmd.index(str(factory))]=str(new_factory);cmd.insert(cmd.index('-o'),str(source));cmd[cmd.index('-o')+1]=str(output)
subprocess.run(cmd,check=True)
old=[extension,texture,factory];new=[new_extension,new_texture,new_factory,source]
drafts={n:h for n,h in b['draft_source_hashes'].items() if n not in [str(f.relative_to(r)) for f in old]};drafts.update({str(f.relative_to(r)):sha(f) for f in new})
output.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(output),'draft_source_hashes':drafts,'derived_from':{**b['derived_from'],**{str(f.relative_to(r)):sha(f) for f in old}}},indent=2)+'\n')
print(output.name,output.stat().st_size,sha(output))
