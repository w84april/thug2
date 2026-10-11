"""Advance the original training fans through their real named rotation script."""
from pathlib import Path
source=Path('local/analysis/trace-particle-dispatch-training.py').read_text().split("scope='Actual complete31prop")[0]
addition='''
rotation_metadata=json.loads((folder/'motion-rotation-descriptors.json').read_text())
functions['0x640e30']={'name':'thug_motion_rotation_descriptors_initialize_draft','this':False,'result':'void','cleanup':0}
functions['0x423130']={'name':'thug_motion_rotation_descriptors_register_draft','this':False,'result':'void','cleanup':0,'memory':True}
for row in rotation_metadata['table']:
 a=row['address'];off=a-0x681eb8;exports.append([a,'thug_motion_rotation_descriptors_draft',off])
 for j,value in enumerate(row['words']):
  glob('thug_motion_rotation_descriptors_draft',a+4*j,value,offset=off+4*j)
  if j==2:pointer_globals.append(index[a+4*j])
 if row['member']:function_exports.append([row['member'],row['export']])
def prepared_motion_descriptor(cpu,at,size,user):
 value=cpu.reg_read(UC_X86_REG_EAX)
 if 0x681eb8<=value<0x682350 and (value-0x681eb8)%24==0:fields.add(cpu.reg_read(UC_X86_REG_ESI)-4)
cpu.hook_add(UC_HOOK_CODE,prepared_motion_descriptor,begin=0x46ffab,end=0x46ffab)
'''
needle='initial=bytes(memory);oracle.initial=initial';assert source.count(needle)==1
source=source.replace(needle,addition+'\n'+needle)
exec(compile(source,'<preserved training prefix plus Motion descriptor identities>','exec'))
assert len(steps)==52 and not boundary_hits
identities_set={e[0] for e in exports}|{e[0] for e in function_exports}
def advance(fn,this=0,args=()):
 before=bytes(cpu.mem_read(BASE,SIZE));sp=oracle.stack+0x18000
 cpu.mem_write(sp,struct.pack('<'+'I'*(len(args)+1),oracle.stop,*args));cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,this);cpu.reg_write(UC_X86_REG_FPCW,0x7f)
 cpu.emu_start(fn,oracle.stop,count=oracle.instruction_limit)
 assert cpu.reg_read(UC_X86_REG_EIP)==oracle.stop,(hex(fn),hex(cpu.reg_read(UC_X86_REG_EIP)),boundary_hits)
 after=bytes(cpu.mem_read(BASE,SIZE));outputs=[]
 for page in range(0,SIZE,4096):
  if before[page:page+4096]!=after[page:page+4096]:
   for i in range(page,min(page+4096,SIZE),4):
    if before[i:i+4]!=after[i:i+4]:outputs.append([BASE+i,after[i:i+4].hex()])
 values=[oracle.global_read(g) for g in globals_]
 outputs.append([MTABLE,struct.pack('<33I',*values[TABLE_INDEX:TABLE_INDEX+33]).hex()])
 for at,data in outputs:
  raw=bytes.fromhex(data)
  for i in range(0,len(raw),4):
   if int.from_bytes(raw[i:i+4],'little') in identities_set:fields.add(at+i)
 float_globals=[]
 for a in [0x6f2348,0x6f2568,*range(0x6f2370,0x6f24b0,16)]:
  if values[index[a]]&0xfe==4:float_globals.append(index[a+8])
 steps.append({'fn':hex(fn),'this':this,'args':list(args)+([0,0] if fn==0x45d920 else []),'result':None,'outputs':outputs,'globals':values,'callbacks':0,'expected_trap':False,'global_float_indices':float_globals})
advance(0x640e30);advance(0x423130)
fan_file=next(a for a in assets if a['member'].lower()=='levels\\tr\\tr_scripts.qb')
assert hashlib.sha256(bytes(cpu.mem_read(fan_file['address'],fan_file['size']))).hexdigest()=='21c9f93830a0a740bc41e13d81e4ec47adf8e7b33f52235a990ca45231807f87'
advance(0x472420,0,[fan_file['filename'],fan_file['address'],0,1,0])
# Select the actual already-created fan owners observed in the complete original
# manager traversal; validate their names and component links before execution.
discovery=json.loads((folder/'motion-rotation-scene-discovery.json').read_text());assert discovery['result']=='returned'
fans=[]
for entry in discovery['rotation_entries']:
 component=entry['component'];owner=oracle.word(component+12)
 assert oracle.word(component)==0x64620c and oracle.word(component+4)==0x0a015e17
 assert owner in discovery['object_update_entries']
 assert oracle.word(owner+0x14)==int(discovery['object_names'][discovery['object_update_entries'].index(owner)],16)
 fans.append({'owner':owner,'component':component,'name':hex(oracle.word(owner+0x14)),'matrices':[]})
commands=[]
def command(cpu,at,size,user):commands.append({'entry':hex(at),'component':cpu.reg_read(UC_X86_REG_ECX)})
for at in [0x424b90,0x424d50,0x424f50]:cpu.hook_add(UC_HOOK_CODE,command,begin=at,end=at)
for frame in range(4):
 for fan in fans:
  advance(0x45d920,fan['owner']);p=fan['component'];o=fan['owner']
  fan['matrices'].append(bytes(cpu.mem_read(o+0x6c,64)).hex())
  fan['flags']=oracle.word(p+0x18);fan['mode']=oracle.word(p+0x1c);fan['rates']=list(struct.unpack('<4f',cpu.mem_read(p+0x15c,16)))
assert len(commands)==2 and len(fans)==2 and all(len(set(f['matrices']))==4 for f in fans)
assert not boundary_hits and len(steps)==63
for i in range(oracle.word(CONTEXT+8)):
 for j in [4,5,6,7,9,10]:fields.add(LOG+i*48+j*4)
scope='Preserved complete31-prop training startup and selected barrel/fire updates, followed by full Motion descriptor initialization/registration and the actual archived TR_scripts.qb. Two original fan owners run TR_Fan01 through named Obj_Rotx and each complete four object updates with changing original matrices.63 complete calls, no interrupted calls. Complete arena/globals/heap/file/GPU witness storage compare; no rendered or complete scene-manager browser frame, controls or playability claimed.45 other registered Motion bodies remain explicit unavailable boundaries.'
fixture={**BASELINE,'memory_fixture':'particle-image-training-ports.wasm','native_callbacks':[{**c,'module':'particle-image-training-ports.wasm'} for c in BASELINE['native_callbacks']],'memory':'motion-rotation-training-memory.bin','functions':{k:v for k,v in functions.items() if k in {s['fn'] for s in steps}},'globals':globals_,'cases':oracle.cases,'case_labels':['actual training fans run original TR_Fan01 and rotate over four updates'],'pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'pointer_globals':pointer_globals,'boundary_address':BOUNDARY,'boundary_factory':0x430e20,'component_initializer_boundary':True,'boundary_after_script':True,'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'motion-rotation-training-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'calls':len(steps),'completed_calls':len(steps),'interrupted_calls':0,'fans':fans,'rotation_commands':commands,'archived_script':fan_file['member'],'script_sha256':'21c9f93830a0a740bc41e13d81e4ec47adf8e7b33f52235a990ca45231807f87','scope':scope,'playable':False}
(folder/'motion-rotation-training-original.json').write_text(json.dumps(report,indent=2)+'\n');print('SAVED63 completecalls, twofans, fourupdates each',flush=True)
