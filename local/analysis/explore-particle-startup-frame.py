"""Original-only first-frame exploration after all31 actual prop constructions."""
from pathlib import Path
source=Path('local/analysis/trace-rigidbody-initialize-training.py').read_text().split("f=json.loads((folder/'level-collision-load-fixtures.json')")[0]
assert '.write_text(' not in source
exec(compile(source,'<preserved isolated fullscene platform setup>','exec'))
if 0x684fc8 in index:defaults[index[0x684fc8]]=0x3f800000
else:glob('thug_frame_length_scale',0x684fc8,0x3f800000)
functions['0x430e20']={'name':'UNRECOVERED_rigidbody_update','this':True,'result':'void','cleanup':0}
functions['0x45d920']={'name':'thug_object_update_components','this':True,'result':'void','cleanup':0}
prior=json.loads((folder/'rigidbody-initialize-training-fixtures.json').read_text())['cases'][0]['steps']
objects=json.loads((folder/'rigidbody-initialize-training-original.json').read_text())['objects']
rigids=[c['address'] for o in objects for c in o['components'] if c['type']==0xffb39248]
# Extra original QB and original native bindings reside above all scene buffers.
PARTICLE,NSLOTS,UICTX,CUTSCENE,GETID=0x5f00000,0x5f10000,0x5f20000,0x5f21000,0x5f30000
particle_bytes=(folder/'particle-startup-archived.qb').read_bytes();particle_filename=PARTICLE+0x10000-256
memory[PARTICLE-BASE:PARTICLE-BASE+len(particle_bytes)]=particle_bytes
name=b'scripts\\fx\\particle_scripts.qb\0';memory[particle_filename-BASE:particle_filename-BASE+len(name)]=name
memory[UICTX-BASE:UICTX-BASE+0x6a4]=bytes(0x6a4);memory[CUTSCENE-BASE:CUTSCENE-BASE+0x100]=bytes(0x100)
glob('thug_ui_manager',0x701440,UICTX);glob('thug_cutscene_context_draft',0x6fa7c0,CUTSCENE)
metadata={e['name']:e for e in json.loads((folder/'script-bindings.json').read_text())}
for i,name in enumerate(['GlobalExists','MangleChecksums','ObjectExists','CutsceneDestroyListActive','StructureContains','CreateCompositeObject']):
 key=crc(name.encode());value=int(metadata[name]['address'],16);slot=NSLOTS+i*20;bucket=BUCKETS+(key&4095)*4
 put(slot,'<BBH4I',0,8,0,key,0,value,int.from_bytes(memory[bucket-BASE:bucket-BASE+4],'little'));put(bucket,'<I',slot)
put(GETID,'<6I',0x500eb224,0x57525413,0x460940,0,0,0)
slot=NSLOTS+6*20;bucket=BUCKETS+(0x500eb224&4095)*4
put(slot,'<BBH4I',0,9,0,0x500eb224,0,GETID,int.from_bytes(memory[bucket-BASE:bucket-BASE+4],'little'));put(bucket,'<I',slot)
# The particle's LockObj uses an already recovered real component factory.
component_count=int.from_bytes(memory[OBJECTS+0x44-BASE:OBJECTS+0x48-BASE],'little')
put(OBJECTS+0x44,'<I',component_count+2);put(OBJECTS+0x48+component_count*8,'<4I',0x5cb5cb7e,0x41ff20,0xc5bceb9e,0x41e1e0)
# LockObj initialization calls the already recovered manager priority virtual.
object_methods=int.from_bytes(memory[OBJECTS-BASE:OBJECTS-BASE+4],'little');put(object_methods+0x10,'<I',0x4619d0)
initial=bytes(memory);oracle.initial=initial
calls=[(int(s['fn'],16),s['this'],s['args']) for s in prior]
calls += [(0x472420,0,[particle_filename,PARTICLE,0,1,0])]
particle_settings=next(a for a in assets if a['member'].lower()=='levels\\tr\\tr_level_particle_data.qb')
calls += [(0x472420,0,[particle_settings['filename'],particle_settings['address'],0,1,0])]
calls += [(0x45d920,objects[7]['object'],[])]
frame_hits=Counter();call_entries=[];frame_started=False;frame_returns=0
def record(cpu,at,size,user):
 global frame_started
 if at in [0x430e20,0x45d920]:
  frame_started=True;call_entries.append([hex(at),hex(cpu.reg_read(UC_X86_REG_ECX))]);print('FRAME',call_entries[-1],flush=True)
 if frame_started:frame_hits[at]+=1
