"""Original component registry, world transform and contact-relative position checks."""
from pathlib import Path
prefix=Path('tools/verify_frame_actions.py').read_text().split('# The raw text getter')[0]
prefix=prefix.replace("'frame-actions.json'","'post-frame.json'")
probe_file=__file__;__file__=str(Path('tools/verify_frame_actions.py').resolve())
exec(compile(prefix,'<existing frame graph>','exec'))
__file__=probe_file
draft=out;report_path=out.parent/'post-frame.json'
TYPE_MANAGER,TRANS_COMPONENT,TRANSFORM,TRANS_OUT=0x1678000,0x1679000,0x1679100,0x1679200
copy(TYPE_MANAGER,bytes(0x2000))
put(TRANS_COMPONENT+12,'<I',BODIES);put(TRANS_COMPONENT+0x18,'<I',TRANSFORM)
put(GROUND_GATE+12,'<I',BODIES);put(GROUND_GATE+0x18,'<I',GCONTACT)
put(GROUND_GATE+0x6c,'<I',GOWNER)
for i in range(128):glob('thug_component_type_heads',0x6f0db8+i*4,0x167a000+i*32,offset=i*4)
NEW=[(0x45f2d0,'thug_component_type_head',1,'word',False,False,True),
     (0x57c4f0,'thug_transform_set',1,'word',False,False,True),
     (0x42ba10,'thug_component_world_transform',1,'word',False,False,True),
     (0x427dd0,'thug_skater_store_contact_relative',0,'void',True,False,True)]
for entry in NEW:
    bind(*entry);oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=entry[0],end=entry[0])
bind(0x416e70,'thug_moving_contact_initialize',1,'word')
hits=Counter();ranges={0x45f2d0:46,0x57c4f0:9,0x42ba10:118,0x427dd0:193}
def hit(cpu,at,size,user):hits[at]+=1
for at,n in ranges.items():oracle.cpu.hook_add(UC_HOOK_CODE,hit,begin=at,end=at+n-1)
initial=bytes(memory);oracle.initial=initial
labels=[];oracle.cases.clear();oracle.counts.clear();oracle.coverage.clear()
def compare(at,this,args=(),p=(),changes=None,label='post-frame',floats=()):
    cpu=oracle.cpu;cpu.reg_write(UC_X86_REG_FPSW,0);cpu.reg_write(UC_X86_REG_FPTAG,0xffff);cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
    stages=oracle.case([call(at,this,args)],p,{index[k]:v for k,v in (changes or {}).items()})
    labels.append(label)
    for step in stages:step['float_fields']=list(floats)
    return stages[-1]

