"""Compare skater up-vector changes and matrix repair with original x86 code.

The oracle executes every callee, including static/moving collision. Read-only
instruction hooks count branch coverage; they do not replace game behavior.
"""
import hashlib,json,math,random,struct,subprocess
from collections import Counter
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EIP,UC_X86_REG_ESP,UC_X86_REG_FPCW
from specimen import ROOT,SHA256,load

out=ROOT/'local/validation/collision';report_path=out.parent/'orientation.json';report_path.unlink(missing_ok=True)
previous=json.loads((out/'skater-fixtures.json').read_text());a=previous['addresses'].copy();base=previous['loader']
a.update(matrix=0x2002000,left=0x2002100,right=0x2002200,context=0x1900000)
DATA,GRID,SCENE,SCENES,RUNTIME,NODES,OWNERS,REFS=[a[k] for k in ('data','grid','scene','scenes','runtime','nodes','owners','refs')]
BODY,PHYSICS,HEAP,CONTEXT,MATRIX,LEFT,RIGHT=[a[k] for k in ('body','physics','heap','context','matrix','left','right')]
STACK,STOP,QUERY_STATE,STAMP=0x3000000,0x3f00000,0x691968,0x693998
pe=load();cpu=Uc(UC_ARCH_X86,UC_MODE_32)
cpu.mem_map(0x400000,(pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095);cpu.mem_write(0x400000,pe.get_memory_mapped_image())
for at,size in [(0,4096),(DATA,0xa00000),(0x2000000,0x600000),(STACK,0x20000),(STOP,4096)]:cpu.mem_map(at,size)
rng=random.Random(0x4fe860);counts=Counter();events=Counter()
fixture={'addresses':a,'loader':base,'comparisons':[],'matrices':[],'world':[],
    'owners':previous['owners'],'references':previous['references']}
def raw(at,n):return bytes(cpu.mem_read(at,n))
def put(at,fmt,*values):cpu.mem_write(at,struct.pack(fmt,*values))
def floats(values):return struct.pack('<'+'f'*len(values),*values)
def fbits(n):return struct.unpack('<I',struct.pack('<f',n))[0]
def call(fn,this,args=(),cleanup=0):
    sp=STACK+0x18000;put(sp,'<'+'I'*(len(args)+1),STOP,*args)
    cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,this);cpu.reg_write(UC_X86_REG_FPCW,0x7f)
    cpu.emu_start(fn,STOP,count=5000000)
    assert cpu.reg_read(UC_X86_REG_EIP)==STOP and cpu.reg_read(UC_X86_REG_ESP)==sp+4+cleanup,hex(fn)
    assert raw(0,4)==bytes(4),'Exception chain not restored'
    return cpu.reg_read(UC_X86_REG_EAX)

special=[0.,-0.,1.,-1.,float('inf'),float('-inf'),float('nan')]
comparisons=[([x,0,0,1],[y,0,0,1]) for x in special for y in special]
for i in range(1024):
    left=[rng.uniform(-1e4,1e4) for _ in range(4)];right=left[:]
    if i%3:right[i%4]=rng.choice(special+[rng.uniform(-1e4,1e4)])
    comparisons.append((left,right))
for left,right in comparisons:
    left=floats(left);right=floats(right);cpu.mem_write(LEFT,left);cpu.mem_write(RIGHT,right)
    returned=call(0x4a86d0,LEFT,[RIGHT],4)&255
    assert raw(LEFT,16)==left and raw(RIGHT,16)==right
    fixture['comparisons'].append({'left':left.hex(),'right':right.hex(),'returned':returned})

identity=[1,0,0,0,0,1,0,0,0,0,1,0,7,8,9,1]
matrices=[identity,[0]*16,[1]*16,[-1,0,0,9,0,1,0,8,0,0,1,7,3,4,5,6]]
for n in [float('nan'),float('inf'),float('-inf'),-0.]:
    m=identity[:];m[0]=n;matrices.append(m)
for i in range(512):
    m=[rng.uniform(-10,10) for _ in range(16)]
    if i%4==0:m[4:7]=[x*(1+2**-20) for x in m[:3]]
    matrices.append(m)
for values in matrices:
    for axis in range(3):
        initial=floats(values);cpu.mem_write(MATRIX,initial+b'\xad'*16)
        assert call(0x405170,MATRIX,[axis],4)==MATRIX
        assert raw(MATRIX+64,16)==b'\xad'*16
        assert raw(MATRIX+axis*16,16)==initial[axis*16:axis*16+16] and raw(MATRIX+48,16)==initial[48:64]
        fixture['matrices'].append({'input':initial.hex(),'axis':axis,'output':raw(MATRIX,64).hex()})

def observe(uc,address,size,user):
    if address==0x4172f0:events['probes']+=1
    elif address==0x4fe93a:events['probe_hits']+=bool(uc.reg_read(UC_X86_REG_EAX)&255)
    elif address==0x405170:events['matrix_updates']+=1
