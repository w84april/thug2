"""Original airtime threshold conversion and unsigned comparison members."""
from pathlib import Path
source=Path('local/analysis/probe-physics-parameter-flags.py').read_text().split('for at,offset,kind in ')[0]
source=source[:source.index('def run(')]
exec(compile(source,'<pinned minimal QB graph and emulator>','exec'))
members={0x4fbea0:'airtime_parameter',0x4fc880:'airtime_less_than_member',0x4fc8e0:'airtime_greater_than_member'}
functions={hex(at):{'name':'thug_physics_'+name+'_draft','this':True,'result':'word'} for at,name in members.items()}
cpu.hook_add(UC_HOOK_CODE,trace,begin=0x4fbea0,end=0x4fbf33)
for at in [0x4766d0,0x44ece0,0x5be970,0x6236fc]:cpu.hook_add(UC_HOOK_CODE,callee,begin=at,end=at)
globals_=[['thug_script_symbol_buckets',0x6f3624,4],['thug_frame_counter',0x7d1ec8,4],['thug_frame_rate',0x684fd0,4],['thug_timer_origin',0x696d64,4],['thug_timer_offset',0x696d60,4],['thug_time_scale',0x67d7c0,4]]
def bits(v):return struct.unpack('<I',struct.pack('<f',v))[0]
def run(addresses,g,params,extra=(),clock=(100,60.,0,0,1.),label='airtime'):
 patches=g.patches()+list(extra);expected=bytearray(initial)
 for at,data in patches:expected[at-BASE:at-BASE+len(data)//2]=bytes.fromhex(data)
 values=[BASE,clock[0],bits(clock[1]),clock[2],clock[3],bits(clock[4])]
 cpu.mem_write(BASE,bytes(expected))
 for (_,at,width),v in zip(globals_,values):cpu.mem_write(at,v.to_bytes(width,'little'))
 stages=[]
 for address in addresses:
  args=[params] if address==0x4fbea0 else [params,rng.randrange(2**32)]
  sp=STACK+0x10000;cpu.mem_write(sp,struct.pack('<'+'I'*(len(args)+1),STOP,*args))
  cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,PHYS);cpu.reg_write(UC_X86_REG_EAX,0xfeedfeed)
  cpu.reg_write(UC_X86_REG_FPCW,0x7f);cpu.reg_write(UC_X86_REG_FPSW,0);cpu.reg_write(UC_X86_REG_FPTAG,0xffff);cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
  guards={UC_X86_REG_EBX:0xeeeeffff,UC_X86_REG_ESI:0x1234ffff,UC_X86_REG_EDI:0xabcdefaa,UC_X86_REG_EBP:0xeebbcccc}
  for reg,value in guards.items():cpu.reg_write(reg,value)
  cpu.emu_start(address,STOP,count=100000)
  assert cpu.reg_read(UC_X86_REG_EIP)==STOP and cpu.reg_read(UC_X86_REG_ESP)==sp+4+4*len(args)
  assert all(cpu.reg_read(reg)==v for reg,v in guards.items())
  after=bytes(cpu.mem_read(BASE,SIZE));assert after==bytes(expected)
  observed=[int.from_bytes(cpu.mem_read(at,width),'little') for _,at,width in globals_];assert observed==values
  stages.append({'fn':hex(address),'this':PHYS,'args':args,'result':cpu.reg_read(UC_X86_REG_EAX),'outputs':[],'globals':observed,'callbacks':0})
  counts[functions[hex(address)]['name']]+=1
 cases.append({'patches':patches,'globals':values,'steps':stages});labels.append(label)
 return stages
flags=[[],[0xd029f619],[0x49e0ee96],[0x019176c5],[0x4a07c332],[0x019176c5,0x49e0ee96],[0x4a07c332,0xd029f619],[0xd029f619,0x49e0ee96,0x019176c5,0x4a07c332]]
float_bits=[0,0x80000000,1,0x80000001,0x3f7fffff,0x3f800000,0x3f800001,0xbf800000,0x4b7fffff,0x4b800000,0x4f000000,0x4f7fffff,0x5effffff,0x5f000000,0xdf000000,0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc12345,0x7f812345]+[rng.randrange(2**32) for _ in range(128)]
for fs,value in itertools.product(flags,float_bits):
 g=Graph();params=g.structure([(0,2,value)]+[(0,13,f) for f in fs])
 run([0x4fbea0]*2,g,params,label=f'helper float{value:x}, flags{fs}')
