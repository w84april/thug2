#include "../../src/collision/load.h"
#include "../../src/script/params.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((uint8_t *)p+o,&v,4);}
static void *pointer(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
void *thug_model_scene_new_sector_draft(void *,const ThugMemory *);
void thug_model_scene_register_sector_draft(void *,void *,const ThugMemory *);
void thug_geometry_set_enabled_draft(void *,uint32_t);
void *thug_collision_load_observer_draft; /* 006fa7c8: virtual +4 receiver */
/* 0048df10. */
void thug_geometry_bind_collision_draft(void *geometry,void *data){put(geometry,8,(uintptr_t)data);}
/* 0049e890. */
void thug_sector_add_flags_draft(void *sector,uint32_t flags){put(sector,8,word(sector,8)|flags);}
/* 0049eaa0. Existing attachment wins, including when the new argument is null. */
uint8_t thug_sector_attach_collision_draft(void *sector,ThugCollisionInstance *instance){
    if(pointer(sector,0x18))return 0;
    put(sector,0x18,(uintptr_t)instance);
    void *geometry=pointer(sector,0x14);
    if(geometry)thug_geometry_bind_collision_draft(geometry,(void *)instance->geometry);
    return 1;
}
/* 0049d590. Fresh validated version-10 buffer; initialized scene and heap.
 * Original allocation failure behavior is retained. Data is relocated in place.
 * The optional observer uses 004a1090's +4 virtual dispatch with no stack args.
 */
uint8_t thug_scene_collision_load_draft(void *scene,void *data,uint32_t flag,const ThugMemory *m){
    uint8_t *s=scene;
    thug_collision_load((uintptr_t)scene,data,(int32_t *)(s+0x158),
        (ThugStaticCollisionInstance **)(s+0x15c),(ThugCollisionObject **)(s+0x160),
        (ThugBounds *)(s+0xb0),flag,m);
    if((int32_t)word(scene,0x158)>0){
        if(s[0x8c]){
            ThugCollisionGrid *grid=m->allocate(m->context,0x4b30,1);
            if(grid){thug_bounds_reset(&grid->bounds);for(unsigned i=0;i<400;i++)thug_collision_cell_initialize(&grid->cells[i]);}
            put(scene,0xd4,(uintptr_t)grid);
            thug_collision_grid_initialize(grid,(ThugBounds *)(s+0xb0));
            thug_collision_grid_populate(grid,pointer(scene,0x15c),(int32_t)word(scene,0x158),m);
        }
        for(int32_t i=0;i<(int32_t)word(scene,0x158);i++){
            ThugStaticCollisionInstance *instances=pointer(scene,0x15c);
            uint32_t key=instances[i].base.checksum;
            void *sector=thug_object_table_find(pointer(scene,0xd0),&key,0);
            if(!sector){
                sector=thug_model_scene_new_sector_draft(scene,m);
                instances=pointer(scene,0x15c);put(sector,4,instances[i].base.checksum);
                thug_geometry_set_enabled_draft(sector,1);
                thug_model_scene_register_sector_draft(scene,sector,m);
            }
            instances=pointer(scene,0x15c);
            thug_sector_attach_collision_draft(sector,&instances[i].base);
            thug_sector_add_flags_draft(sector,0x40);
        }
    }
    if(thug_script_get_global_integer(0xba1e4254,0)){
        void *receiver=thug_collision_load_observer_draft;
        void (*update)(void *)=(void (*)(void *))(uintptr_t)word(pointer(receiver,0),4);
        update(receiver);
    }
    return 1;
}
