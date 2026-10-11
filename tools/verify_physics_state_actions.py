import hashlib,json,subprocess
"""Timed command effects and complete SetState through original dependencies."""
from pathlib import Path
action_prefix=Path('tools/verify_jump.py').read_text().split('for mode in [0,1,2,3,4,5,6,0xffffffff]:')[0]
action_prefix=action_prefix.replace('call(0x509a40,PHYS,[params,0,QUERY])','call(0x509a80,PHYS,[params,0,QUERY])')
exec(compile(action_prefix,'<complete engine graph for state actions>','exec'))
folder=ROOT/'local/validation/collision'
timed_commands={0x4fc840:('cancel_wallpush',0xb8),0x4fcf90:('no_spin',0x68),0x4fcfc0:('in_bail',0x70),0x4fcff0:('not_in_bail',0x70),0x4fd630:('set_vert_air',0x30)}
for at,(name,_) in timed_commands.items():bind(at,'thug_physics_'+name+'_member',2,'word',False,False,True)
bind(0x4fd040,'thug_physics_set_rail_sound_member',2,'word',False,False,True)
bind(0x509a80,'thug_physics_set_state',2,'word',True,True,True)
exports.append([0x64bbd4,'thug_state_lip_exit_events'])
function_exports.append([0x509a80,'thug_physics_set_state_member'])
ROOTS.add(0x509a80)
state_rows=list(md.disasm(pe.get_data(0x109a80,230),0x509a80))
for at in [0x509a80]+[i.address for i in state_rows if i.mnemonic=='ret']:
 oracle.cpu.hook_add(UC_HOOK_CODE,floor_observe,begin=at,end=at)
action_hits=Counter()
def action_trace(cpu,at,size,user):action_hits[at]+=1
action_ranges={0x4fc840:0x31,0x4fcf90:0x30,0x4fcfc0:0x2b,0x4fcff0:0x2b,0x4fd630:0x2b,0x4fd040:0x89,0x509a80:230}
for at,size in action_ranges.items():oracle.cpu.hook_add(UC_HOOK_CODE,action_trace,begin=at,end=at+size-1)
labels=[];oracle.cases.clear();oracle.counts.clear();oracle.coverage.clear();qb_calls.clear();callback_counts.clear()
for at,(_,offset) in timed_commands.items():
 for flag,clock in itertools.product([0,1,2,127,128,255],[0,1,0x7fffffff,0x80000000,0xffffffff]):
  changes={index[0x696d60]:clock}
  compare([call(at,PHYS,[0xdeadbeef,0x87654321])]*2,
   [patch(SKATER_STATE+offset,'<B',flag),patch(SKATER_STATE+offset+4,'<I',0xabcdef01)],changes,
   label=f'timed {at:x}, byte {flag}, offset {clock:x}, retained repeat')
for flag in [0,1,255]:
 compare([call(0x4fcf90,PHYS,[0,0])]*2,[patch(PHYS+0x1528,'<I',PHYS+0x370-0x68),patch(PHYS+0x370,'<B',flag)],label='NoSpin gate aliases timed flag: preserve write/read order')
for items,flag,clock in itertools.product([[],[(0,13,0x8d10119d)],[(0,13,0x12345678)],[(0,1,0x8d10119d)],[(0,13,0x12345678),(0,13,0x8d10119d)]],[0,1,255],[0,0xffffffff]):
 b=Build();params=b.structure(items)
 compare([call(0x4fd040,PHYS,[params,0xdeadbeef])]*2,b.patches()+[patch(SKATER_STATE+0x58,'<B',flag),patch(SKATER_STATE+0x5c,'<I',0xabcdef01),patch(SOUND+0x1e,'<B',255)],{index[0x696d60]:clock},label=f'rail sound values {items}, old {flag}, clock {clock:x}')

def set_state(mode,target=None,extra=(),trigger=False,repeat=1,properties=None,label='SetState'):
 props=([(0,13,target)] if target is not None else []) if properties is None else properties
 return jump(mode=mode,properties=props,extra=extra,trigger=trigger,repeat=repeat,command=True,label=label)
for mode,target in itertools.product([0,1,2,3,4,5,6,0xffffffff],[None,0,0x439f4704,0x58007c97,0xa549b57b,0x12345678]):
 set_state(mode,target,extra=[patch(PHYS+0x1c5,'<B',255)],repeat=2,label=f'SetState old {mode:x}, target {target}, retained repeat')
for target in [0x439f4704,0x58007c97,0xa549b57b]:
 for props in [[(0,1,target)],[(0,13,0x12345678),(0,13,target)],[(0,13,target),(0,13,0x12345678)]]:
  set_state(2,properties=props,label='anonymous checksum type and last match with wallride repair')
