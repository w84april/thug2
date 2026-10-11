"""Original Model component and nested renderer construction, no fake objects."""
from pathlib import Path
source=Path('local/analysis/probe-prop-lifecycle.py').read_text().split('# Constructor/reset fields')[0]
exec(compile(source,'<preserved initialized prop oracle>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.coverage.clear()
specs=[(0x5bc7f0,5,'model_virtual_true',1,'byte',False,True),
 (0x494c40,189,'model_renderer_base_construct',0,'word',True,True),
 (0x4bad90,25,'model_renderer_construct',0,'word',True,True),
 (0x4b29c0,86,'model_renderer_create',0,'word',True,False),
 (0x48bfa0,5,'model_renderer_factory',1,'word',True,False),
 (0x420bf0,275,'model_component_construct',0,'word',True,True),
 (0x421490,89,'model_component_create',0,'word',True,False)]
for a,n,name,argc,result,heap,this in specs:bind_new(a,n,'thug_'+name+'_draft',argc,result,heap,this=this)
exports += [[0x649348,'thug_model_renderer_base_methods_draft'],[0x64a4b4,'thug_model_renderer_methods_draft'],[0x646128,'thug_model_component_methods_draft']]
function_exports.append([0x421490,'thug_model_component_create_draft'])
for a in [0x494c40,0x4bad90,0x420bf0]:oracle.cpu.hook_add(UC_HOOK_CODE,identities,begin=a,end=a)
for ctor,size in [(0x494c40,0x4c),(0x4bad90,0x50),(0x420bf0,0x238)]:
 for fill in [0,0xa5,0xff]:
  g=PropGraph();g.image[P-BASE:P-BASE+size]=bytes([fill])*size
  run(g,[call(ctor,P)]*2,f'constructor {ctor:x} retained bytes {fill}')
for kind in [0,1,6,0xffffffff]:
 for flag in [0,1,4,8,16,32,64,128,255]:
  g=PropGraph();g.put(P+4,'<I',kind);g.put(P+0x44,'<I',0xaabbcc00|flag)
  run(g,[call(0x494c40,P)],f'renderer type{kind}/flags{flag}')
for arg in [0,1,256,0xffffffff]:
 g=PropGraph();run(g,[call(0x5bc7f0,P,[arg]),call(0x48bfa0,args=[arg])],f'actual shared true and ignored factory argument {arg}')
for factory in [0x4b29c0,0x421490]:
 g=PropGraph();run(g,[call(factory)]*2,f'nested real allocations {factory:x}')
missing={hex(a):[hex(i.address) for i in code if not hits[i.address]] for a,code in coverage.items()}
print('MISSING',json.dumps(missing),flush=True)
excluded={'0x494c71':'initialized allocator bypasses process bootstrap',
 '0x494c92':'successful sentinel allocation contract',
 **{hex(a):'successful outer allocation contract' for a in [0x4b2a05,0x4b2a09,0x4b2a0b,0x4b2a12,0x4b2a15,0x4214d8,0x4214dc,0x4214de,0x4214e5,0x4214e8]}}
scope='Seven complete original routines construct the Model component and its real nested renderer, including its base object and circular-list sentinel. Actual allocation/zeroing/base-component callees execute; all initialized fields, retained poisoned bytes, method identities, allocation routes/order, globals and preserved registers compare. Successful allocations and initialized allocator are the tested contract, with explicit failure/bootstrap instruction exclusions. Model initialization, asset loading, destruction and rendering are not supplied by these constructors and remain unavailable.'
finish('model-component',scope,excluded,extra)
