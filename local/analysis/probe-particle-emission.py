"""Complete original particle emission and geometry/virtual prerequisites."""
from pathlib import Path
exec(compile(Path('local/analysis/probe-particle-setup.py').read_text().split('for fn in [0x497790')[0],'<preserved initialized particle services>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
for a,n,name,argc,result in [(0x52dac0,6,'particle_one_segment',0,'word'),(0x49bb70,6,'particle_four_colors',0,'word'),
 (0x4968b0,33,'particle_extents',3,'void'),(0x4968e0,33,'particle_acceleration',3,'void'),(0x496910,33,'particle_direction',3,'void'),(0x496940,33,'particle_angles',3,'void'),
 (0x41d9c0,51,'particle_flag',2,'void'),(0x4969f0,324,'particle_basis',1,'void'),(0x496fe0,1959,'particle_emit',1,'void')]:bind_new(a,n,'thug_'+name+'_draft',argc,result)
for a,n,name,argc,result in [(0x410980,57,'collision_static_vertex',2,'word'),(0x412230,129,'collision_moving_vertex',2,'word'),(0x4174a0,611,'collision_probe_light',0,'double')]:bind_new(a,n,'thug_'+name+'_draft',argc,result)
exports.extend([[0x645c18,'thug_static_collision_methods'],[0x645ce0,'thug_moving_collision_methods']])
initial=bytes(memory);oracle.initial=initial
class EmissionGraph(SetupGraph):
 def __init__(self,capacity=7,first=0):
  super().__init__();self.image[P-BASE:P-BASE+0x138]=bytes(0x138)
  self.put(P,'<I',0x64a5ac);fields.add(P)
  self.put(P+0x7c,'<I',capacity);self.put(P+0x8c,'<I',first)
  self.records=self.alloc(48*(capacity+2))+48;self.positions=self.alloc(12*(capacity+2))+12
  self.put(P+0xf8,'<I',self.records);self.put(P+0x11c,'<I',self.positions)
  self.put(P+0x20,'<4f',1,2,-3,1);self.put(P+0x30,'<4f',2,-4,7,1)
  self.put(P+0x90,'<16f',1,2,3,4,5,.3,.1,-.2,.3,1,2,3,4,1,.2,.7)
  self.put(P+0xd0,'<3f',.3,1,-.2)
 def matrix(self):
  matrix=self.alloc(64);self.put(matrix,'<16f',.7,.1,-.2,0,.2,.9,.3,0,.1,-.3,.8,0,2,3,4,1)
  self.put(P+0xdc,'<I',matrix);return matrix
 def flags(self,mask):
  for i,o in enumerate([0x125,0x126,0x128,0x129,0x12c,0x131]):self.put(P+o,'<B',bool(mask&(1<<i)))
def run_emission(g,calls,label,changes=None):
 try:result=case(calls,g.patches(),changes,label)
 except Exception:print('FAILED',label,flush=True);raise
 if len(labels)%25==0:print('Original emission cases',len(labels),flush=True)
 return result
for raw in [0,0x80000000,0x7f812345,0xffc12345,0x7f800000,0xffffffff,0x3f000000]:
 g=EmissionGraph();calls=[call(0x52dac0,P),call(0x49bb70,P)]
 calls += [call(a,P,[raw,raw^0x80000000,0x12345678]) for a in [0x4968b0,0x4968e0,0x496910,0x496940]]
 run_emission(g,calls,f'raw setters/{raw:x}')
for flag in [0,4,8,31,32,63,0xffffffff]:
 for enabled in [0,1,255,256,257,0xffffffff]:
  g=EmissionGraph();g.put(P+0x120,'<I',0xa5a5a5a5)
  run_emission(g,[call(0x41d9c0,P,[flag,enabled])]*2,f'flag/{flag}/{enabled}')
for vector in [(0,0,0),(0,1,0),(0,-1,0),(1,0,0),(0,0,-1),(.3,1,-.2),(.01,.99,.1),(1e30,2e30,-3e30),(1e-30,-2e-30,3e-30)]:
 for out in [P+0x200,P+0xb0,P+0xc0,P+0xd0]:
  g=EmissionGraph();g.put(P+0xd0,'<3f',*vector)
  run_emission(g,[call(0x4969f0,P,[out])],f'basis/{vector}/{out}')
for offset in [-4,0,4,16,64]:
 g=EmissionGraph();matrix=g.matrix();run_emission(g,[call(0x4969f0,P,[matrix+offset])],f'explicit matrix alias/{offset}')
for seed in [0,1,0x12345678,0xffffffff]:
 for mask in range(64):
  g=EmissionGraph();g.flags(mask)
  if mask&8:g.matrix()
  if mask&4:g.put(P+0xc4,'<f',.7)
  if mask&2:g.put(P+0x30,'<4f',1,2,-3,1)
  run_emission(g,[call(0x496fe0,P,[2]),call(0x496fe0,P,[3]),call(0x496fe0,P,[5])],f'emit flags/{seed}/{mask}',{PTLS+0x14:seed})
for capacity in [0,1,7]:
 for first in sorted({0,capacity,min(capacity,2)}):
  for amount in [0,1,3,11]:
   for moving in [False,True]:
    g=EmissionGraph(capacity,first);g.flags(16 if moving else 0)
    run_emission(g,[call(0x496fe0,P,[amount])],f'capacity/{capacity}/{first}/{amount}/{moving}')
for amount in [0xffffffff,0xfffffffe]:
 g=EmissionGraph(first=3);g.flags(16);run_emission(g,[call(0x496fe0,P,[amount])],f'negative amount/{amount}')
# Broad finite exponents distinguish x87 register values from float spills.
for scale in [1e-15,1e15,1e-30,1e30]:
 for mask in [16,24,28,48,56,60]:
  g=EmissionGraph();g.flags(mask);g.put(P+0x90,'<5f',scale,2*scale,scale,-scale,.5*scale)
  g.put(P+0xc8,'<2f',scale,2*scale);g.put(P+0xa4,'<f',.7)
  run_emission(g,[call(0x496fe0,P,[2])],f'wide/{scale}/{mask}')
# Real static and moving collision vertex methods, then vertex-light interpolation.
def triangle(g,small_faces,small_vertices,moving,lights=(0,128,255)):
 geometry=g.alloc(64);g.image[geometry-BASE:geometry-BASE+64]=bytes(64)
 faces=g.alloc(12);vertices=g.alloc(36);aux=g.alloc(4);actor=g.alloc(0xd4);probe=g.alloc(0xb0)
 g.image[actor-BASE:actor-BASE+0xd4]=bytes(0xd4);g.image[probe-BASE:probe-BASE+0xb0]=bytes(0xb0)
 points=[(0.,0.,0.),(16.,4.,0.),(0.,-8.,16.)]
 g.put(geometry,'<IHHHBBI',0x12345678,0,3,1,small_faces,small_vertices,faces)
 g.put(geometry+16,'<8f',-32,-32,-32,1,32,32,32,1)
 g.put(geometry+48,'<4I',vertices,0,aux,bits(1))
 if small_faces:g.put(faces,'<4B3BB',0,0,0,0,0,1,2,0)
 else:g.put(faces,'<5H',0,0,0,1,2)
 if small_vertices:g.put(vertices,'<9H',*[int((v+32)*16) for p in points for v in p])
 else:g.put(vertices,'<9f',*[v for p in points for v in p])
 g.put(aux,'<3B',*lights);g.put(actor,'<I',0x645ce0 if moving else 0x645c18);fields.add(actor);g.put(actor+12,'<I',geometry)
 matrix=[.8,0,-.6,0,0,1,0,0,.6,0,.8,0,0,0,0,1]
 if moving:g.put(actor+16,'<4f',3,4,-5,1);g.put(actor+32,'<16f',*matrix)
 def world(point):
  if not moving:return point
  return tuple(sum(point[k]*matrix[k*4+j] for k in range(3))+[3,4,-5][j] for j in range(3))
 g.put(probe+0x44,'<I',0);g.put(probe+0x54,'<I',actor);g.put(probe+0x6c,'<B',1)
 return actor,probe,vertices,[world(p) for p in points]
for small_faces in [False,True]:
 for small_vertices in [False,True]:
  for moving in [False,True]:
   for lights in [(0,128,255),(255,7,128),(33,33,33)]:
    for weights in [(.2,.3,.5),(.7,.1,.2),(-.2,.6,.6),(.1,.8,.1)]:
     g=EmissionGraph();actor,probe,vertices,points=triangle(g,small_faces,small_vertices,moving,lights)
     hit=[sum(weights[k]*points[k][j] for k in range(3)) for j in range(3)];g.put(probe+0x34,'<3f',*hit)
     fn=0x412230 if moving else 0x410980
     run_emission(g,[call(fn,actor,[P+0x200,i]) for i in range(3)]+[call(0x4174a0,probe)],f'light/{small_faces}/{small_vertices}/{moving}/{lights}/{weights}')
for moving in [False,True]:
 for out_kind in ['distinct','position','orientation','vertices']:
  g=EmissionGraph();actor,probe,vertices,points=triangle(g,False,False,moving)
  out={'distinct':P+0x200,'position':actor+16,'orientation':actor+32,'vertices':vertices+4}[out_kind]
  run_emission(g,[call(0x412230 if moving else 0x410980,actor,[out,1])],f'vertex alias/{moving}/{out_kind}')
g=EmissionGraph();g.put(P+0x6c,'<B',0);run_emission(g,[call(0x4174a0,P)],'light miss default')
missing={hex(a):[hex(i.address) for i in code if not hits[i.address]] for a,code in coverage.items()};print('MISSING',json.dumps(missing),flush=True)
excluded={hex(a):'Unreachable alignment instructions skipped by unconditional jumps.' for a in [0x497047,0x49704e,0x4975da]}
scope='Twelve complete particle emission and mesh-lighting routines: raw parameter setters, bit flags, real point/buffer segment and color-count virtual methods, explicit or direction-derived basis, complete496fe0 emission. Deterministic original CRT randomness, frozen and moving records, velocity/spread, independent random shape, elliptical distribution, prior-position interpolation, local/world positions, lifetimes, clamping, negative count reduction and wide finite inputs. Actual point-class virtual dispatch; no substituted game callback. Valid finite input graphs and bounded readable/writable buffers. Original static/moving vertex transforms and collision-hit vertex-light interpolation on nondegenerate geometry, including compressed vertices, both face formats and aliases. Full arena, global state, returns and heap compare; no full particle frame, rendering or playability claimed.'
finish('particle-emission',scope,excluded,extra)
