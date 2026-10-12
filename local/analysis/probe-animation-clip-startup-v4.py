"""Isolated original clip startup using preserved real playback assets and services."""
from pathlib import Path
import hashlib,itertools,json
ROOT=Path.cwd();folder=ROOT/'local/analysis';saved_file=__file__
preserved=ROOT/'local/validation/objective-notifications.json';preserved_hash=hashlib.sha256(preserved.read_bytes()).hexdigest()
original_read=Path.read_text
allowed={'verify_animation_playback.py','verify_animation_controllers.py','verify_animation_assets.py','verify_objective_notifications.py'}
def readonly_source(path,*args,**kwargs):
 text=original_read(path,*args,**kwargs)
 if path.parent==ROOT/'tools' and path.name in allowed:text=text.replace('report_path.unlink(missing_ok=True)','None # preserved report; read-only prefix')
 return text
try:
 Path.read_text=readonly_source
 __file__=str(ROOT/'tools/verify_animation_playback.py')
 source=Path(__file__).read_text().split('rng=random.Random(0x482200)')[0]
 exec(compile(source,'<read-only preserved original playback services>','exec'))
finally:
 Path.read_text=original_read;__file__=saved_file
assert hashlib.sha256(preserved.read_bytes()).hexdigest()==preserved_hash
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
from specimen import load
pe=load();decoder=Cs(CS_ARCH_X86,CS_MODE_32);coverage={};hits={}
specs=[(0x4823c0,1442,'thug_animation_channel_start_clip_v1',8,'void',True,True,True),(0x4616f0,25,'thug_ui_object_merge_parameters_v1',1,'void',True,False,True)]
for a,size,name,argc,result,heap,diag,this in specs:
 bind(a,name,argc,result,heap,diag,this);coverage[a]={v.address for v in decoder.disasm(pe.get_data(a-0x400000,size),a)};hits[a]=set()
 oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,n,user,root=a:hits[root].add(at),begin=a,end=a+size-1)
functions['0x4823c0']['float_args']=[1,2,4,5]
labels.clear();oracle.cases.clear();oracle.counts.clear();oracle.coverage.clear();oracle.heap_events.clear()
# No missing bootstrap asset is claimed: two actual archived clips are loaded.
# Event array replacement is exercised separately from timeline event delivery.
put(ASTATE+0x58,'<I',0);initial=bytes(memory);oracle.initial=initial
for loop,variant,mirror,pooled in itertools.product([0,1,2,3],['none','empty','secondary','flag','bone','all'],[0,1,256,257],[False,True]):
 b=Build();entries=[]
 if variant in ['secondary','all']:entries += [(0xd697a799,13,0x124),(0xc6ae16ac,2,bits(.25))]
 if variant=='flag':entries += [(0,13,0x1b92121c),(0xc6ae16ac,2,bits(.5))]
 if variant in ['bone','all']:entries.append((0xaeeec12e,10,b.structure([])))
 options=0 if variant=='none' else b.structure(entries)
 calls=[call(0x482af0,ANIM),call(0x4856c0,ANIM,[FILE,len(clips[0]),0]),call(0x482af0,ANIM2),call(0x4856c0,ANIM2,[FILE2,len(clips[1]),0]),call(0x4823c0,CHANNEL,[0x123,bits(0),bits(2),loop,bits(.25),bits(1),mirror,options]),call(0x481870,CHANNEL),call(0x4823c0,CHANNEL,[0x124,bits(.25),bits(1.75),loop,bits(0),bits(-1),mirror,options]),call(0x481f20,CHANNEL),call(0x482b30,ANIM),call(0x482b30,ANIM2)]
 patches=b.patches()+[raw(FILE,clips[0]),raw(FILE2,clips[1]),patch(CHANNEL+0x68,'<2I',EV if variant in ['bone','all'] else 0,8 if variant in ['bone','all'] else 0)]
 case(calls,patches,{0x701438:SPOOL if pooled else 0},label=f'actual clip startup/{loop}/{variant}/{mirror}/{pooled}')
# Real selected structure pools cover the inline pool allocation/release route.
STRUCT_POOL,STRUCT_BLOCKS=BASE+0x1f0000,BASE+0x1f0100
for selected,loop,empty_header,options_kind,pool_route in itertools.product([0,1],[0,3],[False,True],['none','all'],['selected','alternate']):
 b=Build();nested=b.structure([]);options=0 if options_kind=='none' else b.structure([(0xd697a799,13,0x124),(0xc6ae16ac,2,bits(.5)),(0xaeeec12e,10,nested)])
 pool=bytearray(96);struct.pack_into('<6I',pool,0,STRUCT_BLOCKS,STRUCT_BLOCKS+512,0,0,0,STRUCT_BLOCKS)
 blocks=b''.join(struct.pack('<2I',STRUCT_BLOCKS+(i+1)*8 if i<63 else 0,0xa5a5a5a5) for i in range(64))
 patches=b.patches()+[raw(STRUCT_POOL,pool),raw(STRUCT_BLOCKS,blocks),raw(FILE,clips[0]),raw(FILE2,clips[1]),patch(CHANNEL+0x68,'<2I',EV,8),patch(EV-4,'<I',0 if empty_header else 8)]
 calls=[call(0x482af0,ANIM),call(0x4856c0,ANIM,[FILE,len(clips[0]),0]),call(0x482af0,ANIM2),call(0x4856c0,ANIM2,[FILE2,len(clips[1]),0]),call(0x4823c0,CHANNEL,[0x123,bits(0),bits(2),loop,bits(.25),bits(1),257,options]),call(0x481f20,CHANNEL),call(0x482b30,ANIM),call(0x482b30,ANIM2)]
 case(calls,patches,{0x6f3614:selected,0x6f361c+4*(selected if pool_route=='selected' else selected^1):STRUCT_POOL},label=f'inline structure pool/zero-event-header/{selected}/{loop}/{empty_header}/{options_kind}/{pool_route}')
