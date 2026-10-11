"""Reconstruct the accepted final arena, without executing more game code."""
import json,struct
from pathlib import Path
p=Path('local/analysis');f=json.loads((p/'lock-frame-training-fixtures.json').read_text());t=json.loads((p/'lock-frame-training-original.json').read_text());base=f['base'];memory=bytearray((p/f['memory']).read_bytes())
for address,data in f['cases'][0]['patches']:memory[address-base:address-base+len(data)//2]=bytes.fromhex(data)
for step in f['cases'][0]['steps']:
 for address,data in step['outputs']:memory[address-base:address-base+len(data)//2]=bytes.fromhex(data)
def word(a):return struct.unpack_from('<I',memory,a-base)[0]
def floats(a,count=4):return list(struct.unpack_from('<'+'f'*count,memory,a-base))
def chain(owner):
 result=[];at=word(owner+0x100)
 while at:
  assert len(result)<32
  result.append({'address':at,'methods':hex(word(at)),'type':hex(word(at+4)),'flags':hex(word(at+8)),'owner':word(at+12)});at=word(at+16)
 return result
barrel=t['barrel'];owner=t['particle_object'];component=t['particle_component'];effect=t['effect']['address'];lock=t['attachment']['particle_lock']
out={'provenance':'Accepted original arena, also compared by Node and Chromium; no additional execution.','barrel':{'address':barrel,'id':hex(word(barrel+0x14)),'flags':hex(word(barrel+8)),'position':floats(barrel+0x4c),'components':chain(barrel)},
 'particle_owner':{'address':owner,'id':hex(word(owner+0x14)),'flags':hex(word(owner+8)),'flags104':hex(word(owner+0x104)),'position':floats(owner+0x4c),'components':chain(owner)},
 'attachment':{'address':lock,'flags':hex(word(lock+0x8c)),'target':hex(word(lock+0x18)),'override':hex(word(lock+0x1c)),'bone':hex(word(lock+0x20)),'offset':floats(lock+0x24)},
 'flexparticle':{'address':component,'effect':word(component+0x18),'elapsed':floats(component+0x2c,1)[0],'suspend':word(component+0x30),'model':word(component+0x34),'orientation_byte':memory[component-base+0x38]},
 'effect':{**t['effect'],'flags12a':memory[effect-base+0x12a],'visible12f':memory[effect-base+0x12f],'visible130':memory[effect-base+0x130],'setup_script':word(effect+0xfc),'update_script':word(effect+0x100)},
 'boundary':{'address':hex(word(f['boundary_address'])),'component':word(f['boundary_address']+4),'owner':word(f['boundary_address']+8)},'playable':False}
(p/'lock-frame-next-state.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
