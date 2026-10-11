"""Compare the complete wall-contact caller through collision, projection and network callees."""
import struct,json,subprocess,random,math,hashlib
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EAX,UC_X86_REG_EIP,UC_X86_REG_FPSW,UC_X86_REG_FPTAG,UC_X86_REG_MXCSR
from script_heap_oracle import ScriptHeapOracle
from specimen import ROOT

def build_wall_contact(out):
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

    EFFECT,CONTACT_BODY,CONTACT_COMPONENT,CONTACT_DIRECTION,QUERY,MOVING_NODES,PRINT,CONTACT_VERTICES,CONTACT_FACES=[BASE+x for x in [0xd0000,0xd0100,0xd0300,0xd0400,0xd0500,0xd0600,0xd0700,0xd0800,0xd0900]]
    put(EFFECT+12,'<I',EMITTER_OWNER);put(EFFECT+0x18,'<If',0,0);put(EFFECT+0x20,'<f',0)
    put(EFFECT+0x24,'<I',CONTACT_DIRECTION);put(EFFECT+0x2c,'<I',CONTACT_COMPONENT);put(EFFECT+0x34,'<I',EMITTER)
    put(CONTACT_COMPONENT+12,'<I',CONTACT_BODY)
    put(CONTACT_BODY+0xac,'<4f',0,0,-1,0);put(CONTACT_BODY+0x7c,'<4f',0,0,1,0)
    put(CONTACT_DIRECTION+0x48,'<4f',0,12,-1,0);put(EMITTER_OWNER+0x4c,'<4f',0,-50,10,1)
    put(QUERY,'<3I',0x12345678,0xabcdef01,0x98765432)
    put(MOVING_NODES,'<4I',0,0xffffffff,0,MOVING_NODES)
    put(PRINT,'<2I',CONTEXT,0)
    put(COLLISION,'<IHHHBBI',0x101,0,3,1,1,0,CONTACT_FACES)
    put(COLLISION+0x30,'<3If',CONTACT_VERTICES,0,CONTACT_VERTICES+64,0)
    put(CONTACT_FACES,'<HH4B',0,3,0,1,2,255)
    for i,xyz in enumerate([(-1,-1,0),(1,-1,0),(0,1,0)]):put(CONTACT_VERTICES+i*12,'<3f',*xyz)
    put(SYMBOLS+(0x6775e538&0xfff)*4,'<I',SYMBOL+64);put(SYMBOL+64,'<5I',0xa00,0x6775e538,0,SYMBOL+96,0)
    put(SYMBOL+96,'<2I',0,SYMBOL+112)
    put(SYMBOL+112,'<4I',2,0xe7ab5365,bits(30),SYMBOL+128);put(SYMBOL+128,'<4I',2,0x7b5e76c4,bits(30),0)
    for name,at,value,width in [('thug_moving_collision_list',0x691984,MOVING_NODES,4),('thug_collision_default_cache',0x691974,0,4),('thug_collision_select_farthest',0x691910,0,1)]:
        globals_.append([name,at,width]);defaults.append(value)
    for i in range(1024):
        globals_.append(['thug_collision_fallback_indices',0x67c6b8+i*4,4,i*4]);defaults.append(i*2|((i*2+1)<<16))
    # Relocate the saved full training geometry by documented header/BSP fields.
    from collision_file import layout
    raw=(out/'training.bin').read_bytes();sections=layout(raw);TRAIN_DATA=BASE+0x100000;delta=TRAIN_DATA-0x1000000
    loaded=bytearray(training[:len(raw)])
    for offset in sections['objects']:
        for field in [12,0x30,0x34,0x38]:
            pointer=struct.unpack_from('<I',loaded,offset+field)[0]
            assert 0x1000000<=pointer<0x1000000+len(raw),(hex(offset),hex(field),hex(pointer))
            struct.pack_into('<I',loaded,offset+field,pointer+delta)
    for offset in range(sections['nodes'],sections['face_list'],8):
        pointer=struct.unpack_from('<I',loaded,offset+4)[0]
        assert 0x1000000<=pointer<0x1000000+len(raw)
        struct.pack_into('<I',loaded,offset+4,pointer+delta)
    memory[TRAIN_DATA-BASE:TRAIN_DATA-BASE+len(loaded)]=loaded
    for i in range(605):
        for field in [12,16]:
            pointer=struct.unpack_from('<I',training,0x100000+i*24+field)[0]
            if pointer:
                assert 0x1000000<=pointer<0x1000000+len(raw),(i,field,hex(pointer))
                put(TRAIN_INST+i*24+field,'<I',pointer+delta)
    MOVING,MOVING_OWNER,MOVING_REF,MOVING_POSITION,MOVING_MATRIX=[BASE+x for x in [0xd1000,0xd1200,0xd1300,0xd1400,0xd1500]]
    put(MOVING_OWNER+4,'<I',0);put(MOVING_OWNER+0x14,'<I',0xabcdef01)
    put(MOVING_REF,'<3I',MOVING_OWNER,0,0)
    put(MOVING_POSITION,'<4f',0,0,2,1)
    put(MOVING_MATRIX,'<16f',*[1 if i%5==0 else 0 for i in range(16)])
    exports.append([0x645ce0,'thug_moving_collision_methods'])
    for at,name,result in [(0x413000,'thug_moving_collision_initialize','word'),(0x412f90,'thug_moving_collision_set_position','void'),(0x412070,'thug_moving_collision_set_orientation','word'),(0x40ae40,'thug_moving_collision_set_owner','void')]:
        functions[hex(at)]={'name':name,'this':True,'result':result,'cleanup':4,'memory':False,'stack_args':[0]}
    functions['0x51ddf0']={'name':'thug_wall_contact_mark','this':True,'result':'byte','cleanup':12,'memory':True,'stack_args':[0,1,2]}
    observed.extend([0x51ddf0,0x417760,0x4170f0,0x4172f0,0x410580,0x4117a0,0x413b50,0x414460,0x416320,0x528560,0x4637e0,0x4637c0])
    exports.extend([[0x64c3c8,'thug_wall_contact_missing'],[0x64c3e8,'thug_wall_contact_emitting']])
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

    def contact_boundary(cpu,at,size,user):
        sp=cpu.reg_read(UC_X86_REG_ESP)
        if at==0x51ddf0:cpu.mem_write(0x691968,bytes(cpu.mem_read(QUERY,12)))
        elif at==0x51e270:cpu.mem_write(QUERY,bytes(cpu.mem_read(0x691968,12)))
        else:
            fmt=oracle.word(sp+4);assert fmt in [0x64c3c8,0x64c3e8],hex(fmt)
            oracle.record(4,fmt,0,0)
            cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
    for at in [0x51ddf0,0x51e270,0x401c30]:oracle.cpu.hook_add(UC_HOOK_CODE,contact_boundary,begin=at,end=at)
    from collections import Counter
    branches=Counter()
    branch_names={0x51de1f:'positive_cooldown',0x51de8f:'body_direction',0x51deb5:'component_direction',0x51ded8:'alternate_direction',
        0x51df4c:'height_50',0x51df54:'height_20',0x51df5c:'height_30',0x51e043:'contact_hit',0x51e228:'contact_miss',
        0x51e132:'arm_mark',0x51e142:'emit_unarmed',0x51e1a7:'emit_armed',0x51e21f:'unlink_after_hit'}
    def branch_observe(cpu,at,size,user):branches[branch_names[at]]+=1
    for at in branch_names:oracle.cpu.hook_add(UC_HOOK_CODE,branch_observe,begin=at,end=at)

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

    def contact(label,kind=0,dir=0,height=0,p=(),repeats=1,before=()):
        cpu=oracle.cpu;cpu.reg_write(UC_X86_REG_FPSW,0);cpu.reg_write(UC_X86_REG_FPTAG,0xffff);cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
        steps=oracle.case(list(before)+[(0x51ddf0,EFFECT,[kind,dir,height,QUERY,PRINT])]*repeats,p);labels.append(label);annotate(steps,p)
        for step in steps:
            for at,data in step['outputs']:
                if int.from_bytes(bytes.fromhex(data),'little') in dict(exports):pointer_fields.add(at)
        print('Wall contact original',len(labels),label,[step['result'] for step in steps],flush=True)
    for cooldown in [0,.1,1,1.1,2,-1,float('nan'),float('inf')]:
        contact('cooldown '+str(cooldown),p=[patch(EFFECT+0x20,'<f',cooldown)],repeats=2)
    for inhibit in [-0x80000000,-1,0,1,10,0x7fffffff]:
        contact('inhibit '+str(inhibit),p=[patch(EFFECT+0x18,'<i',inhibit)])
    for kind in [0,1,255,256,257]:
        for direction in [0,1,256,257]:
            for height in [0,1]:
                y=-30 if kind&255 else -20 if height else -50
                contact('kind/direction/height '+str((kind,direction,height)),kind,direction,height,
                    p=[patch(EMITTER_OWNER+0x4c,'<4f',0,y,10,1)])
    for armed in [0,1,2,255]:
        contact('armed hit '+str(armed),p=[patch(EFFECT+0x1c,'<B',armed)],repeats=2)
    contact('no scene',p=[patch(NODES+4,'<I',0xffffffff)])
    contact('miss above face',p=[patch(EMITTER_OWNER+0x50,'<f',100)])
    contact('excluded face',p=[patch(CONTACT_FACES,'<H',0x1000)])
    contact('disabled instance',p=[patch(INSTANCE+8,'<H',2)])
    moving_setup=[(0x413000,MOVING,[COLLISION]),(0x412f90,MOVING,[MOVING_POSITION]),(0x412070,MOVING,[MOVING_MATRIX]),(0x40ae40,MOVING,[MOVING_OWNER])]
    for z in [-2,0,2,100]:
        for mode in [0,1,2]:
            for linked in [False,True]:
                p=[patch(MOVING_NODES,'<4I',0,MOVING,0,MOVING_NODES+16),patch(MOVING_NODES+16,'<4I',0,0xffffffff,0,MOVING_NODES+16),
                    patch(MOVING_POSITION,'<4f',0,0,z,1)]
                if mode==1:p.append(patch(INSTANCE+8,'<H',2))
                if mode==2:
                    a=.1;c=math.cos(a);t=math.sin(a)
                    p.append(patch(MOVING_MATRIX,'<16f',1,0,0,0,0,c,t,0,0,-t,c,0,0,0,0,1))
                if linked:p.append(patch(MOVING_OWNER+4,'<I',MOVING_REF))
                contact('moving position/mode/linked '+str((z,mode,linked)),p=p,before=moving_setup,repeats=2)

    # Slanted synthetic walls isolate all normal components and nonzero W lanes.
    rng=random.Random(0x51ddf0)
    for sample in range(48):
        tilt_x=rng.uniform(-1,1);tilt_y=rng.uniform(-1,1)
        points=[(-40,-40,-40*tilt_x-40*tilt_y),(40,-40,40*tilt_x-40*tilt_y),(0,40,40*tilt_y)]
        center=[0,-40/3,-40*tilt_y/3]
        direction=[rng.uniform(-.5,.5),rng.uniform(-50,50),-rng.uniform(.1,10),[0,1,-1,10][sample%4]]
        norm=math.hypot(direction[0],direction[2])
        origin=[center[0]-direction[0]/norm*5,center[1],center[2]-direction[2]/norm*5]
        kind=sample%2;origin[1]-=30 if kind else 50
        p=[patch(EFFECT+0x1c,'<B',sample%3),patch(EMITTER_OWNER+0x4c,'<4f',*origin,[0,1,-1,2][sample%4]),
            patch(CONTACT_BODY+0xac,'<4f',*direction),patch(CONTACT_DIRECTION+0x48,'<4f',*direction),
            patch(CONTACT_BODY+0x7c,'<4f',-direction[0],direction[1],-direction[2],direction[3]),
            patch(COLLISION+0x10,'<8f',*[min(v[k] for v in points) for k in range(3)],1,*[max(v[k] for v in points) for k in range(3)],1)]
        for j in range(3):p += [patch(CONTACT_VERTICES+j*12,'<3f',*points[j]),patch(VERTICES+j*16,'<3f',*points[j])]
        contact('slanted wall direction and W '+str(sample),kind,(sample//2)%2,p=p)
    contact('alternate hit arms then gates',1,p=[patch(EMITTER_OWNER+0x50,'<f',-30)],repeats=3)
    geometry=json.loads((out/'geometry-fixtures.json').read_text());vertices=(out/'vertices.bin').read_bytes();normals=(out/'normals.bin').read_bytes()
    by_offset={o['object']:o for o in geometry['objects']}
    for sample in range(0,605,12):
        offset=struct.unpack_from('<I',training,0x100000+sample*24+12)[0]-0x1000000;obj=by_offset[offset]
        if not obj['faces']:continue
        face=(sample*13)%obj['faces'];small=training[offset+10]
        face_start=struct.unpack_from('<I',training,offset+12)[0]-0x1000000
        indices=struct.unpack_from('<3B' if small else '<3H',training,face_start+face*(8 if small else 10)+4)
        points=[struct.unpack_from('<3f',vertices,obj['vertex_start']+index*16) for index in indices]
        normal=struct.unpack_from('<3f',normals,obj['normal_start']+face*16)
        length=math.hypot(normal[0],normal[2])
        if not math.isfinite(length) or length<.1:continue
        center=[sum(p[k] for p in points)/3 for k in range(3)]
        direction=[-normal[0]/length,0,-normal[2]/length,0]
        p=[patch(SCENE+0xd0,'<2I',TRAIN_TABLE,TRAIN_GRID),patch(TRAIN_RENDER+sample*32+20,'<I',CONTAINER)]
        p += [patch(VERTICES+j*16,'<3f',*points[j]) for j in range(3)]
        p += [patch(CONTACT_BODY+0xac,'<4f',*direction),patch(CONTACT_BODY+0x7c,'<4f',-direction[0],0,-direction[2],0)]
        for kind,armed in [(0,0),(1,0),(1,1)]:
            origin=[center[k]-direction[k]*5 for k in range(3)];origin[1]-=30 if kind else 50
            contact('training object '+str(sample)+' kind/armed '+str((kind,armed)),kind,
                p=p+[patch(EMITTER_OWNER+0x4c,'<4f',*origin,1),patch(EFFECT+0x1c,'<B',armed)])

    fixture={'base':BASE,'memory':'wall-contact-memory.bin','globals':globals_,'functions':functions,'float_fields':[],
     'cases':oracle.cases,'case_labels':labels,'scope':'Complete wall-contact caller through original collision, mark emission and network callees. Full relocated training geometry/BSP and all 605 grid objects, slanted walls, moving surfaces and existing reference chains. Every arena/global/result byte compares exactly with no numeric exceptions in this corpus; configured distances, initialized successful heap and selected math dispatch are internal contracts. Terminal diagnostics/GPU/CRT remain host boundaries. The emitter fixture seeds only the two originally unwritten packet padding bytes.',
     'native_callbacks':[{'module':'wall-contact-callbacks.wasm','export':'fixture_wall_contact_print','slots':[PRINT+4]},{'module':'decal-projection-callbacks.wasm','export':'fixture_projection_get','slots':[METHODS+0x194]},
     {'module':'decal-projection-callbacks.wasm','export':'fixture_projection_crt_free','original':0x62411b}],
     'pointer_initializers':[['thug_mesh_crt_heap',CONTEXT],['thug_mesh_crt_heap',0x62411b,4]],
     'pointer_symbols':[[0x64c3c8,'thug_wall_contact_missing','No contact found for sticker?\n'],[0x64c3e8,'thug_wall_contact_emitting','sticker.............................\n']],'pointer_exports':exports,'pointer_fields':sorted(pointer_fields),'zeroed_packet_padding_entries':padding_entries,
     'memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope']}

    sdk=ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang'
    subprocess.run([str(sdk),'--target=wasm32-unknown-unknown','-O2','-nostdlib',
        '-Wl,--no-entry,--import-memory,--export=fixture_wall_contact_print',
        str(ROOT/'tools/wall_contact_callbacks.c'),'-o',str(out/'wall-contact-callbacks.wasm')],check=True)
    assert all(branches[name]>0 for name in branch_names.values()),dict(branches)
    (out/fixture['memory']).write_bytes(memory)
    path=out/'wall-contact-fixtures.json'
    fixture['branch_counts']=dict(branches)
    path.write_text(json.dumps(fixture,separators=(',',':')))
    return fixture,path,oracle
