"""Original movement sweep with actual collision, QB delivery and wall response.

Reuse the full wall oracle's initialized state and its recorded OS/native/heap
boundaries. Only this outer entry maps the original query globals to port memory;
the nested wall call sees the query state left by the first collision.
"""
import hashlib,json,math,random,struct,subprocess
from collections import Counter
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ESP
import verify_wall_response as w
from verify_wall_response import ROOT,SHA256,out,BASE,SIZE,P,BODY,BODY2,STATE,STATE2,INPUT,CALLBACK,PRINT,QUERY,GAME,NODES,OWNERS,REFS,RUNTIME,BUCKETS,GRAPH,ADAPTER,HEAP,LOG,NATIVE,RECEIVE,OBJECT,patch,bits
report_path=out.parent/'movement-sweep.json';report_path.unlink(missing_ok=True)
EVENT,GATE,GATE2,PROVIDER,PROVIDER_METHODS=GAME+0x4000,GAME+0x5000,GAME+0x5100,GAME+0x6000,GAME+0x6100
NODE_FN=0x3f01050;NODE_TABLE=0x1900000;NODE_ARRAY=0x1911000
# Keep reference chains but provide initialized object-component lists for
# moving hit owners, whose original component lookup reads offset100.
for i in range(3):w.put(OWNERS+i*32+0x100,'<I',0)
w.put(P+0x1510,'<I',EVENT);w.put(P+0x1530,'<I',GATE)
w.put(EVENT+12,'<I',BODY);w.put(EVENT+0x28,'<I',0xabcdef01)
w.put(GATE+0x26,'<B',0);w.put(GATE2+0x26,'<B',1)
w.put(PROVIDER,'<5I',PROVIDER_METHODS,0xc472ecc5,0,OWNERS,0);w.put(PROVIDER_METHODS+0x34,'<I',NODE_FN)
# Start with an empty, correctly terminated node table. Cases register the
# actual checksum of the intersected training object in its real hash slot.
for j in range(16384):w.put(NODE_TABLE+j*4,'<Hh',0,-1)
w.put(NODE_TABLE+0x1000c,'<I',NODE_ARRAY)
w.initial=bytes(w.memory);w.oracle.initial=w.initial
w.functions['0x506e50']={'name':'thug_skater_movement_sweep','this':True,'result':'void','cleanup':0,'memory':True,'stack_args':[]}
w.cpu.hook_del(w.query_hook);w.cpu.hook_add(UC_HOOK_CODE,w.begin,begin=0x506e50,end=0x506e50)
w.boundary_kinds[NODE_FN]=3;w.cpu.hook_add(UC_HOOK_CODE,w.event_callback,begin=NODE_FN,end=NODE_FN)
w.fields.add(PROVIDER_METHODS+0x34)
for at in [0x506e50,0x434bf0,0x434a60,0x45c1b0,0x45cfc0,0x461480,0x475420,0x474540,0x4750b0,0x473420]:w.cpu.hook_add(UC_HOOK_CODE,w.oracle.observe,begin=at,end=at)
first_hit={}
def branch(uc,address,size,user):
 if address==0x507004:
  hit=bool(uc.reg_read(UC_X86_REG_EAX)&255);w.case_events['first_probe_hit' if hit else 'first_probe_miss']+=1
  if hit:first_hit.update(checksum=w.oracle.word(P+0x100),flags=int.from_bytes(uc.mem_read(P+0xf8,2),'little'),material=uc.mem_read(P+0xfa,1)[0],owner=w.oracle.word(P+0x110),moving_owner=w.oracle.word(P+0x140),normal=bytes(uc.mem_read(P+0x130,16)).hex())
 else:w.case_events[{0x506e99:'changed_position',0x50706b:'skateable_position_correction',0x5070e1:'collision_event_delivery',0x50710c:'wall_response_calls'}[address]]+=1
