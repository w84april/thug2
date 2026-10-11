"""Load original QB files and stop TR_startup at its first unrecovered native.

This is a partial execution trace, not a completed startup or a game substitute.
The breakpoint never executes or fabricates the LoadSkeleton implementation.
"""
import hashlib,json,struct,zlib
from collections import Counter
from pathlib import Path
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import *

# Reuse verified whole-file loader/allocator/TLS setup without its old report
# deletion or fixture writes. No historical validation artifact is regenerated.
source=Path('tools/verify_script_load.py').read_text()
prefix=source[:source.index('labels=[];max_heap=HEAP')]
prefix=prefix.replace(';report_path.unlink(missing_ok=True)','')
prefix=prefix.replace(";(out/'script-load-memory.bin').write_bytes(initial)",'')
assert '.write_' not in prefix and '.unlink(' not in prefix
exec(compile(prefix,'<preserved whole-file loader setup>','exec'))
folder=ROOT/'local/analysis';state=json.loads((out/'script-state-fixtures.json').read_text())
for g in state['globals']:
    if g[1] not in index:
        index[g[1]]=len(globals_);globals_.append(g);defaults.append(0)
for at,value in [(0x6f3530,0),(0x6f3538,0),(0x6f353c,0),(0x6f3540,1),
                 (0x6f3558,CACHE),(0x6f352c,0),(0x684fc8,0x3f800000),
                 (0x7d1ec8,120),(0x684fd0,0x42700000),(0x696d64,0),(0x67d7c0,0x3f800000),(0x696d60,0)]:
    defaults[index[at]]=value
oracle.defaults=defaults
SCRIPT,BOUNDARY,NATIVE_SYMBOLS,TOD_DATA,TOD_FILENAME=BASE+0xc000,BASE+0xe000,BASE+0xa000,PROGRAM,BASE+0xb000
functions['0x4738e0']=state['functions']['0x4738e0']
functions['0x474540']={'name':'thug_script_setup','this':True,'result':'void','cleanup':16,'memory':True,'stack_args':[0,1,2,3]}
functions['0x4750b0']={'name':'thug_script_execute','this':True,'result':'void','cleanup':0,'memory':True,'stack_args':[]}
native_names={'Change':0x449d00,'LoadSkeleton':0x445640}
native_metadata={row['name']:row for row in json.loads((folder/'script-bindings.json').read_text())}
for name,at in native_names.items():assert int(native_metadata[name]['address'],16)==at
memory=bytearray(initial)
def write(at,data):memory[at-BASE:at-BASE+len(data)]=data
write(BOUNDARY,bytes(16));write(SCRIPT,bytes(244));write(TOD_FILENAME,b'scripts\\engine\\tod_manager.qb\0')
tod_path=ROOT/'local/game-files/Game/Data/scripts/engine/tod_manager.qb';tod=tod_path.read_bytes()
assert len(tod)<LOCAL-PROGRAM;write(TOD_DATA,tod)
pointer_fields={CONTEXT+24}
for i,(name,address) in enumerate(native_names.items()):
    checksum=crc(name.encode());at=NATIVE_SYMBOLS+i*20;bucket=BUCKETS+(checksum&4095)*4
    previous=struct.unpack_from('<I',memory,bucket-BASE)[0]
    write(at,struct.pack('<BBH4I',0x91,8,0x1234,checksum,0,address,previous))
    write(bucket,word(at));pointer_fields.add(at+12)
initial=bytes(memory);oracle.initial=initial
native_hits=Counter();boundary_args=None
def native_observer(cpu,address,size,user):
    global boundary_args
    native_hits[hex(address)]+=1
    if address==0x445640:
        sp=cpu.reg_read(UC_X86_REG_ESP);params,script=oracle.word(sp+4),oracle.word(sp+8)
        boundary_args=(params,script)
        cpu.mem_write(BOUNDARY,struct.pack('<4I',address,params,script,oracle.word(BOUNDARY+12)+1))
        cpu.emu_stop()
for at in native_names.values():oracle.cpu.hook_add(UC_HOOK_CODE,native_observer,begin=at,end=at)
for at in [0x4738e0,0x474540,0x4750b0,0x46ff00,0x475e80]:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
training=next(a for a in assets if a['member'].lower()=='levels\\tr\\tr_scripts.qb')
calls=[(0x472420,0,[TOD_FILENAME,TOD_DATA,0,0,0]),
       (0x472420,0,[training['filename'],training['address'],0,0,0]),
       (0x4738e0,SCRIPT,[]),(0x474540,SCRIPT,[crc(b'TR_startup'),0,0,0,0])]
steps=oracle.case(calls)
def symbol(name):
    at=oracle.word(BUCKETS+(name&4095)*4)
    while at and oracle.word(at+4)!=name:at=oracle.word(at+16)
    assert at,hex(name)
    return at
tod_key=crc(b'tod_manager_inactive');before_symbol=symbol(tod_key)
assert oracle.cpu.mem_read(before_symbol+1,1)[0]==1
before_value=oracle.word(before_symbol+12);before_file=oracle.word(before_symbol+8)
program=oracle.word(ENTRIES+4);assert program
stored=oracle.word(symbol(crc(b'TR_startup'))+12);program_size=oracle.word(stored+4)
prepared=bytes(oracle.cpu.mem_read(program,program_size))
for name,address in native_names.items():
    needle=b'\x43'+word(address);positions=[i for i in range(len(prepared)-4) if prepared[i:i+5]==needle]
    assert len(positions)==1,(name,positions)
    pointer_fields.add(program+positions[0]+1)
