"""Compare the actual SimpleSound factory and initializer required by training."""
from pathlib import Path
source=Path('local/analysis/probe-texture-buffer.py').read_text().split('for fill in [0,0xa5,0xff]:')[0]
exec(compile(source,'<preserved bounded comparison arena>','exec'))
functions.clear();code.clear();hits.clear();labels.clear()
put(CONTEXT+32,'<I',0);initial=bytes(memory)
PROX,PARAMS=P+0x800,P+0x400
globals_.append(['thug_proximity_manager_draft',0x6f2268,4]);defaults.append(PROX)
class FactoryOracle(ScriptHeapOracle):
 def heap(self,cpu,address,size,user):
  if address in [0x5bbae0,0x5bafc0] and self.word(CONTEXT+32):
   sp=cpu.reg_read(UC_X86_REG_ESP);self.setword(CONTEXT+32,0)
   ScriptHeapOracle.record(self,1,self.word(sp+4),int(address==0x5bafc0),0)
   cpu.reg_write(UC_X86_REG_EAX,0);cpu.reg_write(UC_X86_REG_EIP,self.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4+(12 if address==0x5bafc0 else 0));return
  super().heap(cpu,address,size,user)
oracle=FactoryOracle(initial,BASE,CONTEXT,MANAGER,globals_,defaults,functions)
original_record=oracle.record
oracle.record=record
specs=[(0x433d90,121,'simple_sound_create',False,0,'word',True),(0x433900,48,'simple_sound_initialize',True,1,'void',False)]
for a,n,name,this,argc,result,heap in specs:
 functions[hex(a)]={'name':'thug_'+name+'_draft','this':this,'result':result,'cleanup':argc*4 if this else 0,'memory':heap}
 code[a]=list(md.disasm(pe.get_data(a-0x400000,n),a));oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:hits.update([at]),begin=a,end=a+n-1)
exports += [[0x646594,'thug_simple_sound_methods_draft'],[0x647618,'thug_component_methods']]
for failure in [0,1]:
 g=Graph();g.put(CONTEXT+32,'<I',failure);run(g,[call(0x433d90)],'factory allocation failure'+str(failure))
for poison in [0,0xa5,0xff]:
 for field in ['absent','wrong type','zero','match','collision','duplicate','missing']:
  g=Graph();g.data[P-BASE:P-BASE+0x2c]=bytes([poison])*0x2c;g.put(PARAMS,'<2I',0,0);g.put(PROX,'<I',0)
  if field!='absent':
   item=g.alloc(16);g.put(item,'<4I',2 if field=='wrong type' else 26,0x08470f2e,0 if field=='zero' else 0x13579bdf,0);g.put(PARAMS+4,'<I',item)
  if field in ['match','collision','duplicate','missing','zero']:
   nodes=[g.alloc(0xa8) for _ in range(3)];g.put(PROX,'<I',nodes[0])
   keys=[0,1,2] if field=='zero' else [0x13579bdf,1,2] if field=='match' else [1,0x13579bdf,0x13579bdf] if field=='duplicate' else [1,2,0x13579bdf] if field=='collision' else [1,2,3]
   for i,node in enumerate(nodes):g.put(node,'<I',keys[i]);g.put(node+0xa4,'<I',nodes[i+1] if i<2 else 0)
  run(g,[call(0x433900,P,[PARAMS])]*2,f'initialize poison{poison}/{field}')
# Initialization through the newly allocated component uses its actual factory.
g=Graph();g.put(PARAMS,'<2I',0,0);g.put(PROX,'<I',0)
run(g,[call(0x433d90),call(0x433900,HEAP,[PARAMS])],'factory then initializer')
coverage={hex(a):{'total':len(c),'covered':sum(bool(hits[i.address]) for i in c),'missing':[hex(i.address) for i in c if not hits[i.address]]} for a,c in code.items()}
assert all(not c['missing'] for c in coverage.values()),coverage
for case in oracle.cases:
 for step in case['steps']:
  for at,data in step['outputs']:
   if int.from_bytes(bytes.fromhex(data),'little') in {e[0] for e in exports}:fields.add(at)
clang=ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang';port=folder/'scene-create-memory.c';output=folder/'scene-create-memory.wasm'
cmd=[str(clang),'--target=wasm32-unknown-unknown','-O2','-nostdlib','-Wl,--no-entry,--export-all,--import-memory',str(port),'-o',str(output)];subprocess.run(cmd,check=True)
output.with_suffix('.build.json').write_text(json.dumps({'command':cmd,'source_sha256':hashlib.sha256(port.read_bytes()).hexdigest(),'sha256':hashlib.sha256(output.read_bytes()).hexdigest()},indent=2)+'\n')
scope='Two complete SimpleSound routines: actual zeroed44-byte factory including allocation failure, and proximity initializer preserving the old pointer when the field is absent or wrong typed, otherwise storing the first matching original proximity node or null. All original instructions, whole arena/globals/heap/returns and preserved registers compare. Method bindings reuse recovered originals. Component destruction and sound playback commands remain unavailable, not success stubs.'
fixture={'base':BASE,'memory':'scene-create-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'scene-create-memory.wasm','memory_exports':['fixture_scene_allocate','fixture_values_release','fixture_values_scope'],
 'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'pointer_fields':sorted(fields),'pointer_exports':exports,'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'scene-create-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(len(c['steps']) for c in oracle.cases),'instruction_coverage':coverage,'scope':scope}
(folder/'scene-create-original.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
