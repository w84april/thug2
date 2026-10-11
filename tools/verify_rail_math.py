"""Recovered rail-search line geometry and segment-reversal comparisons."""
from pathlib import Path
prefix=Path('tools/verify_frame_actions.py').read_text().split('# The raw text getter')[0]
prefix=prefix.replace("'frame-actions.json'","'rail-math.json'")
probe_file=__file__;__file__=str(Path('tools/verify_frame_actions.py').resolve())
exec(compile(prefix,'<initialized engine graph>','exec'));__file__=probe_file
draft=out;report_path=out.parent/'rail-math.json'
A,B,OUT_A,OUT_B,AMOUNTS,PROBE=0x16b0000,0x16b0100,0x16b0200,0x16b0240,0x16b0300,0x16b1000
copy(A,bytes(0x2000));put(AMOUNTS,'<2I',0x12345678,0xabcdef01)
for row in [(0x57c210,'thug_collision_probe_reverse',0,'void',False,False,True),
            (0x57c260,'thug_segment_bounds',4,'word',False,False,False),
            (0x402f00,'thug_segment_closest_points',7,'byte',False,False,False)]:
    bind(*row);oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=row[0],end=row[0])
ranges={0x57c210:71,0x57c260:203,0x402f00:773};hits=Counter()
def trace(cpu,at,size,user):hits[at]+=1
for at,n in ranges.items():oracle.cpu.hook_add(UC_HOOK_CODE,trace,begin=at,end=at+n-1)
initial=bytes(memory);oracle.initial=initial
labels=[];oracle.cases.clear();oracle.counts.clear();oracle.coverage.clear()
def compare(fn,this=0,args=(),p=(),label='rail math',floats=(),quiet=()):
    cpu=oracle.cpu;cpu.reg_write(UC_X86_REG_FPSW,0);cpu.reg_write(UC_X86_REG_FPTAG,0xffff);cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
    step=oracle.case([call(fn,this,args)],p)[-1];labels.append(label)
    step['float_fields']=list(floats);step['quiet_float_fields']=list(quiet);return step
words=[0,0x80000000,0x3f800000,0xbf800000,1,0x80000001,0x7f7fffff,0x7f800000,0xff800000,0x7fa12345,0xffa12345,0x7fc12345]
for i in range(32):
    data=bytearray(rng.getrandbits(8) for _ in range(0xb0))
    struct.pack_into('<8I',data,0,*[words[(i+j)%len(words)] for j in range(8)])
    compare(0x57c210,PROBE,p=[raw(PROBE,data)],label='reverse raw segment and preserve probe state',quiet=[PROBE,PROBE+4])
for a,b in itertools.product(words,words):
    compare(0x57c260,args=[A,B,OUT_A,OUT_B],p=[patch(A,'<4I',a,b,a,0xdeadbeef),patch(B,'<4I',b,a,b,0xcafebabe)],label='endpoint ordered comparisons, signs and exact quieting',quiet=[OUT_A,OUT_A+4,OUT_A+8,OUT_B,OUT_B+8])
for destination,other in itertools.product([A,A+4,B,OUT_A],[A,A+4,B,OUT_A+4,OUT_B]):
    # The last writer decides whether the final aliased lane is quieted or raw.
    writes={}
    for at,q in [(destination,1),(destination+4,1),(destination+12,0),(destination+8,1),(other+4,0),(other,1),(other+12,0),(other+8,1)]:writes[at]=q
    compare(0x57c260,args=[A,B,destination,other],p=[patch(A,'<4I',0x7fa12345,bits(2),bits(3),0xdeadbeef),patch(B,'<4I',bits(1),0xffa12345,bits(-1),0xcafebabe)],label='overlapping endpoint and bound outputs',quiet=[at for at,q in writes.items() if q])
def closest(a,b,clamp=0,pa=OUT_A,pb=OUT_B,ta=AMOUNTS,tb=AMOUNTS+4,label='closest lines'):
    return compare(0x402f00,args=[A,B,pa,pb,ta,tb,clamp],p=[patch(A,'<8f',*a),patch(B,'<8f',*b)],label=label,
        floats=sorted(set([ta,tb]+list(range(pa,pa+16,4))+list(range(pb,pb+16,4)))))
