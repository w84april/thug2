import hashlib,json,subprocess
"""Named-script integration of sixteen recovered physics members."""
from pathlib import Path
flags_context_source=Path('tools/physics_flags_context_setup.py').read_text()
exec(compile(flags_context_source[:flags_context_source.index('for entry,reverse,seed in ')],'<verified named-physics setup>','exec'))
folder=ROOT/'local/analysis'
members.clear()
actions={0x4fbfe0:'set_skater_vehicle',0x4fc040:'lock_velocity_direction',0x4fc060:'set_grind_tweak',0x4fc180:'set_ammo_type',0x4fd140:'last_spin_was'}
actions.update({0x4fc880:'airtime_less_than',0x4fc8e0:'airtime_greater_than',0x4fc940:'get_airtime',0x4fd580:'get_matrix_normal',0x4fd5e0:'get_last_ground_pos',0x4fd610:'get_last_ground_heading',0x4fdc30:'get_ammo',0x4fdc50:'get_ammo_type',0x4fdc70:'get_pitch_bail_dir',0x500e80:'can_kick',0x509b70:'trigger_grind_off'})
for address,name in actions.items():
 members[address]='thug_physics_'+name+'_member_draft'
 function_exports.append([address,members[address]])
 oracle.cpu.hook_add(UC_HOOK_CODE,member_observe,begin=address,end=address)
exports.append([0x64bc1c,'thug_grind_off_events_draft'])
selected=[row for row in table_metadata['entries'] if int(row['member'],16) in members]
assert len(selected)==16
groups=[selected]
for entry,reverse,seed,group in itertools.product(['startup','object'],[False,True],[0,1,255],range(1)):
 b,_=jump_config(trigger=seed==1);descriptor=b.alloc(physics_table_bytes)
 for row in table_metadata['entries']:fields.add(descriptor+row['index']*24+8)
 commands=list(reversed(groups[group])) if reverse else groups[group]
 bytecode=bytearray();native_offsets=[]
 for row in commands:
  address=int(row['member'],16)
  bytecode+=b'\x01\x16'+struct.pack('<I',int(row['name_checksum'],16))
  if address in [0x4fbfe0,0x4fc180]:
   bytecode+=b'\x16'+struct.pack('<I',0x12345678+seed)
  elif address==0x4fc060:
   bytecode+=b'\x17'+struct.pack('<I',0xffffffff if seed else 0)
  elif address==0x4fc040 and seed:
   bytecode+=b'\x16'+struct.pack('<I',0xf649d637)
  elif address==0x4fd140 and seed:
   bytecode+=b'\x16'+struct.pack('<I',0x47953f00)
   if seed==255:bytecode+=b'\x16'+struct.pack('<I',0x996d5512)
  elif address in [0x4fc880,0x4fc8e0] and seed:
   bytecode+=b'\x1a'+struct.pack('<f',1.5)+b'\x16'+struct.pack('<I',0x019176c5 if seed==1 else 0xd029f619)
  native_offsets.append(len(bytecode)+2)
  bytecode+=b'\x01\x43'+struct.pack('<I',NATIVE)
 bytecode+=b'\x01\x24';code=b.alloc(bytes(bytecode))
 fields.update(code+offset for offset in native_offsets)
 name=0x71660043;b.symbol(name,7,code)
 cache_entry=b.alloc(struct.pack('<5I',name,code,1,0,0));slot=CACHETABLE+32+(name&3)*12
 previous=next((bytes.fromhex(data) for at,data in reversed(b.extra) if at==slot),initial[slot-BASE:slot-BASE+12])
 link=b.alloc(previous);b.extra.append(patch(slot,'<3I',name,cache_entry,link))
 before,body=setup(False,0xbaf9b341)
 p=b.patches()+body+network()+[patch(BODIES,'<I',CTABLE),patch(BODIES+0x10,'<I',SCRIPTS),patch(BODIES+0x104,'<I',0),patch(PHYS,'<I',0x64bc48),patch(BODIES+0x110,'<B',seed),patch(BODIES+0x2bc,'<I',1),patch(game+0x39d,'<B',seed),patch(PHYS+0x2e0,'<f',10.000001),patch(PHYS+0x22c,'<I',0),patch(SKATER_STATE+0x18,'<I',{0:0,1:2,255:3}[seed]),patch(BODIES+0x6c,'<16f',*identity),patch(PHYS+0x18,'<16f',*identity),patch(PHYS+0x58,'<4f',0,1,0,1)]
 p += [patch(c+8,'<I',1) for c in chain]
 p += [patch(SKATER_STATE+0x28,'<B',seed),patch(PHYS+0x3a5,'<B',255-seed)]
 p += [patch(PHYS+0x380,'<2I',0xfffffff0,1000+seed),patch(PHYS+0x310,'<B',0),patch(PHYS+0x2d9,'<B',1),patch(INPUT+0x180,'<B',0),patch(INPUT+0x40,'<B',0),patch(SKATER_STATE+0x20,'<B',0),patch(PHYS+0x303,'<B',0),patch(BODIES+0xac,'<4f',10,0,0,1),patch(PHYS+0x2f8,'<I',0xffffffff if seed else 0),patch(PHYS+0x2d4,'<I',0x12345678),patch(PHYS+0x348,'<I',0x7f812345 if seed==255 else bits(90)),patch(PHYS+0x338,'<3I',bits(10),bits(20),0xff812345 if seed==255 else bits(30)),patch(BODIES+0x7c,'<3I',0x7f812345 if seed==255 else 0,bits(1),0),patch(PHYS+0x22c,'<I',RAILS if seed==1 else 0),patch(PHYS+0x230,'<I',WORLD),patch(GROUND_GATE+0x18,'<I',0)]
 for i in range(3):p += [patch(RAILS+i*0x54+0x20,'<4f',0,20000,i*100,1),patch(RAILS+i*0x54+0x40,'<5I',RAILS+(i+1)*0x54 if i<2 else 0,RAILS+(i-1)*0x54 if i else 0,4,0x1800+i,0)]
 calls=before+[call(0x46f060,0,[0x5bd63b29,descriptor,24]),call(0x4738e0,SCRIPTS),call(0x474540,SCRIPTS,[name,0,0,BODIES])]
 calls += [call(0x4750b0,SCRIPTS,[QUERY]) if entry=='startup' else call(0x45d920,BODIES,[QUERY])]
 old_hits=member_hits.copy();compare(calls,p,label=f'{entry}, registered actions group{group}, reverse{reverse}, seed{seed}')
 assert oracle.word(GOBS)==len(commands)+int(seed==1)
 expected_members={int(row['member'],16) for row in commands}
 assert all(member_hits[address]-old_hits[address]==int(address in expected_members) for address in members)
