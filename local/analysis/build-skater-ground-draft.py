import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
b=json.loads((p/'skater-adjust-draft.build.json').read_text())
for n,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/n)==h,n
pairs=[]
for kind in ['static','moving']:
 old=p/('sphere-query-static-derived.c' if kind=='static' else 'particle-emission-moving-derived.c');new=p/f'skater-ground-{kind}-derived.c';s=old.read_text();needle=f'const ThugCollisionMethods thug_{kind}_collision_methods = {{'
 assert s.count(needle)==1
 s=s.replace(needle,'uint8_t thug_collision_accepts_light_draft(const void *);\n'+needle+'\n    .unknown_4=(uintptr_t)thug_collision_accepts_light_draft,')
 new.write_text(s);pairs.append((old,new))
old=p/'geometry-clone-initialize-derived.c';new=p/'skater-ground-model-derived.c';s=old.read_text();needle='const LightMethods thug_model_light_methods_draft={.dispose='
assert s.count(needle)==1
s=s.replace(needle,'static void light_refresh(void *p,uint32_t a,uint32_t b){thug_component_empty_two(p,(void *)(uintptr_t)a,(void *)(uintptr_t)b);}\nconst LightMethods thug_model_light_methods_draft={.unavailable_4_to_20={[7]=(uintptr_t)light_refresh},.dispose=')
new.write_text(s);pairs.append((old,new))
old=p/'skater-adjust-draft.c';new=p/'skater-ground-adjust-derived.c';s=old.read_text();needle='static void pending_frame(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){(void)p;(void)q;(void)d;(void)m;__builtin_trap();}'
assert s.count(needle)==1
s=s.replace(needle,'void thug_skater_adjust_update_draft(void *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);\nstatic void pending_frame(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){thug_skater_adjust_update_draft(p,q,d,m);}')
new.write_text(s);pairs.append((old,new))
cmd=b['command'][:];draft=b['draft_source_hashes'].copy();derived=b['derived_from'].copy()
for old,new in pairs:
 matches=[i for i,v in enumerate(cmd) if Path(v).resolve()==old];assert len(matches)==1,(old,matches)
 cmd[matches[0]]=str(new);derived[str(old.relative_to(r))]=sha(old);draft.pop(str(old.relative_to(r)),None);draft[str(new.relative_to(r))]=sha(new)
for source in [p/'skater-ground-light.c',p/'skater-ground-draft.c']:
 cmd.insert(cmd.index('-o'),str(source));draft[str(source.relative_to(r))]=sha(source)
output=p/'skater-ground-draft.wasm';cmd[cmd.index('-o')+1]=str(output);subprocess.run(cmd,check=True)
output.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(output),'draft_source_hashes':draft,'derived_from':derived},indent=2)+'\n')
print(output.name,output.stat().st_size,sha(output))
