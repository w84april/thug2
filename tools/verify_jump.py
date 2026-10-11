import hashlib,json,subprocess
"""Full original jump parent and command, with the established real engine graph."""
from pathlib import Path
prefix=Path('tools/verify_rail_entry_paths.py').read_text().split("for kind in ['point','natas','lip','grind']:enter(kind)")[0]
prefix=prefix.replace('rail-entry-paths.json','jump.json')
# Imported setup code may emit old intermediate evidence. Keep all existing
# artifacts immutable; this probe emits its own corpus after initialization.
original_write_bytes,original_write_text,original_unlink=Path.write_bytes,Path.write_text,Path.unlink
setup_writes=[]
def setup_write_bytes(path,data):setup_writes.append(str(path));return len(data)
def setup_write_text(path,data,*a,**k):setup_writes.append(str(path));return len(data)
def setup_unlink(path,*a,**k):setup_writes.append(str(path))
Path.write_bytes,Path.write_text,Path.unlink=setup_write_bytes,setup_write_text,setup_unlink
try:exec(compile(prefix,'<complete engine fixture initialization>','exec'))
finally:Path.write_bytes,Path.write_text,Path.unlink=original_write_bytes,original_write_text,original_unlink
folder=ROOT/'local/validation/collision';report_path=folder.parent/'jump.json'
for row in [(0x509450,'thug_skater_jump',1,'void',True,True,True),
            (0x509a40,'thug_skater_jump_command',2,'word',True,True,True)]:
 bind(*row);ROOTS.add(row[0]);oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=row[0],end=row[0])
exports.append([0x64bc10,'thug_jump_rail_events'])
function_exports.append([0x509a40,'thug_skater_jump_member'])
ranges={0x509450:1225,0x509a40:18};jump_hits=Counter();jump_case_hits=Counter()
def jump_trace(cpu,at,size,user):jump_hits[at]+=1;jump_case_hits[at]+=1
for at,size in ranges.items():
 oracle.cpu.hook_add(UC_HOOK_CODE,jump_trace,begin=at,end=at+size-1)
 oracle.cpu.hook_add(UC_HOOK_CODE,floor_observe,begin=at,end=at)
 oracle.cpu.hook_add(UC_HOOK_CODE,floor_observe,begin=at+size-3,end=at+size-3)
for at in [0x518d60,0x518ee0,0x5002d0,0x5092e0,0x460a20,0x434bf0]:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
JUMP_EVENT=0x8687163a
# Reuse the verified jump-sound graph in unused arena space. Only this synthetic
# graph is word-relocated; game assets and instructions remain untouched.
audio_folder=ROOT/'local/validation/collision'
audio=json.loads((audio_folder/'jump-sound-fixtures.json').read_text())
AUDIO,AUDIO_OLD=0x1b00000,audio['base']
assert memory[AUDIO-BASE:AUDIO-BASE+0x80000]==b'\xad'*0x80000
def audio_rebase(v):return v+AUDIO-AUDIO_OLD if AUDIO_OLD<=v<AUDIO_OLD+0x80000 else v
def audio_bytes(data):
 data=bytearray(data)
 for i in range(0,len(data)-3,4):
  v=struct.unpack_from('<I',data,i)[0]
  if audio_rebase(v)!=v:struct.pack_into('<I',data,i,audio_rebase(v))
 return data
am=audio_bytes((audio_folder/audio['memory']).read_bytes())
for at,data in audio['cases'][0]['patches']:
 offset=audio_rebase(at)-AUDIO;data=audio_bytes(bytes.fromhex(data));am[offset:offset+len(data)]=data
copy(AUDIO,am)
for i in range(4096):
 head=struct.unpack_from('<I',am,0x1000+i*4)[0]
 if not head:continue
 at=head
 while struct.unpack_from('<I',memory,at-BASE+16)[0]:at=struct.unpack_from('<I',memory,at-BASE+16)[0]
 old=struct.unpack_from('<I',memory,SYMBOLS-BASE+i*4)[0];put(at+16,'<I',old);put(SYMBOLS+i*4,'<I',head)
