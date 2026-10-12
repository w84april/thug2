"""Original local network component lifecycle; frame logic is not substituted."""
from pathlib import Path
source=Path('local/analysis/probe-skater-walk.py').read_text().split('# Real original CRT')[0].replace('0x7cd3e6d5','0xb1d5a3e1')
exec(compile(source,'<preserved component lifecycle graph>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x513630,140,'thug_local_net_create_draft',0,'word',True,False,False),
 (0x512e30,11,'thug_local_net_destroy_draft',0,'void',False,False,True),
 (0x512e40,33,'thug_local_net_delete_draft',1,'word',True,False,True),
 (0x512e70,37,'thug_local_net_bind_draft',0,'void',False,False,True)]
for row in specs:bind_new(*row)
for row in [(0x4fbda0,'thug_skater_cleanup_initialize_draft',1,'void',False,False),(0x51adc0,'thug_local_net_command_draft',3,'word',False,False),
 (0x45e510,'thug_composite_initialize_draft',0,'word',False,False),(0x45ee20,'thug_composite_add_parameters_draft',2,'void',True,True),
 (0x45db30,'thug_composite_finalize_draft',0,'void',True,True),(0x45d890,'thug_composite_destroy_draft',0,'void',True,True)]:bind(*row)
exports.append([0x64bef0,'thug_local_net_pending_methods_draft']);function_exports.append([0x513630,'thug_local_net_create_draft'])
for flags in [0,1,2,3,255,256,257,0xffffffff]:
 g=WalkGraph();g.run([call(0x513630),call(0x512e40,HEAP,[flags])],f'local network factory/delete {flags}')
g=WalkGraph();g.put(CONTEXT+32,'<I',1);g.run([call(0x513630)]*2,'local network factory allocation failure')
for fill,offset in itertools.product([0,0xa5,255],[0,1,4]):
 g=WalkGraph();g.image[P-BASE:P-BASE+0x80]=bytes([fill])*0x80;fields.add(P+offset)
 g.run([call(0x4fbda0,P+offset,[0]),call(0x512e30,P+offset)]*2,f'local network lifetime raw {fill}/{offset}')
for shape in ['none','state','physics','both','reverse','duplicate']:
 g=WalkGraph();types=[] if shape=='none' else [0x43686585] if shape=='state' else [0x5bd63b29] if shape=='physics' else [0x5bd63b29,0x43686585] if shape=='reverse' else [0x43686585,0x5bd63b29]*(2 if shape=='duplicate' else 1)
 nodes=[g.component(t) for t in types]
 for i,node in enumerate(nodes):g.put(node+16,'<I',nodes[i+1] if i+1<len(nodes) else 0)
 g.put(OBJ+0x100,'<I',nodes[0] if nodes else 0);g.run([call(0x512e70,P)]*2,f'local network binding {shape}')
 assert [oracle.word(P+0x3c),oracle.word(P+0x40)]==[nodes[types.index(t)] if t in types else 0 for t in [0x43686585,0x5bd63b29]]
for key in [0,1,0xffffffff]:
 g=WalkGraph();g.run([call(0x51adc0,P,[key,0,0])],f'local network unhandled command {key}')
for reverse in [False,True]:
 g=WalkGraph();registry=[(0x7cd3e6d5,0x513630),(0x43686585,0x519740)];g.registry(registry)
 order=registry[::-1] if reverse else registry;descriptors=[g.structure([(0xb6015ea8,13,t)]) for t,_ in order]
 calls=[call(0x45e510,OBJ)]+[call(0x45ee20,OBJ,[s,0]) for s in descriptors]+[call(0x45db30,OBJ),call(0x45d890,OBJ)]
 g.run(calls,f'local network shared lifetime {reverse}')
scope='Four complete local network lifecycle routines: factory513630, destructor512e30, deletion512e40 and dependency binding512e70. Shared initialization, unhandled command and composite lifecycle execute unchanged. Network frame5136c0/5131a0 and full skater startup remain explicitly pending; no network or playable-game claim.'
extra={**extra,'function_exports':function_exports,'memory_fixture':'skater-walk-memory.wasm'}
finish('skater-local-net',scope,{},extra)
(folder/'skater-local-net-routines.json').write_text(json.dumps({hex(row[0]):{'bytes':row[1],'instructions':len(coverage[row[0]]),'name':row[2]} for row in specs},indent=2)+'\n')
