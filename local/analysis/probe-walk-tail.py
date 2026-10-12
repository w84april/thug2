"""Connect critical-point correction, common pose updates and camera-facing events."""
from pathlib import Path
source=Path('local/analysis/probe-walk-critical.py').read_text().split('for state,offset,dt')[0]
exec(compile(source,'<preserved critical-point and common Walk graph>','exec'))
# The prerequisite prefix has installed observers for the common/animation roots.
specs += [(0x525f70,53,'thug_walk_camera_facing_draft',2,'void',False,False,True),(0x529f80,498,'thug_walk_update_camera_draft',0,'void',False,False,True)]
for row in specs[1:]:
 bind_new(*row);oracle.cpu.hook_add(UC_HOOK_CODE,observe_cache,begin=row[0],end=row[0])
functions[hex(0x525f70)]['float_args']=[1]
for row in [(0x527be0,'thug_walk_decay_model_offset_draft',0,'void',False,False),(0x527420,'thug_walk_restore_up_draft',0,'void',False,False),(0x528400,'thug_walk_filter_speed_event_draft',1,'void',False,False),(0x529ce0,'thug_walk_write_owner_draft',0,'void',False,False),(0x529800,'thug_walk_rotate_owner_draft',0,'void',False,False),(0x481640,'thug_animation_update_time',0,'void',False,False),(0x52ad10,'thug_walk_transition_frame_draft',0,'void',True,False)]:bind(*row)
CAM=P+0x18000;fields.add(P+0x1760)
class TailGraph(CriticalGraph):
 def __init__(self):
  super().__init__();self.image[CAM-BASE:CAM-BASE+0x100]=bytes(0x100);self.put(P+0x1760,'<I',CAM)
  self.parameters(overrides={**required_parameters,0xb32c972b:4,0x0f22c135:3,0xb0675803:1})
def tail():return [call(0x5278d0,P,[Q]),call(0x527be0,P),call(0x527420,P),call(0x529ce0,P),call(0x529800,P),call(0x528400,P,[0x1d537eff]),call(0x529f80,P)]
records=[]
for state,shape,limit,rotation in itertools.product([0,1,3],['empty','static wall','moving wall','floor'],[False,True],[False,True]):
 g=TailGraph();g.put(P+0x18,'<I',state);g.put(P+0x80,'<f',.001);g.put(P+0x71c,'<4f',0,0,8,1);g.put(P+0x58,'<4f',.6,.8,0,1)
 g.put(P+0x78,'<I',0x4194ecca);g.put(P+0x9c,'<f',3);g.put(P+0x704,'<2f',2,3)
 if shape.endswith('wall'):g.obstacle('z',5,moving=shape=='moving wall')
 if shape=='floor':g.put(P+0x71c,'<4f',0,8,0,1);g.put(P+0x68,'<4f',0,-4,0,1);g.plane(5,moving=False,up=False)
 if limit:g.put(P+0x18b0,'<B',1);g.put(P+0x18b4,'<5f',.6,0,.8,1,0)
 if rotation:g.put(P+0x72c,'<2f',.002,.7);g.put(P+0x734,'<4f',0,1,0,1)
 g.run(tail()*3,f'critical/common/camera/{state}/{shape}/{limit}/{rotation}')
 assert bytes(oracle.cpu.mem_read(OBJ+0x4c,16))==bytes(oracle.cpu.mem_read(P+0x24,16))
 assert bytes(oracle.cpu.mem_read(CAM+0x7c,16))==bytes(oracle.cpu.mem_read(P+0x48,16))
 records.append({'kind':'collision_pose_camera','state':state,'shape':shape,'limiting_plane':limit,'rotation':rotation,'steps':3,'diagnostics':oracle.word(DLOG)})
for direction,choice,moving in itertools.product([0,0xffffffff],[0,1],[False,True]):
 g=TailGraph();g.put(P+0x18,'<I',4);g.put(P+0x1944,'<I',choice);g.put(CH+0x18,'<f',6 if direction else 2);g.put(CH+0x20,'<f',1);g.put(CH+0x24,'<I',direction)
 g.put(P+0x71c,'<4f',0,0,8,1)
 if not moving:g.put(GATE+0x18,'<I',0)
 else:g.put(PLATFORM+0x4c,'<4f',11,22,33,1)
 g.run(([call(0x481640,CH),call(0x52ad10,P)]+tail())*4,f'animation/common/camera/{direction}/{choice}/{moving}')
 assert bytes(oracle.cpu.mem_read(OBJ+0x4c,16))==bytes(oracle.cpu.mem_read(P+0x24,16))
 assert bytes(oracle.cpu.mem_read(CAM+0x7c,16))==bytes(oracle.cpu.mem_read(P+(0x191c if choice else 0x48),16))
 records.append({'kind':'animation_pose_camera','direction':direction,'stored_target':choice,'moving_contact':moving,'steps':4,'state':oracle.word(P+0x18)})
scope='Connected critical-point collision/common pose/camera updates and advancing animation/pose/camera sequences. The full shared Walk frame still has missing transfer, ground-validation and animation-event helpers; no complete frame or playable level is claimed.'
saved=coverage.copy();coverage.clear();finish('walk-tail',scope,{},extra);coverage.update(saved)
report=json.loads((folder/'walk-tail-original.json').read_text());report['flow_records']=records;report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
(folder/'walk-tail-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n')
(folder/'walk-tail-original.json').write_text(json.dumps(report,indent=2)+'\n');print(report['instruction_coverage']);print('Connected sequences',len(records))
