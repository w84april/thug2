"""Original mesh lifetime and terminal resource callbacks."""
import struct,json,itertools,subprocess
from collections import Counter
from specimen import ROOT
from script_heap_oracle import ScriptHeapOracle
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EAX,UC_X86_REG_EIP

def build_lifecycle(out):
    BASE,SIZE=0x1800000,0x40000
    CONTEXT,MANAGER,DEVICE,METHODS,MESH=BASE+0x20,BASE+0x100,BASE+0x400,BASE+0x500,BASE+0x1000
    LOG,HEAP,OBJECTS,COM_METHODS,INDICES,VERTICES,DATA,ILINKS,VLINKS,GROUP,SENTINELS,MATERIAL,NODE,ENTRY=[BASE+x for x in [0x4000,0x20000,0xa000,0xb000,0xc000,0xd000,0xe000,0xf000,0xf100,0x18000,0x18100,0x18200,0x18400,0x18500]]
    CALLBACK=0x3f00100
    memory=bytearray(b'\xad'*SIZE)
    def put(at,fmt,*v):struct.pack_into(fmt,memory,at-BASE,*v)
    def patch(at,fmt,*v):return [at,struct.pack(fmt,*v).hex()]
    def obj(i):return OBJECTS+i*16
    def ib(i):return INDICES+i*32
    def vb(i):return VERTICES+i*64
    put(CONTEXT,'<8I',HEAP,BASE+SIZE,0,LOG,BASE,BASE+SIZE,0,0);put(MANAGER+0x124,'<I',MANAGER+0x200)
    put(DEVICE,'<I',METHODS);put(METHODS+0x194,'<I',CALLBACK);put(METHODS+0x190,'<I',CALLBACK+16)
    put(COM_METHODS+8,'<I',CALLBACK+32)
    for i in range(17):put(obj(i),'<I',COM_METHODS)
    memory[MESH-BASE:MESH-BASE+0xd8]=bytes(0xd8);put(MESH+0x1a,'<B',3)
    for i in range(8):
     put(MESH+0x54+i*4,'<I',ib(i));put(ib(i),'<6I',100+i,200+i,300+i,obj(i),DATA+i*32,600+i)
     put(ILINKS+i*16,'<3I',ib(i),ILINKS+(i-1)*16 if i else 0,ILINKS+(i+1)*16 if i<7 else 0)
    for i in range(7):
     offset=(0xcc+i*4) if i<3 else (0xbc+(i-3)*4) if i<6 else 0xc8
     put(MESH+offset,'<I',vb(i));put(vb(i),'<9I',100+i,200+i,obj(8+i),DATA+0x200+i*32,400+i,500+i,600+i,700+i,800+i)
     put(VLINKS+i*16,'<3I',vb(i),VLINKS+(i-1)*16 if i else 0,VLINKS+(i+1)*16 if i<6 else 0)
    for i,offset in enumerate([0x90,0x8c,0x48,0x4c,0x94,0xb8,0xb0]):put(MESH+offset,'<I',DATA+0x400+i*32)
    put(MESH+0x14,'<I',MATERIAL)
    put(GROUP,'<5I',0,MATERIAL,*[SENTINELS+i*20 for i in range(3)])
    for i in range(3):
     p=SENTINELS+i*20;put(p,'<5I',0x64a898,0xffffffff,0,p,p)
    put(SENTINELS+12,'<2I',NODE,NODE);put(NODE,'<5I',0x64a894,ENTRY,0,SENTINELS,SENTINELS);put(ENTRY,'<2I',0,MESH)
    globals_=[['NEXT_vertex_list',0x7865e4,4],['NEXT_index_list',0x7865e8,4]]
    functions={'0x4d69e0':{'name':'NEXT_mesh_destroy','this':True,'result':'void','cleanup':0,'memory':False},
     '0x4d3be0':{'name':'NEXT_unregister_vertex','this':True,'result':'void','cleanup':0,'memory':False}}
    CONTROL,TABLE=BASE+0x800,BASE+0x19000
    put(CONTROL,'<8I',0,0,0,0,0,MESH,0,0)
    put(DEVICE+4,'<I',CONTROL)
    for i in range(17):put(obj(i)+4,'<I',CONTROL)
    put(TABLE,'<2I',0,GROUP)
    functions['0x4d69e0'].update(name='thug_mesh_destroy',memory=True)
    functions['0x4d3be0']['name']='thug_mesh_unregister_vertex'
    globals_=[['thug_mesh_vertex_registry',0x7865e4,4],['thug_mesh_index_registry',0x7865e8,4],
     ['thug_mesh_device',0x7d69e0,4],['thug_mesh_material_table',0x775b80,4,0],['thug_mesh_material_table',0x775b84,4,4]]
    defaults=[VLINKS,ILINKS,DEVICE,0,GROUP]
    exports=[[0x64a894,'thug_material_node_methods'],[0x64a898,'thug_material_sentinel_methods']]
    pointer_fields={at for at in range(BASE,BASE+SIZE,4) if int.from_bytes(memory[at-BASE:at-BASE+4],'little') in dict(exports)}
    ADAPTER=BASE+0x50;put(ADAPTER,'<4I',CONTEXT,0,0,0)
    oracle=ScriptHeapOracle(memory,BASE,CONTEXT,MANAGER,globals_,defaults,functions,
     observe=[0x4d69e0,0x4d3be0,0x4ce9f0,0x4ce250,0x4ce960,0x4ce9a0,0x4ce9d0,0x6242a0])
    counts=Counter()
    def external(cpu,at,size,user):
     sp=cpu.reg_read(UC_X86_REG_ESP);arg=oracle.word(sp+4);cleanup=0;result=0x80004005
     b=c=d=0
     if at==CALLBACK:
      args=list(struct.unpack('<5I',cpu.mem_read(sp+4,20)));assert args[:2]==[DEVICE,0]
      for ptr,value in zip(args[2:],[oracle.word(CONTROL+4),7,16]):oracle.setword(ptr,value)
      kind=0;c=oracle.word(CONTROL+4);cleanup=20
     elif at==CALLBACK+16:
      args=list(struct.unpack('<5I',cpu.mem_read(sp+4,20)));assert args==[DEVICE,0,0,0,0]
      kind=1;cleanup=20
     elif at==CALLBACK+32:kind=2;cleanup=4;result=17
     else:kind=3;result=0
     n=oracle.word(CONTROL);oracle.setword(CONTROL,n+1)
     snap=list(struct.unpack('<4I',cpu.mem_read(arg,16))) if kind==3 and BASE<=arg<BASE+SIZE-16 else [0]*4
     cpu.mem_write(CONTROL+0x1800+n*48,struct.pack('<12I',kind,arg,b,c,d,oracle.word(MESH),oracle.word(MESH+0xbc),oracle.word(MESH+0xcc),*snap))
     if kind==3 and arg==oracle.word(CONTROL+8) and arg:
      oracle.setword(oracle.word(CONTROL+12),oracle.word(CONTROL+16));oracle.setword(CONTROL+8,0)
     counts[str(kind)]+=1
     cpu.reg_write(UC_X86_REG_EAX,result);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4+cleanup)
    for at in [CALLBACK,CALLBACK+16,CALLBACK+32,0x62411b]:oracle.cpu.hook_add(UC_HOOK_CODE,external,begin=at,end=at)
    labels=[]
    def case(label,p=(),changes=None,fn=0x4d69e0,this=MESH,stream=0,mutation=None,registered=False):
     changes={**(changes or {}),3:int(registered)}
     patches=[*p,patch(CONTROL+4,'<I',stream),patch(TABLE,'<I',int(registered))]
     if mutation:patches.append(patch(CONTROL+8,'<3I',*mutation))
     stages=oracle.case([(fn,this,[])],patches,changes);labels.append(label)
     for s in stages:
      # Explicit relocation of the original embedded table to host-owned storage.
      # The real original instructions still address775b80, never a game stub.
      s['outputs'].append(patch(TABLE,'<2I',*s['globals'][3:5]))
      s['callbacks']=oracle.word(CONTROL)
      for at,data in s['outputs']:
       if int.from_bytes(bytes.fromhex(data),'little') in dict(exports):pointer_fields.add(at)
    for count,shared in itertools.product(range(4),[False,True]):
     case('owned/shared '+str((count,shared)),[patch(MESH,'<I',int(shared)),patch(MESH+0x1a,'<B',count)])
    for bound in [0,obj(0),obj(8),obj(10),obj(11),obj(13),obj(14),obj(16)]:case('bound '+hex(bound),stream=bound)
    case('restore index device',mutation=(ILINKS,ib(0)+12,obj(15)))
    case('restore vertex device',mutation=(VLINKS,vb(0)+8,obj(15)))
    case('change next slot count',mutation=(VLINKS,MESH+0x18,0x00010000))
    case('registered owned',[patch(MESH,'<I',0x10)],registered=True)
    case('registered shared',[patch(MESH,'<I',0x11)],registered=True)
    case('empty references',[[MESH,bytes(0xd8).hex()]])
    for head,target in [(0,vb(0)),(VLINKS,vb(0)),(VLINKS,vb(3)),(VLINKS,vb(6)),(VLINKS,vb(16))]:
     case('unregister '+str((head,target)),changes={0:head},fn=0x4d3be0,this=target)
    # Missing owned slots and CPU storage are independent of registry membership.
    for i in range(8):case('missing index slot '+str(i),[patch(MESH+0x54+i*4,'<I',0)])
    for i in range(7):
     offset=0xcc+i*4 if i<3 else 0xbc+(i-3)*4 if i<6 else 0xc8
     case('missing vertex slot '+str(i),[patch(MESH+offset,'<I',0)])
    case('index wrappers without CPU storage',[patch(ib(i)+16,'<I',0) for i in range(8)])
    case('vertex wrappers without CPU storage',[patch(vb(i)+12,'<I',0) for i in range(7)])
    case('wrappers absent from registries',changes={0:0,1:0})
    case('first duplicate registration',[patch(VLINKS+3*16,'<I',vb(0))],fn=0x4d3be0,this=vb(0))
    case('CRT free changes later outer cleanup',mutation=(DATA+0x400+5*32,MESH+0xb0,0))
    sdk=ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang'
    subprocess.run([str(sdk),'--target=wasm32-unknown-unknown','-O2','-nostdlib',
     '-Wl,--no-entry,--import-memory,--export=fixture_mesh_get,--export=fixture_mesh_set,--export=fixture_mesh_release,--export=fixture_mesh_crt_free',
     str(ROOT/'tools/mesh_lifecycle_callbacks.c'),'-o',str(out/'mesh-lifecycle-callbacks.wasm')],check=True)
    callbacks=[{'module':'mesh-lifecycle-callbacks.wasm','export':name,'slots':[slot]} for name,slot in [
     ('fixture_mesh_get',METHODS+0x194),('fixture_mesh_set',METHODS+0x190),('fixture_mesh_release',COM_METHODS+8)]]
    callbacks.append({'module':'mesh-lifecycle-callbacks.wasm','export':'fixture_mesh_crt_free','original':0x62411b})
    fixture={'base':BASE,'memory':'mesh-lifecycle-memory.bin','globals':globals_,'functions':functions,'float_fields':[],
     'cases':oracle.cases,'case_labels':labels,'scope':'Complete mesh destruction and vertex-buffer unregister, preserving material-table disposal, owned/shared resources, two buffer registries, stream binding, exact release order, wrapper zeroing and external callback mutations. Embedded material table is explicitly relocated to host-owned storage; CRT heap and terminal GPU methods are host boundaries. GetStreamSource supplies all outputs, resource counts/storage remain valid internal contracts.',
     'native_callbacks':callbacks,'callback_counter':'external_callbacks','pointer_exports':exports,'pointer_fields':sorted(pointer_fields),
     'pointer_initializers':[['thug_mesh_material_table',TABLE],['thug_mesh_crt_heap',CONTROL],['thug_mesh_crt_heap',0x62411b,4]],
     'indirect_globals':['thug_mesh_material_table'],'memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm',
     'memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope']}
    
    (out/fixture['memory']).write_bytes(memory)
    path=out/'mesh-lifecycle-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
    print('Original mesh lifecycle:',len(labels),sum(oracle.counts.values()),dict(counts),flush=True)
    return fixture,path,oracle,dict(counts)