examples=[([0,0,0,1,10,0,0,1],[5,-5,2,1,5,5,2,1]),
          ([0,0,0,1,10,0,0,1],[15,5,2,1,15,15,2,1]),
          ([0,0,0,1,10,0,0,1],[-5,-15,2,1,-5,-5,2,1]),
          ([0,0,0,1,0,0,0,1],[1,2,3,1,4,5,6,1]),
          ([0,0,0,1,10,0,0,1],[0,1,0,1,10,1,0,1]),
          ([0,0,0,1,10,0,0,1],[0,1,0,1,0,1,0,1])]
for a,b in examples:
    for clamp in [0,1,255,256,257]:closest(a,b,clamp,label='degenerate, parallel, crossing or exterior; clamp low byte')
for axis,length,clamp in itertools.product(range(3),[0,1e-8,9.999998e-6,9.999999747378752e-6,1.0000002e-5,.01,1,1e10],[0,1]):
    a=[0.,0,0,1,0,0,0,1];b=[0.,0,0,1,0,0,0,1]
    a[4+axis]=length;b[4+(axis+1)%3]=1
    closest(a,b,clamp,label='direction and denominator epsilon boundaries')
for i in range(320):
    scale=[1e-8,1e-3,1,1e3,1e10][i%5]
    a=[rng.uniform(-scale,scale) for _ in range(8)];b=[rng.uniform(-scale,scale) for _ in range(8)]
    closest(a,b,[0,1,256,257][i%4],label='random spatial segments and all four interpolated lanes')
for lane,value in itertools.product(range(8),[0.,-0.,1e-40,1e30,math.inf,-math.inf,math.nan]):
    a=examples[0][0][:];b=examples[0][1][:];a[lane]=value
    closest(a,b,lane%2,label='special arithmetic values in each input lane')
for pa,pb,ta,tb in [(A,B,AMOUNTS,AMOUNTS+4),(A+4,B+4,AMOUNTS,AMOUNTS+4),(B,A,AMOUNTS,AMOUNTS+4),
                   (OUT_A,OUT_A,AMOUNTS,AMOUNTS+4),(OUT_A,OUT_A+4,AMOUNTS,AMOUNTS+4),
                   (OUT_A,OUT_B,A,B),(OUT_A,OUT_B,AMOUNTS,AMOUNTS),(AMOUNTS,OUT_B,AMOUNTS,AMOUNTS+4),
                   (OUT_A,AMOUNTS,AMOUNTS,AMOUNTS+4),(OUT_A,OUT_B,A+16,B+16)]:
    for clamp in [0,1]:closest(*examples[1],clamp,pa,pb,ta,tb,label='output aliases preserve late parameter and endpoint reads')
coverage={};pe=load();md=Cs(CS_ARCH_X86,CS_MODE_32)
for at,n in ranges.items():
    ins=list(md.disasm(pe.get_data(at-0x400000,n),at));missing=[hex(i.address) for i in ins if not hits[i.address]]
    coverage[hex(at)]={'total':len(ins),'covered':len(ins)-len(missing),'missing':missing}
assert all(not row['missing'] for row in coverage.values()),coverage
scope='Recovered segment reverse57c210, ordered endpoint bounds57c260 and closest-line points402f00. Original x87 arithmetic, low-byte clamping, aliased outputs and raw/quieted lanes. Computed NaNs classify; explicit raw-copy quiet-bit corrections model physical x87. Integrated into the main module; the complete playable level remains unfinished.'
fixture={'base':BASE,'memory':'rail-math-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'native_callbacks':[{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]}
path=draft/'rail-math-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(draft/fixture['memory']).write_bytes(initial)
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'instruction_coverage':coverage,'scope':scope}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('Original rail math',len(labels),coverage,flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_rail_math_wasm.mjs')],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory']]}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS rail math',len(labels),sum(oracle.counts.values()))
