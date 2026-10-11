"""Original 0050dae0 with real rail search, entry and moving-contact callees."""
from pathlib import Path
prefix=Path('tools/verify_rail_entry_paths.py').read_text().split("for kind in ['point','natas','lip','grind']:enter(kind)")[0]
prefix=prefix.replace('rail-entry-paths.json','rail-acquisition.json')
prefix=prefix.replace('call(0x50a770,PHYS,[POINT,RAILS,WORLD,force_no_lip,walking,QUERY])','call(0x50dae0,PHYS,[force_no_lip,QUERY])')
exec(compile(prefix,'<complete rail entry graph>','exec'))
folder=out;report_path=out.parent/'rail-acquisition.json'
TYPE_MANAGER,TRANS_COMPONENT,TRANSFORM,TRANS_COMPONENT2,TRANSFORM2=0x1678000,0x1679000,0x1679100,0x1679200,0x1679300
MOVING_RAILS,ORIENT=0x167a000,0x16d1400
copy(TYPE_MANAGER,bytes(0x4000));copy(ORIENT,bytes(0x80))
put(ORIENT+0x40,'<I',0xd443a2bc)
put(GAME+0x24,'<I',WORLD);put(GROUND_GATE+12,'<I',BODIES)
put(TYPE_MANAGER+0x44,'<3I',1,0x1cdfb2a3,0)
glob('thug_component_type_registry',0x6f0fb8,TYPE_MANAGER)
glob('thug_skater_orientation_context',0x7ce5d8,ORIENT)
for i in range(128):glob('thug_component_type_heads',0x6f0db8+i*4,0,offset=i*4)
for c,t in [(TRANS_COMPONENT,TRANSFORM),(TRANS_COMPONENT2,TRANSFORM2)]:
 put(c,'<7I',0x64637c,0x1cdfb2a3,0,GOWNER,0,0,t)
 put(t,'<16f',*identity);put(t+0x40,'<I',MOVING_RAILS);put(t+0x48,'<I',3)
 fields.add(c)
exports += [[0x64637c,'thug_attachment_provider_methods']]
bind(0x50dae0,'thug_skater_acquire_rail',1,'void',True,True,True)
ROOTS.add(0x50dae0)
acq_instructions=list(md.disasm(pe.get_data(0x10dae0,770),0x50dae0));acq_hits=Counter();acq_case_hits=Counter()
def acquisition_trace(cpu,at,size,user):acq_hits[at]+=1;acq_case_hits[at]+=1
oracle.cpu.hook_add(UC_HOOK_CODE,acquisition_trace,begin=0x50dae0,end=0x50dde1)
for at in [0x50dae0]+[i.address for i in acq_instructions if i.mnemonic=='ret']:
 oracle.cpu.hook_add(UC_HOOK_CODE,floor_observe,begin=at,end=at)
for at in [0x50dae0,0x57e2d0,0x45f2d0,0x5480f0,0x42ba10,0x405600,0x427c70,0x500020,0x43eb80,0x427dd0,0x4fc4a0]:
 oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
initial=bytes(memory);oracle.initial=initial
original_config=config_entry;overrides={}
def config_entry(trigger=False):
 b=original_config(trigger)
 for name,kind,value in [(0xf840753e,2,bits(12)),(0x96dca7dc,1,0),(0x76c1da15,2,bits(45)),(0x19fb78fa,1,0)]:b.symbol(name,kind,value)
 for name,(kind,value) in overrides.items():b.symbol(name,kind,value)
 return b
def acquire(kind='grind',force=0,moving=False,extra=(),changes=None,trigger=False,label='rail acquisition'):
 acq_case_hits.clear();z=0 if kind in ['point','natas'] else 50
 p=[patch(SKATER_STATE+0x18,'<I',1),patch(SKATER_STATE+0x70,'<B',0),patch(PHYS+0x3a4,'<B',0),patch(INPUT+0x1a0,'<B',1),patch(PHYS+0x4e0,'<I',0),patch(GROUND_GATE+0x18,'<I',0),patch(BODIES+0x5c,'<4f',-20,20000,z,1),patch(BODIES+0x4c,'<4f',20,20000,z,1)]
 for i in range(3):
  p += [patch(RAILS+i*0x54,'<8f',0,20000,i*100,1,0,20000,(i+1)*100,1)]
 if moving:
  p += [patch(WORLD+0x48,'<I',0),patch(GOWNER+0x4c,'<4f',0,20000,0,1),patch(GOWNER+0x6c,'<16f',*identity),patch(GOWNER+0xac,'<4f',2,3,4,0)]
  for i in range(3):
   next_=MOVING_RAILS+(i+1)*0x54 if i<2 and kind not in ['point','natas'] else 0
   previous=MOVING_RAILS+(i-1)*0x54 if i and kind not in ['point','natas'] else 0
   p += [patch(MOVING_RAILS+i*0x54,'<12f',0,0,i*100,1,0,0,(i+1)*100,1,0,0,i*100,1),patch(MOVING_RAILS+i*0x54+0x40,'<5I',next_,previous,4,0x1800+i,0)]
 changes={**({0x6f0db8:TRANS_COMPONENT} if moving else {}),**(changes or {})}
 enter(kind,force_no_lip=force,extra=p+list(extra),changes=changes,trigger=trigger)
 path_results[-1].update({'label':label,'acquisition_hits':[hex(at) for at in sorted(acq_case_hits)],'moving':moving})
