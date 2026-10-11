import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
b=json.loads((p/'render-instance-draft.build.json').read_text())
for n,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/n)==h,n
pairs=[]
def derive(old,new,changes):
 old=p/old;new=p/new;s=old.read_text()
 for a,z in changes:
  assert s.count(a)==1,(old,a);s=s.replace(a,z)
 new.write_text(s);pairs.append((old,new))
derive('model-initialize-component-derived.c','renderer-bounds-component-derived.c',[
 ('    uintptr_t unavailable_20_to_34[6];','    uintptr_t unavailable_20_to_2c[4];\n    void *(*sphere)(void *,void *);uintptr_t unavailable_34;'),
 ('extern const RendererMethods thug_model_renderer_base_methods_draft,thug_model_renderer_methods_draft;',
 'void *thug_model_renderer_sphere_pc_draft(void *,void *);\nextern const RendererMethods thug_model_renderer_base_methods_draft,thug_model_renderer_methods_draft;'),
 ('const RendererMethods thug_model_renderer_methods_draft={','const RendererMethods thug_model_renderer_methods_draft={\n    .sphere=thug_model_renderer_sphere_pc_draft,')])
derive('render-instance-initialize-derived.c','renderer-bounds-initialize-derived.c',[
 (' uintptr_t unused10[23];void (*lights)(void *,void *);uintptr_t unused70[4];uint32_t (*flag16)(void *,uint32_t);',
 ' uintptr_t unused10[13];void *(*sphere)(void *,void *);uintptr_t unused48[9];\n void (*lights)(void *,void *);uintptr_t unused70[4];uint32_t (*flag16)(void *,uint32_t);'),
 ('uint32_t thug_model_virtual_true_draft(void *,uint32_t);','uint32_t thug_model_virtual_true_draft(void *,uint32_t);\nvoid *thug_model_geometry_sphere_pc_draft(void *,void *);'),
 ('const GeometryMethods thug_model_geometry_lights_methods_draft={.load=',
 'const GeometryMethods thug_model_geometry_lights_methods_draft={.sphere=thug_model_geometry_sphere_pc_draft,.load=')])
derive('render-instance-configuration-derived.c','renderer-bounds-configuration-derived.c',[
 ('void (*thug_model_renderer_ready_pending_draft)(void *,const ThugScriptStructure *);',
 'void *thug_model_renderer_sphere_draft(void *,void *);\nvoid (*thug_model_renderer_ready_pending_draft)(void *,const ThugScriptStructure *);'),
 ('''    if(thug_model_renderer_ready_pending_draft)thug_model_renderer_ready_pending_draft(p,s);
    __builtin_trap(); /* 421191: actual model load returned; configuration tail remains */''',
 '''    if(thug_model_renderer_ready_pending_draft){thug_model_renderer_ready_pending_draft(p,s);__builtin_trap();}
    /* Original421191 tail. The update/lighting and skeleton-cache paths still
     * stop explicitly; the training collectible does not take either path. */
    if(word(pointer(p,12),0x104)&0x20)__builtin_trap();
    uint32_t sphere[4];void *value=thug_model_renderer_sphere_draft(pointer(p,0x208),sphere);
    for(unsigned i=0;i<4;i++)put(p,0x18+i*4,word(value,i*4));
    if(thug_script_get_global_integer(0x74ff5cb4,0))__builtin_trap(); /*420350*/''')])
source=p/'renderer-bounds-draft.c';output=p/'renderer-bounds-draft.wasm';cmd=b['command'][:]
for old,new in pairs:cmd[cmd.index(str(old))]=str(new)
cmd.insert(cmd.index('-o'),str(source));cmd[cmd.index('-o')+1]=str(output);subprocess.run(cmd,check=True)
drafts={n:h for n,h in b['draft_source_hashes'].items() if n not in {str(a.relative_to(r)) for a,_ in pairs}}
drafts.update({str(f.relative_to(r)):sha(f) for f in [*[b for a,b in pairs],source]})
output.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(output),'draft_source_hashes':drafts,'derived_from':{**b['derived_from'],**{str(a.relative_to(r)):sha(a) for a,_ in pairs}}},indent=2)+'\n')
print(output.name,output.stat().st_size,sha(output))
