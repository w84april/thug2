"""Original pending flip, board rotation and orientation reversal."""
from pathlib import Path
prefix=Path('tools/verify_frame_actions.py').read_text().split('# The raw text getter')[0]
prefix=prefix.replace("'frame-actions.json'","'pending-flip.json'")
probe_file=__file__;__file__=str(Path('tools/verify_frame_actions.py').resolve())
exec(compile(prefix,'<initialized skater network graph>','exec'));__file__=probe_file
draft=out;report_path=out.parent/'pending-flip.json'
COMPLETE=0x16f0000;copy(COMPLETE,bytes(0x300));put(COMPLETE+0x1f4,'<B',255)
put(FLIP+0x20,'<2I',COMPLETE,PHYS);put(FLIP+0x18,'<4B',0,0,0,0)
fields.update([FLIP+0x20,FLIP+0x24])
for row in [(0x4fe120,'thug_skater_reverse_orientation',0,'void',False,False,True),(0x511390,'thug_skater_set_board_rotated',4,'byte',True,True,True),(0x511570,'thug_skater_apply_pending_flip',0,'void',True,True,True)]:bind(*row)
ranges={0x4fe120:173,0x511390:140,0x511570:139};hits=Counter();rotation_packets=[]
def trace(cpu,at,size,user):hits[at]+=1
for at,n in ranges.items():
    oracle.cpu.hook_add(UC_HOOK_CODE,trace,begin=at,end=at+n-1)
    oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
def packet(cpu,at,size,user):
    sp=cpu.reg_read(UC_X86_REG_ESP);spec=oracle.word(sp+4)
    if bytes(cpu.mem_read(spec,1))!=b'\x2a':return
    assert int.from_bytes(cpu.mem_read(spec+2,2),'little')==2
    rotation_packets.append(bytes(cpu.mem_read(oracle.word(spec+4),2)).hex())
oracle.cpu.hook_add(UC_HOOK_CODE,packet,begin=0x459e50,end=0x459e50)
initial=bytes(memory);oracle.initial=initial
labels=[];oracle.cases.clear();oracle.counts.clear();oracle.coverage.clear()
def compare(fn,this,args=(),p=(),net=None,label='pending flip',repeat=1,quiet=()):
    cpu=oracle.cpu;cpu.reg_write(UC_X86_REG_FPSW,0);cpu.reg_write(UC_X86_REG_FPTAG,0xffff);cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
    stages=oracle.case(body_setup()+[call(fn,this,args)]*repeat,network(**(net or {}))+list(p));labels.append(label)
    for i,step in enumerate(stages):step['quiet_float_fields']=list(quiet) if i>=len(stages)-repeat else []
    return stages[-1]
words=[0,0x80000000,bits(1),bits(-1),1,0x80000001,0x7f7fffff,0x7f800000,0xff800000,0x7fa12345,0xffa12345,0x7fc12345]
quiet=[base+4*i for base in [BODIES+0x6c,PHYS+0x18] for i in [0,1,2,3,8,9,10,11]]
for j in range(48):
    compare(0x4fe120,PHYS,p=[patch(BODIES+0x6c,'<16I',*[words[(i+j)%len(words)] for i in range(16)]),patch(PHYS+0x34c,'<B',[0,1,255][j%3])],quiet=quiet,label='orientation reversal raw lanes and signaling-NaN quieting',repeat=2)
for player,flag,send in itertools.product(['local','remote','hidden','missing'],[0,1,255,256,257,0xffffffff],[0,1,256,257]):
    compare(0x511390,FLIP,[0x200,flag,0xabcdef01,send],p=[patch(FLIP+0x18,'<B',177)],net={'player':player},label='board rotation raw flag and send bytes with player gates',repeat=2)
for slot,peer,active in itertools.product([0,1],[0,1,8],[False,True]):
    compare(0x511390,FLIP,[0x200,128,0,1],net={'slot':slot,'peer':peer,'active':active},label='board rotation actual network queue fanout')
for old,pending,slot in itertools.product([0,1,255],itertools.product([0,1],repeat=3),[0,1]):
    compare(0x511570,FLIP,p=[patch(FLIP+0x18,'<4B',old,*pending),patch(PHYS+0x34c,'<B',3)],net={'slot':slot},label='all three pending flags and repeated completion',repeat=2)
for player,peer in itertools.product(['local','remote'],[0,1,8]):
    compare(0x511570,FLIP,p=[patch(FLIP+0x18,'<4B',255,255,255,255)],net={'player':player,'peer':peer},label='pending nonboolean flags with network queue gates')
coverage={};pe=load();md=Cs(CS_ARCH_X86,CS_MODE_32)
for at,n in ranges.items():
    ins=list(md.disasm(pe.get_data(at-0x400000,n),at));missing=[hex(i.address) for i in ins if not hits[i.address]]
    coverage[hex(at)]={'total':len(ins),'covered':len(ins)-len(missing),'missing':missing}
assert all(not row['missing'] for row in coverage.values()),coverage
scope='Recovered orientation reversal4fe120, board-rotated setter511390 and complete pending flip511570. Actual player lookup, animation flips, queue allocation/payloads and live component fields execute. Raw x87 negation lanes retain exact quiet-bit behavior. Integrated into the main module; the complete playable level remains unfinished.'
fixture={'base':BASE,'memory':'pending-flip-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'native_callbacks':[{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]}
path=draft/'pending-flip-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(draft/fixture['memory']).write_bytes(initial)
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'instruction_coverage':coverage,'rotation_packets':rotation_packets,'scope':scope}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('Original pending flip',len(labels),coverage,flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_pending_flip_wasm.mjs')],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [draft/'pending-flip-fixtures.json',draft/fixture['memory']]}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS pending flip',len(labels),sum(oracle.counts.values()))
