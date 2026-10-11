"""Original collision scene integration, including real and boundary-case inputs."""
from pathlib import Path
source=Path('local/analysis/probe-texture-buffer.py').read_text().split('for fill in [0,0xa5,0xff]:')[0]
exec(compile(source,'<preserved comparison heap setup>','exec'))
functions.clear();code.clear();hits.clear();oracle.counts.clear();fields.clear()
for a,n,name,argc,result,heap in [(0x49d590,483,'scene_collision_load',2,'byte',True),(0x49e890,15,'sector_add_flags',1,'void',False),(0x49eaa0,40,'sector_attach_collision',1,'byte',False),(0x48df10,10,'geometry_bind_collision',1,'void',False)]:
 functions[hex(a)]={'name':'thug_'+name+'_draft','this':True,'result':result,'cleanup':argc*4,'memory':heap}
 code[a]=list(md.disasm(pe.get_data(a-0x400000,n),a));oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:hits.update([at]),begin=a,end=a+n-1)
exports += [[0x64a6b8,'thug_model_scene_pc_methods_draft'],[0x64a718,'thug_model_sector_pc_methods_draft'],[0x645c18,'thug_static_collision_methods']]
SYMBOLS,OBSERVER,OVT=BASE+0x1c0000,BASE+0x1d0000,BASE+0x1d0040
memory[SYMBOLS-BASE:SYMBOLS-BASE+0x4000]=bytes(0x4000);put(OBSERVER,'<3I',OVT,0x12345678,0);put(OVT+4,'<I',oracle.stop+0x400)
globals_ += [['thug_script_symbol_buckets',0x6f3624,4],['thug_collision_load_observer_draft',0x6fa7c8,4]];defaults += [SYMBOLS,OBSERVER]
def observer(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);receiver=cpu.reg_read(UC_X86_REG_ECX);assert receiver==OBSERVER
 oracle.setword(receiver+8,oracle.word(receiver+8)+1);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
oracle.cpu.hook_add(UC_HOOK_CODE,observer,begin=oracle.stop+0x400,end=oracle.stop+0x400)
put(MANAGER+0x110,'<I',MANAGER+0x200);oracle.scope_entries[MANAGER+0x200]=2
initial=bytes(memory);oracle.initial=initial;oracle.event_limit=2700;oracle.instruction_limit=20000000
raw=(ROOT/'local/game-files/Game/Data/levels/TR/TR.col.xbx').read_bytes()
from collision_file import layout
layout(raw)
# Small helpers must preserve all unrelated bytes and refuse a second attachment.
for old in [0,INPUT]:
 for geo in [0,P+0x100]:
  for instance in [0,P+0x200]:
   if geo and not old and not instance:continue
   g=Graph();g.put(P+0x14,'<2I',geo,old);g.put(P+0x20c,'<I',0x12345678)
   run(g,[call(0x49eaa0,P,[instance])]*2,f'attach old{old:x}/geo{geo:x}/instance{instance:x}')
for flags in [0,1,0x40,0x80000000,0xffffffff]:
 g=Graph();g.put(P+8,'<I',0x1248);run(g,[call(0x49e890,P,[flags]),call(0x48df10,P,[flags])],f'full-word flags and pointer{flags:x}')
for actual,grid,existing,notify in [(False,0,False,False),(False,1,False,True),(True,0,False,False),(True,1,True,False)]:
 g=Graph();g.data[P-BASE:P-BASE+644]=bytes(644);g.put(P,'<I',0x64a6b8);g.put(P+0x8c,'<B',grid)
 g.put(P+0xb0,'<8f',1e7,1e7,1e7,1,-1e7,-1e7,-1e7,1)
 data=raw if actual else struct.pack('<9I',10,0,0,0,0,0,0,0,0)
 g.data[TEXTURES-BASE:TEXTURES-BASE+len(data)]=data
 rows=[]
 if existing:
  sector=g.alloc(52);geo=g.alloc(100);g.put(sector+0x14,'<2I',geo,0);rows=[(struct.unpack_from('<I',raw,32)[0],sector)]
 g.put(P+0xd0,'<I',g.table(rows,shift=5))
 if notify:
  sym=g.alloc(20);g.put(sym,'<BBH4I',0,1,0,0xba1e4254,0,1,0);g.put(SYMBOLS+(0xba1e4254&4095)*4,'<I',sym)
 run(g,[call(0x49d590,P,[TEXTURES,0xffffffff])],f'actual{actual}/grid{grid}/existing{existing}/observer{notify}')
 assert oracle.word(OBSERVER+8)==int(notify)
coverage={hex(a):{'total':len(c),'covered':sum(bool(hits[i.address]) for i in c),'missing':[hex(i.address) for i in c if not hits[i.address]]} for a,c in code.items()}
for case in oracle.cases:
 for a,data in case['patches']:
  if int.from_bytes(bytes.fromhex(data),'little') in {e[0] for e in exports}:fields.add(a)
scope='Four original functions: resident collision-file integration49d590, geometry binding48df10, one-time sector attachment49eaa0, flag OR49e890. Actual TR version10 file with empty and existing-sector tables, enabled/disabled grid; zero-object file; duplicate/null attachments; full-word flags; optional observer virtual+4 with an explicit observable comparison callback. Initialized successful heap and valid internal data contracts. All actual parsing/grid/table code executes unchanged.'
fixture={'base':BASE,'memory':'level-collision-load-unit-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'texture-buffer-ports.wasm','memory_exports':['fixture_texture_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'pointer_fields':sorted(fields),'pointer_exports':exports,'native_callbacks':[{'module':'level-collision-load-unit-ports.wasm','export':'fixture_collision_observer','slots':[OVT+4]}],'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'level-collision-load-unit-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(len(c['steps']) for c in oracle.cases),'instruction_coverage':coverage,'scope':scope}
(folder/'level-collision-load-unit-original.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
