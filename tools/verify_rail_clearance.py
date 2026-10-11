"""Rail clearance/side queries against the actual training collision scene."""
from pathlib import Path
prefix=Path('tools/verify_frame_actions.py').read_text().split('# The raw text getter')[0]
prefix=prefix.replace("'frame-actions.json'","'rail-clearance.json'")
probe_file=__file__;__file__=str(Path('tools/verify_frame_actions.py').resolve())
exec(compile(prefix,'<initialized engine graph>','exec'));__file__=probe_file
draft=out;report_path=out.parent/'rail-clearance.json'
RAILS,DIRECTION,CONTEXT=0x16c0000,0x16c0200,0x16c0300
copy(RAILS,bytes(0x1000));put(RAILS+0x40,'<I',RAILS+0x100)
fields.add(RAILS+0x40)
glob('thug_skater_orientation_context',0x7ce5d8,CONTEXT)
bind(0x57c600,'thug_rail_clearance',8,'byte',False,False,False)
functions[hex(0x57c600)]['float_args']=list(range(8))
bind(0x57cc30,'thug_rail_side',1,'word',False,False,True)
for row in [(0x413000,'thug_moving_collision_initialize',1,'word',False,False,True),(0x412f90,'thug_moving_collision_set_position',1,'void',False,False,True),(0x40ae40,'thug_moving_collision_set_owner',1,'void',False,False,True)]:
    bind(*row);oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=row[0],end=row[0])
ranges={0x57c600:1310,0x57cc30:884};hits=Counter();query_counts=Counter()
def trace(cpu,at,size,user):
    hits[at]+=1
    if at in ranges:cpu.mem_write(0x691968,bytes(cpu.mem_read(QUERY,12)))
    if at in [0x57c889,0x57c8e1,0x57cab6,0x57cae3,0x57cb1d,0x57cfa1]:cpu.mem_write(QUERY,bytes(cpu.mem_read(0x691968,12)))
for at,n in ranges.items():
    oracle.cpu.hook_add(UC_HOOK_CODE,trace,begin=at,end=at+n-1)
    oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
initial=bytes(memory);oracle.initial=initial
labels=[];oracle.cases.clear();oracle.counts.clear();oracle.coverage.clear()
def compare(a,b,d=(1.,0,0,1),extra=(),label='training rail',before=()):
    cpu=oracle.cpu;cpu.reg_write(UC_X86_REG_FPSW,0);cpu.reg_write(UC_X86_REG_FPTAG,0xffff);cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
    stages=oracle.case(list(before)+[call(0x57c600,0,[*[bits(v) for v in a+b],QUERY]),call(0x57cc30,RAILS,[DIRECTION,QUERY])],
        [patch(RAILS+0x20,'<4f',*a),patch(RAILS+0x120,'<4f',*b),patch(DIRECTION,'<4f',*d)]+list(extra))
    labels.append(label)
    return stages
for v in [0,0xd443a2bc]:compare([0.,0,0,1],[100.,0,0,1],extra=[patch(CONTEXT+0x40,'<I',v)],label='orientation exemption')
for i in [0,1,2,3,13,24,26,30,34,39,57,70,98,129,278,400,488,510,521,545]:
    q=loader['queries'][i];data=bytes.fromhex(q['result']);normal=struct.unpack_from('<4f',data);point=struct.unpack_from('<4f',data,16)
    for height in [-10.,-6,-2,-1,0,1,2,6,10]:
        for axis in [0,2]:
            center=[point[j]+normal[j]*height for j in range(3)]+[1.]
            a=center[:];b=center[:];a[axis]-=8;b[axis]+=24
            direction=[0.,0,0,1];direction[axis]=[-1.,1.][(i+axis+int(height))%2]
            compare(a,b,direction,label=f'training {i} height {height} axis {axis}')
for i in range(100):
    q=loader['queries'][i*5];point=struct.unpack_from('<4f',bytes.fromhex(q['result']),16)
    a=[point[j]+rng.uniform(-12,12) for j in range(3)]+[1.]
    b=[a[j]+rng.uniform(-24,24) for j in range(3)]+[1.]
    compare(a,b,[rng.uniform(-1,1) for _ in range(4)],label='random local training segment')
