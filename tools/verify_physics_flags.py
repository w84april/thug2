import hashlib,json,subprocess
"""Compare fixed-ABI physics state commands against original instructions."""
import itertools,json,random,re,struct
from collections import Counter
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
from specimen import ROOT,SHA256,load

folder=ROOT/'local/validation/collision';pe=load();rng=random.Random(0x4fc780)
BASE,SIZE=0x1800000,0x6000
PHYS,STATE,OWNER,GAME=BASE+0x1000,BASE+0x2800,BASE+0x3000,BASE+0x4000
STACK,STOP=0x3000000,0x3f00000
initial=bytearray(rng.randrange(256) for _ in range(SIZE))
def put(at,fmt,*values):struct.pack_into(fmt,initial,at-BASE,*values)
put(PHYS+0xc,'<I',OWNER);put(PHYS+0x1528,'<I',STATE)
put(OWNER+0x2bc,'<I',0);put(OWNER+0x110,'<B',1)
initial=bytes(initial)
cpu=Uc(UC_ARCH_X86,UC_MODE_32)
cpu.mem_map(0x400000,(pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095)
cpu.mem_write(0x400000,pe.get_memory_mapped_image())
for at,size in [(BASE,SIZE),(STACK,0x20000),(STOP,4096)]:cpu.mem_map(at,size)
declarations=re.findall(r'/\* ([0-9a-f]{8}) \*/ (MEMBER|SET|GET|STATE)\(([^)]*)\)',(ROOT/'src/game/physics_flags.c').read_text())
entries=json.loads((ROOT/'local/analysis/physics-command-path-index.json').read_text())['entries']
original_entries={int(row['member'],16):row for row in entries if not row['direct_calls'] and not row['indirect_calls']}
assert len(declarations)==len(original_entries)==58
functions={};specs={};hits=Counter();cases=[];labels=[];counts=Counter()
for address,kind,args in declarations:
    address=int(address,16);parts=[part.strip() for part in args.split(',')];name=parts[0]
    assert address in original_entries
    functions[hex(address)]={'name':'thug_physics_'+name+'_member','this':True,'result':'word'}
    specs[name]=(address,kind,parts[1:])
def observe(uc,at,size,user):hits[at]+=1
cpu.hook_add(UC_HOOK_CODE,observe,begin=0x4fbf40,end=0x4fd1df)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
def run(calls,patches=(),game=GAME,label='state command'):
    expected=bytearray(initial)
    for at,data in patches:expected[at-BASE:at-BASE+len(data)//2]=bytes.fromhex(data)
    cpu.mem_write(BASE,bytes(expected));cpu.mem_write(0x7ce478,struct.pack('<I',game))
    stages=[]
    for address,args in calls:
        sp=STACK+0x10000;cpu.mem_write(sp,struct.pack('<3I',STOP,*args))
        cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,PHYS)
        cpu.reg_write(UC_X86_REG_EAX,0xadadadad);cpu.reg_write(UC_X86_REG_FPCW,0x7f)
        saved={UC_X86_REG_EBX:0xbeefaabb,UC_X86_REG_ESI:0x55112233,UC_X86_REG_EDI:0xababaabb,UC_X86_REG_EBP:0xbbccccdd}
        for reg,value in saved.items():cpu.reg_write(reg,value)
        cpu.emu_start(address,STOP,count=1000)
        assert cpu.reg_read(UC_X86_REG_EIP)==STOP and cpu.reg_read(UC_X86_REG_ESP)==sp+12
        assert all(cpu.reg_read(reg)==value for reg,value in saved.items())
        after=bytes(cpu.mem_read(BASE,SIZE));outputs=[]
        for page in range(0,SIZE,4096):
            if after[page:page+4096]!=expected[page:page+4096]:
                outputs += [[BASE+i,after[i:i+4].hex()] for i in range(page,page+4096,4) if after[i:i+4]!=expected[i:i+4]]
        stages.append({'fn':hex(address),'this':PHYS,'args':args,'result':cpu.reg_read(UC_X86_REG_EAX),'outputs':outputs,'globals':[int.from_bytes(cpu.mem_read(0x7ce478,4),'little')],'callbacks':0})
        expected=bytearray(after);counts[functions[hex(address)]['name']]+=1
    cases.append({'patches':list(patches),'globals':[game],'steps':stages});labels.append(label)
def call(name):return (specs[name][0],[rng.randrange(2**32),rng.randrange(2**32)])

for name,(address,kind,args) in specs.items():
    if kind=='MEMBER':continue
    offset=int(args[0],0);at=(STATE if kind=='STATE' else PHYS)+offset
    for value in range(256):
        run([call(name)]*2,[patch(at,'<B',value)],label=f'{name} byte {value}, retained repeat')
for value in range(256):
    run([call('auto_kick_is_off')]*2,[patch(PHYS+0x2d9,'<B',value)],label=f'autokick inverse {value}')
    run([call('reset_projectile_input')]*2,[patch(PHYS+0x308,'<I',rng.randrange(2**32))],label='projectile sentinel preserves adjacent bytes')
for owner,flipped in itertools.product([0,1,127,128,255],range(256)):
    run([call('switched')]*2,[patch(OWNER+0x110,'<B',owner),patch(STATE+0x28,'<B',flipped)],label=f'stance owner {owner}, flipped {flipped}')
for player,value in itertools.product([0,1,2,15,31,0x20000000,0x20000001,0x40000002],range(256)):
    offset=(player*8+0x395)&0xffffffff
    run([call('restore_auto_kick'),call('auto_kick_is_off')],
        [patch(OWNER+0x2bc,'<I',player),patch(GAME+offset,'<B',value)],label=f'copy autokick player {player:x}, raw byte {value}')
threshold=int.from_bytes(pe.get_data(0x246710,4),'little');assert threshold==0x41200000
values=[0,0x80000000,1,0x80000001,threshold-1,threshold,threshold+1,0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc12345,0x7f812345,0xff812345]+[rng.randrange(2**32) for _ in range(128)]
for enabled,bits in itertools.product([0,1,127,128,255],values):
    run([call('doing_flip')]*2,[patch(PHYS+0x2db,'<B',enabled),patch(PHYS+0x2e0,'<I',bits)],label=f'doing flip flag {enabled}, float bits {bits:x}')
# Real command sequences verify that related predicates see preceding writes.
sequences=[['skater_vehicle_on','is_skater_on_vehicle','skater_vehicle_off','is_skater_on_vehicle'],
 ['bail_on','bail_is_on','bail_off','bail_is_on'],
 ['set_landed_from_vert','landed_from_vert','reset_landed_from_vert','landed_from_vert'],
 ['in_revert','is_in_revert','out_revert','is_in_revert'],
 ['moto_skateboard_on','is_on_moto_skateboard','moto_skateboard_off','is_on_moto_skateboard'],
 ['set_throwing_projectile','is_throwing_projectile','unset_throwing_projectile','is_throwing_projectile'],
 ['enter_tantrum','in_tantrum','exit_tantrum','in_tantrum'],
 ['enter_tagging','is_tagging','exit_tagging','is_tagging'],
 ['force_auto_kick_on','auto_kick_is_off','force_auto_kick_off','auto_kick_is_off','restore_auto_kick','auto_kick_is_off']]
for names in sequences:run([call(n) for n in names]*3,label='retained sequence '+','.join(names))
blocks=(ROOT/'local/analysis/physics-command-path-instructions.txt').read_text().split('\n\n')
coverage={};md=Cs(CS_ARCH_X86,CS_MODE_32)
for address,row in original_entries.items():
    block=next(b for b in blocks if b.lstrip().startswith(f'{address:08x} '))
    addresses=[int(line[:8],16) for line in block.splitlines() if re.match(r'^[0-9a-f]{8} (?:mov|xor|test|set|ret|fld|fcomp|fnstsw|je|jne)',line)]
    assert len(addresses)==row['reachable_instructions'],hex(address)
    decoded={i.address for i in md.disasm(pe.get_data(address-0x400000,int(row['next_indexed_entry'],16)-address),address)}
    assert set(addresses)<=decoded
    missing=[hex(at) for at in addresses if not hits[at]];assert not missing,(hex(address),missing)
    coverage[hex(address)]={'total':len(addresses),'covered':len(addresses),'missing':[]}
scope='58 complete original fixed-ABI physics state command members, with real object/state/owner pointers and game-context lookup. All256 input byte values, separate stance booleans, raw autokick byte copying with unsigned indexed offsets, repeated writes, related command sequences, projectile sentinel, and DoingFlip strict10 threshold including signed zero, infinities and NaNs. Full fixture memory and return values compare, all original instructions covered. Unknown flags are not normalized on stores that copy bytes. Valid object pointers and mapped indexed storage remain original contracts. This direct corpus does not establish playable-level startup.'
scope += ' Maintained main-module comparison; browser and level integration are recorded separately.'
fixture={'base':BASE,'memory':'physics-flags-memory.bin','globals':[['thug_game_context',0x7ce478,4]],'functions':functions,'float_fields':[],'cases':cases,'case_labels':labels,'scope':scope}
(folder/fixture['memory']).write_bytes(initial)
(folder/'physics-flags-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(cases),'calls':sum(counts.values()),'counts':dict(counts),'instruction_coverage':coverage,'scope':scope}
(folder.parent/'physics-flags.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['counts','instruction_coverage']}),flush=True)
print('Instructions',sum(v['covered'] for v in coverage.values()),'functions',len(coverage),flush=True)

subprocess.run(['node',str(ROOT/'tools/verify_physics_flags_wasm.mjs')],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file() and p.name!='.DS_Store'}
artifacts=[folder/'physics-flags-fixtures.json',folder/fixture['memory']]
artifacts += [folder/spec['module'] for spec in fixture.get('native_callbacks',[])]
if fixture.get('memory_fixture'):artifacts.append(folder/fixture['memory_fixture'])
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in artifacts}
(folder.parent/'physics-flags.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS physics-flags',len(fixture['cases']),flush=True)