before=bytes(oracle.cpu.mem_read(BASE,len(initial)));sp=oracle.stack+0x18000
oracle.cpu.mem_write(sp,word(oracle.stop));oracle.cpu.reg_write(UC_X86_REG_ESP,sp)
oracle.cpu.reg_write(UC_X86_REG_ECX,SCRIPT);oracle.cpu.reg_write(UC_X86_REG_FPCW,0x7f)
oracle.cpu.emu_start(0x4750b0,oracle.stop,count=5000000)
assert oracle.cpu.reg_read(UC_X86_REG_EIP)==0x445640 and boundary_args is not None
assert native_hits=={'0x449d00':1,'0x445640':1}
assert oracle.word(BOUNDARY+12)==1 and boundary_args[1]==SCRIPT
after_symbol=symbol(tod_key)
assert oracle.cpu.mem_read(after_symbol+1,1)[0]==1 and oracle.word(after_symbol+12)==1
assert oracle.word(after_symbol+8)==before_file
params=boundary_args[0];arguments=[];item=oracle.word(params+4)
while item:
    kind=oracle.cpu.mem_read(item,1)[0]>>1;name=oracle.word(item+4);value=oracle.word(item+8)
    text=bytes(oracle.cpu.mem_read(value,100)).split(b'\0',1)[0].decode('ascii') if kind in [3,4] else None
    arguments.append({'name':hex(name),'type':kind,'value':hex(value),'text':text});item=oracle.word(item+12)
assert any(a['name']==hex(crc(b'name')) and a['text']=='skeletons/CS_Cardboard.ske' for a in arguments)
assert any(a['name']=='0x0' and a['type']==13 and a['value']==hex(crc(b'CS_Cardboard')) for a in arguments)
after=bytes(oracle.cpu.mem_read(BASE,len(initial)))
outputs=[]
for page in range(0,len(initial),4096):
    if before[page:page+4096]!=after[page:page+4096]:
        for i in range(page,min(page+4096,len(initial)),4):
            if before[i:i+4]!=after[i:i+4]:outputs.append([BASE+i,after[i:i+4].hex()])
steps.append({'fn':'0x4750b0','this':SCRIPT,'args':[0],'result':None,'outputs':outputs,
              'globals':[oracle.global_read(g) for g in globals_],'callbacks':0,'expected_trap':True})
for i in range(oracle.word(CONTEXT+8)):pointer_fields.add(LOG+i*48+36)
for step in steps:
    step['global_float_indices']=[]
    for at in [0x6f2348,0x6f2568,*range(0x6f2370,0x6f24b0,16)]:
        if step['globals'][index[at]]&0xfe==4:step['global_float_indices'].append(index[at+8])
scope='Original tod_manager.qb and archived TR_scripts.qb are loaded by the recovered whole-file loader, compressed/cached and executed as unchanged script content. An initialized fixture supplies memory, script cache and two real native bindings. TR_startup runs Change and sets tod_manager_inactive to1, then deliberately stops at the entry to unrecovered LoadSkeleton before executing that command. The matching Wasm boundary records its arguments and traps; it never reports handler success. Entire fixture memory/globals/heap effects compare through that breakpoint. This is a partial startup dependency trace, not completed level startup, a cold engine boot or playable training.'
fixture={'base':BASE,'memory':'training-startup-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-loader-memory.wasm',
 'memory_exports':['fixture_loader_allocate','fixture_loader_release','fixture_values_scope'],'globals':globals_,'functions':functions,
 'float_fields':[],'cases':oracle.cases,'case_labels':['actual TR_startup until missing LoadSkeleton'],'scope':scope,
 'pointer_symbols':parser['pointer_symbols'],'pointer_globals':[index[0x6f2560]],
 'pointer_exports':[[0x6f2364,'thug_script_loading_file']],'pointer_fields':sorted(pointer_fields),
 'function_exports':[[0x449d00,'thug_script_change_native_draft']],
 'native_callbacks':[{'module':'training-startup-boundary.wasm','export':'fixture_missing_load_skeleton','original':0x445640}],
 'boundary_address':BOUNDARY}
(folder/fixture['memory']).write_bytes(initial);(folder/'training-startup-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original partial trace reached expected boundary; Wasm pending','specimen_sha256':SHA256,
 'sources':[{'path':str(tod_path.relative_to(ROOT)),'sha256':hashlib.sha256(tod).hexdigest()},
            {'member':training['member'],'sha256':training['sha256']}],
 'cases':1,'completed_setup_calls':4,'interrupted_execute_calls':1,'native_entries':dict(native_hits),
 'startup_checksum':hex(crc(b'TR_startup')),'tod_value_before':before_value,'tod_value_after':1,
 'next_missing_handler':{'name':'LoadSkeleton','address':'0x445640','arguments':arguments},
 'prepared_program':{'address':program,'bytes':program_size,'sha256':hashlib.sha256(prepared).hexdigest()},
 'callee_calls':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'scope':scope}
(folder/'training-startup-original.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['callee_calls','heap_events','scope']}),flush=True)
