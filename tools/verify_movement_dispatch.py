"""Compare movement-dispatch with the original game instructions."""
from pathlib import Path
dispatch_seed=Path('tools/verify_rail_state.py').read_text().split('for special,node,speed in ')[0]
dispatch_seed=dispatch_seed.replace('rail-state','movement-dispatch').replace('call(0x50ddf0,PHYS,[QUERY])','call(0x510830,PHYS,[QUERY])')
exec(compile(dispatch_seed,'<all recovered movement-state graph>','exec'))
folder=out;report_path=out.parent/'movement-dispatch.json'
bind(0x510830,'thug_skater_update_movement',0,'void',True,True,True);ROOTS.add(0x510830)
bind(0x40ab50,'thug_collision_cache_initialize',result='word')
for j in range(8):glob('thug_collision_cache_registry',0x6918ec+4*j,0,offset=j*4)
glob('thug_collision_cache_mask',0x69190c)
dispatch_instructions=list(md.disasm(pe.get_data(0x110830,1226),0x510830));dispatch_hits=Counter();dispatch_case_hits=Counter()
def trace_dispatch(cpu,at,size,user):dispatch_hits[at]+=1;dispatch_case_hits[at]+=1
oracle.cpu.hook_add(UC_HOOK_CODE,trace_dispatch,begin=0x510830,end=0x510cf9)
for at in [0x510830,0x510cf9]:oracle.cpu.hook_add(UC_HOOK_CODE,floor_observe,begin=at,end=at)
oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=0x510830,end=0x510830)
WCOMP=0x167b000;copy(WCOMP,bytes(0x40));put(WCOMP+4,'<I',0xbf518e27);put(WCOMP+12,'<I',BODIES);put(GAP+16,'<I',WCOMP)
initial=bytes(memory);oracle.initial=initial
dispatch_prior_config=config_entry
def config_entry(trigger=False):
 b=dispatch_prior_config(trigger)
 for name,value in {0x2eacddb3:500.,0xcc5f87aa:1000.}.items():
  pair=b.alloc(struct.pack('<I2f',0,value,value));b.symbol(name,10,b.structure([(0,5,pair)]))
 for name,value in {0xfaa40754:-800.,0xc31ca696:1.,0x441c38a0:1.,0x850eb87a:.001,0xf4813ad5:1.,0xc6b38be0:2.,0xf9b006aa:.5,0x0c617caf:-300.,0x64a48a64:.02,0x438ba168:-12.,0x349d02d4:60.,0x5a9de35a:100.,0x542cf0c7:36.}.items():b.symbol(name,2,bits(value))
 b.symbol(0xd7e8d8de,1,100)
 return b
dispatch_prior_compare=compare
dispatch_changes={}
def compare(calls,p,changes=None,label='movement dispatcher'):
 return dispatch_prior_compare(calls[:-1]+[call(0x40ab50,PHYS+0x4f4)]+calls[-1:],p,{**(changes or {}),**{index[k]:v for k,v in dispatch_changes.items()}},label)
def frame(mode,extra=(),label='movement state',changes=None):
 global dispatch_changes
 dispatch_changes=changes or {}
 dispatch_case_hits.clear()
 p=[patch(SKATER_STATE+0x18,'<I',mode),patch(PHYS+0x3ac,'<f',1),patch(PHYS+0x14cc,'<I',123),patch(PHYS+0x38c,'<4f',0,0,1,0)]
 if mode==3:p += [patch(GCONTEXT+0x18,'<I',0xa549b57b)]
 update(extra=p+list(extra),label=label+' '+str(mode))
 path_results[-1]['dispatch_hits']=[hex(at) for at in sorted(dispatch_case_hits)]
 assert oracle.word(0x691974)==0
 print('Dispatch',len(path_results),mode,'->',path_results[-1]['state'],len(dispatch_case_hits),flush=True)
for mode in [0,1,2,3,4,5,6,0xffffffff]:frame(mode)
for mode in range(6):
 for held in [0,1]:
  frame(mode,[patch(INPUT+0x1c0,'<B',held),patch(INPUT+0x1a0,'<B',0)]+[patch(SKATER_STATE+o,'<B',255) for o in [0x98,0xa0]],label='jump latch and frame flags')
