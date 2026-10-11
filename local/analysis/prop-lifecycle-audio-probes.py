"""Only included by the new prop probe, after shared lifecycle tests."""
from unicorn.x86_const import UC_X86_REG_EIP
AUDIO_CONTROL,AUDIO_LOG,AUDIO_CB=BASE+0x1b0000,BASE+0x1b1000,oracle.stop+0x500
def audio_callback(cpu,at,size,user):
    sp=cpu.reg_read(UC_X86_REG_ESP);buffer=oracle.word(sp+4);n=oracle.word(AUDIO_LOG);assert n<100
    oracle.setword(AUDIO_LOG,n+1);watch=oracle.word(AUDIO_CONTROL);watch2=oracle.word(AUDIO_CONTROL+4)
    cpu.mem_write(AUDIO_LOG+32+n*16,struct.pack('<4I',buffer,oracle.word(watch) if watch else 0,oracle.word(watch2) if watch2 else 0,0))
    for offset in [8,16]:
        write=oracle.word(AUDIO_CONTROL+offset)
        if write:oracle.setword(write,oracle.word(AUDIO_CONTROL+offset+4))
    cpu.reg_write(UC_X86_REG_EAX,oracle.word(AUDIO_CONTROL+24));cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+8)
oracle.cpu.hook_add(UC_HOOK_CODE,audio_callback,begin=AUDIO_CB,end=AUDIO_CB)
extra['native_callbacks']=[{'module':'prop-lifecycle-audio-callback.wasm','export':'fixture_prop_audio_stop','original':AUDIO_CB}]
class AudioGraph(PropGraph):
    def __init__(self):
        super().__init__();self.image[AUDIO_CONTROL-BASE:AUDIO_CONTROL-BASE+0x2000]=bytes(0x2000)
        self.vt=self.alloc(80);self.buffer=self.alloc(8);self.put(self.vt+0x48,'<I',AUDIO_CB);fields.add(self.vt+0x48);self.put(self.buffer,'<I',self.vt)
    def pending(self,owners,ids):
        nodes=[self.alloc(24) for _ in owners]
        for i,(owner,id_) in enumerate(zip(owners,ids)):
            self.put(nodes[i],'<6I',id_,0x98765432,0xa5a5a5a5,owner,nodes[i+1] if i+1<len(nodes) else 0,nodes[i-1] if i else 0)
        return nodes
    def audio_state(self,slot=0,id_=0x12345678,name=0x87654321,active=1,buffer=True):
        return {0x6f7a68+slot*60:id_,0x6f7a6c+slot*60:name,0x6f85c8+slot*24:self.buffer if buffer else 0,0x6f85d8+slot*24:active}
for slot,buffer,active in itertools.product([0,47],[False,True],[0,1,255]):
    g=AudioGraph();run(g,[call(0x47c7a0,args=[slot])]*2,f'audio stop slot{slot}/buffer{buffer}/active{active}',g.audio_state(slot,active=active,buffer=buffer))
for mode in ['none','id first','id last','inactive first duplicate','name first','name last','name inactive','zero id']:
    for debug in [0,1]:
        g=AudioGraph();g.symbol(0x6d2e270e,1,debug);g.symbol(0xd7bb618d,1,1)
        key=0 if mode=='zero id' else 0x12345678;changes={}
        if mode!='none':
            slot=47 if mode.endswith('last') else 0
            changes=g.audio_state(slot,id_=key if mode.startswith('id') or mode=='zero id' else 2,name=key if mode.startswith('name') else 3,active=0 if mode=='name inactive' else 1)
            if mode=='inactive first duplicate':
                changes=g.audio_state(0,id_=key,active=0);changes.update(g.audio_state(47,id_=key))
        run(g,[call(0x47ad80,0,[key])],f'voice lookup {mode}/debug{debug}',changes)
for owners in [[],[P+4],[P],[P,P],[P,P+4,P],[P+4,P,P+4]]:
    for device,mode in [(0,0),(1,0),(1,2),(1,6),(1,7)]:
        g=AudioGraph();nodes=g.pending(owners,[0x12345678]*len(owners));changes=g.audio_state()
        changes.update({0x6f85b0:nodes[0] if nodes else 0,0x6f85bc:len(nodes),0x7d6a38:device,0x7cefa8:mode})
        if nodes:g.put(AUDIO_CONTROL,'<2I',nodes[0]+8,nodes[0]+0x10)
        run(g,[call(0x47bb50,0,[P])]*2,f'pending removal owners{owners}/device{device}/mode{mode}',changes)
for state in ['zero id','missing id','inactive','null buffer','duplicate inactive first','last slot']:
    g=AudioGraph();id_=0 if state=='zero id' else 0x12345678;nodes=g.pending([P],[id_]);changes=g.audio_state(47 if state=='last slot' else 0,id_=id_^1 if state=='missing id' else id_,active=0 if state in ['inactive','duplicate inactive first'] else 1,buffer=state!='null buffer')
    if state=='duplicate inactive first':changes.update(g.audio_state(47,id_=id_))
    changes.update({0x6f85b0:nodes[0],0x6f85bc:0});run(g,[call(0x47bb50,0,[P])],f'pending sound state {state}',changes)
# A stop can change the record links; traversal retains the previously captured
# next, whereas unlink reads both links after the callback returns.
for mutation in ['next','previous','both','owner']:
    g=AudioGraph();nodes=g.pending([P,P,P+4],[0x12345678]*3);changes=g.audio_state();changes.update({0x6f85b0:nodes[0],0x6f85bc:3})
    g.put(AUDIO_CONTROL,'<7I',nodes[0]+8,nodes[0]+16,nodes[0]+(12 if mutation=='owner' else 16),P+4 if mutation=='owner' else nodes[2],0,0,0xffffffff)
    if mutation in ['previous','both']:
        # An independent predecessor exercises live unlink without making a
        # cycle through the traversal's captured successor (the old test did).
        predecessor=g.alloc(24);g.put(predecessor,'<6I',0,0,0,P+4,nodes[0],0)
        g.put(AUDIO_CONTROL+8,'<4I',nodes[0]+20,predecessor,nodes[0]+16,nodes[2] if mutation=='both' else nodes[1])
    run(g,[call(0x47bb50,0,[P])],f'audio callback live link mutation {mutation}',changes)
# Sound concrete destruction really removes owner records and then changes to
# the base component method table; no cleanup callback replaces either routine.
g=AudioGraph();nodes=g.pending([P,P+4,P],[0x12345678]*3);changes=g.audio_state();changes.update({0x6f85b0:nodes[0],0x6f85bc:3})
run(g,[call(0x432d90,P),call(0x433160,P,[1])],'concrete Sound disposal with active pending list',changes)
