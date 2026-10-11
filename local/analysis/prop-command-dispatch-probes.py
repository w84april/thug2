"""Test-only dispatch witnesses cover byte/word results and live next links."""
WCONTROL,WLOG,WCHECK,WMEMBER=BASE+0x1e0000,BASE+0x1e1000,oracle.stop+0x700,oracle.stop+0x710
def witness(cpu,at,size,user):
 kind=1 if at==WCHECK else 2;sp=cpu.reg_read(UC_X86_REG_ESP);p=cpu.reg_read(UC_X86_REG_ECX);i=oracle.word(WCONTROL);assert i<32
 args=[oracle.word(sp+4+j*4) for j in range(3 if kind==1 else 2)];row=[kind,p,*args] if kind==1 else [kind,p,0,*args]
 cpu.mem_write(WLOG+i*20,struct.pack('<5I',*row));oracle.setword(WCONTROL,i+1);result=oracle.word(WCONTROL+128+i*4)
 if oracle.word(WCONTROL+4)==kind and oracle.word(WCONTROL+8)==i:
  for j in [12,20]:
   target=oracle.word(WCONTROL+j)
   if target:oracle.setword(target,oracle.word(WCONTROL+j+4))
 cpu.reg_write(UC_X86_REG_EAX,result);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+(16 if kind==1 else 12))
for a,n in [(WCHECK,'checksum'),(WMEMBER,'member')]:
 oracle.cpu.hook_add(UC_HOOK_CODE,witness,begin=a,end=a)
 extra.setdefault('native_callbacks',[]).append({'module':'prop-command-callback.wasm','export':'fixture_prop_'+n,'original':a})
def wg():
 g=CommandGraph();g.image[WCONTROL-BASE:WCONTROL-BASE+0x2000]=bytes(0x2000);g.put(OBJ,'<I',0x647650);g.put(OBJ+0x100,'<I',0);return g
for results in [[0],[1],[2],[256],[0xffffffff],[2,0],[2,1],[0x10001,256,1],[2,2,2]]:
 for mutate in [False,True]:
  g=wg();s=g.structure([]);vt=g.alloc(52);g.put(vt+48,'<I',WCHECK);fields.add(vt+48)
  comps=[g.component(7,vt) for _ in results];g.put(OBJ+0x100,'<I',comps[0])
  for a,b in zip(comps,comps[1:]):g.put(a+16,'<I',b)
  g.put(WCONTROL+128,'<'+'I'*len(results),*results)
  if mutate:g.put(WCONTROL+4,'<6I',1,0,comps[0]+16,0,0,0)
  d=g.descriptor(0x12345678,0)
  run(g,[call(0x45d850,OBJ,[d,s,SCRIPTS])],f'checksum witness {results}/clear-next{mutate}')
for result in [0,1,2,255,256,257,0x12345600,0xffffffff]:
 for adjustment in [0,64,-64]:
  g=wg();s=g.structure([]);d=g.descriptor(0x12345678,WMEMBER,adjustment);g.put(WCONTROL+128,'<2I',result,result)
  run(g,[call(0x45d850,OBJ,[d,s,SCRIPTS]),call(0x472980,args=[d,s,OBJ,SCRIPTS])],f'direct member byte {result:x}/adjust{adjustment}')
# An exhausted selected structure pool is a valid branch: optional event
# parameters become null while the event itself is still installed.
g=CommandGraph();t=g.event_table([]);a=g.event_array([(1,2,7)]);pool=g.pool(16);g.put(pool+20,'<I',0)
run(g,[call(0x4601a0,t,[a,0])],'exhausted selected event-parameter pool',{0x6f361c:pool})
