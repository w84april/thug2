"""Compare complete landing sound selection and dispatch with original x86."""
from pathlib import Path
source=Path('tools/verify_sound_events.py').read_text()
prefix=source.split('# Selection/fallback')[0].replace("'sound-events.json'","'jump-sound.json'").replace("'sound-events-memory.bin'","'jump-sound-memory.bin'")
exec(compile(prefix,'<jump sound prerequisites>','exec'))
functions['0x518ee0']={'name':'thug_sound_component_jump','this':True,'result':'void','cleanup':8,'memory':True,'stack_args':[0,1],'float_args':[0]}
for at in [0x518ee0,0x4443b0]:cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
selected=Counter();dispatches=[]
def trace(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP)
 if at==0x4443b0:selected[hex(oracle.word(sp+4))]+=1
 else:dispatches.append([oracle.word(sp+4+i*4) for i in range(7)])
cpu.hook_add(UC_HOOK_CODE,trace,begin=0x4443b0,end=0x4443b0)
cpu.hook_add(UC_HOOK_CODE,trace,begin=0x444bb0,end=0x444bb0)
EVENTS=[0x129ab922,0x8f5791b0,0x8bb1ab02]
functions['0x518d60']={'name':'thug_sound_jump_for_state','this':True,'result':'void','cleanup':12,'memory':True,'stack_args':[0,1,2],'float_args':[0]}
hits=Counter()
def instructions(cpu,at,size,user):hits[at]+=1
for at,size in [(0x518d60,101),(0x518ee0,22)]:
 cpu.hook_add(UC_HOOK_CODE,instructions,begin=at,end=at+size-1)
cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=0x518d60,end=0x518d60)
def landing(intensity,material=7):return 0x518ee0,COMPONENT,[bits(intensity),material,0]
def landing_graph(mode='direct',bounds=(100,100,100,0),missing=None,rotate=0):
 b=graph(mode,bounds)
 entries=[(0,b.words(0,0x11111111,EVENT_PARAMETER))]
 for j,name in enumerate(EVENTS):
  if name!=missing:
   event=5+(j+rotate)%3;entries.append((event,b.words(0x10000+event,name,EVENT_PARAMETER)))
 b.table('events',entries);return b
for state in [0,3,4,5,0x104,0xffffffff]:
 for flag in [0,1,2,127,128,255]:
  for i,intensity in enumerate([0.,-0.,.001,.5,1.,1.5,-1.]):
   mode=['direct','weighted','threshold','empty','event_fallback','material_fallback','missing_path'][i]
   p=[patch(COMPONENT+0x18,'<I',state),patch(COMPONENT+0x1e,'<B',flag),patch(COMPONENT+0x24,'<f',[0.,.25,1.,2.][(flag+i)%4])]
   changes={0x6f8a4c:i%2,0x67db08:bits([0,25,100][i%3])}
   case([landing(intensity,0xab000007)],landing_graph(mode,(120,40,100,0),rotate=i%3),p,changes,'landing state and full byte flag, event-table order, remapping and fallback')
   expected=EVENTS[0 if state!=4 else 2 if flag else 1]
   assert (dispatches[-1][0]&255)==5+(EVENTS.index(expected)+i%3)%3
for name,state,flag in [(EVENTS[0],0,0),(EVENTS[1],4,0),(EVENTS[2],4,1)]:
 for missing in [None,name]:
  for peer in [0,1,8,9]:
   p=[patch(COMPONENT+0x18,'<I',state),patch(COMPONENT+0x1e,'<B',flag),patch(PEER+0x60,'<I',peer)]
   case([landing(.75)],landing_graph(missing=missing),p,label='registered default id zero when named event is absent, peer filters')
   assert (dispatches[-1][0]&255)==(0 if missing else 5+EVENTS.index(name))
