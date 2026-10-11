"""Grind-entry balance, selection, walk parameters and repetition scoring."""
from pathlib import Path
prefix=Path('tools/verify_frame_actions.py').read_text().split('# The raw text getter')[0]
prefix=prefix.replace("'frame-actions.json'","'grind-helpers.json'")
probe_file=__file__;__file__=str(Path('tools/verify_frame_actions.py').resolve())
exec(compile(prefix,'<initialized skater and UI graph>','exec'));__file__=probe_file
draft=out;report_path=out.parent/'grind-helpers.json'
COMPONENTS=0x16e0000;copy(COMPONENTS,bytes(0x2000))
base_balance=bytes(memory[GCONTEXT+0x24-BASE:GCONTEXT+0x7c-BASE])
for i in range(4):
    ptr=GCONTEXT+0x24+i*0x58;component=COMPONENTS+i*0x20
    copy(ptr,base_balance);put(ptr+12,'<I',component);put(component+0x18,'<I',SCORE)
    put(ptr+0x44,'<2I',0x12345678+i,0xabcdef01-i)
rows=[(0x5799d0,'thug_balance_stop',0,'void',True,True,True),
      (0x4f8ee0,'thug_balance_context_stop',0,'void',True,True,True),
      (0x4f8f20,'thug_balance_position',0,'double',False,False,True),
      (0x5627b0,'thug_score_record_rail',1,'void',False,False,True),
      (0x43da70,'thug_walk_parameter',1,'double',False,False,True),
      (0x46ba50,'thug_grind_trick_variant',4,'word',False,False,False)]
for row in rows:bind(*row)
functions['0x43da70']['cleanup']=0
ranges={0x5799d0:45,0x4f8ee0:51,0x4f8f20:91,0x5627b0:253,0x43da70:40,0x46ba50:37};hits=Counter()
def trace(cpu,at,size,user):hits[at]+=1
for at,n in ranges.items():
    oracle.cpu.hook_add(UC_HOOK_CODE,trace,begin=at,end=at+n-1)
    oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
initial=bytes(memory);oracle.initial=initial
labels=[];oracle.cases.clear();oracle.counts.clear();oracle.coverage.clear()
def compare(calls,p=(),label='grind helper',float_fields=()):
    cpu=oracle.cpu;cpu.reg_write(UC_X86_REG_FPSW,0);cpu.reg_write(UC_X86_REG_FPTAG,0xffff);cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
    stages=oracle.case(calls,p);labels.append(label);previous=0
    for step in stages:
        step['float_fields']=list(float_fields)
        current=previous
        for at,data in step['outputs']:
            if at<=GOBS<at+len(data)//2:current=int.from_bytes(bytes.fromhex(data)[GOBS-at:GOBS-at+4],'little')
        step['callbacks']=current-previous;previous=current
    return stages[-1]
for mode in [0,1,0x8d10119c,0x8d10119d,0x8d10119e,0x255ed86f,0x3506ce64,0x0ac90769,0xef24413b,0xa549b57b,0xffffffff]:
    for value in [0,0x80000000,bits(123.5),0x7f800000,0xff800000,0x7fa12345]:
        p=[patch(GCONTEXT+0x18,'<I',mode)]+[patch(GCONTEXT+0x24+i*0x58+0x30,'<I',value if i%2 else (value^0x80000000)) for i in range(4)]
        compare([call(0x4f8f20,GCONTEXT)],p,label='balance mode selection and raw loaded position')
for counts in itertools.product([0,1,20,21,254,255],repeat=2):
    for threshold in [None,-2147483648,-1,0,1,20,21,254,255,2147483647]:
        b=Build()
        if threshold is not None:b.symbol(0x6ee127b7,1,threshold&0xffffffff)
        p=b.patches()+[patch(SCORE+0x1b0+42,'<B',counts[0]),patch(SCORE+0xb74+42,'<B',counts[1]),patch(SCORE+0x1538,'<5I',0xffffffff,2,0xffffffff,4,0xffffffff)]
        compare([call(0x5627b0,SCORE,[42])]*2,p,label='saturated rail counts, integer wrap and penalty clamp',float_fields=[SCORE+0x154c])
for index in [-0x1b0,-4,-1,0,2499,2500,2501,0x7fffffff]:
    compare([call(0x5627b0,SCORE,[index])],Build().patches(),label='signed rail-index upper gate and valid negative aliases',float_fields=[SCORE+0x154c])
for a,b,c,d in itertools.product(range(16),range(8),range(4),range(2)):
    if a+2*b+4*c+8*d>=16:continue
    args=[v|0xfedcba00 for v in [a,b,c,d]]
    compare([call(0x46ba50,0,args)],label='all valid weighted low-byte table indices')
for seed in [0,bits(.25),0x80000000,0x7fa12345]:
    for kind,value in [(None,0),(1,0x7fffffff),(1,0x80000000),(2,bits(-.75)),(2,0x7f800000),(2,0x7fa12345),(13,0x1234)]:
        b=Build();entries=[] if kind is None else [(0x12345678,kind,value)]
        b.symbol(0x6775e538,10,b.structure(entries))
        compare([call(0x43da70,seed,[0x12345678])],b.patches(),label='walk parameter float/int or unchanged seeded output')
for absent in [False,True]:
    compare([call(0x43da70,bits(.5),[0x12345678])],Build().patches() if absent else [],label='absent walk parameter set preserves seed')
setup=body_setup()+[call(0x461a00,UM,[METER])]
for fn,this in [(0x5799d0,GCONTEXT+0x24),(0x4f8ee0,GCONTEXT)]:
    for live,active in itertools.product([0,1],[0,1]):
        p=[patch(COMPONENTS+i*0x20+0x18,'<I',SCORE if live else 0) for i in range(4)]+[patch(ATTR+16,'<I',active),patch(GCONTEXT+0x18,'<2I',0xa549b57b,0xaabbccdd)]
        compare(setup+[call(fn,this)]*2,p,label='balance stop with absent score or actual meter-hide scripts')
    for target in [GCONTEXT+0x68,GCONTEXT+0x6c,GCONTEXT+0x18,GCONTEXT+0x1c]:
        p=[patch(ATTR+16,'<I',1),patch(GOBS+4,'<4I',target,0x12345678,4,0x58783b40)]
        compare(setup+[call(fn,this)],p,label='actual meter-hide callback changes state before final clearing')
coverage={};pe=load();md=Cs(CS_ARCH_X86,CS_MODE_32)
for at,n in ranges.items():
    ins=list(md.disasm(pe.get_data(at-0x400000,n),at));missing=[hex(i.address) for i in ins if not hits[i.address]]
    coverage[hex(at)]={'total':len(ins),'covered':len(ins)-len(missing),'missing':missing}
scope='Recovered six grind-entry helpers: balance stop/context/position, rail repetition score, walk parameter and 16-entry grind variant. Actual score-meter, script and parameter callees execute. Variant index must address the original 16-entry table. Integrated into the main module; the complete playable level remains unfinished.'
fixture={'base':BASE,'memory':'grind-helpers-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'native_qb_callbacks','pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'native_callbacks':[{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]}
path=draft/'grind-helpers-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(draft/fixture['memory']).write_bytes(initial)
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'instruction_coverage':coverage,'native_qb_calls':dict(qb_calls),'scope':scope}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('Original grind helpers',len(labels),coverage,flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_grind_helpers_wasm.mjs')],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [draft/'grind-helpers-fixtures.json',draft/fixture['memory']]}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS grind helpers',len(labels),sum(oracle.counts.values()))