pointer_globals=set()
for j,(entry,value) in enumerate(zip(audio['globals'],audio['cases'][0]['globals'])):
 name,at,width,*offset=entry
 if name=='thug_script_symbol_buckets':continue
 if name=='thug_math_errno':at=TLS+8
 k=glob(name,at,audio_rebase(value),width,offset[0] if offset else 0)
 if j in audio['pointer_globals']:pointer_globals.add(k)
glob('thug_audio_master_volume',0x67db08,bits(100));glob('thug_audio_spatial_enabled',0x6f8a4c,0,1)
exports+=audio['pointer_exports'];fields.update(audio_rebase(x) for x in audio['pointer_fields'])
audio_setup=Path('tools/verify_air_wall.py').read_text()
audio_setup=audio_setup[audio_setup.index('AUDIO_CONTEXT='):audio_setup.index('for at in [0x444bb0,0x444480')]
exec(compile(audio_setup,'<established OS audio boundary>','exec'))
put(SOUND+0x24,'<f',1);put(SOUND2+0x24,'<f',.5)
BCAST_TABLE,BCAST_BUCKETS,BCAST_LIST,BCAST_NODES,BCAST_SCRIPTS,BCAST_EVENTS,BCAST_ENTRIES=0x16d3000,0x16d3040,0x16d3100,0x16d3140,0x16d3400,0x16d3800,0x16d3900
copy(BCAST_TABLE,bytes(0x1000))
fields.update([BCAST_LIST,BCAST_NODES,BCAST_NODES+20,BCAST_SCRIPTS+0xec,BCAST_SCRIPTS+0x100+0xec])
initial=bytes(memory);oracle.initial=initial
labels=[];oracle.cases.clear();oracle.counts.clear();oracle.coverage.clear()
summaries=[]
def jump_config(properties=(),limit=100,values=None,trigger=False):
 b=config_entry(trigger)
 b.symbol(0xf733c097,1,limit&0xffffffff);b.symbol(0x38505ef3,2,bits(15))
 stats={0x02ade3ad:500,0xc8815e43:200,0x9f79c8ea:700,0x91b07824:300,
        0x39766891:800,0x4cdb18cb:350,0x8851a76e:550,0x6e8efe38:220}
 stats.update(values or {})
 for name,value in stats.items():
  pair=b.alloc(struct.pack('<I2f',0,value,value));b.symbol(name,10,b.structure([(0,5,pair)]))
 program(b,JUMP_EVENT)
 return b,b.structure(list(properties))
def jump(mode=0,charge=50,limit=100,properties=(),extra=(),changes=None,repeat=1,command=False,label='jump',trigger=False,before_extra=()):
 b,params=jump_config(properties,limit,trigger=trigger)
 before,body=setup(False,0xbaf9b341)
 p=b.patches()+body+network()+[
  patch(SKATER_STATE+0x18,'<I',mode),patch(PHYS+0x378,'<I',charge&0xffffffff),
  patch(BODIES+0x4c,'<4f',10,20000,20,1),patch(BODIES+0x5c,'<4f',10,20000,20,1),
  patch(BODIES+0x6c,'<16f',*identity),patch(PHYS+0x18,'<16f',*identity),
  patch(BODIES+0xac,'<4f',30,-20,40,1),patch(PHYS+0x58,'<4f',0,1,0,0),
  patch(PHYS+0x68,'<4f',0,1,0,0),patch(PHYS+0x2ec,'<B',0),
  patch(PHYS+0x94,'<I',0),patch(PHYS+0x22c,'<I',0),patch(GATE+0x26,'<B',0)]
 p += [patch(SKATER_STATE+off,'<B',0) for off in [0x20,0x30,0x40,0x48,0x78,0xa8,0xb0]]
 p += [patch(INPUT+0x20+i*0x20,'<B',0) for i in range(16)]
 p += list(extra)
 calls=before+list(before_extra)+[call(0x509a40,PHYS,[params,0,QUERY]) if command else call(0x509450,PHYS,[params,QUERY])]*repeat
 jump_case_hits.clear();stages=compare(calls,p,{index[a]:v for a,v in (changes or {}).items()},label)
 previous_audio=0
 for step in stages:
  current=previous_audio
  for at,data in step['outputs']:
   if at<=AUDIO_CONTEXT<at+len(data)//2:current=int.from_bytes(bytes.fromhex(data)[AUDIO_CONTEXT-at:AUDIO_CONTEXT-at+4],'little')
   if len(data)==8 and int.from_bytes(bytes.fromhex(data),'little') in {entry[0] for entry in exports}:fields.add(at)
  step['callbacks']+=current-previous_audio;previous_audio=current
 summaries.append({'mode':mode,'result_mode':oracle.word(SKATER_STATE+0x18),'charge':oracle.word(PHYS+0x378),'velocity':list(struct.unpack('<4I',oracle.cpu.mem_read(BODIES+0xac,16))),'qb_callbacks':oracle.word(GOBS),'instructions':[f'{a:08x}' for a in sorted(jump_case_hits)]})
 if len(labels)%20==0:print('Jump cases',len(labels),flush=True)
 return stages
