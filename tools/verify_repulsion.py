"""Complete four-probe obstacle response against training geometry and real x86.

Only initialized Windows TLS/last-error services are modeled for CRT math errors.
"""
import hashlib,json,math,random,struct,subprocess
from collections import Counter
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EIP,UC_X86_REG_ESP,UC_X86_REG_FPCW,UC_X86_REG_MXCSR
from specimen import ROOT,SHA256,load

out=ROOT/'local/validation/collision';report_path=out.parent/'repulsion.json';report_path.unlink(missing_ok=True)
old=json.loads((out/'skater-fixtures.json').read_text());a=old['addresses'].copy();base=old['loader']
a.update(matrix=0x2002000,vector_block=0x2002100,tls=0x2002300)
DATA,GRID,SCENE,SCENES,RUNTIME,NODES,OWNERS,REFS=[a[k] for k in ('data','grid','scene','scenes','runtime','nodes','owners','refs')]
BODY,PHYSICS,SYMBOLS,HEAP,MATRIX,VECTORS,TLS=[a[k] for k in ('body','physics','symbols','heap','matrix','vector_block','tls')]
STACK,STOP,QUERY_STATE,STAMP,OUTPUT=0x3000000,0x3f00000,0x691968,0x693998,0x2002400
pe=load();cpu=Uc(UC_ARCH_X86,UC_MODE_32)
cpu.mem_map(0x400000,(pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095);cpu.mem_write(0x400000,pe.get_memory_mapped_image())
for at,size in [(0,4096),(DATA,0xa00000),(0x2000000,0x600000),(STACK,0x20000),(STOP,4096)]:cpu.mem_map(at,size)
rng=random.Random(0x5055b0);events=Counter();totals=Counter();os_calls=Counter()
fixture={'addresses':a,'loader':base,'helpers':[],'world':[]}
def raw(at,n):return bytes(cpu.mem_read(at,n))
def put(at,fmt,*values):cpu.mem_write(at,struct.pack(fmt,*values))
def floats(v):return struct.pack('<'+'f'*len(v),*v)
def bits(v):return struct.unpack('<I',struct.pack('<f',v))[0]
def call(fn,this,args=(),cleanup=0,numeric=False):
    sp=STACK+0x18000;put(sp,'<'+'I'*(len(args)+1),STOP+32 if numeric else STOP,*args)
    cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,this)
    cpu.reg_write(UC_X86_REG_FPCW,0x7f);cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
    cpu.emu_start(fn,STOP,count=5000000)
    assert cpu.reg_read(UC_X86_REG_EIP)==STOP and cpu.reg_read(UC_X86_REG_ESP)==sp+4+cleanup,hex(fn)
    assert cpu.reg_read(UC_X86_REG_FPCW)==0x7f and raw(0,4)==bytes(4)
    return raw(OUTPUT,8).hex() if numeric else cpu.reg_read(UC_X86_REG_EAX)
put(0x684fe4,'<I',0x5df4ac)
cpu.mem_write(STOP+32,b'\xdd\x1d'+struct.pack('<I',OUTPUT)+b'\xe9'+struct.pack('<i',-43))
GET_ERROR,GET_TLS,SET_ERROR=STOP+0x100,STOP+0x110,STOP+0x120
for slot,target in [(0x6450d4,GET_ERROR),(0x7db10c,GET_TLS),(0x64516c,SET_ERROR)]:put(slot,'<I',target)
put(0x68ef14,'<I',7)
for at,n in [(GET_ERROR,0),(GET_TLS,4),(SET_ERROR,4)]:cpu.mem_write(at,b'\xc2'+struct.pack('<H',n))
last_error=0x12345678
def os_service(uc,address,size,user):
    global last_error
    sp=uc.reg_read(UC_X86_REG_ESP)
    if address==GET_ERROR:uc.reg_write(UC_X86_REG_EAX,last_error);os_calls['GetLastError']+=1
    elif address==GET_TLS:
        assert struct.unpack('<I',uc.mem_read(sp+4,4))[0]==7
        uc.reg_write(UC_X86_REG_EAX,TLS);os_calls['TLS_read']+=1
    else:last_error=struct.unpack('<I',uc.mem_read(sp+4,4))[0];os_calls['SetLastError']+=1
for address in [GET_ERROR,GET_TLS,SET_ERROR]:cpu.hook_add(UC_HOOK_CODE,os_service,begin=address,end=address)

# Helper cases cover collapsed projections, overlap, wide exponents and W writes.
special=[[0,0,0,1],[1,0,0,7],[0,1,0,1],[0,0,1,0],[1e-30,2e-30,-1e-30,1],
    [1e30,2e30,-1e30,1],[float('nan'),1,0,1],[float('inf'),0,1,1]]
