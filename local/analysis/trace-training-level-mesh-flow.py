"""Execute the first original training mesh with explicit CRT/GPU test ports."""
from pathlib import Path
setup=Path('local/analysis/trace-level-scene.py').read_text().split('\ndef observe(')[0]
exec(compile(setup,'<preserved original scene-file setup>','exec'))
cpu.mem_map(0x4000000,0x2400000)
crt_cursor=0x4000000;buffer_cursor=0x4c00000;buffers=[];crt_calls=Counter();buffer_calls=Counter();flow=[];mesh_entries=[]
BUFFER_CREATE,BUFFER_LOCK,BUFFER_UNLOCK=oracle.stop+0x200,oracle.stop+0x210,oracle.stop+0x220
BVT=BASE+0x3000
put(DVT+0x68,'<2I',BUFFER_CREATE,BUFFER_CREATE);put(BVT+0x2c,'<2I',BUFFER_LOCK,BUFFER_UNLOCK)
def crt(cpu,at,size,user):
 global crt_cursor
 sp=cpu.reg_read(UC_X86_REG_ESP);n=oracle.word(sp+4);result=crt_cursor;crt_cursor=(result+n+19)&~3
 assert crt_cursor<0x4c00000
 cpu.mem_write(result,b'\xa5'*n);crt_calls[n]+=1;finish(result)
cpu.hook_add(UC_HOOK_CODE,crt,begin=0x624031,end=0x624031)
def buffer_gpu(cpu,at,size,user):
 global buffer_cursor
 sp=cpu.reg_read(UC_X86_REG_ESP);arg=lambda i:oracle.word(sp+4+i*4)
 if at==BUFFER_CREATE:
  device,n,usage,format_,pool,out,shared=[arg(i) for i in range(7)];assert device==DEVICE
  p=buffer_cursor;buffer_cursor=(p+0x100+n+15)&~15;assert buffer_cursor<0x6000000
  oracle.setword(p,BVT);oracle.setword(p+4,n);oracle.setword(out,p);buffers.append({'buffer':hex(p),'bytes':n,'usage':usage,'format':format_});buffer_calls['create']+=1;finish(0,7)
 elif at==BUFFER_LOCK:
  p,offset,n,out,flags=[arg(i) for i in range(5)];assert offset+n<=oracle.word(p+4)
  oracle.setword(out,p+0x100+offset);buffer_calls['lock']+=1;finish(0,5)
 else:buffer_calls['unlock']+=1;finish(0,1)
for at in [BUFFER_CREATE,BUFFER_LOCK,BUFFER_UNLOCK]:cpu.hook_add(UC_HOOK_CODE,buffer_gpu,begin=at,end=at)
branch_hits=Counter();sectors=[];meshes=[]
def observe(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);branch_hits[hex(at)]+=1
 if at==0x4c6b10:
  sectors.append({'sector':hex(cpu.reg_read(UC_X86_REG_ECX)),'position':position})
  if len(sectors)%100==0:print('SECTORS',len(sectors),'MESHES',len(meshes),'POSITION',position,flush=True)
 if at==0x4d6100:
  meshes.append({'mesh':hex(cpu.reg_read(UC_X86_REG_ECX)),'args':[hex(oracle.word(sp+4+i*4)) for i in range(5)],'position':position})
 if at==0x4b52f0:meshes[-1]['end_position']=position
 if at in [0x4d4350,0x4d5940,0x4ddc00]:
  print('SPECIAL',hex(at),position,hex(oracle.word(0x7865cc)),hex(oracle.word(0x7865dc)),flush=True)
for at in [0x4de300,0x4c6130,0x4c6b10,0x4d6100,0x4d4350,0x4d5940,0x4d5c30,0x4da6d0,0x4ddc00,0x4b52f0,0x4d0d30]:cpu.hook_add(UC_HOOK_CODE,observe,begin=at,end=at)
oracle.scope_entries[MANAGER+0x200]=1;oracle.event_limit=80000;put(CONTEXT+12,'<I',0x6000000);oracle.initial=bytes(memory)
try:
 steps=oracle.case([(0x49f050,0,[0x12345678,TEXDATA,len(tex),0,0,0,0])]);dictionary=steps[-1]['result']
 sp=oracle.stack+0x18000;cpu.mem_write(sp,struct.pack('<7I',oracle.stop,NAME,dictionary,1,0,0,0));cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_FPCW,0x7f)
 cpu.emu_start(0x4b36d0,oracle.stop,count=100000000)
 assert cpu.reg_read(UC_X86_REG_EIP)==oracle.stop
 for m in meshes:
  at=int(m['mesh'],16);m['flags']=hex(oracle.word(at));m['vertices']=int.from_bytes(cpu.mem_read(at+0x22,2),'little');m['stride']=cpu.mem_read(at+0x18,1)[0];m['index_counts']=list(struct.unpack('<8H',cpu.mem_read(at+0x24,16)));m['formats']=[hex(oracle.word(at+0x38)),hex(oracle.word(at+0x3c))]
 report={'specimen_sha256':SHA256,'scene_sha256':hashlib.sha256(scn).hexdigest(),'texture_sha256':hashlib.sha256(tex).hexdigest(),'scene':hex(cpu.reg_read(UC_X86_REG_EAX)),'sectors':sectors,'meshes':meshes,'branch_hits':dict(branch_hits),'buffers':buffers,'buffer_calls':dict(buffer_calls),'crt_calls':dict(crt_calls),'file_calls':dict(io_calls),'position':position,'playable':False}
 (ROOT/'local/analysis/training-level-mesh-flow-trace.json').write_text(json.dumps(report,indent=2)+'\n');print('COMPLETE',len(sectors),len(meshes),position,dict(branch_hits),flush=True)
except Exception:
 print('STOP',hex(cpu.reg_read(UC_X86_REG_EIP)),'position',position,'sectors',len(sectors),'meshes',len(meshes),'branches',dict(branch_hits),'CRTEND',hex(crt_cursor),'GPUEND',hex(buffer_cursor),flush=True);raise
