import hashlib,json,subprocess
"""Named-script integration of all65 recovered physics command members."""
from pathlib import Path
flags_context_source=Path('tools/physics_flags_context_setup.py').read_text()
exec(compile(flags_context_source[:flags_context_source.index('for entry,reverse,seed in ')],'<verified named-physics setup>','exec'))
actions={0x4fc840:'cancel_wallpush',0x4fcf90:'no_spin',0x4fcfc0:'in_bail',0x4fcff0:'not_in_bail',0x4fd630:'set_vert_air',0x4fd040:'set_rail_sound',0x509a80:'set_state'}
for address,name in actions.items():
 members[address]='thug_physics_'+name+'_member'
 function_exports.append([address,members[address]])
 oracle.cpu.hook_add(UC_HOOK_CODE,member_observe,begin=address,end=address)
exports.append([0x64bbd4,'thug_state_lip_exit_events'])
selected=[row for row in table_metadata['entries'] if int(row['member'],16) in members]
assert len(selected)==65
groups=[selected[:33],selected[33:]]
for entry,reverse,seed,group in itertools.product(['startup','object'],[False,True],[0,1,255],range(2)):
 b,_=jump_config();descriptor=b.alloc(physics_table_bytes)
 for row in table_metadata['entries']:fields.add(descriptor+row['index']*24+8)
 commands=list(reversed(groups[group])) if reverse else groups[group]
 bytecode=bytearray();native_offsets=[]
 for row in commands:
  address=int(row['member'],16)
  bytecode+=b'\x01\x16'+struct.pack('<I',int(row['name_checksum'],16))
  if address==0x509a80:
   bytecode+=b'\x16'+struct.pack('<I',{0:0x58007c97,1:0x439f4704,255:0xa549b57b}[seed])
  elif address==0x4fd040:
   bytecode+=b'\x16'+struct.pack('<I',0x8d10119d if seed else 0x12345678)
  native_offsets.append(len(bytecode)+2)
  bytecode+=b'\x01\x43'+struct.pack('<I',NATIVE)
 bytecode+=b'\x01\x24';code=b.alloc(bytes(bytecode))
 fields.update(code+offset for offset in native_offsets)
 name=0x71660023;b.symbol(name,7,code)
 cache_entry=b.alloc(struct.pack('<5I',name,code,1,0,0));slot=CACHETABLE+32+(name&3)*12
 previous=next((bytes.fromhex(data) for at,data in reversed(b.extra) if at==slot),initial[slot-BASE:slot-BASE+12])
 link=b.alloc(previous);b.extra.append(patch(slot,'<3I',name,cache_entry,link))
 before,body=setup(False,0xbaf9b341)
 p=b.patches()+body+network()+[patch(BODIES,'<I',CTABLE),patch(BODIES+0x10,'<I',SCRIPTS),patch(BODIES+0x104,'<I',0),patch(PHYS,'<I',0x64bc48),patch(BODIES+0x110,'<B',seed),patch(BODIES+0x2bc,'<I',1),patch(game+0x39d,'<B',seed),patch(PHYS+0x2e0,'<f',10.000001),patch(PHYS+0x22c,'<I',0),patch(SKATER_STATE+0x18,'<I',{0:0,1:2,255:3}[seed]),patch(BODIES+0x6c,'<16f',*identity),patch(PHYS+0x18,'<16f',*identity),patch(PHYS+0x58,'<4f',0,1,0,1)]
 p += [patch(c+8,'<I',1) for c in chain]
 for address,kind,args in re.findall(r'/\* ([0-9a-f]{8}) \*/ (MEMBER|SET|GET|STATE)\(([^)]*)\)',(ROOT/'src/game/physics_flags.c').read_text()):
  if kind!='MEMBER':p.append(patch((SKATER_STATE if kind=='STATE' else PHYS)+int(args.split(',')[1],0),'<B',seed))
 calls=before+[call(0x46f060,0,[0x5bd63b29,descriptor,24]),call(0x4738e0,SCRIPTS),call(0x474540,SCRIPTS,[name,0,0,BODIES])]
 calls += [call(0x4750b0,SCRIPTS,[QUERY]) if entry=='startup' else call(0x45d920,BODIES,[QUERY])]
 old_hits=member_hits.copy();compare(calls,p,label=f'{entry}, registered actions group{group}, reverse{reverse}, seed{seed}')
 assert oracle.word(GOBS)==len(commands)
 expected_members={int(row['member'],16) for row in commands}
 assert all(member_hits[address]-old_hits[address]==int(address in expected_members) for address in members)
assert set(member_hits)==set(members) and set(member_hits.values())=={12}
scope='All65 recovered physics state members execute via actual named QB opcode16, complete109entry table registration, real symbol lookup and fixed-ABI descriptor dispatch. Two groups remain below the native observation log capacity. Both script orders, old ground/wallride/lip modes, initial0/1/255flags, actual SetState/SetRailSound parameter parsing, startup/object frames and prior host context restoration are covered. Every member executes12times originally. Real state/orientation/timer dependencies run; terminal native QB calls observe command completion. Other component frames are suspended, and the remaining43command entries plus Jump are not invoked here. Original initializer is reference fixture preparation only. This fixture integration does not establish level startup.'
scope += ' Maintained main-module comparison; browser and level integration are recorded separately.'
fixture={'base':BASE,'memory':'physics-state-actions-context-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'native_qb_callbacks','pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'pointer_globals':sorted(pointer_globals),'scoped_event_services':{'symbol':'thug_component_services','pointer':0},'outer_scope':OUTER_SCOPE,'native_callbacks':[{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]}
(folder/'physics-state-actions-context-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
(folder/fixture['memory']).write_bytes(initial)
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(oracle.counts.values()),'counts':dict(oracle.counts),'member_calls':{hex(k):v for k,v in member_hits.items()},'native_qb_calls':dict(qb_calls),'scope':scope}
(folder.parent/'physics-state-actions-context.json').write_text(json.dumps(report,indent=2)+'\n')
print('Named physics actions',len(labels),sum(oracle.counts.values()),sum(member_hits.values()),sum(qb_calls.values()),flush=True)

subprocess.run(['node',str(ROOT/'tools/verify_physics_state_actions_context_wasm.mjs')],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file() and p.name!='.DS_Store'}
artifacts=[folder/'physics-state-actions-context-fixtures.json',folder/fixture['memory']]
artifacts += [folder/spec['module'] for spec in fixture.get('native_callbacks',[])]
if fixture.get('memory_fixture'):artifacts.append(folder/fixture['memory_fixture'])
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in artifacts}
(folder.parent/'physics-state-actions-context.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS physics-state-actions-context',len(fixture['cases']),flush=True)
