"""Compare the complete walking wallplant precheck, with real collision and QB execution."""
from pathlib import Path
source=Path('tools/verify_standard_wallplant.py').read_text().split('\nfor args in [(0,0,0)')[0]
source=source.replace('report_path.unlink(missing_ok=True)','pass # Preserve the pinned report')
source=source.replace('[0x64c3c8,0x64c3e8,0x64bd58],hex(fmt)','[0x64c3c8,0x64c3e8,0x64bd58,0x64c66c],hex(fmt)')
# Query services belong to the outer root, including during its nested wallplant.
source=source.replace('for at in [0x507500,0x508134]:','for at in []:')
exec(compile(source,'<standard wallplant prerequisites>','exec'))
local=ROOT/'local/analysis';P=BASE+0x1b0000;PARAM=BASE+0x1b2000;SYMS=BASE+0x1b2100;ENTRY=BASE+0x1b2300
zero(P,0x1900);zero(PARAM,0x1000)
put(P+12,'<I',BODY);put(P+0x24,'<4f',0,0,10,1);put(P+0x48,'<4f',0,0,-1,0)
put(P+0x1770,'<I',INPUT);put(P+0x1788,'<2I',STATE,PHYS)
put(INPUT+0x1c0,'<B',1);put(INPUT+0x40,'<2I',1,1000)
defaults[index[0x7d1ec8]]=0;defaults[index[0x696d60]]=1000
put(PARAM,'<2I',0,PARAM+16)
put(PARAM+16,'<4I',4,0x6da7f696,bits(30),PARAM+32)
put(PARAM+32,'<4I',4,0x99978d2b,bits(20),0)
for i,(name,kind,value) in enumerate([(0x6775e538,10,PARAM),(0x4c2b6df3,2,bits(0)),(0x7243098f,7,PROGRAM)]):
 at=SYMS+i*32;bucket=SYMBOLS+(name&0xfff)*4;old=struct.unpack_from('<I',memory,bucket-BASE)[0]
 put(at,'<5I',kind<<8,name,0,value,old);put(bucket,'<I',at);numeric[name]=at+12
put(CTABLE+8,'<I',2);put(CTABLE+32+(0x7243098f&3)*12,'<3I',0x7243098f,ENTRY,0)
put(ENTRY,'<5I',0x7243098f,PROGRAM,1,0,0)
functions.clear();functions['0x526e00']={'name':'thug_walk_air_wallplant_draft','this':True,'result':'void','cleanup':0,'stack_args':[],'memory':True}
exports.append([0x64c66c,'thug_walk_wallplant_text_draft'])
exports.extend([[0x6478e4,'thug_reference_target_methods'],[0x6478d8,'thug_script_listener_methods'],[0x6478dc,'thug_script_listener_list_methods']])
oracle.initial=bytes(memory);instructions=Counter();transitions=Counter();query_inputs=[];wallplant_args=[]
def trace(cpu,at,size,user):
 instructions[hex(at)]+=1
 if at==0x526e00:cpu.mem_write(0x691968,bytes(cpu.mem_read(QUERY,12)))
 if at in [0x526f6d,0x527070]:cpu.mem_write(QUERY,bytes(cpu.mem_read(0x691968,12)))
 if at in [0x526e4c,0x526f6e,0x527011,0x527026,0x52703f]:transitions[hex(at)]+=1
oracle.cpu.hook_add(UC_HOOK_CODE,trace,begin=0x526e00,end=0x527070)
from unicorn.x86_const import UC_X86_REG_ECX
def observe_calls(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);ret=oracle.word(sp)
 if at==0x4172f0 and ret==0x526f2d:
  probe=cpu.reg_read(UC_X86_REG_ECX)
  query_inputs.append({'segment':bytes(cpu.mem_read(probe,32)).hex(),'moving':oracle.word(sp+4),'farthest':oracle.word(sp+8)})
 if at==0x507500 and ret==0x527022:wallplant_args.append(list(struct.unpack('<3I',cpu.mem_read(sp+4,12))))
for at in [0x4172f0,0x507500]:oracle.cpu.hook_add(UC_HOOK_CODE,observe_calls,begin=at,end=at)
def attempt(label,p=(),changes=None,repeats=1):
 cpu=oracle.cpu;cpu.reg_write(UC_X86_REG_FPSW,0);cpu.reg_write(UC_X86_REG_FPTAG,0xffff);cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
 steps=oracle.case([(0x526e00,P,[QUERY,PRINT])]*repeats,p,changes);labels.append(label);previous=0
 for step in steps:
  callbacks=previous
  for at,data in step['outputs']:
   if int.from_bytes(bytes.fromhex(data),'little') in dict(exports):fields.add(at)
   if at==OBS:callbacks=int.from_bytes(bytes.fromhex(data),'little')
  step['callbacks']=callbacks-previous;previous=callbacks
 print('Walking wallplant',len(labels),label,'callbacks',previous,flush=True)
 return steps
