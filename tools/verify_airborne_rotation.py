"""Compare complete airborne input rotations with their original instruction paths."""
from pathlib import Path
task_source=Path(__file__).with_name('verify_grounded_update.py').read_text()
exec(compile(task_source.split('\nfor speed in [0,100]:')[0].replace("'grounded-update.json'","'airborne-rotation.json'"),'<airborne rotation prerequisites>','exec'))
NEW=[(0x420520,'thug_rotation_queue_add',7,'void',False,False,True),
 (0x420730,'thug_rotation_schedule',8,'void',True,True,True),
 (0x51ebd0,'thug_skater_commit_input_marks',1,'void',False,False,True),
 (0x51f9b0,'thug_skater_match_rotation_input',2,'byte',False,False,True),
 (0x4ffb90,'thug_skater_check_rotation_input',0,'void',True,True,True)]
for row in NEW:
 bind(*row);oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=row[0],end=row[0])
functions['0x420730']['float_args']=[0,1,2]
for at in [0x4549f0,0x532ea0,0x459e50,0x457eb0,0x454fa0,0x4555f0,0x543300,0x5434b0,0x53aea0,0x479070,0x46cc30,0x476950,0x476630,0x475790]:
 if at not in observe:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at);observe.append(at)
ROT,KEYS,AXIS,ROT_PROGRAM,CLIENT2,PEER2,LINK2=0x1661000,0x1661300,0x1661400,0x1661600,0x1664000,0x1666500,0x1666a00
copy(ROT,bytes(0x600));copy(CLIENT2,bytes(0x3000))
put(ROT+4,'<I',0x286a8d26);put(ROT+12,'<2I',BODIES,0)
put(GCONTEXT+16,'<I',NAME_CONTEXT);put(NAME_CONTEXT+4,'<I',0x270f56e1);put(NAME_CONTEXT+12,'<2I',BODIES,ROT)
put(BODIES+0x100,'<I',PHYS);put(KEYS,'<3I',0x11111111,0x22222222,0x33333333)
# A real cached bytecode handler reaches the existing terminal native observer.
name=0xd8fa65d7;at=ROT_PROGRAM;code=at+64;bucket=SYMBOLS+(name&0xfff)*4
old=struct.unpack_from('<I',memory,bucket-BASE)[0]
put(at,'<BBHIIII',0,7,0,name,0,code,old);put(bucket,'<I',at);put(at+32,'<5I',name,code,1,0,0)
copy(code,b'\x01\x43'+struct.pack('<I',NATIVE)+b'\x01\x24');fields.add(code+2)
slot=CACHETABLE+32+(name&3)*12;copy(at+80,memory[slot-BASE:slot-BASE+12]);put(slot,'<3I',name,at+32,at+80)
put(CACHETABLE+8,'<I',15)
initial=bytes(memory);oracle.initial=initial

# Only the original unwritten packet byte is seeded. No defined wire field,
# rotation record, game return or queue operation is replaced.
padding_entries=0;packets=[]
def rotation_trace(cpu,at,size,user):
 global padding_entries
 sp=cpu.reg_read(UC_X86_REG_ESP)
 if at==0x420730:cpu.mem_write(sp-0x21,b'\0');padding_entries+=1
 elif at==0x4208ba:
  spec=oracle.word(sp);assert bytes(cpu.mem_read(spec,1))==b'\x76'
  assert int.from_bytes(cpu.mem_read(spec+2,2),'little')==16
  packets.append(bytes(cpu.mem_read(oracle.word(spec+4),16)).hex())
 elif at==0x4555f0:fields.add(cpu.reg_read(UC_X86_REG_ECX))
