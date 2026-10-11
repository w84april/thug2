"""Original file-mesh path and shader skipping, with existing bounded GPU ports."""
from pathlib import Path
exec(compile(Path('local/analysis/probe-vertex-upload.py').read_text().split('\nspecs=')[0],'<preserved vertex fixture setup>','exec'))
IOCTRL,IOLOG=BASE+0x1a000,BASE+0x30000
put(IOCTRL,'<I',0)
for i in range(6):globals_.append(['thug_mesh_vertex_formats_draft',0x775b64+i*4,4,i*4]);defaults.append(0x152+i*0x100)
globals_.append(['thug_mesh_index_registry',0x7865e8,4]);defaults.append(0)
globals_.append(['thug_mesh_shader_conversion_enabled_draft',0x786ab8,1]);defaults.append(0)
globals_ += [['thug_scene_file_read_draft',0x340,4],['thug_scene_file_seek_draft',0x344,4]];defaults += [0x5b9ee0,0x5b9fa0]
stream_ports=Path('local/analysis/probe-level-material.py').read_text().split('def file_port(',1)[1].split('# Reuse the same',1)[0]
exec(compile(('def file_port('+stream_ports).replace('i<40000','i<2000'),'<recorded stream ports>','exec'))
initial=bytes(memory);oracle.initial=initial
specs=[(0x4d6100,1038,'thug_mesh_file_parse_draft',5,'void',True,True),(0x4da6d0,61,'thug_mesh_file_shader_skip_draft',1,'word',False,False)]
for a,n,name,argc,result,this,heap in specs:
 functions[hex(a)]={'name':name,'this':this,'result':result,'cleanup':argc*4 if this else 0,'memory':heap}
 code[a]=list(md.disasm(pe.get_data(a-0x400000,n),a));oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:hits.update([at]),begin=a,end=a+n-1)
(folder/'level-mesh-instructions.txt').write_text('\n'.join(line for a,n,*_ in specs for line in [f'FUNCTION {a:08x} {n} bytes']+[f'{i.address:08x} {i.mnemonic} {i.op_str}' for i in code[a]])+'\n')
def packet(indices=(3,0,0,0,0,0,0,0),sizes=(17,),formats=(0x152,0),palette=0,passes=1,shader=0,vertices=3,stride=36):
 data=b''
 for n in indices:data+=struct.pack('<H',n)+b''.join(struct.pack('<H',i%max(vertices,1)) for i in range(n))
 data+=struct.pack('<BHB',stride,vertices,len(sizes))
 for j,n in enumerate(sizes):data+=struct.pack('<BI',0,n)+bytes((i*19+j*17+3)&255 for i in range(n))
 data+=struct.pack('<2I4B',*formats,7,8,9,palette)
 if palette:data+=bytes((i+2)&255 for i in range(vertices))
 data+=struct.pack('<I',passes)
 if 1<passes<0x80000000:data+=b''.join(struct.pack('<I',i*37+9) for i in range(passes))
 data+=struct.pack('<I',shader)
 if shader==1:data+=struct.pack('<2I',0xabcdef01,9)+b'123456789'
 return data
def check(label,dynamic=0,aux=False,material='ordinary',fill=0xa5,lock=0,**options):
 g=Graph();g.data[P-BASE:P-BASE+216]=bytes([fill])*216
 header=P+0x300;owner=P+0x400;g.put(owner,'<3I',0xabcd,0xdcba,0xffffffe0)
 value=g.alloc(0x110);g.put(value,'<I',0x1234);g.put(value+0x20,'<I',0x10 if material=='flag' else 0)
 table=g.table([(0x1234,value)]);g.put(header+0x18,'<I',0 if material=='absent' else table)
 g.file(packet(**options));g.put(INDEXCTL+12,'<I',lock);g.put(INDEXCTL+24,'<I',int(lock<0x80000000))
 key=0xabcd if material=='missing' else 0x1234
 run(g,[call(0x4d6100,P,[CURSOR,key,header,owner if aux else 0,dynamic])],label)
 assert oracle.word(CURSOR)==INPUT+len(packet(**options)),label
