import subprocess
"""Original physics command with real Motion, shadow, reset and camera walk."""
from pathlib import Path
prefix=Path('tools/verify_motion_command.py').read_text().split('for properties in [')[0]
prefix=prefix.replace('motion-command.json','physics-command.json')
exec(compile(prefix,'<actual Motion and script graph>','exec'))
folder=ROOT/'local/validation/collision';report_path=folder.parent/'physics-command.json'
bind(0x501600,'thug_skater_physics_command',3,'word',True,True,True)
bind(0x474540,'thug_script_setup',4,'void',True,True,True)
for row in [(0x4317c0,'thug_shadow_set_position',1,'void',False,False,True),
 (0x4317e0,'thug_shadow_set_up',1,'void',False,False,True),
 (0x580880,'thug_skater_camera_object',0,'word',False,False,True),
 (0x511420,'thug_skater_sync_flip',0,'void',True,True,True),
 (0x45d920,'thug_object_update_components',0,'void',True,True,True),
 (0x45e4c0,'thug_object_mark_moved',1,'void',True,True,True)]:bind(*row)
SHADOW,CTABLE,MTABLE,CAMERA,CMANAGER,CPRIMARY,CSECONDARY,CBUCKETS,CBUCKETS2=0x16d4400,0x16d4800,0x16d4900,0x16d5000,0x16d6000,0x16d6100,0x16d6140,0x16d6180,0x16d61c0
copy(SHADOW,bytes(0x2000));put(CTABLE+4,'<I',0x5480a0);put(CTABLE+0x24,'<I',0x5480a0);put(CTABLE+0x28,'<I',0x5480a0)
put(MTABLE+0x24,'<I',0x5480a0);put(MTABLE+0x30,'<I',0x4274d0)
fields.update([CTABLE+4,CTABLE+0x24,CTABLE+0x28,MTABLE+0x24,MTABLE+0x30])
function_exports += [[0x5480a0,'thug_component_empty_frame_bridge'],[0x4274d0,'thug_motion_command_bridge']]
chain=[];node=struct.unpack_from('<I',memory,BODIES+0x100-BASE)[0]
while node:
 assert node not in chain;chain.append(node);put(node,'<I',CTABLE);node=struct.unpack_from('<I',memory,node+0x10-BASE)[0]
put(chain[-1]+0x10,'<I',MOTION)
put(MOTION,'<5I',MTABLE,0x0a015e17,0,BODIES,SHADOW)
put(SHADOW,'<5I',CTABLE,0x8a897dd2,0,BODIES,0)
put(CAMERA,'<I',CTABLE);put(CAMERA+0x104,'<I',0);put(CAMERA+0x58,'<I',0x80000000)
put(CMANAGER+8,'<2I',CPRIMARY,CSECONDARY);put(CPRIMARY,'<2I',0,CBUCKETS);put(CSECONDARY,'<2I',0,CBUCKETS2)
put(CBUCKETS,'<3I',0x967c138c,CAMERA,0)
glob('thug_component_type_registry',0x6f0fb8,CMANAGER)
initial=bytes(memory);oracle.initial=initial
ranges={0x501600:590};physics_hits=Counter()
def physics_trace(cpu,at,size,user):physics_hits[at]+=1
oracle.cpu.hook_add(UC_HOOK_CODE,physics_trace,begin=0x501600,end=0x50184d)
for at in [0x501600,0x4317c0,0x4317e0,0x580880,0x511420,0x45d920,0x45e4c0]:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
labels=[];oracle.cases.clear();oracle.counts.clear();oracle.coverage.clear()
def run(properties=(),p=(),kind='none',existing=False,label='physics move command',command=0x8819dd8b,repeat=2,camera='disabled',slot=0,net=None,name=NODE_NAME):
 b,request,_,_=config(properties,script_kind=kind,name=name)
 before,body=setup(existing,0xbaf9b341)
 flags=[patch(BODIES+0xbc,'<B',int(camera!='disabled')),patch(CBUCKETS,'<3I',0xe17b231a if slot==1 else 0x967c138c,CAMERA if camera=='present' else 0,0)]
 patches=b.patches()+body+network(slot=slot,**(net or {}))+[patch(BODIES+0x4c,'<4f',4,5,6,1),patch(BODIES+0xac,'<4f',3,9,4,1),patch(PHYS+0x1c5,'<B',255)]+flags+list(p)
 stages=compare(before+[call(0x501600,PHYS,[command,request,0,QUERY])]*repeat,patches,{index[0x6f0fc0]:CMANAGER},label)
 if len(labels)%25==0:print('Physics command cases',len(labels),flush=True)
 return stages
