"""Compare complete rail entry with the original executable instructions."""
from pathlib import Path
prefix=Path('tools/verify_pending_trick.py').read_text().split('for mode,mask in ')[0]
prefix=prefix.replace('pending-trick.json','rail-entry-edges.json')
exec(compile(prefix,'<complete trick runtime graph>','exec'))
report_path=out.parent/'rail-entry-edges.json'
WORLD,RAILS,POINT,GAP,COMPONENTS=0x16d0000,0x16d0100,0x16d1000,0x16f6000,0x16e0000
copy(WORLD,bytes(0x2000));put(WORLD,'<16f',*identity);put(WORLD+0x40,'<I',RAILS);put(WORLD+0x48,'<I',3)
copy(GAP,bytes(0x100));put(GAP+4,'<I',0x11b4c67f);put(GAP+12,'<I',BODIES);put(FLIP+16,'<I',GAP)
put(GAP+0x18,'<5I',0x64be88,0xffffffff,0,GAP+0x18,GAP+0x18)
put(GAP+0x2c,'<5I',0x64be8c,0xffffffff,0,GAP+0x2c,GAP+0x2c)
copy(COMPONENTS,bytes(0x200))
put(PHYS+0x1520,'<I',COMPONENTS)
base_balance=bytes(memory[GCONTEXT+0x24-BASE:GCONTEXT+0x7c-BASE])
for i in range(4):
 ptr=GCONTEXT+0x24+i*0x58;component=COMPONENTS+i*0x20
 copy(ptr,base_balance);put(ptr+12,'<I',component);put(component+0x18,'<I',SCORE)
fields.update([GAP,GAP+0x18,GAP+0x2c,WORLD+0x40])
exports += [[0x64be88,'thug_trick_primary_methods'],[0x64be8c,'thug_trick_secondary_methods']]
bind(0x50a770,'thug_skater_enter_rail',5,'void',True,True,True)
ROOTS.add(0x50a770)
pe=load();md=Cs(CS_ARCH_X86,CS_MODE_32);instructions=list(md.disasm(pe.get_data(0x10a770,6111),0x50a770))
for at in [0x50a770]+[i.address for i in instructions if i.mnemonic=='ret']:
 oracle.cpu.hook_add(UC_HOOK_CODE,floor_observe,begin=at,end=at)
entry_hits=Counter();case_hits=Counter();path_results=[];recent=[]
def entry_trace(cpu,at,size,user):entry_hits[at]+=1;case_hits[at]+=1;recent.append(at)
oracle.cpu.hook_add(UC_HOOK_CODE,entry_trace,begin=0x50a770,end=0x50bf4e)
diagnostics=[]
def diagnostic_call(cpu,at,size,user):
 # Adapt only the formatted-output boundary. The existing score-reset hook
 # accepts a different literal, so intercept these CALL instructions before it.
 sp=cpu.reg_read(UC_X86_REG_ESP);fmt=oracle.word(sp)
 expected={0x50b619:(0x6466b0,0x239c),0x50b64d:(0x64bd6c,0x239d)}[at]
 assert fmt==expected[0] and oracle.word(sp+4)==0x64bce0 and oracle.word(sp+8)==expected[1]
 text=pe.get_data(fmt-0x400000,100).split(b'\0')[0]
 if at==0x50b619:assert oracle.word(sp+12)==0x64bd90;args=['GRINDING FROM ACID DROP']
 else:args=list(struct.unpack('<3d',cpu.mem_read(sp+12,24)))
 diagnostics.append({'call':hex(at),'format':text.decode(),'arguments':args})
 n=oracle.word(DIAG);assert n<20;oracle.setword(DIAG,n+1);h=0
 for ch in text:h=(h*33+ch)&0xffffffff
 cpu.mem_write(DIAG+16+n*16,struct.pack('<4I',h,oracle.word(SCORE+0x1538),oracle.word(SCORE+0x54),oracle.word(SCORE+0x38)))
 if oracle.word(DIAG+8):oracle.setword(oracle.word(DIAG+8),oracle.word(DIAG+12))
 cpu.reg_write(UC_X86_REG_EAX,0xffffffff);cpu.reg_write(UC_X86_REG_EIP,at+5)
