"""Original-only discovery trace; none of the new index builders is lifted yet.
Run real NodeArray registration with callback construction disabled (argument0).
"""
from pathlib import Path
source=Path('tools/verify_script_load.py').read_text().split('labels=[];max_heap=HEAP')[0]
source=source.replace(';report_path.unlink(missing_ok=True)','').replace(";(out/'script-load-memory.bin').write_bytes(initial)",'')
assert '.write_' not in source and '.unlink(' not in source
exec(compile(source,'<preserved whole-QB loader setup>','exec'))
from unicorn.x86_const import UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP,UC_X86_REG_ECX
folder=ROOT/'local/analysis';TABLE=BASE+0x90000
for name,address,value in [('unrecovered_node_table',0x6f0d84,TABLE),('unrecovered_prefix_manager',0x6f0d80,0)]:
    index[address]=len(globals_);globals_.append([name,address,4]);defaults.append(value)
functions['0x45d370']={'name':'unrecovered_node_table_initialize','this':True,'result':'void','cleanup':0}
functions['0x45d520']={'name':'unrecovered_node_array_register','this':True,'result':'byte','cleanup':8}
observe=[0x45d370,0x45d520,0x45d3a0,0x45ce60,0x45c900,0x45c700,0x45c5d0,0x45c650,0x45bda0,0x45c240,0x46f9b0,0x45d480]
for address in observe:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=address,end=address)
asset=next(a for a in assets if a['member'].lower()=='levels\\tr\\tr.qb')
key=crc(b'TR_NodeArray');regs=[UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP]
before=[oracle.cpu.reg_read(r) for r in regs]
calls=[(0x472420,0,[asset['filename'],asset['address'],0,1,0]),(0x45d370,TABLE,[]),(0x45d520,TABLE,[key,0])]
steps=oracle.case(calls)
assert steps[-1]['result']==1 and [oracle.cpu.reg_read(r) for r in regs]==before
assert oracle.word(TABLE+0x10004)==1 and oracle.word(TABLE+0x10008)==key
array=oracle.word(TABLE+0x1000c);count=oracle.word(array+4)
def array_item(a,i):return oracle.word(a+8) if oracle.word(a+4)==1 else oracle.word(oracle.word(a+8)+i*4)
def checksum_field(p,key):
    output=BASE+0xe100;sp=oracle.stack+0x18000;oracle.setword(output,0)
    oracle.cpu.mem_write(sp,struct.pack('<4I',oracle.stop,key,output,0))
    oracle.cpu.reg_write(UC_X86_REG_ESP,sp);oracle.cpu.reg_write(UC_X86_REG_ECX,p)
    oracle.cpu.emu_start(0x476950,oracle.stop,count=1000000)
    assert oracle.cpu.reg_read(UC_X86_REG_EIP)==oracle.stop and oracle.cpu.reg_read(UC_X86_REG_ESP)==sp+16
    return oracle.word(output) if oracle.cpu.reg_read(UC_X86_REG_EAX)&255 else None
def local_text(key):
    p=oracle.word(0x6f2368)+(key&4095)*12
    while p:
        if oracle.word(p)==key:
            text=oracle.word(p+4)
            return bytes(oracle.cpu.mem_read(text,1000)).split(b'\0',1)[0].decode('latin1') if text else None
        p=oracle.word(p+8)
    return None
def prefix_indices(name):
    key=crc(name.encode());entry=oracle.word(oracle.word(0x6f0d80));result=[]
    while entry:
        table=oracle.word(entry);p=oracle.word(table+4)+(key&((1<<(oracle.word(table)&31))-1))*12
        while p and (oracle.word(p)!=key or not oracle.word(p+4)):p=oracle.word(p+8)
        if p:
            found=oracle.word(p+4);n=oracle.word(found)&65535;indices=oracle.word(found+4)
            result += [int.from_bytes(oracle.cpu.mem_read(indices+i*2,2),'little') for i in range(n)]
        entry=oracle.word(entry+8)
    return result
classes=Counter();nodes=[]
for i in range(count):
    node=array_item(array,i);name=checksum_field(node,0xa1dc81f9);kind=checksum_field(node,0x12b4e660)
    classes[hex(kind or 0)]+=1;nodes.append({'index':i,'name':hex(name) if name is not None else None,'text':local_text(name) if name is not None else None,'class':hex(kind or 0)})
prefixes={name:[nodes[i] for i in prefix_indices(name)] for name in ['WH_Classic_Sk8brd_','g_wall_break_','TRG']}
slots=sum(int.from_bytes(oracle.cpu.mem_read(TABLE+i*4+2,2),'little')!=65535 for i in range(16384))
target=[n for n in nodes if n['name']==hex(crc(b'g_wall_break_pre'))]
report={'result':'original-only node registration completed; builders not yet recovered in Wasm','specimen_sha256':SHA256,
 'asset':{k:asset[k] for k in ['member','size','sha256']},'calls':3,'original_checksum_queries':count*2,'register_result':steps[-1]['result'],
 'node_count':count,'occupied_name_slots':slots,'classes':dict(classes),'prefix_matches':prefixes,'first_freeskate_target':target,
 'observed_original_calls':{hex(a):oracle.coverage[hex(a)] for a in observe},'heap_events':dict(oracle.heap_events),
 'scope':'Real archived TR.qb loaded with local readable names retained, then original node-table constructor and full45d520 registration run with its low-byte trigger-build option0. Name hash and prefix indexes, position conversion and link checksum conversion run without replacements. This is discovery evidence for the next recovery step, not a Wasm validation or TR_Setup advancement.'}
(folder/'training-node-index-discovery.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['scope','classes','heap_events']}),flush=True)
