"""Execute original material parsing; reuse recovered constructors and real texture data."""
from pathlib import Path
source=Path('local/analysis/probe-texture-buffer.py').read_text().split('for fill in [0,0xa5,0xff]:')[0]
exec(compile(source,'<pinned texture heap/GPU setup>','exec'))
functions.clear();code.clear();hits.clear();oracle.counts.clear();oracle.coverage.clear();oracle.event_limit=2600
specs=[(0x4d2cb0,1746,'thug_material_buffer_parse_draft',2,'word',True,False),
 (0x4de300,64,'thug_model_scene_data_initialize_draft',0,'word',False,True),
 (0x4d1a90,176,'thug_render_material_initialize',0,'word',False,True)]
for a,n,name,argc,result,heap,this in specs:
 functions[hex(a)]={'name':name,'this':this,'result':result,'cleanup':argc*4 if this else 0,'memory':heap}
 code[a]=list(md.disasm(pe.get_data(a-0x400000,n),a));oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:hits.update([at]),begin=a,end=a+n-1)
functions['0x49f050']={'name':'thug_texture_dictionary_get_buffer_draft','this':False,'result':'word','cleanup':0,'memory':True}
def bits(f):return struct.unpack('<I',struct.pack('<f',f))[0]
def material(key=1,passes=(),cutoff=7,sorted_=0,two=0,limit=3,depth=(),power=0,rgb=(0x11223344,0x55667788,0x99aabbcc)):
 s=struct.pack('<4IBIBBiB',key,0x12345678,len(passes),cutoff,0x81,0xc1200000,sorted_,two,limit,int(bool(depth)))
 if depth:s+=struct.pack('<2I',*depth)
 s+=struct.pack('<I',power)
 if struct.unpack('<f',struct.pack('<I',power))[0]>0:s+=struct.pack('<3I',*rgb)
 for i,p in enumerate(passes):
  flags=p.get('flags',0);colour=p.get('colour',[0x3f000000]*3)
  s+=struct.pack('<2IB3I7I',p.get('key',1),flags,0xab,*colour,p.get('blend',0),p.get('alpha',128),0x1234,0xabcd,0x40800000,0x41000000,0x30004)
  if flags&1:s+=struct.pack('<8I',*range(0x33445560,0x33445568))
  if i==0 and flags&2:
   channels=p.get('channels',[[(0,1),(2,3)],[]]);s+=struct.pack('<I',len(channels))
   for j,rows in enumerate(channels):
    s+=struct.pack('<2I',len(rows),j+17)
    for row in rows:s+=struct.pack('<2I',*row)
  if flags&0x800:
   frames=p.get('frames',[(10,5),(20,9),(30,0xfefefefe)])
   s+=struct.pack('<4I',len(frames),0xdddddddd,23,47)
   for row in frames:s+=struct.pack('<2I',*row)
  s+=struct.pack('<4I',0x11111111,0x22222222,p.get('bias',bits(-9)),0x33333333)
 return s
class Materials(Graph):
 def texture_table(self,mode='mixed'):
  if mode=='absent':
   t=self.alloc(24);self.put(t,'<6I',0,0,0,0,0,0);return t
  rows=[]
  for i,key in enumerate([0,1,5,9]):
   wrapper=self.alloc(20);resource=self.alloc(32);self.put(wrapper+8,'<I',i&1)
   if i&1:
    indirect=self.alloc(4);self.put(indirect,'<I',0 if mode=='null' else resource);self.put(wrapper+16,'<I',indirect)
   else:self.put(wrapper+16,'<I',0 if mode=='null' else resource)
   rows.append((key,wrapper))
  rows.insert(2,(13,0));return self.table(rows,chain=mode=='chain')
 def materials(self,rows):
  data=struct.pack('<I',len(rows))+b''.join(rows)
  if len(data)<0x6000:self.file(data);return INPUT
  at=self.alloc(len(data));self.data[at-BASE:at-BASE+len(data)]=data;self.put(CURSOR,'<I',at);return at