for fs,items in itertools.product(flags,[[],[(1,2,bits(3))],[(0,1,16777217)],[(0,1,0xffffffff)],[(0,4,0x12345678)],[(0,2,bits(1)),(0,2,bits(2))],[(0,13,0x71660044)]]):
 g=Graph();g.symbol(0x71660044,1,17);params=g.structure(items+[(0,13,f) for f in fs]);run([0x4fbea0]*2,g,params,label=f'helper typed values{items},flags{fs}')
for fs in flags:
 g=Graph();inside=g.structure([(0,2,bits(1.5))]+[(0,13,f) for f in fs]);g.symbol(0x71664400,10,inside);params=g.structure([(0,13,0x71664400)])
 run([0x4fbea0]*2,g,params,label='included helper parameters')
# Completed airborne intervals exercise unsigned wrap and equality on each side.
for mode,delta,threshold in itertools.product([0,3,4,5,6,0xffffffff],[0,1,15,16,17,999,1000,1001,0x7fffffff,0x80000000,0xffffffff],[0.,1.,16.,1000.,2147483648.,-1.]):
 g=Graph();params=g.structure([(0,2,bits(threshold))]);start=0xfffffff0;end=(start+delta)&0xffffffff
 run([0x4fc880,0x4fc8e0]*2,g,params,[patch(STATE+0x18,'<I',mode),patch(PHYS+0x380,'<2I',start,end)],label=f'completed state{mode:x},elapsed{delta:x},threshold{threshold}')
for mode,frame,origin,offset,rate,scale in itertools.product([1,2],[0,1,100,0x80000000,0xffffffff],[0,0xffffffff],[0,0x80000000,0xffffffff],[30.,60.,120.],[0.,.5,1.,2.]):
 g=Graph();params=g.structure([(0,2,bits(1.5)),(0,13,0xd029f619)])
 run([0x4fc880,0x4fc8e0],g,params,[patch(STATE+0x18,'<I',mode),patch(PHYS+0x380,'<2I',0xfffffff0,17)],(frame,rate,origin,offset,scale),label=f'live mode{mode},frame{frame:x},origin{origin:x},offset{offset:x},rate{rate},scale{scale}')
coverage={}
for at,n in [(0x4fbea0,148),(0x4fc880,85),(0x4fc8e0,85)]:
 ins=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(at-0x400000,n),at));assert ins[-1].mnemonic=='ret'
 missing=[hex(i.address) for i in ins if not hits[i.address]];assert not missing,(hex(at),missing)
 coverage[hex(at)]={'total':len(ins),'covered':len(ins),'missing':[]}
scope='Original4fbea0 airtime-unit conversion and4fc880/4fc8e0 unsigned predicates. Real QB numeric/flag lookups, seconds-before-frames priority, exact16ms frame unit, f32 bit patterns including NaNs/infinities, integer truncation, missing/types/aliases/inclusions, completed/live intervals, unsigned timer wrap, equality and state1/2 selection. Actual44ece0/5be970 timing and6236fc execute; no gameplay stubs. Full memory/globals, callee-saved registers and RET cleanup compare. Positive finite frame rates, finite time scales and mapped acyclic parameters are contracts; no x87 exception-status claim.'
fixture={'base':BASE,'memory':'physics-airtime-memory.bin','globals':globals_,'functions':functions,'float_fields':[],'cases':cases,'case_labels':labels,'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'physics-airtime-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(cases),'calls':sum(counts.values()),'counts':dict(counts),'instruction_coverage':coverage,'callee_calls':dict(callee_hits),'scope':scope}
(folder/'physics-airtime-original.json').write_text(json.dumps(report,indent=2)+'\n');print('Airtime',len(cases),sum(counts.values()),sum(v['covered'] for v in coverage.values()),flush=True)
