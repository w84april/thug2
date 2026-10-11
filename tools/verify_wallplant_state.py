"""Complete mode5 update."""
from pathlib import Path
prefix=Path('tools/verify_frame_actions.py').read_text().split('# The raw text getter')[0]
prefix=prefix.replace("'frame-actions.json'","'wallplant-state.json'")
probe_file=__file__;__file__=str(Path('tools/verify_frame_actions.py').resolve())
exec(compile(prefix,'<full initialized skater graph>','exec'));__file__=probe_file
draft=out;report_path=out.parent/'wallplant-state.json'
bind(0x509050,'thug_skater_update_wallplant_state',heap=True,diag=True)
oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=0x509050,end=0x509050)
hits=Counter()
def trace(cpu,at,size,user):
    hits[at]+=1
    if at==0x509050 and oracle.word(cpu.reg_read(UC_X86_REG_ESP))==oracle.stop:
        cpu.mem_write(0x691968,bytes(cpu.mem_read(QUERY,12)))
    if at in [0x509215,0x5092dd,0x50924a,0x509263]:
        # The recovered query service makes original global traversal state
        # explicit. Copy back at all parent returns, including release tails.
        cpu.mem_write(QUERY,bytes(cpu.mem_read(0x691968,12)))
oracle.cpu.hook_add(UC_HOOK_CODE,trace,begin=0x509050,end=0x5092dd)
put(SKATER_STATE+0x18,'<I',5);put(PHYS+0x2e4,'<B',255)
put(PHYS+0x22c,'<I',0x12345678);put(PHYS+0x244,'<I',0xabcdef01)
put(GROUND_GATE+0x18,'<I',0)
initial=bytes(memory);oracle.initial=initial
oracle.case([call(0x460b80,BODIES)])
body_base=bytes(oracle.cpu.mem_read(BODIES,0x4c));fields.add(SCRIPTS+0xec)
labels=[];oracle.cases.clear();oracle.counts.clear();oracle.coverage.clear()
def config_timed(duration=1000.,missing=False):
    b=grounded_config()
    if not missing:b.symbol(0xa06e446b,1 if isinstance(duration,int) else 2,duration&0xffffffff if isinstance(duration,int) else bits(duration))
    return b
computed=[BODIES+o for o in range(0x4c,0xac,4)]+[PHYS+o for o in list(range(0x18,0x58,4))+list(range(0x208,0x228,4))]
def timed(p=(),b=None,changes=None,label='mode5',repeat=1,attached=False):
    cpu=oracle.cpu;cpu.reg_write(UC_X86_REG_FPSW,0);cpu.reg_write(UC_X86_REG_FPTAG,0xffff);cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
    setup=body_setup()[1:]+[call(0x41d1d0,SCRIPTS+0xbc,[BODIES])] if attached else body_setup()
    stages=oracle.case(setup+[call(0x509050,PHYS,[QUERY])]*repeat,
                      (b or config_timed()).patches()+list(p),{index[k]:v for k,v in (changes or {}).items()})
    labels.append(label);previous=0
    for step in stages:
        step['float_fields']=computed+[GCONTACT+o for o in range(0xc,0xac,4)]
        current=previous
        for at,data in step['outputs']:
            if at<=GOBS<at+len(data)//2:current=int.from_bytes(bytes.fromhex(data)[GOBS-at:GOBS-at+4],'little')
        step['callbacks']=current-previous;previous=current
    return stages[-1]

for age,duration in itertools.product([0,1,999,1000,1001,1666,16777217,0x7fffffff,0x80000000,0xffffffff],[-1.,0.,1000.,math.inf,math.nan]):
    timed([patch(PHYS+0x90,'<I',(1666-age)&0xffffffff)],config_timed(duration),label='unsigned elapsed promotion and strict optional duration')
for duration in [-2147483648,-1,0,16777217,2147483647]:
    timed(b=config_timed(duration),label='integer duration retains precision before comparison')
