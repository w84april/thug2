"""Run original model parser/finalization with real minimal models and companions."""
from pathlib import Path
source=Path('local/analysis/probe-model-asset.py').read_text().split('for explicit in [False,True]:')[0]
exec(compile(source,'<preserved heap/file/cache/CRT setup>','exec'))
import random
functions.clear();code.clear();hits.clear();oracle.counts.clear();oracle.coverage.clear()
oracle.setword(0x645888+0x34,0x409c70)
specs=[(0x409c70,187,'model_asset_parse',2,'void',True,True),
 (0x4b7af0,62,'model_companion_compare',2,'word',False,False),
 (0x4b7c60,225,'model_companion_parse',1,'word',True,True),
 (0x4b7eb0,21,'model_companion_load',1,'void',True,True)]
for a,n,name,argc,result,heap,this in specs:
 functions[hex(a)]={'name':'thug_'+name+'_draft','this':this,'result':result,'cleanup':argc*4 if this else 0,'memory':heap}
 code[a]=list(md.disasm(pe.get_data(a-0x400000,n),a));oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:hits.update([at]),begin=a,end=a+n-1)
for a,name,argc,result in [(0x409c40,'model_asset_initialize',0,'word'),(0x409e10,'model_asset_options',2,'void')]:
 functions[hex(a)]={'name':'thug_'+name+'_draft','this':True,'result':result,'cleanup':argc*4,'memory':False}
exports += [[0x6459a8,'thug_texture_asset_methods_draft'],[0x6499e0,'thug_model_scene_base_methods_draft'],[0x64a6b8,'thug_model_scene_pc_methods_draft'],
 [0x6499dc,'thug_model_scene_list_methods_draft'],[0x6492e4,'thug_model_object_base_methods_draft'],[0x64a490,'thug_model_object_pc_methods_draft']]
for a in [0x49c2a0,0x4c65d0,0x490a60,0x4b7b30]:oracle.cpu.hook_add(UC_HOOK_CODE,identity,begin=a,end=a)
for i in range(6):globals_.append(['thug_model_render_cache_draft',0x7865cc+i*4,4,i*4]);defaults.append(0xabcdef01+i)
oracle.globals=globals_;oracle.defaults=defaults
wrapper_code={a:list(md.disasm(pe.get_data(a-0x400000,n),a)) for a,n in [(0x4b3ad0,215),(0x48c030,70)]};wrapper_hits=Counter()
for a,c in wrapper_code.items():oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:wrapper_hits.update([at]),begin=a,end=c[-1].address)

def companion_data(version,keys):
 values=[version]+([0x76543210] if version>=2 else [])+[len(keys)]
 for i,key in enumerate(keys):values += [0x100+i,key,0xfedc0000+i]
 return struct.pack('<'+'I'*len(values),*values)
for x,y in [(0,0),(0,1),(1,0),(0xffff,0x10000),(0x10000,0xffff),(0x80000000,0x7fffffff),(0xffffffff,0xffffffff),(0xfffffffe,0xffffffff),(0xffffffff,0xfffffffe)]:
 g=AssetGraph();a=g.alloc(16);b=g.alloc(16);g.put(a+4,'<I',x);g.put(b+4,'<I',y)
 run(g,[call(0x4b7af0,args=[a,b]),call(0x4b7af0,args=[b,a])],f'companion compare{x:x}/{y:x}')
rng=random.Random(0x4b7c60)
for version in [0,1,2,0xffffffff]:
 for count in [0,1,2,8,9,33]:
  for order in ['forward','reverse','random','ties']:
   keys=[0x10000*(i%3)+i for i in range(count)] if order!='ties' else [7]*count
   if order=='reverse':keys.reverse()
   if order=='random':rng.shuffle(keys)
   g=AssetGraph();data=companion_data(version,keys);g.file(data);g.put(CURSOR,'<I',INPUT)
   run(g,[call(0x4b7c60,P,[CURSOR])],f'companion version{version:x}/n{count}/{order}')
   assert oracle.word(CURSOR)==INPUT+len(data) and oracle.word(P+0xc0)==count
   if count:
    records=oracle.word(P+0xbc);actual=[oracle.word(records+i*16+4) for i in range(count)];assert actual==sorted(keys)
    assert all(oracle.word(records+i*16+12)==0 for i in range(count))
for present in [False,True]:
 for count in [0,3]:
  g=AssetGraph();g.file(companion_data(2,[3,1,2][:count]));run(g,[call(0x4b7eb0,P,[INPUT if present else 0])],f'companion load present{present}/n{count}')

