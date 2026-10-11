"""Compare the complete surface-mark projection against the pinned PC body."""
import struct,json,subprocess,random,math,hashlib
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EAX,UC_X86_REG_EIP,UC_X86_REG_FPSW,UC_X86_REG_FPTAG,UC_X86_REG_MXCSR
from script_heap_oracle import ScriptHeapOracle
from specimen import ROOT

def build_wall_marks(out):
    BASE,SIZE=0x1800000,0x200000
    CONTEXT,MANAGER,DEVICE,METHODS,GPU=BASE+0x20,BASE+0x100,BASE+0x400,BASE+0x500,BASE+0x800
    LIST,GEOMETRY,CONTAINER,MESHES,MESH,VB,IB,VERTICES,INDICES,PROJECTION,TEXTURE,PREVIOUS=[BASE+x for x in [0x1000,0x1100,0x1200,0x1300,0x1400,0x1500,0x1600,0x1700,0x1800,0x1900,0x1a00,0x1b00]]
    TABLE,BUCKETS,LOG,HEAP=BASE+0x2000,BASE+0x2100,BASE+0x4000,BASE+0x20000
    TLS=0x7d2100;GET=0x3f00100
    memory=bytearray(b'\xad'*SIZE)
    def put(at,fmt,*v):struct.pack_into(fmt,memory,at-BASE,*v)
    def patch(at,fmt,*v):return [at,struct.pack(fmt,*v).hex()]
    def bits(f):return int.from_bytes(struct.pack('<f',f),'little')
    put(CONTEXT,'<8I',HEAP,BASE+0x80000,0,LOG,BASE,BASE+SIZE,0,0);put(MANAGER+0x124,'<I',MANAGER+0x200)
    put(DEVICE,'<2I',METHODS,GPU);put(METHODS+0x194,'<I',GET);put(GPU,'<I',0)
    put(LIST,'<2I',GEOMETRY,0);put(GEOMETRY+0x14,'<I',CONTAINER)
    put(CONTAINER+0x3c,'<2I',MESHES,1);put(MESHES,'<I',MESH)
    put(MESH,'<I',0);put(MESH+0x18,'<8B',16,0,1,0,12,0,0,0)
    put(MESH+0x24,'<H',3);put(MESH+0xcc,'<I',VB);put(MESH+0x54,'<I',IB)
    put(VB,'<9I',64,0,0,VERTICES,0,0,0,0,0);put(IB,'<6I',0,0,0,0,INDICES,0)
    for i,xyz in enumerate([(-1,-1,0),(1,-1,0),(0,1,0),(1,1,0)]):put(VERTICES+i*16,'<3fI',*xyz,0x40112233+i*0x111111)
    put(INDICES,'<6H',0,1,2,3,3,0)
    put(PROJECTION,'<13f4I',0,0,10,1,0,0,-10,1,4,4,0,1,2,TEXTURE,0,0,0)
    put(TEXTURE+8,'<I',0);put(TEXTURE+0x10,'<I',0x12345678)
    put(PREVIOUS,'<4f',-2,0,10,1)
    put(TABLE,'<6I',2,BUCKETS,0,0xffffffff,0,0)
    for i in range(4):put(BUCKETS+i*12,'<3I',0,0,0)
    ADAPTER=BASE+0x50
    put(ADAPTER,'<4I',CONTEXT,0,0,0)
    globals_=[['thug_decal_buffers',0x7004b0,4],['thug_crt_random_state',TLS+0x14,4],['thug_lookup_node_pool',0x7d1808,4],['thug_decal_area_threshold',0x67ddf0,4],['thug_mesh_device',0x7d69e0,4],['thug_mesh_vertex_registry',0x7865e4,4],['thug_mesh_index_registry',0x7865e8,4]]
    defaults=[TABLE,1,0,bits(82944),DEVICE,0,0]
    for name,at,size in [('thug_decal_work_stack',0x6fc4a0,0x4008),('thug_decal_scratch_vertices',0x7052c0,768)]:
     for i in range(0,size,4):globals_.append([name,at+i,4,i]);defaults.append(0)
    SCENE,NODES,OBJECT_TABLE,OBJECT_BUCKETS,INSTANCE,COLLISION,PREV_TABLE,PREV_BUCKETS,POINT,SYMBOL,GRID,SYMBOLS=[BASE+x for x in [0x2600,0x2400,0x2800,0x2900,0x2a00,0x2b00,0x2c00,0x2d00,0x2e00,0x3000,0x10000,0x15000]]
    put(TEXTURE+4,'<I',0xcafebabe)
    DICTIONARY,TEX_TABLE,TEX_BUCKETS,TEX_NAME=BASE+0x3100,BASE+0x3200,BASE+0x3300,BASE+0x3400
    put(DICTIONARY+12,'<I',TEX_TABLE);put(TEX_TABLE,'<6I',2,TEX_BUCKETS,1,0,0,0)
    for i in range(4):put(TEX_BUCKETS+i*12,'<3I',0,0,0)
    put(TEX_BUCKETS+36,'<3I',0xffffffff,TEXTURE,0);put(TEX_NAME,'<I',0)

    put(NODES,'<4I',0,SCENE,0,NODES+16);put(NODES+16,'<4I',0,0xffffffff,0,NODES+16)
    put(SCENE+0xd0,'<2I',OBJECT_TABLE,GRID)
    put(OBJECT_TABLE,'<6I',2,OBJECT_BUCKETS,1,0,0,0)
    for i in range(4):put(OBJECT_BUCKETS+i*12,'<3I',0,0,0)
    put(OBJECT_BUCKETS+12,'<3I',0x101,GEOMETRY,0)
    put(INSTANCE,'<3I',0x645c18,0x101,0);put(INSTANCE+12,'<I',COLLISION)
    put(COLLISION+0x10,'<8f',-1,-1,0,1,1,1,0,1)
    put(GRID,'<10f2I',-50,-50,-50,1,50,50,50,1,100,100,1,1)
    put(GRID+0x54,'<I',1);put(GRID+0x5c,'<I',MESHES+0x40);put(MESHES+0x40,'<I',INSTANCE)
    put(PREV_TABLE,'<6I',2,PREV_BUCKETS,0,0,0,0)
    for i in range(4):put(PREV_BUCKETS+i*12,'<3I',0,0,0)
    put(POINT,'<4f2I',-2,0,10,1,99,999)
    memory[SYMBOLS-BASE:SYMBOLS-BASE+0x4000]=bytes(0x4000)
    put(SYMBOLS+(0x26fcb7be&0xfff)*4,'<I',SYMBOL);put(SYMBOL,'<5I',0x100,0x26fcb7be,0,128,0)
    extra=[('thug_decal_previous_points',0x7004b4,PREV_TABLE),('thug_decal_texture_dictionary',0x700f20,DICTIONARY),
     ('thug_collision_scene_list',0x6fa7ec,NODES),('thug_script_symbol_buckets',0x6f3624,SYMBOLS),
     ('thug_decal_reserved_slots',0x67dde0,128),('thug_decal_fade_step',0x67dde4,8),('thug_frame_counter',0x7d1ec8,60),
     ('thug_frame_rate',0x684fd0,bits(60)),('thug_frame_length_scale',0x684fc8,bits(1)),('thug_decal_light_count',0x6faef4,0)]
    for name,at,value in extra:globals_.append([name,at,4]);defaults.append(value)
    globals_.append(['thug_collision_grid_stamp',0x693998,1]);defaults.append(0)
    for name,at,n in [('thug_decal_selected_geometry',0x700510,128),('thug_decal_selected_collision',0x700710,128),
     ('thug_collision_selected_scenes',0x6fa738,16),('thug_collision_selected_grids',0x6fa778,16),('thug_collision_grid_output',0x691998,2048)]:
     for i in range(n):globals_.append([name,at+i*4,4,i*4]);defaults.append(0)
    # Repack the complete pinned training collision grid, its605 objects and
    # checksum lookup. Each test exposes one sampled face as a render mesh;
    # other render geometries have no mesh, while all real bounds/flags/order stay.
    training_path=out/'scene-training.bin';training=training_path.read_bytes()
    proof=json.loads((out.parent/'collision-browser.json').read_text())
    assert hashlib.sha256(training).hexdigest()==proof['artifact_hashes'][str(training_path.relative_to(ROOT))]
    TRAIN_GRID,TRAIN_INST,TRAIN_GEO,TRAIN_LIST,TRAIN_TABLE,TRAIN_BUCKETS,TRAIN_LINKS,TRAIN_RENDER=[BASE+x for x in [0x80000,0x85000,0x89000,0x93000,0xb0000,0xb1000,0xb4000,0xb7000]]
    memory[TRAIN_GRID-BASE:TRAIN_GRID-BASE+0x4b30]=training[0x200000:0x204b30]
    memory[TRAIN_INST-BASE:TRAIN_INST-BASE+605*24]=training[0x100000:0x100000+605*24]
    pointer_fields=[INSTANCE]+[TRAIN_INST+i*24 for i in range(605)]
    for i in range(605):
        old=struct.unpack_from('<I',training,0x100000+i*24+12)[0]-0x1000000
        memory[TRAIN_GEO-BASE+i*64:TRAIN_GEO-BASE+(i+1)*64]=training[old:old+64]
        put(TRAIN_INST+i*24+12,'<I',TRAIN_GEO+i*64)
        put(TRAIN_RENDER+i*32+20,'<I',0)
    cursor=TRAIN_LIST
    for i in range(400):
        cell=TRAIN_GRID+i*48+0x30;n,old=struct.unpack_from('<I4xI',memory,cell-BASE+0x24)
        pointers=struct.unpack_from('<'+'I'*n,training,old-0x1000000)
        put(cell+0x2c,'<I',cursor)
        for pointer in pointers:put(cursor,'<I',TRAIN_INST+pointer-0x1100000);cursor+=4
    assert cursor<TRAIN_TABLE
    put(TRAIN_TABLE,'<6I',10,TRAIN_BUCKETS,605,0,0,0)
    for i in range(1024):put(TRAIN_BUCKETS+i*12,'<3I',0,0,0)
    cursor=TRAIN_LINKS
    for i in range(605):
        key=struct.unpack_from('<I',memory,TRAIN_INST-BASE+i*24+4)[0];bucket=TRAIN_BUCKETS+(key&1023)*12
        value,next_=struct.unpack_from('<2I',memory,bucket-BASE+4)
        if value:
            put(cursor,'<3I',key,TRAIN_RENDER+i*32,next_);put(bucket+8,'<I',cursor);cursor+=12
        else:put(bucket,'<3I',key,TRAIN_RENDER+i*32,0)
    assert cursor<TRAIN_RENDER
    EMITTER,EMITTER_OWNER,NETWORK,CONNECTION,CLIENT,PEER,PEER_LINK,EMIT_FROM,EMIT_TO=[BASE+x for x in [0xc0000,0xc0100,0xc1000,0xc2000,0xc3000,0xc6000,0xc7000,0xc7100,0xc7140]]
    ROTATED_TEXTURE=BASE+0xc7200
    put(ROTATED_TEXTURE+4,'<2I',0xfaceb00c,1)
    put(ROTATED_TEXTURE+0x10,'<I',ROTATED_TEXTURE+0x20);put(ROTATED_TEXTURE+0x20,'<I',0x87654321)
    put(EMITTER+12,'<I',EMITTER_OWNER);put(EMITTER+0x1c,'<2I',TEXTURE,ROTATED_TEXTURE)
    put(EMITTER_OWNER+0x14,'<I',0x12345678)
    put(NETWORK,'<3I',4,CONNECTION,CLIENT);put(CONNECTION+0x1e84,'<I',0)
    put(CLIENT+8,'<I',0xfffffffa);put(CLIENT+0x1e84,'<I',8)
    put(CLIENT+0x1e8c,'<5I',0x647578,0xffffffff,0,PEER_LINK,PEER_LINK)
    put(PEER_LINK,'<5I',0x647578,PEER,0,CLIENT+0x1e8c,CLIENT+0x1e8c)
    for k in range(3):
        node=PEER+k*20;put(node,'<5I',0x6474cc+4*k,0xffffffff,0,node,node)
    put(PEER+0x3c,'<I',7);put(PEER+0x60,'<I',1)
    put(PEER+0x78,'<256I',*[0xfffffffe+i for i in range(2)],*[i for i in range(254)])
    put(MANAGER+0x12c,'<I',MANAGER+0x400)
    put(EMIT_FROM,'<4f',0,0,10,1);put(EMIT_TO,'<4f',0,0,-10,1)
    put(SYMBOLS+(0x2d7df904&0xfff)*4,'<I',SYMBOL+32);put(SYMBOL+32,'<5I',0x200,0x2d7df904,0,bits(60),0)
    globals_.append(['thug_network_state',0x7cce14,4]);defaults.append(NETWORK)
    for i,value in enumerate([0x12345678,0xabcdef01,123]):
        globals_.append(['thug_random_state',0x690fd4+i*4,4,i*4]);defaults.append(value)
    exports=[[0x645c18,'thug_static_collision_methods']]
    exports += [[0x6474cc+4*k,'thug_'+n+'_queue_methods'] for k,n in enumerate(['plain','reliable','sequenced'])]
    exports += [[0x647578+4*k,'thug_'+n+'_node_methods'] for k,n in enumerate(['plain','reliable','sequenced'])]
    pointer_fields=set(pointer_fields)|{at for at in range(BASE,BASE+SIZE,4) if int.from_bytes(memory[at-BASE:at-BASE+4],'little') in dict(exports)}
    functions={'0x4928a0':{'name':'thug_decal_project_scene','this':False,'result':'byte','cleanup':0,'memory':True,'float_args':[2,3,4,5,6]}}
    functions['0x51dbc0']={'name':'thug_wall_mark_emit','this':True,'result':'void','cleanup':44,'memory':True,'stack_args':list(range(11))}
    observed=[0x51dbc0,0x403de0,0x44e4f0,0x4549f0,0x532ea0,0x459e50,0x457eb0,0x455040,0x455650,0x457350,0x4928a0,0x5b80d0,0x462740,0x5be970,0x412750,0x418710,0x48c980,0x490ec0,0x4b87b0,0x5480c0,0x4b9c30,0x4b9a60,0x4d69e0,0x4d4be0,0x4b8220,0x490d50,0x490d80,0x4b88d0,0x4b7f30,0x5e17ed,0x5e16ea,0x5c0985,0x5c0b39,0x5df4ac,0x623ba3,0x6236fc]
    oracle=ScriptHeapOracle(memory,BASE,CONTEXT,MANAGER,globals_,defaults,functions,observe=observed,instruction_limit=20000000,scope_entries={MANAGER+0x200:1,MANAGER+0x400:4})
    for at,fn in [(0x684ff4,0x5e17ed),(0x685000,0x5e16ea),(0x684fe4,0x5df4ac)]:oracle.setword(at,fn)
    def external(cpu,at,size,user):
     sp=cpu.reg_read(UC_X86_REG_ESP);cleanup=0;result=0
     if at==0x629be5:result=TLS
     elif at==0x62411b:oracle.record(2,oracle.word(sp+4),1,0)
     else:
      device,stream,out_ptr,offset,stride=struct.unpack('<5I',cpu.mem_read(sp+4,20))
      assert device==DEVICE and stream==0
      for p in [out_ptr,offset,stride]:oracle.setword(p,0)
      oracle.setword(GPU,oracle.word(GPU)+1);cleanup=20
     cpu.reg_write(UC_X86_REG_EAX,result);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4+cleanup)
    for at in [0x629be5,0x62411b,GET]:oracle.cpu.hook_add(UC_HOOK_CODE,external,begin=at,end=at)
    padding_entries=0
    def seed_packet_padding(cpu,at,size,user):
        nonlocal padding_entries
        sp=cpu.reg_read(UC_X86_REG_ESP)
        # Only the two bytes never written by 51dbc0 are initialized. All 38
        # defined payload bytes and every original game/queue instruction run.
        cpu.mem_write(sp-0x26,bytes(2));padding_entries+=1
    oracle.cpu.hook_add(UC_HOOK_CODE,seed_packet_padding,begin=0x51dbc0,end=0x51dbc0)
    labels=[]
    def annotate(stages,patches):
        expected=bytearray(memory)
        for at,data in patches:expected[at-BASE:at-BASE+len(data)//2]=bytes.fromhex(data)
        def nanword(v):return v&0x7f800000==0x7f800000 and v&0x7fffff!=0
        for step in stages:
         for at,data in step['outputs']:expected[at-BASE:at-BASE+len(data)//2]=bytes.fromhex(data)
         typed=set()
         def floats(at,count,stride,offsets):
          typed.update(at+i*stride+k for i in range(count) for k in offsets)
         def buffer_fields(at):
          floats(at+0x3410,768,24,[0,4,8,16,20])
          floats(at+0x1c10,256,24,[0,4,8,12,16,20])
         buffer_fields(BASE+0x8000)
         for i in range(struct.unpack_from('<I',expected,CONTEXT-BASE+8)[0]):
          kind,size,route,at=struct.unpack_from('<4I',expected,LOG-BASE+i*48)
          if kind==1 and size==0x7c10:buffer_fields(at)
          if kind==1 and size==0x2000:floats(at,0x2000//24,24,[0,4,8,16,20])
         step['float_fields']=[at for at in sorted(typed) if nanword(struct.unpack_from('<I',expected,at-BASE)[0])]
         step['global_float_indices']=[]
         for i,(entry,value) in enumerate(zip(globals_,step['globals'])):
          name,_,_,*offsets=entry;offset=offsets[0] if offsets else 0
          is_float=(name=='thug_decal_area_threshold' or
           name=='thug_decal_work_stack' and offset>=8 and (offset-8)%24 in [0,4,8,16,20] or
           name=='thug_decal_scratch_vertices' and offset%128 in [0,4,8,16,20])
          if is_float and nanword(value):step['global_float_indices'].append(i)

    def run(label,p=(),tracking=0,repeats=1,texture=TEXTURE,changes=None,params=(4,4,0,1,2)):
     cpu=oracle.cpu
     cpu.reg_write(UC_X86_REG_FPSW,0);cpu.reg_write(UC_X86_REG_FPTAG,0xffff);cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
     args=[PROJECTION,PROJECTION+16,*[bits(v) for v in params],TEX_NAME,0x54628ed7,tracking,0,texture]
     steps=oracle.case([(0x4928a0,0,args)]*repeats,p,changes);labels.append(label)
     annotate(steps,p)
     print('Wall marks original',len(labels),label,flush=True)
     for s in steps:
      merged=[]
      for at,data in s['outputs']:
       if int.from_bytes(bytes.fromhex(data),'little') in dict(exports):pointer_fields.add(at)
       if merged and merged[-1][0]+len(merged[-1][1])//2==at:merged[-1][1]+=data
       else:merged.append([at,data])
      s['outputs']=merged
    run('untracked immediate mark')
    run('untracked scene miss',[patch(NODES+4,'<I',0xffffffff)])
    run('untracked object exclusion',[patch(INSTANCE+8,'<H',2)])
    run('untracked outside object bounds',[patch(COLLISION+0x10,'<8f',30,30,30,1,40,40,40,1)])
    run('tracking first point and unchanged repeat',tracking=99,repeats=2)
    linked=[patch(PREV_TABLE+8,'<I',1),patch(PREV_BUCKETS,'<3I',POINT,POINT,0)]
    run('tracking extended mark',linked,tracking=99)
    run('tracking unchanged',linked+[patch(POINT,'<4f',0,0,10,1)],tracking=99)
    run('tracking expired',linked+[patch(POINT+20,'<I',0)],tracking=99)
    run('tracking future time',linked+[patch(POINT+20,'<I',1001)],tracking=99)
    run('tracking different ID',linked,tracking=100)
    for stamp in [498,499,500,998,999,1000,0xffffffff]:
     run('tracking timestamp '+str(stamp),linked+[patch(POINT+20,'<I',stamp)],tracking=99)
    for x in [-65.99999,-66,-66.00001,66,100]:
     run('tracking distance '+str(x),linked+[patch(POINT,'<4f',x,0,10,1)],tracking=99)

    run('texture name lookup',texture=0)
    run('missing render geometry after candidate',[patch(OBJECT_BUCKETS+16,'<I',0)])
    run('tracking point plus scene miss',linked+[patch(NODES+4,'<I',0xffffffff)],tracking=99)
    run('tracked texture name lookup',linked,tracking=99,texture=0)
    run('untracked repeated pressure fading',repeats=18)
    for stamp in [254,255]:
     changes={i:stamp for i,g in enumerate(globals_) if g[0]=='thug_collision_grid_stamp'}
     run('query stamp wrapping '+str(stamp),changes=changes,repeats=2)
    for count in [0,2,3]:
     run('duplicate candidate list '+str(count),[patch(GRID+0x54,'<I',count),patch(MESHES+0x40,'<3I',INSTANCE,INSTANCE,INSTANCE)])
    for reserve in [0,1,255,256,257,0xffffffff]:
     run('script reserve/fade pressure '+str(reserve),[patch(SYMBOL+12,'<I',reserve)],repeats=2)
    # Multi-node previous-point chains verify advance-before-unlink ownership.
    for count in [1,2,4,8]:
        for match in [-1,0,count-1]:
            p=[patch(PREV_TABLE+8,'<I',count),patch(PREV_BUCKETS,'<3I',POINT,POINT,BASE+0x6000 if count>1 else 0)]
            for i in range(count):
                point=POINT if i==0 else BASE+0x7000+i*32
                p.append(patch(point,'<4f2I',-2-i,0,10,1,99 if i==match else 77,999 if i==match else 1))
                if i:
                    node=BASE+0x6000+(i-1)*16
                    p.append(patch(node,'<3I',point,point,node+16 if i+1<count else 0))
            run('previous collision-chain expired/reuse '+str((count,match)),p,tracking=99)
    # Multiple independently selected grids preserve shared stamp order and
    # per-scene geometry fallback. Objects repeat intentionally across grids.
    for scenes in [2,3,15]:
        p=[]
        for i in range(scenes):
            scene=SCENE if i==0 else BASE+0x50000+i*0x100
            grid=GRID if i==0 else BASE+0x52000+i*0x5000
            p += [patch(NODES+i*16,'<4I',0,scene,0,NODES+(i+1)*16),patch(scene+0xd0,'<2I',OBJECT_TABLE,grid)]
            if i:
                raw=bytearray(memory[GRID-BASE:GRID-BASE+0x4b30]);p.append([grid,raw.hex()])
        p.append(patch(NODES+scenes*16,'<4I',0,0xffffffff,0,NODES+scenes*16))
        run('ordered independent scenes '+str(scenes),p)
    geometry=json.loads((out/'geometry-fixtures.json').read_text());vertices=(out/'vertices.bin').read_bytes();normals=(out/'normals.bin').read_bytes()
    by_offset={o['object']:o for o in geometry['objects']}
    for sample in range(0,605,8):
        old=struct.unpack_from('<I',training,0x100000+sample*24+12)[0]-0x1000000;obj=by_offset[old]
        if not obj['faces']:continue
        face=(sample*13)%obj['faces'];small=training[old+10]
        start=struct.unpack_from('<I',training,old+12)[0]-0x1000000
        indices=struct.unpack_from('<3B' if small else '<3H',training,start+face*(8 if small else 10)+4)
        points=[struct.unpack_from('<3f',vertices,obj['vertex_start']+index*16) for index in indices]
        normal=struct.unpack_from('<3f',normals,obj['normal_start']+face*16)
        if not all(math.isfinite(x) for x in normal) or sum(x*x for x in normal)<.5:continue
        center=[sum(p[k] for p in points)/3 for k in range(3)]
        ends=[[center[k]+sign*normal[k]*32 for k in range(3)] for sign in [1,-1]]
        p=[patch(SCENE+0xd0,'<2I',TRAIN_TABLE,TRAIN_GRID),patch(TRAIN_RENDER+sample*32+20,'<I',CONTAINER),patch(PROJECTION,'<8f',*ends[0],1,*ends[1],1)]
        p += [patch(VERTICES+j*16,'<3f',*points[j]) for j in range(3)]
        run('actual training grid object '+str(sample)+' face '+str(face),p)
    def emit(label,kind=0,send=0,extent=4,p=(),changes=None,repeats=1):
        cpu=oracle.cpu
        cpu.reg_write(UC_X86_REG_FPSW,0);cpu.reg_write(UC_X86_REG_FPTAG,0xffff);cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
        initial=bytearray(memory)
        for at,data in p:initial[at-BASE:at-BASE+len(data)//2]=bytes.fromhex(data)
        words=list(struct.unpack_from('<4I',initial,EMIT_FROM-BASE))+list(struct.unpack_from('<4I',initial,EMIT_TO-BASE))
        args=[kind,*words,extent&0xffffffff,send]
        steps=oracle.case([(0x51dbc0,EMITTER,args)]*repeats,p,changes);labels.append(label)
        annotate(steps,p)
        for step in steps:
            # Explicit original by-value to captured port-vector ABI mapping.
            step['args']=[kind,EMIT_FROM,EMIT_TO,extent&0xffffffff,send,0]
            for at,data in step['outputs']:
                if int.from_bytes(bytes.fromhex(data),'little') in dict(exports):pointer_fields.add(at)
        print('Wall marks original',len(labels),label,flush=True)
    for kind in [0,1,2,255,256,257,0xffffffff]:
        for send in [0,1,256,257]:
            emit('emitter byte flags '+str((kind,send)),kind,send)
    for extent in [-1,0,1,30,100,1000,0x7fffffff,-0x80000000]:
        emit('emitter signed extent '+str(extent),1,1,extent)
    for active,connection_flags,peer_flags,empty in [(0,0,1,False),(4,8,1,False),(4,0,8,False),(4,0,1,True),(4,0,0,False),(8,0,1,False)]:
        p=[patch(NETWORK,'<I',active),patch(CONNECTION+0x1e84,'<I',connection_flags),patch(PEER+0x60,'<I',peer_flags)]
        if empty:p += [patch(CLIENT+0x1e8c+12,'<2I',CLIENT+0x1e8c,CLIENT+0x1e8c)]
        emit('emitter network/peer gates '+str((active,connection_flags,peer_flags,empty)),1,1,p=p)
    emit('emitter repeated queued records',1,1,repeats=4)
    emit('emitter sends despite scene miss',1,1,p=[patch(NODES+4,'<I',0xffffffff)])
    emit('emitter falls back to named texture',0,1,p=[patch(EMITTER+0x1c,'<I',0)])
    for angle in [-90,0,.0001,30,90,180,360]:
        emit('emitter global angle '+str(angle),1,1,p=[patch(SYMBOL+32+12,'<f',angle)])
    for k,words in enumerate([
        [0x80000000,0,0x3f800000,0x7fc12345,0,0x80000000,0xbf800000,0xffc54321],
        [0x7f800000,0xff800000,0,1,0x7f800001,0xff800001,0x80000001,0x7f7fffff],
        [0x12345678,0xabcdef01,0xffffffff,0x7fffffff,0,1,2,3],
    ]):
        emit('emitter retained packet vector words '+str(k),k,1,p=[patch(NODES+4,'<I',0xffffffff),
            patch(EMIT_FROM,'<4I',*words[:4]),patch(EMIT_TO,'<4I',*words[4:])])
    fixture={'base':BASE,'memory':'wall-marks-memory.bin','globals':globals_,'functions':functions,'float_fields':[],
     'cases':oracle.cases,'case_labels':labels,'scope':'Complete scene projection and wall-mark emission, including the actual optional network queue path, through original scene/grid selection, concrete bounds virtuals, distinct direct/indirect textures, tracked point lifetime, full projection, fading and color refresh. The complete 605-object training collision grid is repacked with real bounds, flags and cell order; sampled collision faces serve as CPU render strips, not original render assets. All arena/global/return bytes and heap snapshots compared; only typed computed NaNs use classification. The two otherwise unwritten packet padding bytes are seeded to zero at original function entry, matching explicit port initialization; all 38 defined payload bytes remain exact, including raw nonfinite vector words. Initialized heap, selected math dispatch, CRT TLS/free and terminal GPU outputs remain explicit host boundaries.',
     'native_callbacks':[{'module':'decal-projection-callbacks.wasm','export':'fixture_projection_get','slots':[METHODS+0x194]},
     {'module':'decal-projection-callbacks.wasm','export':'fixture_projection_crt_free','original':0x62411b}],
     'pointer_initializers':[['thug_mesh_crt_heap',CONTEXT],['thug_mesh_crt_heap',0x62411b,4]],
     'pointer_exports':exports,'pointer_fields':sorted(pointer_fields),'zeroed_packet_padding_entries':padding_entries,
     'memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope']}

    (out/fixture['memory']).write_bytes(memory)
    path=out/'wall-marks-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
    return fixture,path,oracle
