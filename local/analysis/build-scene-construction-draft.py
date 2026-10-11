import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
b=json.loads((p/'material-buffer-draft.build.json').read_text())
for n,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/n)==h,n
old=p/'material-buffer-draft.c';new=p/'scene-construction-material-derived.c';s=old.read_text()
needle='    if(thug_model_scene_constructor_pending_draft)thug_model_scene_constructor_pending_draft(scene,shift,m);\n    __builtin_trap();'
assert s.count(needle)==1
s=s.replace(needle,'    if(thug_model_scene_constructor_pending_draft){thug_model_scene_constructor_pending_draft(scene,shift,m);__builtin_trap();}\n    thug_model_scene_construct_draft(scene,shift,m);\n    thug_model_scene_load_geometry_prefix_draft(scene,header,p,count,m);')
new.write_text(s.replace('void thug_model_geometry_load_prefix_draft(', 'void *thug_model_scene_construct_draft(void *,uint32_t,const ThugMemory *);\nvoid thug_model_scene_load_geometry_prefix_draft(void *,void *,const uint8_t *,uint32_t,const ThugMemory *);\nvoid thug_model_geometry_load_prefix_draft(',1))
source=p/'scene-construction-draft.c';output=p/'scene-construction-draft.wasm';cmd=b['command'][:]
cmd[cmd.index(str(old))]=str(new);cmd.insert(cmd.index('-o'),str(source));cmd[cmd.index('-o')+1]=str(output)
subprocess.run(cmd,check=True)
drafts={n:h for n,h in b['draft_source_hashes'].items() if n!=str(old.relative_to(r))};drafts.update({str(f.relative_to(r)):sha(f) for f in [new,source]})
output.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(output),'draft_source_hashes':drafts,'derived_from':{**b['derived_from'],str(old.relative_to(r)):sha(old)}},indent=2)+'\n')
print(output.name,output.stat().st_size,sha(output))
