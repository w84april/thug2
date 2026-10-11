"""Compare complete landing sound selection and dispatch with original x86."""
from pathlib import Path
source=Path(__file__).with_name('verify_sound_events.py').read_text()
prefix=source.split('# Selection/fallback')[0].replace("'sound-events.json'","'landing-sound.json'").replace("'sound-events-memory.bin'","'landing-sound-memory.bin'")
exec(compile(prefix,'<landing sound prerequisites>','exec'))
functions['0x518cf0']={'name':'thug_sound_component_land','this':True,'result':'void','cleanup':8,'memory':True,'stack_args':[0,1],'float_args':[0]}
for at in [0x518cf0,0x4443b0]:cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
selected=Counter();dispatches=[]
def trace(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP)
 if at==0x4443b0:selected[hex(oracle.word(sp+4))]+=1
 else:dispatches.append([oracle.word(sp+4+i*4) for i in range(7)])
cpu.hook_add(UC_HOOK_CODE,trace,begin=0x4443b0,end=0x4443b0)
cpu.hook_add(UC_HOOK_CODE,trace,begin=0x444bb0,end=0x444bb0)
EVENTS=[0x1d296aec,0x80e4427e,0x840278cc]
def landing(intensity,material=7):return 0x518cf0,COMPONENT,[bits(intensity),material,0]
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
assert all(selected[hex(n)] for n in EVENTS)
scope='One complete original routine518cf0: landing sound selection for ordinary landings, grinding and sliding. Actual event-table iteration, material fallback, clip selection, percentage remapping, positional attenuation, device playback and network queues execute through recovered callees. Full fixture memory, globals, device traces and defined packet bytes compare. Missing named events use a registered default ID0; required material/settings/device preconditions remain. Stateful callbacks and repeated calls verify live component changes. OS audio and heap services are explicit boundaries; original unwritten sound-packet tail byte is seeded/defined zero as in sound-events. Nonfinite wire conversion is covered with local audio suppressed to respect existing positional-stack contracts. No platform audio backend, full airborne update or playable level claim.'
fixture={'base':BASE,'memory':'landing-sound-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'audio_device_calls','pointer_exports':exports,'pointer_fields':sorted(fields),'pointer_globals':prior['pointer_globals'],'native_callbacks':prior['native_callbacks']}
path=out/'landing-sound-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
print('x86 complete:',len(oracle.cases),'cases',sum(oracle.counts.values()),'calls',dict(callback_counts),dict(oracle.heap_events),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_landing_sound_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'selected_event_names':dict(selected),'dispatch_observations':len(dispatches),'audio_device_calls':dict(callback_counts),'heap_events':dict(oracle.heap_events),'os_services':dict(os_calls),'zeroed_packet_padding_entries':padding_entries,'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/'landing-sound-memory.bin',out/'audio-device-callbacks.wasm',out/'script-values-memory.wasm']},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
