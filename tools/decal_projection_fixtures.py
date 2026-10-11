"""Compare the complete surface-mark projection against the pinned PC body."""
import struct,json,subprocess,random,math
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EAX,UC_X86_REG_EIP,UC_X86_REG_FPSW,UC_X86_REG_FPTAG,UC_X86_REG_MXCSR
from script_heap_oracle import ScriptHeapOracle
from specimen import ROOT

def build_projection(out):
    BASE,SIZE=0x1800000,0x100000
    CONTEXT,MANAGER,DEVICE,METHODS,GPU=BASE+0x20,BASE+0x100,BASE+0x400,BASE+0x500,BASE+0x800
    LIST,GEOMETRY,CONTAINER,MESHES,MESH,VB,IB,VERTICES,INDICES,PROJECTION,TEXTURE,PREVIOUS=[BASE+x for x in [0x1000,0x1100,0x1200,0x1300,0x1400,0x1500,0x1600,0x1700,0x1800,0x1900,0x1a00,0x1b00]]
    TABLE,BUCKETS,LOG,HEAP=BASE+0x2000,BASE+0x2100,BASE+0x4000,BASE+0x20000
    TLS=0x7d2100;GET=0x3f00100
    memory=bytearray(b'\xad'*SIZE)
    def put(at,fmt,*v):struct.pack_into(fmt,memory,at-BASE,*v)
    def patch(at,fmt,*v):return [at,struct.pack(fmt,*v).hex()]
    def bits(f):return int.from_bytes(struct.pack('<f',f),'little')
    put(CONTEXT,'<8I',HEAP,BASE+SIZE,0,LOG,BASE,BASE+SIZE,0,0);put(MANAGER+0x124,'<I',MANAGER+0x200)
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
    functions={'0x4b9c30':{'name':'thug_decal_project','this':False,'result':'word','cleanup':0,'memory':True}}
    observed=[0x4b9c30,0x4b9a60,0x4d69e0,0x4d4be0,0x4b8220,0x490d50,0x490d80,0x4b88d0,0x4b7f30,0x5e17ed,0x5e16ea,0x5c0985,0x5c0b39,0x5df4ac,0x623ba3,0x6236fc]
    oracle=ScriptHeapOracle(memory,BASE,CONTEXT,MANAGER,globals_,defaults,functions,observe=observed,instruction_limit=20000000)
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
    labels=[]
    def run(label,p=(),changes=None,repeats=1):
     cpu=oracle.cpu
     cpu.reg_write(UC_X86_REG_FPSW,0);cpu.reg_write(UC_X86_REG_FPTAG,0xffff);cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
     steps=oracle.case([(0x4b9c30,0,[LIST,0,PROJECTION])]*repeats,p,changes);labels.append(label)
     expected=bytearray(memory)
     for at,data in p:expected[at-BASE:at-BASE+len(data)//2]=bytes.fromhex(data)
     def nanword(v):return v&0x7f800000==0x7f800000 and v&0x7fffff!=0
     for step in steps:
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
      merged=[]
      for at,data in step['outputs']:
       if merged and merged[-1][0]+len(merged[-1][1])//2==at:merged[-1][1]+=data
       else:merged.append([at,data])
      step['outputs']=merged
     print('Projection original',len(labels),label,flush=True)
     return steps
    run('inside face')
    run('empty geometry list',[patch(LIST,'<I',0)])
    run('missing geometry mesh',[patch(GEOMETRY+0x14,'<I',0)])
    run('empty mesh container',[patch(CONTAINER+0x40,'<I',0)])
    run('disabled mesh',[patch(MESH,'<I',2)])
    run('short strip',[patch(MESH+0x24,'<H',2)])
    run('repeated index',[patch(INDICES,'<3H',0,0,2)])
    run('two triangle strip',[patch(MESH+0x24,'<H',4)])
    run('zero lifetime',[patch(PROJECTION+0x30,'<f',0)])
    run('negative lifetime',[patch(PROJECTION+0x30,'<f',-1)])
    run('zero angle strict rejection',[patch(PROJECTION+0x2c,'<f',0)])
    run('previous point ribbon',[patch(PROJECTION+0x3c,'<I',PREVIOUS)])
    run('outside square',[patch(VERTICES,'<3f',10,10,0),patch(VERTICES+16,'<3f',11,10,0),patch(VERTICES+32,'<3f',10,11,0)])
    run('indirect texture',[patch(TEXTURE+8,'<I',1),patch(TEXTURE+0x10,'<I',TEXTURE+0x20),patch(TEXTURE+0x20,'<I',0x12345678)])
    vertical=[patch(PROJECTION,'<8f',0,10,0,1,0,-10,0,1),patch(VERTICES,'<3f',-1,0,-1),patch(VERTICES+16,'<3f',1,0,-1),patch(VERTICES+32,'<3f',0,0,1)]
    run('vertical projection random rotation',vertical)
    run('vertical projection specified rotation',vertical+[patch(PROJECTION+0x28,'<f',.25)])
    # Exercise whole sequences: buffer reuse and age-based replacement after
    # all 256 records have become occupied, preserving retained scratch storage.
    run('repeated projection through slot exhaustion',repeats=18)
    run('mutating previous-point descriptor reused', [patch(PROJECTION+0x3c,'<I',PREVIOUS)],repeats=3)
    for value in [-100000,.0001,.001,.99999,1.234567,2147483.75,4294968,1e20]:
        run('lifetime conversion '+str(value),[patch(PROJECTION+0x30,'<f',value)])
    for angle in [0.000001,.5,1.57079637,3.14159274,-1,20]:
        run('angle gate '+str(angle),[patch(PROJECTION+0x2c,'<f',angle)])
    for z in [-100,-20,-10,-9.9999,0,9.9,10,20,100]:
        run('depth rejection '+str(z),[patch(VERTICES+i*16+8,'<f',z) for i in range(3)])
    for width in [.01,.5,1,2,2.0000002,8,1000]:
        run('projection extent '+str(width),[patch(PROJECTION+0x20,'<2f',width,17)])
    for order in [(0,2,1),(2,1,0),(1,2,0),(0,1,1,2,3),(0,1,2,2,3,0)]:
        run('strip order and degenerates '+str(order),[patch(INDICES,'<'+'H'*len(order),*order),patch(MESH+0x24,'<H',len(order))])
    run('two geometry entries reuse buffer',[patch(LIST,'<3I',GEOMETRY,GEOMETRY,0)])
    run('two mesh entries reuse buffer',[patch(CONTAINER+0x40,'<I',2),patch(MESHES,'<2I',MESH,MESH)])
    for stride,color_offset in [(17,13),(24,16),(32,28)]:
        p=[patch(MESH+0x18,'<B',stride),patch(MESH+0x1c,'<B',color_offset)]
        for i,xyz in enumerate([(-1,-1,0),(1,-1,0),(0,1,0)]):
            p += [patch(VERTICES+i*stride,'<3f',*xyz),patch(VERTICES+i*stride+color_offset,'<I',0xff804021+i*0x111111)]
        run('vertex stride and color offset '+str((stride,color_offset)),p)
    old_buffer,material=BASE+0x8000,BASE+0x3000
    for mode in range(5):
        remaining=[0 if mode==0 else (0xffffffff if mode==1 else i+1) for i in range(256)]
        initial=[(x+(i%7)*100)&0xffffffff for i,x in enumerate(remaining)]
        if mode==3:remaining[255]=0
        if mode==4:remaining=[0x80000000+i for i in range(256)]
        p=[patch(BUCKETS,'<3I',0,old_buffer,0),patch(old_buffer,'<512I',*remaining,*initial),
           patch(old_buffer+0x1c0c,'<I',material),patch(material+0x30,'<I',0x12345678)]
        run('preexisting texture buffer slots '+str(mode),p,repeats=2)
    rng=random.Random(0x4b9c30)
    for i in range(96):
        # Arbitrary finite triangles and rays cover non-axis-aligned view frames.
        points=[[rng.uniform(-8,8) for _ in range(3)] for _ in range(3)]
        center=[sum(p[k] for p in points)/3 for k in range(3)]
        direction=[rng.uniform(-1,1) for _ in range(3)]
        d=math.sqrt(sum(x*x for x in direction));direction=[x/d for x in direction]
        endpoints=[[center[k]+sign*direction[k]*20 for k in range(3)] for sign in [1,-1]]
        p=[patch(VERTICES+j*16,'<3f',*points[j]) for j in range(3)]
        p += [patch(PROJECTION,'<8f',*endpoints[0],1,*endpoints[1],1),
              patch(PROJECTION+0x20,'<5f',rng.uniform(.5,30),rng.uniform(.5,20),rng.uniform(-6,6),rng.uniform(.1,3),rng.uniform(-2,30))]
        if i%4==0:p += [patch(PROJECTION+0x3c,'<I',PREVIOUS),patch(PREVIOUS,'<4f',*[endpoints[0][k]-rng.uniform(-8,8) for k in range(3)],1)]
        run('seeded arbitrary triangle/ray '+str(i),p,changes={1:rng.getrandbits(32)})
    # Use installed training collision faces as real geometry, repacked into
    # CPU-backed render strips. This validates the projection body, not a
    # recovered rendering asset loader or a claim these are original draw meshes.
    geometry=json.loads((out/'geometry-fixtures.json').read_text())
    data=(out/'training-relocated.bin').read_bytes();vertices=(out/'vertices.bin').read_bytes();normals=(out/'normals.bin').read_bytes()
    selected=[o for o in geometry['objects'] if o['faces']]
    for sample,obj in enumerate(selected[::max(1,len(selected)//128)]):
        face=(sample*13)%obj['faces'];offset=obj['object'];small=data[offset+10]
        start=struct.unpack_from('<I',data,offset+12)[0]-geometry['data']
        indices=struct.unpack_from('<3B' if small else '<3H',data,start+face*(8 if small else 10)+4)
        points=[struct.unpack_from('<3f',vertices,obj['vertex_start']+index*16) for index in indices]
        normal=struct.unpack_from('<3f',normals,obj['normal_start']+face*16)
        if not all(math.isfinite(x) for x in normal) or sum(x*x for x in normal)<.5:continue
        center=[sum(p[k] for p in points)/3 for k in range(3)]
        endpoints=[[center[k]+sign*normal[k]*32 for k in range(3)] for sign in [1,-1]]
        radius=max(math.sqrt(sum((p[k]-center[k])**2 for k in range(3))) for p in points)
        p=[patch(VERTICES+j*16,'<3f',*points[j]) for j in range(3)]
        p += [patch(PROJECTION,'<8f',*endpoints[0],1,*endpoints[1],1),patch(PROJECTION+0x20,'<f',max(1,radius*2))]
        run('installed training object '+str(offset)+' face '+str(face),p)
    sdk=ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang'
    subprocess.run([str(sdk),'--target=wasm32-unknown-unknown','-O2','-nostdlib',
     '-Wl,--no-entry,--import-memory,--export=fixture_projection_get,--export=fixture_projection_crt_free',
     str(ROOT/'tools/decal_projection_callbacks.c'),'-o',str(out/'decal-projection-callbacks.wasm')],check=True)
    fixture={'base':BASE,'memory':'decal-projection-memory.bin','globals':globals_,'functions':functions,'float_fields':[],
     'cases':oracle.cases,'case_labels':labels,'scope':'Complete original decal projection through original math, strip traversal, texture buffer lookup/allocation, subdivision, timers/colors and temporary mesh destruction. All arena/global bytes and heap callback snapshots compared; only typed computed NaNs compare by classification. Initialized successful heap, CRT TLS/free and terminal GPU GetStreamSource are explicit host boundaries; CPU-backed valid mesh buffers and selected SSE math dispatch are the internal contract.',
     'native_callbacks':[{'module':'decal-projection-callbacks.wasm','export':'fixture_projection_get','slots':[METHODS+0x194]},
     {'module':'decal-projection-callbacks.wasm','export':'fixture_projection_crt_free','original':0x62411b}],
     'pointer_initializers':[['thug_mesh_crt_heap',CONTEXT],['thug_mesh_crt_heap',0x62411b,4]],
     'memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope']}
    (out/fixture['memory']).write_bytes(memory)
    path=out/'decal-projection-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
    return fixture,path,oracle
