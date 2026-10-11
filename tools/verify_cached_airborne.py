"""Exercise original airborne frames after the newly recovered cache builder."""
from pathlib import Path
prefix=Path('tools/verify_airborne_update.py').read_text().split('for dt in [0,1/60,1,-.1]:')[0]
prefix=prefix.replace("report_path=out.parent/'airborne-update.json'","report_path=out.parent/'cached-airborne.json'")
exec(compile(prefix,'<maintained airborne arena>','exec'))
saved=json.loads((out/'airborne-update-fixtures.json').read_text())
assert saved['globals']==globals_
functions.update(saved['functions'])
for at,name,result in [(0x500670,'thug_skater_build_collision_cache','void'),(0x40ab50,'thug_collision_cache_initialize','word')]:
 functions[hex(at)]={'name':name,'this':True,'result':result,'cleanup':0,'memory':False,'stack_args':[]}
for at in [0x500670,0x40ab50,0x40aba0]:
 if at not in observed:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at);observed.append(at)
labels=[]
for c,label in zip(saved['cases'],saved['case_labels']):
 if not label.startswith(('original training','floor flags/','floor collision QB','alternate transfer kills','wide wall','raised landing','no collision dt 0')):continue
 assert sum(s['fn']=='0x50ca00' for s in c['steps'])==1
 cpu=oracle.cpu;cpu.reg_write(UC_X86_REG_FPSW,0);cpu.reg_write(UC_X86_REG_FPTAG,0xffff);cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
 calls=[(0x40ab50,PHYS+0x4f4,[])]
 for s in c['steps']:
  if s['fn']=='0x50ca00':calls.append((0x500670,PHYS,[]))
  calls.append((int(s['fn'],16),s['this'],s['args']))
 stack_objects.clear();stages=oracle.case(calls,c['patches'],dict(enumerate(c['globals'])))
 if stack_objects:stages[-1]['stack_objects']=stack_objects[:]
 callbacks=audio_calls=0
 for step in stages:
  new_callbacks=callbacks;new_audio=audio_calls
  for at,data in step['outputs']:
   if int.from_bytes(bytes.fromhex(data),'little') in {e[0] for e in exports}:fields.add(at)
   if at==OBS:new_callbacks=int.from_bytes(bytes.fromhex(data),'little')
   if at==AUDIO_CONTEXT:new_audio=int.from_bytes(bytes.fromhex(data),'little')
  step['callbacks']=new_callbacks-callbacks+new_audio-audio_calls;callbacks=new_callbacks;audio_calls=new_audio
  step['float_fields']=[]
 labels.append('embedded cache + '+label)
 print('Cached frame',len(labels),label,flush=True)
fixture={**saved,'memory':'cached-airborne-memory.bin','functions':functions,'pointer_fields':sorted(fields),'cases':oracle.cases,'case_labels':labels,'scope':'Complete embedded collision-cache builder followed by the complete original airborne frame. Real training geometry, transfers, landing callbacks and moving-owner death; exact defined arena/global/heap/callback comparison. This is a dependency integration check, not the full dispatcher or a playable game.'}
(out/'cached-airborne-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(memory)
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'native_qb_calls':dict(qb_calls),'audio_callbacks':dict(callback_counts),'scope':fixture['scope']}
report_path.write_text(json.dumps(report,indent=2)+'\n')
subprocess.run(['node',str(ROOT/'tools/verify_cached_airborne_wasm.mjs'),str(out)],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [out/'cached-airborne-fixtures.json',out/fixture['memory']]}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS cached airborne',len(labels),dict(oracle.counts))
