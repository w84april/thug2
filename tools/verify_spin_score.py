"""Compare complete spin scoring and its remaining prerequisites to original x86."""
from pathlib import Path
from unicorn import Uc
# Capture only the existing diagnostic hook so this suite can retain typed
# spin diagnostics. Gameplay instructions and all their callees stay untouched.
original_hook_add=Uc.hook_add;diagnostic_hooks=[]
def capture_hook(self,*args,**kwargs):
 h=original_hook_add(self,*args,**kwargs)
 if kwargs.get('begin',args[3] if len(args)>3 else None)==0x401c30 and getattr(args[1],'__name__','')=='debug_output':diagnostic_hooks.append((self,h))
 return h
Uc.hook_add=capture_hook
try:
 task_source=Path(__file__).with_name('verify_grounded_update.py').read_text()
 exec(compile(task_source.split('\nfor speed in [0,100]:')[0].replace("'grounded-update.json'","'spin-score.json'"),'<spin scoring prerequisites>','exec'))
finally:Uc.hook_add=original_hook_add
assert len(diagnostic_hooks)==1, ('diagnostic hooks',len(diagnostic_hooks))
for cpu,h in diagnostic_hooks:cpu.hook_del(h)
NEW=[(0x4022c0,'thug_clamp_number',3,'double',False,False,False),
 (0x419c70,'thug_animation_component_all_flipped',0,'byte',False,False,True),
 (0x51cac0,'thug_timed_tricks_set_spin',1,'void',False,False,True),
 (0x563f30,'thug_score_update_spin',1,'void',True,True,True),
 (0x564be0,'thug_score_update_spin_if_trick',1,'void',True,True,True)]
for row in NEW:
 bind(*row);oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=row[0],end=row[0])
functions['0x4022c0']['float_args']=[0,1,2]
for at in [0x51c950,0x6234fe,0x561670,0x562e40,0x561890,0x460a20]:
 if at not in observe:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at);observe.append(at)
DIAG,BLEND_NODES=0x1670000,0x1661000
copy(DIAG,bytes(0x5000));copy(BLEND_NODES,bytes(0x1000));put(PRINT,'<I',DIAG);put(DIAG+4,'<I',SCORE);fields.add(DIAG+8)
put(GACOMP+0x34,'<I',BLEND_NODES)
for i in range(4):
 put(BLEND_NODES+i*128+4,'<I',i if i<3 else 0xffffffff)
 put(BLEND_NODES+i*128+12,'<I',BLEND_NODES+(i+1)*128 if i<3 else 0)
 put(BLEND_NODES+i*128+0x54,'<I',0x20000000)
# Same diagnostic adapter as balance-score; it already handles integer-only
# formats and observes score changes without replacing gameplay behavior.
score_source=Path(__file__).with_name('verify_balance_score.py').read_text()
code=score_source[score_source.index('def hash_text'):score_source.index('oracle.cpu.hook_add(UC_HOOK_CODE,score_output')]
code=code.replace("b'   total %d\\n']","b'   total %d\\n',b'New spin value %d:\\n']")
exec(compile(code,'<typed score diagnostic>','exec'))
oracle.cpu.hook_add(UC_HOOK_CODE,score_output,begin=0x401c30,end=0x401c30)
# A real event subscription invokes a terminating diagnostic QB handler.
spin_event=0x68b887bb;at=0x1662000;program=at+64;bucket=SYMBOLS+(spin_event&0xfff)*4
old=struct.unpack_from('<I',memory,bucket-BASE)[0]
put(at,'<BBHIIII',0,7,0,spin_event,0,program,old);put(bucket,'<I',at);put(at+32,'<5I',spin_event,program,1,0,0)
copy(program,b'\x01\x43'+struct.pack('<I',NATIVE)+b'\x01\x24');fields.add(program+2)
slot=CACHETABLE+32+(spin_event&3)*12;copy(at+80,memory[slot-BASE:slot-BASE+12]);put(slot,'<3I',spin_event,at+32,at+80);put(CACHETABLE+8,'<I',15)
SPIN_NOTIFY_PROGRAM=0x1662600
copy(SPIN_NOTIFY_PROGRAM,b'\x01\x43'+struct.pack('<I',NATIVE)+b'\x01\x24');fields.add(SPIN_NOTIFY_PROGRAM+2)
initial=bytes(memory);oracle.initial=initial
spin_branches={0x563f80:'negative_angle',0x563f96:'backside',0x564012:'half_cab',0x564044:'cabalerial',0x564075:'extended_cab',0x5640b8:'spin_diagnostic',0x5640fb:'ollie_reverse',0x56419a:'numeric_label',0x5641f2:'named_label',0x5641fa:'combo_update',0x564211:'recalculate',0x564230:'timed_spin',0x564246:'numeric_update',0x564256:'spin_event',0x564bfa:'guarded_spin',0x51cad0:'timed_store',0x419c80:'blend_node'}
branch_at.update(spin_branches)
for at in spin_branches:oracle.cpu.hook_add(UC_HOOK_CODE,branch,begin=at,end=at)
spin_base_case=case
def case(calls,p=(),changes=None,label='spin score'):
 oracle.cpu.reg_write(UC_X86_REG_FPSW,0);oracle.cpu.reg_write(UC_X86_REG_FPTAG,0xffff);oracle.cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
 stages=spin_base_case(calls,p,changes,label);previous=0
 for s in stages:
  for at,data in s['outputs']:
   if at<=GOBS and at+len(data)//2>=GOBS+4:
    current=int.from_bytes(bytes.fromhex(data)[GOBS-at:GOBS-at+4],'little');s['callbacks']+=current-previous;previous=current
 return stages