for count in [0,1,2,17,128]:
    p=[patch(TYPE_MANAGER+0x44,'<I',count)]
    for i in range(count):p.append(patch(TYPE_MANAGER+0x48+i*8,'<2I',0xface0000+i,0xdead0000+i))
    for selected in [0,count//2,max(0,count-1),count,0xffffffff]:
        r=compare(0x45f2d0,TYPE_MANAGER,[0xface0000+selected if selected!=0xffffffff else selected],p,label='component registry order, empty and missing')
        assert r['result']==(0x167a000+selected*32 if selected<count else 0)
compare(0x45f2d0,TYPE_MANAGER,[17],[patch(TYPE_MANAGER+0x44,'<5I',2,17,0xaaaaaaaa,17,0xbbbbbbbb)],label='duplicate registry keys select the first global head')
compare(0x45f2d0,TYPE_MANAGER,[17],[patch(TYPE_MANAGER+0x44,'<3I',1,17,0xbbbbbbbb)],{0x6f0db8:0},label='registered type with null head')

words=[0,0x80000000,0x3f800000,0xbf800000,0x7f812345,0xff812345,0x7fc12345,0x7f800000,0xff800000]
for offset in [-16,-4,0,4,16,64,0x50]:
    source=TRANSFORM+offset
    compare(0x57c4f0,TRANSFORM,[source],[patch(source,'<16I',*[words[j%len(words)] for j in range(16)])],label='forward transform copy with overlap and changed-marker alias')
for seed in range(12):
    matrix=[rng.getrandbits(32) for _ in range(16)]
    for destination in [TRANS_OUT,TRANSFORM,BODIES+0x6c,BODIES+0x4c]:
        compare(0x42ba10,TRANS_COMPONENT,[destination],[patch(BODIES+0x6c,'<16I',*matrix),patch(BODIES+0x4c,'<4I',words[seed%len(words)],0x7f812345,0x80000000,0xdeadbeef)],label='captured affine transform, raw lanes and output alias')

matrices=[identity,[2.,0,0,0,0,3.,0,0,0,0,4.,0,10.,20.,30.,1.],
          [0,0,1.,0,0,1.,0,0,-1.,0,0,0,0,0,0,1.],
          [1.,.1,0,0,.2,1.,0,0,0,.3,1.,0,3.,4.,5.,1.],
          [0.]*16,[1e-20,0,0,0,0,1e-20,0,0,0,0,1e-20,0,0,0,0,1.]]
for matrix,contact,old_owner in itertools.product(matrices,[0,GCONTACT],[0,GOWNER]):
    compare(0x427dd0,GROUND_GATE,p=[patch(GROUND_GATE+0x18,'<I',contact),patch(GROUND_GATE+0x6c,'<I',old_owner),patch(GOWNER+0x6c,'<16f',*matrix),patch(GOWNER+0x4c,'<4f',10,20,30,1),patch(BODIES+0x4c,'<4f',40,55,70,1)],label='live contact or retained owner with full inverse',floats=[GROUND_GATE+0x1c+i*4 for i in range(4)])
for old_owner in [0,GOWNER]:
    compare(0x427dd0,GROUND_GATE,p=[patch(GCONTACT,'<I',0),patch(GROUND_GATE+0x6c,'<I',old_owner)],label='dead contact release replaces retained owner before fallback')
for value in [0.,-0.,1e-40,1e30,math.inf,-math.inf,math.nan]:
    compare(0x427dd0,GROUND_GATE,p=[patch(BODIES+0x4c,'<4f',value,value,value,value),patch(GOWNER+0x4c,'<4f',value,0,1,-0.)],label='relative position arithmetic and fourth lane',floats=[GROUND_GATE+0x1c+i*4 for i in range(4)])
coverage={};pe=load();md=Cs(CS_ARCH_X86,CS_MODE_32)
for at,n in ranges.items():
    instructions=list(md.disasm(pe.get_data(at-0x400000,n),at));missing=[hex(i.address) for i in instructions if not hits[i.address]]
    coverage[hex(at)]={'total':len(instructions),'covered':len(instructions)-len(missing),'missing':missing}
    assert not missing,(hex(at),missing)
scope=('Complete component-type lookup45f2d0, transform storage57c4f0, world transform42ba10 and '
       'moving-contact relative position427dd0, using actual matrix inverse, vector and contact-release callees. '
       'Exact defined bytes except declared computed NaNs; valid registered counts and component layouts are '
       'internal contracts. Integrated with the main module; not the full dispatcher or playable level.')
fixture={'base':BASE,'memory':'post-frame-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm',
         'memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,
         'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,
         'pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),
         'native_callbacks':[{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},
                            {'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]}
path=draft/'post-frame-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
(draft/fixture['memory']).write_bytes(initial)
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'counts':dict(oracle.counts),
        'callee_coverage':dict(oracle.coverage),'instruction_coverage':coverage,'scope':scope}
report_path.write_text(json.dumps(report,indent=2)+'\n')
print('Original post-frame:',len(labels),coverage,flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_post_frame_wasm.mjs'),str(out)],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory']]}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS post-frame',len(labels),sum(oracle.counts.values()))
