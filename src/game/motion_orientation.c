#include "components.h"
#include "nodes.h"
/* 00425970. Identity first, then postmultiply X, Y and Z rotations and copy
 * the resulting basis to the separate render orientation. */
void thug_motion_orient_to_node(ThugObjectComponent *component,const ThugScriptStructure *node) {
    ThugSkaterBody *body=component->owner;
    float *basis=body->orientation;
    for(unsigned i=0;i<16;++i)basis[i]=(i%5)==0?1:0;
    float angles[4];thug_node_angles(node,angles);
    if(angles[0]!=0||angles[1]!=0||angles[2]!=0) {
        float rotation[16];basis=((ThugSkaterBody *)component->owner)->orientation;
        thug_matrix_rotation_x(rotation,angles[0]);thug_matrix_multiply(basis,basis,rotation);
        basis=((ThugSkaterBody *)component->owner)->orientation;
        thug_matrix_rotation_y(rotation,angles[1]);thug_matrix_multiply(basis,basis,rotation);
        basis=((ThugSkaterBody *)component->owner)->orientation;
        thug_matrix_rotation_z(rotation,angles[2]);thug_matrix_multiply(basis,basis,rotation);
    }
    body=component->owner;thug_matrix_copy(body->orientation_c0,body->orientation);
}
