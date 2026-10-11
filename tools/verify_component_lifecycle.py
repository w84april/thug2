import subprocess
"""Original base/physics lifecycle and descriptor forwarding, full method tables."""
from pathlib import Path
prefix=Path('tools/verify_physics_command.py').read_text().split('for value in [0,1,2,255]:')[0]
prefix=prefix.replace('physics-command.json','component-lifecycle.json')
exec(compile(prefix,'<complete physical command graph>','exec'))
folder=ROOT/'local/validation/collision';report_path=folder.parent/'component-lifecycle.json'
for row in [(0x45d730,'thug_component_construct',0,'word',False,False,True),
 (0x45d740,'thug_component_destroy',0,'void',False,False,True),
 (0x45d780,'thug_component_delete',1,'word',True,False,True),
 (0x45d760,'thug_component_suspend',1,'void',False,False,True),
 (0x4e3f90,'thug_component_refresh',1,'void',False,False,True),
 (0x48dcd0,'thug_component_empty_two',2,'void',False,False,True),
 (0x5bab90,'thug_component_empty_one',1,'void',False,False,True),
 (0x45d720,'thug_component_descriptor_base',3,'word',False,False,True),
 (0x42bb20,'thug_component_descriptor_scoped',3,'word',True,True,True),
 (0x500ca0,'thug_physics_construct',0,'word',False,False,True),
 (0x4fc500,'thug_physics_destroy',0,'void',False,False,True),
 (0x500db0,'thug_physics_delete',1,'word',True,False,True),
 (0x505440,'thug_physics_create',0,'word',True,False,False),
 (0x4739a0,'thug_script_set_object_wait',3,'void',False,False,True)]:bind(*row)
LBASE,NEWPHYS,LWAIT,LFRAMES,LDESC,LLOG,LOBJECTS,LVT=0x16d8000,0x16d9000,0x16db000,0x16dc000,0x16dc800,0x16dc900,0x16dd000,0x16dde00
copy(LBASE,bytes(0x6000));put(NEWPHYS+12,'<I',BODIES)
CHECKSUM,MEMBER=0x3f00e00,0x3f00e40
put(LVT+0x30,'<I',CHECKSUM)
fields.update([LBASE,NEWPHYS,LVT+0x30,LDESC+8,PHYS]+[HEAP+j*0x154c for j in range(10)])
exports += [[0x647618,'thug_component_methods'],[0x64bc48,'thug_physics_methods']]
for j in range(8):glob('thug_collision_cache_registry',0x6918ec+4*j,0,offset=j*4)
glob('thug_collision_cache_mask',0x69190c,0)
ranges={0x45d730:16,0x45d740:23,0x45d780:52,0x45d760:29,0x4e3f90:5,0x48dcd0:3,0x5bab90:3,0x45d720:15,0x42bb20:49,0x500ca0:267,0x4fc500:186,0x500db0:33,0x505440:89}
hits=Counter();command_probe_calls=Counter()
def lifecycle_trace(cpu,at,size,user):hits[at]+=1
for at,n in ranges.items():
 oracle.cpu.hook_add(UC_HOOK_CODE,lifecycle_trace,begin=at,end=at+n-1)
 oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
def command_probe(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);self=cpu.reg_read(UC_X86_REG_ECX);n=oracle.word(LLOG);assert n<100
 if at==CHECKSUM:row=[self,oracle.word(sp+4),oracle.word(sp+8),oracle.word(sp+12)];cleanup=12
 else:row=[self,0,oracle.word(sp+4),oracle.word(sp+8)];cleanup=8
 cpu.mem_write(LLOG+32+n*16,struct.pack('<4I',*row));oracle.setword(LLOG,n+1);command_probe_calls[hex(at)]+=1
 cpu.reg_write(UC_X86_REG_EAX,oracle.word(LLOG+4));cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4+cleanup)
for at in [CHECKSUM,MEMBER]:
 oracle.cpu.mem_write(at,b'\xc3');oracle.cpu.hook_add(UC_HOOK_CODE,command_probe,begin=at,end=at)
initial=bytes(memory);oracle.initial=initial
labels=[];oracle.cases.clear();oracle.counts.clear();oracle.coverage.clear()
def test(calls,p=(),changes=None,label='component lifecycle'):
 stages=compare(calls,list(p),changes,label)
 if len(labels)%25==0:print('Component lifecycle cases',len(labels),flush=True)
 return stages
for fill in [0,0xa5,0xff]:
 test([call(0x45d730,LBASE)]*2,[raw(LBASE,bytes([fill])*0x60)],label='base constructor leaves non-owned bytes')
for flags,enabled in itertools.product([0,2,0xfffffffe,0xffffffff],[0,1,255,256,257,0xffffffff]):
 test([call(0x45d760,LBASE,[enabled])]*2,[patch(LBASE+8,'<I',flags)],label='suspend bit and low-byte argument')
