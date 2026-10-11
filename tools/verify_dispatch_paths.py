"""Compare complete attachment acquisition and post-transfer speed updates."""
from pathlib import Path
import itertools
prefix=Path(__file__).with_name('verify_frame_prerequisites.py').read_text().split('FRAME_PRINT,FRAME_OBS=')[0]
exec(compile(prefix.replace("'frame-prerequisites.json'","'dispatch-paths.json'"),'<initialized dispatcher graph>','exec'))
TYPE_MANAGER,DPRINT,DOBS,OWNER2,ATTACH2,PROVIDER2,POINTS2,NODES2=0x1678000,0x167a000,0x167b000,0x1680000,0x1680800,0x1680900,0x1680a00,0x1680b00
SCRIPT1,SCRIPT2,EVENT1,EVENT2,ENTRY1,ENTRY2=0x1681000,0x1681200,0x1681400,0x1681420,0x1681500,0x1681520
copy(TYPE_MANAGER,bytes(0x4000));copy(OWNER2,bytes(0x2000))
put(TYPE_MANAGER+0x44,'<5I',2,0xface,0xdeadbeef,0x3506ce64,0xbadf00d)
glob('thug_component_type_registry',0x6f0fb8,TYPE_MANAGER)
for i in range(128):glob('thug_component_type_heads',0x6f0db8+i*4,GATTACH if i==1 else 0,offset=i*4)
glob('thug_transfer_speed_diagnostic_counter',0x7ccdcc,0)
exports.append([0x7ccdcc,'thug_transfer_speed_diagnostic_counter'])
put(DPRINT,'<I',DOBS);put(DOBS+4,'<I',PHYS);PRINT=DPRINT
fields.add(DOBS+8)
for i in range(64):fields.add(DOBS+32+i*40+28)
put(PHYS+0x364,'<3I',0,0,0);put(PHYS+0x3ac,'<f',1)
put(INPUT+0x20,'<B3xI',1,0);put(INPUT+0xb0,'<I',0xabcd12ff);put(INPUT+0x110,'<I',0xefab34ff)
put(GATTACH+0x14,'<IB3x',ATTACH2,1)
put(ATTACH2,'<8I',0,0x3506ce64,0,OWNER2,0,0,1,PROVIDER2)
put(PROVIDER2,'<I',0x6462d4);put(PROVIDER2+0x18,'<I',POINTS2);put(POINTS2,'<I',NODES2)
put(OWNER2+0x100,'<I',ATTACH2);put(OWNER2+0x6c,'<16f',*identity)
put(OWNER2+0x4c,'<4f',25,0,0,1)
put(GOWNER+0x4c,'<4f',0,0,0,1);put(BODIES+0x4c,'<4f',10,0,10,1)
for j in range(3):put(NODES2+j*32,'<4fI',j*24,0,0,1,NODES2+(j+1)*32 if j<2 else 0)
fields.add(PROVIDER2)
for row in [(0x503ec0,'thug_skater_find_attachment',0,'void',True,True,True),
            (0x4ff200,'thug_skater_update_transfer_speed',0,'void',False,True,True),
            (0x487ad0,'thug_min_three',3,'double',False,False,False)]:bind(*row)
functions['0x487ad0']['float_args']=[0,1,2]
for at in [0x503ec0,0x4ff200,0x487ad0,0x45f2d0,0x51ba70,0x5480f0,0x4023c0,0x46b7e0,0x41d1d0,0x4609f0,0x580790]:
    if (at,at) not in observers:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
format_bytes=b'Post-Transfer Speed Limit Overrides:  current / standard = %.2f\n'
def text_hash(data):
    h=0
    for c in data:h=(h*33+c)&0xffffffff
    return h
diagnostics=0
def print_boundary(cpu,at,size,user):
    global diagnostics
    sp=cpu.reg_read(UC_X86_REG_ESP);fmt=oracle.word(sp+4)
    assert fmt==0x64bc88 and bytes(cpu.mem_read(fmt,len(format_bytes)+1))==format_bytes+b'\0'
    n=oracle.word(DOBS);assert n<64
    value=bytes(cpu.mem_read(sp+8,8));target,raw,limit=[oracle.word(DOBS+off) for off in [8,12,16]]
    row=struct.pack('<I',text_hash(format_bytes))+value+struct.pack('<7I',*[oracle.word(PHYS+off) for off in [0x350,0x354,0x358,0x3ac]],target,raw,limit)
    cpu.mem_write(DOBS+32+n*40,row);oracle.setword(DOBS,n+1);diagnostics+=1
    if target and n<limit:oracle.setword(target,raw)
    cpu.reg_write(UC_X86_REG_EAX,0);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
