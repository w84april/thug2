"""Isolated rail-trigger traversal and complete lip-state comparisons."""
from pathlib import Path
prefix=Path('tools/verify_frame_actions.py').read_text().split('# The raw text getter')[0]
prefix=prefix.replace("'frame-actions.json'","'lip-state.json'")
probe_file=__file__;__file__=str(Path('tools/verify_frame_actions.py').resolve())
exec(compile(prefix,'<initialized skater graph>','exec'));__file__=probe_file
draft=out;report_path=out.parent/'lip-state.json'
RAILS,RAIL_TRANSFORM,RAIL_EVENTS=0x16a0000,0x16a3000,0x16a4000
copy(RAILS,bytes(0x8000));put(RAIL_TRANSFORM,'<16f',*identity)
put(RAIL_EVENTS,'<3I',7,2,0);put(GAME+0x24,'<I',RAIL_TRANSFORM)
put(PHYS+0x22c,'<6I',RAILS,RAIL_TRANSFORM,0,0,100,0)
put(PHYS+0x244,'<I',0);put(SKATER_STATE+0x18,'<I',3)
put(GROUND_GATE+0x6c,'<I',GOWNER);put(GROUND_GATE+0x1c,'<4f',10,20,30,1)
copy(GCONTEXT+0xd4,bytes(memory[GCONTEXT+0x24-BASE:GCONTEXT+0x7c-BASE]))
for i in range(16):put(RAILS+i*0x100+0x4c,'<I',0x1800+i)
for row in [(0x5092e0,'thug_skater_rail_event',1,'void',True,True,True),
            (0x50bf50,'thug_skater_update_lip',0,'void',True,True,True)]:
    bind(*row);oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=row[0],end=row[0])
for at in [0x427a00,0x434a60,0x476950,0x45c1b0]:
    if (at,at) not in observers:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
hits=Counter();ranges={0x5092e0:361,0x50bf50:687}
def trace(cpu,at,size,user):hits[at]+=1
for at,n in ranges.items():oracle.cpu.hook_add(UC_HOOK_CODE,trace,begin=at,end=at+n-1)
initial=bytes(memory);oracle.initial=initial
oracle.case([call(0x460b80,BODIES)])
body_base=bytes(oracle.cpu.mem_read(BODIES,0x4c));fields.add(SCRIPTS+0xec)
labels=[];oracle.cases.clear();oracle.counts.clear();oracle.coverage.clear()
def nodes(b,triggers,extra=()):
    entries=[]
    for i,key in enumerate(triggers):
        content=[(0xa1dc81f9,13,0x1800+i)]
        if key is not None:content.append((0x2ca8a299,13,key))
        entries.append(b.structure(content+list(extra)))
    b.extra.append(patch(NODE_TABLE+0x1000c,'<I',b.array(10,entries)))
    b.extra += [patch(NODE_TABLE+(0x1800+i)*4,'<Hh',0,i) for i in range(len(entries))]
    return b
def config_lip(triggers=(0xa7662059,),extra=()):
    b=grounded_config();b.symbol(0xcd09e062,1,4);return nodes(b,triggers,extra)
computed=[BODIES+o for o in range(0x4c,0xac,4)]+[PHYS+o for o in list(range(0x18,0x58,4))+list(range(0x258,0x268,4))]+[GCONTACT+o for o in range(0xc,0xac,4)]+[GCONTEXT+0xd4+o for o in [0x24,0x28,0x30,0x34,0x38]]+[GCONTROLLER+0x28]
def run(fn=0x5092e0,p=(),b=None,changes=None,label='rail trigger',before=(),repeat=1,attached=False):
    cpu=oracle.cpu;cpu.reg_write(UC_X86_REG_FPSW,0);cpu.reg_write(UC_X86_REG_FPTAG,0xffff);cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
    setup=body_setup()[1:]+[call(0x41d1d0,SCRIPTS+0xbc,[BODIES])] if attached else body_setup()
    stages=oracle.case(setup+list(before)+[call(fn,PHYS,[RAIL_EVENTS] if fn==0x5092e0 else [])]*repeat,
        (b or config_lip()).patches()+list(p),{index[k]:v for k,v in (changes or {}).items()})
    labels.append(label);previous=0
    for step in stages:
        step['float_fields']=computed;current=previous
        for at,data in step['outputs']:
            if at<=GOBS<at+len(data)//2:current=int.from_bytes(bytes.fromhex(data)[GOBS-at:GOBS-at+4],'little')
        step['callbacks']=current-previous;previous=current
    return stages[-1]
