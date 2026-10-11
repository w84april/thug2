"""Explicit resident-file/GPU/heap-ownership comparison ports for real training."""
AM,ATABLE,AB,TEXCACHE,FILE,IO,IOC,IOLOG,TEXDATA,DEVICE,DVT,TVT,CONTROL,GLOG,OWNER_HEADER,TEXTURES=[BASE+n for n in
 [0xf0000,0xf0100,0xf0200,0xf0300,0xf0400,0xf0500,0xf0600,0xf0700,0xf0e00,0xf1000,0xf1100,0xf1200,0xf1300,0xf1400,0xf1380,0xf3000]]
memory[AM-BASE:AM-BASE+0x4000]=bytes(0x4000)
put(AM+0x1c,'<I',ATABLE);put(AM+0x14,'<B',0x5a);put(ATABLE,'<6I',4,AB,0,0xffffffff,0,0)
put(DEVICE,'<I',DVT);put(CONTROL,'<3I',0,0,0x1234);put(OWNER_HEADER,'<I',HSTATE)
MODELFILE,MODELDATA=BASE+0xf4080,BASE+0xf9000
model_path=ROOT/'local/game-files/Game/Data/models/GameObjects/SKATE/Letter_S/Letter_S.mdl.xbx';model_bytes=model_path.read_bytes()
assert len(model_bytes)==4710
memory[MODELDATA-BASE:MODELDATA-BASE+len(model_bytes)]=model_bytes
memory[MODELFILE-BASE:MODELFILE-BASE+0x3c]=bytes(0x3c)
texture_path=ROOT/'local/game-files/Game/Data/models/GameObjects/SKATE/Letter_S/Letter_S.tex.xbx';texture_bytes=texture_path.read_bytes()
assert hashlib.sha256(texture_bytes).hexdigest()=='66bc9d8ac9cf881dbe381764e02fb4cd86976de99ae2fecfc5842d62a10406b3'
memory[TEXDATA-BASE:TEXDATA-BASE+len(texture_bytes)]=texture_bytes
put(IO,'<5I',IOC,0,0,0,0);put(IOC,'<6I',TEXDATA,len(texture_bytes),FILE,0,IOLOG,CONTEXT)
for name,a,value in [('thug_asset_manager',0x6918dc,AM),('thug_asset_io_draft',0x300,IO),('thug_mesh_device',0x7d69e0,DEVICE),
 ('thug_texture_resource_registry_draft',0x7cc254,0),('thug_asset_options_mask_draft',0x6918d8,0)]:glob(name,a,value)
for i,v in enumerate([4,TEXCACHE,0,0xffffffff,0,0]):glob('thug_model_texture_table_draft',0x700f04+i*4,v,offset=i*4)
for i in range(96):glob('thug_asset_options_storage_draft',0x691758+i*4,0xa5a5a5a5,offset=i*4)
exports += [[0x6459a8,'thug_texture_asset_methods_draft'],[0x645888,'thug_model_asset_methods_draft'],
 [0x6455c0,'thug_asset_link_methods'],[0x645564,'thug_asset_detached_link_methods_draft'],
 [0x649bb4,'thug_texture_dictionary_base_methods_draft'],[0x64a824,'thug_texture_dictionary_pc_methods_draft'],
 [0x649af0,'thug_texture_wrapper_base_methods_draft'],[0x64a770,'thug_texture_wrapper_pc_methods_draft']]
exports += [[0x691758+i*96,'thug_asset_options_storage_draft',i*96] for i in range(4)]
def asset_identity(cpu,at,size,user):
    p=cpu.reg_read(UC_X86_REG_ECX);fields.update([p,p+0x38,p+0x4c])
