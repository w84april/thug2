"""Original quaternion-to-matrix and node orientation, including untouched words."""
from pathlib import Path
exec(compile(Path('local/analysis/composite-construction-fixture-setup.py').read_text(),'<composite setup>','exec'))
bind_new(0x42bc40,274,'thug_quaternion_basis_draft',1)
bind_new(0x45c0b0,195,'thug_node_orientation_draft',2,this=False)
basis=[0,1,2,4,5,6,8,9,10]
rng=random.Random(0x42bc40)
vectors=[[bits(x) for x in q] for q in [(0,0,0,0),(0,0,0,1),(1,0,0,0),(0,1,0,0),(0,0,1,0),(.2,-.3,.4,.5),(-1,-2,3,-4),(1e-40,2e-40,-3e-40,4e-40),(1e30,-2e30,3e30,-4e30)]]
vectors += [[rng.getrandbits(32) for j in range(4)] for i in range(96)]
for special in [0,0x80000000,1,0x80000001,0x007fffff,0x00800000,0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc12345,0xffc23456,0x7f812345,0xffa23456]:
    for axis in range(4):
        q=[bits(.25),bits(-.5),bits(.125),bits(.75)];q[axis]=special;vectors.append(q)
for i,q in enumerate(vectors):
    g=CompositeGraph();out=g.alloc(80);src=g.alloc(16)
    for j in range(20):g.put(out+j*4,'<I',rng.getrandbits(32))
    g.put(src,'<4I',*q)
    stages=case([call(0x42bc40,src,[out])],g.patches(),label=f'quaternion {i}')
    stages[0]['float_fields']=[out+j*4 for j in basis]
# The converter consumes all quaternion words before output stores, even when
# input and output overlap. Unwritten matrix words remain exact raw payloads.
for offset in [0,4,16,32,48]:
    g=CompositeGraph();out=g.alloc(80)
    for j in range(20):g.put(out+j*4,'<I',0xa5a50000+j)
    g.put(out+offset,'<4f',.1,-.2,.3,.4)
    case([call(0x42bc40,out+offset,[out])],g.patches(),label=f'alias quaternion +{offset}')
for mode in ['missing','wrong','direct','included','indirect']:
    for i,q in enumerate(vectors[:9]+vectors[-56:]):
        g=CompositeGraph();out=g.alloc(64)
        for j in range(16):g.put(out+j*4,'<I',0x7f812300+j)
        v=g.vector(q[:3]);items=[] if mode=='missing' else [(0xc97f3aa9,1 if mode=='wrong' else 6,v)]
        if mode=='indirect':g.symbol(0x12004321,6,v);items=[(0xc97f3aa9,13,0x12004321)]
        node=g.structure(items)
        if mode=='included':g.symbol(0x54321001,10,node);node=g.structure([(0,13,0x54321001)])
        stages=case([call(0x45c0b0,args=[node,out])],g.patches(),label=f'node {mode} {i}')
        stages[0]['float_fields']=[out+j*4 for j in basis]
finish('composite-math','Two original functions: quaternion basis conversion and optional node quaternion orientation. All finite arithmetic and all non-output bytes compare exactly. Only the nine arithmetic basis outputs permit NaN classification; input signaling payloads and seven untouched output words remain exact. Original x87 PC24 operation order, float spills, wider stack exponents, zero-length fallback, norm clamp, overlaps, included structures and checksum indirection are exercised. No scene instantiation or rendering is implied.',extra=extra)