for mode in [0,1,2,3,4,5,6,0xffffffff]:
 for command in [False,True]:jump(mode=mode,command=command,label='all movement states and direct/script entry')
for charge in [-2147483648,-1,0,1,99,100,101,2147483647]:
 for limit in [1,100,16777217,2147483647]:jump(mode=1,charge=charge,limit=limit,label='signed charge clamp and real FILD ratio')
for mode,vert,surface,alternate in itertools.product([0,1,4],[0,1,255],[0,1],[0,1]):
 props=[(0,13,0xec6b7fc7)] if alternate else []
 jump(mode=mode,properties=props,extra=[patch(SKATER_STATE+0x30,'<B',vert),patch(SKATER_STATE+0x40,'<B',surface)],label='four real stat pairs and floor preparation')
for value in [-100.,-0.,0.,.125,100.,1e30]:
 for kind in [1,2]:
  jump(mode=1,properties=[(0xf0d90109,kind,int(value)&0xffffffff if kind==1 else bits(value))],label='Speed override through actual typed getter')
for vertical in [-100.,-0.,0.,100.]:
 for vert in [0,1,255]:
  jump(mode=1,extra=[patch(BODIES+0xac,'<4f',30,vertical,40,1),patch(SKATER_STATE+0x30,'<B',vert),patch(PHYS+0x58,'<4f',.25,.5,-.75,2)],label='normal versus vertical impulse and timed flag cleanup')
for tilt in [-1.,-.100001,-.1,-.099999,0.,1.]:
 basis=identity[:];basis[4:8]=[.2,tilt,.3,1]
 jump(mode=1,extra=[patch(BODIES+0x6c,'<16f',*basis)],label='tilted-up threshold, position nudge and asymmetric spills')
for mode,previous,left,right in itertools.product([0,1,4],[0,4],[0,1],[0,255]):
 jump(mode=mode,extra=[patch(PHYS+0x94,'<I',previous),patch(INPUT+0x60,'<B',left),patch(INPUT+0x80,'<B',right)],label='rail and previous-rail directional turn')
for disabled,blocked in itertools.product([0,1],[0,1,255]):
 jump(properties=[(0,13,0xe13620a8)] if disabled else [],extra=[patch(GATE+0x26,'<B',blocked)],command=True,label='sound suppression and blocked ground jump returns one')
for old,offset in itertools.product([0,1,255],[0,0x80000000,0xffffffff]):
 jump(extra=[patch(SKATER_STATE+0x20,'<B',old),patch(SKATER_STATE+0x48,'<B',old)],changes={0x696d60:offset},label='flag equality, timestamps and unsigned wrap')
for mode in [0,1,4]:jump(mode=mode,repeat=4,label='four retained jumps')
rail_patches=[]
for i in range(3):
 rail_patches += [patch(RAILS+i*0x54+0x20,'<4f',0,20000,i*100,1),patch(RAILS+i*0x54+0x40,'<5I',RAILS+(i+1)*0x54 if i<2 else 0,RAILS+(i-1)*0x54 if i else 0,4,0x1800+i,0)]
for mode,trigger,contact in itertools.product([0,1,4],[False,True],['none','live','dead']):
 extra=rail_patches+[patch(PHYS+0x2ec,'<B',1),patch(PHYS+0x22c,'<I',RAILS+0x54),patch(PHYS+0x230,'<I',WORLD),patch(GROUND_GATE+0x18,'<I',0 if contact=='none' else GCONTACT)]
 if contact=='dead':extra.append(patch(GCONTACT,'<I',0))
 prior_count=qb_calls[hex(0xa7662059)]
 jump(mode=mode,trigger=trigger,extra=extra,label=f'rail-off event with {contact} contact, trigger {trigger}')
 if trigger:assert qb_calls[hex(0xa7662059)]>prior_count,'rail trigger did not execute'