oracle.cpu.hook_add(UC_HOOK_CODE,print_boundary,begin=0x401c30,end=0x401c30)
instruction_hits=Counter();ranges={0x503ec0:410,0x4ff200:619,0x487ad0:45}
def trace(cpu,at,size,user):instruction_hits[at]+=1
for at,length in ranges.items():oracle.cpu.hook_add(UC_HOOK_CODE,trace,begin=at,end=at+length-1)
initial=bytes(memory);oracle.initial=initial
# Populate each object's ordinary header using the recovered original constructor.
for body in [BODIES,GOWNER,OWNER2]:
    oracle.case([call(0x460b80,body)])
    copy(body,bytes(oracle.cpu.mem_read(body,0x4c)))
initial=bytes(memory);oracle.initial=initial
labels=[];oracle.cases.clear();oracle.counts.clear();oracle.coverage.clear()

def configuration(soft=100.,maximum=3.,decay=.5,hold=100,distance=100.):
    b=grounded_config()
    pair=b.alloc(struct.pack('<I2f',0,soft,soft));b.symbol(0x2eacddb3,10,b.structure([(0,5,pair)]))
    for key,value in [(0xc6b38be0,maximum),(0xf9b006aa,decay),(0x2928f080,distance)]:
        b.symbol(key,1 if isinstance(value,int) else 2,value&0xffffffff if isinstance(value,int) else bits(value))
    b.symbol(0x19b2c752,1,hold&0xffffffff)
    name=0x2f184eb1;code=b.alloc(b'\x01\x43'+struct.pack('<I',NATIVE)+b'\x01\x24');fields.add(code+2)
    entry=b.alloc(struct.pack('<5I',name,code,1,0,0));slot=CACHETABLE+32+(name&3)*12
    previous=next((bytes.fromhex(data) for at,data in reversed(b.extra) if at==slot),initial[slot-BASE:slot-BASE+12])
    link=b.alloc(previous);b.extra.append(patch(slot,'<3I',name,entry,link));b.symbol(name,7,code)
    return b

def attached_events():
    p=[]
    for owner,script,events,entry in [(GOWNER,SCRIPT1,EVENT1,ENTRY1),(BODIES,SCRIPT2,EVENT2,ENTRY2)]:
        data=bytearray(244)
        for off,v in [(0x2c,script+0x1c),(0x94,script+0x34),(0xe0,events),(0xec,0x6478e4)]:struct.pack_into('<I',data,off,v)
        fields.add(script+0xec)
        p += [raw(script,data),patch(owner+0x10,'<I',script),patch(events,'<IIBBHI',entry,1,1,0,0,0),patch(entry,'<5I',0x2f184eb1,0x2f184eb1,0,0,1)]
    return p

def run(at,this=PHYS,args=(),p=(),b=None,changes=None,label='dispatcher path',repeat=1,events=False,before=(),floats=()):
    cpu=oracle.cpu;cpu.reg_write(UC_X86_REG_FPSW,0);cpu.reg_write(UC_X86_REG_FPTAG,0xffff);cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
    setup=[]
    if at==0x503ec0:
        for j,body in enumerate([BODIES,GOWNER,OWNER2]):setup += [call(0x461930,body,[0x200+j]),call(0x461a00,UM,[body])]
        if events:setup += [call(0x41d1d0,SCRIPT1+0xbc,[GOWNER]),call(0x41d1d0,SCRIPT2+0xbc,[BODIES])]
    stages=oracle.case(setup+list(before)+[call(at,this,args)]*repeat,
                      (b or configuration()).patches()+(attached_events() if events else [])+list(p),
                      {index[k]:v for k,v in (changes or {}).items()})
    labels.append(label);previous=0;previous_qb=0
    for step in stages:
        step['float_fields']=list(floats);count=previous;qb=previous_qb
        for address,data in step['outputs']:
            end=address+len(data)//2;decoded=bytes.fromhex(data)
            if address<=DOBS<end:count=int.from_bytes(decoded[DOBS-address:DOBS-address+4],'little')
            if address<=GOBS<end:qb=int.from_bytes(decoded[GOBS-address:GOBS-address+4],'little')
        step['callbacks']=count-previous+qb-previous_qb;previous=count;previous_qb=qb
    if len(labels)%100==0:print('Dispatcher cases',len(labels),flush=True)
    return stages[-1]

values=[0,-0.,1,-1,1e-40,1e30,math.inf,-math.inf,math.nan]
for first,second,third in itertools.product(values,repeat=3):
    run(0x487ad0,0,[bits(first),bits(second),bits(third)],label='ordered three-way minimum, signed zeros and NaNs')
for nan_word,lane in itertools.product([0x7f800001,0xff800001,0x7fa12345,0xffa12345],range(3)):
    args=[bits(1),bits(-1),bits(0)];args[lane]=nan_word
    run(0x487ad0,0,args,label='signaling NaN minimum operand order')

