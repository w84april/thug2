"""Original whole Physics QB load and camera arrays; discovery, zero credit."""
from pathlib import Path
source=Path('local/analysis/inspect-tr-level-selection-v1.py').read_text().split('files=')[0]
exec(compile(source,'<preserved whole original QB loader helpers>','exec'))
file='scripts/game/skater/physics.qb';path=ROOT/'local/game-files/Game/Data'/file;raw=path.read_bytes();data=BASE+0x6b0000;filename=BASE+0x6af000
memory=bytearray(initial);assert data-BASE+len(raw)<=len(memory)
memory[data-BASE:data-BASE+len(raw)]=raw;text=file.replace('/','\\').encode()+b'\0';memory[filename-BASE:filename-BASE+len(text)]=text
pool_entries=BASE+0x8000;capacity=1500
struct.pack_into('<6I',memory,POOL-BASE,pool_entries,pool_entries+capacity*20,0,0,0,pool_entries);struct.pack_into('<I',memory,POOL-BASE+88,0)
for i in range(capacity):struct.pack_into('<I',memory,pool_entries-BASE+i*20,pool_entries+(i+1)*20 if i+1<capacity else 0)
oracle.initial=bytes(memory);oracle.case([load(data,local=1,filename=filename)])
symbols=[]
for bucket in range(4096):
 symbol=oracle.word(BUCKETS+bucket*4);chain=0
 while symbol:
  kind=cpu.mem_read(symbol+1,1)[0];key=oracle.word(symbol+4);at=oracle.word(symbol+12);name=readable(key)
  if name in ['Skater_Camera_Array','Skater_Camera_2P_Vert_Array','Skater_Camera_2P_Horiz_Array']:
   assert kind==12;symbols.append({'name':hex(key),'text':name,'type':kind,'value':value(kind,at)})
  symbol=oracle.word(symbol+16);chain+=1;assert chain<100
assert len(symbols)==3
configurations=[];seen=set()
for symbol in symbols:
 for item in symbol['value']['items']:
  key=int(item['checksum'],16)
  if key in seen:continue
  seen.add(key);at=invoke(0x479020,0,[key,0],0);assert at
  configurations.append({'name':hex(key),'text':item['text'],'type':10,'value':value(10,at)})
result={'configurations':configurations,'result':'original QB camera configuration discovery only','specimen_sha256':SHA256,'path':str(path.relative_to(ROOT)),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'symbols':symbols,'scope':'Original whole Physics QB loader, exact camera configuration arrays and debug names. No reset, camera behavior, startup or gameplay completion credit.','completion_credit':0,'matching_credit':0,'playable':False}
target=ROOT/'local/analysis/skater-camera-config-v2-original.json';assert not target.exists();target.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['symbols','configurations']}));print([(s['text'],len(s['value']['items'])) for s in symbols]);print('Referenced original camera structures',len(configurations))
