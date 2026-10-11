"""Full original particle command dispatcher, without substituted game callees."""
from pathlib import Path
commandprobe_source=Path('local/analysis/probe-particle-emission.py').read_text()
exec(compile(commandprobe_source.split('for raw in [')[0],'<verified emission setup>','exec'))
exec(compile('def triangle'+commandprobe_source.split('def triangle')[1].split('for small_faces in [')[0],'<verified collision mesh builder>','exec'))
functions.clear();coverage.clear();hits.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
bind_new(0x497b00,2960,'thug_particle_command_draft',3,'byte')
for name,address,value,width in [('thug_collision_default_cache',0x691974,0,4),('thug_collision_select_farthest',0x691910,0,1)]:glob(name,address,value,width)
for j in range(1024):glob('thug_collision_fallback_indices',0x67c6b8+j*4,j*2|((j*2+1)<<16),offset=j*4)
initial=bytes(memory);oracle.initial=initial
class CommandGraph(EmissionGraph):
 def __init__(self):
  super().__init__();self.query=self.alloc(12);self.put(self.query,'<3I',0,0,0)
  for offset in [0x10c,0x110,0x114]:self.put(P+offset,'<I',self.alloc(48)+16)
  self.put(P+0x108,'<f',.3);self.put(P+0xec,'<f',.25)
 def command(self,name,items=()):return call(0x497b00,P,[name,self.structure(items),0,self.query])
def run(g,calls,label,changes=None):return run_emission(g,calls,label,changes)
# Numeric defaults, every optional parameter subset, float/integer conversion,
# included structures and named symbol resolution all use original QB getters.
numeric={0x8ffdef38:[0x73e5bad0,0x0ab21af0,0x055ce396],0x63274395:[0x5e84e22f,0x6289dd76],0xd3f1d333:[0x5e84e22f,0x6289dd76],0x7911855b:[0x834a5f87],0x35b65bd4:[0x2013c0c6],0x2e66815e:[0x5b1d3822],0x2a479569:[0x745523aa,0xf95d2e5f,0x68cd967d,0xe5c59b88],0xfbb6720d:[0x4eedfae7,0xd7e4ab5d]}
for name,keys in numeric.items():
 for mask in range(1<<len(keys)):
  for kind in [1,2]:
   g=CommandGraph();items=[(key,kind,bits((-1 if i%2 else 1)*(i+1)*.7) if kind==2 else (-3+i)&0xffffffff) for i,key in enumerate(keys) if mask&(1<<i)]
   run(g,[g.command(name,items),g.command(name)],f'numeric/{name:x}/{mask}/{kind}')
 for mode in ['included','symbol','wrong']:
  g=CommandGraph();g.symbol(0x33445566,2,bits(-7.25));items=[(keys[0],13,0x33445566)]
  if mode=='included':g.symbol(0x55667788,10,g.structure(items));items=[(0,13,0x55667788)]
  if mode=='wrong':items=[(keys[0],13,0x12345678)]
  run(g,[g.command(name,items)],f'numeric/{name:x}/{mode}')
for value in [0,1,255,256,0x80000000,0xffffffff]:
 g=CommandGraph();run(g,[g.command(0xfbb6720d,[(0x6c4e18eb,1,value)])],f'boolean/{value}')
for name,key in [(0x099cd17b,0x7f261953),(0xa075ee45,0x68977cd7),(0xb373fb6e,0xb990d003),(0x1cfbf078,0xff7ebaf6)]:
 for vector in [(0,0,0),(0,1,0),(0,1,2),(1,1,0),(.2,-.3,.4),(-180,360,45),(1e30,-1e30,1e-30)]:
  for vector_mode in [False,True]:
   g=CommandGraph();items=[(k,2,bits(v)) for k,v in zip([0x7323e97c,0x0424d9ea,0x9d2d8850],vector)]
   if vector_mode:items=[(key,6,g.vector([bits(v) for v in vector]))]+[(0x7323e97c,2,bits(123))]
   run(g,[g.command(name,items)],f'vector/{name:x}/{vector}/{vector_mode}')