cpu.hook_add(UC_HOOK_CODE,record,begin=0x42bb00,end=0x431240)
cpu.hook_add(UC_HOOK_CODE,record,begin=0x45d920,end=0x45da21)
diagnostic_calls=[]
component_requests=[]
boundary=None;particle_native_calls=Counter()
def particle_entry(cpu,at,size,user):
 global boundary
 if not frame_started:return
 particle_native_calls[hex(at)]+=1
 if at==0x41e1e0:
  boundary={'address':hex(at),'component':'FlexParticle','type':'0xc5bceb9e','state':'stopped before the original factory; no replacement result'}
  cpu.emu_stop()
for entry in [0x44a380,0x44be40,0x462340,0x5ae000,0x44a940,0x449540,0x460940,0x41f520,0x4619d0,0x41e1e0]:cpu.hook_add(UC_HOOK_CODE,particle_entry,begin=entry,end=entry)
def requested_component(cpu,at,size,user):
 if frame_started:
  kind=oracle.word(cpu.reg_read(UC_X86_REG_ESP)+4);component_requests.append(hex(kind));print('COMPONENT',hex(kind),flush=True)
cpu.hook_add(UC_HOOK_CODE,requested_component,begin=0x45f2a0,end=0x45f2a0)
def diagnostic(cpu,at,size,user):
 if not frame_started:return
 sp=cpu.reg_read(UC_X86_REG_ESP)
 args=[oracle.word(sp+4+i*4) for i in range(8)]
 strings=[]
 for a in args:
  try:
   raw=bytes(cpu.mem_read(a,512)).split(b'\0')[0]
   strings.append(raw.decode('latin1') if raw and all(v in [9,10,13] or 32<=v<127 for v in raw) else None)
  except Exception:strings.append(None)
 item={'at':hex(at),'args':[hex(v) for v in args],'strings':strings}
 diagnostic_calls.append(item);print('DIAGNOSTIC',item,flush=True)
cpu.hook_add(UC_HOOK_CODE,diagnostic,begin=0x401c30,end=0x401c30)
read_players=[oracle.word(0x695150+i*12) for i in range(8)]
error=None;steps=[]
try:steps=oracle.case(calls)
except Exception as e:
 error=repr(e);print('CAUSE',repr(e.__cause__),flush=True);print('STOP',error,'EIP',hex(cpu.reg_read(UC_X86_REG_EIP)),flush=True)
report={'result':'original exploration complete' if error is None else 'original exploration stopped','error':error,'eip':hex(cpu.reg_read(UC_X86_REG_EIP)),'requested_calls':len(calls),'particle_asset_sha256':hashlib.sha256(particle_bytes).hexdigest(),'particle_settings':particle_settings,'returned_calls':len(steps),'frame_entries':call_entries,'original_initial_player_references':read_players,'executed_frame_instructions':{hex(a):n for a,n in sorted(frame_hits.items())},'diagnostic_calls':diagnostic_calls,'recent_blocks':list(recent_blocks),'playable':False,'scope':'Original isolated instruction execution only. Actual31prop startup followed by the archived particle-script load and barrel-fire owner update, with original native bindings, Obj_GetId descriptor and initialized empty UI selection/cutscene context. No constructed skater. No missing implementation or success is substituted.'}
report['component_requests']=component_requests
report['boundary']=boundary;report['particle_native_calls']=dict(particle_native_calls)
(folder/'particle-startup-frame-exploration.json').write_text(json.dumps(report,indent=2)+'\n')
print('SAVED',report['result'],'entries',len(call_entries),flush=True)
if error:raise SystemExit(1)