for fill in [0,0xa5,0xff]:
 g=Materials();g.data[P-BASE:P-BASE+272]=bytes([fill])*272
 run(g,[call(0x4d1a90,P),call(0x4de300,P+0x200),call(0x4de300,P+0x200)],f'constructors retained bytes{fill}')
for count in [0,1,2,3,4,8,2048]:
 g=Materials();t=g.texture_table();g.materials([material(key=i if count>8 else i*4096) for i in range(count)])
 run(g,[call(0x4d2cb0,args=[CURSOR,t])],f'material count{count}/collision and shift cap')
for keys in [[0,0],[1,1],[0,16,32,0,16],[3,3,0,0]]:
 g=Materials();t=g.texture_table();g.materials([material(key=k) for k in keys]);run(g,[call(0x4d2cb0,args=[CURSOR,t])],f'duplicate materials{keys}')
for power in [0,0x80000000,bits(-1),bits(2),0x7f800000,0xff800000,0x7fc12345,0x7f812345]:
 for limit in [-7,16,17,256]:
  g=Materials();t=g.texture_table();g.materials([material(power=power,limit=limit,depth=(11,22) if limit&1 else ())]);run(g,[call(0x4d2cb0,args=[CURSOR,t])],f'power{power:x} limit{limit}')
for mode in ['mixed','chain','null','absent']:
 for key in [0,1,5,9,13,0xfefefefe]:
  g=Materials();t=g.texture_table(mode);g.materials([material(passes=[{'key':key,'flags':0}])]);run(g,[call(0x4d2cb0,args=[CURSOR,t])],f'texture lookup{mode} key{key:x}')
for alpha in [0,1,127,128,255,256,0x7fffffff,0x80000000,0xffffffff]:
 for sorted_ in [0,1]:
  g=Materials();t=g.texture_table();g.materials([material(passes=[{'alpha':alpha,'blend':0xabcdef01}],sorted_=sorted_)]);run(g,[call(0x4d2cb0,args=[CURSOR,t])],f'alpha{alpha:x} explicit-sort{sorted_}')
for bias in [-100,-9,-8,-7,-0.0,0,1,float('inf'),float('-inf')]:
 g=Materials();t=g.texture_table();g.materials([material(passes=[{'bias':bits(bias)}])]);run(g,[call(0x4d2cb0,args=[CURSOR,t])],f'clamped bias{bias}')
for bias in [0x7fc12345,0x7f812345,0xffc54321,0xc0ffffff,0xc1000001]:
 g=Materials();t=g.texture_table();g.materials([material(passes=[{'bias':bias}])]);run(g,[call(0x4d2cb0,args=[CURSOR,t])],f'bias payload and boundary{bias:x}')
for component in range(3):
 g=Materials();t=g.texture_table();colour=[0x3f000000]*3;colour[component]=0x3f800000
 g.materials([material(passes=[{'colour':colour},{},{'colour':colour},{}])]);run(g,[call(0x4d2cb0,args=[CURSOR,t])],f'neutral colour component{component}')
for flags in [1,2,3,0x800,0x801,0x802,0x803]:
 for frames in [[],[(1,0)],[(2,1),(3,5),(4,9),(5,13),(6,0xfefefefe)]]:
  g=Materials();t=g.texture_table('chain');g.materials([material(passes=[{'flags':flags,'frames':frames,'channels':[] if not frames else [[(1,2)],[(3,4),(5,6)],[]]}]*4)])
  run(g,[call(0x4d2cb0,args=[CURSOR,t])],f'animation flags{flags:x} frames{len(frames)}')
