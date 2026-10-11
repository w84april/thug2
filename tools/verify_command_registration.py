import hashlib,json,subprocess
"""Original descriptor registration followed by actual named Jump QB dispatch."""
from pathlib import Path
registration_context_source=Path('tools/verify_jump_context.py').read_text()
registration_context_loop_start=registration_context_source.index('for entry,mode,blocked,flags in ')
exec(compile(registration_context_source[:registration_context_loop_start],'<complete Jump context graph>','exec'))
folder=ROOT/'local/validation/collision'
bind(0x46f060,'thug_script_register_commands',3,'void',True,False,False)
registration_hits=Counter()
def registration_trace(cpu,at,size,user):registration_hits[at]+=1
oracle.cpu.hook_add(UC_HOOK_CODE,registration_trace,begin=0x46f060,end=0x46f08a)
labels=[];oracle.cases.clear();oracle.counts.clear();oracle.coverage.clear();qb_calls.clear();callback_counts.clear()
def register(names,stride=24,unused=0,repeat=1):
 b=Build();data=bytearray([0xa7]*((len(names)+1)*stride))
 for i,name in enumerate(names+[0]):struct.pack_into('<I',data,i*stride,name)
 table=b.alloc(data)
 compare([call(0x46f060,0,[unused,table,stride])]*repeat,b.patches(),label=f'command names {names[:3]}, count {len(names)}, stride {stride}, ignored argument {unused:x}, repeats {repeat}')
 # Independently establish registration order and the borrowed payload identity.
 for name in set(names[:names.index(0)] if 0 in names else names):
  symbol=oracle.word(SYMBOLS+(name&4095)*4)
  while oracle.word(symbol+4)!=name:symbol=oracle.word(symbol+16)
  last=max(i for i,n in enumerate(names[:names.index(0)] if 0 in names else names) if n==name)
  assert oracle.cpu.mem_read(symbol+1,1)[0]==9 and oracle.word(symbol+12)==table+last*stride
for registration_names in [[],[0],[1],[0x584cf9e9],[1,1],[1,0x1001,0x2001,1],[7,0,9],list(range(1,110))]:
 for stride,unused in itertools.product([4,8,16,24],[0,0x5bd63b29,0xffffffff]):register(registration_names,stride,unused)
for repeats in [2,4]:
 for registration_names in [[0x584cf9e9],[1,1,0x1001],list(range(1,17))]:register(registration_names,repeat=repeats)
generic_cases=len(labels)
# Keep the verified host fixture, changing only registration and the QB opcode:
# raw name16 must resolve the new type9 symbol instead of using direct opcode46.
loop=registration_context_source[registration_context_loop_start:registration_context_source.index("scope='Host integration")]
loop=loop.replace("struct.pack('<6I',0x584cf9e9,0x5bd63b29,0x509a40,0,0,0)","struct.pack('<6I',0x584cf9e9,0x5bd63b29,0x509a40,0,0,0)+bytes(24)")
loop=loop.replace("b'\\x01\\x46'+struct.pack('<I',descriptor)","b'\\x01\\x16'+struct.pack('<I',0x584cf9e9)")
loop=loop.replace("calls=before+[call(0x4738e0,SCRIPTS)","calls=before+[call(0x46f060,0,[0xdeadbeef,descriptor,24]),call(0x4738e0,SCRIPTS)")
loop=loop.replace('QB Jump descriptor state','QB named registered Jump state')
assert "b'\\x01\\x46'" not in loop
exec(compile(loop,'<named registered Jump cases>','exec'))
rows=list(md.disasm(pe.get_data(0x6f060,43),0x46f060));missing=[hex(i.address) for i in rows if not registration_hits[i.address]]
assert not missing
scope='Complete original46f060 command-symbol registration: unused leading argument, caller stride, zero-name terminator, duplicate insertion, bucket collisions, repeated registration and borrowed descriptor identity. Actual479110 symbol allocation/insertion executes.102generic cases plus36real QB named-Jump cases reach the recovered member through type9 lookup from startup/object frames; pointer fields, memory, globals and native/audio observations compare exactly. Valid readable terminating tables, successful allocation and existing fixture runtime contracts apply. Other physics commands and full level startup remain unfinished.'
scope += ' Maintained main-module comparison; browser and level integration are recorded separately.'
fixture={'base':BASE,'memory':'command-registration-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'native_qb_and_audio_callbacks','pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'pointer_globals':sorted(pointer_globals),'scoped_event_services':{'symbol':'thug_component_services','pointer':0},'outer_scope':OUTER_SCOPE,'native_callbacks':[{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]+[dict(spec,module='wall-audio-callbacks.wasm') for spec in audio['native_callbacks']]}
(folder/'command-registration-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')));(folder/fixture['memory']).write_bytes(initial)
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'generic_cases':generic_cases,'named_jump_cases':len(labels)-generic_cases,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'instruction_coverage':{'total':len(rows),'covered':len(rows),'missing':missing},'native_qb_calls':dict(qb_calls),'audio_device_calls':dict(callback_counts),'scope':scope}
(folder.parent/'command-registration.json').write_text(json.dumps(report,indent=2)+'\n');print('Original registration',len(labels),sum(oracle.counts.values()),report['instruction_coverage'],flush=True)

subprocess.run(['node',str(ROOT/'tools/verify_command_registration_wasm.mjs')],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file() and p.name!='.DS_Store'}
artifacts=[folder/'command-registration-fixtures.json',folder/fixture['memory']]
artifacts += [folder/spec['module'] for spec in fixture.get('native_callbacks',[])]
if fixture.get('memory_fixture'):artifacts.append(folder/fixture['memory_fixture'])
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in artifacts}
(folder.parent/'command-registration.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS command-registration',len(fixture['cases']),flush=True)
