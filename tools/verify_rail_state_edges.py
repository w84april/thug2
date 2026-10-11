"""Additional original rail-state paths; baseline observations stay pinned."""
from pathlib import Path
source=Path('tools/verify_rail_state.py').read_text()
prefix=source.split('for special,node,speed in ')[0].replace('rail-state','rail-state-edges')
prefix=prefix.replace('*(start+end+start)','*([min(a,b) for a,b in zip(start,end)]+[max(a,b) for a,b in zip(start,end)]+start)')
exec(compile(prefix,'<complete rail runtime edge graph>','exec'))
for flags in [1,255]:
 update(extra=[patch(SKATER_STATE+o,'<B',flags) for o in [0x78,0xa8,0x80,0xb0,0x50]],label='timestamp clearing '+str(flags))
for reverse,slope,speed in itertools.product([0,1,255],[-100.,100.],[-1.,1.]):
 update(slope=slope,speed=speed,extra=[patch(PHYS+0x34c,'<B',reverse)],label='slope reverses velocity and board heading')
for special,z in itertools.product([False,True],[50.,90.,99.,100.,100.01,100.2]):
 update(special=special,node=1,z=z,speed=-100.,label='backwards linked-rail continuation')
for backwards,x in itertools.product([False,True],[-200.,-100.,0.,100.,200.]):
 positions=[[0,20000,j*100,1] for j in range(4)];positions[0 if backwards else 2][0]=x
 offsets=[]
 for j in range(3):
  start,end=positions[j:j+2]
  offsets += [patch(RAILS+j*0x54,'<12f',*([min(a,b) for a,b in zip(start,end)]+[max(a,b) for a,b in zip(start,end)]+start))]
 update(node=1 if backwards else 0,z=90 if backwards else 110,speed=-100 if backwards else 100,extra=offsets,label='sharp adjacent corner transition')
update(node=1,z=205,speed=100,label='forward terminal rail endpoint')
update(z=110,speed=100,extra=[patch(RAILS+0x54+0x48,'<I',0)],label='forward disabled linked rail')
for enabled in [1,255]:
 update(extra=[patch(WORLD+0x44,'<I',enabled)],label='rail node name and notification gate')
# Real transform-component lookup and contact transport. Rails are local to the
# owner; component_world_transform writes their actual owned transform.
for angle,dx in itertools.product([0.,.3,-.7],[0.,2.]):
 c=math.cos(angle);s=math.sin(angle);matrix=[c,0,-s,0,0,1,0,0,s,0,c,0,0,0,0,1]
 extra=[patch(GROUND_GATE+0x18,'<I',GCONTACT),patch(GCONTACT,'<I',GOWNER),patch(GCONTACT+0xc,'<16f',*identity),patch(GCONTACT+0x4c,'<4f',0,20000,0,1),patch(GOWNER+0x100,'<I',TRANS_COMPONENT),patch(GOWNER+0x4c,'<4f',dx,20000,-dx,1),patch(GOWNER+0x6c,'<16f',*matrix),patch(TRANSFORM+0x40,'<I',RAILS),patch(PHYS+0x230,'<I',TRANSFORM)]
 for i in range(3):extra += [patch(RAILS+i*0x54,'<12f',0,0,i*100,1,0,0,(i+1)*100,1,0,0,i*100,1)]
 update(extra=extra,label='moving rail carries and rotates player')
# Full original training collision; put the supplied rail along the actual
# contact normal and move from its front side through the surface. No result
# or surface-query callee is substituted.
for face,special in itertools.product([0,1,3,13,30,34,39,46,70,129],[False,True]):
 data=bytes.fromhex(loader['queries'][face]['result']);point=list(struct.unpack_from('<4f',data,16));normal=list(struct.unpack_from('<4f',data))
 position=[point[j]+2*normal[j] for j in range(3)]+[1]
 extra=[patch(BODIES+0x4c,'<4f',*position),patch(BODIES+0x5c,'<4f',*position),patch(BODIES+0xac,'<4f',*([-100*v for v in normal[:3]]+[0])),patch(PHYS+0x8c,'<f',.03)]
 for i in range(3):
  start=[point[j]+(50-i*100)*normal[j] for j in range(3)]+[1];end=[point[j]+(50-(i+1)*100)*normal[j] for j in range(3)]+[1]
  extra += [patch(RAILS+i*0x54,'<12f',*([min(a,b) for a,b in zip(start,end)]+[max(a,b) for a,b in zip(start,end)]+start))]
 extra += [patch(RAILS+2*0x54+0x48,'<I',0)]
 update(special=special,extra=extra,label='original training face '+str(face))
for target,value in [(PHYS+0x22c,RAILS),(PHYS+0x1528,SKATER_STATE2),(PHYS+0x1514,SOUND2)]:
 update(z=110,extra=[patch(GOBS+4,'<4I',target,value,4,0xa7662059)],label='linked rail event mutates '+hex(target))
# Keep actual state across frames and copy the previous position through the
# original vector routine, matching the enclosing movement update's contract.
bind(0x402320,'thug_vector_copy',1,'word')
rail_edge_compare=compare
rail_repeat=8
def compare(calls,p,changes=None,label='rail repeated frames'):
 return rail_edge_compare(calls[:-1]+[item for frame in range(rail_repeat) for item in [call(0x402320,BODIES+0x5c,[BODIES+0x4c]),calls[-1]]],p,changes,label)
for slope,speed in itertools.product([-25.,0.,25.],[-30.,30.]):
 update(node=1,z=150,slope=slope,speed=speed,label='eight retained grinding frames')
update('natas',extra=[patch(PHYS+0x2ec,'<B',1)],label='eight retained Natas frames')
rail_edge_source=Path('tools/verify_rail_state.py').read_text()
tail=rail_edge_source[rail_edge_source.index("\nscope=")+1:].replace('rail-state','rail-state-edges').replace('rail_state','rail_state_edges')
exec(compile(tail,'<save original rail edges>','exec'))