for at in [0x420730,0x4208ba,0x4555f0]:oracle.cpu.hook_add(UC_HOOK_CODE,rotation_trace,begin=at,end=at)
rotation_branches={0x420543:'axis_insert',0x42053e:'axis_full',0x42079e:'schedule_x',0x4207d3:'schedule_y',0x420808:'schedule_z',0x42083c:'schedule_local_player',0x4208ba:'schedule_packet',0x51fa65:'match_success',0x51fa99:'match_second_stage',0x51fa33:'match_final_stage',0x51fb7b:'match_failure',0x4ffbda:'parent_search',0x4ffc80:'parent_next',0x4ffc91:'parent_match',0x4ffd02:'parent_x',0x4ffd33:'parent_half_turn',0x4ffd53:'parent_y',0x4ffd8d:'parent_z',0x4ffd9e:'parent_handler'}
branch_at.update(rotation_branches)
for at in rotation_branches:oracle.cpu.hook_add(UC_HOOK_CODE,branch,begin=at,end=at)
rotation_base_case=case
def case(calls,p=(),changes=None,label='airborne rotation',floats=()):
 oracle.cpu.reg_write(UC_X86_REG_FPSW,0);oracle.cpu.reg_write(UC_X86_REG_FPTAG,0xffff);oracle.cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
 stages=rotation_base_case(calls,p,changes,label);previous=0
 for s in stages:
  s['float_fields']=list(floats)
  for at,data in s['outputs']:
   if at<=GOBS and at+len(data)//2>=GOBS+4:
    current=int.from_bytes(bytes.fromhex(data)[GOBS-at:GOBS-at+4],'little');s['callbacks']+=current-previous;previous=current
 return stages
rng=random.Random(0x4ffb90)

# Every occupancy combination, nonsemantic bytes and both flag input bits.
for occupancy in range(64):
 p=[raw(AXIS,bytes(rng.getrandbits(8) for _ in range(0x94)))]
 p += [patch(AXIS+j*24+20,'<B',(rng.getrandbits(8)&0xfe)|((occupancy>>j)&1)) for j in range(6)]
 args=[0x7f812345,0xffffffff,0x80000000,0xffc12345,0xaabbccdd,occupancy,occupancy>>1]
 case([call(0x420520,AXIS,args),call(0x420520,AXIS,args)],p,label=f'axis queue occupancy {occupancy:02x}, raw float bits and padding')
case([call(0x420520,AXIS,[1,2,3,4,5,0xffffffff,0x100]) for _ in range(8)],[raw(AXIS,bytes(0x94))],label='fill queue then retain full queue state')

global_at={g[0]:g[1] for g in globals_};K=[0x11111111,0x22222222,0x33333333]
def history(rows,head=50,count=None):
 p=[patch(NAME_CONTEXT+0x998,'<2H',len(rows) if count is None else count,head)]
 for i,row in enumerate(rows):
  age,kind,key,mask,consumed=row
  p.append(patch(NAME_CONTEXT+0x38+((head-i)%100)*24,'<4IB3sI',(1666-age)&0xffffffff,kind,key,0xaabbcc00+i,consumed,b'xyz',mask))
 return p
for count in [0,1,2,99,100]:
 for head in [0,1,50,99]:
  for mask in [0,0x100,0xffffffff]:
   rows=[(i,1,K[i%3],(i<<16)|i,[0,1,255][i%3]) for i in range(count)]
   case([call(0x51ebd0,NAME_CONTEXT,[mask]),call(0x51ebd0,NAME_CONTEXT,[mask^0xffffffff])],history(rows,head),label='commit marked history twice over full or partial ring')

def row(key,kind=1,mask=0,age=0,marked=0):return (age,kind,key,mask,marked)
patterns=[[],[row(K[1])],[row(K[1]),row(K[0])],[row(K[1]),row(K[0]),row(K[2])],
 [row(K[1]),row(77),row(K[0]),row(K[2])],
 [row(K[1]),row(77),row(88),row(K[0]),row(K[2])],
 [row(K[1]),row(K[2],2),row(K[0]),row(K[2])],
 [row(K[1]),row(K[0]),row(K[2],2)],
 [row(K[1]),row(K[0]),row(77,2)],
 [row(K[1]),row(K[0]),row(K[2],mask=0x100)],
 [row(K[1],mask=0x100),row(K[0]),row(K[2])],
 [row(K[1]),row(K[0],mask=0x100),row(K[2])],
 [row(77,marked=255),row(K[1]),row(K[0]),row(K[2])],
 [row(K[1]),row(K[0]),row(77),row(K[2])]]
