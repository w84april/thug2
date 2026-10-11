#include "../../src/graphics/mesh.h"
#include "../../src/core/vector.h"
#include "../../src/core/sort.h"
#include "../../src/platform/math.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((uint8_t *)p+o,&v,4);}
static void *pointer(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void put_number(void *p,unsigned o,float v){__builtin_memcpy((uint8_t *)p+o,&v,4);}
static uint16_t half(const void *p,unsigned o){uint16_t v;__builtin_memcpy(&v,(const uint8_t *)p+o,2);return v;}
#define R thug_platform_round_x87_single
uint32_t thug_mesh_index_buffer_upload_draft(void *);
uint32_t thug_mesh_vertex_buffer_upload_draft(void *);
/* 004d7580,1373bytes. Valid serialized kinds1/2 and four accessible vertices.
 * Normal Z and two edge coordinates retain the x87 exponent until their
 * original spills. Index upload is repeated; vertex mode10 suppresses its GPU
 * upload while the CPU coordinates change into the billboard's local basis. */
void thug_mesh_billboard_prepare_draft(void *mesh,uint32_t kind,const float *pivot,const float *axis,const ThugMemory *m){
    if(kind!=1&&kind!=2)__builtin_trap();
    void *record=m->allocate(m->context,36,1);put(mesh,0x4c,(uintptr_t)record);
    if(kind==1)put(record,0,0);
    else {double dot=R(R(R((double)axis[2]*0.0)+R((double)axis[0]*0.0))+axis[1]);put(record,0,__builtin_fabs(dot)>(double)0.9900000095367432f?1:2);}
    record=pointer(mesh,0x4c);for(unsigned i=0;i<4;i++)put(record,4+i*4,word(pivot,i*4));
    record=pointer(mesh,0x4c);if(word(record,0)==2)for(unsigned i=0;i<4;i++)put(record,20+i*4,word(axis,i*4));
    void *vertex=pointer(mesh,0xcc),*data=pointer(vertex,12);put(vertex,16,0);put(vertex,20,word(vertex,0));put(vertex,24,0x10);
    void *index=pointer(mesh,0x54),*indices=pointer(index,16);uint32_t stride=((uint8_t *)mesh)[0x18];
    uint8_t *a=(uint8_t *)data+half(indices,0)*stride,*b=(uint8_t *)data+half(indices,2)*stride,*c=(uint8_t *)data+half(indices,4)*stride;
    float bx=(float)R((double)number(c,0)-number(a,0)),by=(float)R((double)number(c,4)-number(a,4)),bz=(float)R((double)number(c,8)-number(a,8));
    float ax=(float)R((double)number(b,0)-number(a,0));double ay=R((double)number(b,4)-number(a,4)),az=R((double)number(b,8)-number(a,8));
    float normal[4]={0,0,0,0};normal[0]=(float)R(R(ay*bz)-R(az*by));normal[1]=(float)R(R(az*bx)-R((double)bz*ax));
    double nz=R(R((double)by*ax)-R(ay*bx));normal[2]=(float)nz;
    double length=R(__builtin_sqrt(R(R(R((double)normal[0]*normal[0])+R(nz*nz))+R((double)normal[1]*normal[1]))));
    if(length>0){double inverse=R(1.0/length);normal[0]=(float)R((double)normal[0]*inverse);normal[1]=(float)R((double)normal[1]*inverse);nz=R(nz*inverse);normal[2]=(float)nz;}
    thug_mesh_index_buffer_upload_draft(index);
    float right[4],up[4];uint32_t type=word(pointer(mesh,0x4c),0);
    if(type==2){thug_vector_cross(right,normal,axis);thug_vector_normalize(right);}
    else if(type<=3){
        double yzero=R((double)normal[1]*0.0);
        right[0]=(float)R(yzero-normal[2]);right[1]=(float)R(R((double)normal[2]*0.0)-R((double)normal[0]*0.0));right[2]=(float)R((double)normal[0]-yzero);right[3]=0;thug_vector_normalize(right);
    }else __builtin_trap(); /* original basis would be uninitialized */
    thug_vector_cross(up,right,normal);thug_vector_normalize(up);
    for(unsigned i=0;i<4;i++){
        void *v=(uint8_t *)data+i*((uint8_t *)mesh)[0x18];double x=R((double)number(v,0)-pivot[0]),y=R((double)number(v,4)-pivot[1]),z=R((double)number(v,8)-pivot[2]);
        put_number(v,0,(float)R(R(R(x*right[0])+R(z*right[2]))+R(y*right[1])));
        put_number(v,4,(float)R(R(R(x*up[0])+R(z*up[2]))+R(y*up[1])));
        put_number(v,8,(float)R(R(R(x*normal[0])+R(z*normal[2]))+R(y*normal[1])));
    }
    put(mesh,0,word(mesh,0)|0x10);thug_mesh_vertex_buffer_upload_draft(vertex);
}
/* 004cebe0: only textured materials enter the table. Preserve insertion before
 * sorting and add the mesh to the selected group after the array has moved. */
void thug_material_table_add_mesh_draft(ThugMaterialTable *table,ThugRenderMesh *mesh,const ThugMemory *m){
    ThugRenderMaterial *material=pointer(mesh,0x14);if(!material||!word(material,0x30))return;
    ThugMaterialGroup *group=thug_material_table_find(table,material);
    if(!group){
        group=m->allocate(m->context,20,1);if(group)thug_material_group_initialize(group,pointer(mesh,0x14),m);
        table->groups[table->count]=group;table->count=(int32_t)((uint32_t)table->count+1);
        thug_crt_qsort(table->groups,(uint32_t)table->count,4,thug_material_group_compare);
    }
    thug_material_group_add_mesh(group,mesh,m);
}
#include "../../src/core/bounds.h"
#include "../../src/core/lookup.h"
extern uint32_t (*thug_scene_file_read_draft)(void *,uint32_t,uint32_t,void *);
void *(*thug_scene_file_open_draft)(const char *,const char *);
uint32_t (*thug_scene_file_close_draft)(void *);
static uint32_t take(void *file){uint32_t v;thug_scene_file_read_draft(&v,4,1,file);return v;}
static uint32_t negate(uint32_t v){if((v&0x7f800000)==0x7f800000&&(v&0x7fffff))v|=0x400000;return v^0x80000000;}
void thug_mesh_file_parse_draft(void *,void *,uint32_t,void *,void *,uint32_t,const ThugMemory *);
void thug_mesh_set_bounds_draft(void *,const void *,uint32_t,const void *,const void *);
void thug_model_geometry_append_mesh_draft(void *,void *,const ThugMemory *);
/* Partial004c6b10: streamed sectors, including billboard meshes. Additional
 * material layers4d0d30 are still unavailable and explicitly trap; none occur
 * among the original training scene's851 referenced materials. */
uint8_t thug_model_sector_file_parse_draft(void *sector,void *file,void *aux,const ThugMemory *m){
    void *geometry=pointer(sector,0x14);put(sector,4,take(file));uint32_t bone=take(file);
    thug_scene_file_read_draft((uint8_t *)sector+0x1c,4,1,file);thug_scene_file_read_draft((uint8_t *)geometry+0x40,4,1,file);
    uint32_t box[6],sphere[4];thug_scene_file_read_draft(box,4,6,file);
    for(unsigned i=0;i<3;i++)put(geometry,0x14+i*4,box[i]);put(geometry,0x20,0x3f800000);
    for(unsigned i=0;i<3;i++)put(geometry,0x24+i*4,box[3+i]);put(geometry,0x30,0x3f800000);
    thug_scene_file_read_draft(sphere,4,4,file);
    uint32_t kind=0,discarded[4],pivot[4],axis[4];
    if(word(sector,0x1c)&0x800000){
        kind=take(file);thug_scene_file_read_draft(discarded,12,1,file);thug_scene_file_read_draft(pivot,12,1,file);thug_scene_file_read_draft(axis,12,1,file);
        discarded[2]=negate(discarded[2]);discarded[3]=0;pivot[2]=negate(pivot[2]);pivot[3]=0;axis[3]=0;
    }
    for(uint32_t serial=0;serial<word(geometry,0x40);serial++){
        void *mesh=m->allocate(m->context,216,1);if(mesh)thug_render_mesh_initialize(mesh);
        uint32_t bounds[10];thug_scene_file_read_draft(bounds,4,3,file);bounds[3]=take(file);
        thug_scene_file_read_draft(bounds+4,4,3,file);thug_scene_file_read_draft(bounds+7,4,3,file);
        uint32_t flags=take(file);if(flags&0x400)put(mesh,0,word(mesh,0)|2);if(flags&0x20000)put(mesh,0,word(mesh,0)|0x20000);
        uint32_t key=take(file),strips=take(file);if(strips>8)__builtin_trap();void *indices[8]={0};
        for(uint32_t i=0;i<strips;i++){uint32_t n=take(file);m->temp_scope(m->context,2);indices[i]=m->allocate(m->context,n*2,1);m->temp_scope(m->context,0);thug_scene_file_read_draft(indices[i],2,n,file);}
        uint16_t low=serial;__builtin_memcpy((uint8_t *)mesh+0x20,&low,2);flags=word(sector,0x1c);
        thug_mesh_file_parse_draft(mesh,file,key,pointer(pointer(geometry,0x34),0x280),(flags&0x800000)?0:aux,(flags>>23)&0xffffff01,m);
        thug_mesh_set_bounds_draft(mesh,bounds,bounds[3],bounds+4,bounds+7);
        thug_bounds_expand((ThugBounds *)((uint8_t *)pointer(pointer(geometry,0x34),0x280)+0x44),(const float *)(bounds+4));
        thug_bounds_expand((ThugBounds *)((uint8_t *)pointer(pointer(geometry,0x34),0x280)+0x44),(const float *)(bounds+7));
        if(word(sector,0x1c)&0x800000){thug_mesh_billboard_prepare_draft(mesh,kind,(const float *)pivot,(const float *)axis,m);thug_material_table_add_mesh_draft(thug_mesh_material_table,mesh,m);}
        if(word(sector,0x1c)&0x200000)put(mesh,0,word(mesh,0)|0x200);
        thug_model_geometry_append_mesh_draft(geometry,mesh,m);((uint8_t *)mesh)[0x1f]=bone;
        void *material=pointer(mesh,0x14);if(material&&((word(material,0x20)&0x8000000)||word(material,0x18)))__builtin_trap();
        for(unsigned i=0;i<8;i++)m->release(m->context,indices[i]);
    }
    uint32_t count=0;void *node=pointer(pointer(geometry,0x38),12);
    while(word(node,4)!=0xffffffff&&node){node=pointer(node,12);count++;}put(geometry,0x40,count);return 1;
}
void *thug_model_scene_data_initialize_draft(void *);
ThugObjectLookupTable *thug_material_file_parse_draft(void *,const ThugObjectLookupTable *,const ThugMemory *);
void *thug_model_scene_construct_draft(void *,uint32_t,const ThugMemory *);
void *thug_model_scene_new_sector_draft(void *,const ThugMemory *);
void *thug_model_geometry_create_draft(const ThugMemory *);
void thug_model_sector_bind_geometry_draft(void *,void *);
void thug_model_geometry_mesh_list_initialize_draft(void *,const ThugMemory *);
void thug_model_scene_register_sector_draft(void *,void *,const ThugMemory *);
void thug_model_scene_data_bounds_draft(void *);
/* Partial004b36d0: real file-to-scene path. Additional80byte tail records remain
 * a trap; the training scene has a zero tail count. Platformopen/close are
 * explicit host boundaries, not recovered Windows filesystem code. */
void *thug_model_scene_file_load_draft(const char *name,void *textures,uint32_t flag_a,uint32_t flag_b,uint32_t flag_c,void *aux,const ThugMemory *m){
    void *header=m->allocate(m->context,132,1);if(header)thug_model_scene_data_initialize_draft(header);
    ((uint8_t *)header)[0x40]=flag_c;void *file=thug_scene_file_open_draft(name,"rb");if(!file)return 0;
    (void)take(file);(void)take(file);(void)take(file);put(header,0x18,(uintptr_t)thug_material_file_parse_draft(file,pointer(textures,12),m));
    uint32_t count=take(file),shift=1,slots=2;while(slots<count*2&&shift<12){slots*=2;shift++;}
    void *scene=m->allocate(m->context,644,1);if(scene)thug_model_scene_construct_draft(scene,shift,m);
    ((uint8_t *)scene)[0x8c]=flag_a;((uint8_t *)scene)[0x8d]=flag_b;put(scene,0x280,(uintptr_t)header);
    for(int32_t i=0;i<(int32_t)count;i++){
        void *sector=thug_model_scene_new_sector_draft(scene,m),*geometry=thug_model_geometry_create_draft(m);
        put(geometry,0x34,(uintptr_t)scene);thug_model_sector_bind_geometry_draft(sector,geometry);thug_model_geometry_mesh_list_initialize_draft(geometry,m);
        if(thug_model_sector_file_parse_draft(sector,file,aux,m))thug_model_scene_register_sector_draft(scene,sector,m);
    }
    thug_model_scene_data_bounds_draft(header);if((int32_t)take(file)>0)__builtin_trap();
    thug_scene_file_close_draft(file);return scene;
}
