"""End-to-end original probe / static level / rigid moving scene comparison.

Uses the original loader-built training grid, recovered geometry and rigid objects.
Only callbacks are instrumented. Cached candidate lists and intrusive owner-reference
lists are constructed fixtures; their original builders are not claimed recovered.
"""
import hashlib
import json
import struct
import subprocess
from collections import Counter
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_ECX, UC_X86_REG_EIP, UC_X86_REG_ESP, UC_X86_REG_FPCW
from specimen import ROOT, SHA256, load

out = ROOT / 'local/validation/collision'; report_path = out.parent / 'probes.json'; report_path.unlink(missing_ok=True)
loading = json.loads((out / 'loading-fixtures.json').read_text()); base = loading['datasets'][0]
moving = json.loads((out / 'moving-fixtures.json').read_text())
DATA, GRID, SCENE, SCENES = 0x1000000, 0x1200000, 0x1400000, 0x1402000
RUNTIME, NODES, OWNERS, REFS, CACHE = 0x1500000, 0x1501000, 0x1502000, 0x1503000, 0x1504000
SEGMENT, RESULT, CONTROL, STATE, PROBE, LOG, HEAP = 0x2000100, 0x2000200, 0x2000400, 0x2000500, 0x2000c00, 0x2100000, 0x2400000
STACK, STOP, CALLBACK, PROBE_CALLBACK = 0x3000000, 0x3f00000, 0x3f00100, 0x3f00200
SELECT, QUERY_STATE, STAMP = 0x691910, 0x691968, 0x693998
pe = load(); cpu = Uc(UC_ARCH_X86, UC_MODE_32)
cpu.mem_map(0x400000, (pe.OPTIONAL_HEADER.SizeOfImage + 4095) & ~4095)
cpu.mem_write(0x400000, pe.get_memory_mapped_image())
for at,size in [(0,4096),(DATA,0x600000),(0x2000000,0x600000),(STACK,0x20000),(STOP,4096)]: cpu.mem_map(at,size)
cpu.mem_write(DATA, (out / base['loaded']).read_bytes()); cpu.mem_write(GRID, (out / base['grid']).read_bytes())
heap = (out / base['heap']).read_bytes()
cpu.mem_write(SCENE, b'\0'*0xd4 + struct.pack('<I',GRID))
cpu.mem_write(SCENES, struct.pack('<8I',0,SCENE,0,SCENES+16,0,0xffffffff,0,SCENES+16))
cpu.mem_write(0x6fa7ec, struct.pack('<I', SCENES)); cpu.mem_write(0x67c6b8, struct.pack('<2048H',*range(2048)))
cpu.mem_write(CALLBACK,b'\xc3'); cpu.mem_write(PROBE_CALLBACK,b'\xc3')
fixture = {'addresses': {'data':DATA,'grid':GRID,'scene':SCENE,'scenes':SCENES,'runtime':RUNTIME,'nodes':NODES,
    'owners':OWNERS,'refs':REFS,'cache':CACHE,'segment':SEGMENT,'result':RESULT,'control':CONTROL,'state':STATE,
    'probe':PROBE,'log':LOG,'heap':HEAP,'callback':CALLBACK,'probe_callback':PROBE_CALLBACK},
    'loader':base,'cases':[]}
counts = Counter(); observations=[]; runtime_bytes=bytearray()


def raw(at,n): return bytes(cpu.mem_read(at,n))
def word(at): return struct.unpack('<I',raw(at,4))[0]
def write_word(at,value): cpu.mem_write(at,struct.pack('<I',value))


def call(fn,this,args,cleanup=0):
    sp=STACK+0x18000; cpu.mem_write(sp,struct.pack('<'+'I'*(len(args)+1),STOP,*args))
    cpu.reg_write(UC_X86_REG_ESP,sp); cpu.reg_write(UC_X86_REG_ECX,this); cpu.reg_write(UC_X86_REG_FPCW,0x007f)
    cpu.emu_start(fn,STOP,count=5000000)
    assert cpu.reg_read(UC_X86_REG_EIP)==STOP and cpu.reg_read(UC_X86_REG_ESP)==sp+4+cleanup,hex(fn)
    return cpu.reg_read(UC_X86_REG_EAX)


