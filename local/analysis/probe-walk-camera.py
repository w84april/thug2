"""Original Walk camera-facing selection and sequential override setter."""
from pathlib import Path
source=Path('local/analysis/probe-walk-common.py').read_text().split('for state,offset,rate')[0]
exec(compile(source,'<preserved common Walk graph>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x525f70,53,'thug_walk_camera_facing_draft',2,'void',False,False,True),
 (0x529f80,498,'thug_walk_update_camera_draft',0,'void',False,False,True)]
for row in specs:
 bind_new(*row);oracle.cpu.hook_add(UC_HOOK_CODE,observe_cache,begin=row[0],end=row[0])
functions[hex(0x525f70)]['float_args']=[1]
for row in [(0x481640,'thug_animation_update_time',0,'void',False,False),(0x52ad10,'thug_walk_transition_frame_draft',0,'void',True,False),(0x529ce0,'thug_walk_write_owner_draft',0,'void',False,False)]:bind(*row)

CAM=P+0x18000;VECTOR=CAM+0x100;fields.add(P+0x1760)
class CameraGraph(CommonGraph):
 def __init__(self):
  super().__init__();self.image[CAM-BASE:CAM-BASE+0x140]=bytes(0x140);self.put(P+0x1760,'<I',CAM)
  self.put(VECTOR,'<4f',.6,.25,.8,1);self.put(CAM+0x74,'<8f',1,2,3,4,5,6,7,8)
for alias,duration in itertools.product(['separate','same','flag','before','after'],[-1,0,.05,1]):
 g=CameraGraph();address={'separate':VECTOR,'same':CAM+0x7c,'flag':CAM+0x78,'before':CAM+0x74,'after':CAM+0x80}[alias]
 g.run([call(0x525f70,CAM,[address,bits(duration)])]*2,f'camera setter/{alias}/{duration}')
for event,choice,face in itertools.product([0,0x4194ecca,0x2d9815c3,0x279b1f0b,0x4fe6069c,0xaf5abc82,0xc84243da,0xfec9dded,0xffffffff],[0,1],[(0,0,1,1),(.6,.25,.8,-1),(-2,3,4,0),(0,0,0,1)]):
 g=CameraGraph();g.put(P+0x78,'<I',event);g.put(P+0x1944,'<I',choice);g.put(P+0x48,'<4f',*face)
 g.run([call(0x529f80,P)]*2,f'camera event/{event:x}/{choice}/{face}')
flow_records=[]
for direction,choice,moving in itertools.product([0,0xffffffff],[0,1],[False,True]):
 g=CameraGraph();g.put(CH+0x18,'<f',6 if direction else 2);g.put(CH+0x20,'<f',1);g.put(CH+0x24,'<I',direction);g.put(P+0x1944,'<I',choice)
 if not moving:g.put(GATE+0x18,'<I',0)
 else:g.put(PLATFORM+0x4c,'<4f',11,22,33,1)
 g.run([call(0x481640,CH),call(0x52ad10,P),call(0x529ce0,P),call(0x529f80,P)]*4,f'animation/pose/camera/{direction}/{choice}/{moving}')
 assert oracle.word(P+0x78)==0x4fe6069c and bytes(oracle.cpu.mem_read(CAM+0x78,1))==b'\x01'
 source=P+(0x191c if choice else 0x48)
 assert bytes(oracle.cpu.mem_read(CAM+0x7c,16))==bytes(oracle.cpu.mem_read(source,16))
 flow_records.append({'direction':direction,'stored_target':choice,'moving_contact':moving,'frames':4,'camera_matches_selected_facing':True})
scope='Candidates for the complete event-driven Walk camera-facing override and its sequential setter. Full camera update and shared walking frame remain unfinished; not playable.'
saved=coverage.copy();coverage.clear();finish('walk-camera',scope,{},extra);coverage.update(saved)
report=json.loads((folder/'walk-camera-original.json').read_text());report['flow_records']=flow_records;report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
(folder/'walk-camera-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n')
(folder/'walk-camera-original.json').write_text(json.dumps(report,indent=2)+'\n');print(report['instruction_coverage'])
