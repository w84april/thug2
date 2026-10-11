"""Compare bytecode boundary helpers on synthetic data and real training QB files.

Real archive members must match the existing original-LZSS oracle hashes. Token
offsets are derived by executing the original x86, never by the recovered code.
Traversal is not loading or executing scripts.
"""
import ctypes,hashlib,json,random,struct,subprocess
from collections import Counter
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_MEM_WRITE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EIP,UC_X86_REG_ESP
from specimen import ROOT,SHA256,load
from prx import entries,decoded_size
out=ROOT/'local/validation/collision';report_path=out.parent/'script-tokens.json';report_path.unlink(missing_ok=True)
BASE,CAPACITY,STACK,STOP=0x1800000,0x200000,0x3000000,0x3f00000
rng=random.Random(0x46f690);memory=bytearray(b'\xad'*0x10000);samples=[]
def add(data):
    at=BASE+len(memory);memory.extend(data);memory.extend(b'\xad'*((16-len(memory)%16)%16+16));return at
def word(v):return struct.pack('<I',v&0xffffffff)
def token(t,v=0):
    if t in [0x1b,0x1c]:return bytes([t])+word(v)+b'\x03\x04\x05\x06\x24\x00'*8
    if t==0x2b:return bytes([t])+word(v)+b'\xffname-\x03\x24\0'
    return bytes([t])+word(v)+bytes(range(1,32))
functions={
 '0x46f690':{'name':'thug_script_next_token'},
 '0x46f7e0':{'name':'thug_script_read_word'},
 '0x46fd60':{'name':'thug_script_skip_value','eax_argument':True},
 '0x46f920':{'name':'thug_script_skip_script'}}
for t in range(256):
    for alignment in range(4):
        at=add(b'\xad'*alignment+token(t,[0,1,0xffffffff,0x80000000][alignment]))+alignment
        samples.append((0x46f690,at))
        if t not in [3,5]:samples.append((0x46fd60,at))
for i in range(1024):
    at=add(bytes(rng.randrange(256) for _ in range(16)))+i%4;samples.append((0x46f7e0,at))
for depth in [1,2,3,8,32,64]:
    for t in [3,5]:
        for other in [b'',b'\x03\x05\x06\x04']:
            payload=b'\x1b'+word(6)+b'\x03\x04\x05\x06\x24\0'
            body=bytes([t])*depth+other+payload+bytes([t+1])*depth+b'\x01\0'
            samples.append((0x46fd60,add(body)))
for suffix in [b'\x01',b'\x02'+word(123),b'\x02'+word(123)+b'\x02'+word(456),b'\0']:
    for n in [0,1,5,64]:
        body=(b'\x16'+word(0x24242424)+b'\x1b'+word(4)+b'A\x24B\0')*n+b'\x24'+suffix+b'\0'
        samples.append((0x46f920,add(body)))

lib=ctypes.CDLL(str(ROOT/'local/validation/lzss.dylib'))
lib.thug_lzss_decode_unchecked.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_void_p,ctypes.c_uint32]
lib.thug_lzss_decode_unchecked.restype=ctypes.c_void_p
lzss=json.loads((ROOT/'local/validation/lzss.json').read_text())
expected={(a['name'],m['name']):m['sha256'] for a in lzss['archives'] for m in a['members']}
assets=[]
for archive in sorted((ROOT/'local/game-files/Game/Data/pre').glob('TR*.prx')):
    raw=archive.read_bytes()
    for entry in entries(raw):
        if not entry.name.lower().endswith('.qb'):continue
        if entry.compressed:
            assert decoded_size(entry.payload)==entry.size
            state=ctypes.create_string_buffer(4096);destination=ctypes.create_string_buffer(entry.size)
            end=lib.thug_lzss_decode_unchecked(state,entry.payload,destination,len(entry.payload))
            assert end-ctypes.addressof(destination)==entry.size;data=destination.raw
        else:data=entry.payload
        digest=hashlib.sha256(data).hexdigest();assert digest==expected[archive.name,entry.name]
        assets.append({'archive':archive.name,'archive_sha256':hashlib.sha256(raw).hexdigest(),
            'member':entry.name,'size':len(data),'sha256':digest,'address':add(data),'data':data})