for at in [0x50b619,0x50b64d]:oracle.cpu.hook_add(UC_HOOK_CODE,diagnostic_call,begin=at,end=at)
initial=bytes(memory);oracle.initial=initial
labels=[];oracle.cases.clear();oracle.counts.clear();oracle.coverage.clear()
def config_entry(trigger=False):
 b=grounded_config()
 for key,value in {0xa477668:0.2,0xbb357ecb:30.,0xa3ef4833:100.,0x2b4645ad:100.,0x8157c5d9:45.,0xf3b6f95e:70.,0xe2a85fbb:20.,0x61079462:25.,0x457bb395:50.,0x9cd7ed5c:12.,0x31669752:8.,0xd0688d4e:0.5}.items():b.symbol(key,2,bits(value))
 pair=b.alloc(struct.pack('<I2f',0,100,100));b.symbol(0xcc5f87aa,10,b.structure([(0,5,pair)]))
 b.symbol(0x6775e538,10,b.structure([(0x896c8888,2,bits(50))]))
 entries=[b.structure([(0xa1dc81f9,13,0x1800+i)]+([(0x2ca8a299,13,0xa7662059)] if trigger else [])) for i in range(3)]
 b.extra.append(patch(NODE_TABLE+0x1000c,'<I',b.array(10,entries)))
 b.extra += [patch(NODE_TABLE+(0x1800+i)*4,'<Hh',0,i) for i in range(3)]
 variants=[b.array(13,[0x71230001]*16) for _ in range(9)];b.symbol(0x2ab3341d,12,b.array(12,variants))
 program(b,0x71230001);program(b,0x1647cf96)
 return b
def enter(kind='grind',velocity=(0,0,100,1),walking=0,force_no_lip=0,skip_score=False,extra=(),trigger=False,changes=None):
 case_hits.clear();b=config_entry(trigger)
 p=b.patches()+network()+[patch(PHYS+0x1518,'<I',TRICK),patch(PHYS+0x22c,'<I',RAILS if skip_score else 0),patch(PHYS+0x375,'<B',kind=='lip'),patch(PHYS+0x2ed,'<B',0),patch(PHYS+0x1504,'<I',0),patch(BODIES+0xac,'<4f',*velocity),patch(POINT,'<4f',0,20000,0,1),patch(PHYS+0x338,'<4f',10,20000,0,1)]
 p += [patch(SKATER_STATE+o,'<B',0) for o in [0x30,0x38,0x40,0x48,0x50,0x78,0x80,0xa8,0xb0]]
 p += [patch(INPUT+0x20+i*0x20,'<B',0) for i in range(16)]
 if kind=='natas':p += [patch(INPUT+0x100,'<B',1)]
 for i in range(3):
  p += [patch(RAILS+i*0x54+0x20,'<4f',0,20000,i*100,1),patch(RAILS+i*0x54+0x40,'<5I',RAILS+(i+1)*0x54 if kind not in ['point','natas'] and i<2 else 0,RAILS+(i-1)*0x54 if kind not in ['point','natas'] and i else 0,4,0x1800+i,0)]
 p += list(extra)
 try:stages=compare(body_setup()+[call(0x461a00,UM,[METER]),call(0x50a770,PHYS,[POINT,RAILS,WORLD,force_no_lip,walking,QUERY])],p,{index[k]:v for k,v in (changes or {}).items()},label=kind)
 except Exception:
  print('Parent tail',[hex(at) for at in recent[-12:]],'ECX',hex(oracle.cpu.reg_read(UC_X86_REG_ECX)),flush=True)
  raise
 path_results.append({'kind':kind,'velocity':list(velocity),'walking':walking,'no_lip':force_no_lip,'state':oracle.word(SKATER_STATE+0x18),'position':list(struct.unpack('<4f',oracle.cpu.mem_read(BODIES+0x4c,16))),'velocity_out':list(struct.unpack('<4f',oracle.cpu.mem_read(BODIES+0xac,16))),'hits':[hex(at) for at in sorted(case_hits)],'qb_callbacks':oracle.word(GOBS)})
 if len(path_results)<=4:print(kind,'state',path_results[-1]['state'],'instructions',len(case_hits),flush=True)