for at in [0x506e99,0x507004,0x50706b,0x5070e1,0x50710c]:w.cpu.hook_add(UC_HOOK_CODE,branch,begin=at,end=at)
# Spawn notifications retain the separately documented three zero tail bytes.
spawn_padding_entries=0
def seed_spawn(uc,address,size,user):
 global spawn_padding_entries
 uc.mem_write(uc.reg_read(UC_X86_REG_ESP)-0x23,bytes(3));spawn_padding_entries+=1
w.cpu.hook_add(UC_HOOK_CODE,seed_spawn,begin=0x473420,end=0x473420)
def case(b=None,p=(),changes=None,label='sweep'):
 first_hit.clear();b=b or w.configuration(height=0.,extra=0.,turn=.5,angle=45.,speed=100.)
 b.symbol(0x3eede4d3,2,bits(30))
 result=w.case(b,p,changes,label=label,fn=0x506e50);result['first_hit']=dict(first_hit)
 return result
def nodes(b,names,script=8,local=False):
 entries=[]
 # Collision delivery requires a bytecode instance; use the real cached QB
 # handler, whose native command is observed at the established boundary.
 key=script
 for name in names:entries.append(b.structure([(0xa1dc81f9,13,name),(0x2ca8a299,13,key)]))
 array=b.array(entries)
 if local:return [patch(CALLBACK+40,'<I',array)]+[patch(OWNERS+i*32+0x100,'<I',PROVIDER) for i in range(3)]
 patches=[patch(NODE_ARRAY,'<3I',0xa00,len(entries),entries[0] if len(entries)==1 else b.words(*entries))]
 slots=set()
 for i,name in enumerate(names):
  slot=name&0x3fff
  while slot in slots:slot=(slot+1)&0x3fff
  slots.add(slot);patches.append(patch(NODE_TABLE+slot*4,'<Hh',0,i))
 return patches
# Smoke coverage uses the real loader's recorded crossing segment.
first=next(t for t in w.loader['queries'] if t['returned'])
segment=struct.unpack('<8f',bytes.fromhex(first['segment']))
case(p=[patch(BODY+0x5c,'<4f',*segment[:4]),patch(BODY+0x4c,'<4f',*segment[4:])],label='training sweep smoke')
case(p=[patch(BODY+0x4c,'<4f',25,10,20,1)],label='unchanged position short circuit')

floor=next(t for t in w.loader['queries'] if t['returned'] and struct.unpack_from('<f',bytes.fromhex(t['result']),4)[0]>.9 and not (struct.unpack_from('<H',bytes.fromhex(t['result']),0x2c)[0]&6))
segment=struct.unpack('<8f',bytes.fromhex(floor['segment']))
case(p=[patch(BODY+0x5c,'<4f',*segment[:4]),patch(BODY+0x4c,'<4f',*segment[4:]),patch(P+0x68,'<4f',float('nan'),1,0,0)],label='unordered surface orientation comparison')

