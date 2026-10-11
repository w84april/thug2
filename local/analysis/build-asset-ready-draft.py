import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
b=json.loads((p/'scene-finalize-draft.build.json').read_text())
for n,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/n)==h,n
pairs=[]
def derive(old,new,changes):
 old=p/old;new=p/new;s=old.read_text()
 for a,z in changes:
  assert s.count(a)==1,(old,a);s=s.replace(a,z)
 new.write_text(s);pairs.append((old,new))
derive('material-factory-derived.c','asset-ready-factory-derived.c',[(
 '#include "material-texture-derived.c"','#include "asset-ready-texture-derived.c"')])
derive('material-texture-derived.c','asset-ready-texture-derived.c',[(
 '#include "material-model-asset-derived.c"','#include "asset-ready-model-derived.c"')])
old=p/'material-model-asset-derived.c';s=old.read_text();start=s.index('/* Partial00409c70:');end=s.index('/* 0040a140:',start)
s=s[:start]+'''/* 00409c70: parse, attach data, release temporary options/files, mark ready.
 * The geometry dependency still explicitly traps on unrecovered formats. */
void thug_model_geometry_load_prefix_draft(uint32_t,const void *,uint32_t,const void *,void *,uint32_t,uint32_t,uint32_t,const ThugMemory *);
void *thug_model_geometry_load_draft(uint32_t,const void *,uint32_t,const void *,void *,uint32_t,uint32_t,uint32_t,const ThugMemory *);
void (*thug_model_buffer_pending_draft)(uint32_t,const void *,uint32_t,const void *,void *,uint32_t,uint32_t,uint32_t,const ThugMemory *)=thug_model_geometry_load_prefix_draft;
void thug_model_asset_parse_draft(ThugAsset *a,const void *data,uint32_t size,const ThugMemory *m){
    ThugAsset *dependency=(void *)(uintptr_t)a->unknown_34;
    void *dictionary=methods(dependency)->data(dependency);
    const uint8_t *options=model_pointer(a,0x50);
    if(thug_model_buffer_pending_draft!=thug_model_geometry_load_prefix_draft){
        if(thug_model_buffer_pending_draft)thug_model_buffer_pending_draft(a->unknown_4,data,size,
            (void *)(uintptr_t)texture_word(options,8),dictionary,texture_word(options,4),options[16],options[0],m);
        __builtin_trap();
    }
    void *model=thug_model_geometry_load_draft(a->unknown_4,data,size,
        (void *)(uintptr_t)texture_word(options,8),dictionary,texture_word(options,4),options[16],options[0],m);
    methods(a)->set_data(a,model);
    if(((uint8_t *)model_pointer(a,0x50))[17]&&a->buffer)methods(a)->release_buffer(a,m);
    thug_asset_options_release_draft(model_pointer(a,0x50));model_set_pointer(a,0x50,0);
    if(a->file){thug_asset_io_draft->close(thug_asset_io_draft->context,a->file);a->file=0;}
    ThugAsyncFile *file=model_pointer(a,0x54);
    if(file){thug_asset_io_draft->close(thug_asset_io_draft->context,file);model_set_pointer(a,0x54,0);}
    void *companion=model_pointer(a,0x58);
    if(companion){m->release(m->context,companion);model_set_pointer(a,0x58,0);}
    thug_asset_finish_parse_draft(a,data,size);
}
/* Preserve the older comparison export's identity and explicit early hooks. */
void thug_model_asset_parse_prefix_draft(ThugAsset *a,const void *data,uint32_t size,const ThugMemory *m){thug_model_asset_parse_draft(a,data,size,m);}
''' + s[end:]
s=s.replace('.parse=thug_model_asset_parse_prefix_draft,','.parse=thug_model_asset_parse_draft,.set_data=thug_asset_set_data_draft,')
new=p/'asset-ready-model-derived.c';new.write_text(s);pairs.append((old,new))
derive('scene-finalize-material-derived.c','asset-ready-material-derived.c',[
 ('void thug_model_render_cache_reset_draft(void);','void thug_model_render_cache_reset_draft(void);\nvoid thug_model_companion_load_draft(void *,const uint8_t *,const ThugMemory *);'),
 ('void thug_model_geometry_load_prefix_draft(uint32_t key,','void *thug_model_geometry_load_draft(uint32_t key,'),
 ('    if(companion)__builtin_trap(); /* missing companion parser4b7c60 */','    thug_model_companion_load_draft(model,companion,m);'),
 ('''    if(thug_model_object_ready_pending_draft)thug_model_object_ready_pending_draft(model);
    __builtin_trap(); /* 409cb0:48c030 returned;asset finalization pending */''','''    if(thug_model_object_ready_pending_draft){thug_model_object_ready_pending_draft(model);__builtin_trap();}
    return model;''')])
new=p/'asset-ready-material-derived.c'
new.write_text(new.read_text()+'''
/* Older void entry retained for comparison callbacks; default asset path uses
 * the real returned model through thug_model_geometry_load_draft. */
void thug_model_geometry_load_prefix_draft(uint32_t key,const void *data,uint32_t size,const void *companion,void *dictionary,uint32_t offset,uint32_t skin,uint32_t flag,const ThugMemory *m){
    (void)thug_model_geometry_load_draft(key,data,size,companion,dictionary,offset,skin,flag,m);
}
''')
derive('model-texture-load-prefix.c','asset-ready-load-derived.c',[
 ('void thug_model_texture_load_prefix_draft(', 'void (*thug_model_asset_ready_pending_draft)(void *,void *,void *);\nvoid thug_model_texture_load_prefix_draft('),
 ('    m->allocate(m->context,24,1); /* part retained by the suspended original call */','    void *part=m->allocate(m->context,24,1); /* part retained by the suspended original call */'),
 ('    thug_asset_get_or_load_draft(manager,path,','    void *model=thug_asset_get_or_load_draft(manager,path,'),
 ('    __builtin_trap();\n}', '    if(thug_model_asset_ready_pending_draft)thug_model_asset_ready_pending_draft(renderer,part,model);\n    __builtin_trap(); /* 493798: model asset returned, renderer association pending */\n}')])
source=p/'asset-ready-draft.c';output=p/'asset-ready-draft.wasm';cmd=b['command'][:]
for old,new in pairs:
 if str(old) in cmd:cmd[cmd.index(str(old))]=str(new)
cmd.insert(cmd.index('-o'),str(source));cmd[cmd.index('-o')+1]=str(output);subprocess.run(cmd,check=True)
drafts={n:h for n,h in b['draft_source_hashes'].items() if n not in {str(a.relative_to(r)) for a,_ in pairs}}
drafts.update({str(f.relative_to(r)):sha(f) for f in [*[b for a,b in pairs],source]})
output.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(output),'draft_source_hashes':drafts,'derived_from':{**b['derived_from'],**{str(a.relative_to(r)):sha(a) for a,_ in pairs}}},indent=2)+'\n')
print(output.name,output.stat().st_size,sha(output))
