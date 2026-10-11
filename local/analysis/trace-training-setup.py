"""Original-instruction dependency discovery. Stops before GameModeEquals."""
from pathlib import Path
source=Path('local/analysis/probe-training-startup.py').read_text().split('native_hits=Counter()')[0]
source=source.replace("native_names={'Change':0x449d00,'LoadSkeleton':0x445640}","native_names={'GameModeEquals':0x5a11d0}")
exec(compile(source,'<preserved startup environment>','exec'))
training=next(a for a in assets if a['member'].lower()=='levels\\tr\\tr_scripts.qb')
calls=[(0x472420,0,[TOD_FILENAME,TOD_DATA,0,0,0]),
       (0x472420,0,[training['filename'],training['address'],0,0,0]),
       (0x4738e0,SCRIPT,[]),(0x474540,SCRIPT,[crc(b'TR_Setup'),0,0,0,0])]
oracle.case(calls)
entries=[]
def breakpoint(cpu,address,size,user):
    sp=cpu.reg_read(UC_X86_REG_ESP);params,script=oracle.word(sp+4),oracle.word(sp+8)
    entries.append({'address':hex(address),'params':hex(params),'script':hex(script)})
    cpu.emu_stop()
oracle.cpu.hook_add(UC_HOOK_CODE,breakpoint,begin=0x5a11d0,end=0x5a11d0)
sp=oracle.stack+0x18000;oracle.cpu.mem_write(sp,word(oracle.stop))
oracle.cpu.reg_write(UC_X86_REG_ESP,sp);oracle.cpu.reg_write(UC_X86_REG_ECX,SCRIPT);oracle.cpu.reg_write(UC_X86_REG_FPCW,0x7f)
oracle.cpu.emu_start(0x4750b0,oracle.stop,count=5000000)
assert oracle.cpu.reg_read(UC_X86_REG_EIP)==0x5a11d0 and len(entries)==1
item=oracle.word(int(entries[0]['params'],16)+4);arguments=[]
while item:
    kind=oracle.cpu.mem_read(item,1)[0]>>1
    arguments.append({'name':hex(oracle.word(item+4)),'type':kind,'value':hex(oracle.word(item+8))});item=oracle.word(item+12)
assert arguments==[{'name':'0x0','type':13,'value':hex(crc(b'is_career'))}],arguments
report={'scope':'Original TR_Setup dependency trace from initialized script services. Stops before first instruction of GameModeEquals; no game-mode result or scene setup is supplied. Not a completed script and not a Wasm equivalence proof.',
 'specimen_sha256':SHA256,'sources':[{'path':str(tod_path.relative_to(ROOT)),'sha256':hashlib.sha256(tod).hexdigest()},{'member':training['member'],'sha256':training['sha256']}],
 'requested_script':'TR_Setup','completed_setup_calls':4,'interrupted_execute_calls':1,'next_missing_handler':{'name':'GameModeEquals','address':'0x5a11d0','arguments':arguments},'observed_native_entries':entries}
(folder/'training-setup-next-trace.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
