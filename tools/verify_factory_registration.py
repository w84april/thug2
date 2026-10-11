import hashlib,json,subprocess
"""Original component factory registration, with an explicit callback boundary."""
import itertools,json,random,struct
from collections import Counter
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
from specimen import ROOT,SHA256,load

folder=ROOT/'local/validation/collision'
BASE,SIZE,MANAGER,LOG=0x1800000,0x5000,0x1800100,0x1803000
STACK,STOP,CALLBACK=0x3000000,0x3f00000,0x3f00100
pe=load();cpu=Uc(UC_ARCH_X86,UC_MODE_32)
cpu.mem_map(0x400000,(pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095)
cpu.mem_write(0x400000,pe.get_memory_mapped_image())
for at,size in [(BASE,SIZE),(STACK,0x20000),(STOP,4096)]:cpu.mem_map(at,size)
cpu.mem_write(CALLBACK,b'\xc3')
initial=bytearray(b'\xa7'*SIZE)
struct.pack_into('<4I',initial,LOG-BASE,0,MANAGER,0,0)
initial=bytes(initial);cases=[];labels=[];hits=Counter();callback_total=0
def word(at):return int.from_bytes(cpu.mem_read(at,4),'little')
def setword(at,value):cpu.mem_write(at,struct.pack('<I',value&0xffffffff))
def patch(at,*words):return [at,struct.pack('<'+'I'*len(words),*words).hex()]
def observe(uc,at,size,user):hits[at]+=1
cpu.hook_add(UC_HOOK_CODE,observe,begin=0x45f270,end=0x45f299)
def callback(uc,at,size,user):
    global callback_total
    callback_total+=1
    index=word(LOG);assert index<32;manager=word(LOG+4)
    setword(LOG,index+1)
    for i,offset in enumerate([0x44,0x40,0x48,0x4c]):setword(LOG+32+index*16+i*4,word(manager+offset))
    if word(LOG+8):setword(manager+0x44,word(LOG+12))
    # The routine must not depend on caller-saved registers after this call.
    for register in [UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EDX]:cpu.reg_write(register,0xdedeeeed)
cpu.hook_add(UC_HOOK_CODE,callback,begin=CALLBACK,end=CALLBACK)
def case(count,entries,mutate=None):
    patches=[patch(MANAGER+0x44,count)]
    if mutate is not None:patches.append(patch(LOG+8,1,mutate))
    expected=bytearray(initial)
    for at,data in patches:expected[at-BASE:at-BASE+len(data)//2]=bytes.fromhex(data)
    cpu.mem_write(BASE,bytes(expected));stages=[]
    for type_,factory,initialize in entries:
        sp=STACK+0x10000;args=[type_,factory,CALLBACK if initialize else 0]
        cpu.mem_write(sp,struct.pack('<4I',STOP,*args))
        cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,MANAGER)
        guards={UC_X86_REG_EBX:0xbbaabb11,UC_X86_REG_ESI:0x55ee5511,UC_X86_REG_EDI:0xddee5511,UC_X86_REG_EBP:0xbeef1234}
        for reg,value in guards.items():cpu.reg_write(reg,value)
        old_callbacks=word(LOG)
        cpu.emu_start(0x45f270,STOP,count=1000)
        assert cpu.reg_read(UC_X86_REG_EIP)==STOP and cpu.reg_read(UC_X86_REG_ESP)==sp+16
        assert all(cpu.reg_read(reg)==value for reg,value in guards.items())
        after=bytes(cpu.mem_read(BASE,SIZE))
        outputs=[[BASE+i,after[i:i+4].hex()] for i in range(0,SIZE,4) if after[i:i+4]!=expected[i:i+4]]
        expected=bytearray(after)
        stages.append({'fn':'0x45f270','this':MANAGER,'args':args,'result':None,'outputs':outputs,'globals':[],'callbacks':word(LOG)-old_callbacks})
    cases.append({'patches':patches,'globals':[],'steps':stages})
    labels.append(f'count {count:x}; entries {entries}; callback count override {mutate}')

for count,type_,factory,initialize in itertools.product([0,1,2,31,127],[0,0x5bd63b29,0xffffffff],[0,0x505440,0xffffffff],[False,True]):
    case(count,[(type_,factory,initialize)])
for count,mutate in itertools.product([0,7,31],[0,1,255,0xffffffff]):
    case(count,[(0x5bd63b29,0x505440,True)],mutate)
for count in [0,3,15]:
    case(count,[(0x5bd63b29,0x505440,True),(0x5bd63b29,0,False),(0x12345678,0x11111111,True)])
# Count aliases factory storage when scaled arithmetic wraps. The final
# increment must reread the just-written factory word, not reuse the old count.
for count,factory,initialize in itertools.product([0x1fffffff,0x7fffffff,0xffffffff],[0,1,0xfffffffe,0xffffffff],[False,True]):
    case(count,[(0x5bd63b29,factory,initialize)])
md=Cs(CS_ARCH_X86,CS_MODE_32);instructions=list(md.disasm(pe.get_data(0x5f270,42),0x45f270))
missing=[hex(row.address) for row in instructions if not hits[row.address]];assert not missing
scope='Original45f270 component factory registration: borrowed type/factory words, ordered count reloads, unsigned offset wrapping, duplicates, repeated appends, count increment before the optional no-argument callback, callback observations and mutation. All manager/guard/log bytes compare. Callback is explicit test instrumentation; no actual component initialization, factory invocation or full level startup is claimed. Valid mapped storage is required; malformed pointers are outside the corpus. The initialization callback is a separate test module.'
scope += ' Maintained main-module comparison; browser and level integration are recorded separately.'
fixture={'base':BASE,'memory':'factory-registration-memory.bin','globals':[],
 'functions':{'0x45f270':{'name':'thug_component_register_factory','this':True,'result':'void','pointer_args':[2]}},
 'float_fields':[],'native_callbacks':[{'module':'factory-registration-callback.wasm','export':'fixture_factory_registration_callback','original':CALLBACK}],
 'cases':cases,'case_labels':labels,'scope':scope,'callback_counter':'initialization_callbacks'}
(folder/fixture['memory']).write_bytes(initial)
(folder/'factory-registration-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(cases),
 'calls':sum(len(c['steps']) for c in cases),'initialization_callbacks':callback_total,
 'instruction_coverage':{'total':len(instructions),'covered':len(instructions),'missing':missing},'scope':scope}
(folder.parent/'factory-registration.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report),flush=True)

adapter=folder/'factory-registration-callback.wasm'
subprocess.run([str(ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang'),'--target=wasm32-unknown-unknown','-O2','-nostdlib','-Wl,--no-entry,--import-memory,--export-all,--global-base=58720256',str(ROOT/'tools/factory_registration_callback.c'),'-o',str(adapter)],check=True)

subprocess.run(['node',str(ROOT/'tools/verify_factory_registration_wasm.mjs')],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file() and p.name!='.DS_Store'}
artifacts=[folder/'factory-registration-fixtures.json',folder/fixture['memory']]
artifacts += [folder/spec['module'] for spec in fixture.get('native_callbacks',[])]
if fixture.get('memory_fixture'):artifacts.append(folder/fixture['memory_fixture'])
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in artifacts}
(folder.parent/'factory-registration.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS factory-registration',len(fixture['cases']),flush=True)
