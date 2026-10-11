"""Extract concrete frame outcomes from the original execution snapshots."""
import ast,json,struct
from pathlib import Path
p=Path('local/analysis');read=lambda name:json.loads((p/name).read_text())
f=read('skater-ground-fixtures.json');r=read('skater-ground-original.json');base=f['base'];initial=(p/f['memory']).read_bytes()
source=ast.parse((p/'probe-skater-ground.py').read_text());specs=next(ast.literal_eval(n.value) for n in source.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='specs' for t in n.targets))
routines={hex(a):{'bytes':size,'instructions':r['instruction_coverage'][hex(a)]['total'],'name':'thug_'+name+'_draft'} for a,size,name,*_ in specs}
(p/'skater-ground-routines.json').write_text(json.dumps(routines,indent=2)+'\n')
records=[]
for label,case in zip(f['case_labels'],f['cases']):
 if not label.startswith('original owner virtual frame/'):continue
 image=bytearray(initial)
 for at,data in case['patches']:image[at-base:at-base+len(data)//2]=bytes.fromhex(data)
 def words(at,count):return list(struct.unpack_from('<'+'I'*count,image,at-base))
 def floats(at,count):return list(struct.unpack_from('<'+'f'*count,image,at-base))
 owner=base+0x10000;physics=base+0xc2000;state=base+0xc4000;rows=[]
 before=floats(owner+0x4c,4)
 for step in case['steps']:
  assert step['fn']=='0x45d920'
  for at,data in step['outputs']:image[at-base:at-base+len(data)//2]=bytes.fromhex(data)
  rows.append({'position':floats(owner+0x4c,4),'previous_position':floats(owner+0x5c,4),'physics_saved_position':floats(physics+0x98,4),'state':words(state+0x18,1)[0],'moving_escape_diagnostics':words(base+0xce100,1)[0]})
 records.append({'label':label,'position_before':before,'frames':rows})
evidence={'cases':r['cases'],'calls':r['calls'],'exports_used':len(f['functions']),'new_routines':len(routines),
 'new_instructions_exercised':sum(x['covered'] for x in r['instruction_coverage'].values()),'new_instructions_total':sum(x['total'] for x in r['instruction_coverage'].values()),
 'unexercised':{a:x['missing'] for a,x in r['instruction_coverage'].items() if x['missing']},'exclusions':{},
 'owner_virtual_frames':records,'original_collision_queries':r['callees']['0x4172f0'],'original_event_emissions':r['callees']['0x4609f0'],
 'scope':'Full frame on synthetic initialized graphs, using original collision and event callees. These are not playable training-level frames.'}
assert len(records)==8 and all(len(row['frames'])==3 for row in records)
(p/'skater-ground-evidence.json').write_text(json.dumps(evidence,indent=2)+'\n');print(json.dumps({k:v for k,v in evidence.items() if k!='owner_virtual_frames'}))
