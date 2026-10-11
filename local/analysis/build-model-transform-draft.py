import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
b=json.loads((p/'renderer-bounds-draft.build.json').read_text())
for n,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/n)==h,n
pairs=[]
def derive(old,new,changes):
 old=p/old;new=p/new;s=old.read_text()
 for a,z in changes:
  assert s.count(a)==1,(old,a);s=s.replace(a,z)
 new.write_text(s);pairs.append((old,new))
derive('renderer-bounds-component-derived.c','model-transform-component-derived.c',[
 ('    uintptr_t unavailable_8;','    RendererOne bone_map;'),
 ('void *thug_model_renderer_sphere_pc_draft(void *,void *);','void *thug_model_renderer_sphere_pc_draft(void *,void *);\nuint32_t thug_model_renderer_bone_map_draft(void *,uint32_t);'),
 ('const RendererMethods thug_model_renderer_methods_draft={','const RendererMethods thug_model_renderer_methods_draft={\n    .bone_map=thug_model_renderer_bone_map_draft,'),
 ('const ThugComponentMethods thug_model_component_methods_draft={',
 '''void thug_model_component_finalize_draft(void *);
void thug_model_update_frame_draft(void *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
void thug_model_component_moved_prefix_draft(void *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
const ThugComponentMethods thug_model_component_methods_draft={
    .finalize=thug_model_component_finalize_draft,.update=thug_model_update_frame_draft,
    .moved=thug_model_component_moved_prefix_draft,''')])
derive('renderer-bounds-initialize-derived.c','model-transform-initialize-derived.c',[
 (' uintptr_t unused10[13];void *(*sphere)(void *,void *);uintptr_t unused48[9];\n void (*lights)(void *,void *);uintptr_t unused70[4];uint32_t (*flag16)(void *,uint32_t);',
 ''' uintptr_t unused10[9];void (*enabled)(void *,uint32_t);uintptr_t unused38[3];
 void *(*sphere)(void *,void *);uintptr_t unused48[9];void (*lights)(void *,void *);
 uint8_t (*transform)(void *,const float *,const void *,uint32_t,uint32_t,uint32_t);
 uintptr_t unused74[3];uint32_t (*flag16)(void *,uint32_t);'''),
 ('void *thug_model_geometry_sphere_pc_draft(void *,void *);',
 '''void *thug_model_geometry_sphere_pc_draft(void *,void *);
void thug_model_geometry_enabled_draft(void *,uint32_t);
uint8_t thug_model_geometry_transform_pc_draft(void *,const float *,const void *,uint32_t,uint32_t,uint32_t);'''),
 ('const GeometryMethods thug_model_geometry_lights_methods_draft={.sphere=',
 'const GeometryMethods thug_model_geometry_lights_methods_draft={.enabled=thug_model_geometry_enabled_draft,.transform=thug_model_geometry_transform_pc_draft,.sphere=')])
source=p/'model-transform-draft.c';output=p/'model-transform-draft.wasm';cmd=b['command'][:]
for old,new in pairs:cmd[cmd.index(str(old))]=str(new)
cmd.insert(cmd.index('-o'),str(source));cmd[cmd.index('-o')+1]=str(output);subprocess.run(cmd,check=True)
drafts={n:h for n,h in b['draft_source_hashes'].items() if n not in {str(a.relative_to(r)) for a,_ in pairs}}
drafts.update({str(f.relative_to(r)):sha(f) for f in [*[b for a,b in pairs],source]})
output.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(output),'draft_source_hashes':drafts,'derived_from':{**b['derived_from'],**{str(a.relative_to(r)):sha(a) for a,_ in pairs}}},indent=2)+'\n')
print(output.name,output.stat().st_size,sha(output))
