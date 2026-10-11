/* Test-only callback mutations and nested traversal, with observable order.
 * The callback is not an object destructor or a scene command. */
#include <stdint.h>
extern void thug_object_manager_visit_draft(void *,void (*)(void *,void *),void *);
static uint32_t *ptr(uint32_t value){return (uint32_t *)(uintptr_t)value;}
void fixture_scene_visit(void *object,void *context) {
    uint32_t *o=object,*c=context,*manager=ptr(c[0]),*log=ptr(c[1]);
    uint32_t *record=log+1+log[0]++*6;
    record[0]=(uintptr_t)object;record[1]=o[5];record[2]=o[7];
    record[3]=manager[6];record[4]=manager[7];record[5]=(uintptr_t)context;
    if(c[4]++)return;
    switch(c[3]) {
    case 1:ptr(c[5])[7]|=c[2];break;
    case 2: {
        uint32_t *node=ptr(c[5]);
        ptr(node[4])[3]=node[3];ptr(node[3])[4]=node[4];
        node[3]=node[4]=c[5];manager[7]|=c[6];break;
    }
    case 3:ptr(c[5])[1]=c[6];break;
    case 4: {
        uint32_t *node=ptr(c[5]);
        node[3]=manager[4];node[4]=c[0]+4;
        ptr(manager[4])[4]=c[5];manager[4]=c[5];manager[7]|=c[2];break;
    }
    case 5:manager[7]|=c[2];break;
    case 6: {
        /* The witness is linked into the engine's function table by the
         * fixture; its local module table index is not an engine identity. */
        void (*visit)(void *,void *)=*(void (**)(void *,void *))0x1806000;
        thug_object_manager_visit_draft(manager,visit,ptr(c[7]));break;
    }
    case 7:manager[6]=c[6];break;
    }
}
