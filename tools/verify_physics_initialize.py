import subprocess
"""Isolated initialization/linking evidence; main checkpoint stays unchanged."""
from pathlib import Path
prefix=Path('tools/verify_pending_trick.py').read_text().split('for mode,mask in ')[0]
prefix=prefix.replace('pending-trick.json','physics-initialize.json')
exec(compile(prefix,'<real physics parameter and object graph>','exec'))
folder=ROOT/'local/validation/collision';report_path=folder.parent/'physics-initialize.json'
bind(0x4fc5c0,'thug_skater_initialize_physics',1,'void')
bind(0x4fc690,'thug_skater_link_physics',0,'void')
ranges={0x4fc5c0:206,0x4fc690:233};hits=Counter()
def trace(cpu,at,size,user):hits[at]+=1
for at,n in ranges.items():
 oracle.cpu.hook_add(UC_HOOK_CODE,trace,begin=at,end=at+n-1)
 oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
initial=bytes(memory);oracle.initial=initial
labels=[];oracle.cases.clear();oracle.counts.clear();oracle.coverage.clear()
sets=[(0,0x8cbc89dd),(0x3029fb1f,0x8b3b782b),(0x61c62b2d,0x05716042),(0x86929898,0x8711bc92),(0xb2c99bf0,0x871ffb73),(0x906f06e2,0x43da544e),(0xd8d2d646,0x08c9ad5e),(0x14a3a4cf,0xd3d12913)]
for index_,(mode,set_) in enumerate(sets):
 for enabled,fallback in [(0,0),(1,0),(255,1)]:
  b=Build();b.symbol(0x78f80ec4,1,33)
  value=0x3e4ccccd+index_*1000
  b.symbol(set_,10,b.structure([(0x78f80ec4,2,value)]))
  p=b.patches()+[raw(PHYS,bytes([0xa7])*0x153c),patch(PHYS+4,'<I',0x5bd63b29),patch(PHYS+12,'<2I',BODIES,0),patch(BODIES+0x100,'<I',PHYS),patch(BODIES+0xbc,'<B',enabled),patch(PHYS+0x2ed,'<B',bool(mode)),patch(PHYS+0x2f0,'<I',mode),patch(PHYS+0x302,'<B',fallback)]
  compare([call(0x4fc5c0,PHYS,[0])]*2,p,label='parameter selection and repeated initialization')
# Integer fallback and float payloads preserve the exact original float store.
for kind in [1,2]:
 for value in [0,1,0xffffffff,0x80000000,0x7fffffff,0x3f800000,0x00000001,0x7f800000,0xff800000,0x7fc12345]:
  b=Build();b.symbol(0x78f80ec4,kind,value)
  compare([call(0x4fc5c0,PHYS,[0xdeadbeef])],b.patches()+[patch(BODIES+0xbc,'<B',0)],label='global fallback numeric bits')
# The real matrix-copy routine preserves its original forward-copy semantics.
for body in [PHYS,PHYS+0x40,PHYS+0x100,PHYS+0x400]:
 b=Build();b.symbol(0x78f80ec4,2,bits(.5))
 p=b.patches()+[patch(PHYS+12,'<I',body),patch(body+0xbc,'<B',0)]
 compare([call(0x4fc5c0,PHYS,[0])],p,label='owner/component memory alias')
types=[0x27d7cd28,0x187574fa,0xe594f0a2,0x270f56e1,0x52d61a0d,0xd262802f,0x589e5fb3,0x43686585,0x408d2aa9,0xd9151d4d,0x726e85aa,0x380d909a]
nodes=0x16e8000
for absent in [-1,*range(12),12]:
 for reverse in [False,True]:
  selected=[] if absent==12 else [t for i,t in enumerate(types) if i!=absent]
  if reverse:selected.reverse()
  # Wrong types before/between matches and duplicate matches after the first.
  entries=[0x12345678]+[v for t in selected for v in [t,0x87654321,t]]
  p=[patch(BODIES+0x100,'<I',nodes),raw(PHYS+0x150c,b'\xa7'*48)]
  for i,t in enumerate(entries):
   at=nodes+i*0x20;next_=at+0x20 if i+1<len(entries) else 0
   p.append(patch(at,'<5I',0,t,0,BODIES,next_))
  compare([call(0x4fc690,PHYS)]*2,p,label='missing/reordered/duplicate component links')
compare([call(0x4fc690,PHYS)],[patch(BODIES+0x100,'<I',0)],label='empty component list')
coverage={};pe=load();md=Cs(CS_ARCH_X86,CS_MODE_32)
for at,n in ranges.items():
 rows=list(md.disasm(pe.get_data(at-0x400000,n),at));missing=[hex(i.address) for i in rows if not hits[i.address]]
 coverage[hex(at)]={'total':len(rows),'covered':len(rows)-len(missing),'missing':missing}
scope='Complete004fc5c0 physics initialization and004fc690 component linking with actual parameter selection, numeric reads, matrix copying and linked-component lookups. Full game integration remains unfinished.'
fixture={'base':BASE,'memory':'physics-initialize-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'native_qb_callbacks','pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'native_callbacks':[{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]}
(folder/'physics-initialize-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')));(folder/fixture['memory']).write_bytes(initial)
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'counts':dict(oracle.counts),'instruction_coverage':coverage,'callee_coverage':dict(oracle.coverage),'scope':scope}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('Original physics initialization',len(labels),coverage,flush=True)

subprocess.run(['node',str(ROOT/'tools/verify_physics_initialize_wasm.mjs')],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [folder/'physics-initialize-fixtures.json',folder/fixture['memory']]}
(folder.parent/'physics-initialize.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS physics-initialize',report['cases'],sum(oracle.counts.values()))
