import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
b=json.loads((p/'mesh-index-draft.build.json').read_text())
for n,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/n)==h,n
old=p/'mesh-index-draft.c';new=p/'vertex-upload-mesh-derived.c';s=old.read_text()
s=s.replace('/* Partial4d5cc0: real eight index streams and uncompressed vertex metadata,\n * stopping before4d5c30. Compressed/alternate shader routes remain unavailable. */','''void thug_mesh_vertex_load_draft(void *,const void *,uint32_t,void *);
uint32_t thug_mesh_shader_code_draft(uint32_t);
uint32_t thug_mesh_shader_skip_draft(const uint8_t **);
uint8_t thug_mesh_shader_conversion_enabled_draft;
void (*thug_mesh_bounds_pending_draft)(void *);
/* Partial4d5cc0: the standard vertex path now returns after shader selection
 * and temporary stream release. Compression/alternate loading/conversion trap. */''')
needle='''    if(thug_mesh_vertex_load_pending_draft)thug_mesh_vertex_load_pending_draft(mesh,data[0],sizes[0],aux,m);
    __builtin_trap();'''
assert s.count(needle)==1
s=s.replace(needle,'''    if(thug_mesh_vertex_load_pending_draft){thug_mesh_vertex_load_pending_draft(mesh,data[0],sizes[0],aux,m);__builtin_trap();}
    thug_mesh_vertex_load_draft(mesh,data[0],sizes[0],aux);
    uint32_t shader=take(&p);
    if(shader==1){put(mesh,0x44,thug_mesh_shader_skip_draft(&p));if(thug_mesh_shader_conversion_enabled_draft)__builtin_trap();}
    else put(mesh,0x44,thug_mesh_shader_code_draft(shader));
    *input=p;for(unsigned stream=0;stream<b[0x1a];stream++)m->release(m->context,data[stream]);''')
needle='    thug_mesh_buffer_prefix_draft(mesh,&p,material_key,header,0,m);\n    __builtin_trap();';assert s.count(needle)==1
s=s.replace(needle,'    thug_mesh_buffer_prefix_draft(mesh,&p,material_key,header,0,m);\n    if(thug_mesh_bounds_pending_draft)thug_mesh_bounds_pending_draft(mesh);\n    __builtin_trap();')
s=s.replace('/* Partial4c6650: original geometry header and first mesh, preserving the caller','/* Partial4c6650: stops before4d5900 mesh bounds, preserving the caller')
new.write_text(s)
source=p/'vertex-upload-draft.c';output=p/'vertex-upload-draft.wasm';cmd=b['command'][:];cmd[cmd.index(str(old))]=str(new);cmd.insert(cmd.index('-o'),str(source));cmd[cmd.index('-o')+1]=str(output)
subprocess.run(cmd,check=True)
drafts={n:h for n,h in b['draft_source_hashes'].items() if n!=str(old.relative_to(r))};drafts.update({str(f.relative_to(r)):sha(f) for f in [new,source]})
output.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(output),'draft_source_hashes':drafts,'derived_from':{**b['derived_from'],str(old.relative_to(r)):sha(old)}},indent=2)+'\n')
print(output.name,output.stat().st_size,sha(output))
