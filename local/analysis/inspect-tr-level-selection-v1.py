"""Original QB loading and token traversal for scene identity; zero credit."""
from pathlib import Path
source=Path('tools/verify_script_load.py').read_text().split('# Debug map preserves')[0]
source=source.replace('report_path.unlink(missing_ok=True)','None').replace("(out/'script-load-memory.bin').write_bytes(initial)",'None')
assert '.write_' not in source and '.unlink(' not in source
exec(compile(source,'<preserved original QB loader setup>','exec'))
from unicorn.x86_const import UC_X86_REG_ECX
cpu=oracle.cpu
def invoke(fn,this,args,cleanup):
    sp=oracle.stack+0x18000
    cpu.mem_write(sp,struct.pack('<'+'I'*(len(args)+1),oracle.stop,*args))
    cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,this)
    cpu.emu_start(fn,oracle.stop,count=1000000)
    assert cpu.reg_read(UC_X86_REG_EIP)==oracle.stop and cpu.reg_read(UC_X86_REG_ESP)==sp+4+cleanup
    return cpu.reg_read(UC_X86_REG_EAX)
def string(at):
    result=bytearray()
    for i in range(10000):
        b=cpu.mem_read(at+i,1)[0]
        if not b:return result.decode('latin1')
        result.append(b)
    raise AssertionError('unbounded string')
def readable(key):
    at=invoke(0x46f9b0,0,[key],0)
    return string(at) if at else None
def value(kind,at,depth=0):
    assert depth<24
    if kind in [3,4]:return string(at)
    if kind==13:return {'checksum':hex(at),'text':readable(at)}
    if kind==10:
        rows=[];node=oracle.word(at+4)
        while node:
            tag=cpu.mem_read(node,1)[0]>>1;name=oracle.word(node+4)
            rows.append({'name':hex(name),'text':readable(name),'type':tag,'value':value(tag,oracle.word(node+8),depth+1)})
            node=oracle.word(node+12);assert len(rows)<2000
        return rows
    if kind==12:
        tag=cpu.mem_read(at+1,1)[0];count=oracle.word(at+4);items=oracle.word(at+8);assert count<3000
        return {'item_type':tag,'items':[value(tag,items if count==1 else oracle.word(items+i*4),depth+1) for i in range(count)]}
    if kind in [5,6]:return list(struct.unpack('<'+'f'*(kind-3),cpu.mem_read(at+4,4*(kind-3))))
    if kind==2:return struct.unpack('<f',struct.pack('<I',at))[0]
    return hex(at)
files=['scripts/game/menu/gamemenu_levelselect.qb','levels/TR/TR_Scripts.qb']
results=[]
for file in files:
    path=ROOT/'local/game-files/Game/Data'/file;raw=path.read_bytes();data=BASE+0x6b0000;filename=BASE+0x6af000
    memory=bytearray(initial);memory[data-BASE:data-BASE+len(raw)]=raw;text=file.replace('/','\\').encode()+b'\0';memory[filename-BASE:filename-BASE+len(text)]=text
    pool_entries=BASE+0x8000;capacity=1500
    struct.pack_into('<6I',memory,POOL-BASE,pool_entries,pool_entries+capacity*20,0,0,0,pool_entries);struct.pack_into('<I',memory,POOL-BASE+88,0)
    for i in range(capacity):struct.pack_into('<I',memory,pool_entries-BASE+i*20,pool_entries+(i+1)*20 if i+1<capacity else 0)
    oracle.initial=bytes(memory);oracle.case([load(data,local=1,filename=filename)])
    symbols=[];scripts=[]
    for bucket in range(4096):
        symbol=oracle.word(BUCKETS+bucket*4);chain=0
        while symbol:
            kind=cpu.mem_read(symbol+1,1)[0];key=oracle.word(symbol+4);at=oracle.word(symbol+12);name=readable(key)
            if kind==7:scripts.append((key,name,at))
            else:symbols.append({'name':hex(key),'text':name,'type':kind,'value':value(kind,at)})
            symbol=oracle.word(symbol+16);chain+=1;assert chain<100
    bodies=[]
    for key,name,stored in scripts:
        program=invoke(0x475e80,CACHE,[key],4);assert program
        size=oracle.word(stored+4);cursor=program;tokens=[]
        while cursor<program+size:
            tag=cpu.mem_read(cursor,1)[0];next_at=invoke(0x46f690,0,[cursor],0)
            assert cursor<next_at<=program+size,(file,name,hex(tag),cursor-program,size)
            token={'offset':cursor-program,'type':hex(tag)}
            if tag==0x16:
                checksum=oracle.word(cursor+1);token.update(name=hex(checksum),text=readable(checksum))
            elif tag in [0x1b,0x1c]:token['text']=string(cursor+5)
            elif tag in [0x17,0x18]:token['word']=hex(oracle.word(cursor+1))
            tokens.append(token);cursor=next_at
        bodies.append({'name':hex(key),'text':name,'bytes':size,'prepared_sha256':hashlib.sha256(cpu.mem_read(program,size)).hexdigest(),'tokens':tokens})
    results.append({'path':str(path.relative_to(ROOT)),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'symbols':symbols,'scripts':bodies})
    print('Original loaded',file,len(symbols),'data symbols',len(bodies),'scripts',flush=True)
target=ROOT/'local/analysis/tr-level-selection-v1-original.json';assert not target.exists()
target.write_text(json.dumps({'specimen_sha256':SHA256,'files':results,'scope':'Read-only original whole QB load, cache acquisition and token stepping; references only, no gameplay or original camera execution.','completion_credit':0,'matching_credit':0,'playable':False},indent=2)+'\n')
for f in results:
    for s in f['scripts']:
        if (s['text'] or '').lower() in ['load_tr','tr_setup','tr_startup','tr_initailizer'] or any('ware_restart' in (t.get('text') or '').lower() for t in s['tokens']):
            print(f['path'],s['text'],[(t['offset'],t.get('text',t.get('word',t['type']))) for t in s['tokens']],flush=True)