for name,key in [(0xe985a9a6,0x9d2e07b3),(0xdb8621f7,0xe9c4252a),(0xe3309ab5,0)]:
 for value in [None,0,1,2,255,256,0x7fffffff,0x80000000,0xffffffff]:
  g=CommandGraph();g.put(P+0x120,'<I',0xa5a5a5a5)
  run(g,[g.command(name,[] if value is None else [(key,1,value)])],f'flag/{name:x}/{value}')
colors=[0x18a762f2,0x757a8619,0x05107296,0x9c19232c,0xd07ee8fa,0xbda30c11,0xcdc9f89e,0x54c0a924,0x043fd725,0x69e233ce,0x1988c741,0x808196fb]
for index_ in [None,-3,-1,0,2,3,4,0x7fffffff]:
 for mask in [0,1,8,15,0xf0,0xf00,0xaaa,0xfff]:
  for middle in [False,True]:
   g=CommandGraph();g.put(P+0x12d,'<B',middle)
   items=[(key,1,(-3+71*i)&0xffffffff) for i,key in enumerate(colors) if mask&(1<<i)]
   if index_ is not None:items.append((0xfec1c2fb,1,index_&0xffffffff))
   if mask&1:items.append((0x856bc5e2,2,bits(.7)))
   run(g,[g.command(0x514b2584,items)],f'color/{index_}/{mask}/{middle}')
for mask in [0,16,20,24,28,48,60,63]:
 for amount in [None,0,2,11]:
  g=CommandGraph();g.flags(mask)
  run(g,[g.command(0x711b1a6a,[] if amount is None else [(0x23bc5091,1,amount)]),g.command(0x482482c6)],f'emit/{mask}/{amount}')
# Cache encloses the complete lighting ray. Actual triangle query and virtuals
# execute; BSP-less meshes preserve the query context's initial state.
for present in [False,True]:
 for hit in [False,True]:
  for small_faces in [False,True]:
   for small_vertices in [False,True]:
    g=CommandGraph();actor,probe,vertices,points=triangle(g,small_faces,small_vertices,False)
    geometry=g.word(actor+12);faces=g.word(geometry+12)
    if small_faces:g.put(faces+4,'<4B',0,2,1,255)
    else:
     g.put(faces+4,'<3H',0,2,1)
     radius=g.alloc(4);g.put(radius,'<B',255);g.put(actor+16,'<I',radius)
    cache=g.alloc(0xfd0);g.image[cache-BASE:cache-BASE+0xfd0]=bytes(0xfd0)
    g.put(cache,'<8f',-10000,-10000,-10000,1,10000,10000,10000,1)
    g.put(cache+32,'<2I',actor,geometry+16);g.put(cache+0xfc0,'<3I',int(present),int(present),0)
    g.put(P+0x20,'<4f',4 if hit else 50,40,4 if hit else 50,1)
    calls=[g.command(0x96896315,[(0,13,0x652f5d69)]),g.command(0x96896315)]
    result=run(g,calls,f'lighting/{present}/{hit}/{small_faces}/{small_vertices}',{0x691974:cache})
    after=oracle.word(P+0xec)
    assert (after!=bits(.25))==bool(present and hit),(present,hit,hex(after))
commands=list(numeric)+[0x099cd17b,0xa075ee45,0xb373fb6e,0x1cfbf078,0xe985a9a6,0xdb8621f7,0xe3309ab5,0x482482c6,0x711b1a6a,0x514b2584,0x96896315]
for name in sorted({0,0xffffffff,*[(n+d)&0xffffffff for n in commands for d in [-1,1]]}):
 g=CommandGraph();run(g,[g.command(name)],f'unknown/{name:x}')
missing={hex(a):[hex(i.address) for i in code if not hits[i.address]] for a,code in coverage.items()};print('MISSING',json.dumps(missing),flush=True)
scope='Complete497b00 particle command dispatcher with original parameter lookup, defaults, symbols/inclusions, vector/scalar branches, signed flags, every color group, valid guarded negative color indices, emission/reset and actual collision mesh lighting with cached static triangles. Full arena/globals/returns/heap comparison, no replacement game callbacks. Finite numeric inputs and initialized buffers; explicit BSP query context inherited from recovered collision code. No full particle frame, renderer or playability claimed.'
finish('particle-command',scope,{},extra)
