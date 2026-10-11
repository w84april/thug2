"""Independent reconstruction of the original combined startup comparison."""
import hashlib,json,struct
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';read=lambda n:json.loads((p/n).read_text());sha=lambda q:hashlib.sha256(q.read_bytes()).hexdigest()
f=read('level-collision-component-fixtures.json');t=read('level-collision-component-original.json');trace=read('level-collision-load-trace.json');base=f['base'];arena=bytearray((p/f['memory']).read_bytes())
assert base==0x800000 and len(arena)==0x5800000 and len(f['cases'])==1
c=f['cases'][0];steps=c['steps'];assert not c['patches'] and len(steps)==24
assert [s['fn'] for s in steps]==['0x472420']*4+['0x45d370','0x45d520','0x479070','0x49f050','0x48ccb0','0x49d590','0x4088e0','0x4738e0']+['0x5a4ff0']*12
assert [bool(s.get('expected_trap')) for s in steps]==[False]*24
assert f['float_fields']==[] and 'boundary_factory' not in f and 'boundary_address' not in f
assert (t['completed_calls'],t['interrupted_calls'],t['completed_objects'],t['playable'])==(24,0,12,False)
assert len(trace['all_startup'])==31 and sum(n['alternate'] for n in trace['all_startup'])==19
assert len(trace['selected'])==12 and not trace['created']
raw=lambda a,n:arena[a-base:a-base+n];w=lambda a:struct.unpack_from('<I',arena,a-base)[0]
for s,name in zip(steps[:4],['scripts/game/object.qb','scripts/game/skutils.qb','scripts/game/ped.qb','levels/TR/TR.qb']):
 data=(r/'local/game-files/Game/Data'/name).read_bytes();assert raw(s['args'][1],len(data))==data
