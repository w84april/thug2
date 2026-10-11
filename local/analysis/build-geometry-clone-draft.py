import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
b=json.loads((p/'level-register-draft.build.json').read_text())
for n,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/n)==h,n
pairs=[]
def derive(old,new,changes):
 old=p/old;new=p/new;s=old.read_text()
 for a,z in changes:
  assert s.count(a)==1,(old,a);s=s.replace(a,z)
 new.write_text(s);pairs.append((old,new))
derive('model-transform-initialize-derived.c','geometry-clone-initialize-derived.c',[
 (' uintptr_t unused0[3];uint8_t (*load)', ' uintptr_t unused0[2];void *(*clone)(void *,uint32_t,void *,const ThugMemory *);uint8_t (*load)'),
 ('extern const LightMethods thug_model_light_base_methods_draft', 'void *thug_geometry_clone_pc_draft(void *,uint32_t,void *,const ThugMemory *);\nextern const LightMethods thug_model_light_base_methods_draft'),
 ('const GeometryMethods thug_model_geometry_lights_methods_draft={', 'const GeometryMethods thug_model_geometry_lights_methods_draft={.clone=thug_geometry_clone_pc_draft,')])
derive('renderer-bounds-configuration-derived.c','geometry-clone-configuration-derived.c',[
 ('void thug_model_configuration_prefix_draft(void *p,const ThugScriptStructure *s){', 'void thug_model_level_object_draft(void *,uint32_t,const ThugMemory *);\nvoid thug_model_configuration_prefix_draft(void *p,const ThugScriptStructure *s){'),
 ('    if(kind==0xb7b3bd86)__builtin_trap(); /* unrecovered41ffa0 LevelObject path */', '    if(kind==0xb7b3bd86){uint32_t key;if(!thug_script_get_checksum(s,0xa1dc81f9,&key,1))__builtin_trap();thug_model_level_object_draft(p,key,m);goto ready;}'),
 ('    if(word(pointer(p,12),0x104)&0x20)__builtin_trap();','ready:\n    if(word(pointer(p,12),0x104)&0x20)__builtin_trap();')])
source=p/'geometry-clone-draft.c';output=p/'geometry-clone-draft.wasm';cmd=b['command'][:]
for old,new in pairs:cmd[cmd.index(str(old))]=str(new)
cmd.insert(cmd.index('-o'),str(source));cmd[cmd.index('-o')+1]=str(output);subprocess.run(cmd,check=True)
drafts={n:h for n,h in b['draft_source_hashes'].items() if n not in {str(a.relative_to(r)) for a,_ in pairs}}
drafts.update({str(f.relative_to(r)):sha(f) for f in [*[b for a,b in pairs],source]})
output.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(output),'draft_source_hashes':drafts,'derived_from':{**b['derived_from'],**{str(a.relative_to(r)):sha(a) for a,_ in pairs}}},indent=2)+'\n')
print(output.name,output.stat().st_size,sha(output))