for flag,release,length in itertools.product([0,1,2,3,0xffffffff],[0,1,256,257],[0,1,3]):
 p=[patch(LBASE+8,'<I',flag)]
 for j in range(length):
  at=LWAIT+j*0x100;frames=LFRAMES+j*0x100
  p += [patch(at,'<I',at+0x100 if j+1<length else 0),patch(at+0x30,'<I',3),patch(at+0x94,'<I',frames),patch(at+0xa4,'<3I',9,0x12345678,LBASE if j!=1 else NEWPHYS)]
  for k in range(3):p += [patch(frames+k*48+0x18,'<I',[0,LBASE,NEWPHYS][k]),patch(frames+k*48+0x28,'<I',0xabcdffff)]
 test([call(0x45d780,LBASE,[release])],p,{index[0x6f3538]:LWAIT if length else 0},'base deletion and real live/saved wait cleanup')
# Direct destructor and a real wait setter also exercise the constructor-to-wait path.
for owner in [LBASE,NEWPHYS]:
 test([call(0x45d730,LBASE),call(0x4738e0,LWAIT),call(0x4739a0,LWAIT,[9,owner,77]),call(0x45d740,LBASE)],label='real script wait setup before base destruction')
for mask in [0,1,0x7f,0xff,0x100,0xffffffff]:
 for fill in [0,0xa7]:
  p=[raw(NEWPHYS,bytes([fill])*0x153c)]
  test([call(0x500ca0,NEWPHYS),call(0x4fc500,NEWPHYS)],p,{index[0x69190c]:mask},'physics construction and cache registry full/partial')
# Actual zero-allocation factory, including filling all registry slots. Heap
# failure is outside this allocator corpus; its original null branch is retained.
for count,mask in itertools.product([1,2,9],[0,0xff]):
 calls=[call(0x505440,0) for j in range(count)]
 calls += [call(0x500db0,HEAP+j*0x154c,[1]) for j in range(count)]
 stages=test(calls,changes={index[0x69190c]:mask},label='actual zero-allocation physics factory and destruction')
 assert [s['result'] for s in stages[:count]]==[HEAP+j*0x154c for j in range(count)]
 assert oracle.word(0x69190c)==mask
# Three original reference assignment calls attach the probe and skater references.
for mask,split,release in itertools.product(range(8),[False,True],[0,1]):
 calls=[call(0x500ca0,NEWPHYS)]
 for i,offset in enumerate([0x140,0x1f0,0x364]):
  if mask&(1<<i):calls += [call(0x41d1d0,NEWPHYS+offset,[LOBJECTS+i*0x40 if split else LOBJECTS])]
 calls += [call(0x4738e0,LWAIT),call(0x4739a0,LWAIT,[9,NEWPHYS,77]),call(0x500db0,NEWPHYS,[release])]
 test(calls,label='physics destroys all live reference combinations and waits')
for flags in [2,255,256,257,0xffffffff]:
 test([call(0x500ca0,NEWPHYS),call(0x500db0,NEWPHYS,[flags])],label='physics delete low bit')
for value in [0,1,0xffffffff]:
 test([call(0x48dcd0,LBASE,[value,0xdeadbeef]),call(0x5bab90,LBASE,[value])],label='real no-op stack arities')
# Refresh reaches the real concrete virtual initialization slot.
for value in [0.,.125,1e30]:
 b=Build();b.symbol(0x78f80ec4,2,bits(value))
 test([call(0x500ca0,NEWPHYS),call(0x4e3f90,NEWPHYS,[0xdeadbeef])],b.patches()+[patch(BODIES+0xbc,'<B',0)],label='refresh through constructed physics method table')
# Direct descriptor forwarding uses explicit test observation for unknown member
# targets; complete gameplay dispatch cases below use the actual physics handler.
for fn,direct,adjust,result in itertools.product([0x45d720,0x42bb20],[False,True],[-32,0,32],[0,1,0xffffffff]):
 p=[patch(LBASE,'<I',LVT),patch(LDESC,'<4I',0xabcdefff,0x76543210,MEMBER if direct else 0,adjust&0xffffffff),patch(LLOG+4,'<I',result)]
 args=[LDESC,0x12345678,0x23456789]+([QUERY] if fn==0x42bb20 else [])
 test([call(fn,LBASE,args)]*2,p,label='descriptor receiver adjustment, arguments and raw return')
for name in [0,0x315d9ed4,0x8819dd8b]:
 b,request,_,_=config([(0,13,0xd607e2e6),(0,13,0x90a91232)])
 before,body=setup(False,0xbaf9b341)
 p=b.patches()+body+network()+[patch(PHYS,'<I',0x64bc48),patch(PHYS+0x248,'<B',255),patch(LDESC,'<4I',name,0x5bd63b29,0,0),patch(BODIES+0xbc,'<B',0)]
 test(before+[call(0x42bb20,PHYS,[LDESC,request,0,QUERY])]*2,p,label='actual physics virtual command and scoped Motion delegation')
