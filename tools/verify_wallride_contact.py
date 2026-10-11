"""Original wallride continuation against actual wallrideable training faces."""
from pathlib import Path
wallride_source_text=Path('tools/verify_wallride_paths.py').read_text()
prefix=wallride_source_text.split('for dt in [')[0].replace('wallride-paths.json','wallride-contact.json')
exec(compile(prefix,'<wallride complete engine graph>','exec'))
chosen=[]
for i,q in enumerate(loader['queries']):
 data=bytes.fromhex(q['result'])
 if q['returned'] and struct.unpack_from('<H',data,44)[0]&4 and abs(struct.unpack_from('<f',data,4)[0])<.1:
  chosen.append((i,data))
for i,data in chosen[:16]:
 point=list(struct.unpack_from('<4f',data,16));normal=list(struct.unpack_from('<4f',data))
 tangent=[normal[2],0,-normal[0],0];right=[-normal[1]*normal[0],normal[2]**2+normal[0]**2,-normal[1]*normal[2],0]
 matrix=right+normal+tangent+[0,0,0,1]
 for offset,into in [(1,False),(-1,False),(1,True)]:
  position=[point[j]+normal[j]*offset for j in range(3)]+[1]
  velocity=[(-normal[j] if into else tangent[j])*100 for j in range(3)]+[1]
  p=[patch(BODIES+0x4c,'<4f',*position),patch(BODIES+0x5c,'<4f',*position),patch(BODIES+0x6c,'<16f',*matrix),patch(PHYS+0x18,'<16f',*matrix),patch(PHYS+0x38c,'<4f',*normal),patch(BODIES+0xac,'<4f',*velocity)]
  wallride(p,label=f'wallrideable training face{i}, offset{offset}, into{into}')
  path_results[-1]['training_face']=i
  if offset==1 and not into:
   for target,value,width in [(GATE+0x26,1,1),(PHYS+0x1528,SKATER_STATE2,4),(PHYS+0x1514,SOUND2,4)]:
    wallride(p+[patch(GOBS+4,'<4I',target,value,width,0)],label='wallride callback mutation')
   if i==chosen[0][0]:
    for pending in [0,1]:
     wallride(p+[patch(TRICK+0x13b0,'<B',pending),patch(PHYS+0x158+0x54,'<I',0x12345678)],label='wall surface changed and notification flag')
for i,q in [(i,q) for i,q in enumerate(loader['queries']) if q['returned'] and struct.unpack_from('<f',bytes.fromhex(q['result']),4)[0]<-.1][:8]:
 point=list(struct.unpack_from('<4f',bytes.fromhex(q['result']),16))
 for normal in [[0,0,0,0],[1,0,0,0]]:
  position=[point[j]-18*normal[j]-(18 if j==1 else 0) for j in range(3)]+[1]
  wallride([patch(PHYS+0x8c,'<f',0),patch(BODIES+0x4c,'<4f',*position),patch(BODIES+0x5c,'<4f',*position),patch(PHYS+0x38c,'<4f',*normal)],label='actual training overhead face'+str(i))
tail=wallride_source_text[wallride_source_text.index("\nscope=")+1:].replace('wallride-paths','wallride-contact').replace('wallride_paths','wallride_contact')
exec(compile(tail,'<save original wallride contact observations>','exec'))
