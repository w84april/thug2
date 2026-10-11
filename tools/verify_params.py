"""Original QB symbol/parameter accessors on valid constructed linked graphs."""
import hashlib,json,random,struct,subprocess
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EIP,UC_X86_REG_ESP,UC_X86_REG_FPCW
from specimen import ROOT,SHA256,load
out=ROOT/'local/validation/collision'; report_path=out.parent/'params.json'; report_path.unlink(missing_ok=True)
BASE,OUTPUT,STACK,STOP=0x1800000,0x2000600,0x3000000,0x3f00000
pe=load();cpu=Uc(UC_ARCH_X86,UC_MODE_32)
cpu.mem_map(0x400000,(pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095);cpu.mem_write(0x400000,pe.get_memory_mapped_image())
for at,size in [(BASE,0x20000),(0x2000000,0x10000),(STACK,0x20000),(STOP,4096)]:cpu.mem_map(at,size)
image=bytearray(0x20000); cursor=0x4000; rng=random.Random(0x4764b0); names=[]

def allocate(size):
    global cursor
    at=BASE+cursor; cursor+=size; assert cursor<=len(image); return at

def put(at,fmt,*values):struct.pack_into(fmt,image,at-BASE,*values)
def word(at):return struct.unpack_from('<I',image,at-BASE)[0]
def symbol(name,type_,value):
    at=allocate(20); bucket=BASE+(name&0xfff)*4
    put(at,'<BBHIIII',0xa5,type_,0xabcd,name,0x12345678,value,word(bucket));put(bucket,'<I',at)
    names.append(name);return at

def structure(components):
    at=allocate(8); entries=[allocate(16) for _ in components];put(at,'<II',0xabcdef01,entries[0] if entries else 0)
    for i,(name,type_,value) in enumerate(components):put(entries[i],'<BBHIII',(type_<<1)|(i&1),0xad,0xadad,name,value,entries[i+1] if i+1<len(entries) else 0)
    return at

values=[0,0x7fffffff,0x80000000,16777217,0xff000001,0x3f800000,0x80000000,0x7fc12345]
for i in range(64):symbol(0x10000+i*0x1000+17,i%15,values[i%len(values)])
for i in range(8):symbol(0x80000000+i*0x1000+17,13,names[3] if i==0 else 0x80000000+(i-1)*0x1000+17)
symbol(0xdead1234,13,0xdead9999)
leaf=structure([(0x123,1,16777217),(0x456,2,0x7fc12345),(0,2,0x41400000)])
symbol(0xaaa10001,10,leaf)
nested=structure([(0,13,0xaaa10001),(0x123,2,0x41c80000),(0,13,0xaaa10001)])
symbol(0xaaa10002,10,nested)
roots=[structure([]),leaf,nested,structure([(0x123,2,0x3f800000),(0,13,0xaaa10002),(0x123,4,0x11111111),
    (0x123,2,0x41200000),(0x456,13,0xdead1234)])]
for i in range(64):
    roots.append(structure([(j%4,i%15,values[(i+j)%len(values)]) for j in range(8)] + [(0,13,0xaaa10002),(0x123,13,names[i])]))
image=image[:cursor];cpu.mem_write(BASE,bytes(image));cpu.mem_write(0x6f3624,struct.pack('<I',BASE))
fixture={'addresses':{'base':BASE,'output':OUTPUT},'lookups':[],'cases':[]}

def call(fn,this,args,cleanup=0):
    sp=STACK+0x18000;cpu.mem_write(sp,struct.pack('<'+'I'*(len(args)+1),STOP,*args))
    cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,this);cpu.reg_write(UC_X86_REG_FPCW,0x7f)
    cpu.emu_start(fn,STOP,count=1000000)
    assert cpu.reg_read(UC_X86_REG_EIP)==STOP and cpu.reg_read(UC_X86_REG_ESP)==sp+4+cleanup
    return cpu.reg_read(UC_X86_REG_EAX)

for name in names+[0,0xdead9999,17,0xffffffff]:fixture['lookups'].append([name,call(0x478cf0,0,[name])])
for root in roots:
    for name in [0,1,2,3,0x123,0x456,0xffffffff]:
        for type_ in [0,1,2,4,10,13,15,256]:
            initial=rng.getrandbits(32);cpu.mem_write(OUTPUT,struct.pack('<I',initial)+b'\xad'*16)
            returned=call(0x4764b0,root,[name,type_,OUTPUT],12)&255
            assert bytes(cpu.mem_read(OUTPUT+4,16))==b'\xad'*16
            fixture['cases'].append({'kind':'typed','root':root,'name':name,'type':type_,'initial':initial,
                'returned':returned,'output':struct.unpack('<I',cpu.mem_read(OUTPUT,4))[0]})
        for assert_missing in [0,1]:
            initial=rng.getrandbits(32);cpu.mem_write(OUTPUT,struct.pack('<I',initial)+b'\xad'*16)
            returned=call(0x4766d0,root,[name,OUTPUT,assert_missing],12)&255
            assert bytes(cpu.mem_read(OUTPUT+4,16))==b'\xad'*16
            fixture['cases'].append({'kind':'float','root':root,'name':name,'assert_missing':assert_missing,'initial':initial,
                'returned':returned,'output':struct.unpack('<I',cpu.mem_read(OUTPUT,4))[0]})
assert bytes(cpu.mem_read(BASE,len(image)))==image
(out/'params-memory.bin').write_bytes(image);path=out/'params-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
subprocess.run(['node',str(ROOT/'tools/verify_params_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'lookups':len(fixture['lookups']),'parameter_cases':len(fixture['cases']),
    'scope':'Constructed QB symbol/component graphs: collisions, alias chains, missing aliases, nested structures, last-match precedence and integer/float conversion; no QB file parser.',
    'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
    'fixture_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'memory_sha256':hashlib.sha256(image).hexdigest(),
    'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src/script').glob('*'))},'byte_matching':'not attempted'}
report_path.write_text(json.dumps(report,indent=2)+'\n')