for length in [0.,1e-40,1e-10,1,1e5,1e30]:
    compare([0.,0,0,1],[length,0,length,1],label='zero and extreme horizontal segment lengths')
# Relocate actual training collision objects with their original constructors.
# The side/clearance parents must attach and release a real moving reference.
for i in [0,1,3,13,30,34,39,46,70,129]:
    data=bytes.fromhex(loader['queries'][i]['result']);point=struct.unpack_from('<4f',data,16)
    instance=struct.unpack_from('<I',data,0x30)[0];geometry=struct.unpack_from('<I',initial,instance+12-BASE)[0]
    target=[50000.,20000,50000];position=RAILS+0x500;owner=RAILS+0x600
    p=[patch(position,'<4f',*[target[k]-point[k] for k in range(3)],0),patch(COLL_NODES,'<8I',0,RUNTIME,0,COLL_NODES+16,0,0xffffffff,0,COLL_NODES+16),patch(owner+0x14,'<I',0x12345678)]
    before=[call(0x413000,RUNTIME,[geometry]),call(0x412f90,RUNTIME,[position]),call(0x40ae40,RUNTIME,[owner])]
    for angle,height in itertools.product([0,math.pi/4,math.pi/2,math.pi,3*math.pi/2],[-8.,-3,0,3,8]):
        direction=[math.cos(angle),0,math.sin(angle),0]
        a=[target[j]-8*direction[j] for j in range(3)]+[1.];b=[target[j]+24*direction[j] for j in range(3)]+[1.]
        a[1]+=height;b[1]+=height
        compare(a,b,direction,p,label=f'moving training object {i} angle {angle} height {height}',before=before)
for i in [13,30,34,39,129,278]:
    data=bytes.fromhex(loader['queries'][i]['result']);point=struct.unpack_from('<4f',data,16)
    for angle,height in itertools.product([math.pi/4,3*math.pi/4,5*math.pi/4,7*math.pi/4],[-3.,-1.5,0,1.5,3]):
        direction=[math.cos(angle),0,math.sin(angle),0]
        a=[point[j]-8*direction[j] for j in range(3)]+[1.];b=[point[j]+24*direction[j] for j in range(3)]+[1.]
        a[1]+=height;b[1]+=height
        compare(a,b,direction,label='diagonal rail over uneven support heights')
for angle,height in itertools.product([.08,.1,.12,.15,.2,.25,.3,.4],[-1.,0,1.]):
    data=bytes.fromhex(loader['queries'][34]['result']);point=struct.unpack_from('<4f',data,16)
    direction=[math.cos(angle),0,math.sin(angle),0]
    a=[point[j]-8*direction[j] for j in range(3)]+[1.];b=[point[j]+24*direction[j] for j in range(3)]+[1.]
    a[1]+=height;b[1]+=height
    compare(a,b,direction,label='shallow crossing angle straddles support-height thresholds')
coverage={};pe=load();md=Cs(CS_ARCH_X86,CS_MODE_32)
for at,n in ranges.items():
    ins=list(md.disasm(pe.get_data(at-0x400000,n),at));missing=[hex(i.address) for i in ins if not hits[i.address]]
    coverage[hex(at)]={'total':len(ins),'covered':len(ins)-len(missing),'missing':missing}
assert coverage['0x57c600']['missing']==['0x57cafa','0x57cb01','0x57cb02'],coverage
assert coverage['0x57cc30']['missing']==[],coverage
scope='Recovered rail clearance57c600 and side57cc30 with original static and relocated moving training scene queries and query-state copy-in/out. No collision responses are replaced. Integrated into the main module; the complete playable level remains unfinished.'
fixture={'base':BASE,'memory':'rail-clearance-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'native_callbacks':[{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]}
path=draft/'rail-clearance-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(draft/fixture['memory']).write_bytes(initial)
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'instruction_coverage':coverage,'scope':scope}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('Original rail clearance',len(labels),coverage,flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_rail_clearance_wasm.mjs')],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory']]}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS rail clearance',len(labels),sum(oracle.counts.values()))
