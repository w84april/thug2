import subprocess
"""Original shadow vectors, skater camera lookup, and flip synchronization."""
from pathlib import Path
prefix=Path('tools/verify_pending_flip.py').read_text().split('words=[0,0x80000000')[0]
prefix=prefix.replace('pending-flip.json','physics-reset.json')
exec(compile(prefix,'<real animation and network graph>','exec'))
folder=ROOT/'local/validation/collision';report_path=folder.parent/'physics-reset.json'
for row in [(0x4317c0,'thug_shadow_set_position',1,'void',False,False,True),
 (0x4317e0,'thug_shadow_set_up',1,'void',False,False,True),
 (0x580880,'thug_skater_camera_object',0,'word',False,False,True),
 (0x511420,'thug_skater_sync_flip',0,'void',True,True,True)]:bind(*row)
ranges={0x4317c0:30,0x4317e0:30,0x580880:32,0x511420:70};reset_hits=Counter()
def reset_trace(cpu,at,size,user):reset_hits[at]+=1
for at,n in ranges.items():
 oracle.cpu.hook_add(UC_HOOK_CODE,reset_trace,begin=at,end=at+n-1)
 oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
SHADOW,SOURCE,CMANAGER,CPRIMARY,CSECONDARY,CBUCKETS,CBUCKETS2,CNODE=0x16d0000,0x16d0100,0x16d0200,0x16d0280,0x16d02a0,0x16d0300,0x16d0380,0x16d0400
copy(SHADOW,b'\xad'*0x800);put(CMANAGER+8,'<2I',CPRIMARY,CSECONDARY)
put(CPRIMARY,'<2I',0,CBUCKETS);put(CSECONDARY,'<2I',0,CBUCKETS2)
glob('thug_component_type_registry',0x6f0fb8,CMANAGER)
initial=bytes(memory);oracle.initial=initial
labels=[];oracle.cases.clear();oracle.counts.clear();oracle.coverage.clear()
words=[0,0x80000000,0x3f800000,0xbf800000,1,0x80000001,0x7f7fffff,0x7f800000,0xff800000,0x7fa12345,0xffa12345,0x7fc12345]
for fn,off in [(0x4317c0,0x1c),(0x4317e0,0x2c)]:
 for shift in range(len(words)):
  p=[patch(SOURCE,'<4I',*[words[(shift+i)%len(words)] for i in range(4)])]
  compare(fn,SHADOW,[SOURCE],p=p,label='shadow raw lanes',repeat=2)
 for delta in [-12,-8,-4,0,4,8,12]:
  p=[patch(SHADOW,'<24I',*[0x12340000+i for i in range(24)])]
  compare(fn,SHADOW,[SHADOW+off+delta],p=p,label='shadow forward-copy aliases',repeat=2)
for slot,where in itertools.product([0,1,2,0x7fffffff,0xffffffff],['primary','secondary','missing','collision','null-primary']):
 key=0xe17b231a if slot==1 else 0x967c138c
 p=[patch(BODIES+0x2bc,'<I',slot),patch(CBUCKETS,'<3I',0,0,0),patch(CBUCKETS2,'<3I',0,0,0)]
 if where in ['primary','null-primary']:p += [patch(CBUCKETS,'<3I',key,SHADOW if where=='primary' else 0,0)]
 if where in ['secondary','null-primary']:p += [patch(CBUCKETS2,'<3I',key,SOURCE,0)]
 if where=='collision':p += [patch(CBUCKETS,'<3I',key^1,SOURCE,CNODE),patch(CNODE,'<3I',key,SHADOW,0)]
 oracle.case([call(0x580880,BODIES)]*2,p,{index[0x6f0fc0]:CMANAGER,index[0x6f0fb8]:0xdeadbeef})
 labels.append('camera slot primary/secondary lookup ignores passed manager')
for flag,slot,player in itertools.product([0,1,2,255],[0,1],['local','remote','hidden','missing']):
 compare(0x511420,FLIP,p=[patch(SKATER_STATE+0x28,'<B',flag)],net={'slot':slot,'player':player},label='state flip synchronization and queue player gates',repeat=2)
for count in [0,1,2]:
 p=[patch(FSTATES+count*0x100+4,'<I',0xffffffff),patch(SKATER_STATE+0x28,'<B',255)]
 compare(0x511420,FLIP,p=p,label='animation sentinel and full traversal',repeat=2)
coverage={};pe=load();md=Cs(CS_ARCH_X86,CS_MODE_32)
for at,n in ranges.items():
 rows=list(md.disasm(pe.get_data(at-0x400000,n),at));missing=[hex(i.address) for i in rows if not reset_hits[i.address]]
 coverage[hex(at)]={'total':len(rows),'covered':len(rows)-len(missing),'missing':missing}
scope='Complete4317c0/4317e0 shadow word copies,580880 skater camera object lookup and511420 flip resynchronization. Actual object/component lookups, animation-state traversal and network queues; full game integration remains unfinished.'
fixture={'base':BASE,'memory':'physics-reset-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'native_callbacks':[{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]}
(folder/'physics-reset-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')));(folder/fixture['memory']).write_bytes(initial)
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'counts':dict(oracle.counts),'instruction_coverage':coverage,'callee_coverage':dict(oracle.coverage),'scope':scope}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('Original reset helpers',len(labels),coverage,flush=True)

subprocess.run(['node',str(ROOT/'tools/verify_physics_reset_wasm.mjs')],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [folder/'physics-reset-fixtures.json',folder/fixture['memory']]}
(folder.parent/'physics-reset.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS physics-reset',report['cases'],sum(oracle.counts.values()))
