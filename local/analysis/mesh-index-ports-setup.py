"""Explicit isolated CRT arena and GPU index operations, shared by two probes."""
# Caller supplies CRTCTX,CRTBEGIN,CRTLIMIT,CRTLOG,INDEXCTL,INDEXLOG,INDEXVT,INDEXDEV.
put(CRTCTX,'<8I',CRTBEGIN,CRTLIMIT,0,CRTLOG,BASE,BASE+len(memory),0,0)
put(INDEXCTL,'<8I',0,0,0,0,0,1,1,0)
INDEX_CREATE,INDEX_LOCK,INDEX_UNLOCK=oracle.stop+0x350,oracle.stop+0x360,oracle.stop+0x370
put(DVT+0x6c,'<I',INDEX_CREATE);put(INDEXVT+0x2c,'<2I',INDEX_LOCK,INDEX_UNLOCK)
index_calls=Counter();crt_calls=Counter()
def mesh_crt(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);n=oracle.word(sp+4);result=oracle.word(CRTCTX)
 assert result+n+16<=oracle.word(CRTCTX+4)
 oracle.setword(CRTCTX,(result+n+19)&~3)
 if n:cpu.mem_write(result,b'\xa5'*n)
 index=oracle.word(CRTCTX+8);assert index<40;oracle.setword(CRTCTX+8,index+1)
 snapshot=list(struct.unpack('<4I',cpu.mem_read(result,16)))
 cpu.mem_write(CRTLOG+index*48,struct.pack('<12I',1,n,2,result,*snapshot,1,0,0,0));crt_calls[n]+=1
 cpu.reg_write(UC_X86_REG_EAX,result);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
oracle.cpu.hook_add(UC_HOOK_CODE,mesh_crt,begin=0x624031,end=0x624031)
def mesh_gpu(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);arg=lambda i:oracle.word(sp+4+i*4)
 op={INDEX_CREATE:1,INDEX_LOCK:2,INDEX_UNLOCK:3}[at];i=oracle.word(INDEXCTL);assert i<128
 oracle.setword(INDEXCTL,i+1);log=[op]+[0]*15
 if op==1:
  device,n,usage,format_,pool,out,shared=[arg(k) for k in range(7)];count=oracle.word(INDEXCTL+4);assert count<8 and n<=0x7000
  result=oracle.word(INDEXCTL+8);output=oracle.word(INDEXCTL+20);resource=INDEXDEV+count*0x8000
  oracle.setword(INDEXCTL+4,count+1);log[1:11]=[device,n,usage,format_,pool,shared,oracle.word(out),resource,result,output]
  if output:oracle.setword(resource,INDEXVT);oracle.setword(out,resource)
  argc=7
 elif op==2:
  device,offset,n,out,flags=[arg(k) for k in range(5)];result=oracle.word(INDEXCTL+12);output=oracle.word(INDEXCTL+24)
  data=(device+0x100+oracle.word(INDEXCTL+28))&0xffffffff;log[1:8]=[device,offset,n,flags,result,data,output]
  if output:oracle.setword(out,data)
  argc=5
 else:result=oracle.word(INDEXCTL+16);log[1:3]=[arg(0),result];argc=1
 cpu.mem_write(INDEXLOG+i*64,struct.pack('<16I',*log));index_calls[op]+=1
 cpu.reg_write(UC_X86_REG_EAX,result);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4+argc*4)
for at in [INDEX_CREATE,INDEX_LOCK,INDEX_UNLOCK]:oracle.cpu.hook_add(UC_HOOK_CODE,mesh_gpu,begin=at,end=at)
