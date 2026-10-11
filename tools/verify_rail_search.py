"""Original rail selection with real math and static/moving query callees."""
from pathlib import Path
prefix=Path('tools/verify_frame_actions.py').read_text().split('# The raw text getter')[0]
prefix=prefix.replace("'frame-actions.json'","'rail-search.json'")
probe_file=__file__;__file__=str(Path('tools/verify_frame_actions.py').resolve())
exec(compile(prefix,'<initialized engine graph>','exec'));__file__=probe_file
draft=out;report_path=out.parent/'rail-search.json'
WORLD,RAILS,FROM,TO,OUT,OUT_NODE,ORIENT=0x16d0000,0x16d0100,0x16d1000,0x16d1100,0x16d1200,0x16d1300,0x16d1400
copy(WORLD,bytes(0x2000));put(WORLD+0x40,'<I',RAILS);fields.update([WORLD+0x40,OUT_NODE])
for i in range(16):fields.update([RAILS+i*0x54+0x40,RAILS+i*0x54+0x44])
glob('thug_skater_orientation_context',0x7ce5d8,ORIENT);put(ORIENT+0x40,'<I',0xd443a2bc)
put(OUT,'<4I',0x12345678,0x87654321,0xabcdef01,0x10203040)
bind(0x57e2d0,'thug_rail_search',7,'byte',False,False,True);functions[hex(0x57e2d0)]['float_args']=[5]
bind(0x5902e0,'thug_segment_initialize',0,'word',False,False,True)
ranges={0x57e2d0:1676,0x5902e0:3};hits=Counter()
def trace(cpu,at,size,user):
    hits[at]+=1
    if at==0x57e2d0:cpu.mem_write(0x691968,bytes(cpu.mem_read(QUERY,12)))
    if at==0x57e959:cpu.mem_write(QUERY,bytes(cpu.mem_read(0x691968,12)))
for at,n in ranges.items():
    oracle.cpu.hook_add(UC_HOOK_CODE,trace,begin=at,end=at+n-1)
    oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
for at in [0x57c600,0x57cc30,0x57c260,0x402f00]:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
initial=bytes(memory);oracle.initial=initial
labels=[];oracle.cases.clear();oracle.counts.clear();oracle.coverage.clear()
def node(position,next=None,previous=None,flags=4,bounds=None):return dict(position=position,next=next,previous=previous,flags=flags,bounds=bounds)
def compare(nodes,from_,to,radius=12.,minimum=1.,side=0,skip=None,extra=(),count=None,out=OUT,out_node=OUT_NODE,label='rail search'):
    b=Build()
    if radius is not None:b.symbol(0xf840753e,1 if isinstance(radius,int) else 2,radius&0xffffffff if isinstance(radius,int) else bits(radius))
    p=b.patches()+[patch(FROM,'<4f',*from_),patch(TO,'<4f',*to),patch(WORLD+0x48,'<i',len(nodes) if count is None else count)]+list(extra)
    for i,n in enumerate(nodes):
        at=RAILS+i*0x54;position=n['position'];other=nodes[n['next']]['position'] if n['next'] is not None else position
        bounds=n['bounds'] or ([min(position[j],other[j]) for j in range(3)]+[1.]+[max(position[j],other[j]) for j in range(3)]+[1.])
        p += [patch(at,'<12f',*bounds,*position),patch(at+0x40,'<5I',RAILS+n['next']*0x54 if n['next'] is not None else 0,RAILS+n['previous']*0x54 if n['previous'] is not None else 0,n['flags'],i+0x100,0)]
    cpu=oracle.cpu;cpu.reg_write(UC_X86_REG_FPSW,0);cpu.reg_write(UC_X86_REG_FPTAG,0xffff);cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
    step=oracle.case([call(0x57e2d0,WORLD,[FROM,TO,out,out_node,0 if skip is None else RAILS+skip*0x54,bits(minimum),side&0xffffffff,QUERY])],p)[-1]
    step['float_fields']=list(range(out,out+16,4));labels.append(label);return step
for c in [-3,0]:compare([],[-10.,0,0,1],[10.,0,0,1],count=c,label='empty signed node count')
for destination in [WORLD,RAILS,FROM,OUT]:
    oracle.case([call(0x5902e0,destination)]);labels.append('identity constructor preserves storage')
for flags,skip,prev in itertools.product([0,4,16,20,0xffffffff],[None,0],[None,0]):
    compare([node([0.,2,0,1],previous=prev,flags=flags)],[-10.,0,0,1],[10.,0,0,1],skip=skip,label='point flag skip and predecessor filters')
for radius,distance in itertools.product([None,0.,-1.,1.,12.,math.inf,math.nan,16777217],[0.,.5,1,2,11.999,12,12.001,50]):
    compare([node([0.,distance,0,1])],[-10.,0,0,1],[10.,0,0,1],radius=radius,label='point distance and numeric radius boundary')
