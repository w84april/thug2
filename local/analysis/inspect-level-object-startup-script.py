import struct,json
from pathlib import Path
p=Path('local/game-files/Game/Data/scripts/game/skutils.qb');d=p.read_bytes();rows=[];names={};i=0
while i<len(d):
 t=d[i];n=1;v=None
 if t in [2,0x16,0x17,0x18,0x1a,0x2e,0x43,0x44,0x46]:n=5;v=struct.unpack_from('<I',d,i+1)[0]
 elif t in [0x1b,0x1c]:n=5+struct.unpack_from('<I',d,i+1)[0]
 elif t==0x1e:n=13
 elif t==0x1f:n=9
 elif t==0x2b:
  v=struct.unpack_from('<I',d,i+1)[0];n=d.index(0,i+5)-i+1;names[v]=d[i+5:i+n-1].decode('latin1')
 elif t in [0x2f,0x37,0x40,0x41]:n=5+6*struct.unpack_from('<I',d,i+1)[0]
 elif t in [0x47,0x48,0x49]:n=3
 rows.append((i,t,v));i+=n
 if not t:break
for a in [0xa98f5c63,0x69c257e9]:print(hex(a),names.get(a))
start=next(j for j in range(len(rows)-1) if rows[j][1]==0x23 and rows[j+1][2]==0xa98f5c63)
lines=[]
for i,t,v in rows[start:]:
 if t in [1,2]:lines.append('\n')
 elif v is not None:lines.append(names.get(v,hex(v))+' ')
 else:lines.append({3:'{ ',4:'} ',5:'[ ',6:'] ',7:'= ',0x23:'function ',0x24:'endfunction '}.get(t,f'<{t:02x}> '))
 if t==0x24:break
print(''.join(lines));Path('local/analysis/level-object-startup-script.txt').write_text(''.join(lines)+'\n')
