"""Wake actual training props after the full, verified original startup trace."""
from pathlib import Path
exec(compile(Path('local/analysis/trace-rigidbody-update-training.py').read_text(),'<complete training manager prefix>','exec'))
snapshot=bytes(cpu.mem_read(BASE,SIZE));snapshot_globals=[oracle.global_read(g) for g in globals_]
props=list(dict.fromkeys(row['component'] for row in frame_records[0]['rigidbodies']));assert len(props)==19
patches=[];before=[]
for p in props:
 assert oracle.word(p+0x10c)==0
 before.append({'component':p,'owner':oracle.word(p+12),'position':list(struct.unpack('<4f',cpu.mem_read(p+0x110,16)))})
 patches.append([p+0x10c,'01000000']);oracle.setword(p+0x10c,1)
steps=[];object_entries.clear();rigid_entries.clear();dependencies.clear();records=[]
for frame in range(2):
 count=len(object_entries);r=len(rigid_entries)
 advance(0x45f4a0,OBJECTS);steps[-1]['args']=[0x6f00000,0]
 assert not boundary_hits
 records.append({'frame':frame,'object_updates':len(object_entries)-count,'rigidbody_updates':len(rigid_entries)-r,
  'props':[{'component':p,'mode':oracle.word(p+0x10c),'position':list(struct.unpack('<4f',cpu.mem_read(p+0x110,16))),
   'velocity':list(struct.unpack('<4f',cpu.mem_read(p+0x120,16))),'contact_count':cpu.mem_read(p+0x190,1)[0],
   'active_contacts':cpu.mem_read(p+0x191,1)[0]} for p in props]})
 print('ACTIVE TRAINING MANAGER',frame,records[-1]['object_updates'],'owners',records[-1]['rigidbody_updates'],'Rigidbodies',flush=True)
assert len(steps)==2 and len(object_entries)==64 and len(rigid_entries)==38
assert dependencies['0x42bf00']>=19 and dependencies['0x42c950']>=19
for i in range(oracle.word(CONTEXT+8)):
 for j in [4,5,6,7,9,10]:fields.add(LOG+i*48+j*4)
scope='Snapshot after the recorded67-call original training startup and four manager passes. One explicit test input wakes all19 original Rigidbody props by changing only mode10c from0 to1; original shapes, positions, gravity, scripts, geometry and component links remain. Two complete45f4a0 passes run64 actual object updates and38 Rigidbody calls, including active integration/contact work. Exact arena/globals/heap/file/GPU witness comparison. Snapshot restoration and wake input are fixture setup; no skater/input loop, rendered frame, production platform ports or playable-level claim.'
name='rigidbody-update-active-training'
active_fixture={**fixture,'memory':name+'-memory.bin','cases':[{'patches':patches,'globals':snapshot_globals,'steps':steps}],
 'case_labels':['all19 actual training Rigidbody props wake and update'],'pointer_fields':sorted(fields),'scope':scope}
(folder/active_fixture['memory']).write_bytes(snapshot);(folder/(name+'-fixtures.json')).write_text(json.dumps(active_fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':1,'calls':2,'completed_calls':2,'interrupted_calls':0,
 'snapshot_prefix_calls':67,'full_manager_updates':2,'object_updates':64,'rigidbody_updates':38,
 'wake_input':patches,'initial_props':before,'frames':records,'dependency_calls':dict(dependencies),'scope':scope,'playable':False}
(folder/(name+'-original.json')).write_text(json.dumps(report,indent=2)+'\n');print('SAVED two active training manager passes',flush=True)