for i in range(512):
    v=special[i%len(special)] if i<64 else [rng.uniform(-100,100) for _ in range(4)]
    n=special[(i//len(special))%len(special)] if i<64 else [rng.uniform(-1,1) for _ in range(4)]
    for offset in [-8,0,4,16]:
        block=bytearray(b'\xad'*128);struct.pack_into('<4f',block,48,*v);struct.pack_into('<4f',block,48+offset,*n)
        cpu.mem_write(VECTORS,bytes(block));assert call(0x4060f0,VECTORS+48,[VECTORS+48+offset],4)==VECTORS+48
        fixture['helpers'].append({'kind':'project','offset':offset,'input':block.hex(),'output':raw(VECTORS,128).hex()})
for value in [0,0x80000000,1,0x80000001,0x3f800000,0xbf800000,0x7f800000,0xff800000,0x7fc12345,0x7f812345]+[rng.randrange(2**32) for _ in range(256)]:
    fixture['helpers'].append({'kind':'sign','input':value,'output':call(0x405fd0,0,[value],numeric=True)})
for i in range(512):
    angle=[0.,-0.,math.pi/2,math.pi,1e-30,1e6,float('nan')][i%7] if i<56 else rng.uniform(-100,100)
    matrix=[rng.uniform(-3,3) for _ in range(16)];cpu.mem_write(MATRIX,floats(matrix)+b'\xad'*16)
    assert call(0x405710,MATRIX,[bits(angle)],4)==MATRIX and raw(MATRIX+64,16)==b'\xad'*16
    fixture['helpers'].append({'kind':'rotate','input':floats(matrix).hex(),'angle':bits(angle),'output':raw(MATRIX,64).hex()})

script=bytearray(0x4100)
for i,(name,value) in enumerate([(0x3eede4d3,30),(0xb45b39e2,0)]):
    entry=SYMBOLS+0x4000+i*20;struct.pack_into('<I',script,(name&4095)*4,entry)
    struct.pack_into('<BBHIIII',script,0x4000+i*20,0,2,0,name,0,bits(value),0)
fixture['script_memory']=script.hex();cpu.mem_write(SYMBOLS,bytes(script));put(0x6f3624,'<I',SYMBOLS)
cpu.mem_write(DATA,(out/base['loaded']).read_bytes());cpu.mem_write(GRID,(out/base['grid']).read_bytes());heap=(out/base['heap']).read_bytes()
cpu.mem_write(SCENE,bytes(0xd4)+struct.pack('<I',GRID));put(SCENES,'<8I',0,SCENE,0,SCENES+16,0,0xffffffff,0,SCENES+16)
put(0x6fa7ec,'<I',SCENES);put(0x691984,'<I',NODES);put(0x691974,'<I',0)
cpu.mem_write(0x67c6b8,struct.pack('<2048H',*range(2048)))
for j in range(3):put(NODES+j*16,'<4I',0,RUNTIME+j*0x100,0,NODES+(j+1)*16)
put(NODES+48,'<4I',0,0xffffffff,0,NODES+48)
def timer(config):
    counter,fps,origin,scale,offset=config
    put(0x7d1ec8,'<2I',counter,0xabadcafe);put(0x684fd0,'<I',fps);put(0x696d64,'<I',origin);put(0x67d7c0,'<I',scale);put(0x696d60,'<I',offset)
def observe(uc,address,size,user):
    names={0x501c90:'direction_probes',0x5003a0:'surface_queries',0x44ece0:'timer_reads',0x405710:'matrix_rotations',0x4060f0:'tangent_projections',0x623630:'acos_calls',0x4637c0:'attachments',0x4637e0:'unlinks'}
    if address in names:events[names[address]]+=1
    elif address==0x501d29:events['probe_hits']+=bool(uc.reg_read(UC_X86_REG_EAX)&255)
    elif address==0x505890:events['repulsions']+=1
for address in [0x501c90,0x5003a0,0x44ece0,0x405710,0x4060f0,0x623630,0x4637c0,0x4637e0,0x501d29,0x505890]:cpu.hook_add(UC_HOOK_CODE,observe,begin=address,end=address)
cpu.ctl_flush_tb()
def world(test,index,variant,direct=False):
    global last_error
    cpu.mem_write(HEAP,heap);cpu.mem_write(OWNERS,bytes.fromhex(old['owners']));cpu.mem_write(REFS,bytes.fromhex(old['references']))
    cpu.mem_write(RUNTIME,bytes.fromhex(test['actors']))
    body=bytearray(bytes.fromhex(test['body'])+b'\xad'*16);physics=bytearray(bytes.fromhex(test['physics'])+b'\xad'*(0x410-0x318))
    # A complete orthonormal frame points forward toward the chosen training face.
    side=struct.unpack_from('<3f',body,0x6c);forward=struct.unpack_from('<3f',body,0x8c)
    up=[forward[1]*side[2]-forward[2]*side[1],forward[2]*side[0]-forward[0]*side[2],forward[0]*side[1]-forward[1]*side[0]]
    struct.pack_into('<4f',body,0x7c,*up,0);struct.pack_into('<4f',body,0xac,*[f*20 for f in forward],1)
    physics[0x18:0x58]=body[0x6c:0xac];struct.pack_into('<4f',physics,0x68,*up,0)
    struct.pack_into('<f',physics,0x8c,[1/60,1/30,0,-1/60][index%4])
    distance=[16,80,0,16,80,16][variant%6];strength=[40,10,40,0,-10,80][variant%6]
    struct.pack_into('<4f',physics,0x2ac,1,2,3,7);struct.pack_into('<4f',physics,0x2bc,.75,distance,strength,[0,1.5,-2.5,100][index%4])
    config=[60,bits(60),0,bits(1),0xffffff00 if index%7==0 else 0];timer(config)
    now=(1000+config[-1])&0xffffffff
    age=[0,499,500,501,0xffffffff,0][variant%6]
    times=[(now-age)&0xffffffff]*4;struct.pack_into('<4I',physics,0x328,*times)
    cpu.mem_write(BODY,bytes(body));cpu.mem_write(PHYSICS,bytes(physics));call(0x417760,PHYSICS+0xa8)
    if index%2:
        put(PHYSICS+0x140,'<3I',OWNERS,0,REFS);put(REFS+4,'<I',PHYSICS+0x140);put(OWNERS+4,'<I',PHYSICS+0x140)
    height=[0.,8.,-8.,24.25][index%4];kind=1 if index%3==0 else 2
    value=int(height)&0xffffffff if kind==1 else bits(height)
    cpu.mem_write(SYMBOLS+0x4015,bytes([kind]));put(SYMBOLS+0x4020,'<I',value)
    position=struct.unpack_from('<4f',body,0x4c)
    endpoints=[*position,*[position[i]+forward[i]*80 for i in range(3)],position[3]]
    cpu.mem_write(a['points'],floats(endpoints))
    direction=index%4
    args=[a['points'],a['points']+16,direction]
    if direct and variant%3==0:
        # Inputs overlapping the component's destination segment exercise MOV order.
        cpu.mem_write(PHYSICS+0x204,floats(endpoints));args=[PHYSICS+0x204,PHYSICS+0x214,direction]
    before=raw(PHYSICS,0x410);owners=raw(OWNERS,96);refs=raw(REFS,48)
    cpu.mem_write(QUERY_STATE,bytes.fromhex(test['initial_state']));cpu.mem_write(STAMP,bytes([test['stamp']]));cpu.mem_write(0x691910,b'\0')
    cpu.mem_write(TLS,bytes(0x100));put(TLS+8,'<i',-123);last_error=0x12345678
    events.clear();call(0x501c90 if direct else 0x5055b0,PHYSICS,args if direct else [],12 if direct else 0)
    assert last_error==0x12345678 and raw(BODY+0xbc,16)==b'\xad'*16 and raw(PHYSICS+0x400,16)==b'\xad'*16
    assert raw(a['points'],32)==floats(endpoints)
    fixture['world'].append({'kind':'probe' if direct else 'repulsion','object':test['object'],'variant':variant,'args':args,
        'actors':test['actors'],'actors_after':raw(RUNTIME,0x300).hex(),'body':bytes(body).hex(),'body_after':raw(BODY,len(body)).hex(),
        'physics':before.hex(),'physics_after':raw(PHYSICS,len(physics)).hex(),'owners':owners.hex(),'owners_after':raw(OWNERS,96).hex(),
        'refs':refs.hex(),'refs_after':raw(REFS,48).hex(),'height_kind':kind,'height_value':value,'points':floats(endpoints).hex(),
        'initial_state':test['initial_state'],'state':raw(QUERY_STATE,12).hex(),'stamp':test['stamp'],'final_stamp':raw(STAMP,1)[0],
        'stamps':bytes(raw(base['instances']+i*24+10,1)[0] for i in range(base['count'])).hex(),'timer':config,'events':dict(events),
        'errno':struct.unpack('<i',raw(TLS+8,4))[0]})
    totals['probes' if direct else 'updates']+=1;totals.update(events)
for index,test in enumerate(old['world'][::3]):
    for variant in range(6):world(test,index,variant)
    for variant in [0,1,2,3,4]:world(test,index,variant,True)
    if index%100==0:print(index,'training objects',dict(totals),flush=True)
assert totals['repulsions'] and totals['matrix_rotations'] and totals['attachments'] and totals['probe_hits']
fixture['totals']=dict(totals);path=out/'repulsion-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
subprocess.run(['node',str(ROOT/'tools/verify_repulsion_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(totals),'helper_cases':len(fixture['helpers']),'os_services':dict(os_calls),
    'x87_control_word':'0x007f','mxcsr':'0x1f80','scope':'Complete four-probe obstacle repulsion using original training collision, real timer/parameter/angle callees, and constructed skater states. No full skating loop.',
    'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
    'artifact_hashes':{str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest()},
    'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(totals))
