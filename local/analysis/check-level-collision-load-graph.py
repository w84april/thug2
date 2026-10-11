"""Independent reconstruction of the original combined startup comparison."""
import hashlib,json,struct
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';read=lambda n:json.loads((p/n).read_text());sha=lambda q:hashlib.sha256(q.read_bytes()).hexdigest()
f=read('level-collision-load-fixtures.json');t=read('level-collision-load-original.json');trace=read('level-collision-load-trace.json');base=f['base'];arena=bytearray((p/f['memory']).read_bytes())
assert base==0x800000 and len(arena)==0x5800000 and len(f['cases'])==1
c=f['cases'][0];steps=c['steps'];assert not c['patches'] and len(steps)==12
assert [s['fn'] for s in steps]==['0x472420']*4+['0x45d370','0x45d520','0x479070','0x49f050','0x48ccb0','0x49d590','0x4738e0','0x5a4ff0']
assert [bool(s.get('expected_trap')) for s in steps]==[False]*11+[True]
assert f['float_fields']==[] and f['boundary_factory']==0x41c920 and f['boundary_address']==base+0xe000
assert (t['completed_calls'],t['interrupted_calls'],t['completed_objects'],t['playable'])==(11,1,0,False)
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
assert list(struct.unpack('<4I',raw(base+0xe000,16)))==[0x41c920,0,base+0xc000,1]
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
assert len(t['objects'])==1;o=t['objects'][0];assert o['index']==375 and o['text']=='LO_forlease03' and not o['complete']
assert w(o['object']+0x14)==0x83691b35 and w(o['object']+0x104)==0 and w(o['object']+0x10)==0
assert w(w(base+0xa1004+12)+4)==o['object'] and w(w(base+0xa1004+12)+12)==base+0xa1004
chain=[];component=w(o['object']+0x100)
while component:
 assert len(chain)<7;chain.append((component,w(component+4)));assert w(component+12)==o['object'];component=w(component+16)
assert [k for a,k in chain]==[0xce0ca665,0x0a015e17,0x1d5b1ae6,0x07713c7b,0x5cb5cb7e,0x286a8d26]
assert chain==[(c['address'],c['type']) for c in o['components']] and chain[-1][0]==o['model']
assert w(o['model']+0x208)==o['renderer'] and raw(o['model']+0x235,1)==b'\x01'
p0=o['parts'][0];geometry=p0['geometry'];source_geometry=w(sectors[0x83691b35]+0x14)
assert w(geometry+0x40)==w(source_geometry+0x40)==1
assert w(geometry+8)==w(source_geometry+8)==0 and w(sectors[0x83691b35]+0x18)==0
assert 0x83691b35 not in keys # The original first prop has no named collision sector.
original=w(w(source_geometry+0x3c));clone=w(w(geometry+0x3c));expected=bytearray(raw(original,216));struct.pack_into('<I',expected,0,w(original)|0x41)
assert raw(clone,216)==expected and p0['meshes']==[clone]
instance=w(geometry+0x4c);private=w(instance+0x58)
assert instance==p0['instance'] and w(private+0x20)==w(private+0x28)==1 and w(w(private+0x1c))==clone
assert raw(private+0x44,32)==raw(geometry+0x14,32)==raw(source_geometry+0x14,32)
assert list(struct.unpack('<16I',raw(instance+4,64)))==[0x3f800000 if i%5==0 else 0 for i in range(16)]
assert raw(instance+0x4c,1)==b'\x01' and w(instance)&1
assert f['scope']==t['scope']
print('Independent graph:',len(sectors),'sectors,605 collision attachments,400 grid cells',cell_references,'references;790 graphics sectors,2269 meshes;first partial prop correctly has no named collision payload;0 completed objects.')
