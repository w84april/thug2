"""Original original rail-transition eligibility and endpoint transform checks."""
from pathlib import Path
prefix=Path('tools/verify_frame_actions.py').read_text().split('# The raw text getter')[0]
prefix=prefix.replace("'frame-actions.json'","'rail-gate.json'")
probe_file=__file__;__file__=str(Path('tools/verify_frame_actions.py').resolve())
exec(compile(prefix,'<initialized skater graph>','exec'));__file__=probe_file
draft=out;report_path=out.parent/'rail-gate.json'
RAIL_TRANSFORM,RAILS,RAIL_OUT=0x16a0000,0x16a1000,0x16a1800
copy(RAIL_TRANSFORM,bytes(0x3000));put(RAIL_TRANSFORM,'<16f',*identity)
orientation_context=0x16a1900
glob('thug_skater_orientation_context',0x7ce5d8,orientation_context)
put(orientation_context+0x40,'<I',0)
for i in range(4):put(RAILS+i*0x100+0x20,'<4f',i*20,0,0,1)
put(RAILS+0x40,'<2I',RAILS+0x100,0);put(RAILS+0x240,'<2I',RAILS+0x300,0)
put(PHYS+0x22c,'<5I',RAILS,RAIL_TRANSFORM,0,0,100)
put(SKATER_STATE+0x50,'<B3sI',0,b'abc',123)
for row in [(0x57cb60,'thug_rail_point',2,'word',False,False,True),
            (0x500020,'thug_skater_rail_eligible',3,'byte',False,False,True)]:
    bind(*row);oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=row[0],end=row[0])
hits=Counter();ranges={0x57cb60:101,0x500020:675}
def trace(cpu,at,size,user):hits[at]+=1
for at,length in ranges.items():oracle.cpu.hook_add(UC_HOOK_CODE,trace,begin=at,end=at+length-1)
initial=bytes(memory);oracle.initial=initial
labels=[];oracle.cases.clear();oracle.counts.clear();oracle.coverage.clear()
def run(at,this,args,p=(),changes=None,label='rail gate',floats=()):
    cpu=oracle.cpu;cpu.reg_write(UC_X86_REG_FPSW,0);cpu.reg_write(UC_X86_REG_FPTAG,0xffff);cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
    stages=oracle.case([call(at,this,args)],p,{index[k]:v for k,v in (changes or {}).items()});labels.append(label)
    for step in stages:step['float_fields']=list(floats)
    return stages[-1]
for transformed,offset in itertools.product([0,1,255],[None,0,4,8,12]):
    destination=RAIL_OUT if offset is None else RAILS+0x20+offset
    p=[patch(RAIL_TRANSFORM+0x50,'<B',transformed),patch(RAIL_TRANSFORM+0x30,'<4f',10,20,30,1),patch(RAILS+0x20,'<4I',0x7fa12345,bits(2),bits(3),bits(1))]
    run(0x57cb60,RAIL_TRANSFORM,[destination,RAILS],p,label='rail point raw/affine path with overlap',floats=range(destination,destination+16,4) if transformed else [])
for mode,transfer,d0,previous in itertools.product([0,1,4],[0,1],[0,1],[0,RAILS,RAILS+0x200,RAILS+0x300]):
    p=[patch(SKATER_STATE+0x18,'<I',mode),patch(SKATER_STATE+0xa8,'<B',transfer),patch(SKATER_STATE+0xd0,'<B',d0),patch(PHYS+0x22c,'<I',previous)]
    run(0x500020,PHYS,[RAILS+0x200,0xdeadbeef,0],p,label='rail state and adjacency gates')
for previous_next,candidate_next,identifier in itertools.product([0,RAILS+0x100],[0,RAILS+0x300],[0,0xd443a2bc]):
    p=[patch(RAILS+0x40,'<I',previous_next),patch(RAILS+0x240,'<I',candidate_next),patch(orientation_context+0x40,'<I',identifier)]
    run(0x500020,PHYS,[RAILS+0x200,0,1],p,label='missing endpoint and orientation-mode gate')
for pair,distance,transformed in itertools.product(range(4),[0.,5.999,6.,6.001,100.,math.nan,math.inf],[0,1]):
    # Choose exactly one of the four endpoint pairs near the acceptance bound.
    positions=[[-1000.,0,0,1],[1000.,0,0,1],[0,1000.,0,1],[0,-1000.,0,1]]
    old,candidate=divmod(pair,2);positions[2+candidate]=[positions[old][0]+distance,0,0,1]
    p=[patch(RAILS+i*0x100+0x20,'<4f',*pos) for i,pos in enumerate(positions)]+[patch(RAIL_TRANSFORM+0x50,'<B',transformed)]
    run(0x500020,PHYS,[RAILS+0x200,0,0],p,label='each transformed endpoint distance and strict six-unit bound')
for flag,age,delay,force in itertools.product([0,1,255],[0,100,101,0x80000000,0xffffffff],[100,0xffffffff],[0,1,0x100]):
    p=[patch(PHYS+0x22c,'<I',RAILS+0x200),patch(SKATER_STATE+0x50,'<B',flag),patch(PHYS+0x234,'<I',(1666-age)&0xffffffff),patch(PHYS+0x23c,'<I',delay)]
    run(0x500020,PHYS,[RAILS+0x200,7,force],p,label='unsigned rail retry age and low-byte force')
for mode,transition,velocity in itertools.product([0,1,4],[0,1],[0.,-0.,1.,-1.,math.nan,math.inf]):
    p=[patch(PHYS+0x22c,'<I',0),patch(SKATER_STATE+0x18,'<I',mode),patch(SKATER_STATE+0x38,'<B',transition),patch(BODIES+0xb0,'<f',velocity)]
    run(0x500020,PHYS,[RAILS+0x200,0,0],p,label='late state, transition and ordered vertical velocity')
coverage={};pe=load();md=Cs(CS_ARCH_X86,CS_MODE_32)
for at,length in ranges.items():
    instructions=list(md.disasm(pe.get_data(at-0x400000,length),at));missing=[hex(i.address) for i in instructions if not hits[i.address]]
    coverage[hex(at)]={'total':len(instructions),'covered':len(instructions)-len(missing),'missing':missing}
    assert not missing,(hex(at),missing)
scope='Complete rail eligibility500020 and endpoint transform57cb60; actual math and clock callees, ordered endpoint-distance gate, adjacency and low-byte force. Defined bytes compare except declared computed NaNs. Integrated into the main module; full dispatcher and playable level remain unfinished.'
fixture={'base':BASE,'memory':'rail-gate-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'native_callbacks':[{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]}
path=draft/'rail-gate-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(draft/fixture['memory']).write_bytes(initial)
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'instruction_coverage':coverage,'scope':scope}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('Original rail gate',len(labels),coverage,flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_rail_gate_wasm.mjs')],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory']]}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS rail gate',len(labels),sum(oracle.counts.values()))