default_file=ROOT/'local/game-files/Game/Data/anims/THPS6_Basics/Default.ska.xbx'
default_data=default_file.read_bytes();input_hashes[str(default_file.relative_to(ROOT))]=hashlib.sha256(default_data).hexdigest()
assert len(default_data)==400 and input_hashes[str(default_file.relative_to(ROOT))]=='d1e46f693c7b7216298c526f23723df51b2826903719e75c9f22ecfe4ab77dbb'
for loop,mirror in itertools.product([0,1,2,3],[0,257]):
 calls=[call(0x482af0,ANIM),call(0x4856c0,ANIM,[FILE,len(default_data),0]),call(0x4823c0,CHANNEL,[0x1ca1ff20,bits(0),bits(1000),loop,bits(.3),bits(1),mirror,0]),call(0x481f20,CHANNEL),call(0x482b30,ANIM)]
 case(calls,[raw(FILE,default_data),patch(AB,'<3I',0x1ca1ff20,ASSET,0)],label=f'original Default bootstrap clip checksum/{loop}/{mirror}')
for existing,kind,value in itertools.product([False,True],[None,1,2,13],[0,1,0x80000000]):
 b=Build();s=0 if kind is None else b.structure([(0x123,kind,value),(0x456,1,7)])
 patches=b.patches()+[patch(WIDGET+0x20,'<I',b.structure([(0x123,1,99)]) if existing else 0)]
 # Build may have grown after the snapshot; take the complete image now.
 patches=b.patches()+patches[1:]
 case([call(0x4616f0,WIDGET,[s])]*2,patches,label=f'owner optional parameter merge/{existing}/{kind}/{value}')
scope='Original clip startup4823c0 and owner optional-parameter merge4616f0 use real archived AirIdle/AirTurnLeft clips, standard dictionaries, asset/cache readers, concrete controller factories and command methods. Initialized successful allocators, valid owned channels/parameters and at most six controllers required. Finite PC24 timeline arithmetic; mirrored low byte. Original THPS6_Basics/Default400B asset is also loaded and directly started with its actual checksum1ca1ff20. No cold bootstrap, full Animation/profile startup, pose rendering, skater control or gameplay credit. Existing explicit heap/cache/diagnostic/native event adapters remain unchanged; no fake game callees or comparator changes.'
fixture={'base':BASE,'memory':'animation-clip-startup-v4-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'animation-playback-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_animation_cache_scope','fixture_animation_cache_available'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'instrumented_native_event_callbacks','pointer_exports':exports,'pointer_fields':sorted(fields),'function_exports':[[0x482b90,'thug_keyframe_animation_cache_cleared']],'native_callbacks':[{'module':'animation-asset-callbacks.wasm','export':'fixture_animation_diagnostics','slots':[PRINT+4]},{'module':'animation-events-callbacks.wasm','export':'fixture_animation_event_native','original':NATIVE}]}
for suffix in ['-fixtures.json','-original.json','-routines.json','-memory.bin']:assert not (folder/('animation-clip-startup-v4'+suffix)).exists()
(folder/fixture['memory']).write_bytes(initial);(folder/'animation-clip-startup-v4-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
instruction_coverage={hex(a):{'covered':len(hits[a]&coverage[a]),'total':len(coverage[a]),'missing':[hex(v) for v in sorted(coverage[a]-hits[a])]} for a,*_ in specs}
excluded={}
for a in [0x482451,0x4824ac,0x482588,0x48262e,0x4826c2,0x48275b,0x4827f5]:excluded[hex(a)]='initialized allocator contract excludes literal cold bootstrap call'
for a in [0x482482,0x482484,0x482489,0x4824dc,0x4825b8,0x48265e,0x4826f2,0x48278b,0x482826]:excluded[hex(a)]='required temporary structure allocation succeeds; null path faults at unchecked mandatory parameter setter'
excluded['0x482922']='stable allocator selection and pool ownership: nonnull selected pool owns the final temporary structure, so failed selected membership is unreachable'
assert set(instruction_coverage['0x4823c0']['missing'])==set(excluded)
instruction_coverage['0x4823c0']['excluded']=excluded;instruction_coverage['0x4616f0']['excluded']={}
(folder/'animation-clip-startup-v4-original.json').write_text(json.dumps({'result':'original pass; Wasm pending; coverage unselected','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(oracle.counts.values()),'counts':dict(oracle.counts),'instruction_coverage':instruction_coverage,'input_hashes':input_hashes,'heap_events':dict(oracle.heap_events),'scope':scope},indent=2)+'\n')
(folder/'animation-clip-startup-v4-routines.json').write_text(json.dumps({hex(a):{'bytes':size,'instructions':len(coverage[a]),'name':name} for a,size,name,*_ in specs},indent=2)+'\n')
print('Original clip startup PASS',len(labels),sum(oracle.counts.values()),instruction_coverage,flush=True)
