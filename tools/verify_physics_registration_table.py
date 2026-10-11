import hashlib,json,subprocess
"""Register the full original physics table, then run named Jump scripts."""
from pathlib import Path
registration_probe=Path('tools/verify_command_registration.py').read_text()
registration_setup=registration_probe[:registration_probe.index('for registration_names in ')]
exec(compile(registration_setup,'<pinned command-registration setup>','exec'))

# Establish the table with the real straight-line initializer in the isolated
# original CPU. This verifies discovery data; it is not a recovered initializer.
table_address=0x6826c8;table_size=110*24
initializer_hits=Counter()
def trace_initializer(cpu,at,size,user):initializer_hits[at]+=1
oracle.cpu.hook_add(UC_HOOK_CODE,trace_initializer,begin=0x6417d0,end=0x6423e0)
sp=oracle.stack+0x18000
oracle.cpu.mem_write(sp,struct.pack('<I',oracle.stop))
oracle.cpu.reg_write(UC_X86_REG_ESP,sp)
oracle.cpu.emu_start(0x6417d0,oracle.stop,count=1000)
assert oracle.cpu.reg_read(UC_X86_REG_EIP)==oracle.stop
assert oracle.cpu.reg_read(UC_X86_REG_ESP)==sp+4
assert len(initializer_hits)==557
physics_table_bytes=bytes(oracle.cpu.mem_read(table_address,table_size))
table_metadata=json.loads((ROOT/'local/analysis/physics-descriptor-bindings.json').read_text())
table_rows=table_metadata['entries']+[table_metadata['terminator']]
expected_table=b''.join(struct.pack('<6I',int(row['name_checksum'],16),int(row['component_type'],16),int(row['member'],16),row['receiver_offset'],row['word_10'],row['word_14']) for row in table_rows)
assert physics_table_bytes==expected_table

loop=registration_context_source[registration_context_loop_start:registration_context_source.index("scope='Host integration")]
loop=loop.replace("struct.pack('<6I',0x584cf9e9,0x5bd63b29,0x509a40,0,0,0)","physics_table_bytes")
loop=loop.replace("b'\\x01\\x46'+struct.pack('<I',descriptor)","b'\\x01\\x16'+struct.pack('<I',0x584cf9e9)")
loop=loop.replace("calls=before+[call(0x4738e0,SCRIPTS)","calls=before+[call(0x46f060,0,[0x5bd63b29,descriptor,24]),call(0x4738e0,SCRIPTS)")
loop=loop.replace('QB Jump descriptor state','full physics table, named Jump state')
loop+='''
 for row in table_metadata['entries']:
  name=int(row['name_checksum'],16);symbol=oracle.word(SYMBOLS+(name&4095)*4)
  while symbol and oracle.word(symbol+4)!=name:symbol=oracle.word(symbol+16)
  assert symbol and oracle.cpu.mem_read(symbol+1,1)[0]==9
  assert oracle.word(symbol+12)==descriptor+row['index']*24
'''
exec(compile(loop,'<full table followed by named Jump>','exec'))
scope='Full109-entry original physics descriptor table, established by running the original6417d0 initializer and comparing all2640bytes to prior static discovery. Real46f060 registers every name as type9 with its borrowed descriptor identity, then actual named Jump dispatch runs from startup and object frames. All109symbols are independently checked after every case. Only Jump is invoked; other member addresses remain opaque fixture data, not recovered command bodies. Initializer execution prepares the reference fixture and is not counted as a new recovery. Existing successful-allocation, initialized-component and terminal-observer contracts apply. The initializer itself remains reference-only.'
scope += ' Maintained main-module comparison; browser and level integration are recorded separately.'
fixture={'base':BASE,'memory':'physics-registration-table-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'native_qb_and_audio_callbacks','pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'pointer_globals':sorted(pointer_globals),'scoped_event_services':{'symbol':'thug_component_services','pointer':0},'outer_scope':OUTER_SCOPE,'native_callbacks':[{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]+[dict(spec,module='wall-audio-callbacks.wasm') for spec in audio['native_callbacks']]}
(folder/'physics-registration-table-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
(folder/fixture['memory']).write_bytes(initial)
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(oracle.counts.values()),'counts':dict(oracle.counts),'symbols_checked':109*len(labels),'initializer_instructions':len(initializer_hits),'table_bytes':table_size,'table_sha256':hashlib.sha256(physics_table_bytes).hexdigest(),'native_qb_calls':dict(qb_calls),'audio_device_calls':dict(callback_counts),'scope':scope}
(folder.parent/'physics-registration-table.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report),flush=True)

subprocess.run(['node',str(ROOT/'tools/verify_physics_registration_table_wasm.mjs')],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file() and p.name!='.DS_Store'}
artifacts=[folder/'physics-registration-table-fixtures.json',folder/fixture['memory']]
artifacts += [folder/spec['module'] for spec in fixture.get('native_callbacks',[])]
if fixture.get('memory_fixture'):artifacts.append(folder/fixture['memory_fixture'])
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in artifacts}
(folder.parent/'physics-registration-table.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS physics-registration-table',len(fixture['cases']),flush=True)
