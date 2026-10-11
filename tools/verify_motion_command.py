import subprocess
"""Complete original Motion move command, node arrival and attached spawn."""
from pathlib import Path
prefix=Path('tools/verify_pending_trick.py').read_text().split('for mode,mask in ')[0]
prefix=prefix.replace('pending-trick.json','motion-command.json')
exec(compile(prefix,'<actual object script and network graph>','exec'))
folder=ROOT/'local/validation/collision';report_path=folder.parent/'motion-command.json'
for row in [(0x461410,'thug_object_spawn_attached_script',4,'word',True,True,True),
 (0x424020,'thug_motion_arrive_at_node',1,'void',True,True,True),
 (0x4269f0,'thug_motion_move_to_position',7,'byte',False,False,True),
 (0x426c10,'thug_motion_move_to_node',2,'void',True,True,True),
 (0x4274d0,'thug_motion_command',3,'word',True,True,True),
 (0x475920,'thug_script_update_spawned',0,'void',True,True,False),
 (0x4750b0,'thug_script_execute',0,'word',True,True,True)]:bind(*row)
functions['0x4269f0']['float_args']=[2,3,4,5]
MOTION=0x16d4000;copy(MOTION,b'\xa7'*0x300);put(MOTION+12,'<I',BODIES)
initial=bytes(memory);oracle.initial=initial
ranges={0x461410:97,0x424020:181,0x4269f0:538,0x426c10:152,0x4274d0:41};motion_hits=Counter()
def motion_trace(cpu,at,size,user):motion_hits[at]+=1
for at,n in ranges.items():
 oracle.cpu.hook_add(UC_HOOK_CODE,motion_trace,begin=at,end=at+n-1)
 oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
labels=[];oracle.cases.clear();oracle.counts.clear();oracle.coverage.clear()
NODE_NAME=0x71449955;SCRIPT_NAME=0x71664441;SECOND_SCRIPT=0x71664442
def config(properties=(),node_properties=(),script_kind='none',argument=True,name=NODE_NAME):
 b=Build();vector=b.alloc(struct.pack('<I3f',0,100,200,300));angles=b.alloc(struct.pack('<I3f',0,.125,-.5,.75))
 entries=[(0xa1dc81f9,13,name),(0x7f261953,6,vector),(0x9d2d0915,6,angles)]+list(node_properties)
 params=b.structure([(0x12345678,1,0xabcdef12),(0x23456789,3,b.text(b'motion node parameters'))])
 if argument:entries.append((0x7031f10c,10,params))
 if script_kind in ['spawn','both']:entries.append((0x3aefe377,13,SCRIPT_NAME));program(b,SCRIPT_NAME)
 if script_kind in ['replace','both']:entries.append((0x86125749,13,SECOND_SCRIPT));program(b,SECOND_SCRIPT)
 node=b.structure(entries);array=b.array(10,[node])
 b.extra += [patch(NODE_TABLE+(name&0x3fff)*4,'<Hh',0,0),patch(NODE_TABLE+0x1000c,'<I',array)]
 request=b.structure([(0xa1dc81f9,13,name)]+list(properties))
 return b,request,params,node
def execute(calls,b,p=(),changes=None,label='motion command',existing=False):
 before,body=setup(existing,0xbaf9b341)
 patches=b.patches()+body+[patch(BODIES+0x4c,'<4f',4,5,6,1)]+list(p)
 return compare(before+calls,patches,changes,label)
for properties in [[],[(0x906b67ba,2,bits(2))],[(0xf0d90109,2,bits(20))],[(0xf0d90109,2,bits(20)),(0x85894a84,2,bits(3))],[(0,13,0x90a91232)]]:
 for fn in [0x426c10,0x4274d0]:
  b,request,_,_=config(properties)
  args=[request,0] if fn==0x426c10 else [0x8819dd8b,request,0]
  execute([call(fn,MOTION,args)]*2,b,label='complete move-to-node direct and handler paths')
for command in [0,1,0xffffffff,0x315d9ed4]:
 b,request,_,_=config();execute([call(0x4274d0,MOTION,[command,request,0])],b,label='unhandled commands')
for name in [None,0]:
 b=Build();request=b.structure([] if name is None else [(0xa1dc81f9,13,name)])
 for fn in [0x426c10,0x4274d0]:execute([call(fn,MOTION,[request,0] if fn==0x426c10 else [0x8819dd8b,request,0])],b,label='missing or zero Name is no-op')
