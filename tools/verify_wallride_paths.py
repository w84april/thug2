"""Compare complete wallride paths with original game instructions."""
from pathlib import Path
source=Path('tools/verify_rail_acquisition.py').read_text().split("\nfor kind in ['grind','point','natas','lip']:")[0]
source=source.replace('rail-acquisition.json','wallride-paths.json').replace('call(0x50dae0,PHYS,[force_no_lip,QUERY])','call(0x50f830,PHYS,[QUERY])')
exec(compile(source,'<rail acquisition and entry graph>','exec'))
report_path=out.parent/'wallride-paths.json'
bind(0x50f830,'thug_skater_update_wallride',0,'void',True,True,True)
ROOTS.add(0x50f830)
wall_instructions=list(md.disasm(pe.get_data(0x10f830,4083),0x50f830));wall_hits=Counter();wall_case_hits=Counter()
def wall_trace(cpu,at,size,user):wall_hits[at]+=1;wall_case_hits[at]+=1
oracle.cpu.hook_add(UC_HOOK_CODE,wall_trace,begin=0x50f830,end=0x510822)
for at in [0x50f830]+[i.address for i in wall_instructions if i.mnemonic=='ret']:
 oracle.cpu.hook_add(UC_HOOK_CODE,floor_observe,begin=at,end=at)
oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=0x50f830,end=0x50f830)
# The landing branch copies the owning body's orientation through this actual
# component lookup. Its other methods are not called by this parent.
WCOMP=0x167b000;copy(WCOMP,bytes(0x40));put(WCOMP+4,'<I',0xbf518e27);put(WCOMP+12,'<I',BODIES);put(GAP+16,'<I',WCOMP)
initial=bytes(memory);oracle.initial=initial
acquisition_config=config_entry
def config_entry(trigger=False):
 b=acquisition_config(trigger)
 for key,value in {0x0c617caf:-300.,0x64a48a64:0.02,0x20102726:4.,0x438ba168:-12.,0x349d02d4:60.,0x5a9de35a:100.,0x542cf0c7:36.}.items():b.symbol(key,2,bits(value))
 return b
def wallride(extra=(),label='wallride'):
 wall_case_hits.clear()
 matrix=[0.,1,0,0,0,0,1,0,1,0,0,0,0,0,0,1]
 p=[patch(SKATER_STATE+0x18,'<I',2),patch(PHYS+0x8c,'<f',1/60),patch(PHYS+0x38c,'<4f',0,0,1,0),patch(BODIES+0x6c,'<16f',*matrix),patch(PHYS+0x18,'<16f',*matrix),patch(BODIES+0xac,'<4f',100,0,0,1),patch(INPUT+0x1a0,'<B',0)]
 acquire(extra=p+list(extra),label=label)
 path_results[-1].update({'wallride_hits':[hex(at) for at in sorted(wall_case_hits)]})
for dt in [0.,1/120,1/60,1/30]:
 for release in [0,1]:
  wallride([patch(PHYS+0x8c,'<f',dt),patch(INPUT+0x1c0,'<B',release)],label='free-space exit, frame duration and release')
for contact in ['none','live','dead']:
 p=[patch(GROUND_GATE+0x18,'<I',0 if contact=='none' else GCONTACT)]
 if contact=='dead':p += [patch(GCONTACT,'<I',0)]
 wallride(p,label='moving contact '+contact)
for i in [0,1,3,13,30,34,39,46,70,129]:
 data=bytes.fromhex(loader['queries'][i]['result']);point=list(struct.unpack_from('<4f',data,16));normal=list(struct.unpack_from('<4f',data,0))
 for offset in [-4.,0,4.]:
  position=[point[j]+normal[j]*offset for j in range(3)]+[1]
  p=[patch(BODIES+0x4c,'<4f',*position),patch(BODIES+0x5c,'<4f',*position),patch(PHYS+0x38c,'<4f',*normal)]
  wallride(p,label='original training surface '+str(i)+' offset '+str(offset))
wallride([patch(SKATER_STATE+o,'<B',255) for o in [0x78,0xa8,0x80,0xb0]],label='clear transfer flags and timestamps')
for flagged in [0,1,255]:
 wallride([patch(SKATER_STATE+0x20,'<B',1),patch(SKATER_STATE+0xd8,'<B',flagged),patch(INPUT+0x1c0,'<B',0)],label='released jump input and exit impulse')
rotation=[0.,0,1,0,0,1,0,0,-1,0,0,0,0,0,0,1]
wallride([patch(GROUND_GATE+0x18,'<I',GCONTACT),patch(GOWNER+0x6c,'<16f',*rotation),patch(GOWNER+0x4c,'<4f',0,20000,0,1),patch(GCONTACT+0x4c,'<4f',0,20000,0,1)],label='moving-contact orientation transport')
scope='Complete wallride0050f830 through real movement, training collision, orientation, state, events, scripts, rail acquisition and moving-contact callees. Initialized game components and successful allocation; all fixture bytes compare exactly. Full game integration remains unfinished.'
fixture={'base':BASE,'memory':'wallride-paths-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'native_qb_callbacks','pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'native_callbacks':[{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]}
(folder/'wallride-paths-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')));(folder/fixture['memory']).write_bytes(initial)
coverage={'total':len(wall_instructions),'covered':sum(bool(wall_hits[i.address]) for i in wall_instructions),'missing':[hex(i.address) for i in wall_instructions if not wall_hits[i.address]]}
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(path_results),'counts':dict(oracle.counts),'instruction_coverage':coverage,'callee_coverage':dict(oracle.coverage),'paths':path_results,'scope':scope}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('Original wallride',len(path_results),coverage['covered'],'/',coverage['total'],flush=True)

subprocess.run(['node',str(ROOT/'tools/verify_wallride_paths_wasm.mjs')],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [folder/'wallride-paths-fixtures.json',folder/fixture['memory']]}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS wallride-paths',len(path_results),sum(oracle.counts.values()))
