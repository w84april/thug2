"""Full grind-script startup with real allocation, selection and interpreter."""
from pathlib import Path
prefix=Path('tools/verify_pending_flip.py').read_text().split('for j in range(48):')[0]
prefix=prefix.replace('pending-flip.json','grind-script.json')
exec(compile(prefix,'<pending flip prerequisites>','exec'))
draft=out;report_path=out.parent/'grind-script.json'
bind(0x5004b0,'thug_skater_start_grind_script',5,'void',True,True,True)
bind(0x4738e0,'thug_script_initialize',0,'word',False,False,True)
fields.add(BODIES+0x10)
SCRIPT_POOL,SCRIPT_BLOCK=0x16f1000,0x16f1100
copy(SCRIPT_POOL,bytes(0x500));put(SCRIPT_POOL,'<6I',SCRIPT_BLOCK,SCRIPT_BLOCK+0x200,0,0,0,SCRIPT_BLOCK)
put(SCRIPT_BLOCK,'<I',SCRIPT_BLOCK+0x100);put(SCRIPT_BLOCK+0x100,'<I',0)
fields.update([SCRIPT_POOL,SCRIPT_POOL+4,SCRIPT_POOL+20,SCRIPT_BLOCK,SCRIPT_BLOCK+0x100])
initial=bytes(memory);oracle.initial=initial
oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=0x5004b0,end=0x5004b0)
parent_hits=Counter()
def parent_trace(cpu,at,size,user):parent_hits[at]+=1
oracle.cpu.hook_add(UC_HOOK_CODE,parent_trace,begin=0x5004b0,end=0x500649)
oracle.case([call(0x460b80,BODIES)])
body_base=bytes(oracle.cpu.mem_read(BODIES,0x4c))
labels=[];oracle.cases.clear();oracle.counts.clear();oracle.coverage.clear()
def program(b,name):
    code=b.alloc(b'\x01\x43'+struct.pack('<I',NATIVE)+b'\x01\x24');fields.add(code+2)
    b.symbol(name,7,code);entry=b.alloc(struct.pack('<5I',name,code,1,0,0));slot=CACHETABLE+32+(name&3)*12
    previous=bytes(initial[slot-BASE:slot-BASE+12]);link=b.alloc(previous)
    b.extra.append(patch(slot,'<3I',name,entry,link))
def grind(category=0,flags=(0,0,0,0),fallback=0,existing=False,pending=(0,0,0),outer_one=False,inner_one=False,extra=(),pool=0,label='grind script'):
    b=Build();arrays=[]
    for i in range(1 if outer_one else 9):arrays.append(b.array(13,[0x71110000+i*0x100+j for j in range(1 if inner_one else 16)]))
    b.symbol(0x2ab3341d,12,b.array(12,arrays))
    mask=sum((int(v)&255!=0)<<j for j,v in enumerate(flags));cat=0 if category>8 or outer_one else category
    chosen=0xf7ca3f78 if fallback else 0x71110000+cat*0x100+(0 if inner_one else mask)
    program(b,chosen)
    p=b.patches()+network()+[patch(PHYS+0x302,'<B',fallback),patch(FLIP+0x19,'<3B',*pending),patch(PHYS+0x3a8,'<I',0xdeadbeef),patch(SKATER_STATE+0xe0,'<B',0)]+list(extra)
    if existing:
        p += [raw(BODIES,body_base),patch(BODIES+0x10,'<I',SCRIPTS)]
        setup=body_setup()[1:]+[call(0x4738e0,SCRIPTS)]
    else:setup=body_setup()
    cpu=oracle.cpu;cpu.reg_write(UC_X86_REG_FPSW,0);cpu.reg_write(UC_X86_REG_FPTAG,0xffff);cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
    changes={index[0x6f3548]:pool-1,index[0x6f3550+4*(pool-1)]:SCRIPT_POOL} if pool else {}
    stages=oracle.case(setup+[call(0x5004b0,PHYS,[category,*flags])],p,changes);labels.append(label)
    previous=0
    for step in stages:
        current=previous
        for at,data in step['outputs']:
            if at<=GOBS<at+len(data)//2:current=int.from_bytes(bytes.fromhex(data)[GOBS-at:GOBS-at+4],'little')
        step['callbacks']=current-previous;previous=current
    assert oracle.word(GOBS)>0,(label,chosen)
    assert oracle.word(GOBS+64)==chosen,(label,hex(oracle.word(GOBS+64)),hex(chosen))
    return stages[-1]
for category in [0,1,2,3,4,5,6,7,8,9,0xffffffff]:
    for mask in range(16):
        grind(category,[1 if mask&(1<<j) else 0 for j in range(4)],existing=bool(mask&1),label='category and all four trick flags')
for flags in [(256,257,0xffffffff,255),(0,0,0,0),(1,1,1,1)]:
    for outer_one,inner_one in itertools.product([False,True],repeat=2):
        grind(8,flags,outer_one=outer_one,inner_one=inner_one,label='low-byte flags and inline single-element arrays')
for fallback,existing in itertools.product([1,255],[False,True]):
    grind(0xffffffff,[255]*4,fallback=fallback,existing=existing,pending=(1,1,1),label='fallback script bypasses selection and pending flips')
for pending in itertools.product([0,1],repeat=3):
    grind(3,[1,0,1,0],pending=pending,label='actual pending flip orientation and board updates before script')
for target,value,width in [(SKATER_STATE+0xe0,0,1),(PHYS+0x1528,SKATER_STATE2,4),(PHYS+0x3a8,0x12345678,4)]:
    grind(2,[1,0,0,1],extra=[patch(GOBS+4,'<4I',target,value,width,0)],label='grind QB changes state before completion write')
for pool,existing,fallback in itertools.product([1,2],[False,True],[0,1]):
    grind(4,[0,1,0,1],pool=pool,existing=existing,fallback=fallback,label='actual fixed script pool selection and existing instance')
pe=load();md=Cs(CS_ARCH_X86,CS_MODE_32);ins=list(md.disasm(pe.get_data(0x5004b0-0x400000,410),0x5004b0))
coverage={'total':len(ins),'covered':sum(bool(parent_hits[i.address]) for i in ins),'missing':[hex(i.address) for i in ins if not parent_hits[i.address]]}
assert coverage['missing']==['0x5004f6','0x500523'],coverage
scope='Recovered complete grind-script startup5004b0 with original array selection, heap/fixed-pool allocation and initialization, pending flips, real QB setup/execution and live state reload. Successful allocation and loaded script graphs are internal contracts. Integrated into the main module; the complete playable level remains unfinished.'
fixture={'base':BASE,'memory':'grind-script-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'native_qb_callbacks','pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'native_callbacks':[{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]}
path=draft/'grind-script-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(draft/fixture['memory']).write_bytes(initial)
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'instruction_coverage':{'0x5004b0':coverage},'native_qb_calls':dict(qb_calls),'scope':scope}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('Original grind script',len(labels),coverage,flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_grind_script_wasm.mjs')],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [draft/'grind-script-fixtures.json',draft/fixture['memory']]}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS grind script',len(labels),sum(oracle.counts.values()))