# Base table dispatch is genuinely unhandled, including a nonzero direct field
# that45d720 deliberately ignores.
test([call(0x45d730,LBASE),call(0x45d720,LBASE,[LDESC,0,0])],[patch(LDESC,'<4I',0x8819dd8b,0,MEMBER,0)],label='base table unhandled method')
# Reenter the actual physics descriptor from a camera QB program. Its first
# native observation disables further camera recursion; all movement/reset,
# parameter parsing and component dispatch between callbacks are original code.
for nested_name,keep in itertools.product([0x315d9ed4,0x8819dd8b],[False,True]):
 b,request,_,_=config([(0,13,0xd607e2e6),(0,13,0x90a91232)])
 descriptor=b.alloc(struct.pack('<4I',nested_name,0x5bd63b29,0,0))
 args=(b'\x16'+struct.pack('<I',0xd607e2e6)) if keep else b''
 code=b.alloc(b'\x01\x43'+struct.pack('<I',NATIVE)+b'\x01\x46'+struct.pack('<I',descriptor)+args+b'\x01\x43'+struct.pack('<I',NATIVE)+b'\x01\x24')
 fields.update([code+2,code+14+len(args)])
 name=0x71664443;b.symbol(name,7,code);entry=b.alloc(struct.pack('<5I',name,code,1,0,0));slot=CACHETABLE+32+(name&3)*12
 link=b.alloc(initial[slot-BASE:slot-BASE+12]);b.extra.append(patch(slot,'<3I',name,entry,link))
 before,body=setup(False,0xbaf9b341)
 p=b.patches()+body+network()+[patch(PHYS,'<I',0x64bc48),patch(PHYS+0x248,'<B',1),patch(LDESC,'<4I',0x8819dd8b,0x5bd63b29,0,0),patch(BODIES+0xbc,'<B',1),patch(CAMERA+0x10,'<I',SCRIPTS),patch(GOBS+4,'<4I',BODIES+0xbc,0,1,0)]
 stages=test(before+[call(0x4738e0,SCRIPTS),call(0x474540,SCRIPTS,[name,0,0,BODIES]),call(0x42bb20,PHYS,[LDESC,request,0,QUERY])],p,{index[0x6f0fc0]:CMANAGER},'camera QB reenters the complete physics virtual descriptor')
 assert stages[-1]['callbacks']==2
coverage={};pe=load();md=Cs(CS_ARCH_X86,CS_MODE_32);raw_rows=[]
for at,n in ranges.items():
 rows=list(md.disasm(pe.get_data(at-0x400000,n),at));missing=[hex(i.address) for i in rows if not hits[i.address]]
 coverage[hex(at)]={'total':len(rows),'covered':len(rows)-len(missing),'missing':missing}
 raw_rows += ['\n'+hex(at)]+[f'{i.address:08x} {i.mnemonic:8} {i.op_str}' for i in rows]
(folder/'component-lifecycle-instructions.txt').write_text('\n'.join(raw_rows)+'\n')
scope='Recovered13 original base/physics component lifecycle, factory and dispatch functions, exact13-slot tables with typed host bridges. Real collision-cache registration, three reference links/unlinks, script wait setup/cleanup, virtual physics initialization, node movement/reset and nested camera QB reentry into the physics descriptor. Descriptor probe callbacks only observe forwarding/receiver adjustment; they are test instrumentation. Abstract623771 is an explicit host trap, not a recovered routine. Win32 SEH is host ABI; no exception/unwind injection. Factory allocation failure is outside the successful allocator corpus; the null-result branch is retained. Integrated into the main module and training remains unplayable.'
fixture={'base':BASE,'memory':'component-lifecycle-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'native_qb_callbacks','pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'native_callbacks':[{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE},{'module':'component-command-callbacks.wasm','export':'fixture_component_checksum','original':CHECKSUM},{'module':'component-command-callbacks.wasm','export':'fixture_component_member','original':MEMBER}]}
(folder/'component-lifecycle-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')));(folder/fixture['memory']).write_bytes(initial)
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'counts':dict(oracle.counts),'instruction_coverage':coverage,'callee_coverage':dict(oracle.coverage),'command_probe_calls':dict(command_probe_calls),'scope':scope}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('Original component lifecycle',len(labels),sum(oracle.counts.values()),coverage,flush=True)

subprocess.run([str(ROOT/".tools/wasi-sdk-34.0-arm64-macos/bin/clang"),"--target=wasm32-unknown-unknown","-O2","-nostdlib","-Wl,--no-entry,--import-memory,--export-all,--global-base=58720256",str(ROOT/"tools/component_command_callbacks.c"),"-o",str(folder/"component-command-callbacks.wasm")],check=True)

subprocess.run(['node',str(ROOT/'tools/verify_component_lifecycle_wasm.mjs')],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [folder/'component-lifecycle-fixtures.json',folder/fixture['memory'],folder/'component-command-callbacks.wasm',ROOT/'tools/component_command_callbacks.c',folder/'component-lifecycle-instructions.txt']}
(folder.parent/'component-lifecycle.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS component-lifecycle',report['cases'],sum(oracle.counts.values()))
