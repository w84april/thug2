"""Read original TR nodes and sector headers; discovery only, no new credit."""
from pathlib import Path
source=Path('local/analysis/trace-training-scene-nodes.py').read_text().split('rows=[]')[0]
exec(compile(source,'<preserved original node-load setup; no output writes>','exec'))
import math,bisect,hashlib,json,struct
cpu=oracle.cpu
root=ROOT/'local/game-files/Game/Data';raw_qb=(root/'levels/TR/TR.qb').read_bytes()
assert hashlib.sha256(raw_qb).hexdigest()==asset['sha256']
ledger=json.loads((ROOT/'progress/ledger.json').read_text())
vector_at=next(int(row['address'],16) for row in ledger['records'] if row['name']=='thug_script_get_vector')
def array_symbol(name):
 key=crc(name);symbol=oracle.word(BUCKETS+(key&4095)*4)
 while symbol and oracle.word(symbol+4)!=key:symbol=oracle.word(symbol+16)
 assert symbol and cpu.mem_read(symbol+1,1)==b'\x0c'
 at=oracle.word(symbol+12);assert cpu.mem_read(at+1,1)==b'\x0a';return at
def vector(node,name):
 cpu.mem_write(OUT,bytes(16));present=invoke(vector_at,node,[crc(name),OUT,0],12)&255
 if not present:return None
 words=list(struct.unpack('<4I',cpu.mem_read(OUT,16)));values=list(struct.unpack('<4f',cpu.mem_read(OUT,16)))
 assert all(math.isfinite(v) for v in values)
 return {'words':words,'values':values}
def nodes(at):
 n=oracle.word(at+4);items=oracle.word(at+8);result=[]
 for i in range(n):
  node=items if n==1 else oracle.word(items+4*i);name=checksum(node,crc(b'Name'));kind=checksum(node,crc(b'Class'))
  flags={text:bool(invoke(0x476b40,node,[crc(text.encode())],4)&255) for text in ['CreatedAtStart','AbsentInNetGames','TrickObject','Night']}
  result.append({'index':i,'name':hex(name),'text':text_name(name),'class':hex(kind),'class_text':text_name(kind),'flags':flags,'position':vector(node,b'Pos'),'angles':vector(node,b'Angles')})
 return result
# Read both the raw loader output and the actual registered coordinate space.
oracle.case([(0x472420,0,[asset['filename'],asset['address'],0,1,0])])
before=nodes(array_symbol(b'TR_NodeArray'))
oracle.case([(0x472420,0,[asset['filename'],asset['address'],0,1,0]),(0x45d370,TABLE,[]),(0x45d520,TABLE,[key,1])])
after=nodes(oracle.word(TABLE+0x1000c));assert len(before)==len(after)==1917
for a,b in zip(before,after):assert (a['name'],a['class'])==(b['name'],b['class'])
by_name={int(row['name'],16):row for row in after}
trace=json.loads((ROOT/'local/analysis/training-level-mesh-flow-trace.json').read_text());scn=(root/'levels/TR/TR.scn.xbx').read_bytes();tex=(root/'levels/TR/TR.tex.xbx').read_bytes()
assert hashlib.sha256(scn).hexdigest()==trace['scene_sha256'] and hashlib.sha256(tex).hexdigest()==trace['texture_sha256']
positions=[s['position'] for s in trace['sectors']];sectors=[]
for i,entry in enumerate(trace['sectors']):
 at=entry['position'];name,bone,flags,count=struct.unpack_from('<4I',scn,at);box=list(struct.unpack_from('<6f',scn,at+16));sphere=list(struct.unpack_from('<4f',scn,at+40))
 assert all(math.isfinite(v) for v in box+sphere)
 meshes=[j for j,m in enumerate(trace['meshes']) if bisect.bisect_right(positions,m['position'])-1==i]
 assert len(meshes)==count
 row=by_name.get(name)
 sectors.append({'index':i,'file_position':at,'name':hex(name),'text':row['text'] if row else None,'node_index':row['index'] if row else None,'bone':bone,'flags':hex(flags),'mesh_indices':meshes,'serialized_bounds':box,'serialized_sphere':sphere})
assert len(sectors)==790 and sum(len(s['mesh_indices']) for s in sectors)==2269
paths=[root/'levels/TR/TR.qb',root/'levels/TR/TR_Scripts.qb',root/'levels/TR/TR.scn.xbx',root/'levels/TR/TR.tex.xbx',root/'scripts/game/menu/gamemenu_levelselect.qb']
result={'result':'original scene identity discovery; no rendering/frame/gameplay claim','specimen_sha256':SHA256,'assets':{str(f.relative_to(ROOT)):{'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in paths},'nodes_before_registration':before,'nodes_registered':after,'sectors':sectors,'warehouse_named_nodes':sum('warehouse' in (n['text'] or '').lower() for n in after),'nj_named_nodes':sum((n['text'] or '').lower().startswith('nj_') for n in after),'completion_credit':0,'matching_credit':0,'playable':False}
target=ROOT/'local/analysis/tr-scene-identity-v2-original.json';assert not target.exists();target.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['result','warehouse_named_nodes','nj_named_nodes']}),flush=True)
print('Warehouse sectors',[(s['index'],s['text'],len(s['mesh_indices']),s['serialized_bounds']) for s in sectors if 'warehouse' in (s['text'] or '').lower()],flush=True)
print('Restart nodes',[(n['text'],n['position'],n['angles']) for n in after if n['class_text']=='Restart' and ('ware' in (n['text'] or '').lower() or (n['text'] or '').lower() in ['tr_start','player1_start','trg_restart'])],flush=True)
