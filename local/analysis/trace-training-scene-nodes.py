"""Original-only inventory of the registered training nodes to guide scene creation."""
from pathlib import Path
source=Path('local/analysis/probe-training-node-registration.py').read_text().split('for flag in [0,1]:')[0]
exec(compile(source,'<registered training oracle setup only>','exec'))
from unicorn.x86_const import UC_X86_REG_ECX
oracle.case([(0x472420,0,[asset['filename'],asset['address'],0,1,0]),(0x45d370,TABLE,[]),(0x45d520,TABLE,[key,1])])
array=oracle.word(TABLE+0x1000c);items=oracle.word(array+8);count=oracle.word(array+4);OUT=BASE+0xe400
def invoke(fn,this,args,cleanup):
    cpu=oracle.cpu;sp=oracle.stack+0x18000
    cpu.mem_write(sp,struct.pack('<'+'I'*(len(args)+1),oracle.stop,*args))
    cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,this);cpu.reg_write(UC_X86_REG_EAX,0xadadadad)
    cpu.emu_start(fn,oracle.stop,count=100000)
    assert cpu.reg_read(UC_X86_REG_EIP)==oracle.stop and cpu.reg_read(UC_X86_REG_ESP)==sp+4+cleanup
    return cpu.reg_read(UC_X86_REG_EAX)
def checksum(node,key):
    oracle.setword(OUT,0);invoke(0x476950,node,[key,OUT,0],12);return oracle.word(OUT)
def text_name(key):
    p=invoke(0x46f9b0,0,[key],0)
    if not p:return None
    result=bytearray()
    for i in range(1000):
        b=oracle.cpu.mem_read(p+i,1)[0]
        if not b:return result.decode('latin1')
        result.append(b)
    raise AssertionError('unbounded readable name')
rows=[];classes=Counter();created=Counter()
for i in range(count):
    node=oracle.word(items+i*4);kind=checksum(node,0x12b4e660);name=checksum(node,0xa1dc81f9)
    flag=invoke(0x476b40,node,[0x7c2552b9],4)&255
    classes[kind]+=1
    if flag:created[kind]+=1
    rows.append({'index':i,'name':hex(name),'text':text_name(name),'class':hex(kind),'class_text':text_name(kind),'created_at_start':bool(flag)})
report={'result':'original-only discovery','asset':{k:asset[k] for k in ['member','size','sha256']},'specimen_sha256':SHA256,
 'node_count':count,'link_groups':oracle.word(GROUPS+8),'created_at_start_flag':hex(0x7c2552b9),
 'classes':[{'name':hex(k),'text':text_name(k),'nodes':v,'created_at_start':created[k]} for k,v in sorted(classes.items())],
 'nodes':rows,'scope':'Actual whole training QB load and complete original registration with link-group processing, followed by original checksum and flag getters (including inherited properties) and local readable-name lookup. Created-at-start flag inventory guides the unrecovered ParseNodeArray/object-creation path. No scene objects are instantiated here; this is discovery, not a new recovered function or playable-level proof.'}
(folder/'training-scene-node-inventory.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['nodes','scope']}))
