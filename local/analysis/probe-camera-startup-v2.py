"""Original camera storage/projection/synchronization; no pinned builders run."""
from pathlib import Path
source=Path('local/analysis/probe-skater-initialization-links-v1.py').read_text().split('types=[')[0]
exec(compile(source,'<preserved initialized startup oracle>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear();prefix_hits.clear()
specs=[(0x4a07b0,7,'thug_camera_get_default_fov_v2',0,'double',False,False,False),
 (0x4a07c0,7,'thug_camera_get_display_ratio_v2',0,'double',False,False,False),
 (0x485aa0,109,'thug_camera_projection_v2',0,'void',False,False,True),
 (0x485ba0,263,'thug_camera_object_construct_v2',0,'word',False,False,True),
 (0x4859f0,11,'thug_camera_object_destroy_v2',0,'void',True,True,True),
 (0x485a20,33,'thug_camera_object_delete_v2',1,'word',True,True,True),
 (0x41b730,134,'thug_camera_component_construct_v2',0,'word',True,False,True),
 (0x41b840,86,'thug_camera_component_create_v2',0,'word',True,False,False),
 (0x41b6d0,87,'thug_camera_component_destroy_v2',0,'void',True,True,True),
 (0x41b7c0,33,'thug_camera_component_delete_v2',1,'word',True,False,True),
 (0x41b8a0,100,'thug_camera_component_update_v2',0,'void',False,False,True),
 (0x41b810,35,'thug_camera_component_sync_v2',0,'void',False,False,True),
 (0x524c50,83,'thug_walk_camera_bind_owner_v2',1,'void',False,False,True)]
for row in specs:bind_new(*row)
exports.extend([[0x6487e0,'thug_camera_object_methods_v2'],[0x645e34,'thug_camera_component_methods_v2']])
for name,a,value,width in [('thug_camera_default_fov_v2',0x701348,bits(60),4),('thug_camera_display_ratio_v2',0x67e544,bits(4/3),4),('thug_camera_far_override_v2',0x7d643a,0,1),('thug_camera_far_frames_v2',0x7d6444,400,4)]:glob(name,a,value,width)
oracle.globals=globals_;oracle.defaults=defaults
initial=bytes(memory);oracle.initial=initial
for fov,ratio in itertools.product([15,35,45,60,90,110,140],[1,4/3,16/9]):
 g=FinalGraph();g.put(P+0xac,'<f',fov);g.put(P+0xc0,'<f',1)
 g.run([call(0x4a07b0),call(0x4a07c0),call(0x485aa0,P)],f'projection/{fov}/{ratio}',{0x701348:bits(fov),0x67e544:bits(ratio)})
for fill,alignment,override in itertools.product([0,0xa5,255],[0,1,4],[0,1,255]):
 g=FinalGraph(fill);fields.add(P+alignment)
 g.run([call(0x485ba0,P+alignment)]*2+[call(0x4859f0,P+alignment)],f'camera raw storage/destroy/{fill}/{alignment}/{override}',{0x7d643a:override,0x7d6444:0xffffffff if override==255 else 400})
for flags in [0,1,2,255,256,257,0xffffffff]:
 g=FinalGraph();g.run([call(0x485ba0,P),call(0x485a20,P,[flags])],f'camera deleting flags/{flags}')
 g=FinalGraph();g.run([call(0x41b840),call(0x41b7c0,HEAP,[flags])],f'component factory/deleting flags/{flags}')
for fill,alignment in itertools.product([0,0xa5,255],[0,1,4]):
 g=FinalGraph(fill);fields.add(P+alignment);g.run([call(0x41b730,P+alignment),call(0x41b6d0,P+alignment)],f'component raw ctor/destroy/{fill}/{alignment}')
g=FinalGraph();g.put(CONTEXT+32,'<I',1);g.run([call(0x41b840)],'component allocation failure')
g=FinalGraph();g.put(CONTEXT+32,'<I',1);g.run([call(0x41b730,P),call(0x41b6d0,P)],'camera payload allocation failure')
for shape,pattern in itertools.product(['distinct','camera overlaps owner'],[0,1,2]):
 g=FinalGraph();camera=OBJ if shape!='distinct' else g.alloc(0xc4)
 g.put(P+12,'<I',OBJ);g.put(P+0x18,'<I',camera)
 position=[0x80000000,0x7fc12345,0x3f800000,0x7f800000] if pattern==1 else [0xdeadbeef,0x00000001,0x80800000,0x3f000000] if pattern==2 else [bits(10),bits(20),bits(30),bits(1)]
 matrix=[0x3f000000+i*0x10000 for i in range(16)] if pattern!=1 else [0x7fc00000+i for i in range(16)]
 g.put(OBJ+0x4c,'<4I',*position);g.put(OBJ+0x6c,'<16I',*matrix)
 g.run([call(0x41b8a0,P),call(0x41b810,P)]*2,f'camera raw owner snapshot/sync/{shape}/{pattern}')
for fill,shape in itertools.product([0,0xa5,255],['empty','all','reversed','walk','trick','duplicates']):
 g=FinalGraph(fill);ts=[] if shape=='empty' else [0xd9151d4d,0x726e85aa] if shape=='reversed' else [0x726e85aa] if shape=='walk' else [0xd9151d4d] if shape=='trick' else [0x726e85aa,0xd9151d4d]*(2 if shape=='duplicates' else 1)
 nodes=[g.component(t) for t in ts]
 for i,c in enumerate(nodes):g.put(c+16,'<I',nodes[i+1] if i+1<len(nodes) else 0)
 g.put(OBJ+0x100,'<I',nodes[0] if nodes else 0)
 g.run([call(0x524c50,P,[OBJ])]*2+[call(0x524c50,P,[0])],f'walking camera owner links/clear/{fill}/{shape}')
 assert oracle.word(P+0x9c)==oracle.word(P+0xa0)==oracle.word(P+0xa4)==0
scope='Thirteen complete camera dependencies: default FOV/display ratio getters, PC24 projection arithmetic with existing SDK transcendental adapters, camera object construction/destruction/deleting wrapper, actual component payload construction/factory/destruction/deleting wrapper, raw owner snapshot/update and synchronization, and WalkCamera owner binding/clearing. Finite bounded projection parameters, initialized heap/UI services and valid ownership graphs; raw copy cases preserve NaN payloads without arithmetic. Allocation failures and low-byte flag behavior covered. No physical x87 transcendental parity, camera-specific QB initialization/commands, viewport registration, full skater initialization, actual rendered frame or gameplay claimed. Existing checker and comparison allowances unchanged.'
finish('camera-startup-v2',scope,{},extra)
(folder/'camera-startup-v2-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n')
