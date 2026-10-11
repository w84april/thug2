import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
b=json.loads((p/'vertex-upload-draft.build.json').read_text())
for n,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/n)==h,n
pairs=[]
old=p/'vertex-upload-mesh-derived.c';new=p/'mesh-register-mesh-derived.c'
s=old.read_text();assert s.count('/* Partial4c6650:')==1;s=s.split('/* Partial4c6650:')[0];new.write_text(s);pairs.append((old,new))
old=p/'mesh-index-scene-derived.c';new=p/'mesh-register-scene-derived.c';s=old.read_text()
s=s[:s.index('void thug_model_scene_load_geometry_prefix_draft(')]+'''void thug_model_scene_data_bounds_draft(void *);
void thug_model_scene_load_geometry_prefix_draft(void *scene,void *header,const uint8_t *cursor,uint32_t count,const ThugMemory *m){
    ((uint8_t *)scene)[0x8c]=0;((uint8_t *)scene)[0x8d]=0;put(scene,0x280,(uintptr_t)header);
    for(int32_t i=(int32_t)count;i>0;i--){
        void *sector=thug_model_scene_new_sector_draft(scene,m),*geometry=thug_model_geometry_create_draft(m);
        put(geometry,0x34,(uintptr_t)scene);thug_model_sector_bind_geometry_draft(sector,geometry);
        thug_model_geometry_mesh_list_initialize_draft(geometry,m);
        if(thug_model_sector_parse_pending_draft!=thug_model_sector_mesh_prefix_draft){
            if(thug_model_sector_parse_pending_draft)thug_model_sector_parse_pending_draft(sector,&cursor,m);
            __builtin_trap();
        }
        thug_model_sector_mesh_prefix_draft(sector,&cursor,m);
        thug_model_scene_register_sector_draft(scene,sector,m);
    }
    thug_model_scene_data_bounds_draft(header);
    if((int32_t)word(cursor,0)>0)__builtin_trap(); /* missing optional80-byte records */
}
''';new.write_text(s);pairs.append((old,new))
old=p/'scene-construction-material-derived.c';new=p/'mesh-register-material-derived.c';s=old.read_text()
s=s.replace('void thug_model_geometry_load_prefix_draft(', 'void (*thug_model_scene_ready_pending_draft)(void *);\nvoid thug_model_geometry_load_prefix_draft(',1)
needle='    thug_model_scene_load_geometry_prefix_draft(scene,header,p,count,m);';assert s.count(needle)==1
s=s.replace(needle,needle+'\n    if(thug_model_scene_ready_pending_draft)thug_model_scene_ready_pending_draft(scene);\n    __builtin_trap(); /* 4b3490 returned;4b3ad0 continuation4b3b1c pending */')
new.write_text(s);pairs.append((old,new))
sources=[p/'mesh-register-draft.c',p/'mesh-register-sector.c'];output=p/'mesh-register-draft.wasm';cmd=b['command'][:]
for old,new in pairs:cmd[cmd.index(str(old))]=str(new)
for source in sources:cmd.insert(cmd.index('-o'),str(source))
cmd[cmd.index('-o')+1]=str(output);subprocess.run(cmd,check=True)
drafts={n:h for n,h in b['draft_source_hashes'].items() if n not in {str(a.relative_to(r)) for a,_ in pairs}};drafts.update({str(f.relative_to(r)):sha(f) for f in [*[b for a,b in pairs],*sources]})
output.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(output),'draft_source_hashes':drafts,'derived_from':{**b['derived_from'],**{str(a.relative_to(r)):sha(a) for a,_ in pairs}}},indent=2)+'\n')
print(output.name,output.stat().st_size,sha(output))