# Input aliases are valid readable vectors; the original writes may change them.
base_point=POINT
for target in [BODIES+0x4c, BODIES+0xac, PHYS+0x208, PHYS+0x218, PHYS+0x338]:
 POINT=target
 for kind in ['point','natas','lip','grind']:
  enter(kind)
  path_results[-1]['alias']=hex(target)
POINT=base_point
# Adjacent binary32 inputs around horizontal velocity thresholds and signed zero.
for raw_value in [0,0x80000000,1,0x80000001,0x3c23d709,0x3c23d70a,0x3c23d70b,0x411fffff,0x41200000,0x41200001]:
 speed=struct.unpack('<f',struct.pack('<I',raw_value))[0]
 for kind in ['point','grind']:
  for walking in [0,1]:
   enter(kind,(speed,1.0,speed,1.0),walking=walking)
   path_results[-1]['speed_bits']=hex(raw_value)
# Exercise live re-reads after original QB/native callbacks.
for kind in ['point','natas','lip','grind']:
 for target,value,width in [(RAILS+0x50,7,1),(SKATER_STATE+0x28,1,1),(PHYS+0x34c,1,1),(BODIES+0xac,bits(-25.0),4),(PHYS+0x22c,RAILS+0x54,4)]:
  enter(kind,trigger=True,extra=[patch(GOBS+4,'<4I',target,value,width,0)])
  path_results[-1]['callback_mutation']={'target':hex(target),'value':value,'width':width}
# The disassembly's x87 status-word tests deliberately include unordered cases.
original_config_entry=config_entry
parameter_overrides={}
def config_entry(trigger=False):
 b=original_config_entry(trigger)
 for key,value in parameter_overrides.items():b.symbol(key,2,value)
 return b
for name in [0x0a477668,0xd0688d4e]:
 for value in [0,0x80000000,0x7f800000,0xff800000,0x7fc12345,0xffc12345]:
  parameter_overrides={name:value}
  enter('natas' if name==0x0a477668 else 'grind')
  path_results[-1]['parameter_override']={'name':hex(name),'value_bits':hex(value)}
  if name==0x0a477668 and value in [0x7fc12345,0xffc12345]:
   assert '0x50aeaa' in path_results[-1]['hits'],'Unordered delay must take Natas path'
  if name==0xd0688d4e and value in [0x7fc12345,0xffc12345]:
   assert '0x50be61' in path_results[-1]['hits'],'Unordered tolerance must take side-dot path'
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(path_results),'counts':dict(oracle.counts),'instruction_coverage':{'total':len(instructions),'covered':sum(bool(entry_hits[i.address]) for i in instructions),'missing':[hex(i.address) for i in instructions if not entry_hits[i.address]]},'paths':path_results,'scope':'Original-only rail-entry numerical, alias and live-callback exploration; no recovered-C or browser claim.'}
report['scope']='Complete rail-entry0050a770: point kick, Natas, lip and grind paths with actual collision, score, material, sound, pending flips, QB scripts, events and network callees. Successful allocation and initialized host memory; original null assignment retained. Game integration remains unfinished.'
report['formatted_output_boundary']=diagnostics
fixture={'base':BASE,'memory':'rail-entry-edges-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':report['scope'],'callback_counter':'native_qb_callbacks','pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'native_callbacks':[{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]}
(out/'rail-entry-edges-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
(out/fixture['memory']).write_bytes(initial)
report_path.write_text(json.dumps(report,indent=2)+'\n')
print('Original rail entry',len(path_results),report['instruction_coverage']['covered'],'/',len(instructions))

subprocess.run(['node',str(ROOT/'tools/verify_rail_entry_edges_wasm.mjs')],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [out/'rail-entry-edges-fixtures.json',out/fixture['memory']]}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS rail entry',len(path_results),sum(oracle.counts.values()))