for blocked,locked,pressed,mode in itertools.product([0,1,255],[0,1],[0,1],[0,1,2]):
    run(0x503ec0,p=[patch(PHYS+0x2ed,'<B',blocked),patch(SKATER_STATE+0x88,'<B',locked),patch(INPUT+0x20,'<B',pressed),patch(SKATER_STATE+0x18,'<I',mode)],label='attachment early gates')
for age,hold in itertools.product([0,99,100,101,1666,0x7fffffff,0x80000000,0xffffffff],[0,100,0x7fffffff,0x80000000,0xffffffff]):
    run(0x503ec0,p=[patch(INPUT+0x24,'<I',(1666-age)&0xffffffff)],b=configuration(hold=hold),label='attachment unsigned hold threshold')
for variant in ['empty registry','missing type','null head','disabled','own body','no owner','no provider','no points','no nodes','tie','nearer second','farther second']:
    p=[];changes={}
    if variant=='empty registry':p=[patch(TYPE_MANAGER+0x44,'<I',0)]
    elif variant=='missing type':p=[patch(TYPE_MANAGER+0x50,'<I',0x1234)]
    elif variant=='null head':changes={0x6f0dbc:0}
    elif variant=='disabled':p=[patch(GATTACH+0x18,'<B',0)]
    elif variant=='own body':p=[patch(GATTACH+12,'<I',BODIES)]
    elif variant=='no owner':p=[patch(GATTACH+12,'<I',0)]
    elif variant=='no provider':p=[patch(GATTACH+0x1c,'<I',0)]
    elif variant=='no points':p=[patch(GPROVIDER+0x18,'<I',0)]
    elif variant=='no nodes':p=[patch(GPOINTS,'<I',0)]
    elif variant=='tie':p=[patch(OWNER2+0x4c,'<4f',0,0,0,1)]
    elif variant=='nearer second':p=[patch(OWNER2+0x4c,'<4f',10,0,10,1)]
    elif variant=='farther second':p=[patch(OWNER2+0x4c,'<4f',1e7,0,0,1)]
    run(0x503ec0,p=p,changes=changes,label='attachment '+variant,repeat=2)
for bound in [-1,0,1,9.999,10,10.001,14.1421,14.1422,100,math.nan,math.inf]:
    run(0x503ec0,b=configuration(distance=bound),label='attachment actual distance boundary')
for seed in range(48):
    p=[patch(BODIES+0x4c,'<4f',*[rng.uniform(-100,100) for _ in range(3)],1)]
    for body,nodes in [(GOWNER,GNODES),(OWNER2,NODES2)]:
        angle=rng.uniform(-3,3);c,s=math.cos(angle),math.sin(angle)
        p += [patch(body+0x6c,'<16f',c,0,-s,0,0,1,0,0,s,0,c,0,0,0,0,1),patch(body+0x4c,'<4f',*[rng.uniform(-50,50) for _ in range(3)],1)]
        for j in range(3):p.append(patch(nodes+j*32,'<4f',*[rng.uniform(-100,100) for _ in range(3)],1))
    run(0x503ec0,p=p,b=configuration(distance=1000),label='attachment transformed candidate geometry')
for target,value,width in [(0,0,0),(PHYS+0x24c,2,4),(PHYS+0xc,OWNER2,4),(INPUT+0xb0,1,1),(PHYS+0x2ed,1,1),(GATTACH+0x14,0,4)]:
    before=qb_calls['0x2f184eb1']
    run(0x503ec0,p=[patch(GOBS+4,'<4I',target,value,width,0x2f184eb1)],events=True,label='attachment original QB events and live body mutation')
    assert qb_calls['0x2f184eb1']>before

computed=[PHYS+o for o in [0x350,0x354,0x358,0x3ac]]
for previous,current,resistance,mode in itertools.product([0,1,255],[0,1],[0,1],[0,1,2]):
    run(0x4ff200,p=[patch(PHYS+0x255,'<B',previous),patch(SKATER_STATE+0x78,'<B',current),patch(SKATER_STATE+0x70,'<B',resistance),patch(SKATER_STATE+0x18,'<I',mode),patch(BODIES+0xac,'<4f',200,30,60,1)],label='post-transfer gates and modes',floats=computed)
for speed in [0,1,99,100,124.999,125,125.001,200,400,1e-30,1e30,math.inf,math.nan]:
    for maximum in [1.,2.,3.,-1.,math.nan]:
        run(0x4ff200,p=[patch(PHYS+0x255,'<B',1),patch(BODIES+0xac,'<4f',speed,0,0,0)],b=configuration(maximum=maximum),label='post-transfer activation threshold and cap',floats=computed)