# Real texture parser -> real material parser, using untouched Letter S data.
texture=(ROOT/'local/game-files/Game/Data/models/GameObjects/SKATE/Letter_S/Letter_S.tex.xbx').read_bytes()
model=(ROOT/'local/game-files/Game/Data/models/GameObjects/SKATE/Letter_S/Letter_S.mdl.xbx').read_bytes()
g=Materials();g.file(texture);model_at=INPUT+0x100;g.data[model_at-BASE:model_at-BASE+len(model)]=model;g.put(CURSOR,'<I',model_at+12);cache=g.table()
get=call(0x49f050,args=[0xf4eab21c,INPUT,len(texture),0,0,0,0])
old_counts=oracle.counts.copy();stages=oracle.case([get],g.patches(),{0:0,**{3+i:g.word(cache+4*i) for i in range(6)}})
dictionary=stages[-1]['result'];texture_table=oracle.word(dictionary+12);oracle.cases.pop();oracle.counts=old_counts;gpu_counts.clear()
stages=run(g,[get,call(0x4d2cb0,args=[CURSOR,texture_table])],'actual Letter S texture and materials',cache=cache)
table=stages[-1]['result'];count=oracle.word(table+8);cursor=oracle.word(CURSOR)
assert count==1 and model_at+12<cursor<model_at+len(model)
buckets=oracle.word(table+4);material_ptr=next(oracle.word(buckets+i*12+4) for i in range(1<<oracle.word(table)) if oracle.word(buckets+i*12+4))
texture_resource=oracle.word(material_ptr+0x30);assert texture_resource and oracle.word(texture_resource+16)==TEXTURES
actual={'model_sha256':hashlib.sha256(model).hexdigest(),'texture_sha256':hashlib.sha256(texture).hexdigest(),'materials':count,'material_key':hex(oracle.word(material_ptr)),'passes':oracle.word(material_ptr+8),'flags':hex(oracle.word(material_ptr+0x20)),'material_pointer':hex(material_ptr),'texture_resource':hex(texture_resource),'cursor_offset':cursor-model_at,'next_geometry_count':oracle.word(cursor),'gpu_calls':dict(gpu_counts)}
print('ACTUAL',json.dumps(actual),flush=True)
missing={hex(a):[hex(i.address) for i in c if not hits[i.address]] for a,c in code.items()};print('MISSING',json.dumps(missing),flush=True)
coverage={hex(a):{'total':len(c),'covered':len(c)-len(missing[hex(a)]),'missing':missing[hex(a)]} for a,c in code.items()}
excluded={hex(a):'memory manager bootstrap; initialized heap contract' for a in [0x4d2d05,0x4d2d5c,0x4d2f4d,0x4d2fc3,0x4d2fed,0x4d3058,0x4d30de,0x4d3146]}
excluded.update({hex(a):'allocation failure; successful allocation contract' for a in [0x4d2d35,0x4d2d84,0x4d2f7d]})
excluded['0x4d3029']='alignment instruction bypassed by both predecessors'
for a,c in coverage.items():
 c['excluded']=excluded if a=='0x4d2cb0' else {};assert set(c['missing'])==set(c['excluded']),(a,c)
scope='Original PC material parsing with exact cursor, heap, globals and storage comparisons, including multiple passes, animated UV/channel/texture data, resource indirection, duplicate materials and float flags. The existing4d1a90 constructor is reused, not counted new. The unchanged Letter S texture is parsed first, then its actual model material binds to that resource. No geometry or drawing is manufactured.'
fixture={'base':BASE,'memory':'material-buffer-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'texture-buffer-ports.wasm','memory_exports':['fixture_texture_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'pointer_fields':sorted(fields),'pointer_exports':exports,
 'pointer_initializers':[['thug_texture_allocation_scope_draft',oracle.stop+0x330]],'native_callbacks':[{'module':'texture-buffer-ports.wasm','export':'fixture_texture_'+name,'slots':slots,**({'original':oracle.stop+0x330} if name=='scope' else {})} for name,slots in [('create',[DVT+0x5c]),('lock',[TVT+0x4c]),('unlock',[TVT+0x50]),('scope',[])]] ,'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'material-buffer-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(oracle.counts.values()),'instruction_coverage':coverage,'existing_dependency_addresses':['0x4d1a90'],'actual_asset':actual,'scope':scope}
(folder/'material-buffer-original.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='instruction_coverage'}))