rng=random.Random(0x563f30)
values=[-math.inf,-5.,-0.,0.,.5,1.,5.,math.inf,math.nan]
for value in values:
 for low,high in [(-1,1),(1,-1),(0,-0.),(-math.inf,math.inf),(math.nan,1),(-1,math.nan),(math.nan,math.nan)]:
  case([call(0x4022c0,args=[bits(value),bits(low),bits(high)])],label='ordered clamp, reversed bounds and nonfinite operands')
for count in range(4):
 for mask in range(8):
  p=[patch(GACOMP+0x34,'<I',BLEND_NODES+3*128 if not count else BLEND_NODES)]
  for i in range(count):p += [patch(BLEND_NODES+i*128+0xc,'<I',BLEND_NODES+(i+1)*128 if i<count-1 else BLEND_NODES+3*128),patch(BLEND_NODES+i*128+0x54,'<I',(rng.getrandbits(32)&~0x20000000)|(((mask>>i)&1)<<29))]
  case([call(0x419c70,GACOMP)],p,label='empty or linked animation blend states and all-flipped flag')
def spin_config(slop=0,career=1,profile_mode=0x0a7be964,enabled=1,available=1,excluded=False):
 b=grounded_config();b.symbol(0x50c5cc2f,2,bits(slop));b.symbol(0xb23d1fb5,1,1)
 settings(b,career=career);b.header(PROFILE+0x5c,b.structure([] if profile_mode is None else [(0xa1dc81f9,13,profile_mode)]))
 b.extra += [patch(GTIMED+0x9f4,'<B',enabled),patch(GTIMED+0xa90,'<I',available),patch(GAME+0x378,'<I',0xe92ecafe if excluded else 0)]
 return b
for options in [{},{'career':0},{'profile_mode':0},{'profile_mode':None},{'enabled':0},{'available':0},{'excluded':True}]:
 for value in [0,0x80000000,0x43b40000,0x7f812345,0xffc12345,0xffffffff]:
  b=spin_config(**options);case([call(0x51cac0,GTIMED,[value]),call(0x51cac0,GTIMED,[value^0xffffffff])],b.patches(),label='all timed-spin enable predicates and raw word stores')
def spin_entries(name=b'Ollie',flags=0,count=1,current=0,spin=0,ollie=False,flipped=1,debug=0):
 p=[patch(SCORE+0x4c,'<5I',ITEMS,250,count,0,count),patch(SCORE+0x60,'<f',2),patch(SCORE+0x6c,'<I',current&0xffffffff),patch(SCORE+0x8c,'<B',debug)]
 for i in range(max(3,count)):
  at=TRICKS+i*256;p += [patch(ITEMS+i*4,'<I',at),patch(at,'<7I',1000+i*123,0,spin,0xdeadbeef,0x9b65d7b8 if ollie else 0x11111111,i%2,flags),raw(at+0x1c,name+b'\0'),raw(at+0x5c,b'Previous label\0')]
 p += [patch(BLEND_NODES+i*128+0x54,'<I',0x20000000 if flipped else 0) for i in range(3)]
 return p

def spin_parent(angle=180,p=(),b=None,at=0x563f30,repeat=None,attached=False,label='complete spin scoring'):
 b=b or spin_config();calls=body_setup()+setup()+numeric_setup()
 if attached:
  p=list(p)+[patch(BODIES+0x10,'<I',SCRIPTS),patch(EVENTS,'<IIBBHI',ENTRIES,1,1,0,0,0),patch(ENTRIES,'<5I',spin_event,spin_event,0,0,1)]
  script=bytearray(244)
  for off,v in [(0x2c,SCRIPTS+0x1c),(0x94,SCRIPTS+0x34),(0xe0,EVENTS),(0xec,0x6478e4)]:struct.pack_into('<I',script,off,v)
  p.append(raw(SCRIPTS,script));fields.add(SCRIPTS+0xec);calls.append(call(0x41d1d0,SCRIPTS+0xbc,[BODIES]))
  bucket,head,node=0x1662400,0x1662480,0x16624a0
  p += [patch(LISTENERS,'<6I',2,bucket,1,0xffffffff,0,0),raw(bucket,bytes(48)),patch(bucket+(spin_event&3)*12,'<3I',spin_event,head,0),patch(head,'<5I',0x6478dc,0xffffffff,0,node,node),patch(node,'<5I',0x6478d8,SCRIPTS,0,head,head)]
  fields.update([head,node])
 calls += [call(at,SCORE,[a]) for a in (repeat or [angle])]
 return case(calls,b.patches()+list(p),label=label)
