"""Original index allocation/upload and material iteration, with explicit ports."""
from pathlib import Path
source=Path('local/analysis/probe-texture-buffer.py').read_text().split('for fill in [0,0xa5,0xff]:')[0]
exec(compile(source,'<pinned heap/GPU setup>','exec'))
functions.clear();code.clear();hits.clear();oracle.counts.clear();oracle.coverage.clear()
CRTCTX,CRTBEGIN,CRTLIMIT,CRTLOG=BASE+0x13000,BASE+0x120000,BASE+0x160000,BASE+0x1d000
INDEXCTL,INDEXLOG,INDEXVT,INDEXDEV=BASE+0x18000,BASE+0x19000,BASE+0x1c000,BASE+0x160000
exec(compile((folder/'mesh-index-ports-setup.py').read_text(),'<explicit separate CRT and GPU index ports>','exec'))
REG=len(globals_);globals_.append(['thug_mesh_index_registry',0x7865e8,4]);defaults.append(0)
initial=bytes(memory);oracle.initial=initial
specs=[(0x4d4270,118,'thug_mesh_index_buffer_construct_draft',3,'word'),
 (0x4d4300,69,'thug_mesh_index_buffer_upload_draft',0,'word'),
 (0x4de420,104,'thug_mesh_find_material_draft',1,'word')]
for a,n,name,argc,result in specs:
 functions[hex(a)]={'name':name,'this':True,'result':result,'cleanup':argc*4,'memory':False}
 code[a]=list(md.disasm(pe.get_data(a-0x400000,n),a));oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:hits.update([at]),begin=a,end=a+n-1)
# Include complete extents, not Ghidra's body-byte totals excluding alignment.
instructions=[]
for a,n in [(0x4c6650,1216),(0x4d5cc0,1054),(0x4d4270,118),(0x4d4300,69),(0x4de420,104)]:
 instructions += [f'FUNCTION {a:08x} {n} bytes']+[f'{i.address:08x} {i.mnemonic} {i.op_str}' for i in md.disasm(pe.get_data(a-0x400000,n),a)]
(folder/'mesh-index-instructions.txt').write_text('\n'.join(instructions)+'\n')
def run_case(g,calls,label,registry=0):
 defaults[REG]=registry;return run(g,calls,label)
for size in [0,1,2,3,4,5,16,272,4097]:
 for usage in [0,8,0x12345678,0xffffffff]:
  g=Graph();run_case(g,[call(0x4d4270,P,[size,usage,0x65]),call(0x4d4270,P+24,[size,usage,0x12345678])],f'index sizes{size}/usage{usage:x}')
for fill in [0,0xa5,0xff]:
 for result,output in [(0,1),(1,1),(0xffffffff,1),(0x80000000,0)]:
  g=Graph();g.data[P-BASE:P-BASE+24]=bytes([fill])*24;g.put(INDEXCTL+8,'<I',result);g.put(INDEXCTL+20,'<I',output)
  head=g.alloc(12);g.put(head,'<3I',P+512,0,0)
  run_case(g,[call(0x4d4270,P,[19,0xabcd,0xef01])],f'constructor fill{fill}/HRESULT{result:x}/output{output}',registry=head)
for size in [0,1,2,3,4,5,17,272]:
 for lock in [0,1,0xffffffff,0x80000000]:
  g=Graph();data=g.alloc(size+20);g.data[data-BASE:data-BASE+size]=bytes((i*19+7)&255 for i in range(size))
  g.put(P,'<6I',size,0,0,INDEXDEV,data,0xdeadbeef);g.put(INDEXDEV,'<I',INDEXVT)
  g.put(INDEXCTL+12,'<2I',lock,0x87654321);g.put(INDEXCTL+24,'<I',int(lock<0x80000000))
  run_case(g,[call(0x4d4300,P)]*2,f'upload size{size}/lock{lock:x}')
# Forward word-copy semantics when host output and CPU storage overlap.
for offset in [-4,-1,0,1,2,4]:
 g=Graph();data=INDEXDEV+0x100;g.data[data-BASE-8:data-BASE+40]=bytes(range(48));g.put(INDEXDEV,'<I',INDEXVT)
 g.put(P,'<6I',17,0,0,INDEXDEV,data,0);g.put(INDEXCTL+28,'<I',offset&0xffffffff)
 run_case(g,[call(0x4d4300,P)],f'overlap forward word copy{offset}')
for chain in [False,True]:
 for mode in ['missing','first','last','different-table-key','null-first','empty','no-buckets','no-table']:
  g=Graph();rows=[]
  for i,key in enumerate([1,5,9]):
   value=g.alloc(16);g.put(value,'<I',key+100 if mode=='different-table-key' else key)
   rows.append((key,0 if mode=='null-first' and i==0 else value))
  table=g.table([] if mode=='empty' else rows,chain=chain)
  if mode=='no-buckets':g.put(table+4,'<I',0)
  g.put(P+0x18,'<I',0 if mode=='no-table' else table)
  key={'first':1,'last':9,'different-table-key':105}.get(mode,0x7777)
  run_case(g,[call(0x4de420,P,[key])]*2,f'material scan{mode}/chain{chain}')
coverage={hex(a):{'total':len(c),'covered':sum(bool(hits[i.address]) for i in c),'missing':[hex(i.address) for i in c if not hits[i.address]]} for a,c in code.items()}
print('COVERAGE',json.dumps(coverage),flush=True)
scope='Three complete original routines: index buffer construction with separate CRT allocations and linked registry, GPU lock/copy/unlock including HRESULT failures and overlap, and material-value iteration. Host CRT/GPU providers are explicit comparison boundaries. No vertex loader, complete mesh parser or rendering is substituted.'
fixture={'base':BASE,'memory':'mesh-index-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'texture-buffer-ports.wasm','memory_exports':['fixture_texture_allocate','fixture_values_release','fixture_values_scope'],
 'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'pointer_fields':sorted(fields),'pointer_exports':exports,
 'pointer_initializers':[['thug_mesh_crt_allocate_draft',0x624031,0]],
 'native_callbacks':[{'module':'mesh-index-ports.wasm','export':'fixture_mesh_crt_allocate','original':0x624031}]+[{'module':'mesh-index-ports.wasm','export':'fixture_index_'+n,'slots':[slot]} for n,slot in [('create',DVT+0x6c),('lock',INDEXVT+0x2c),('unlock',INDEXVT+0x30)]],'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'mesh-index-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(oracle.counts.values()),'instruction_coverage':coverage,'index_calls':dict(index_calls),'crt_calls':dict(crt_calls),'scope':scope}
(folder/'mesh-index-original.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