for a in [0x407910,0x40a580,0x409c40]:oracle.cpu.hook_add(UC_HOOK_CODE,asset_identity,begin=a,end=a)
for a in [0x49f830,0x4c8070,0x49f200]:oracle.cpu.hook_add(UC_HOOK_CODE,identities,begin=a,end=a)
CREATE,LOCK,UNLOCK=oracle.stop+0x300,oracle.stop+0x310,oracle.stop+0x320
put(DVT+0x5c,'<I',CREATE);put(TVT+0x4c,'<2I',LOCK,UNLOCK)
io_calls=Counter();gpu_calls=Counter();raw_sync=[]
def texture_io(cpu,address,size,user):
    sp=cpu.reg_read(UC_X86_REG_ESP);arg=lambda i:oracle.word(sp+4+i*4);cleanup=0
    if address==0x5b6c60:
        actual=bytes(cpu.mem_read(arg(0),256)).split(b'\0',1)[0]
        assert actual in [b'models\\gameobjects\\skate\\letter_s\\letter_s.tex.Xbx',b'models\\gameobjects\\skate\\letter_s\\letter_s.mdl.Xbx'],actual
        model=actual.endswith(b'.mdl.Xbx');oracle.setword(IOC,MODELDATA if model else TEXDATA);oracle.setword(IOC+4,len(model_bytes) if model else len(texture_bytes));oracle.setword(IOC+8,MODELFILE if model else FILE)
        raw_sync.append(arg(1));op,a,b,c=1,arg(1)&255,arg(2),0;result=oracle.word(IOC+8)
    elif address==0x5b63a0:
        assert cpu.reg_read(UC_X86_REG_ECX)==oracle.word(IOC+8);op,a,b,c=2,oracle.word(IOC+8),0,0;result=oracle.word(IOC+4)
    elif address==0x5b6740:
        assert cpu.reg_read(UC_X86_REG_ECX)==oracle.word(IOC+8) and arg(1)==1 and arg(2)==oracle.word(IOC+4)
        op,a,b,c=3,arg(0),arg(1),arg(2);result=oracle.word(IOC+4);cleanup=12;cpu.mem_write(a,bytes(cpu.mem_read(oracle.word(IOC),oracle.word(IOC+4))))
    else:assert address==0x5b68a0 and arg(0)==oracle.word(IOC+8);op,a,b,c=4,arg(0),0,0;result=1
    i=oracle.word(IOC+12);assert i<8;oracle.setword(IOC+12,i+1)
    cpu.mem_write(IOLOG+i*32,struct.pack('<8I',op,a,b,c,oracle.word(IOC+8),oracle.word(IOC+4),oracle.word(CONTEXT+8),oracle.word(IOC)))
    io_calls[hex(address)]+=1;cpu.reg_write(UC_X86_REG_EAX,result);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4+cleanup)
for a in [0x5b6c60,0x5b63a0,0x5b6740,0x5b68a0]:oracle.cpu.hook_add(UC_HOOK_CODE,texture_io,begin=a,end=a)
def texture_gpu(cpu,address,size,user):
    sp=cpu.reg_read(UC_X86_REG_ESP);arg=lambda i:oracle.word(sp+4+i*4)
    op={CREATE:1,LOCK:2,UNLOCK:3,0x5ba090:4}[address];i=oracle.word(CONTROL);assert i<200
    oracle.setword(CONTROL,i+1);log=[op]+[0]*14+[oracle.word(CONTEXT+8)];result=0
    if op==1:
        args=[arg(k) for k in range(9)];count=oracle.word(CONTROL+4);assert count==0
        p=TEXTURES;oracle.setword(CONTROL+4,1);oracle.setword(p,TVT);oracle.setword(args[7],p);log[1:11]=args+[p];cleanup=36
    elif op==2:
        p,level,out,rect,flags=[arg(k) for k in range(5)];assert level<2
        data=p+0x100+level*0x100;pitch=oracle.word(CONTROL+8);oracle.setword(out,pitch);oracle.setword(out+4,data)
        log[1:7]=[p,level,rect,flags,pitch,data];cleanup=20
    elif op==3:log[1:3]=[arg(0),arg(1)];cleanup=8
    else:
        # New allocator adapter query. The original allocator's header layout
        # cannot be reused with the pinned rewind heap's previous-pointer header.
        # All allocations in this fixture belong to its ordinary temporary heap.
        assert HEAP<=arg(0)<BASE+SIZE;log[1]=arg(0);result=OWNER_HEADER;cleanup=0
    cpu.mem_write(GLOG+i*64,struct.pack('<16I',*log));gpu_calls[op]+=1
    cpu.reg_write(UC_X86_REG_EAX,result);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4+cleanup)
for a in [CREATE,LOCK,UNLOCK,0x5ba090]:oracle.cpu.hook_add(UC_HOOK_CODE,texture_gpu,begin=a,end=a)
model_load_code=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(0x4935e0-0x400000,765),0x4935e0));model_load_hits=Counter()
oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:model_load_hits.update([at]),begin=0x4935e0,end=0x4938dc)
for a in [0x4087b0,0x408440,0x40a580,0x40a720,0x40a620,0x40a5a0,0x49f050,0x4c72e0,0x4cb420,0x409c40,0x407840,0x409eb0,0x409e10,0x409c70]:oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:native_hits.update([hex(at)]),begin=a,end=a)

model_file_code=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(0x409eb0-0x400000,645),0x409eb0));model_file_hits=Counter()
oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:model_file_hits.update([at]),begin=0x409eb0,end=0x40a134)