assert len(memory)<CAPACITY
initial=bytes(memory);(out/'script-tokens-memory.bin').write_bytes(initial)
pe=load();cpu=Uc(UC_ARCH_X86,UC_MODE_32)
cpu.mem_map(0x400000,(pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095);cpu.mem_write(0x400000,pe.get_memory_mapped_image())
for at,size in [(BASE,CAPACITY),(STACK,0x20000),(STOP,4096)]:cpu.mem_map(at,size)
cpu.mem_write(BASE,initial)
def reject_write(cpu,access,address,size,value,user):raise AssertionError(('bytecode write',hex(address),size))
cpu.hook_add(UC_HOOK_MEM_WRITE,reject_write,begin=BASE,end=BASE+CAPACITY-1)
counts=Counter();cases=[]
def call(fn,pointer):
    sp=STACK+0x18000;cpu.mem_write(sp,struct.pack('<II',STOP,pointer));cpu.reg_write(UC_X86_REG_ESP,sp)
    cpu.reg_write(UC_X86_REG_EAX,pointer if fn==0x46fd60 else 0xadadadad)
    cpu.emu_start(fn,STOP,count=10000000)
    assert cpu.reg_read(UC_X86_REG_EIP)==STOP and cpu.reg_read(UC_X86_REG_ESP)==sp+4,(hex(fn),hex(pointer))
    result=cpu.reg_read(UC_X86_REG_EAX);cases.append([hex(fn),pointer,result]);counts[functions[hex(fn)]['name']]+=1
    return result
for fn,pointer in samples:call(fn,pointer)
for asset in assets:
    pointer=start=asset['address'];data=asset.pop('data');end=start+len(data);tokens=Counter();value_skips=script_skips=0
    while pointer<end:
        t=data[pointer-start];tokens[hex(t)]+=1
        next_pointer=call(0x46f690,pointer)
        if t==0:
            assert next_pointer==pointer and pointer==end-1,(asset['member'],'trailing bytes',end-pointer)
            break
        assert pointer<next_pointer<=end,(asset['member'],pointer-start,hex(t),next_pointer-start)
        if t in [3,5]:
            skipped=call(0x46fd60,pointer);assert pointer<skipped<=end;value_skips+=1
        elif t==0x23:
            skipped=call(0x46f920,pointer);assert pointer<skipped<=end;script_skips+=1
        elif t in [2,0x16,0x17,0x18,0x1a,0x2e,0x43,0x44,0x46]:call(0x46f7e0,pointer+1)
        pointer=next_pointer
    assert pointer==end-1 and data[-1]==0,asset['member']
    asset.update(tokens=dict(tokens),token_count=sum(tokens.values()),compound_skips=value_skips,script_skips=script_skips,
        terminator_offset=pointer-start)
    print('Traversed',asset['member'],asset['token_count'],'tokens',flush=True)
assert bytes(cpu.mem_read(BASE,len(initial)))==initial
scope='Four original bytecode boundary/read helpers. Every token byte, unaligned words, unsigned offset wrap, balanced nested blocks, embedded delimiters and exactly one optional numbered line after END_SCRIPT. Complete sequential traversal to the final EOF byte of eight training-archive QB files, with compound-value and script-end skips at real token boundaries. Read-only source memory; valid terminated inputs. This is not a QB loader, evaluator or script executor.'
fixture={'base':BASE,'memory':'script-tokens-memory.bin','functions':functions,'cases':cases,'assets':assets,'scope':scope}
path=out/'script-tokens-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
subprocess.run(['node',str(ROOT/'tools/verify_script_tokens_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(counts),'assets':assets,'scope':scope,
 'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
 'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/'script-tokens-memory.bin']},
 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(counts))
