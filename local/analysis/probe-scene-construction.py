"""Compare original scene/sector construction and mesh list initialization."""
from pathlib import Path
source=Path('local/analysis/probe-texture-buffer.py').read_text().split('for fill in [0,0xa5,0xff]:')[0]
exec(compile(source,'<pinned texture heap setup>','exec'))
functions.clear();code.clear();hits.clear();oracle.counts.clear();oracle.coverage.clear()
specs=[(0x49d390,333,'model_scene_base_construct',1,'word',True),
 (0x4c6130,25,'model_scene_construct',1,'word',True),
 (0x49e900,34,'model_sector_base_construct',0,'word',False),
 (0x4c6550,36,'model_sector_construct',0,'word',False),
 (0x4c6190,107,'model_scene_create_sector',0,'word',True),
 (0x49ca10,14,'model_scene_new_sector',0,'word',True),
 (0x49e660,10,'model_sector_bind_geometry',1,'void',False),
 (0x4b5f60,93,'model_geometry_mesh_list_initialize',0,'void',True),
 (0x49d4e0,41,'model_scene_register_sector',1,'void',True)]
instructions=[]
for a,n,name,argc,result,heap in specs:
 functions[hex(a)]={'name':'thug_'+name+'_draft','this':True,'result':result,'cleanup':argc*4,'memory':heap}
 code[a]=list(md.disasm(pe.get_data(a-0x400000,n),a));oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:hits.update([at]),begin=a,end=a+n-1)
 instructions += [f'FUNCTION {a:08x} {n} bytes']+[f'{i.address:08x} {i.mnemonic} {i.op_str}' for i in code[a]]
(folder/'scene-construction-instructions.txt').write_text('\n'.join(instructions)+'\n')
exports += [[0x6499e0,'thug_model_scene_base_methods_draft'],[0x64a6b8,'thug_model_scene_pc_methods_draft'],
 [0x6499dc,'thug_model_scene_list_methods_draft'],[0x64a438,'thug_model_mesh_list_methods_draft'],
 [0x649a40,'thug_model_sector_base_methods_draft'],[0x64a718,'thug_model_sector_pc_methods_draft'],
 [0x64a368,'thug_model_geometry_lights_methods_draft']]
put(MANAGER+0x110,'<I',MANAGER+0x240);oracle.scope_entries[MANAGER+0x240]=2
ALTERNATE=oracle.stop+0x340;METHODS=P+0x1200
put(METHODS+0x1c,'<I',ALTERNATE);fields.add(METHODS+0x1c)
def alternate(cpu,at,size,user):
 scene=cpu.reg_read(UC_X86_REG_ECX);sp=cpu.reg_read(UC_X86_REG_ESP)
 oracle.setword(scene+0x84,oracle.word(scene+0x84)+1)
 cpu.reg_write(UC_X86_REG_EAX,oracle.word(scene+0x80));cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
oracle.cpu.hook_add(UC_HOOK_CODE,alternate,begin=ALTERNATE,end=ALTERNATE)
initial=bytes(memory);oracle.initial=initial
for fill in [0,0xa5,0xff]:
 for shift in [0,1,2,3,6,12]:
  for fn in [0x49d390,0x4c6130]:
   g=Graph();g.data[P-BASE:P-BASE+644]=bytes([fill])*644
   run(g,[call(fn,P,[shift])]*2,f'scene constructor{fn:x} fill{fill} shift{shift} twice')
 for fn in [0x49e900,0x4c6550]:
  g=Graph();g.data[P-BASE:P-BASE+52]=bytes([fill])*52
  run(g,[call(fn,P)]*2,f'sector constructor{fn:x} fill{fill} twice')
 for target in [0,P,P+52,0xffffffff]:
  g=Graph();g.data[P-BASE:P-BASE+52]=bytes([fill])*52
  run(g,[call(0x49e660,P,[target])],f'bind geometry fill{fill} target{target:x}')
 g=Graph();g.data[P-BASE:P-BASE+100]=bytes([fill])*100
 run(g,[call(0x4b5f60,P)]*2,f'mesh list fill{fill} twice')
for this in [0,P,P+0x400]:
 g=Graph();run(g,[call(0x4c6190,this)]*2,f'PC sector allocation ignores receiver{this:x}')
g=Graph();g.put(P,'<I',0x64a6b8);run(g,[call(0x49ca10,P)]*3,'PC scene virtual creates distinct sectors')
for fill in [0,0xa5,0xff]:
 g=Graph();g.put(P,'<I',METHODS);g.put(P+0x80,'<2I',P+0x800,0)
 g.data[P+0x800-BASE:P+0x800-BASE+52]=bytes([fill])*52
 run(g,[call(0x49ca10,P)]*2,f'alternate scene virtual returns existing sector fill{fill}')
for shift in [0,1,2,4]:
 for keys in [[0],[1],[0xffffffff],[0,16,32,48],[0,0],[1,1,17,17]]:
  g=Graph();calls=[call(0x4c6130,P,[shift])]
  for i,key in enumerate(keys):
   sector=P+0x800+i*64;g.put(sector+4,'<I',key);calls.append(call(0x49d4e0,P,[sector]))
  run(g,calls,f'register sectors shift{shift} keys{keys}')
# The original buffer-loading order, using its recovered geometry constructor.
functions['0x4b4460']={'name':'thug_model_geometry_construct_draft','this':True,'result':'word','cleanup':0,'memory':False}
g=Graph();g.put(P+0x804,'<I',0x12345678)
run(g,[call(0x4c6130,P,[1]),call(0x4c6550,P+0x800),call(0x4b4460,P+0x900),
 call(0x49e660,P+0x800,[P+0x900]),call(0x4b5f60,P+0x900),call(0x49d4e0,P,[P+0x800])],'scene sector geometry and mesh list chain')
coverage={hex(a):{'total':len(c),'covered':sum(bool(hits[i.address]) for i in c),'missing':[hex(i.address) for i in c if not hits[i.address]]} for a,c in code.items()}
excluded={
 '0x49d390':{'0x49d3d6':'initialized heap contract',**{a:'successful allocation contract' for a in ['0x49d405','0x49d486','0x49d4b4']}},
 '0x4c6190':{'0x4c61af':'initialized heap contract',**{a:'successful allocation contract' for a in ['0x4c61ea','0x4c61ee','0x4c61f0','0x4c61f7','0x4c61fa']}},
 '0x4b5f60':{a:'successful allocation contract' for a in ['0x4b5fac','0x4b5fae','0x4b5fb1','0x4b5fb7','0x4b5fb8']}}
for a,c in coverage.items():
 c['excluded']=excluded.get(a,{});assert set(c['missing'])==set(c['excluded']),(a,c)
print('COVERAGE',json.dumps(coverage),flush=True)
scope='Nine original scene/sector routines with exact retained bytes, bounds, method identities, table allocation, duplicate/colliding sector registration and scoped mesh sentinel allocation. Existing geometry construction is reused. Successful allocation and initialized heap are explicit internal contracts. No mesh parser or drawing is substituted.'
fixture={'base':BASE,'memory':'scene-construction-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'scene-construction-ports.wasm','memory_exports':['fixture_texture_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'pointer_fields':sorted(fields),'pointer_exports':exports,'native_callbacks':[{'module':'scene-construction-ports.wasm','export':'fixture_alternate_sector','original':ALTERNATE,'slots':[METHODS+0x1c]}],'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'scene-construction-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(oracle.counts.values()),'instruction_coverage':coverage,'scope':scope}
(folder/'scene-construction-original.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