surface_patches=[patch(PHYS+0x1b0,'<I',0x1800),patch(PHYS+0x1c5,'<B',1)]
for command in [False,True]:
 for target,value,width in [(0,0,0),(GATE+0x26,1,1),(GATE+0x26,255,1),(PHYS+0x1528,SKATER_STATE2,4),(PHYS+0x1514,SOUND2,4),(PHYS+0x378,99,4),(BODIES+0xb0,bits(-300),4),(SKATER_STATE+0x30,1,1)]:
  prior_count=qb_calls[hex(0xa7662059)]
  jump(command=command,trigger=True,extra=surface_patches+[patch(GOBS+4,'<4I',target,value,width,0xa7662059)],label=f'ground contact QB callback mutates {target:x}')
  assert qb_calls[hex(0xa7662059)]>prior_count,'ground trigger did not execute'
for target,value,width in [(PHYS+0x1528,SKATER_STATE2,4),(PHYS+0x378,2,4),(GCONTACT,0,4),(BODIES+0xb0,bits(-999),4)]:
 prior_count=qb_calls[hex(0xa7662059)]
 extra=rail_patches+[patch(PHYS+0x2ec,'<B',1),patch(PHYS+0x22c,'<I',RAILS),patch(PHYS+0x230,'<I',WORLD),patch(GROUND_GATE+0x18,'<I',GCONTACT),patch(GOBS+4,'<4I',target,value,width,0xa7662059)]
 jump(mode=4,trigger=True,extra=extra,label=f'rail-off QB callback mutates {target:x}')
 assert qb_calls[hex(0xa7662059)]>prior_count,'rail mutation callback did not execute'
near_listener=[patch(BODIES+0x4c,'<4f',25,10,30,1),patch(BODIES+0x5c,'<4f',25,10,30,1)]
for mode,disabled in itertools.product([0,1,4],[False,True]):
 jump(mode=mode,properties=[(0,13,0xe13620a8)] if disabled else [],extra=near_listener,label='real jump audio enabled/suppressed')
 assert bool(oracle.word(AUDIO_CONTEXT))==(not disabled)
for mode,(target,value,width) in itertools.product([0,1,4],[(PHYS+0x1528,SKATER_STATE2,4),(PHYS+0x378,99,4),(BODIES+0xb0,bits(-123),4)]):
 jump(mode=mode,extra=near_listener+[patch(AUDIO_CONTEXT+40,'<4I',16,target,value,width)],label=f'audio device callback mutates {target:x}')
 assert oracle.word(AUDIO_CONTEXT)>0,'audio mutation did not execute'
for failure in [11,12,13,16]:
 jump(mode=1,extra=near_listener+[patch(AUDIO_CONTEXT+4,'<2I',failure,0x80004005)],label=f'jump audio device failure {failure}')
 assert oracle.word(AUDIO_CONTEXT)>0,'audio failure did not execute'
for mode,(surface_material,rail_material),sound_state in itertools.product([0,1,4],[(7,1),(1,7),(255,3)],[0,4]):
 jump(mode=mode,extra=near_listener+[patch(PHYS+0x1aa,'<B',surface_material),patch(SKATER_STATE+0xe1,'<B',rail_material),patch(SOUND+0x18,'<I',sound_state),patch(SOUND+0x1e,'<B',255)],label='mode-specific material and independent stored sound state')
for velocity in [(0.,0,0,1),(1e-40,0,0,1),(.1,.2,.3,1),(100,200,300,1),(1e15,-1e15,1e15,1),(1e30,0,0,1)]:
 jump(mode=1,extra=near_listener+[patch(BODIES+0xac,'<4f',*velocity)],label='speed normalization through real sound network and playback')