for value in [0,1,2,255]:run(command=0x315d9ed4,p=[patch(PHYS+0x248,'<B',value)],label='ledge flag boolean query')
for value in [0,1,0xffffffff,0x8819dd8a]:run(command=value,label='unrecognized command returns two')
for camera,slot in itertools.product(['disabled','missing','present'],[0,1]):
 run(camera=camera,slot=slot,label='camera enable and both camera names')
for state,selector,old in itertools.product(range(6),[0,1,255],[0,1,255]):
 run(p=[patch(SKATER_STATE+0x18,'<I',state),patch(BODIES+0x110,'<B',selector),patch(SKATER_STATE+0x28,'<B',old)],label='reset state, flip equality and live timestamp')
for properties in [[],[(0,13,0x90a91232)],[(0x906b67ba,2,bits(2))],[(0xf0d90109,2,bits(20)),(0x85894a84,2,bits(3))]]:
 for keep in [False,True]:
  run(properties+([(0,13,0xd607e2e6)] if keep else []),label='immediate or scheduled move, reset and orientation flags')
for velocity in [[0.,0.,0.,1.],[3.,9.,4.,2.],[-3.,-9.,-4.,-0.],[1e30,7.,-1e30,1.],[1e-30,-0.,-1e-30,0.]]:
 run([(0,13,0xd607e2e6),(0,13,0x90a91232)],p=[patch(BODIES+0xac,'<4f',*velocity)],label='NoReset Orient preserves vertical raw bits and horizontal magnitude')
for kind,existing in itertools.product(['spawn','replace','both'],[False,True]):
 run(kind=kind,existing=existing,camera='present',label='Motion arrival performs actual attached script setup')
for player,peer in itertools.product(['local','remote','hidden','missing'],[0,1,8]):
 run(net={'player':player,'peer':peer},label='reset flip synchronizes animation and real network queue')
run(name=0,label='recognized move without Name still performs physics reset')
# Camera traversal can run its own genuine QB script, which mutates live physics
# fields before the parent NoReset/reset decision. No camera behavior is replaced.
for target,value,width in [(BODIES+0xac,bits(15),4),(PHYS+0x1c5,77,1),(BODIES+0x110,255,1),(CAMERA+8,1,4)]:
 b,request,_,_=config([(0,13,0xd607e2e6)],script_kind='none');program(b,SECOND_SCRIPT)
 before,body=setup(False,0xbaf9b341)
 p=b.patches()+body+network()+[patch(BODIES+0xbc,'<B',1),patch(CAMERA+0x10,'<I',SCRIPTS),patch(GOBS+4,'<4I',target,value,width,0)]
 compare(before+[call(0x4738e0,SCRIPTS),call(0x474540,SCRIPTS,[SECOND_SCRIPT,0,0,CAMERA]),call(0x501600,PHYS,[0x8819dd8b,request,0,QUERY])],p,{index[0x6f0fc0]:CMANAGER},'camera QB runs within actual object update')
pe=load();md=Cs(CS_ARCH_X86,CS_MODE_32);rows=list(md.disasm(pe.get_data(0x101600,590),0x501600))
missing=[hex(i.address) for i in rows if not physics_hits[i.address]]
coverage={'total':len(rows),'covered':len(rows)-len(missing),'missing':missing}
scope='Complete501600 physics command through actual4274d0 Motion virtual dispatch, node/position/orientation, attached scripts, shadow vectors, moved notification, camera lookup and real object/script update, state/flip reset and actual animation/network queues. Test component notification slots use the real5480a0 empty method; this is not a recovered full camera/component constructor graph. Finite numeric corpus; zero NaN allowances. Integrated into the main module and the training level is not playable.'
fixture={'base':BASE,'memory':'physics-command-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'native_qb_callbacks','pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'native_callbacks':[{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]}
(folder/'physics-command-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')));(folder/fixture['memory']).write_bytes(initial)
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'counts':dict(oracle.counts),'instruction_coverage':{'0x501600':coverage},'callee_coverage':dict(oracle.coverage),'scope':scope}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('Original physics command',len(labels),sum(oracle.counts.values()),coverage,flush=True)

subprocess.run(['node',str(ROOT/'tools/verify_physics_command_wasm.mjs')],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [folder/'physics-command-fixtures.json',folder/fixture['memory']]}
(folder.parent/'physics-command.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS physics-command',report['cases'],sum(oracle.counts.values()))