attempt('qualifying wall and synchronous QB',repeats=2)
for held,jump in [(0,0),(0,1),(1,0),(255,2)]:attempt('input gates '+str((held,jump)),[patch(INPUT+0x1c0,'<B',held),patch(INPUT+0x40,'<B',jump)])
for age in [-1,0,1,29,30,31,32,0x7fffffff,0x80000000,0xffffffff]:
 attempt('unsigned input age '+str(age),[patch(INPUT+0x44,'<I',(1000-age)&0xffffffff)])
for height in [-200,-100,-1,0,30,99,100,101,200]:attempt('probe height '+str(height),[patch(PARAM+24,'<f',height)])
for radius in [-100,0,1,9.999999,10,10.000001,20,100]:attempt('probe reach '+str(radius),[patch(PARAM+40,'<f',radius)])
for position in [(0,0,0,1),(0,0,-1,1),(90,0,10,1),(-90,0,10,1),(0,0,10,2)]:attempt('probe origin '+str(position),[patch(P+0x24,'<4f',*position)])
for direction in [(0,0,1,0),(1,0,0,0),(.125,.25,-1,2),(0,0,0,1),(0,0,-.5,-1)]:attempt('probe direction '+str(direction),[patch(P+0x48,'<4f',*direction)])
attempt('empty collision scene',[patch(NODES+4,'<I',0xffffffff)])
for key in [0xd5349cc6,0x82135dd7,0x4c2b6df3]:
 for v in [-1,0,99,100,101,999,1000,1001,1e10,float('nan')]:attempt('gate '+hex(key)+' '+str(v),[patch(numeric[key],'<f',v)])
for at,value in [(PHYS+0x2ed,1),(PHYS+0x2db,1),(GATE+0x24,1),(NAME+0xa0b,0)]:attempt('underlying wallplant reject '+hex(at),[patch(at,'<B',value)])
for target,value,width in [(0,0,0),(P+12,BODY2,4),(INPUT+0x1c0,0,1),(PHYS+0x2db,1,1),(P+0x28,bits(222),4)]:
 attempt('script callback '+hex(target),[patch(OBS+4,'<3I',target,value,width)],repeats=2)
for age in [0,999,1000,1001,0x7fffffff,0x80000000,0xffffffff]:
 for at,key in [(PHYS+0x4e0,0x82135dd7),(P+0x1c,0x4c2b6df3)]:
  for threshold in [1000,2147483648.0]:
   attempt('wrapped cooldown '+str((hex(at),age,threshold)),[patch(at,'<I',(1000-age)&0xffffffff),patch(numeric[key],'<f',threshold)])
assert padding_entries==0
assert wallplant_args and all(a==[0,1,0] for a in wallplant_args)
assert query_inputs and all(q['moving']==q['farthest']==0 for q in query_inputs)
fixture={**{k:v for k,v in prior.items() if k not in ['cases','case_labels','branch_counts','zeroed_packet_padding_entries']},'memory':'walk-air-wallplant-memory.bin','globals':globals_,'functions':functions,'pointer_exports':exports,'pointer_fields':sorted(fields),'float_fields':[],
 'pointer_symbols':prior['pointer_symbols']+[[0x64bd58,'thug_late_wallplant_text','late wallplant\n'],[0x64c66c,'thug_walk_wallplant_text_draft','walking sticker slap...........\n']],
 'native_callbacks':prior['native_callbacks']+[{'module':'wallplant-callbacks.wasm','export':'fixture_wallplant_native','original':NATIVE}],
 'callback_counter':'native_qb_observer_callbacks','cases':oracle.cases,'case_labels':labels,
 'scope':'Complete walking wallplant precheck 526e00 through original input, timer, static collision, 507500 check-only and synchronous QB instructions. Native QB observer and terminal diagnostics/heap are explicit fixture boundaries; no gameplay callee is replaced, no padding is seeded, and every retained byte is compared exactly.'}
(local/fixture['memory']).write_bytes(memory);(local/'walk-air-wallplant-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
import capstone
code=list(capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32).disasm(bytes(oracle.cpu.mem_read(0x526e00,625)),0x526e00))
assert len(code)==163 and code[-1].address+code[-1].size==0x527071
report={'specimen_sha256':SHA256,'cases':len(oracle.cases),'calls':sum(oracle.counts.values()),'counts':dict(oracle.counts),'instructions':dict(instructions),'coverage':dict(oracle.coverage),'transitions':dict(transitions),'qb_calls':dict(qb_calls),'query_inputs':query_inputs,'wallplant_args':wallplant_args,'zeroed_packet_padding_entries':padding_entries,
 'instruction_coverage':{'0x526e00':{'covered':sum(bool(instructions[hex(i.address)]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not instructions[hex(i.address)]],'excluded':{}}}}
(local/'walk-air-wallplant-original.json').write_text(json.dumps(report,indent=2)+'\n')
(local/'walk-air-wallplant-routines.json').write_text(json.dumps({'0x526e00':{'bytes':625,'instructions':163,'name':'thug_walk_air_wallplant_draft'}},indent=2)+'\n')
