import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
b=json.loads((p/'mesh-register-draft.build.json').read_text())
for n,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/n)==h,n
pairs=[]
old=p/'mesh-register-draft.c';new=p/'scene-finalize-register-derived.c';s=old.read_text()
s=s.replace('const uintptr_t thug_model_mesh_node_methods_draft[1]={0};', '''void *thug_model_mesh_node_delete_draft(void *,uint32_t,const ThugMemory *);
const uintptr_t thug_model_mesh_node_methods_draft[1]={(uintptr_t)thug_model_mesh_node_delete_draft};''');new.write_text(s);pairs.append((old,new))
old=p/'mesh-register-scene-derived.c';new=p/'scene-finalize-scene-derived.c';s=old.read_text()
s=s.replace('typedef struct {uintptr_t unavailable[7];', 'void thug_model_scene_finalize_draft(void *,void *,const ThugMemory *);\ntypedef struct {uintptr_t dispose;void (*finalize)(void *,void *,const ThugMemory *);uintptr_t unavailable[5];')
s=s.replace('const uintptr_t thug_model_mesh_list_methods_draft[1]={0};','void *thug_model_mesh_sentinel_delete_draft(void *,uint32_t,const ThugMemory *);\nconst uintptr_t thug_model_mesh_list_methods_draft[1]={(uintptr_t)thug_model_mesh_sentinel_delete_draft};')
s=s.replace('={.create_sector=thug_model_scene_create_sector_draft};','={.finalize=thug_model_scene_finalize_draft,.create_sector=thug_model_scene_create_sector_draft};');new.write_text(s);pairs.append((old,new))
old=p/'mesh-register-material-derived.c';new=p/'scene-finalize-material-derived.c';s=old.read_text()
s=s.replace('void (*thug_model_scene_ready_pending_draft)(void *);', '''void (*thug_model_scene_ready_pending_draft)(void *);
void (*thug_model_object_ready_pending_draft)(void *);
void thug_model_scene_name_finalize_draft(void *,const char *,void *,const ThugMemory *);
void *thug_model_object_construct_draft(void *);
void thug_model_object_bind_scene_draft(void *,void *);
void thug_model_render_cache_reset_draft(void);
uint32_t thug_crc32_string(const char *);
/* The wrapper's original sprintf("%d\\n",key), bounded to12bytes plus NUL. */
static void model_key_name(char out[16],uint32_t key){
    char reversed[10];unsigned n=0,i=0;uint32_t magnitude=(int32_t)key<0?0-key:key;
    do{reversed[n++]='0'+magnitude%10;magnitude/=10;}while(magnitude);
    if((int32_t)key<0)out[i++]='-';while(n)out[i++]=reversed[--n];out[i++]='\\n';out[i]=0;
}''')
needle='''    if(thug_model_scene_ready_pending_draft)thug_model_scene_ready_pending_draft(scene);
    __builtin_trap(); /* 4b3490 returned;4b3ad0 continuation4b3b1c pending */''';assert s.count(needle)==1
s=s.replace(needle,'''    if(thug_model_scene_ready_pending_draft){thug_model_scene_ready_pending_draft(scene);__builtin_trap();}
    char name[16];model_key_name(name,key);put(scene,0x84,thug_crc32_string(name));put(scene,0x88,(uintptr_t)dictionary);
    thug_model_scene_name_finalize_draft(scene,name,0,m);
    void *model=thug_allocate_zeroed(200,m);if(model)thug_model_object_construct_draft(model);
    if(companion)__builtin_trap(); /* missing companion parser4b7c60 */
    thug_model_render_cache_reset_draft();thug_model_object_bind_scene_draft(model,scene);put(model,4,(uintptr_t)dictionary);
    if(thug_model_object_ready_pending_draft)thug_model_object_ready_pending_draft(model);
    __builtin_trap(); /* 409cb0:48c030 returned;asset finalization pending */''')
new.write_text(s);pairs.append((old,new))
source=p/'scene-finalize-draft.c';output=p/'scene-finalize-draft.wasm';cmd=b['command'][:]
for old,new in pairs:cmd[cmd.index(str(old))]=str(new)
cmd.insert(cmd.index('-o'),str(source));cmd[cmd.index('-o')+1]=str(output);subprocess.run(cmd,check=True)
drafts={n:h for n,h in b['draft_source_hashes'].items() if n not in {str(a.relative_to(r)) for a,_ in pairs}};drafts.update({str(f.relative_to(r)):sha(f) for f in [*[b for a,b in pairs],source]})
output.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(output),'draft_source_hashes':drafts,'derived_from':{**b['derived_from'],**{str(a.relative_to(r)):sha(a) for a,_ in pairs}}},indent=2)+'\n')
print(output.name,output.stat().st_size,sha(output))
