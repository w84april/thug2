"""Actual original startup links; old builders and output writes are omitted."""
from pathlib import Path
source=Path('local/analysis/probe-skater-full-startup.py').read_text().split('records=[]')[0]
old="source=Path('local/analysis/probe-skater-final-startup.py').read_text().split('# Final complete startup cases.')[0]"
source=source.replace(old,old+"\nsource='\\n'.join(line for line in source.splitlines() if not line.startswith(\"port=folder/'skater-final-startup-ports.c'\"))")
exec(compile(source,'<immutable startup setup, builders omitted>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear();prefix_hits.clear()
specs=[(0x433c10,33,'thug_object_light_construct_v1',0,'word',False,False,True),
 (0x57b2f0,301,'thug_skater_add_shared_components_v1',1,'void',True,False,False),
 (0x4fa3c0,84,'thug_skater_camera_bind_owner_v1',1,'void',False,False,True),
 (0x525e60,33,'thug_walk_bind_camera_v1',1,'void',False,False,True)]
for row in specs:bind_new(*row)
bind(0x582d90,'thug_skater_construct_complete_draft',6,'word',True,True)
bind(0x45e510,'thug_composite_initialize_draft',0,'word')
exports.extend([[0x646594,'thug_object_light_pending_methods_v1'],[0x64620c,'thug_motion_methods_draft'],[0x64b6c4,'thug_object_proximity_methods_draft'],[0x646514,'thug_object_sound_methods_draft'],[0x6460e4,'thug_lockobj_methods_draft']])
types=[0x0a015e17,0x1d5b1ae6,0x07713c7b,0x0f1641e3,0x5cb5cb7e]
for fill,alignment in itertools.product([0,0xa5,255],[0,1,4]):
 g=FinalGraph(fill);fields.add(P+alignment);g.run([call(0x433c10,P+alignment)]*2,f'raw light construction/{fill}/{alignment}')
for repeats,existing in itertools.product([1,2,3],[False,True]):
 g=FinalGraph();g.registry([(t,0) for t in types]);calls=[call(0x45e510,OBJ)]
 if existing:
  c=g.component(0x43686585);g.put(c+12,'<I',OBJ);g.put(OBJ+0x100,'<I',c);calls=[]
 calls += [call(0x57b2f0,args=[OBJ])]*repeats
 g.run(calls,f'shared component append/{repeats}/{existing}');chain=[];c=oracle.word(OBJ+0x100)
 while c:chain.append(oracle.word(c+4));assert oracle.word(c+12)==OBJ,(repeats,existing,hex(c),hex(oracle.word(c+4)),hex(oracle.word(c+12)),hex(OBJ));c=oracle.word(c+16)
 assert chain==([0x43686585] if existing else [])+types*repeats
for local in [0,1,256,257]:
 g=FinalGraph();g.symbol(0x78f80ec4,2,bits(.125));g.registry(registry+[(t,0) for t in types]);g.run([call(0x582d90,OBJ,[0,MANAGER,local,0,0,1]),call(0x57b2f0,args=[OBJ])],f'completed constructor then real shared components/{local}')
 chain=[];c=oracle.word(OBJ+0x100)
 while c:chain.append(oracle.word(c+4));c=oracle.word(c+16)
 assert chain[-5:]==types
for fill,shape in itertools.product([0,0xa5,255],['empty','all','reversed','state','trick','duplicates']):
 g=FinalGraph(fill);ts=[] if shape=='empty' else [0xd9151d4d,0x43686585] if shape=='reversed' else [0x43686585] if shape=='state' else [0xd9151d4d] if shape=='trick' else [0x43686585,0xd9151d4d]* (2 if shape=='duplicates' else 1)
 nodes=[g.component(t) for t in ts]
 for i,c in enumerate(nodes):g.put(c+16,'<I',nodes[i+1] if i+1<len(nodes) else 0)
 g.put(OBJ+0x100,'<I',nodes[0] if nodes else 0)
 g.run([call(0x4fa3c0,P,[OBJ])]*2+[call(0x4fa3c0,P,[0])],f'camera owner links and clear/{fill}/{shape}')
 assert oracle.word(P+0x170)==oracle.word(P+0x174)==oracle.word(P+0x178)==0 and oracle.word(P+0x28)==3
for fill in [0,0xa5,255]:
 g=FinalGraph(fill);g.run([call(0x4fa3c0,P,[0])]*2,f'null camera owner preserves state/{fill}');assert oracle.word(P+0x28)==int.from_bytes(bytes([fill])*4,'little')
for fill,shape in itertools.product([0,0xa5,255],['empty','other','camera','after other','duplicates']):
 g=FinalGraph(fill);ts=[] if shape=='empty' else [0x11223344] if shape=='other' else [0xc7d37ec2] if shape=='camera' else [0x11223344,0xc7d37ec2] if shape=='after other' else [0xc7d37ec2]*2
 nodes=[g.component(t) for t in ts]
 for i,c in enumerate(nodes):g.put(c+16,'<I',nodes[i+1] if i+1<len(nodes) else 0)
 g.put(OBJ+0x100,'<I',nodes[0] if nodes else 0);g.run([call(0x525e60,P,[OBJ])]*2,f'walking camera link/{fill}/{shape}')
 assert oracle.word(P+0x175c)==OBJ and oracle.word(P+0x1760)==(nodes[ts.index(0xc7d37ec2)] if 0xc7d37ec2 in ts else 0)
scope='Four complete post-construction dependencies: raw Light construction, cdecl Motion/Proximity/Sound/Light/LockObj assembly with live appends, camera owner/state/trick linking and clearing, and walking camera linking. Existing actual constructors and component searches run unchanged. Four sequences start with the complete original local/remote skater constructor. Initialized services, bounded component lists, nonnull walking camera owners and successful internal allocations are required; allocation failures fault before shared assembly returns. Light vtable is identity-only; no virtual behavior, complete581850/profile initialization, rendered frame or gameplay is claimed.'
excluded={a:'unchecked allocation failure appends null and faults; valid startup requires successful storage' for a in ['0x57b32b','0x57b365','0x57b399','0x57b3ca','0x57b3fe']}
finish('skater-initialization-links-v1',scope,excluded,extra)
(folder/'skater-initialization-links-v1-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n')