for head in [0,1,2,50,99]:
 for override in [0,1,0x100,0xff]:
  for i,rows in enumerate(patterns):
   case([call(0x51f9b0,NAME_CONTEXT,[KEYS,override])],history(rows,head),label=f'three-key pattern {i}, ring head {head}, override {override}')
for age in [0,999,1000,1001,0x80000000,0xffffffff]:
 for position in range(3):
  rows=[row(K[1]),row(K[0]),row(K[2])];old=rows[position];rows[position]=(age,*old[1:])
  case([call(0x51f9b0,NAME_CONTEXT,[KEYS,1])],history(rows),label='input age cutoff and unsigned wrap')
for now in [0,1,0x7fffffff,0x80000000,0xffffffff]:
 changes={global_at['thug_frame_rate']:bits(1000),global_at['thug_frame_counter']:now}
 for age in [0,999,1000]:
  p=history([row(K[1]),row(K[0]),row(K[2])]);p += [patch(NAME_CONTEXT+0x38+(50-i)*24,'<I',(now-age)&0xffffffff) for i in range(3)]
  case([call(0x51f9b0,NAME_CONTEXT,[KEYS,0])],p,changes,label='input absolute frame clock high bits and wrapped timestamps')
# Success copies checksum words forwards even when the source aliases its output.
for offset in [-4,0,4]:
 ptr=NAME_CONTEXT+0x99c+offset
 p=history([row(K[1]),row(K[0]),row(K[2])])+[patch(ptr,'<3I',*K)]
 case([call(0x51f9b0,NAME_CONTEXT,[ptr,0])],p,label='matched checksum output aliases checksum input')

def network(player='local',slot=0,peer=1,active=True):
 p=online(active)+player_patches(0 if player=='missing' else 1)
 p += [patch(PLAYERS+0x1d0,'<I',{'local':1,'remote':0,'hidden':5,'missing':1}[player]),patch(BODIES+0x2bc,'<I',slot),patch(PEERS+0x60,'<I',peer)]
 if slot:
  p += [patch(NETWORK+8+slot*4,'<I',CLIENT2),patch(CLIENT2+8,'<I',12),queue_node(CLIENT2+0x1e8c,prev=LINK2,next_=LINK2),queue_node(LINK2,0x647578,PEER2,CLIENT2+0x1e8c,CLIENT2+0x1e8c),patch(PEER2+0x3c,'<I',9),patch(PEER2+0x60,'<I',peer)]
  for i in range(3):p.append(queue_node(PEER2+i*20,0x6474cc+i*4))
 return p
def schedule(duration=50,start=0,end=180,mode=0,flag=1,axes=(1,1,1)):
 return call(0x420730,ROT,[bits(duration),bits(start),bits(end),mode,flag,*axes])
for mask in range(8):
 for player in ['missing','remote','hidden','local']:
  for full in [False,True]:
   p=network(player,slot=mask%2)+[patch(ROT+0x38+axis*0x94+j*24+20,'<B',int(full)) for axis in range(3) for j in range(6)]
   case(body_setup()+[schedule(axes=tuple((mask>>j)&1 for j in range(3)))],p,label=f'schedule selection {mask}, player {player}, queue full {full}')
for flag in [0,1,2,3,0x100,0xffffffff]:
 for selector in [0,1,0x100,0x101,0xffffffff]:
  case(body_setup()+[schedule(mode=0x98765432,flag=flag,axes=(selector,selector,selector))],network(),label='schedule byte selectors, raw mode and wire flag')
for duration,start,end in [(0,-0.,0),(1/60,-180,180),(1e-30,1e-40,2e-40),(-1,-32769,65537),(1e30,-1e30,1e30),(1,3e38,-3e38),(math.inf,0,1),(math.nan,1,2),(1,math.nan,2),(1,math.inf,math.inf)]:
 floats=[ROT+0x38+j*0x94+k for j in range(3) for k in [0,12]]
 case(body_setup()+[schedule(duration,start,end)],network(),label='rotation numeric boundaries and packet conversion',floats=floats)
for peer in [0,1,8]:
 for active in [False,True]:
  case(body_setup()+[schedule() for _ in range(8)],network(peer=peer,active=active),label='consecutive schedule queues and eligible peer without active-network gate')
