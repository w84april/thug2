"""Derive final training metadata from the recorded original memory snapshots."""
import json,struct
from pathlib import Path
p=Path('local/analysis');f=json.loads((p/'rigidbody-initialize-training-fixtures.json').read_text())
base=f['base'];memory=bytearray((p/f['memory']).read_bytes());steps=f['cases'][0]['steps']
for step in steps:
 for at,data in step['outputs']:
  raw=bytes.fromhex(data);assert base<=at and at+len(raw)<=base+len(memory)
  memory[at-base:at-base+len(raw)]=raw
def word(at):return struct.unpack_from('<I',memory,at-base)[0]
def half(at):return struct.unpack_from('<H',memory,at-base)[0]
def floats(at,n):return list(struct.unpack_from('<'+'f'*n,memory,at-base))
report_path=p/'rigidbody-initialize-training-original.json';report=json.loads(report_path.read_text())
report['unavailable_bouncing_objects']=[]
meshctl=base+0xf2300;report['buffer_calls']=[word(meshctl+o) for o in [12,16,20]];report['crt_calls']=word(meshctl+8)
assert len(steps)==43 and len(report['objects'])==31
rigids=[]
for obj in report['objects']:
 assert word(obj['object']+0x104)==obj['flags']==0x60
 components=obj['components'];assert len(components)==(4 if obj['alternate'] else 8)
 for component in components:
  if component['type']!=0xffb39248:continue
  at=component['address'];assert word(at)==0x6463f8 and word(at+12)==obj['object']
  state={'component':at,'name':obj['text'],'mode':word(at+0x10c),'points':half(at+0x8c),'spheres':half(at+0x94),'contacts':half(at+0x9c),'flags':word(at+0xf4),'position':floats(at+0x110,4),'quaternion':floats(at+0x130,4),'bound_radius':floats(at+0x198,1)[0],'sound_component':word(at+0x19c),'sound_profiles':[word(at+0xd8),word(at+0xdc)]}
  assert state['sound_component'] in [c['address'] for c in components if c['type']==0x07713c7b]
  rigids.append(state)
assert len(rigids)==19
report.update({'rigidbodies':rigids,'bouncing_objects':19,'ordinary_objects':12,'components':sum(len(o['components']) for o in report['objects']),'visible_geometry_clones':sum(len(o['parts']) for o in report['objects']),'owned_scripts':sum(bool(o['script']) for o in report['objects']),'metadata_source':'Recorded final original fixture memory, decoded by inspect-rigidbody-initialize-training.py; comparison ports are not production GPU resources.'})
report_path.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['completed_calls','completed_objects','components','bouncing_objects','visible_geometry_clones','owned_scripts','buffer_calls','crt_calls','heap_events','heap_end']}))
