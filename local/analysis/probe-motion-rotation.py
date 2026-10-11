"""Original rotation command bodies, sign normalization and full registration."""
from pathlib import Path
exec(compile(Path('local/analysis/probe-motion-frame.py').read_text().split('# Repeated rotations')[0],'<verified Motion graph>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x423f10,171,'motion_rotation_direction',1,'void',False,False,True),
 (0x424b90,437,'motion_rotate_x_command',2,'word',False,False,True),
 (0x424d50,511,'motion_rotate_y_command',2,'word',False,False,True),
 (0x424f50,511,'motion_rotate_z_command',2,'word',False,False,True),
 (0x640e30,1381,'motion_rotation_descriptors_initialize',0,'void',False,False,False),
 (0x423130,21,'motion_rotation_descriptors_register',0,'void',True,False,False)]
for a,n,name,nargs,result,heap,diag,this in specs:bind_new(a,n,'thug_'+name+'_draft',nargs,result,heap,diag,this)
bind(0x42bb20,'thug_component_descriptor_scoped',3,'word',True,True)
functions['0x42bb20']['pointer_args']=[0]
bind(0x425c70,'thug_motion_rotate_axes_draft',0)
metadata=json.loads((folder/'motion-rotation-descriptors.json').read_text());pointer_globals=[]
for row in metadata['table']:
 a=row['address'];off=a-0x681eb8;exports.append([a,'thug_motion_rotation_descriptors_draft',off])
 for j,value in enumerate(row['words']):
  glob('thug_motion_rotation_descriptors_draft',a+4*j,value,offset=off+4*j)
  if j==2:pointer_globals.append(index[a+4*j])
 if row['member']:function_exports.append([row['member'],row['export']])
initial=bytes(memory);oracle.initial=initial
for fill in [0,0xa5a5a5a5,0xffffffff]:
 g=MotionGraph();changes={row['address']+j:fill for row in metadata['table'] for j in [8,12,16,20]}
 run_motion(g,[call(0x640e30),call(0x640e30),call(0x423130),call(0x423130)],f'full descriptor initialization and registration/{fill}',changes)
# Valid internal axis indexes; all fields, unrelated axes and flags are checked.
for axis in range(3):
 for angle in [-100.,-0.,0.,.5,1e30]:
  for rates in [(0.,-0.,1.,-2.),(-3.,4.,-5.,6.),(1e30,-1e30,1e-30,-1e-30)]:
   g=MotionGraph();g.axis(axis,speed=rates[0],target_speed=rates[1],accel=rates[2],brake=rates[3],angle=angle)
   run_motion(g,[call(0x423f10,P,[axis])]*2,f'direction/{axis}/{angle}/{rates}')
ANGLE=0xff7ebaf6;SPEED=0xf0d90109;ACCEL=0x85894a84;BRAKE=0xf59ff7d7;ALTERNATE=0x26af9dc9
values=[[],[(ANGLE,0.)],[(ANGLE,-0.)],[(ANGLE,90.)],[(ANGLE,-90.)],[(SPEED,180.)],[(SPEED,-180.)],[(BRAKE,30.)],[(BRAKE,0.)],[(ACCEL,20.)],[(ACCEL,0.)],
 [(ANGLE,90.),(SPEED,-60.)],[(ANGLE,-90.),(SPEED,60.)],[(ANGLE,90.),(BRAKE,30.),(SPEED,10.)],[(ANGLE,-90.),(ACCEL,20.),(SPEED,60.)],
 [(BRAKE,30.),(ACCEL,20.),(SPEED,10.)],[(ACCEL,-20.),(SPEED,-60.)],[(ANGLE,0.),(BRAKE,30.),(ACCEL,20.),(SPEED,100.)],
 [(ANGLE,1e30),(SPEED,1e30),(ACCEL,1e30)],[(ANGLE,1e-30),(SPEED,-1e-30)],[(ANGLE,360.),(BRAKE,-5.),(SPEED,0.)]]
for axis,entry in enumerate([0x424b90,0x424d50,0x424f50]):
 for alternate in [False,True]:
  for flags in [0,7,0x47,0x800000a7]:
   for k,props in enumerate(values):
    g=MotionGraph();g.put(P+0x18,'<I',flags);g.put(P+0x1c,'<I',0x80000000|(0xe0 if k%2 else 0))
    for a in range(3):g.axis(a,speed=-.5-a,target_speed=2+a,accel=3+a,brake=4+a,angle=-5-a,accum=6+a)
    items=[(key,2,bits(value)) for key,value in props]+([(0,13,ALTERNATE)] if alternate else [])
    params=g.structure(items)
    run_motion(g,[call(entry,P,[params,0])]*2,f'command/{axis}/{alternate}/{flags:x}/{k}')
# Integer getters, included parameter structures, wrong types and signed extremes.
for entry in [0x424b90,0x424d50,0x424f50]:
 for kind in ['integer','included','wrong']:
  for value in [0,1,0x7fffffff,0x80000000,0xffffffff]:
   g=MotionGraph();params=g.structure([(SPEED,13 if kind=='wrong' else 1,value),(ANGLE,1,180)])
   if kind=='included':g.symbol(0x11223344,10,params);params=g.structure([(0,13,0x11223344)])
   run_motion(g,[call(entry,P,[params,0])],f'parameter type/{entry:x}/{kind}/{value:x}')
# Real descriptor/member dispatch and subsequent original matrix movement.
for axis,entry in enumerate([0x424b90,0x424d50,0x424f50]):
 row=next(row for row in metadata['table'] if row['member']==entry)
 for alternate in [False,True]:
  for props in [[(SPEED,360.)],[(ANGLE,20.),(SPEED,180.)],[(ANGLE,-30.),(ACCEL,45.),(SPEED,90.)],[(BRAKE,40.),(SPEED,0.)]]:
   g=MotionGraph();g.put(P,'<2I',0x64620c,0x0a015e17);fields.add(P)
   for a in range(3):g.axis(a,speed=2,target_speed=2,angle=1)
   s=g.structure([(k,2,bits(v)) for k,v in props]+([(0,13,ALTERNATE)] if alternate else []))
   run_motion(g,[call(0x640e30),call(0x42bb20,P,[row['address'],s,0,0])]+[call(0x425c70,P)]*3,f'descriptor then real rotation/{axis}/{alternate}/{props}')
print('MISSING',{hex(a):[hex(i.address) for i in code if not hits[i.address]] for a,code in coverage.items()},flush=True)
scope='Six complete routines: three Motion rotation commands, shared target-direction normalization, full49-row static descriptor initializer and registration. Rotation angle, acceleration/deceleration precedence, existing-rate retention, zero stopping, alternate axes and real subsequent matrix updates compare against the original, with finite float inputs including signed zero and wide exponents. All48 registered command identities are retained;45 unrecovered member bodies remain explicit distinct traps, not implemented behavior and not counted as recovered. Main engine and earlier checkpoints are unchanged; full scene and playability remain unfinished.'
finish('motion-rotation',scope,{}, {**extra,'pointer_globals':pointer_globals})
