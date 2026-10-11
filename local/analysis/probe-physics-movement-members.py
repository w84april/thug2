"""CanKick and TriggerGrindOff through the established actual engine graph."""
from pathlib import Path
source=Path('tools/verify_jump.py').read_text().split('for mode in [0,1,2,3,4,5,6,0xffffffff]:')[0]
exec(compile(source,'<complete reference graph>','exec'))
folder=ROOT/'local/analysis'
bind(0x500e80,'thug_physics_can_kick_member_draft',2,'word',False,False,True)
bind(0x509b70,'thug_physics_trigger_grind_off_draft',2,'word',True,True,True)
exports.append([0x64bc1c,'thug_grind_off_events_draft'])
function_exports += [[0x500e80,'thug_physics_can_kick_member_draft'],[0x509b70,'thug_physics_trigger_grind_off_member_draft']]
hits=Counter();guards={};return_entries={0x500e8b:0x500e80,0x509b7f:0x509b70}
from unicorn.x86_const import UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP
def observe_member(cpu,at,size,user):
 hits[at]+=1
 if at in [0x500e80,0x509b70]:guards[at]=[cpu.reg_read(r) for r in [UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP]]
 if at in return_entries:assert guards[return_entries[at]]==[cpu.reg_read(r) for r in [UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP]]
for at,n in [(0x500e80,14),(0x509b70,18)]:oracle.cpu.hook_add(UC_HOOK_CODE,observe_member,begin=at,end=at+n-1)
labels=[];oracle.cases.clear();oracle.counts.clear();oracle.coverage.clear();qb_calls.clear();callback_counts.clear()
def can_kick(flags=(0,1,0,0),selector=(0,0),velocity=0x43fa0000,label='CanKick'):
 b,_=jump_config();p=b.patches()+[patch(PHYS+0x310,'<B',flags[0]),patch(PHYS+0x2d9,'<B',flags[1]),patch(INPUT+0x180,'<B',flags[2]),patch(INPUT+0x40,'<B',flags[3]),patch(SKATER_STATE+0x20,'<B',selector[0]),patch(PHYS+0x303,'<B',selector[1]),patch(BODIES+0xac,'<4I',velocity,0,0,0x3f800000)]
 stages=compare([call(0x500e80,PHYS,[0xdeadbeef,0x87654321])]*2,p,label=label)
 assert all(s['result'] in [0,1] for s in stages)
selectors=[(0,0),(1,0),(0,1),(255,255)]
for flags,selector in itertools.product(itertools.product([0,1],repeat=4),selectors):can_kick(flags,selector,label=f'input gates{flags},selector{selector}')
for selector,velocity in itertools.product(selectors,[bits(0),bits(499),bits(500),bits(500)+1,bits(599),bits(600),bits(600)+1,bits(-500),0x7f800000,0x7f812345]):can_kick(selector=selector,velocity=velocity,label=f'speedbits{velocity:x},selector{selector}')
for index_,value in itertools.product(range(4),[2,127,128,255]):
 flags=[0,1,0,0];flags[index_]=value;can_kick(flags,velocity=bits(10),label=f'nonboolean inputgate{index_},value{value}')
def grind_off(rail=True,trigger=True,contact='none',repeat=2,extra=(),label='grind off'):
 b,_=jump_config(trigger=trigger);before,body=setup(False,0xbaf9b341)
 p=b.patches()+body+network()+[patch(PHYS+0x22c,'<I',RAILS+0x54 if rail else 0),patch(PHYS+0x230,'<I',WORLD),patch(GROUND_GATE+0x18,'<I',0 if contact=='none' else GCONTACT),patch(SKATER_STATE+0x18,'<I',5)]
 for i in range(3):p += [patch(RAILS+i*0x54+0x20,'<4f',0,20000,i*100,1),patch(RAILS+i*0x54+0x40,'<5I',RAILS+(i+1)*0x54 if i<2 else 0,RAILS+(i-1)*0x54 if i else 0,4,0x1800+i,0)]
 if contact=='dead':p.append(patch(GCONTACT,'<I',0))
 old=sum(qb_calls.values());stages=compare(before+[call(0x509b70,PHYS,[0xdeadbeef,0x87654321])]*repeat,p+list(extra),label=label)
 assert all(s['result']==1 for s in stages[-repeat:]);assert (sum(qb_calls.values())>old)==(rail and trigger)
for rail,trigger,contact in itertools.product([False,True],[False,True],['none','live','dead']):grind_off(rail,trigger,contact,label=f'rail{rail},trigger{trigger},contact{contact}')
for address,value,width in [(PHYS+0x1528,SKATER_STATE2,4),(PHYS+0x22c,0,4),(PHYS+0x244,0x12345678,4),(GCONTACT,0,4)]:
 grind_off(contact='live',extra=[patch(GOBS+4,'<4I',address,value,width,0xa7662059)],label=f'actual railQB changes{address:x}')
coverage={}
for at,n in [(0x500e80,14),(0x509b70,18)]:
 ins=list(md.disasm(pe.get_data(at-0x400000,n),at));missing=[hex(i.address) for i in ins if not hits[i.address]];assert not missing
 coverage[hex(at)]={'total':len(ins),'covered':len(ins),'missing':[]}
scope='Original500e80 CanKick and509b70 TriggerGrindOff fixed-ABI members. Actual acceleration gating/stat interpolation/speed comparison and full rail node/contact/event/QB graph run. Gates include raw nonboolean bytes, normal/alternate selectors, equality thresholds and unordered speed; return normalizes AL. Rail events use exact13,4,0 array, absent/disabled triggers, live/dead contact, repeats and real scripts changing live state/rail/contact fields. Callee-saved registers, stack, full memory/globals and QB observations compare. Successful allocation, initialized components and terminating fixture QB are contracts; not level startup.'
fixture={'base':BASE,'memory':'physics-movement-members-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'native_qb_callbacks','pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'pointer_globals':sorted(pointer_globals),'native_callbacks':[{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]+[dict(spec,module='wall-audio-callbacks.wasm') for spec in audio['native_callbacks']]}
(folder/fixture['memory']).write_bytes(initial);(folder/'physics-movement-members-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(oracle.counts.values()),'counts':dict(oracle.counts),'instruction_coverage':coverage,'callee_calls':dict(oracle.coverage),'native_qb_calls':dict(qb_calls),'scope':scope}
(folder/'physics-movement-members-original.json').write_text(json.dumps(report,indent=2)+'\n');print('Movement members',len(labels),sum(oracle.counts.values()),sum(v['covered'] for v in coverage.values()),sum(qb_calls.values()),flush=True)
