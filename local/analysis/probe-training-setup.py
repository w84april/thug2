"""Run unchanged TR_Setup through GameModeEquals, stop before real Kill."""
from pathlib import Path
source=Path('local/analysis/probe-training-startup.py').read_text().split('native_hits=Counter()')[0]
source=source.replace("native_names={'Change':0x449d00,'LoadSkeleton':0x445640}","native_names={'GameModeEquals':0x5a11d0,'Kill':0x5a5030}")
exec(compile(source,'<preserved original script startup>','exec'))
import subprocess
SETTINGS,MODE_COMPONENT,MODE_FILENAME,MODE_DATA=BASE+0xe100,BASE+0xe120,BASE+0xe200,BASE+0x40000
mode_path=ROOT/'local/game-files/Game/Data/scripts/gamemodes/gamemode.qb';mode=mode_path.read_bytes();assert len(mode)<0x10000
memory=bytearray(initial);write(MODE_DATA,mode);write(MODE_FILENAME,b'scripts\\gamemodes\\gamemode.qb\0')
write(SETTINGS,struct.pack('<3I',0,0,MODE_COMPONENT));write(MODE_COMPONENT,struct.pack('<4I',26,0,crc(b'mode_career'),0))
initial=bytes(memory);oracle.initial=initial
assert 0x7ce470 not in index;index[0x7ce470]=len(globals_);globals_.append(['thug_game_settings',0x7ce470,4]);defaults.append(SETTINGS)
oracle.defaults=defaults;oracle.globals=globals_
native_hits=Counter();native_arguments=[];mode_returns=[];observed_pointers=[]
def native_observer(cpu,at,size,user):
    native_hits[hex(at)]+=1
    if at!=0x5a5030:return
    sp=cpu.reg_read(UC_X86_REG_ESP);params,script=oracle.word(sp+4),oracle.word(sp+8);assert script==SCRIPT
    cpu.mem_write(BOUNDARY,struct.pack('<4I',at,params,script,oracle.word(BOUNDARY+12)+1))
    item=oracle.word(params+4)
    while item:
        kind=cpu.mem_read(item,1)[0]>>1;name=oracle.word(item+4);value=oracle.word(item+8)
        text=bytes(cpu.mem_read(value,100)).split(b'\0',1)[0].decode('ascii') if kind in [3,4] else None
        native_arguments.append({'name':hex(name),'type':kind,'value':hex(value),'text':text});item=oracle.word(item+12)
    cpu.emu_stop()
for a in native_names.values():oracle.cpu.hook_add(UC_HOOK_CODE,native_observer,begin=a,end=a)
def mode_return(cpu,at,size,user):mode_returns.append(cpu.reg_read(UC_X86_REG_EAX)&255)
for a in [0x5a1219,0x5a121e]:oracle.cpu.hook_add(UC_HOOK_CODE,mode_return,begin=a,end=a)
def prepared_pointer(cpu,at,size,user):
    value=cpu.reg_read(UC_X86_REG_EAX);assert value in native_names.values()
    field=cpu.reg_read(UC_X86_REG_ESI)-4;pointer_fields.add(field);observed_pointers.append({'field':field,'native':hex(value)})
