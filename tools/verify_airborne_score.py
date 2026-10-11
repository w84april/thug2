"""Full airborne frames using the established original scoring/UI fixture graph."""
from pathlib import Path
import ast
spin_source=Path(__file__).with_name('verify_airborne_spin.py').read_text()
prefix=spin_source.split('\nturn_branches=')[0].replace("'airborne-spin.json'","'airborne-score.json'")
# Collect prerequisite observations, then attach each once to the final oracle.
from unicorn import Uc
original_add=Uc.hook_add;observers={}
def add_once(cpu,kind,callback,*args,**kw):
 if getattr(callback,'__name__','')=='observe':
  begin=kw.get('begin',args[1] if len(args)>1 else 1)
  end=kw.get('end',args[2] if len(args)>2 else 0)
  observers[begin,end]=(kind,args,kw)
  return 0
 return original_add(cpu,kind,callback,*args,**kw)
Uc.hook_add=add_once
try:exec(compile(prefix,'<airborne scoring prerequisites>','exec'))
finally:Uc.hook_add=original_add
for kind,args,kw in observers.values():oracle.cpu.hook_add(kind,oracle.observe,*args,**kw)
chosen=[n for n in ast.parse(spin_source).body if isinstance(n,ast.FunctionDef) and n.name in ['turn_config','button']]
exec(compile(ast.Module(body=chosen,type_ignores=[]),'<airborne scoring helpers>','exec'))
bind(0x50ca00,'thug_skater_update_airborne',0,'void',True,True,True)
ROOTS.add(0x50ca00)
for at in [0x50ca00,0x50d948,0x50dacb]:oracle.cpu.hook_add(UC_HOOK_CODE,floor_observe,begin=at,end=at)
LOCK=0x1669000;copy(LOCK,bytes(0x100));put(PHYS+0x151c,'<I',LOCK)
put(SKATER_STATE+0x18,'<I',1);put(SKATER_STATE+0xb0,'<B',1)
put(PHYS+0x370,'<B',0);put(PHYS+0x3f0,'<37fB',*(identity+identity+[0,1,0,0,0]),1)
put(PHYS+0x488,'<2f',0,1);put(PHYS+0x4a0,'<16f',*identity)
put(SCENES+4,'<I',0xffffffff)
initial=bytes(memory);oracle.initial=initial
labels.clear();oracle.cases.clear()
def frame_score(total=179,target=0,value=0,width=0,repeat=1):
 b=turn_config();b.symbol(0x26495947,1,100)
 b.extra += [patch(PHYS+0x151c,'<I',LOCK),patch(SKATER_STATE+0x18,'<I',1),patch(SKATER_STATE+0xb0,'<B',1),patch(SKATER_STATE+0x30,'<B',0),patch(PHYS+0x370,'<B',0),patch(PHYS+0x320,'<f',0)]
 p=spin_entries(b'Fakie\\_Ollie',count=2,ollie=True)+button(0xa0)+[patch(NAME_CONTEXT+0x13a4,'<f',total)]
 if target:p += [patch(META+12,'<I',SPIN_NOTIFY_PROGRAM),patch(META+36,'<I',SPIN_NOTIFY_PROGRAM),patch(GOBS+4,'<4I',target,value,width,NOTIFY)]
 calls=body_setup()+setup()+numeric_setup()+[call(0x50ca00,PHYS,[QUERY]) for _ in range(repeat)]
 print('Start airborne score',total,hex(target),repeat,flush=True)
 case(calls,b.patches()+p,label='airborne score '+str((total,hex(target),repeat)))
 print('Done airborne score',len(labels),flush=True)
for total in [0,169,179,180,349,359,360,-360,719]:frame_score(total)
for target,value,width in [(NAME_CONTEXT+0x13a4,bits(360),4),(PHYS+0x30c,bits(1),4),(PHYS+0x370,1,1),(SKATER_STATE+0xc0,255,1),(SCORE+0x6c,1,4)]:frame_score(target=target,value=value,width=width,repeat=2)
fixture={'base':BASE,'memory':'airborne-score-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':'Complete airborne frame integrated with original spin scoring, score recalculation, combo and numeric text widgets, timed tricks, and native QB callbacks changing live angle/state/current entry across frames. Uses the maintained scoring/UI fixture graph and its actual setup routines. Arena/global/heap bytes compare exactly without arithmetic NaN allowances. The clear-space geometry avoids landing audio here; airborne-update covers collisions and audio. Diagnostic formatting, heap/OS services and terminal native QB are existing boundaries; this is not movement dispatch, rendering or playable training.','callback_counter':'diagnostic_and_native_qb_callbacks','pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'pointer_globals':[index[0x6918ec+4*i] for i in range(8)],'scoped_event_services':{'symbol':'thug_event_services','pointer':SERVICES},'native_callbacks':[{'module':'balance-score-diagnostics.wasm','export':'fixture_balance_score_print','slots':[PRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]}
path=out/'airborne-score-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
assert oracle.coverage[hex(0x563f30)] and oracle.coverage[hex(0x561670)] and oracle.coverage[hex(0x561890)] and qb_calls[hex(NOTIFY)], ({hex(a):oracle.coverage[hex(a)] for a in [0x563f30,0x561670,0x561890]},dict(qb_calls),hex(NOTIFY))
subprocess.run(['node',str(ROOT/'tools/verify_airborne_score_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'branches':dict(branches),'heap_events':dict(oracle.heap_events),'native_qb_calls':dict(qb_calls),'scope':fixture['scope'],'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()},'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory'],out/'balance-score-diagnostics.wasm',out/'grounded-update-callbacks.wasm']}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS airborne scoring',len(labels),dict(oracle.counts))