run(p=[patch(PHYS+0x22c,'<I',0)],label='no current rail')
run(b=config_lip([]),label='initial node absent')
for context,key in itertools.product([0,RAIL_TRANSFORM],[None,0,0xa7662059]):
    run(b=config_lip([key]),p=[patch(PHYS+0x230,'<I',context)],label='context fallback, absent or explicit-zero script')
for count,end,target in itertools.product([1,2,3,4,7,12],['null','start','self','middle'],[None,0,-1]):
    triggers=[None]*count
    if target==0:triggers[0]=0
    if target==-1:triggers[-1]=0xa7662059
    p=[patch(RAILS+i*0x100+0x44,'<I',RAILS+(i+1)*0x100 if i+1<count else {'null':0,'start':RAILS,'self':RAILS+i*0x100,'middle':RAILS+(count//2)*0x100}[end]) for i in range(count)]
    run(b=config_lip(triggers),p=p,label=f'predecessor chain {count} {end} target {target}')
for previous,flag,contact in itertools.product([0,0x1800],[0,1,255],['none','live','dead']):
    p=[patch(PHYS+0x244,'<I',previous),patch(SKATER_STATE+0xc8,'<B3sI',flag,b'abc',123),patch(GROUND_GATE+0x18,'<I',0 if contact=='none' else GCONTACT)]
    if contact=='dead':p.append(patch(GCONTACT,'<I',0))
    run(p=p,repeat=2,label='node-change flag, timestamp, repeated event and '+contact+' contact')
for flags in [[],[(0,13,0x68910ac6)],[(0,13,0x20209c31)],[(0,13,0x23627fd7)],[(0,13,0x20209c31),(0,13,0x23627fd7)]]:
    run(b=config_lip(extra=flags),label='real collision event flags and QB spawning')
for target,value in [(PHYS+0x22c,RAILS+0x100),(PHYS+0x1528,SKATER_STATE2),(PHYS+0x244,0xdeadbeef)]:
    run(p=[patch(GOBS+4,'<4I',target,value,4,0xa7662059)],b=config_lip([0xa7662059,0xa7662059]),label='native QB changes rail, state or previous name')

for bits_,selector,pressed in itertools.product(range(8),[0,1,255],[0,1]):
    p=[patch(SKATER_STATE+off,'<B3sI',255 if bits_&(1<<j) else 0,b'abc',123) for j,off in enumerate([0x78,0xa8,0x80])]
    p += [patch(SKATER_STATE+0x20,'<B',selector),patch(INPUT+0x1c0,'<B',pressed),patch(PHYS+0x22c,'<I',0)]
    run(0x50bf50,p,label='lip entry flags and held/released input')
for contact,angle,retained in itertools.product(['none','dead','live'],[0,.2,-1.1],[0,GOWNER]):
    c,s=math.cos(angle),math.sin(angle);matrix=[c,0,-s,0,0,1,0,0,s,0,c,0,0,0,0,1]
    p=[patch(GROUND_GATE+0x18,'<I',0 if contact=='none' else GCONTACT),patch(GROUND_GATE+0x6c,'<I',retained),patch(GCONTACT,'<I',0 if contact=='dead' else GOWNER),patch(GOWNER+0x6c,'<16f',*matrix),patch(GOWNER+0x4c,'<4f',10,20,30,1)]
    run(0x50bf50,p,label='lip world position and rotation '+contact,repeat=2)
for mode,cheat,position in itertools.product([0,0xa549b57b],[0,1],[-9000.,0.,100.,9000.]):
    p=[patch(GCONTEXT+0x18,'<I',mode),patch(STATE+0x5f0,'<I',16 if cheat else 0),patch(GCONTEXT+0x104,'<2f',position,2)]
    run(0x50bf50,p,before=[call(0x461a00,UM,[METER])],label='lip balance, perfect-rail cheat, failure events and sprite meter')
for rail,notify,selector,d8 in itertools.product([0,RAILS],[0,1],[0,1],[0,1,255]):
    p=[patch(PHYS+0x22c,'<I',rail),patch(RAIL_TRANSFORM+0x44,'<I',notify),patch(SKATER_STATE+0x20,'<B',selector),patch(SKATER_STATE+0xd8,'<B',d8),patch(INPUT+0x1c0,'<B',0)]
    run(0x50bf50,p,label='lip release emits both rail events then notifies current node')
for target,value in [(PHYS+0x1528,SKATER_STATE2),(PHYS+0x22c,RAILS+0x100),(PHYS+0xc,GOWNER)]:
    script=bytearray(244)
    for off,v in [(0x2c,SCRIPTS+0x1c),(0x94,SCRIPTS+0x34),(0xe0,EVENTS),(0xec,0x6478e4)]:struct.pack_into('<I',script,off,v)
    p=[raw(BODIES,body_base),patch(BODIES+0x10,'<I',SCRIPTS),raw(SCRIPTS,script),patch(EVENTS,'<IIBBHI',ENTRIES,1,1,0,0,0),patch(ENTRIES,'<5I',0x8ffefb28,0x8ffefb28,0,0,1),patch(GOBS+4,'<4I',target,value,4,0x8ffefb28),patch(SKATER_STATE+0x20,'<B',1),patch(INPUT+0x1c0,'<B',0)]
    run(0x50bf50,p,b=config_lip([0xa7662059,0xa7662059]),label='input-release event replaces live lip components',attached=True)
for target,value in [(PHYS+0x22c,RAILS+0x100),(PHYS+0x22c,0),(PHYS+0x1528,SKATER_STATE2),(PHYS+0x244,0x12345678)]:
    run(0x50bf50,[patch(SKATER_STATE+0x20,'<B',1),patch(INPUT+0x1c0,'<B',0),patch(GOBS+4,'<4I',target,value,4,0xa7662059)],
        b=config_lip([0xa7662059,0xa7662059]),label='first rail event changes live state for the second event',repeat=2)
for value in [0.,-0.,1e-40,1e30,math.inf,-math.inf,math.nan]:
    run(0x50bf50,[patch(GROUND_GATE+0x18,'<I',GCONTACT),patch(GROUND_GATE+0x1c,'<4f',value,value,value,1),patch(GOWNER+0x4c,'<4f',value,0,1,1)],label='lip contact computed coordinate edge cases')
for counter,offset in itertools.product([0,0xffffffff],[0,0x80000000,0xffffffff]):
    run(0x50bf50,[patch(SKATER_STATE+0x78,'<B',255),patch(SKATER_STATE+0x20,'<B',1),patch(INPUT+0x1c0,'<B',0)],
        changes={0x7d1ec8:counter,0x696d60:offset},label='lip timestamps and unsigned wrap')
coverage={};pe=load();md=Cs(CS_ARCH_X86,CS_MODE_32)
for at,n in ranges.items():
    instructions=list(md.disasm(pe.get_data(at-0x400000,n),at));missing=[hex(i.address) for i in instructions if not hits[i.address]]
    coverage[hex(at)]={'total':len(instructions),'covered':len(instructions)-len(missing),'missing':missing}
    assert missing==({0x5092e0:[],0x50bf50:['0x50bfff','0x50c001','0x50c006']}[at]),(hex(at),missing)
scope='Complete rail-trigger5092e0 and lip-state50bf50; original node traversal, collision/QB scripts, moving contacts, lip balance, cheat flags, release events and node notifications. Integrated into the main module; full dispatcher and playable level remain unfinished. Computed NaNs classify; other defined bytes are exact.'
fixture={'base':BASE,'memory':'lip-state-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'native_qb_callbacks','pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'native_callbacks':[{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]}
path=draft/'lip-state-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(draft/fixture['memory']).write_bytes(initial)
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'instruction_coverage':coverage,'native_qb_calls':dict(qb_calls),'scope':scope}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('Original lip state',len(labels),coverage,flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_lip_state_wasm.mjs')],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory']]}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS lip state',len(labels),sum(oracle.counts.values()))