oracle.cpu.hook_add(UC_HOOK_CODE,prepared_pointer,begin=0x46ff81,end=0x46ff81)
training=next(a for a in assets if a['member'].lower()=='levels\\tr\\tr_scripts.qb')
observations=[]
for mode_name,expected in [('mode_career',1),('mode_freeskate',0)]:
    native_hits.clear();native_arguments.clear();mode_returns.clear();observed_pointers.clear()
    calls=[(0x472420,0,[TOD_FILENAME,TOD_DATA,0,0,0]),(0x472420,0,[MODE_FILENAME,MODE_DATA,0,0,0]),
           (0x472420,0,[training['filename'],training['address'],0,0,0]),(0x4738e0,SCRIPT,[]),(0x474540,SCRIPT,[crc(b'TR_Setup'),0,0,0,0])]
    steps=oracle.case(calls,[patch(MODE_COMPONENT+8,'<I',crc(mode_name.encode()))])
    before=bytes(oracle.cpu.mem_read(BASE,len(initial)));sp=oracle.stack+0x18000
    oracle.cpu.mem_write(sp,word(oracle.stop));oracle.cpu.reg_write(UC_X86_REG_ESP,sp)
    oracle.cpu.reg_write(UC_X86_REG_ECX,SCRIPT);oracle.cpu.reg_write(UC_X86_REG_FPCW,0x7f)
    oracle.cpu.emu_start(0x4750b0,oracle.stop,count=5000000)
    assert oracle.cpu.reg_read(UC_X86_REG_EIP)==0x5a5030
    assert native_hits=={'0x5a11d0':1,'0x5a5030':1} and mode_returns==[expected],(mode_name,native_hits,mode_returns)
    if expected:assert native_arguments[0]['name']==hex(crc(b'prefix')) and native_arguments[0]['text']=='WH_Classic_Sk8brd_'
    else:assert native_arguments[0]['name']==hex(crc(b'name')) and native_arguments[0]['value']==hex(crc(b'g_wall_break_pre'))
    after=bytes(oracle.cpu.mem_read(BASE,len(initial)));outputs=[]
    for page in range(0,len(initial),4096):
        if before[page:page+4096]!=after[page:page+4096]:
            for i in range(page,min(page+4096,len(initial)),4):
                if before[i:i+4]!=after[i:i+4]:outputs.append([BASE+i,after[i:i+4].hex()])
    steps.append({'fn':'0x4750b0','this':SCRIPT,'args':[0],'result':None,'outputs':outputs,'globals':[oracle.global_read(g) for g in globals_],'callbacks':0,'expected_trap':True})
    for i in range(oracle.word(CONTEXT+8)):pointer_fields.add(LOG+i*48+36)
    for step in steps:
        step['global_float_indices']=[]
        for at in [0x6f2348,0x6f2568,*range(0x6f2370,0x6f24b0,16)]:
            if step['globals'][index[at]]&0xfe==4:step['global_float_indices'].append(index[at+8])
    observations.append({'mode':mode_name,'game_mode_result':expected,'native_entries':dict(native_hits),'kill_arguments':list(native_arguments),'prepared_native_fields':list(observed_pointers)})
clang=ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang'
subprocess.run([str(clang),'--target=wasm32-unknown-unknown','-O2','-nostdlib','-Wl,--no-entry,--export-all,--import-memory',str(folder/'training-setup-boundary.c'),'-o',str(folder/'training-setup-boundary.wasm')],check=True)
scope='Original TR_Setup and nested TR_Initailizer run through real GameModeEquals with settings resolved from the original whole gamemode.qb file. Initialized settings contain an inclusion of mode_career or mode_freeskate, not a replacement mode predicate. Career returns true and reaches Kill prefix WH_Classic_Sk8brd_; freeskate returns false and reaches Kill name g_wall_break_pre. Both stop before the first Kill instruction; the test boundary records arguments and traps without supplying scene behavior. Three whole QB loads, constructor/setup and all execution effects up to that boundary compare over the full arena, globals and heap. Not completed scene setup, cold boot or playable training.'
fixture={'base':BASE,'memory':'training-setup-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-loader-memory.wasm',
 'memory_exports':['fixture_loader_allocate','fixture_loader_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],
 'cases':oracle.cases,'case_labels':['TR_Setup career until Kill','TR_Setup freeskate until Kill'],'scope':scope,
 'pointer_symbols':parser['pointer_symbols'],'pointer_globals':[index[0x6f2560]],'pointer_exports':[[0x6f2364,'thug_script_loading_file']],
 'pointer_fields':sorted(pointer_fields),'function_exports':[[0x5a11d0,'thug_game_mode_equals_draft']],
 'native_callbacks':[{'module':'training-setup-boundary.wasm','export':'fixture_missing_kill','original':0x5a5030}],'boundary_address':BOUNDARY}
(folder/fixture['memory']).write_bytes(initial);(folder/'training-setup-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original partial setup reaches Kill; Wasm pending','specimen_sha256':SHA256,'cases':2,'completed_setup_calls':10,'interrupted_execute_calls':2,
 'sources':[{'path':str(tod_path.relative_to(ROOT)),'sha256':hashlib.sha256(tod).hexdigest()},{'path':str(mode_path.relative_to(ROOT)),'sha256':hashlib.sha256(mode).hexdigest()},{'member':training['member'],'sha256':training['sha256']}],
 'observations':observations,'callee_calls':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'scope':scope}
(folder/'training-setup-original.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['scope','callee_calls','heap_events']}))