for kind in ['grind','point','natas','lip']:
 for moving in [False,True]:acquire(kind,moving=moving)
for mode,force in itertools.product([0,1,2,3,4,5],[0,1,255,256,257]):
 acquire(force=force,extra=[patch(SKATER_STATE+0x18,'<I',mode)],label='mode and force low byte')
for address in [SKATER_STATE+0x70,PHYS+0x3a4,INPUT+0x1a0]:
 for value in [0,1,255]:acquire(extra=[patch(address,'<B',value)],label='resistance rotation and input gates')
for delay in [0,1,1000,0x7fffffff,0x80000000,0xffffffff]:
 overrides={0x96dca7dc:(1,delay)}
 for timestamp in [0,1000,0xffffffff]:acquire(extra=[patch(PHYS+0x4e0,'<I',timestamp)],label='unsigned cooldown and wrap')
overrides={}
for moving in [False,True]:
 for angle in [0.,30.,90.,180.]:
  overrides={0x76c1da15:(2,bits(angle))}
  acquire(moving=moving,extra=[patch(ORIENT+0x40,'<I',0),patch(PHYS+0x234,'<I',0),patch(PHYS+0x23c,'<I',0xffffffff)],label='retry alignment cosine')
overrides={}
acquire(extra=[patch(WORLD+0x48,'<I',0)],label='no fixed rails and no moving component')
acquire(moving=True,extra=[patch(TRANSFORM+0x48,'<I',0)],label='moving search miss')
acquire(moving=True,extra=[patch(TRANSFORM+0x48,'<I',0),patch(TRANS_COMPONENT+0x14,'<I',TRANS_COMPONENT2)],label='second typed-list component selected')
for moving in [False,True]:
 for contact in [GCONTACT,0]:
  acquire(moving=moving,trigger=True,extra=[patch(GROUND_GATE+0x18,'<I',contact)],label='real trigger and contact replacement')
 for reject in [0,1]:
  selected=MOVING_RAILS if moving else RAILS
  acquire(moving=moving,extra=[patch(PHYS+0x22c,'<I',selected),patch(PHYS+0x230,'<I',TRANSFORM if moving else WORLD),patch(SKATER_STATE+0x50,'<B',0),patch(PHYS+0x23c,'<I',0xffffffff if reject else 0)],label='selected rail eligibility and first-match return')
# Moving rails must also work away from an identity owner frame. The parent
# forces both captured input W lanes to one before applying the inverse.
for angle,scale in itertools.product([0.3,1.1,-0.7,2.4],[0.5,1.,2.,3.]):
 c=math.cos(angle);s=math.sin(angle);matrix=[c*scale,0,-s*scale,0,0,1,0,0,s*scale,0,c*scale,0,0,0,0,1]
 def world_point(x,z,w):return [c*scale*x+s*scale*z+123,20000,-s*scale*x+c*scale*z-456,w]
 extra=[patch(GOWNER+0x4c,'<4f',123,20000,-456,1),patch(GOWNER+0x6c,'<16f',*matrix),patch(BODIES+0x5c,'<4f',*world_point(-20,50,0)),patch(BODIES+0x4c,'<4f',*world_point(20,50,-2))]
 acquire(moving=True,extra=extra,label='translated rotated scaled rail and input W replacement')
 assert path_results[-1]['state']==4,path_results[-1]
scope='Complete rail acquisition0050dae0 through real fixed/moving rail search, eligibility, entry, virtual getters, transforms and contact updates. All232parentinstructions covered. Full game integration remains unfinished.'
fixture={'base':BASE,'memory':'rail-acquisition-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'native_qb_callbacks','pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'native_callbacks':[{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]}
(folder/'rail-acquisition-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')));(folder/fixture['memory']).write_bytes(initial)
coverage={'total':len(acq_instructions),'covered':sum(bool(acq_hits[i.address]) for i in acq_instructions),'missing':[hex(i.address) for i in acq_instructions if not acq_hits[i.address]]}
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(path_results),'counts':dict(oracle.counts),'instruction_coverage':coverage,'callee_coverage':dict(oracle.coverage),'paths':path_results,'scope':scope}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('Original rail acquisition',len(path_results),coverage,flush=True)

subprocess.run(['node',str(ROOT/'tools/verify_rail_acquisition_wasm.mjs')],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [folder/'rail-acquisition-fixtures.json',folder/fixture['memory']]}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS rail-acquisition',len(path_results),sum(oracle.counts.values()))
