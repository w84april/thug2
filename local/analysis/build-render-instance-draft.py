import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
b=json.loads((p/'asset-ready-draft.build.json').read_text())
for n,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/n)==h,n
pairs=[]
def derive(old,new,changes):
 old=p/old;new=p/new;s=old.read_text()
 for a,z in changes:
  assert s.count(a)==1,(old,a);s=s.replace(a,z)
 new.write_text(s);pairs.append((old,new))
derive('model-configuration-initialize-derived.c','render-instance-initialize-derived.c',[
 ('typedef struct {uintptr_t unavailable[27];void (*lights)(void *,void *);} GeometryMethods;',
 '''typedef struct {
 uintptr_t unused0[3];uint8_t (*load)(void *,void *,void *,uint32_t,const ThugMemory *);
 uintptr_t unused10[23];void (*lights)(void *,void *);uintptr_t unused70[4];uint32_t (*flag16)(void *,uint32_t);
} GeometryMethods;
uint8_t thug_model_geometry_load_instance_draft(void *,void *,void *,uint32_t,const ThugMemory *);
uint32_t thug_model_virtual_true_draft(void *,uint32_t);'''),
 ('const GeometryMethods thug_model_geometry_lights_methods_draft={.lights=thug_component_empty_one};',
 'const GeometryMethods thug_model_geometry_lights_methods_draft={.load=thug_model_geometry_load_instance_draft,.lights=thug_component_empty_one,.flag16=thug_model_virtual_true_draft};')])
derive('asset-ready-load-derived.c','render-instance-load-derived.c',[
 ('void (*thug_model_asset_ready_pending_draft)(void *,void *,void *);',
 '''void (*thug_model_asset_ready_pending_draft)(void *,void *,void *);
void *thug_model_geometry_create_draft(const ThugMemory *);
uint8_t thug_model_geometry_bind_draft(void *,void *,void *,uint32_t,const ThugMemory *);
uint8_t thug_model_geometry_flag16_draft(void *,uint32_t);
void thug_model_geometry_set_lights_draft(void *,void *);
void thug_model_part_insert_draft(void *,void *,void *const *,const ThugMemory *);
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((uint8_t *)p+o,&v,4);}
static void *pointer(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static uint16_t half(const void *p,unsigned o){uint16_t v;__builtin_memcpy(&v,(const uint8_t *)p+o,2);return v;}
static void put_half(void *p,unsigned o,uint16_t v){__builtin_memcpy((uint8_t *)p+o,&v,2);}'''),
 ('''    if(thug_model_asset_ready_pending_draft)thug_model_asset_ready_pending_draft(renderer,part,model);
    __builtin_trap(); /* 493798: model asset returned, renderer association pending */''',
 '''    if(thug_model_asset_ready_pending_draft){thug_model_asset_ready_pending_draft(renderer,part,model);__builtin_trap();}
    put(part,16,thug_crc32_string(path));put_half(renderer,0x4a,half(renderer,0x4a)+1);put(part,12,0);
    void *geometry=thug_model_geometry_create_draft(m);put(part,0,(uintptr_t)geometry);
    if(!(uint8_t)route&&!geometry)return; /* original AL0; current public prefix has no result */
    thug_model_geometry_bind_draft(geometry,model,renderer,skin,m);put(part,4,word(model,4));
    thug_model_geometry_flag16_draft(pointer(part,0),((uint8_t *)renderer)[0x44]>>4&1);put(part,8,key);
    put(renderer,0x18,word(renderer,0x18)|(1u<<(((uint8_t *)renderer)[0x46]&31)));
    if(word(renderer,0x2c))thug_model_geometry_set_lights_draft(pointer(part,0),pointer(renderer,0x2c));
    put_half(renderer,0x46,half(renderer,0x46)+1);
    if(word(renderer,4)){
        typedef struct{uintptr_t unused[3];uint32_t (*set)(void *,uint32_t);} Methods;
        if((uint8_t)((const Methods *)pointer(renderer,0))->set(renderer,0))put(renderer,4,0);
    }
    put(part,20,0);thug_model_part_insert_draft((uint8_t *)renderer+0x10,pointer(renderer,0x10),&part,m);
    if(half(renderer,0x46)==1)put(renderer,0x30,thug_crc32_string(path));
    /* The actual standard branch returns AL1. Other loading routes remain
     * explicit traps above; this contextual prefix still has a void ABI. */''')])
derive('texture-asset-configuration-derived.c','render-instance-configuration-derived.c',[
 ('void thug_model_configuration_prefix_draft(void *p,const ThugScriptStructure *s){',
 'void (*thug_model_renderer_ready_pending_draft)(void *,const ThugScriptStructure *);\nvoid thug_model_configuration_prefix_draft(void *p,const ThugScriptStructure *s){'),
 ('    __builtin_trap(); /* the dependency breakpoint may not manufacture success */',
 '''    if(thug_model_load_pending_draft!=thug_model_texture_load_prefix_draft)__builtin_trap();
    if(thug_model_renderer_ready_pending_draft)thug_model_renderer_ready_pending_draft(p,s);
    __builtin_trap(); /* 421191: actual model load returned; configuration tail remains */''')])
source=p/'render-instance-draft.c';output=p/'render-instance-draft.wasm';cmd=b['command'][:]
for old,new in pairs:cmd[cmd.index(str(old))]=str(new)
cmd.insert(cmd.index('-o'),str(source));cmd[cmd.index('-o')+1]=str(output);subprocess.run(cmd,check=True)
drafts={n:h for n,h in b['draft_source_hashes'].items() if n not in {str(a.relative_to(r)) for a,_ in pairs}}
drafts.update({str(f.relative_to(r)):sha(f) for f in [*[b for a,b in pairs],source]})
output.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(output),'draft_source_hashes':drafts,'derived_from':{**b['derived_from'],**{str(a.relative_to(r)):sha(a) for a,_ in pairs}}},indent=2)+'\n')
print(output.name,output.stat().st_size,sha(output))