def callback(uc,at,size,context):
    pointer=word(uc.reg_read(UC_X86_REG_ESP)+4); mode=word(CONTROL)
    if at==PROBE_CALLBACK:
        assert pointer==PROBE
        observations.append(raw(PROBE,176))
        result=PROBE+36
        if mode&1:
            for offset in (0x2f,0x4a,0x4b): cpu.mem_write(result+offset,bytes([raw(result+offset,1)[0]^0x5a]))
            cpu.mem_write(result+0x24,struct.pack('<f',.25)); cpu.mem_write(result,struct.pack('<f',42))
        if mode&4:
            x=struct.unpack('<f',raw(PROBE,4))[0]; cpu.mem_write(PROBE,struct.pack('<f',x+1000)); write_word(PROBE+0xac,0)
        if mode&8: cpu.mem_write(result+0x48,b'\0')
    else:
        assert pointer==RESULT
        value=raw(RESULT,80); observations.append(value)
        if mode&1: cpu.mem_write(RESULT,bytes(v^0x5a if i<0x3c or i>=0x40 else v for i,v in enumerate(value)))
    if mode&2: cpu.mem_write(SELECT,bytes([raw(SELECT,1)[0]^1]))


for at in (CALLBACK,PROBE_CALLBACK): cpu.hook_add(UC_HOOK_CODE,callback,begin=at,end=at)
first_cases={}
for case in moving['cases']: first_cases.setdefault(case['object'],case)
helpers = moving['helpers'][::20]
for obj_index, helper in enumerate(helpers):
    object_offset=helper['object']; index=(object_offset-32)//64
    segment=bytes.fromhex(first_cases[object_offset]['segment'])
    # Misses and both cache/live-list paths are explicit variants.
    for variant in range(20):
        observations.clear(); cpu.mem_write(HEAP,heap); cpu.mem_write(RUNTIME,b'\xad'*0x5000)
        actor_pointers=[RUNTIME+i*0x100 for i in range(3)]
        for j,actor in enumerate(actor_pointers):
            cpu.mem_write(actor,bytes.fromhex(helper['initialized']))
            cpu.mem_write(actor+0x10,struct.pack('<4f',0,(j-1)*16,0,1))
            write_word(actor+0xa0,0 if variant==18 else OWNERS+j*32)
            cpu.mem_write(actor+8,struct.pack('<H',2 if variant in (5,8) or (variant==6 and j==1) else 0))
            # Cached entries must carry current bounds even though the live list
            # computes these lazily. Keep dirty set to test both code paths.
            call(0x40b390,actor,[])
        order=[actor_pointers[2],0,actor_pointers[0],actor_pointers[1],actor_pointers[1]]
        for j,actor in enumerate(order): cpu.mem_write(NODES+j*16,struct.pack('<4I',0,actor,0,NODES+(j+1)*16))
        sentinel=NODES+len(order)*16; cpu.mem_write(sentinel,struct.pack('<4I',0,0xffffffff,0,sentinel))
        head=sentinel if variant==7 else NODES; write_word(0x691984,head)
        for j in range(3): cpu.mem_write(OWNERS+j*32,struct.pack('<8I',0,0,0,0,0,0xabc000+j,0,0))
        ref=PROBE+0x98
        chain=[ref,REFS,REFS+16] if variant%3==0 else ([REFS,ref,REFS+16] if variant%3==1 else [REFS,REFS+16,ref])
        if variant>=18:
            chain=[REFS,REFS+16]
            cpu.mem_write(ref,b'\0'*12)
        for j,at in enumerate(chain): cpu.mem_write(at,struct.pack('<3I',OWNERS,chain[j-1] if j else 0,chain[j+1] if j+1<len(chain) else 0))
        reference=raw(ref,12); write_word(OWNERS+4,chain[0])
        bounds=struct.pack('<8f',-1e6,-1e6,-1e6,1,1e6,1e6,1e6,1)
        if variant==9: bounds=struct.pack('<8f',-1,-1,-1,1,1,1,1,1)
        cpu.mem_write(CACHE,bounds)
        static=base['instances']+index*24
        cpu.mem_write(CACHE+32,struct.pack('<2I',static,DATA+object_offset+16))
        for j,actor in enumerate(actor_pointers): cpu.mem_write(CACHE+40+j*8,struct.pack('<2I',actor,0 if variant==10 and j==1 else actor+0xac))
        write_word(CACHE+0xfc4,1); write_word(CACHE+0xfc8,0 if variant==11 else 3)
        cache=CACHE if variant>=8 else 0
        default_cache=cache if variant in (12,13) else 0
        write_word(0x691974,default_cache)
        local_cache=0 if default_cache else cache
        local_segment=segment
        if variant==17: local_segment=struct.pack('<8f',1e5,1e5,1e5,1,1e5,1e5+1,1e5,1)
        prior=bytearray(b'\xad'*80)
        struct.pack_into('<8fIfHH',prior,0,1,2,3,4,5,6,7,8,17,.3 if variant%2 else .8,0xffff if variant==16 else 0,0)
        struct.pack_into('<I',prior,0x3c,0)
        prior[0x48]=variant&1
        probe=bytearray(b'\xad'*176); probe[:32]=local_segment; probe[36:116]=prior
        mode=[0,1,2,4,8,3,6,9][variant%8] if variant!=0 else -1
        kind='moving' if variant<3 else ('farthest' if variant==3 else 'probe')
        struct.pack_into('<I',probe,32,PROBE_CALLBACK if mode>=0 else 0)
        probe[0x98:0xa4]=reference; struct.pack_into('<I',probe,0xac,local_cache)
        cpu.mem_write(PROBE,bytes(probe)+b'\xad'*16); cpu.mem_write(RESULT,bytes(prior)+b'\xad'*16)
        cpu.mem_write(SEGMENT,local_segment); write_word(CONTROL,max(mode,0))
        selection=variant&1; cpu.mem_write(SELECT,bytes([selection])); stamp=(variant*17)&255; cpu.mem_write(STAMP,bytes([stamp]))
        state=struct.pack('<3I',0x12345678,0xabcdef01,0x13579bdf); cpu.mem_write(QUERY_STATE,state)
        offset=len(runtime_bytes); runtime_bytes.extend(raw(RUNTIME,0x5000))
        check_moving=int(variant!=15); farthest=variant%2
        if kind=='probe': returned=call(0x4172f0,PROBE,[check_moving,farthest],8)
        else: returned=call(0x411ae0 if kind=='farthest' else 0x4118c0,0,[SEGMENT,RESULT,CALLBACK if mode>=0 else 0,cache])
        runtime_bytes.extend(raw(RUNTIME,0x5000))
        assert raw(PROBE+176,16)==raw(RESULT+80,16)==b'\xad'*16
        assert raw(SEGMENT,32)==local_segment
        fixture['cases'].append({'kind':kind,'runtime_offset':offset,'actors':actor_pointers,'head':head,
            'segment':local_segment.hex(),'initial_probe':bytes(probe).hex(),'initial_result':bytes(prior).hex(),
            'initial_state':state.hex(),'cache':cache,'default_cache':default_cache,'mode':mode,'selection':selection,
            'stamp':stamp,'check_moving':check_moving,'farthest':farthest,'returned':returned,
            'probe':raw(PROBE,176).hex(),'result':raw(RESULT,80).hex(),'state':raw(QUERY_STATE,12).hex(),
            'final_stamp':raw(STAMP,1)[0],'final_selection':raw(SELECT,1)[0],
            'stamps':bytes(raw(base['instances']+i*24+10,1)[0] for i in range(base['count'])).hex(),
            'callbacks':b''.join(observations).hex()})
        counts[kind]+=1; counts['callbacks']+=len(observations); counts['nonzero_returns']+=int(returned!=0)
        if kind=='probe': counts['attached_moving_objects']+=int(word(PROBE+0x98)!=0)
    if obj_index%10==0: print('probe object',obj_index,dict(counts),flush=True)