# Direct by-value position entry covers every timing/units/acceleration branch.
for time in [-10.,0.,.001,.5,1.,10.,1e30]:
 b,request,_,_=config([(0x906b67ba,2,bits(time)),(0xf0d90109,2,bits(99)),(0x85894a84,2,bits(4))])
 execute([call(0x4269f0,MOTION,[request,0,*map(bits,[100.,200.,300.,2.]),NODE_NAME])]*2,b,label='Time takes precedence over Speed')
unit_sets=[[],[0x2ce7ee02],[0xaad7c80f],[0xa18b8f32],[0x2ce7ee02,0xaad7c80f,0xa18b8f32],[0xaad7c80f,0xa18b8f32]]
for units,speed,acceleration in itertools.product(unit_sets,[-20.,0.,.125,20.,1e30],[None,-2.,0.,3.]):
 properties=[(0xf0d90109,2,bits(speed))]+[(0,13,u) for u in units]
 if acceleration is not None:properties.append((0x85894a84,2,bits(acceleration)))
 b,request,_,_=config(properties)
 execute([call(0x4269f0,MOTION,[request,0,*map(bits,[100.,200.,300.,1.]),NODE_NAME])],b,label='speed units, precedence, acceleration and wide intermediate')
for point,name,orient in itertools.product([[0.,0.,0.,1.],[4.,5.,6.,0.],[1e30,-1e30,1e30,2.]],[0,NODE_NAME],[False,True]):
 b,request,_,_=config([(0,13,0x90a91232)] if orient else [])
 execute([call(0x4269f0,MOTION,[request,0,*map(bits,point),name])]*2,b,label='immediate move and optional orientation')
for kind,existing,argument in itertools.product(['none','spawn','replace','both'],[False,True],[False,True]):
 b,request,_,_=config(script_kind=kind,argument=argument)
 for fn in [0x424020,0x4274d0]:
  args=[NODE_NAME] if fn==0x424020 else [0x8819dd8b,request,0]
  execute([call(fn,MOTION,args)]*2,b,label='node arrival script priority and repeated actual setup',existing=existing)
# Deferred spawning does not execute until the real spawned-script scheduler.
for owner,user_value,active in itertools.product([0,BODIES],[0,1,0x80000000,0xffffffff],[0,1,2,255]):
 b,_,params,_=config(script_kind='spawn')
 execute([call(0x461410,owner,[SCRIPT_NAME,params,user_value,active])],b,label='attached spawn owner, user value and flag bit')
for owner in [0,BODIES]:
 b,_,params,_=config(script_kind='spawn')
 stages=execute([call(0x461410,owner,[SCRIPT_NAME,params,0,0]),call(0x475920,0)],b,label='actual deferred script execution and cleanup')
 assert stages[-2]['callbacks']==0 and stages[-1]['callbacks']==1
# Existing object scripts are configured now, and execute through the interpreter
# only on the explicit subsequent step. Spawn takes priority when both exist.
b,request,_,_=config(script_kind='replace')
stages=execute([call(0x4274d0,MOTION,[0x8819dd8b,request,0]),call(0x4750b0,SCRIPTS)],b,label='actual replacement script executes after movement',existing=True)
assert stages[-2]['callbacks']==0 and stages[-1]['callbacks']==1
coverage={};pe=load();md=Cs(CS_ARCH_X86,CS_MODE_32)
for at,n in ranges.items():
 rows=list(md.disasm(pe.get_data(at-0x400000,n),at));missing=[hex(i.address) for i in rows if not motion_hits[i.address]]
 coverage[hex(at)]={'total':len(rows),'covered':len(rows)-len(missing),'missing':missing}
scope='Complete461410 attached deferred spawn,424020 node arrival,4269f0 position movement,426c10 move-to-node and4274d0 Motion command. Actual node lookup, vector/orientation math, QB parameters, heap/reference lifetime, script setup and spawned execution; finite numeric corpus, signedzero and wide intermediates. Integrated into the main module; timed-motion frame updates and playable level remain unfinished.'
fixture={'base':BASE,'memory':'motion-command-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'native_qb_callbacks','pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'native_callbacks':[{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]}
(folder/'motion-command-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')));(folder/fixture['memory']).write_bytes(initial)
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'counts':dict(oracle.counts),'instruction_coverage':coverage,'callee_coverage':dict(oracle.coverage),'scope':scope}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('Original Motion command',len(labels),sum(oracle.counts.values()),coverage,flush=True)

subprocess.run(['node',str(ROOT/'tools/verify_motion_command_wasm.mjs')],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [folder/'motion-command-fixtures.json',folder/fixture['memory']]}
(folder.parent/'motion-command.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS motion-command',report['cases'],sum(oracle.counts.values()))