rail_patches=[]
for i in range(3):
 rail_patches += [patch(RAILS+i*0x54+0x20,'<4f',0,20000,i*100,1),patch(RAILS+i*0x54+0x40,'<5I',RAILS+(i+1)*0x54 if i<2 else 0,RAILS+(i-1)*0x54 if i else 0,4,0x1800+i,0)]
for target,trigger,contact in itertools.product([0x439f4704,0x58007c97,0xa549b57b,0x12345678],[False,True],['none','live','dead']):
 extra=rail_patches+[patch(PHYS+0x22c,'<I',RAILS+0x54),patch(PHYS+0x230,'<I',WORLD),patch(GROUND_GATE+0x18,'<I',0 if contact=='none' else GCONTACT)]
 if contact=='dead':extra.append(patch(GCONTACT,'<I',0))
 prior=qb_calls[hex(0xa7662059)]
 set_state(3,target,extra,trigger,label=f'lip exit target {target:x}, event {trigger}, contact {contact}')
 assert (qb_calls[hex(0xa7662059)]>prior)==(trigger and target!=0xa549b57b)
for target,(address,value,width) in itertools.product([0x439f4704,0x58007c97,0x12345678],[(PHYS+0x1528,SKATER_STATE2,4),(SKATER_STATE+0x18,2,4),(PHYS+0x22c,0,4),(GCONTACT,0,4)]):
 prior=qb_calls[hex(0xa7662059)]
 extra=rail_patches+[patch(PHYS+0x22c,'<I',RAILS),patch(PHYS+0x230,'<I',WORLD),patch(GROUND_GATE+0x18,'<I',GCONTACT),patch(GOBS+4,'<4I',address,value,width,0xa7662059)]
 set_state(3,target,extra,True,label=f'lip event changes live state {address:x} before target {target:x}')
 assert qb_calls[hex(0xa7662059)]>prior
coverage={}
blocks=(ROOT/'local/analysis/physics-command-path-instructions.txt').read_text().split('\n\n')
import re
for at in action_ranges:
 block=next(b for b in blocks if b.lstrip().startswith(f'{at:08x} '))
 addresses=[int(line[:8],16) for line in block.splitlines()[1:] if re.match(r'^[0-9a-f]{8} ',line)]
 missing=[hex(address) for address in addresses if not action_hits[address]]
 assert not missing,(hex(at),missing)
 coverage[hex(at)]={'total':len(addresses),'covered':len(addresses),'missing':missing}
scope='Seven complete original physics state actions: CancelWallpush, NoSpin, InBail, NotInBail, checksum2a547e37, SetRailSound and SetState. Timed equality checks preserve timestamps when unchanged, raw nonboolean bytes, timer wrap, retained calls and NoSpin aliasing. SetRailSound uses actual checksum parsing and updates the sound byte independently. SetState retains rail-exit events, live pointer/mode reloads, rail-pointer clearing, wallride orientation repair including unknown targets, ground flag clearing and complete real state-change dependencies. Actual rail QB callbacks mutate state, rail and contact data; no gameplay callee is stubbed. Initialized components, finite geometry, successful allocations, mapped pointers and terminating fixture QB are contracts. The named member bridge has a separate integration corpus; original training remains unplayable.'
scope += ' Maintained main-module comparison; browser and level integration are recorded separately.'
fixture={'base':BASE,'memory':'physics-state-actions-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'native_qb_and_audio_callbacks','pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'pointer_globals':sorted(pointer_globals),'native_callbacks':[{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]+[dict(spec,module='wall-audio-callbacks.wasm') for spec in audio['native_callbacks']]}
(folder/'physics-state-actions-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
(folder/fixture['memory']).write_bytes(initial)
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(oracle.counts.values()),'counts':dict(oracle.counts),'instruction_coverage':coverage,'native_qb_calls':dict(qb_calls),'audio_device_calls':dict(callback_counts),'scope':scope}
(folder.parent/'physics-state-actions.json').write_text(json.dumps(report,indent=2)+'\n')
print('Physics state actions',len(labels),sum(oracle.counts.values()),sum(v['covered'] for v in coverage.values()),dict(qb_calls),flush=True)

subprocess.run(['node',str(ROOT/'tools/verify_physics_state_actions_wasm.mjs')],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file() and p.name!='.DS_Store'}
artifacts=[folder/'physics-state-actions-fixtures.json',folder/fixture['memory']]
artifacts += [folder/spec['module'] for spec in fixture.get('native_callbacks',[])]
if fixture.get('memory_fixture'):artifacts.append(folder/fixture['memory_fixture'])
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in artifacts}
(folder.parent/'physics-state-actions.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS physics-state-actions',len(fixture['cases']),flush=True)
