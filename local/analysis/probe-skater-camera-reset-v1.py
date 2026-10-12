"""Original camera reset with real Physics QB values; uncounted candidates."""
from pathlib import Path
source=Path('local/analysis/probe-animation-state-storage-v3.py').read_text().split('for fill,alignment,flag')[0]
exec(compile(source,'<preserved initialized original camera oracle>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear();prefix_hits.clear()
specs=[(0x485b20,18,'thug_camera_set_fov_v1',1,'void',False,False,True),(0x4f9ae0,929,'thug_skater_camera_reset_v1',2,'void',False,False,True)]
for row in specs:bind_new(*row)
functions['0x485b20']['float_args']=[0];functions['0x4f9ae0']['float_args']=[1]
bind(0x41b730,'thug_camera_component_construct_v2',0,'word',True)
bind(0x485ba0,'thug_camera_object_construct_v2',0,'word')
config=json.loads((folder/'skater-camera-config-v2-original.json').read_text());assert config['result']=='original QB camera configuration discovery only'
asset=ROOT/config['path'];assert hashlib.sha256(asset.read_bytes()).hexdigest()==config['sha256']
class ResetGraph(FinalGraph):
 def __init__(self,fill=0,alignment=0,extended=False,overrides=False):
  super().__init__(fill);self.p=P+alignment;component=self.component(0xc4e311fa);decoy=self.component(0x81234567)
  self.put(decoy+16,'<I',component);self.put(OBJ+0x100,'<I',decoy);self.component_pointer=component
  self.put(self.p+12,'<I',OBJ);self.put(self.p+0x168,'<I',self.alloc(0x40));self.put(self.p+0xc4,'<f',36.5);self.put(self.p+0xd0,'<f',17.25)
  for c in config['configurations']:
   rows=[]
   for r in c['value']:
    k=r['type'];v=bits(r['value']) if k==2 else self.text(r['value']) if k in [3,4] else int(r['value'],16);rows.append((int(r['name'],16),k,v))
   if overrides:
    rows=[r for r in rows if r[0] not in [0x7f0032ac,0xadb6390e,0xf54fb9c5,0x2fa11029,0x042fd4a0,0x5a7f5cc5,0xd790b83d,0xd414c22e]]
    rows += [(key,2,bits(.125+i*.0625)) for i,key in enumerate([0x7f0032ac,0xadb6390e,0xf54fb9c5,0x2fa11029,0x042fd4a0,0x5a7f5cc5,0xd790b83d,0xd414c22e])]
    rows.append((0xa1dc81f9,13,0x11223344))
   self.symbol(int(c['name'],16),10,self.structure(rows))
  for a in config['symbols']:
   values=[int(item['checksum'],16) for item in a['value']['items']]
   if extended:values += [values[2]]*8
   self.symbol(int(a['name'],16),12,self.array(13,values))
for fill,alignment,layout,index_,duration in itertools.product([0,0xa5,255],[0,1],[0,1,2],[1,2,3,4],[-1,0,.25]):
 g=ResetGraph(fill,alignment);g.run([call(0x41b730,g.component_pointer),call(0x4f9ae0,g.p,[index_,bits(duration)]),call(0x4f9ae0,g.p,[index_,bits(duration)])],f'actual Physics QB camera reset/{fill}/{alignment}/{layout}/{index_}/{duration}',{0x70134c:layout})
 assert oracle.word(g.p+0x24)==index_
for mode,layout,duration,override in itertools.product(range(5,13),[0,1,2],[0,2],[False,True]):
 g=ResetGraph(0xa5,1,True,override);g.run([call(0x41b730,g.component_pointer),call(0x4f9ae0,g.p,[mode,bits(duration)])],f'bounded extended caller camera array mode/{mode}/{layout}/{duration}/{override}',{0x70134c:layout})
for fov,ratio in itertools.product([15,35,45,60,90,110,140],[1,4/3,16/9]):
 g=FinalGraph();g.run([call(0x485ba0,P),call(0x485b20,P,[bits(fov)])]*2,f'FOV setter with real projection/{fov}/{ratio}',{0x67e544:bits(ratio)})
scope='Two camera dependencies: FOV setter calls the unchanged verified projection routine; SkaterCamera reset uses actual original Physics QB normal/split-screen presets, real component lookup, arrays/checksum/global structure and float/optional getters, immediate/interpolated settings and controller angles. Unaligned/poisoned caller storage, repeat calls, split layouts and actual integer-to-float behind value compare. Required local settings, finite bounded projection parameters, both valid caller-owned component payloads and bounded array indices required. Modes5..12 are instruction-coverage cases using caller arrays extended with an existing original medium-preset checksum; unchanged PC arrays have five entries and no gameplay mode or original startup claim follows. Optional derivative overrides compare separately. Existing PC24 projection SDK transcendental contract retained; no physical x87 transcendental accuracy, numeric/comparator changes, full startup, frame or gameplay credit.'
finish('skater-camera-reset-v1',scope,{},extra)
(folder/'skater-camera-reset-v1-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n')
