"""Extend the real training startup/fan trace through complete manager updates."""
from pathlib import Path
source=Path('local/analysis/trace-motion-rotation-training.py').read_text().split("scope='Preserved complete31-prop")[0]
NEW_GLOBALS='''
unit=json.loads((folder/'rigidbody-update-fixtures.json').read_text())
existing_addresses={entry[1] for entry in globals_}
for entry in unit['globals']:
 name,at,width,*offset=entry
 if name.startswith(('thug_rigidbody_','thug_collision_')) or name in ['thug_sphere_default_cache_draft','thug_sphere_query_fixture_state']:
  if at not in existing_addresses:
   glob(name,at,int.from_bytes(cpu.mem_read(at,width),'little'),width,offset[0] if offset else 0);existing_addresses.add(at)
functions['0x45f4a0']={'name':'thug_composite_manager_update_draft','this':True,'result':'void','cleanup':0,'stack_args':[],'memory':True,'pointer_args':[0]}
# Host-only identity must be outside the full training arena, which includes
# the smaller geometry fixture's1ff0000 token. No original call receives it.
exports.append([0x6f00000,'thug_sphere_query_fixture_state'])
'''
needle="source=source.replace(needle,addition+'\\n'+needle)"
assert source.count(needle)==1
source=source.replace(needle,"source=source.replace(needle,addition+NEW_GLOBALS+'\\n'+needle)\nsource=source.replace('cpu.hook_add(UC_HOOK_CODE,stop_motion,begin=0x430e20,end=0x430e20)','# Complete original Rigidbody update now runs.')")
exec(compile(source,'<preserved63-call training prefix with full Rigidbody>','exec'))
assert len(steps)==63 and not boundary_hits
object_entries=[];rigid_entries=[];frame_records=[];dependencies=Counter()
def object_entry(cpu,at,size,user):object_entries.append(cpu.reg_read(UC_X86_REG_ECX))
def rigid_entry(cpu,at,size,user):
 p=cpu.reg_read(UC_X86_REG_ECX);rigid_entries.append({'component':p,'owner':oracle.word(p+12),'mode':oracle.word(p+0x10c)})
def dependency(cpu,at,size,user):dependencies[hex(at)]+=1
cpu.hook_add(UC_HOOK_CODE,object_entry,begin=0x45d920,end=0x45d920)
cpu.hook_add(UC_HOOK_CODE,rigid_entry,begin=0x430e20,end=0x430e20)
for at in [0x42c140,0x42bf00,0x42c950,0x430140,0x430be0,0x42cf90,0x42d9d0,0x41df80,0x4270e0]:cpu.hook_add(UC_HOOK_CODE,dependency,begin=at,end=at)
for frame in range(4):
 before_o=len(object_entries);before_r=len(rigid_entries)
 advance(0x45f4a0,OBJECTS);steps[-1]['args']=[0x6f00000,0]
 assert not boundary_hits
 frame_records.append({'frame':frame,'objects':object_entries[before_o:],'rigidbodies':rigid_entries[before_r:]})
 print('COMPLETE TRAINING MANAGER',frame,len(object_entries)-before_o,'owners',len(rigid_entries)-before_r,'Rigidbodies',flush=True)
assert len(steps)==67 and len(object_entries)==128 and len(rigid_entries)==76
assert all(len(f['objects'])==32 and len(f['rigidbodies'])==19 for f in frame_records)
for i in range(oracle.word(CONTEXT+8)):
 for j in [4,5,6,7,9,10]:fields.add(LOG+i*48+j*4)
scope='Preserved63-call original training startup, barrel/fire and actual fan scripts, then four complete original45f4a0 manager passes. Each visits32 actual owners and19 initialized Rigidbody components through their real component tables, with Motion/particle/Sound updates. Full arena/globals/heap/file/GPU witness storage compare. These original Rigidbody props remain idle without skater contact; no skater/input loop, rendered frame, production platform ports or playable-level claim.'
fixture={**BASELINE,'memory_fixture':'particle-image-training-ports.wasm','native_callbacks':[{**c,'module':'particle-image-training-ports.wasm'} for c in BASELINE['native_callbacks']],
 'memory':'rigidbody-update-training-memory.bin','functions':{k:v for k,v in functions.items() if k in {s['fn'] for s in steps}},
 'globals':globals_,'cases':oracle.cases,'case_labels':['actual training scene completes four manager passes'],
 'pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'pointer_globals':pointer_globals,
 'boundary_address':BOUNDARY,'boundary_factory':0x430e20,'component_initializer_boundary':True,'boundary_after_script':True,'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'rigidbody-update-training-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':1,'calls':len(steps),'completed_calls':len(steps),'interrupted_calls':0,
 'preserved_prefix_calls':63,'full_manager_updates':4,'object_updates':len(object_entries),'rigidbody_updates':len(rigid_entries),
 'frames':frame_records,'dependency_calls':dict(dependencies),'scope':scope,'playable':False}
(folder/'rigidbody-update-training-original.json').write_text(json.dumps(report,indent=2)+'\n');print('SAVED67 completecalls: four full manager passes',flush=True)