for multiplier,dt,mode in itertools.product([0,-0.,.9,1,1.00001,1.1,2,1e-40,1e30,math.inf,-math.inf,math.nan],[0,1/60,1,-1],[0,1]):
    run(0x4ff200,p=[patch(PHYS+0x3ac,'<f',multiplier),patch(PHYS+0x350,'<3f',-2,175,200),patch(PHYS+0x8c,'<f',dt),patch(SKATER_STATE+0x18,'<I',mode),patch(BODIES+0xac,'<4f',100,40,80,1)],label='post-transfer decay and repeated updates',repeat=2,floats=computed)
for soft,decay in itertools.product([0.,-100.,1e-30,1e30,math.inf,math.nan],[0.,-1.,1e-30,1e30,math.inf,math.nan]):
    run(0x4ff200,p=[patch(PHYS+0x3ac,'<f',2),patch(PHYS+0x354,'<f',200),patch(SKATER_STATE+0x18,'<I',1)],b=configuration(soft=soft,decay=decay),label='post-transfer wide or nonfinite parameters',floats=computed)
for maximum,decay in itertools.product([16777217,2147483647,-2147483648],[0,16777217,-16777217,2147483647]):
    run(0x4ff200,p=[patch(PHYS+0x255,'<B',1),patch(BODIES+0xac,'<4f',1e10,1e9,-1e8,0),patch(PHYS+0x8c,'<f',1e-10)],b=configuration(maximum=maximum,decay=decay),label='exact integer parameter promotion before PC24 arithmetic',floats=computed)
for counter in [0,8,9,10,19,0x7fffffff,0x80000000,0xffffffff,0xfffffff7]:
    run(0x4ff200,p=[patch(PHYS+0x3ac,'<f',2),patch(PHYS+0x354,'<f',200),patch(SKATER_STATE+0x18,'<I',1)],changes={0x7ccdcc:counter},label='signed diagnostic counter wrap and remainder',repeat=2,floats=computed)
for target,value,limit in [(0,0,0),(0x7ccdcc,0xffffffff,1),(0x7ccdcc,9,2),(PHYS+0x354,bits(250),1),(PHYS+0x350,bits(-2),1),(PHYS+0x3ac,bits(1),1)]:
    run(0x4ff200,p=[patch(PHYS+0x3ac,'<f',2),patch(PHYS+0x354,'<f',200),patch(SKATER_STATE+0x18,'<I',1),patch(DOBS+8,'<3I',target,value,limit)],changes={0x7ccdcc:9},label='diagnostic callback mutates counter or limits',floats=computed)

coverage={};pe=load();md=Cs(CS_ARCH_X86,CS_MODE_32)
for at,length in ranges.items():
    instructions=[i for i in md.disasm(pe.get_data(at-0x400000,length),at) if i.mnemonic!='int3']
    missing=[hex(i.address) for i in instructions if not instruction_hits[i.address]]
    coverage[hex(at)]={'total':len(instructions),'covered':len(instructions)-len(missing),'missing':missing}
    # 503f69 is alignment-only LEA ESP,[ESP], skipped by both incoming edges.
    assert missing==(['0x503f69'] if at==0x503ec0 else []),(hex(at),missing)
assert diagnostics>0 and qb_calls['0x2f184eb1']>0
scope='Complete attachment acquisition503ec0, post-transfer speed4ff200 and ordered three-way minimum487ad0. Real registry, attachment geometry, reference binding, object events, synchronous QB, stats and parameter routines execute. Exact defined bytes except declared computed NaNs. Diagnostic and terminal native QB/heap services remain explicit boundaries. Valid component/registry and successful allocation contracts apply. Not the complete dispatcher or playable level.'
fixture={'base':BASE,'memory':'dispatch-paths-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'diagnostic_and_native_qb_callbacks','pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'native_callbacks':[{'module':'dispatch-paths-callbacks.wasm','export':'fixture_dispatch_print','slots':[DPRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]}
callback=out/'dispatch-paths-callbacks.wasm'
subprocess.run([str(ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang'),'--target=wasm32-unknown-unknown','-O2','-nostdlib','-Wl,--no-entry,--export-all,--import-memory',str(ROOT/'tools/dispatch_paths_callbacks.c'),'-o',str(callback)],check=True)
path=out/'dispatch-paths-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'instruction_coverage':coverage,'diagnostic_callbacks':diagnostics,'native_qb_calls':dict(qb_calls),'scope':scope}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('Original dispatcher paths',len(labels),coverage,flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_dispatch_paths_wasm.mjs'),str(out)],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory'],callback]}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS dispatcher paths',len(labels),sum(oracle.counts.values()))