for state,flag in [(0,0),(4,0),(4,1)]:
 for disabled in [{0x7d6a38:0},{0x7cefa8:2},{0x7cefa8:6}]:
  case([landing(1)],landing_graph(),[patch(COMPONENT+0x18,'<I',state),patch(COMPONENT+0x1e,'<B',flag)],disabled,'disabled dispatch still performs original event lookup')
 for failed in [11,12,13,16]:
  case([landing(.5)],landing_graph(),[patch(COMPONENT+0x18,'<I',state),patch(COMPONENT+0x1e,'<B',flag),patch(CONTEXT+4,'<2I',failed,0x80004005)],label='actual device method failure')
 for intensity in [1e-40,1e30,3e38,float('inf'),-float('inf'),float('nan')]:
  for scale in [0.,1.,-1.]:
   p=[patch(COMPONENT+0x18,'<I',state),patch(COMPONENT+0x1e,'<B',flag),patch(COMPONENT+0x24,'<f',scale),patch(CONFIG,'<I',0),patch(POSITION,'<4f',32768,-32769,65536,1)]
   case([landing(intensity)],landing_graph(),p,{0x6fc49c:1},'nonfinite or overflow percentage wire conversion with silent local audio')
# A device callback changes live landing mode; the second call must reselect it.
for target,value,width in [(COMPONENT+0x18,4,4),(COMPONENT+0x1e,255,1),(COMPONENT+0x24,bits(.5),4)]:
 for start_state in [0,4]:
  p=[patch(COMPONENT+0x18,'<I',start_state),patch(COMPONENT+0x1e,'<B',0),patch(CONTEXT+40,'<4I',16,target,value,width)]
  case([landing(.75),landing(.75),landing(.75)],landing_graph(),p,label='consecutive landings retain sound queues and callback-mutated component')
for stored in [0,4]:
 for state in [0,1,4,5,0x104,0xffffffff]:
  for flag in [0,255]:
   calls=[(0x518d60,COMPONENT,[bits(.75),0xab000007,state,0]),landing(.75,0xab000007)]
   p=[patch(COMPONENT+0x18,'<I',stored),patch(COMPONENT+0x1e,'<B',flag)]
   case(calls,landing_graph(),p,label='explicit state overrides stored state; wrapper reloads stored state')
   expected=5+(0 if state!=4 else 2 if flag else 1)
   assert (dispatches[-2][0]&255)==expected
   assert (dispatches[-1][0]&255)==5+(0 if stored!=4 else 2 if flag else 1)
assert all(selected[hex(n)] for n in EVENTS)
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
from specimen import load
pe=load();decoder=Cs(CS_ARCH_X86,CS_MODE_32)
covered=[ins.address for at,size in [(0x518d60,101),(0x518ee0,22)] for ins in decoder.disasm(pe.get_data(at-0x400000,size),at)]
assert len(covered)==43 and all(hits[a] for a in covered)

scope='Two complete original jump-sound routines518d60/518ee0: explicit state selects ordinary/rail/slide events; wrapper captures stored state. Actual event tables, material fallback, clip selection, spatial audio, OS-device boundary and network queues run. Direct-state/stored-state disagreement, nonboolean flag bytes, missing events, callback mutation, repeated calls and nonfinite wire conversion are covered; complete fixture memory/globals/defined packet bytes compare, with existing one-byte unwritten packet padding seeded zero. All43 original instructions covered. Integrated jump-sound recovery; actual browser playback and complete level integration remain unfinished.'
fixture={'base':BASE,'memory':'jump-sound-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'audio_device_calls','pointer_exports':exports,'pointer_fields':sorted(fields),'pointer_globals':prior['pointer_globals'],'native_callbacks':prior['native_callbacks']}
path=out/'jump-sound-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
print('x86 complete:',len(oracle.cases),'cases',sum(oracle.counts.values()),'calls',dict(callback_counts),dict(oracle.heap_events),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_jump_sound_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'instruction_hits':{f'{a:08x}':hits[a] for a in covered},'callee_coverage':dict(oracle.coverage),'selected_event_names':dict(selected),'dispatch_observations':len(dispatches),'audio_device_calls':dict(callback_counts),'heap_events':dict(oracle.heap_events),'os_services':dict(os_calls),'zeroed_packet_padding_entries':padding_entries,'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/'jump-sound-memory.bin',ROOT/'local/validation/collision/audio-device-callbacks.wasm',ROOT/'local/validation/collision/script-values-memory.wasm']},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