assert set(member_hits)==set(members) and set(member_hits.values())=={12}
scope='Sixteen recovered physics members execute through actual named QB opcode16 and full109entry registration. Includes prior five parameter members plus airtime comparisons, seven script-output members, CanKick and TriggerGrindOff. Both script orders, raw payloads, anonymousfloat/unitflags, output allocation, startup/object frames and restored outer scopes are covered. A real nested rail event executes for seed1, in addition to one native observation per member. Every member executes12times originally. Other component frames remain suspended; initializer is reference-only; no level-startup claim.'
fixture={'base':BASE,'memory':'physics-command-values-context-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'native_qb_callbacks','pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'pointer_globals':sorted(pointer_globals),'scoped_event_services':{'symbol':'thug_component_services','pointer':0},'outer_scope':OUTER_SCOPE,'native_callbacks':[{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]}
(folder/'physics-command-values-context-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
(folder/fixture['memory']).write_bytes(initial)
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(oracle.counts.values()),'counts':dict(oracle.counts),'member_calls':{hex(k):v for k,v in member_hits.items()},'native_qb_calls':dict(qb_calls),'scope':scope}
(folder/'physics-command-values-context-original.json').write_text(json.dumps(report,indent=2)+'\n')
print('Named physics actions',len(labels),sum(oracle.counts.values()),sum(member_hits.values()),sum(qb_calls.values()),flush=True)