case(body_setup()+[schedule()],network()+[queue_node(CLIENT+0x1e8c)],label='local rotation without network peers')

def rotation_config(entries):
 b=Build();items=[]
 for first,second,axes in entries:
  members=[(0x24715af5,13,first),(0xbd780b4f,13,second)]
  members += [(key,1,value&0xffffffff) for key,value in zip([0x0affd09d,0x7df8e00b,0xe4f1b1b1],axes) if value is not None]
  items.append(b.structure(members))
 b.symbol(0xb75d73e5,12,b.array(10,items));return b
def parent(entries=None,rows=None,p=(),head=50,repeat=1,label='complete rotation parent'):
 entries=entries if entries is not None else [(K[0],K[1],(90,180,-270))]
 rows=rows if rows is not None else [row(K[1]),row(K[0]),row(0x2b489a86)]
 b=rotation_config(entries)
 return case(body_setup()+[call(0x4ffb90,PHYS) for _ in range(repeat)],b.patches()+history(rows,head)+[patch(INPUT+0x160,'<B',1)]+list(p),label=label)
for at in [SKATER_STATE+0x70,PHYS+0x2db]:parent(p=[patch(at,'<B',255)],label='parent early state or used-input gate')
parent(p=[patch(INPUT+0x160,'<B',0)],label='parent requires held rotation input')
parent(entries=[],label='parent empty configured array')
for held in [0,1,255]:
 for override in [0,1,255]:
  for head in [0,1,50]:
   for final in [0x2b489a86,0x321c9756,77]:
    p=[patch(INPUT+0x160,'<B',held),patch(INPUT+0x180,'<B',1),patch(PHYS+0x2e4,'<B',override)]
    parent(rows=[row(K[1]),row(K[0]),row(final)],p=p,head=head,repeat=2,label='parent held-button precedence, override, wrapped history and repeat gate')
for axes in [(None,None,None),(0,0,0),(90,0,0),(0,180,0),(0,-180,0),(0,181,0),(0,0,-270),(90,180,-270),(0x7fffffff,-0x80000000,0xffffff)]:
 for local in [False,True]:
  entries=[(0xdead,K[1],(1,1,1)),(K[0],K[1],axes),(K[0],K[1],(-1,-1,-1))]
  parent(entries,p=network('local' if local else 'remote'),label='ordered array first match, failed marks, optional axes and full QB handler')
for target,value,width in [(0,0,0),(PHYS+0x2db,0,1),(PHYS+0x2e0,bits(123),4),(PHYS+0x3a4,0,1)]:
 p=[patch(GOBS+4,'<4I',target,value,width,0xd8fa65d7)]
 parent(p=p,repeat=2,label='actual synchronous QB mutation after rotation scheduling')

