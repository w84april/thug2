"""Pending trick resolution, object script setup and actual QB execution."""
from pathlib import Path
prefix=Path('tools/verify_grind_script.py').read_text().split('for category in [')[0]
prefix=prefix.replace('grind-script.json','pending-trick.json')
exec(compile(prefix,'<grind script prerequisites>','exec'))
bind(0x461350,'thug_object_set_script',2,'word',True,True,True)
bind(0x522e80,'thug_skater_run_pending_trick',4,'byte',True,True,True)
TRICK=0x16f2000;copy(TRICK,bytes(0x1400));put(TRICK+12,'<I',BODIES)
put(TRICK+0x28,'<3I',PHYS,FLIP,SKATER_STATE)
fields.update([TRICK+12,TRICK+0x28,TRICK+0x2c,TRICK+0x30,TRICK+0xa28])
initial=bytes(memory);oracle.initial=initial
ranges={0x461350:182,0x522e80:601};parent_hits=Counter()
def parent_trace(cpu,at,size,user):parent_hits[at]+=1
for at,n in ranges.items():
 oracle.cpu.hook_add(UC_HOOK_CODE,parent_trace,begin=at,end=at+n-1)
 oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
labels=[];oracle.cases.clear();oracle.counts.clear();oracle.coverage.clear()
def normalized_crc(data):
 value=0xffffffff
 for ch in data:
  if 65<=ch<=90:ch+=32
  if ch==47:ch=92
  value^=ch
  for _ in range(8):value=(value>>1)^ (0xedb88320 if value&1 else 0)
 return value
def compare(calls,p,changes=None,label='pending trick'):
 cpu=oracle.cpu;cpu.reg_write(UC_X86_REG_FPSW,0);cpu.reg_write(UC_X86_REG_FPTAG,0xffff);cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
 stages=oracle.case(calls,p,changes);labels.append(label);previous=0
 for step in stages:
  current=previous
  for at,data in step['outputs']:
   if at<=GOBS<at+len(data)//2:current=int.from_bytes(bytes.fromhex(data)[GOBS-at:GOBS-at+4],'little')
  step['callbacks']=current-previous;previous=current
 return stages
def setup(existing,bodytype):
 p=[raw(BODIES,body_base),patch(BODIES+0x10,'<I',SCRIPTS if existing else 0),patch(BODIES+0x18,'<I',bodytype)]
 calls=body_setup()[1:]+([call(0x4738e0,SCRIPTS)] if existing else [])
 return calls,p
def pending(mode='scripts',flags=(0,0,0,0),entryindex=1,one=False,existing=False,count=0,bodytype=0xbaf9b341,prefix_text=b'Air_',suffix_null=False,pending_flags=(0,0,0),extra=(),present=1,missing=False,params=True,pool=0):
 b=Build();mask=sum((int(v)&255!=0)<<j for j,v in enumerate(flags));selected=0 if one else mask
 suffixes=[None if suffix_null else ('Trick%d'%j).encode() for j in range(1 if one else 16)]
 names=[0x71220000+j for j in range(1 if one else 16)]
 scripts=b.array(13,names);template=b.array(3,[0 if s is None else b.text(s) for s in suffixes])
 meta=[]
 if mode in ['scripts','both','slot-scripts']:meta.append((0x22e168c1,12,scripts))
 if mode in ['template','both','slot-template']:meta.append((0x689fe07c,12,template))
 if prefix_text is not None:meta.append((0x6c4e7971,3,b.text(prefix_text)))
 original_params=b.structure([(0x12345678,1,0x87654321),(0x23456789,3,b.text(b'original trick params'))])
 if mode.startswith('slot-'):
  # Replacement has deliberately different Params; the caller retains the
  # originally selected entry for the eventual argument copy.
  replacement=b.structure(meta+[(0x7031f10c,10,b.structure([(0x12345678,1,77)]))]);b.symbol(0x73440000,10,replacement)
  meta=[(0xa92a2280,13,0x73441111)]
  if prefix_text is not None:meta.append((0x6c4e7971,3,b.text(b'Overridden_')))
 else:replacement=0
 if params:meta.append((0x7031f10c,10,original_params))
 entry=b.structure(meta);entries=[entry]*(1 if one else 3)
 if not missing:b.symbol(0x73442222,12,b.array(10,entries))
 mapping=b.structure([(0x73441111,13,0x73440000)])
 chosen=names[selected] if mode in ['scripts','both','slot-scripts'] else normalized_crc((prefix_text if prefix_text is not None else b'(null)')+(suffixes[selected] if suffixes[selected] is not None else b'(null)'))
 program(b,chosen)
 calls,p=setup(existing,bodytype)
 p=b.patches()+network()+p+[patch(TRICK+0xa28,'<I',mapping),patch(TRICK+0x12b0,'<B',present),patch(TRICK+0x12b4,'<2I',0x73442222,entryindex),patch(TRICK+0x12c4,'<B',177),patch(TRICK+0xa24,'<B',33),patch(TRICK+0x13ac,'<I',count),patch(PHYS+0x3a8,'<I',0xdeadbeef),patch(FLIP+0x19,'<3B',*pending_flags),patch(SKATER_STATE+0xe0,'<B',0)]+list(extra)
 changes={index[0x6f3548]:pool-1,index[0x6f3550+4*(pool-1)]:SCRIPT_POOL} if pool else {}
 stages=compare(calls+[call(0x522e80,TRICK,list(flags))]*2,p,changes,label=mode)
 assert stages[-2]['result']==int(bool(present) and not missing)
 assert stages[-1]['result']==0
 if present and not missing:assert oracle.word(GOBS+64)==chosen,(mode,hex(chosen),hex(oracle.word(GOBS+64)))