for position in [[0.,0,0,1],[50.,0,0,1],[0.,50,0,1],[0.,0,50,1],[-50.,0,0,1],[0.,-50,0,1],[0.,0,-50,1]]:
    for connected in [False,True]:
        nodes=[node(position,next=1)] if connected else [node(position)]
        if connected:nodes.append(node([position[0],position[1],position[2]+10,1],previous=0))
        compare(nodes,[-10.,0,0,1],[10.,0,0,1],label='all broad-phase rejection axes')
for x,y,minimum,side in itertools.product([-20.,0,20],[0.,6,15],[0.,.5,1.,1.1,math.nan],[0,-1,1]):
    compare([node([x,y,-10,1],next=1),node([x,y,10,1],previous=0)],[-10.,0,0,1],[10.,0,0,1],minimum=minimum,side=side,label='segment exterior distance angle and requested side')
for i in range(260):
    nodes=[]
    for j in range(3):
        a=[rng.uniform(-20,20) for _ in range(3)]+[rng.uniform(-2,2)]
        if i%3==0:nodes.append(node(a))
        else:
            n=len(nodes);nodes += [node(a,next=n+1),node([a[k]+rng.uniform(-20,20) for k in range(4)],previous=n)]
    compare(nodes,[rng.uniform(-10,10) for _ in range(3)]+[1.],[rng.uniform(-10,10) for _ in range(3)]+[1.],radius=[2.,12.,30.][i%3],minimum=[0.,.5,1.][i%3],side=[-1,0,1][i%3],label='ordered multiple candidates and ranking invalidation')
for to in [[0.,0,0,1],[0.,10,0,1],[10.,0,0,1],[0.,0,10,1]]:
    compare([node([0.,2,-10,1],next=1),node([0.,2,10,1],previous=0)],[0.,0,0,1],to,label='zero vertical perpendicular and parallel movement')
for out,outnode in [(FROM,OUT_NODE),(TO,OUT_NODE),(RAILS+0x20,OUT_NODE),(OUT,OUT),(OUT,OUT+4)]:
    compare([node([1.,2,0,1])],[-10.,0,0,1],[10.,0,0,1],out=out,out_node=outnode,label='output commit aliases point input or selected node')
for i in [0,1,3,13,30,34,39,46,70,129]:
    data=bytes.fromhex(loader['queries'][i]['result']);point=list(struct.unpack_from('<4f',data,16))
    for height in [-8.,0,8]:
        a=point[:];b=point[:];a[0]-=8;b[0]+=24;a[1]+=height;b[1]+=height
        from_=point[:];to=point[:];from_[2]-=12;to[2]+=12;from_[1]+=height;to[1]+=height
        compare([node(a,next=1),node(b,previous=0)],from_,to,side=1,extra=[patch(ORIENT+0x40,'<I',0)],label='full rail clearance and side against training geometry')
for lane,value in itertools.product(range(4),[0.,-0.,1e-40,1e30,math.inf,-math.inf,math.nan]):
    position=[0.,2,0,1];position[lane]=value
    compare([node(position,bounds=[-100.,-100,-100,1,100,100,100,1])],[-10.,0,0,1],[10.,0,0,1],label='point arithmetic with nonfinite and extreme coordinates')
for scale in [1e-8,1e-3,1e5,1e10,1e30]:
    for j in range(12):
        a=[rng.uniform(-scale,scale) for _ in range(4)];b=[rng.uniform(-scale,scale) for _ in range(4)]
        compare([node(a,next=1),node(b,previous=0)],[rng.uniform(-scale,scale) for _ in range(4)],[rng.uniform(-scale,scale) for _ in range(4)],radius=scale,label='segment ranking across exponent ranges')
coverage={};pe=load();md=Cs(CS_ARCH_X86,CS_MODE_32)
for at,n in ranges.items():
    ins=list(md.disasm(pe.get_data(at-0x400000,n),at));missing=[hex(i.address) for i in ins if not hits[i.address]]
    coverage[hex(at)]={'total':len(ins),'covered':len(ins)-len(missing),'missing':missing}
assert all(not row['missing'] for row in coverage.values()),coverage
scope='Recovered full rail search57e2d0 and identity constructor5902e0. Original bounds, numeric radius, closest points, clearance/side collision and candidate ranking; point and linked rails, skip/flags, output aliases. Integrated into the main module; the complete playable level remains unfinished.'
fixture={'base':BASE,'memory':'rail-search-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'native_callbacks':[{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]}
path=draft/'rail-search-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(draft/fixture['memory']).write_bytes(initial)
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'instruction_coverage':coverage,'scope':scope}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('Original rail search',len(labels),coverage,flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_rail_search_wasm.mjs')],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,draft/fixture['memory']]}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS rail search',len(labels),sum(oracle.counts.values()))