for count,command in itertools.product([1,2],[False,True]):
 for target,value,width in [(0,0,0),(PHYS+0x1528,SKATER_STATE2,4),(PHYS+0x4ec,123,4),(BODIES+0xb0,bits(-500),4)]:
  p=[patch(EM+16,'<I',BCAST_TABLE),patch(BCAST_TABLE,'<6I',2,BCAST_BUCKETS,1,0xffffffff,0,0),patch(BCAST_BUCKETS+(JUMP_EVENT&3)*12,'<3I',JUMP_EVENT,BCAST_LIST,0),patch(BCAST_LIST,'<5I',0x6478dc,0xffffffff,0,BCAST_NODES,BCAST_NODES+(count-1)*20),patch(GOBS+4,'<4I',target,value,width,JUMP_EVENT)]
  before=[]
  for i in range(count):
   s=BCAST_SCRIPTS+i*0x100;table=BCAST_EVENTS+i*16;entry=BCAST_ENTRIES+i*20;node=BCAST_NODES+i*20
   script=bytearray(244)
   for off,v in [(0x2c,s+0x1c),(0x94,s+0x34),(0xe0,table),(0xec,0x6478e4)]:struct.pack_into('<I',script,off,v)
   p += [raw(s,script),patch(table,'<IIBBHI',entry,1,1,0,0,0),patch(entry,'<5I',JUMP_EVENT,JUMP_EVENT,0,0,1),patch(node,'<5I',0x6478d8,s,0,node+20 if i+1<count else BCAST_LIST,node-20 if i else BCAST_LIST)]
   before.append(call(0x41d1d0,s+0xbc,[BODIES]))
  prior_count=qb_calls[hex(JUMP_EVENT)]
  jump(command=command,extra=p,before_extra=before,label=f'Jump broadcast to {count} actual QB listeners mutates {target:x}')
  assert qb_calls[hex(JUMP_EVENT)]-prior_count==count,'Jump broadcast listeners did not execute'
coverage={}
for at,size in ranges.items():
 rows=list(md.disasm(pe.get_data(at-0x400000,size),at));missing=[f'{i.address:08x}' for i in rows if not jump_hits[i.address]]
 coverage[f'{at:08x}']={'total':len(rows),'covered':len(rows)-len(missing),'missing':missing}
 assert not missing,(hex(at),missing)
assert qb_calls[hex(JUMP_EVENT)]==24 and qb_calls[hex(0xa7662059)]==29
assert callback_counts['play']>0
scope='Two complete original jump routines509450/509a40: signed charge clamp and real stat interpolation, Speed/NoSound/alternate parameters, normal/vertical impulse, tilted position correction, rail turning and events, floor preparation, live state reload, timestamps and final broadcast. All342 parent/wrapper instructions,253cases/792calls (262jump calls,530existing setup calls),53native QB callbacks plus actual sound/network/OS-device paths; exact memory/globals with no NaN allowances. Initialized components, positive configured charge limits, finite velocity/stat inputs, successful allocation and terminating fixture QB are contracts. Native terminal QB, allocator and OS audio boundaries are instrumented; the established unwritten packet padding byte is seeded zero. Generic fixture construction is not level startup. The optional host descriptor bridge is not exercised by this corpus. Integrated into the main module; original training remains unplayable.'
fixture={'base':BASE,'memory':'jump-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'native_qb_callbacks','pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'native_callbacks':[{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]}
fixture.update(pointer_globals=sorted(pointer_globals),callback_counter='native_qb_and_audio_callbacks')
fixture['native_callbacks'] += [dict(spec,module='wall-audio-callbacks.wasm') for spec in audio['native_callbacks']]
(folder/'jump-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')));(folder/'jump-memory.bin').write_bytes(initial)
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'counts':dict(oracle.counts),'instruction_coverage':coverage,'callee_coverage':dict(oracle.coverage),'native_qb_calls':dict(qb_calls),'setup_evidence_writes_suppressed':setup_writes,'paths':summaries,'scope':scope}
report.update(audio_device_calls=dict(callback_counts),audio_packet_padding_entries=audio_padding_entries,os_services=dict(os_calls))
report_path.write_text(json.dumps(report,indent=2)+'\n');print('Original jump',len(labels),sum(oracle.counts.values()),coverage,flush=True)

subprocess.run(['node',str(ROOT/'tools/verify_jump_wasm.mjs')],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [folder/'jump-fixtures.json',folder/fixture['memory']]}
(folder.parent/'jump.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS jump',len(fixture['cases']),sum(oracle.counts.values()))