for mode,mask in itertools.product(['scripts','template','both','slot-scripts','slot-template'],range(16)):
 pending(mode,[(1 if mask&(1<<j) else 0) for j in range(4)],existing=bool(mask&1),params=bool(mask&2))
for mode,one in itertools.product(['scripts','template','slot-template'],[False,True]):
 for flags in [(256,257,255,0xffffffff),(0,0,0,0),(1,1,1,1)]:pending(mode,flags,one=one,entryindex=999 if one else 2)
for prefix_text,suffix_null in itertools.product([b'',b'Air/',None,b'x'*88],[False,True]):
 pending('template',[0,1,0,0],prefix_text=prefix_text,suffix_null=suffix_null)
for count,bodytype in itertools.product([0,2,3,4,0x7fffffff,0x80000000,0xfffffffe,0xffffffff],[0xbaf9b341,0x12345678]):pending(count=count,bodytype=bodytype)
for present,missing in itertools.product([0,1,255],[False,True]):pending(present=present,missing=missing)
for flags in itertools.product([0,1],repeat=3):pending(pending_flags=flags)
for target,value,width in [(SKATER_STATE+0xe0,0,1),(TRICK+0x30,SKATER_STATE2,4),(TRICK+0x13ac,4,4),(TRICK+0xa24,17,1),(TRICK+0x12b0,0,1)]:
 pending(extra=[patch(GOBS+4,'<4I',target,value,width,0)])
for pool,existing in itertools.product([1,2],[False,True]):pending(pool=pool,existing=existing)
# Direct wrapper calls cover its result and repeated setup on the same object.
for existing,pool,params in itertools.product([False,True],[0,1,2],[False,True]):
 b=Build();name=0x73445555;program(b,name);argument=b.structure([(0x12345678,1,5)]) if params else 0
 calls,p=setup(existing,0xbaf9b341)
 changes={index[0x6f3548]:pool-1,index[0x6f3550+4*(pool-1)]:SCRIPT_POOL} if pool else {}
 compare(calls+[call(0x461350,BODIES,[name,argument])]*2,b.patches()+p,changes,'object script repeated setup')
coverage={};pe=load();md=Cs(CS_ARCH_X86,CS_MODE_32);raw=[]
for at,n in ranges.items():
 ins=list(md.disasm(pe.get_data(at-0x400000,n),at));missing=[hex(i.address) for i in ins if not parent_hits[i.address]]
 coverage[hex(at)]={'total':len(ins),'covered':len(ins)-len(missing),'missing':missing};raw+=['\n'+hex(at)]+[f'{i.address:08x} {i.mnemonic:8} {i.op_str}' for i in ins]
assert coverage['0x461350']['missing']==['0x461398','0x4613ca'],coverage
assert not coverage['0x522e80']['missing'],coverage
(draft/'pending-trick-instructions.txt').write_text('\n'.join(raw)+'\n')
scope='Two recovered routines: object script setup461350 and complete pending-trick startup522e80. Actual arrays, slot replacement, fixed %s%s CRT/CRC naming, original-entry Params, pending flips, QB execution, live state and counter-wrap broadcast. Valid loaded metadata and names within100bytes; successful allocation and initialized host memory. Integrated into the main module; the complete playable level remains unfinished.'
fixture={'base':BASE,'memory':'pending-trick-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'native_qb_callbacks','pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'native_callbacks':[{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]}
(draft/'pending-trick-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')));(draft/fixture['memory']).write_bytes(initial)
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'instruction_coverage':coverage,'native_qb_calls':dict(qb_calls),'scope':scope}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('Original pending trick',len(labels),coverage,flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_pending_trick_wasm.mjs')],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [draft/'pending-trick-fixtures.json',draft/fixture['memory']]}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS pending trick',len(labels),sum(oracle.counts.values()))
