"""Test-only original/host callback witnesses and live-link mutation controls."""
CONTROL,OBSLOG=BASE+0x180000,BASE+0x181000
callbacks=[(oracle.stop+0x300+i*16,name,kind,argc) for i,(name,kind,argc) in enumerate([
 ('factory',1,0),('initialize',2,1),('finalize',3,0),('moved',4,0),('before_delete',5,0),('delete',6,1),('add',7,2),('add_alt',8,2)])]
targets={name:at for at,name,kind,argc in callbacks}
def callback(cpu,at,size,user):
    _,name,kind,argc=next(row for row in callbacks if row[0]==at)
    sp=cpu.reg_read(UC_X86_REG_ESP);self=0 if kind==1 else cpu.reg_read(UC_X86_REG_ECX)
    arg=oracle.word(sp+4) if argc else 0;arg2=oracle.word(sp+8) if argc==2 else 0
    read=lambda p,o:oracle.word(p+o) if p else 0
    n=oracle.word(OBSLOG);assert n<64;owner=self if kind>=7 else read(self,12)
    oracle.setword(OBSLOG,n+1)
    cpu.mem_write(OBSLOG+64+n*48,struct.pack('<12I',kind,self,arg,arg2,owner,read(owner,0x104),read(self,0x10),read(self,0x14),read(owner,0x100),oracle.word(MANAGER+0x44),0,0))
    if kind==oracle.word(CONTROL+4) and n==oracle.word(CONTROL+8):
        for offset in [12,20]:
            write=oracle.word(CONTROL+offset)
            if write:oracle.setword(write,oracle.word(CONTROL+offset+4))
    cpu.reg_write(UC_X86_REG_EAX,oracle.word(CONTROL) if kind==1 else self)
    cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4+argc*4)
for at,name,kind,argc in callbacks:
    oracle.cpu.hook_add(UC_HOOK_CODE,callback,begin=at,end=at)
    extra.setdefault('native_callbacks',[]).append({'module':'composite-construction-callback.wasm','export':'fixture_composite_'+name,'original':at})
def witness_graph():
    g=CompositeGraph();g.image[CONTROL-BASE:CONTROL-BASE+0x2000]=bytes(0x2000)
    vt=g.alloc(52)
    for off,name in [(0,'delete'),(8,'initialize'),(12,'finalize'),(16,'before_delete'),(36,'moved')]:
        g.put(vt+off,'<I',targets[name]);fields.add(vt+off)
    g.registry([(0x12345678,targets['factory'])]);return g,vt
def mutate(g,kind,ordinal,first,second=(0,0)):
    g.put(CONTROL+4,'<6I',kind,ordinal,*first,*second)