# Parse the shipped AerialFlips array with the original parser, then run the
# complete input parent against that allocated graph. The QB handler remains
# the explicit diagnostic handler above; this is not complete trick display.
import ctypes
from prx import entries,decoded_size
archive_path=ROOT/'local/game-files/Game/Data/pre/qb_scripts.prx';archive_bytes=archive_path.read_bytes()
archived=next(e for e in entries(archive_bytes) if e.name=='scripts\\game\\skater\\airtricks.qb')
assert archived.compressed and decoded_size(archived.payload)==archived.size
lzss=ctypes.CDLL(str(ROOT/'local/validation/lzss.dylib'));decode=lzss.thug_lzss_decode_unchecked
decode.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_void_p,ctypes.c_uint32];decode.restype=ctypes.c_void_p
dictionary=ctypes.create_string_buffer(4096);decoded=ctypes.create_string_buffer(archived.size)
assert decode(dictionary,archived.payload,decoded,len(archived.payload))-ctypes.addressof(decoded)==archived.size
airtricks=decoded.raw
assert hashlib.sha256(airtricks).hexdigest()=='f0f8542748bd35b878edd75eae73294ac4ece09abdc39bf30b1abbb25afaabb5'
airtricks_path=ROOT/'local/game-files/Game/Data/scripts/game/skater/airtricks.qb'
loose_airtricks=airtricks_path.read_bytes()
array_name=b'\x16'+struct.pack('<I',0xb75d73e5)
array_start=airtricks.index(array_name)+7
array_end=airtricks.index(b'\x23\x16'+struct.pack('<I',0xd8fa65d7),array_start)
assert airtricks[array_start]==5 and airtricks[array_end-2:array_end]==b'\x06\x01'
shipped_array=airtricks[array_start:array_end]
assert loose_airtricks!=airtricks and loose_airtricks[array_start:array_end]==shipped_array
ROT_ARRAY,ROT_CODE=0x1661a00,0x1661c00
actual_flips=[(0xe3006fc4,0x0affd09d,-360),(0xbc6b118f,0x0affd09d,360),(0x85981897,0xe4f1b1b1,-360),(0x4b358aeb,0xe4f1b1b1,360)]
for key,angle_name,angle in actual_flips:
 for held in [0,1]:
  for local in [False,True]:
   b=Build();b.symbol(0xb75d73e5,12,ROT_ARRAY)
   rows=[row(key),row(key),row(0x2b489a86 if held else 0x321c9756)]
   p=b.patches()+history(rows)+network('local' if local else 'remote')+[raw(ROT_ARRAY,bytes(12)),raw(ROT_CODE,shipped_array),patch(INPUT+0x160,'<B',held),patch(INPUT+0x180,'<B',1)]
   case(body_setup()+[call(0x471b00,args=[ROT_ARRAY,ROT_CODE,0]),call(0x4ffb90,PHYS)],p,label=f'shipped AerialFlips key {key:x} angle {angle} held {held} local {local}')
   assert oracle.word(ROT_ARRAY+4)==4
   assert bytes(oracle.cpu.mem_read(PHYS+0x2db,1))==b'\x01'
   axis=0 if angle_name==0x0affd09d else 2
   assert oracle.word(ROT+0x38+axis*0x94+12)==bits(angle)

assert all(branches[name] for name in rotation_branches.values())
assert packets and qb_calls['0xd8fa65d7']
scope='Five complete original routines: airborne rotation input 4ffb90, rotation scheduling 420730, six-record axis enqueue 420520, history-mark commit 51ebd0 and three-key matching 51f9b0. Full input history, timer cutoff/wrap, physical-index ring quirk, failed marks, array order, axis queue saturation, local-player lookup, original network payload/queue execution and synchronous QB/native mutation are compared. The original parser also loads all four archived AerialFlips definitions from qb_scripts.prx/airtricks.qb for sixteen complete parent cases. The loose script differs but its flip table is identical. Their display handler is the explicit diagnostic QB fixture, not recovered complete trick display. Only the unwritten final packet byte is seeded/defined as zero. Typed arithmetic NaNs use declared output classification; raw queue words and padding compare exactly. Heap, terminal native QB observation and pointer relocation are existing boundaries. Valid history, required configuration/components and successful allocation are internal contracts. Full airborne/state integration, startup, rendering and playable training remain unfinished.'
fixture={'base':BASE,'memory':'airborne-rotation-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'diagnostic_and_native_qb_callbacks','pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'pointer_globals':[index[0x6918ec+4*i] for i in range(8)],'scoped_event_services':{'symbol':'thug_event_services','pointer':SERVICES},'native_callbacks':[{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]}
path=out/'airborne-rotation-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
print('Original airborne rotation:',len(labels),sum(oracle.counts.values()),dict(branches),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_airborne_rotation_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'branches':dict(branches),'heap_events':dict(oracle.heap_events),'native_qb_calls':dict(qb_calls),'packet_count':len(packets),'packets':packets,'zeroed_packet_padding_entries':padding_entries,'real_asset':{'archive':str(archive_path.relative_to(ROOT)),'archive_sha256':hashlib.sha256(archive_bytes).hexdigest(),'member':archived.name,'member_sha256':hashlib.sha256(airtricks).hexdigest(),'loose_path':str(airtricks_path.relative_to(ROOT)),'loose_sha256':hashlib.sha256(loose_airtricks).hexdigest(),'array_offset':array_start,'array_end':array_end,'array_sha256':hashlib.sha256(shipped_array).hexdigest(),'array_matches_loose':True,'cases':16},'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory'],airtricks_path,archive_path]},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(labels),sum(oracle.counts.values()))
