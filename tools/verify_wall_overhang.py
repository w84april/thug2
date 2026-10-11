"""Complete rotation and wall-overhang queries through original training geometry."""
from pathlib import Path
prefix=Path('tools/verify_frame_actions.py').read_text().split('# The raw text getter')[0]
prefix=prefix.replace("'frame-actions.json'","'wall-overhang.json'")
probe_file=__file__;__file__=str(Path('tools/verify_frame_actions.py').resolve())
exec(compile(prefix,'<initialized skater graph>','exec'));__file__=probe_file
draft=out;report_path=out.parent/'wall-overhang.json'
VECTOR,AXIS=0x16b0000,0x16b0100
copy(VECTOR,bytes(0x200));put(VECTOR,'<4f',10,20,30,1);put(AXIS,'<4f',0,1,0,0)
bind(0x421440,'thug_vector_rotate_axis',2,'word');functions['0x421440']['float_args']=[1]
bind(0x5051b0,'thug_skater_wall_overhang',result='byte')
ranges={0x421440:71,0x5051b0:651};hits=Counter()
def trace(cpu,at,size,user):
    hits[at]+=1
    if at==0x5051b0 and oracle.word(cpu.reg_read(UC_X86_REG_ESP))==oracle.stop:cpu.mem_write(0x691968,bytes(cpu.mem_read(QUERY,12)))
    if at in [0x505433,0x50543a]:cpu.mem_write(QUERY,bytes(cpu.mem_read(0x691968,12)))
for at,n in ranges.items():
    oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
    oracle.cpu.hook_add(UC_HOOK_CODE,trace,begin=at,end=at+n-1)
initial=bytes(memory);oracle.initial=initial
labels=[];oracle.cases.clear();oracle.counts.clear();oracle.coverage.clear()
def compare(fn,this,args=(),p=(),b=None,label='overhang',floats=()):
    cpu=oracle.cpu;cpu.reg_write(UC_X86_REG_FPSW,0);cpu.reg_write(UC_X86_REG_FPTAG,0xffff);cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
    result=oracle.case([call(fn,this,args)],(b or grounded_config()).patches()+list(p))[-1]
    labels.append(label);result['float_fields']=list(floats);return result
for axis,angle,alias in itertools.product([[0,1,0,0],[1,0,0,0],[0,0,1,0],[.2,.3,.5,1],[0,0,0,0]],[-3.14,0.,-0.,.2,1.,3.14,math.nan],[False,True]):
    compare(0x421440,VECTOR,[VECTOR if alias else AXIS,bits(angle)],
        [patch(AXIS,'<4f',*axis)],label='in-place axis rotation with aliased axis',floats=range(VECTOR,VECTOR+16,4))
computed=[BODIES+o for o in range(0x4c,0xbc,4)]+[PHYS+o for o in range(0x208,0x228,4)]
def overhang(p=(),height=96.,label='overhang'):
    b=grounded_config();b.symbol(0x542cf0c7,1 if isinstance(height,int) else 2,height&0xffffffff if isinstance(height,int) else bits(height))
    return compare(0x5051b0,PHYS,[QUERY],p,b,label,computed)
for height in [-100,0,10,96,1000,math.nan]:overhang(height=height,label='clear-space, zero, reverse and unordered scan height')
selected=[(i,q) for i,q in enumerate(loader['queries']) if q['returned'] and struct.unpack_from('<f',bytes.fromhex(q['result']),4)[0]<-.1]
for i,q in selected:
    data=bytes.fromhex(q['result']);normal=struct.unpack_from('<4f',data);point=struct.unpack_from('<4f',data,16)
    for direction in [[0,0,0,0],[1,0,0,0],[-1,0,0,0],[0,0,1,0],[0,0,-1,0]]:
        position=[point[j]-direction[j]*18-(48 if j==1 else 0) for j in range(3)]+[1]
        overhang([patch(BODIES+0x4c,'<4f',*position),patch(BODIES+0xac,'<4f',100,50,25,0),patch(PHYS+0x38c,'<4f',*direction)],label=f'training overhead face {i} direction {direction}')
for i,q in [(i,q) for i,q in enumerate(loader['queries']) if q['returned'] and struct.unpack_from('<f',bytes.fromhex(q['result']),4)[0]>.1][:12]:
    point=struct.unpack_from('<4f',bytes.fromhex(q['result']),16)
    position=[point[0],point[1]+48,point[2],1]
    overhang([patch(BODIES+0x4c,'<4f',*position),patch(PHYS+0x38c,'<4f',0,0,0,0)],height=-96.,label='upward normal rejects floor collision')
for value in [0.,-0.,1e-40,1e30,math.inf,-math.inf,math.nan]:
    overhang([patch(PHYS+0x38c,'<4f',value,value,value,0)],label='initial wall-normal offset numeric boundaries')
for height in [-2147483648,16777217,2147483647]:
    overhang(height=height,label='integer scan height retains precision through the addition')
coverage={};pe=load();md=Cs(CS_ARCH_X86,CS_MODE_32)
for at,n in ranges.items():
    ins=list(md.disasm(pe.get_data(at-0x400000,n),at));missing=[hex(i.address) for i in ins if not hits[i.address]]
    coverage[hex(at)]={'total':len(ins),'covered':len(ins)-len(missing),'missing':missing}
    assert not missing,(hex(at),missing)
scope='Complete rotation421440 and overhang5051b0; actual quaternion math and original static training queries with full projected correction/velocity. Coverage recorded explicitly; integrated into the main module; full dispatcher and playable level remain unfinished. Computed NaNs classify; other defined bytes compare exactly.'
fixture={'base':BASE,'memory':'wall-overhang-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'native_callbacks':[{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]}
path=draft/'wall-overhang-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(draft/fixture['memory']).write_bytes(initial)
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'instruction_coverage':coverage,'scope':scope}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('Original wall-overhang',len(labels),coverage,flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_wall_overhang_wasm.mjs')],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory']]}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS wall-overhang',len(labels),sum(oracle.counts.values()))