# Exercise the complete original409c70 using actual48c030/4b3ad0 and zero-sector
# model files. File/cache providers only record I/O; no parser result is supplied.
models=[]
for release in [0,1]:
 for primary in [False,True]:
  for companion in [False,True]:
   for files in [0,1,2,3]:
    g=AssetGraph();g.file(struct.pack('<6I',1,1,1,0,0,0));dictionary=g.alloc(32);g.put(dictionary+12,'<I',g.table())
    dependency=g.alloc(0x60);g.put(dependency,'<I',0x6459a8);g.put(dependency+0x10,'<I',dictionary);fields.add(dependency)
    options=g.alloc(20);g.data[options-BASE:options-BASE+20]=bytes(20);g.put(options+17,'<B',release)
    second=g.alloc(48) if companion else 0
    if second:
     data=companion_data(2,[0x10000,1,1]);g.data[second-BASE:second-BASE+len(data)]=data
    g.put(options+8,'<I',second)
    key=[0,1,0xffffffff,0x80000000][files];g.put(P+4,'<I',key);g.put(P+0x34,'<I',dependency)
    # Constructor overwrites50/54/58, so set those fields after it in the next
    # step via a separate case continuation below, without instrumenting code.
    g.put(P,'<I',0x645888);g.put(P+8,'<I',1);g.put(P+0x10,'<I',0)
    g.put(P+0x20,'<I',FILE if files&1 else 0);g.put(P+0x24,'<I',INPUT if primary else 0)
    g.put(P+0x4c,'<I',0);g.put(P+0x54,'<I',FILE+0x80 if files&2 else 0);g.put(P+0x58,'<I',second)
    fields.add(P)
    run(g,[call(0x409e10,P,[options,0]),call(0x409c70,P,[INPUT,24])],f'asset ready release{release}/primary{primary}/companion{companion}/files{files}')
    model=oracle.word(P+0x10);assert model and oracle.word(model)==0x64a490 and oracle.word(model+4)==dictionary
    assert oracle.word(P+8)==4 and oracle.word(P+0x20)==0 and oracle.word(P+0x50)==0 and oracle.word(P+0x54)==0 and oracle.word(P+0x58)==0
    assert oracle.word(MASK)==0 and oracle.word(P+0x24)==(0 if release else INPUT if primary else 0)
    models.append({'model':hex(model),'scene':hex(oracle.word(model+0xc4)),'key':hex(key),'companion':companion,'release':release,'files':files})
# Cache release by key also belongs to409c70's release-buffer virtual branch.
g=AssetGraph();g.file(struct.pack('<6I',1,1,1,0,0,0));dictionary=g.alloc(32);g.put(dictionary+12,'<I',g.table());dependency=g.alloc(96);g.put(dependency,'<I',0x6459a8);g.put(dependency+0x10,'<I',dictionary);fields.add(dependency)
options=g.alloc(20);g.data[options-BASE:options-BASE+20]=bytes(20);g.put(options+17,'<B',1)
g.put(P,'<I',0x645888);g.put(P+0x34,'<I',dependency);g.put(P+4,'<I',0x7fffffff);g.put(P+0x20,'<I',0);g.put(P+0x24,'<I',INPUT);g.put(P+0x4c,'<I',0x87654321);g.put(P+0x54,'<2I',0,0)
run(g,[call(0x409e10,P,[options,0]),call(0x409c70,P,[INPUT,24])],'asset ready cached primary release')
assert oracle.word(P+0x24)==0 and oracle.word(P+0x4c)==0 and oracle.word(P+8)==4
coverage={hex(a):{'total':len(c),'covered':sum(bool(hits[i.address]) for i in c),'missing':[hex(i.address) for i in c if not hits[i.address]]} for a,c in code.items()}
print('COVERAGE',json.dumps(coverage),flush=True)
for case in oracle.cases:
 for at,data in case.get('patches',[]):
  if int.from_bytes(bytes.fromhex(data),'little') in {e[0] for e in exports}:fields.add(at)
scope='Four routines recover model companion sorting/parsing/loading and asset parse/finalization. Original model wrappers and geometry execute on real zero-sector files; every cleanup branch and file/cache release is compared without substituting parser success. The separate training comparison uses the unchanged Letter S files. Complete arena/globals/heap/I-O effects compare; full general geometry and rendering remain pending.'
fixture={'base':BASE,'memory':'asset-ready-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'texture-buffer-ports.wasm','memory_exports':['fixture_texture_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'pointer_fields':sorted(fields),'pointer_exports':exports,
 'native_callbacks':[{'module':'model-asset-ports.wasm','export':'fixture_model_'+name,'slots':[IO+(i+1)*4]} for i,name in enumerate(['open','size','read','close'])]+[{'module':'model-asset-ports.wasm','export':'fixture_model_'+name,'slots':[CACHE_IO+(i+1)*4]} for i,name in enumerate(['acquire','cached_size','cached_release'])],'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'asset-ready-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(len(c['steps']) for c in oracle.cases),'instruction_coverage':coverage,
 'partial_wrapper_coverage':{hex(a):{'total':len(c),'covered':sum(bool(wrapper_hits[i.address]) for i in c),'missing':[hex(i.address) for i in c if not wrapper_hits[i.address]],'complete':False} for a,c in wrapper_code.items()},'model_cases':models,'scope':scope}
(folder/'asset-ready-original.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