for previous,skip in itertools.product([0,1,255],[0,1]):
 frame(1,[patch(INPUT+0x1a0,'<B',0),patch(SKATER_STATE+0x30,'<B',1),patch(SKATER_STATE+0x78,'<B',skip),patch(PHYS+0x4f0,'<B',previous)],label='vert-air event state')
for previous in [1,255]:frame(6,[patch(PHYS+0x4f0,'<B',previous)],label='vert-air exit after non-air state')
for angle,delay in itertools.product([0.,45.,90.],[0,0xffffffff]):
 overrides={0x76c1da15:(2,bits(angle))}
 frame(1,[patch(ORIENT+0x40,'<I',0),patch(PHYS+0x23c,'<I',delay)],label='rail retry direction gate')
overrides={}
for angle,second,empty in [(0.,False,False),(.3,False,False),(-.7,False,False),(0.,True,False),(0.,False,True)]:
 c=math.cos(angle);s=math.sin(angle);matrix=[c,0,-s,0,0,1,0,0,s,0,c,0,0,0,0,1]
 p=[patch(WORLD+0x48,'<I',0),patch(GOWNER+0x4c,'<4f',0,20000,0,1),patch(GOWNER+0x6c,'<16f',*matrix),patch(GOWNER+0xac,'<4f',2,3,4,0),patch(BODIES+0x4c,'<4f',s*50,20000,c*50,1),patch(BODIES+0x5c,'<4f',s*50-c*20,20000,c*50+s*20,1)]
 for i in range(3):
  p += [patch(MOVING_RAILS+i*0x54,'<12f',0,0,i*100,1,0,0,(i+1)*100,1,0,0,i*100,1),patch(MOVING_RAILS+i*0x54+0x40,'<5I',MOVING_RAILS+(i+1)*0x54 if i<2 else 0,MOVING_RAILS+(i-1)*0x54 if i else 0,4,0x1800+i,0)]
 if second:p += [patch(TRANSFORM+0x48,'<I',0),patch(TRANS_COMPONENT+0x14,'<I',TRANS_COMPONENT2)]
 if empty:p += [patch(TRANSFORM+0x48,'<I',0)]
 frame(1,p,label='moving rail acquisition',changes={0x6f0db8:TRANS_COMPONENT})
for face,height in itertools.product([0,1,3,13,34,46,70,129],[0.,2.]):
 data=bytes.fromhex(loader['queries'][face]['result']);point=list(struct.unpack_from('<4f',data,16));normal=list(struct.unpack_from('<4f',data))
 position=[point[j]+normal[j]*height for j in range(3)]+[1]
 frame(1,[patch(BODIES+0x4c,'<4f',*position),patch(BODIES+0x5c,'<4f',*position),patch(BODIES+0xac,'<4f',0,-100,0,0),patch(INPUT+0x1a0,'<B',0),patch(PHYS+0x14cc,'<I',0)],label='training landing '+str(face))
scope='Complete00510830 movement dispatcher with all six recovered movement states, fixed/moving rail acquisition and real frame actions; all350parentinstructions covered. All fixture bytes compare exactly. Full game integration remains unfinished.'
fixture={'base':BASE,'memory':'movement-dispatch-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'native_qb_callbacks','pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'native_callbacks':[{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]}
(folder/'movement-dispatch-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')));(folder/fixture['memory']).write_bytes(initial)
coverage={'total':len(dispatch_instructions),'covered':sum(bool(dispatch_hits[i.address]) for i in dispatch_instructions),'missing':[hex(i.address) for i in dispatch_instructions if not dispatch_hits[i.address]]}
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(path_results),'counts':dict(oracle.counts),'instruction_coverage':coverage,'callee_coverage':dict(oracle.coverage),'paths':path_results,'scope':scope}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('Original movement',len(path_results),coverage['covered'],'/',coverage['total'],flush=True)

subprocess.run(['node',str(ROOT/'tools/verify_movement_dispatch_wasm.mjs')],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [folder/'movement-dispatch-fixtures.json',folder/fixture['memory']]}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS movement-dispatch',len(path_results),sum(oracle.counts.values()))