rng=random.Random(0x506e50);contacts=[]
# Ordered equality across all four lanes, including signed zero, is the only
# no-op path. NaNs and changes confined to W must enter the actual sweep.
for i in range(40):
 position=[(0.,-0.,0.,1.),(25.,10.,30.,1.),(1e30,-1e30,1e-30,-0.),(float('nan'),1.,2.,1.)][i%4]
 previous=list(position)
 if i%5:previous[i%4]=[0.,1.,-1.,float('nan')][(i//4)%4]
 case(p=[patch(BODY+0x4c,'<4f',*position),patch(BODY+0x5c,'<4f',*previous)],label='four-lane equality signed zero and unordered positions')
# The fixture keeps actual training geometry and original static/moving probes.
# Up-vector variations select correction, tangent contact, and wall handling.
for i,test in enumerate(w.loader['queries'][::3]):
 segment=struct.unpack('<8f',bytes.fromhex(test['segment']))
 for variant in range(3):
  up=[(0,1,0,0),(0,0,0,0),(float('nan'),1,0,0)][variant]
  p=[patch(BODY+0x5c,'<4f',*segment[:4]),patch(BODY+0x4c,'<4f',*segment[4:]),patch(P+0x68,'<4f',*up),
     patch(BODY+0xbc,'<B',i%2),patch(GATE+0x26,'<B',255 if variant==1 and i%3==0 else 0)]
  if i%7==0:p.extend([patch(P+0x140,'<3I',OWNERS,0,REFS),patch(OWNERS+4,'<I',P+0x140),patch(REFS+4,'<I',P+0x140)])
  b=w.configuration(height=0.,extra=0.,turn=[0.,.5,1.][i%3],angle=45.,speed=100.)
  if test['returned']:
   material=bytes.fromhex(test['result'])[0x2e]
   b.table('materials',[(material,b.words(material,w.MATERIAL_NAME))])
  result=case(b,p,{0x693998:[1,254,255][i%3]},label='training first sweep correction script gate and real wall chain')
  if variant==1 and result['first_hit'].get('flags',0)&0x40:
   contacts.append((p,result['first_hit']))
# Threshold sides and equality, both signs and unordered dot products, using
# a real nearly-horizontal training face rather than bypassing collision.
floor_segment=struct.unpack('<8f',bytes.fromhex(floor['segment']))
for component in [0.,.009999,.01,.010001,-.009999,-.01,-.010001,float('nan'),float('inf'),-float('inf')]:
 p=[patch(BODY+0x5c,'<4f',*floor_segment[:4]),patch(BODY+0x4c,'<4f',*floor_segment[4:]),patch(P+0x68,'<4f',0,component,0,0)]
 case(p=p,label='surface orientation dot threshold and unordered acceptance')
# Height and extension getters can return exact int32 values or float32. The
# original spills Y/Z/W offset sums while retaining the X sum's wide exponent.
for i in range(64):
 height=[0.,8.,-8.,24.25,2**24+1,2**31-1,-2**31,1e-30,1e30][i%9]
 extra=[0.,20.,-20.,2**24+1,1e-30,1e30][(i//4)%6]
 pos=[(25,10,30,1),(1e30,-1e30,1e30,7),(1e-30,0,-1e-30,0)][(i//6)%3]
 previous=[x*.5 for x in pos]
 case(w.configuration(height=height,extra=extra,turn=.5,angle=45.,speed=1e30),
      [patch(BODY+0x4c,'<4f',*pos),patch(BODY+0x5c,'<4f',*previous)],label='parameter numeric types and wide endpoint intermediates')
# Actual hit checksums drive the real node table and bytecode handler. The
# handler executes a native boundary that changes the post-delivery gate/body
# or overwrites the probe normal; the wall call must retain its local normal.
assert contacts,'Training fixtures must exercise event-marked surfaces'
for i,(p,hit) in enumerate(contacts[::max(1,len(contacts)//8)][:8]):
 for mode,address,value in [(0,0,0),(1,GATE+0x26,1),(1,GATE+0x26,255),(2,P+0x1530,GATE2),
                            (2,P+0x130,bits(.875)),(2,P+0x120,bits(300)),(3,0,BODY2),(4,0,STATE2)]:
  b=w.configuration(height=0.,extra=0.,turn=.5,angle=45.,speed=100.)
  q=nodes(b,[hit['checksum']])+p+[patch(GATE+0x26,'<B',0),patch(CALLBACK+4,'<3I',mode,address,value)]
  b.table('materials',[(hit['material'],b.words(hit['material'],w.MATERIAL_NAME))])
  case(b,q,label='actual collision QB handler mutates gate body state or probe')
# Moving collisions expose an actual owner and call its node-provider method.
# Local arrays retain precedence over the global table and still run real QB.
actors_by_checksum={struct.unpack_from('<I',bytes.fromhex(c['actors']),4)[0]:c['actors'] for c in w.world['world']}
moving_deliveries=0
for p,hit in contacts[::max(1,len(contacts)//6)][:6]:
 b=w.configuration(height=0.,extra=0.,turn=.5,angle=45.,speed=100.)
 # Use the constructor-recorded actor for this actual event-marked mesh. Its
 # identity transform at zero position intersects the same recorded segment.
 # An empty static list and one moving actor isolate the moving-owner path.
 q=nodes(b,[hit['checksum']],local=True)+p+[patch(GATE+0x26,'<B',0),
    [RUNTIME,actors_by_checksum[hit['checksum']]],patch(RUNTIME+0x10,'<4f',0,0,0,0),
    patch(RUNTIME+8,'<H',0),patch(RUNTIME+0xa8,'<B',1),patch(NODES+12,'<I',NODES+48),patch(w.SCENES+4,'<I',0xffffffff)]
 result=case(b,q,label='moving-owner node provider feeds actual QB collision handler')
 assert result['first_hit'].get('moving_owner')==OWNERS,result['first_hit']
 records=w.oracle.word(CALLBACK)
 moving_deliveries+=sum(w.oracle.word(CALLBACK+128+i*96)==3 for i in range(records))
assert moving_deliveries==6,moving_deliveries
assert w.outcomes['first_probe_hit'] and w.outcomes['first_probe_miss'] and w.outcomes['skateable_position_correction'] and w.outcomes['wall_response_calls']
assert w.oracle.coverage['0x461480'] and w.oracle.coverage['0x4750b0'] and w.oracle.coverage['0x5059d0']

scope='Complete original movement sweep 00506e50 through the original training collision grid, skateable-surface correction, collision-script dispatch, suppression gate and complete wall response. Four-lane position comparison, query segments, original hit-normal snapshot and post-event body/gate rereads are compared through real callees. The twelve-byte query-global mapping occurs only at the outer sweep boundary. Heap, OS audio/CRT and native/object/node-provider gameplay methods remain instrumentation boundaries. Original sound/spawn packet padding is explicitly zeroed as previously documented; numeric oracle limits remain. No complete skating update, runtime startup, rendering, browser audio or playable training level is claimed.'
callbacks=[dict(spec,module='sweep-callbacks.wasm') for spec in w.prior['native_callbacks']]+[{'module':'sweep-callbacks.wasm','export':'fixture_sweep_nodes','original':NODE_FN}]+[dict(spec,module='wall-audio-callbacks.wasm') for spec in w.audio['native_callbacks']]
fixture={'base':BASE,'memory':'movement-sweep-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':w.prior['memory_exports'],
 'globals':w.globals_,'functions':w.functions,'float_fields':w.float_fields,'cases':w.oracle.cases,'case_labels':w.labels,'scope':scope,'callback_counter':'event_and_audio_callbacks',
 'pointer_symbols':w.prior['pointer_symbols'],'pointer_exports':w.exports,'pointer_fields':sorted(w.fields),'pointer_globals':sorted(w.pointer_globals),'native_callbacks':callbacks}
path=out/'movement-sweep-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(w.initial)
adapter=out/'sweep-callbacks.wasm'
subprocess.run([str(ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang'),'--target=wasm32-unknown-unknown','-O2','-Wall','-Wextra','-Werror','-nostdlib','-Wl,--no-entry,--import-memory,--export-all,--global-base=58720256',str(ROOT/'tools/sweep_callbacks.c'),'-o',str(adapter)],check=True)
print('x86 complete:',len(w.oracle.cases),'cases',dict(w.outcomes),dict(w.oracle.coverage),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_movement_sweep_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(w.oracle.counts),'outcomes':dict(w.outcomes),'callee_coverage':dict(w.oracle.coverage),'audio_device_calls':dict(w.callback_counts),'heap_events':dict(w.oracle.heap_events),'os_services':dict(w.os_calls),'zeroed_sound_padding_entries':w.padding_entries,'zeroed_spawn_padding_entries':spawn_padding_entries,'scope':scope,
 'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
 'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory'],adapter,out/'wall-audio-callbacks.wasm',out/'script-values-memory.wasm']},
 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(w.oracle.counts))