for address in [0x4172f0,0x4fe93a,0x405170]:cpu.hook_add(UC_HOOK_CODE,observe,begin=address,end=address)
# Matrix helper blocks were translated by the independent checks above. Rebuild
# those blocks so the subsequently installed coverage hooks are present.
cpu.ctl_flush_tb()
cpu.mem_write(DATA,(out/base['loaded']).read_bytes());cpu.mem_write(GRID,(out/base['grid']).read_bytes());heap=(out/base['heap']).read_bytes()
cpu.mem_write(SCENE,b'\0'*0xd4+struct.pack('<I',GRID));put(SCENES,'<8I',0,SCENE,0,SCENES+16,0,0xffffffff,0,SCENES+16)
put(0x6fa7ec,'<I',SCENES);put(0x691984,'<I',NODES);put(0x691974,'<I',0);put(0x7ce5d8,'<I',CONTEXT)
cpu.mem_write(0x67c6b8,struct.pack('<2048H',*range(2048)))
for j in range(3):put(NODES+j*16,'<4I',0,RUNTIME+j*0x100,0,NODES+(j+1)*16)
put(NODES+48,'<4I',0,0xffffffff,0,NODES+48)

def world(test,index,variant,up,mode,unchanged=False):
    events.clear()
    cpu.mem_write(HEAP,heap);cpu.mem_write(OWNERS,bytes.fromhex(previous['owners']));cpu.mem_write(REFS,bytes.fromhex(previous['references']))
    cpu.mem_write(RUNTIME,bytes.fromhex(test['actors']));body=bytes.fromhex(test['body']);cpu.mem_write(BODY,body+b'\xad'*16)
    physics=bytearray(bytes.fromhex(test['physics']))
    physics[0x58:0x68]=floats([rng.uniform(-3,3) for _ in range(4)])
    physics[0x68:0x78]=floats(up if unchanged else [rng.uniform(-1,1) for _ in range(4)])
    cpu.mem_write(PHYSICS,bytes(physics)+b'\xad'*16)
    context=b'\xad'*64+struct.pack('<I',mode);cpu.mem_write(CONTEXT,context)
    cpu.mem_write(QUERY_STATE,bytes.fromhex(test['initial_state']));cpu.mem_write(STAMP,bytes([test['stamp']]));cpu.mem_write(0x691910,b'\0')
    call(0x4fe860,PHYSICS,[fbits(x) for x in up],16)
    assert events['matrix_updates']==int(raw(PHYSICS+0x88,4)==struct.pack('<f',1)), 'Coverage hook missed an update'
    assert raw(PHYSICS+0x318,16)==b'\xad'*16 and raw(BODY+0xbc,16)==b'\xad'*16
    assert raw(CONTEXT,68)==context and raw(OWNERS,96).hex()==previous['owners'] and raw(REFS,48).hex()==previous['references']
    fixture['world'].append({'object':test['object'],'variant':variant,'up':floats(up).hex(),'mode':mode,
        'actors':test['actors'],'actors_after':raw(RUNTIME,0x300).hex(),'body':body.hex(),'body_after':raw(BODY,0xbc).hex(),
        'physics':bytes(physics).hex(),'physics_after':raw(PHYSICS,0x318).hex(),
        'initial_state':test['initial_state'],'state':raw(QUERY_STATE,12).hex(),'stamp':test['stamp'],'final_stamp':raw(STAMP,1)[0],
        'stamps':bytes(raw(base['instances']+i*24+10,1)[0] for i in range(base['count'])).hex(),'events':dict(events)})
    counts['updates']+=1;counts.update(events)
    if not events['matrix_updates']:counts['unchanged_targets']+=1

for index,test in enumerate(previous['world'][::3]):
    direction=list(struct.unpack_from('<4f',bytes.fromhex(test['body']),0x8c));direction[3]=1
    world(test,index,'mesh_direction',direction,0)
    world(test,index,'context_bypass',direction,0xd443a2bc)
    world(test,index,'unchanged_up',[0,1,0,1],0,True)
    up=direction[:];up[1]=abs(up[1])+.1;up[3]=[-1,0,.5,1][index%4]
    world(test,index,'positive_y',up,0)
    if index%100==0:print(index,'training objects',dict(counts),flush=True)
# Edge values with the context bypass: avoid passing invalid geometry into a probe.
for index in range(64):
    up=[rng.uniform(-1,1),rng.choice(special),rng.uniform(-1,1),rng.choice([-0.,0.,1.,-1.])]
    world(previous['world'][0],index,'special_up',up,0xd443a2bc,index%2==0)
path=out/'orientation-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
subprocess.run(['node',str(ROOT/'tools/verify_orientation_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(counts),'vector_comparisons':len(fixture['comparisons']),
    'matrix_cases':len(fixture['matrices']),'x87_control_word':'0x007f','runtime_control_word_observed_in_game':False,
    'scope':'Original up-vector update with loader-built training collision and constructed moving objects; context identifier meaning and full movement loop remain unrecovered.',
    'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
    'fixture_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
    'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report['counts'],indent=2))