tex=(r/'local/game-files/Game/Data/levels/TR/TR.tex.xbx').read_bytes();scn=(r/'local/game-files/Game/Data/levels/TR/TR.scn.xbx').read_bytes()
assert sha(r/'local/game-files/Game/Data/levels/TR/TR.tex.xbx')=='13c28cf820dd4bb989579915ab533b7651ea178ef664d44ad9ec1fc754fa6d21'
assert sha(r/'local/game-files/Game/Data/levels/TR/TR.scn.xbx')=='a4e185b0f050e181850c341a3378b54f1b37adce3099d3568600bf2e02e61332'
assert raw(base+0x1000000,len(tex))==tex and raw(base+0x1400000,len(scn))==scn
collision=(r/'local/game-files/Game/Data/levels/TR/TR.col.xbx').read_bytes()
assert raw(base+0x1b00000,len(collision))==collision and steps[9]['fn']=='0x49d590'
for s in steps:
 assert not s.get('float_fields') and not s.get('quiet_float_fields') and not s.get('global_bit_masks')
 for a,data in s['outputs']:arena[a-base:a-base+len(data)//2]=bytes.fromhex(data)
assert raw(base+0xe000,16)==(p/f['memory']).read_bytes()[0xe000:0xe010]
assert w(base+0xf2000)==base+0x1400000+len(scn) and w(base+0xf2200)==105194
assert [w(base+0xf2300+o) for o in [8,12,16,20,24,28]]==[13614,4538,4594,4594,1,1]
assert w(base+0x28)==t['heap_events']>87661 and hex(w(base+0x20))==t['heap_end']
assert t['file_calls']=={'1':104652,'2':542} and t['gpu_calls']=={'1':596,'2':2486,'3':2486}
scene=t['scene'];header=t['header'];assert steps[8]['result']==scene and w(scene+0x280)==header
assert w(w(header+0x18)+8)==870 and w(w(t['dictionary']+12)+8)==596
assert w(header+0x20)==w(header+0x28)==2269 and w(base+0xf2500)==7
# Every resident mip is still the exact untouched source payload.
cur=8;mips=0
for resource in t['resources']:
 key,width,height,levels,depth,palette_depth,compression,palette_bytes=struct.unpack_from('<8I',tex,cur);cur+=32
 assert (resource['width'],resource['height'],len(resource['surfaces']))==(width,height,levels)
 for a,capacity,pitch in resource['surfaces']:
  n=struct.unpack_from('<I',tex,cur)[0];cur+=4;assert n<=capacity and raw(a,n)==tex[cur:cur+n];cur+=n;mips+=1
assert cur==len(tex) and mips==2486
sectors={};meshes=[];table=w(scene+0xd0);buckets=w(table+4)
for i in range(1<<w(table)):
 node=buckets+i*12
 while node:
  sector=w(node+4)
  if sector:
   key=w(sector+4);assert key not in sectors;geometry=w(sector+0x14);sectors[key]=sector
   if geometry:
    assert w(geometry+0x34)==scene and w(geometry+0x38)==0
    meshes.extend(w(w(geometry+0x3c)+j*4) for j in range(w(geometry+0x40)))
  node=w(node+8)
assert len(sectors)==t['collision']['sectors'] and len(meshes)==len(set(meshes))==2269
assert sum(struct.unpack('<H',raw(m+0x22,2))[0] for m in meshes)==50814
assert sum(sum(struct.unpack('<8H',raw(m+0x24,16))) for m in meshes)==77029
for m in meshes:
 # Original billboards rewrite CPU vertices after upload without a GPU re-upload.
 if not w(m)&0x10:
  v=w(m+0xcc);n=w(v);assert raw(w(v+12),n)==raw(w(v+8)+256,n)
 for j,n in enumerate(struct.unpack('<8H',raw(m+0x24,16))):
  if n:
   v=w(m+0x54+j*4);assert raw(w(v+16),n*2)==raw(w(v+12)+256,n*2)
# Each original collision checksum must attach its own relocated object.
count=struct.unpack_from('<I',collision,4)[0];col=t['collision'];assert count==605==col['count']==w(scene+0x158)
instances=w(scene+0x15c);objects=w(scene+0x160);grid=w(scene+0xd4)
assert (instances,objects,grid)==(col['instances'],col['objects'],col['grid']) and grid and col['grid_enabled']==1
assert objects==base+0x1b00000+32 and w(instances-4)==count
keys=set()
for i in range(count):
 key=struct.unpack_from('<I',collision,32+i*64)[0];assert key not in keys;keys.add(key)
 instance=instances+i*24;obj=objects+i*64;sector=sectors[key]
 assert w(instance)==0x645c18 and w(instance+4)==key and w(instance+12)==obj
 assert w(sector+0x18)==instance and w(sector+8)&0x40
 geometry=w(sector+0x14)
 if geometry:assert w(geometry+8)==obj
assert sum(bool(w(v+0x14)) for v in sectors.values())==790
assert sum(bool(w(v+0x18)) for v in sectors.values())==605
assert w(grid+0x28)==w(grid+0x2c)==20 and raw(grid,32)==raw(scene+0xb0,32)
valid={instances+i*24 for i in range(count)};cell_references=0
for i in range(400):
 cell=grid+0x30+i*48;n=w(cell+0x24);items=w(cell+0x2c)
 assert n<=count and (bool(items)==bool(n));cell_references+=n
 row=[w(items+j*4) for j in range(n)]
 assert len(row)==len(set(row)) and all(v in valid for v in row)
 assert all(struct.unpack('<H',raw(w(v+12)+8,2))[0]>0 for v in row)
assert cell_references>605
assert len(t['objects'])==12 and sum(bool(o['collision']) for o in t['objects'])==10
assert [s['args'][0] for s in steps[12:]]==[o['node'] for o in t['objects']]
assert all(s['result']==1 for s in steps[12:])
manager=t['asset_manager'];assert manager and t['asset_manager_refs']==1 and w(manager)==0x645658
mtable=w(manager+0x1c);assert w(mtable)==10 and w(mtable+8)==0
assert not any(raw(w(mtable+4),1024*12))
mn=w(manager+16);assert w(mn)==0x647284 and w(mn+4)==manager and w(mn+12)==mn==w(mn+16)
task=w(manager+0x38);assert w(task)==0x6476f0 and w(task+24)==0x407eb0 and w(task+28)==manager
n=w(task+8);assert w(n)==0x64549c and w(n+4)==task and w(n+12)==n==w(n+16)
all_objects=[];all_collision=[]
for o in t['objects']:
 obj=o['object'];all_objects.append(obj);assert o['complete'] and w(obj+0x104)==o['flags']==0x60
 assert w(obj+0x14)==int(o['name'],16) and w(obj+0x10)==o['script']
 chain=[];c=w(obj+0x100)
 while c:
  assert len(chain)<8;chain.append((c,w(c+4)));assert w(c+12)==obj;c=w(c+16)
 assert [k for a,k in chain]==[0xce0ca665,0x0a015e17,0x1d5b1ae6,0x07713c7b,0x5cb5cb7e,0x286a8d26,0xa432dc41,0xb87c8e43]
 assert chain==[(c['address'],c['type']) for c in o['components']]
 assert w(o['model']+0x208)==o['renderer'] and raw(o['model']+0x235,1)==bytes([int(bool(o['parts']))])
 assert chain[6][0]==o['collision_component'] and w(chain[6][0])==0x645eec
 inner=o['collision'];assert w(chain[6][0]+24)==inner
 sector=sectors[int(o['name'],16)];static=w(sector+24)
 if inner:
  all_collision.append(inner);assert static and w(inner)==0x645ce0
  assert w(inner+12)==w(static+12) and w(inner+0xa0)==obj
  assert raw(inner+16,16)==raw(obj+0x4c,16)
  assert raw(inner+32,48)==raw(obj+0xc0,48)
  assert [w(inner+0x60+(row*4+col)*4) for row in range(4) for col in range(4)]==[w(inner+0x20+(col*4+row)*4) for row in range(4) for col in range(4)]
 else:assert not static and o['text'] in ['LO_forlease03','LO_forlease03shad']
 assert len(o['parts']) in [0,1]
 if not o['parts']:
  assert w(sector+20)==0 and o['text'] in ['WH_TB_Barrelfire_03_Col','WH_TB_Barrelfire_04_Col'];continue
 geo=o['parts'][0]['geometry'];source=w(sector+20);assert w(geo+8)==w(source+8)
 assert w(geo+0x40)==w(source+0x40)
 for i in range(w(geo+0x40)):
  a=w(w(source+0x3c)+i*4);c=w(w(geo+0x3c)+i*4);expected=bytearray(raw(a,216));struct.pack_into('<I',expected,0,w(a)|0x41);assert raw(c,216)==expected
registry=base+0xa1004;node=w(registry+12);registered=[]
while node!=registry:
 assert len(registered)<12;registered.append(w(node+4));node=w(node+12)
assert set(registered)==set(all_objects) and len(registered)==12
values={entry[1]:steps[-1]['globals'][i] for i,entry in enumerate(f['globals'])}
head=0x691978;node=values[head+12];tail=head;registered=[]
while node!=head:
 assert len(registered)<10 and w(node)==0x645aa0 and w(node+16)==tail
 registered.append(w(node+4));tail=node;node=w(node+12)
assert registered==all_collision and tail==values[head+16]
assert w(base+0x28)==t['heap_events']==90522 and t['heap_end']=='0x2d3ebac'
print('Independent graph:12 completed ordinary props,96 components,10 moving collisions,3 owned scripts;881 sectors/605 static collisions preserved;real manager initialized.')
