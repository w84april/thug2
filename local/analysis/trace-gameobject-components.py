"""Original-only load and inspection of prop descriptors; no fake prop creation."""
from pathlib import Path
source=Path('tools/verify_script_load.py').read_text().split('labels=[];max_heap=HEAP')[0]
source=source.replace(';report_path.unlink(missing_ok=True)','').replace(";(out/'script-load-memory.bin').write_bytes(initial)",'')
assert '.write_' not in source and '.unlink(' not in source
exec(compile(source,'<preserved whole-file loader setup>','exec'))
from unicorn.x86_const import UC_X86_REG_ECX
folder=ROOT/'local/analysis';records=[];calls=[];cursor=ASSETS
for member in ['scripts/game/skutils.qb','scripts/game/ped.qb']:
    path=ROOT/'local/game-files/Game/Data'/member;data=path.read_bytes();filename=cursor+len(data)+16
    memory[cursor-BASE:cursor-BASE+len(data)]=data;encoded=member.replace('/','\\').encode()+b'\0'
    memory[filename-BASE:filename-BASE+len(encoded)]=encoded
    calls.append((0x472420,0,[filename,cursor,0,1,0]))
    records.append({'member':member,'size':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    cursor=(filename+len(encoded)+19)&~3
assert cursor<STRINGS
initial=bytes(memory);oracle.initial=initial;oracle.case(calls)
OUT=BASE+0xf000
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
    raw=bytearray()
    for i in range(512):
        b=oracle.cpu.mem_read(p+i,1)[0]
        if not b:return raw.decode('latin1')
        raw.append(b)
    raise AssertionError('name length')
array=invoke(0x479070,0,[0x735a20ba,0],0);assert array
count=oracle.word(array+4);items=invoke(0x46cb00,array,[],0);rows=[]
for i in range(count):
    node=oracle.word(items+4*i);kind=checksum(node,0xb6015ea8);components=[];p=oracle.word(node+4)
    while p:
        tag=oracle.word(p)&255;name=oracle.word(p+4);value=oracle.word(p+8)
        components.append({'tag':tag,'name':hex(name),'name_text':text_name(name),'raw_value':hex(value),'value_text':text_name(value) if tag&0xfe==26 else None})
        p=oracle.word(p+12)
    rows.append({'index':i,'type':hex(kind),'type_text':text_name(kind),'fields':components})
report={'result':'original-only discovery','specimen_sha256':SHA256,'assets':records,
 'descriptor_array':{'name':'gameobj_composite_structure','checksum':'0x735a20ba','count':count,'components':rows},
 'names':{hex(k):text_name(k) for k in [0xf3b84da6,0x413b766d,0x5cb5cb7e,0xb87c8e43]},
 'scope':'Actual original whole-file loads of extracted skutils.qb and ped.qb, followed by original global array, storage, checksum and readable-name getters. Descriptor fields are discovery only. No factories, gameobj_add_components script, scene props or rendering execute.'}
(folder/'gameobject-component-inventory.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