timed(b=config_timed(missing=True),label='missing optional duration')
for gate in ['none','dead','live','rotate']:
    for angle in [0,.2,-1.1]:
        c,s=math.cos(angle),math.sin(angle);matrix=[c,0,-s,0,0,1,0,0,s,0,c,0,0,0,0,1]
        p=[patch(PHYS+0x90,'<I',1666),patch(GROUND_GATE+0x18,'<I',0 if gate=='none' else GCONTACT),patch(GCONTACT,'<I',0 if gate=='dead' else GOWNER),patch(GOWNER+0x4c,'<4f',20,30,40,1),patch(BODIES+0x4c,'<4f',10,15,30,1)]
        if gate=='rotate':p.append(patch(GOWNER+0x6c,'<16f',*matrix))
        timed(p,label='unexpired moving contact '+gate,repeat=2)
for i in [0,1,2,3,13,24,26,30,34,39,57,70,98,129,278,400,488,510,521,545]:
    q=loader['queries'][i];data=bytes.fromhex(q['result']);normal=struct.unpack_from('<4f',data);point=struct.unpack_from('<4f',data,16)
    for height in [-40,-12,-2,0,2,12,36,40]:
        position=[point[j]+normal[j]*height for j in range(3)]+[1]
        p=[patch(BODIES+0x4c,'<4f',*position),patch(BODIES+0x8c,'<4f',*normal),patch(PHYS+0x90,'<I',0)]
        timed(p,label=f'expired mode5 training probe {i} height {height}')
for value in [0.,-0.,1e-40,1e30,math.inf,-math.inf,math.nan]:
    timed([patch(BODIES+0x8c,'<4f',value,value,value,1)],label='expiry scaled probe arithmetic')
for target,value in [(PHYS+12,GOWNER),(PHYS+0x1528,SKATER_STATE2),(BODIES+0x4c,bits(120)),(BODIES+0x8c,bits(.25))]:
    script=bytearray(244)
    for off,v in [(0x2c,SCRIPTS+0x1c),(0x94,SCRIPTS+0x34),(0xe0,EVENTS),(0xec,0x6478e4)]:struct.pack_into('<I',script,off,v)
    p=[raw(BODIES,body_base),patch(BODIES+0x10,'<I',SCRIPTS),raw(SCRIPTS,script),patch(EVENTS,'<IIBBHI',ENTRIES,1,1,0,0,0),patch(ENTRIES,'<5I',0xa7662059,0xa7662059,0,0,1),patch(GOBS+4,'<4I',target,value,4,0xa7662059)]
    before=qb_calls['0xa7662059'];timed(p,label='state-change QB callback replaces live body or state',attached=True)
    assert qb_calls['0xa7662059']>before

pe=load();md=Cs(CS_ARCH_X86,CS_MODE_32);instructions=list(md.disasm(pe.get_data(0x509050-0x400000,654),0x509050))
coverage={'total':len(instructions),'covered':sum(bool(hits[i.address]) for i in instructions),'missing':[hex(i.address) for i in instructions if not hits[i.address]]}
assert coverage['missing']==['0x50925c','0x50925e','0x50925f','0x509260','0x509263']
scope='Complete mode5 update509050. Original time/parameter access, change-state events, static training surface queries, collision event dispatcher, contact update/release and matrix multiplication execute. Defined bytes compare except declared computed NaNs. Integrated into the main module; unreachable instructions are recorded explicitly.'
fixture={'base':BASE,'memory':'wallplant-state-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'native_qb_callbacks','pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'native_callbacks':[{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]}
path=draft/'wallplant-state-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(draft/fixture['memory']).write_bytes(initial)
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'instruction_coverage':coverage,'native_qb_calls':dict(qb_calls),'scope':scope}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('Original timed state',len(labels),coverage,flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_wallplant_state_wasm.mjs')],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory']]}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS timed state',len(labels),sum(oracle.counts.values()))
