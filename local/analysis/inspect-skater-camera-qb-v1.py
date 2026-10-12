"""Parse the unchanged camera definitions with the existing original QB loader.

Discovery only. Old output deletion and writes are omitted from reused setup.
"""
from pathlib import Path
source=Path('tools/verify_script_load.py').read_text().split('# Debug map preserves')[0]
source=source.replace('report_path.unlink(missing_ok=True)','None')
source=source.replace("(out/'script-load-memory.bin').write_bytes(initial)",'None')
exec(compile(source,'<immutable original QB loader setup>','exec'))
path=ROOT/'local/game-files/Game/Data/scripts/game/skutils.qb';raw=path.read_bytes()
data=BASE+0x6b0000;filename=BASE+0x6af000;pool_entries=BASE+0x8000;capacity=1500
memory=bytearray(initial);memory[data-BASE:data-BASE+len(raw)]=raw
text=b'scripts\\game\\skutils.qb\0';memory[filename-BASE:filename-BASE+len(text)]=text
struct.pack_into('<6I',memory,POOL-BASE,pool_entries,pool_entries+capacity*20,0,0,0,pool_entries)
struct.pack_into('<I',memory,POOL-BASE+88,0)
for i in range(capacity):struct.pack_into('<I',memory,pool_entries-BASE+i*20,pool_entries+(i+1)*20 if i+1<capacity else 0)
initial=bytes(memory);oracle.initial=initial
case([load(data,filename=filename)],label='unchanged skutils.qb camera definitions')
key=crc(b'skatercam_composite_structure');symbol=oracle.word(BUCKETS+(key&4095)*4)
while symbol and oracle.word(symbol+4)!=key:symbol=oracle.word(symbol+16)
assert symbol and oracle.cpu.mem_read(symbol+1,1)==b'\x0c'
array=oracle.word(symbol+12);count=oracle.word(array+4);kind=oracle.cpu.mem_read(array+1,1)[0]
assert kind==10 and 0<count<32
items=oracle.word(array+8);items=[items] if count==1 else [oracle.word(items+4*i) for i in range(count)]
def structure(at):
 result=[];node=oracle.word(at+4)
 while node:
  tag=oracle.cpu.mem_read(node,1)[0]>>1;name=oracle.word(node+4);value=oracle.word(node+8)
  row={'name':hex(name),'type':tag,'value':hex(value)}
  if tag in [3,4]:row['text']=bytes(oracle.cpu.mem_read(value,256)).split(b'\0')[0].decode('latin1')
  result.append(row);node=oracle.word(node+12);assert len(result)<128
 return result
descriptors=[structure(at) for at in items]
types=[next(row['value'] for row in rows if row['name']=='0xb6015ea8') for rows in descriptors]
result={'result':'original QB discovery; no completion or integration claim','specimen_sha256':SHA256,'asset':{'path':str(path.relative_to(ROOT)),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()},'array_name':'skatercam_composite_structure','array_checksum':hex(key),'array_type':kind,'components':count,'component_types':types,'descriptors':descriptors,'original_loader_calls':1,'symbol_pool_in_use':oracle.word(POOL+16),'heap_end':hex(oracle.word(CONTEXT)),'old_outputs_untouched':True}
target=ROOT/'local/analysis/skater-camera-qb-v1-discovery.json';assert not target.exists();target.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['result','asset','array_name','components','component_types','symbol_pool_in_use']}),flush=True)