fixture_path=out/'probe-fixtures.json'; fixture_path.write_text(json.dumps(fixture,separators=(',',':')))
(out/'probe-runtime.bin').write_bytes(runtime_bytes)
compiler=ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang'
command=[str(compiler),'--target=wasm32-unknown-unknown','-O2','-ffreestanding','-fno-builtin','-nostdlib',
    '-Wl,--no-entry,--export-all,--import-memory,--global-base=8388608',
    '-Wl,-z,stack-size=65536,--initial-memory=67108864,--max-memory=134217728',
    str(ROOT/'tools/probe_callback_fixture.c'),'-o',str(out/'probe-callback-fixture.wasm')]
subprocess.run(command,check=True)
subprocess.run(['node',str(ROOT/'tools/verify_probes_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(counts),
    'scope':'Skater collision-probe wrapper with original loader-built static grid and rigid moving objects; constructed cache/reference lists and instrumented callbacks; no skater update loop.',
    'x87_control_word':'0x007f','runtime_control_word_observed_in_game':False,
    'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
    'fixture_sha256':hashlib.sha256(fixture_path.read_bytes()).hexdigest(),
    'runtime_sha256':hashlib.sha256(runtime_bytes).hexdigest(),'callback_build_command':command,
    'callback_sha256':hashlib.sha256((out/'probe-callback-fixture.wasm').read_bytes()).hexdigest(),
    'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()},
    'byte_matching':'not attempted'}
report_path.write_text(json.dumps(report,indent=2)+'\n'); print(json.dumps({'result':'pass','counts':dict(counts)},indent=2))