for dynamic in [0,1,255,256,257,0xffffffff]:
 for palette in [0,1,255]:
  for aux in [False,True]:check(f'usage {dynamic:x}/palette{palette}/aux{aux}',dynamic=dynamic,palette=palette,aux=aux)
for fill in [0,0xa5,0xff]:
 for material in ['ordinary','flag','absent','missing']:check(f'fill{fill}/material{material}',material=material,fill=fill)
for slots in [(0,)*8,(1,2,3,4,5,6,7,0),(0,0,0,0,0,0,0,17)]:check(f'index slots{slots}',indices=slots)
for size in [0,1,2,3,4,5,31,32,33,4097]:
 for streams in [1,2,3]:check(f'bytes{size}/streams{streams}',sizes=(size,)*streams)
for code0 in [1,2,3,4,5,6,7,0x152,0xffffffff]:
 for code1 in [0,1,6,0x152]:check(f'formats{code0:x}/{code1:x}',formats=(code0,code1))
for passes in [0,1,2,4,0x80000000,0xffffffff]:check(f'passes{passes:x}',passes=passes)
for shader in [*range(21),0x80000000,0xffffffff]:check(f'shader{shader:x}',shader=shader)
for lock in [1,0xffffffff,0x80000000]:check(f'lock{lock:x}',lock=lock)
for size in [0,1,4,16,0xffffffff,0xfffffff8,0x80000000]:
 g=Graph();g.file(struct.pack('<2I',0xabcdef01,size));run(g,[call(0x4da6d0,0,[CURSOR])],f'shader skip{size:x}')
coverage={hex(a):{'total':len(c),'covered':sum(bool(hits[i.address]) for i in c),'missing':[hex(i.address) for i in c if not hits[i.address]]} for a,c in code.items()}
assert not coverage['0x4da6d0']['missing'];print('COVERAGE',json.dumps(coverage),flush=True)
clang=ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang';port=folder/'level-mesh-ports.c';output=folder/'level-mesh-ports.wasm'
cmd=[str(clang),'--target=wasm32-unknown-unknown','-O2','-nostdlib','-Wl,--no-entry,--export-all,--import-memory',str(port),'-o',str(output)];subprocess.run(cmd,check=True)
output.with_suffix('.build.json').write_text(json.dumps({'command':cmd,'source_sha256':hashlib.sha256(port.read_bytes()).hexdigest(),'sha256':hashlib.sha256(output.read_bytes()).hexdigest()},indent=2)+'\n')
prior=json.loads((folder/'vertex-upload-fixtures.json').read_text())
callbacks=[{**c,'module':'level-mesh-ports.wasm'} for c in prior['native_callbacks']]
callbacks += [{'module':'level-mesh-ports.wasm','export':'fixture_scene_read','original':0x5b9ee0},{'module':'level-mesh-ports.wasm','export':'fixture_scene_seek','original':0x5b9fa0}]
scope='Partial original file-mesh4d6100 standard vertex path returns after exact stream reads, index and vertex uploads, material lookup, palette/usage flags, pass data, shader selection and temporary release. Correction4d4350, packed-vertex4d5940 and shader conversion4ddc00 remain explicit traps. Complete shader-file skip4da6d0. Bounded successful internal allocations and complete records; no rendering.'
fixture={**prior,'memory':'level-mesh-memory.bin','globals':globals_,'pointer_globals':[len(globals_)-2,len(globals_)-1],'functions':functions,'cases':oracle.cases,'case_labels':labels,'pointer_fields':sorted(fields),
 'pointer_initializers':prior['pointer_initializers']+[['thug_scene_file_read_draft',0x5b9ee0],['thug_scene_file_seek_draft',0x5b9fa0]],'native_callbacks':callbacks,'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'level-mesh-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(oracle.counts.values()),'instruction_coverage':coverage,'index_calls':dict(index_calls),'crt_calls':dict(crt_calls),'scope':scope}
(folder/'level-mesh-original.json').write_text(json.dumps(report,indent=2)+'\n');print('REPORT',len(labels),'cases',sum(oracle.counts.values()),'calls',flush=True)
