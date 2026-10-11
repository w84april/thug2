"""Original QB dispatch reached through scoped startup and object-frame entry."""
from pathlib import Path
prefix=Path('tools/verify_component_lifecycle.py').read_text().split('for fill in [0,0xa5,0xff]:')[0]
prefix=prefix.replace('component-lifecycle.json','component-context.json')
exec(compile(prefix,'<complete component graph without its corpus>','exec'))
folder=ROOT/'local/validation/collision';report_path=folder.parent/'component-context.json'
bind(0x4750b0,'thug_component_execute_script',0,'word',True,True,True)
SCOPED_PREVIOUS=0x16dd400
put(SCOPED_PREVIOUS,'<3I',QUERY,PRINT,ADAPTER)
initial=bytes(memory);oracle.initial=initial
labels=[];oracle.cases.clear();oracle.counts.clear();oracle.coverage.clear()
for entry,name,flags in itertools.product(['startup','object'],[0,0x315d9ed4,0x8819dd8b],[[],[0xd607e2e6],[0xd607e2e6,0x90a91232]]):
 b,_,_,_=config()
 descriptor=b.alloc(struct.pack('<4I',name,0x5bd63b29,0,0))
 args=b'\x16'+struct.pack('<I',0xa1dc81f9)+b'\x07\x16'+struct.pack('<I',NODE_NAME)
 args+=b''.join(b'\x16'+struct.pack('<I',flag) for flag in flags)
 code=b.alloc(b'\x01\x46'+struct.pack('<I',descriptor)+args+b'\x01\x43'+struct.pack('<I',NATIVE)+b'\x01\x24')
 fields.add(code+8+len(args))
 program_name=0x71664443;b.symbol(program_name,7,code)
 cache_entry=b.alloc(struct.pack('<5I',program_name,code,1,0,0));slot=CACHETABLE+32+(program_name&3)*12
 link=b.alloc(initial[slot-BASE:slot-BASE+12]);b.extra.append(patch(slot,'<3I',program_name,cache_entry,link))
 before,body=setup(False,0xbaf9b341)
 p=b.patches()+body+network()+[patch(BODIES,'<I',CTABLE),patch(BODIES+0xbc,'<B',0),patch(BODIES+0x10,'<I',SCRIPTS),patch(BODIES+0x104,'<I',0),patch(PHYS,'<I',0x64bc48),patch(PHYS+0x248,'<B',1)]
 p += [patch(c+8,'<I',1) for c in chain+[MOTION,SHADOW]]
 calls=before+[call(0x4738e0,SCRIPTS),call(0x474540,SCRIPTS,[program_name,0,0,BODIES])]
 calls += [call(0x4750b0,SCRIPTS,[QUERY]) if entry=='startup' else call(0x45d920,BODIES,[QUERY])]
 stages=test(calls,p,label=entry+' script calls real component descriptor '+hex(name))
 assert stages[-1]['callbacks']==1
for flags,dead in itertools.product([0,1,2,3,8,0xffffffff],[0,1]):
 p=[patch(BODIES,'<I',CTABLE),patch(BODIES+8,'<I',dead),patch(BODIES+0x10,'<I',0),patch(BODIES+0x104,'<I',flags)]
 p += [patch(c+8,'<I',1) for c in chain+[MOTION,SHADOW]]
 test([call(0x45d920,BODIES,[QUERY])]*2,p,label='object frame early returns restore prior host scope')
scope='Host-context integration, not additional recovered functions: real QB calls component descriptors and complete physics/Motion commands from startup execution and object updates. Component frame methods are suspended in this fixture to isolate script entry; actual node/reset/animation/network effects run. Every call checks restoration of the previous host-service pointer; the Wasm checker replays both null and a valid outer scope. Full playable-level startup remains unfinished.'
fixture={'base':BASE,'memory':'component-context-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'native_qb_callbacks','pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'scoped_event_services':{'symbol':'thug_component_services','pointer':0},'outer_scope':SCOPED_PREVIOUS,'native_callbacks':[{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE},{'module':'component-command-callbacks.wasm','export':'fixture_component_checksum','original':CHECKSUM},{'module':'component-command-callbacks.wasm','export':'fixture_component_member','original':MEMBER}]}
(folder/'component-context-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')));(folder/fixture['memory']).write_bytes(initial)
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'scope':scope}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('Original component context',len(labels),sum(oracle.counts.values()),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_component_context_wasm.mjs')],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [folder/'component-context-fixtures.json',folder/fixture['memory'],ROOT/'tools/component_context_wasm_checks.mjs']}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS component-context',report['cases'],sum(oracle.counts.values()))