for j,name in enumerate([b'Ollie',b'Fakie\\_Ollie',b'Half\\_Cab',b'Cabalerial']):
 for k,flags in enumerate([0,0x20,0x80,0xa0]):
  for n,count,current in [(0,1,0),(1,2,0),(2,2,1)]:
   for i,angle in enumerate([0,179,180,360,540,720]):
    sign=-1 if (i+j+k+n)%2 else 1;flipped=(i+k)%2
    p=spin_entries(name,flags,count,current,ollie=(i+j)%2==0,flipped=flipped,debug=i==2)
    spin_parent(sign*angle,p,label='spin thresholds, all Cab names, color priority, suffix and signed side')
for angles in [[180,360,540,720],[720,540,360,180],[180,-180,360,-360]]:
 spin_parent(p=spin_entries(b'Fakie\\_Ollie',ollie=True),repeat=angles,label='consecutive spin growth and prior Cab label mutation')
for slop in [-181,-1,0,1,10,179,180,1e30,math.nan]:
 for angle in [0,179,-179,0x7fffffff,-0x80000000]:
  spin_parent(angle,p=spin_entries(),b=spin_config(slop),label='slop conversion, signed division and wrapping angle arithmetic')
for at in [0x563f30,0x564be0]:
 for count,current,flags in [(0,0,0),(1,-1,0),(1,0,2),(1,0,0)]:
  spin_parent(p=spin_entries(flags=flags,count=count,current=current),at=at,label='score gates and guarded separator tail call')
for offset,value in [(SCORE+0x6c,1),(TRICKS+0x10,0x9b65d7b8),(TRICKS+0x18,0x80)]:
 p=spin_entries(count=2,debug=1)+[patch(DIAG+8,'<3I',offset,value,1)]
 spin_parent(p=p,label='spin diagnostic changes entry selection or format before live reads')
for target,value,width in [(0,0,0),(SCORE+0x14,777,4),(GTIMED+0xa58,0x12345678,4)]:
 p=spin_entries()+[patch(GOBS+4,'<4I',target,value,width,spin_event)]
 spin_parent(p=p,attached=True,label='actual original spin broadcast reaches cached QB and native observation')
 assert oracle.word(GOBS)>0
for i,notify in enumerate([NOTIFY,NUMERIC_NOTIFY]):
 for target,value,width in [(SCORE+0x6c,1,4),(SCORE+0x60,bits(3.5),4),(GTIMED+0x9f4,0,1)]:
  p=spin_entries(count=2)+[patch(META+i*256+12,'<I',SPIN_NOTIFY_PROGRAM),patch(META+i*256+36,'<I',SPIN_NOTIFY_PROGRAM),patch(GOBS+4,'<4I',target,value,width,notify)]
  spin_parent(p=p,label='UI notification QB changes entry, multiplier or timed gate during complete spin update')
  assert oracle.word(GOBS)==1
assert all(branches[name] for name in spin_branches.values()),{name:branches[name] for name in spin_branches.values()}
scope='Five complete original routines: spin scoring563f30, guarded scoring564be0, animation blend flip predicate419c70, timed-spin storage51cac0 and ordered clamp4022c0. Original score recalculation, Cab label changes, CRT sprintf, both UI updates, timed enable predicates and spin-event QB delivery execute unchanged. All names, color/suffix combinations, signed angles, slop conversion/wrap, repeated calls and callback-mutated entry state compare through full memory/globals/heap traces. Diagnostic formatting, terminal native QB and heap/Windows services are existing explicit boundaries; no scoring/gameplay helper is substituted. Valid linked sentinels, required registered skater/components/widgets, fitting strings and nonnegative score-table indices retain original contracts. Clamp numeric NaN returns classify as existing numeric oracle results. This does not recover the enclosing airborne spin update504060, startup, rendering or a playable level.'
fixture={'base':BASE,'memory':'spin-score-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'diagnostic_and_native_qb_callbacks','pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'pointer_globals':[index[0x6918ec+4*i] for i in range(8)],'scoped_event_services':{'symbol':'thug_event_services','pointer':SERVICES},'native_callbacks':[{'module':'balance-score-diagnostics.wasm','export':'fixture_balance_score_print','slots':[PRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]}
path=out/'spin-score-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
print('x86 spin scoring:',len(labels),sum(oracle.counts.values()),dict(branches),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_spin_score_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'branches':dict(branches),'heap_events':dict(oracle.heap_events),'native_qb_calls':dict(qb_calls),'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory'],out/'balance-score-diagnostics.wasm',out/'grounded-update-callbacks.wasm']},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(labels),sum(oracle.counts.values()))
