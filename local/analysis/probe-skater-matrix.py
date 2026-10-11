"""Original SkaterMatrixQueries, numeric helper and next real startup boundary."""
from pathlib import Path
source=Path('local/analysis/probe-skater-score.py').read_text().split('for value in [0,1,2,255,0x80000000,0xffffffff]:')[0]
old='if oracle.word(node+8) not in [0xbf518e27,0x850eef66]:return'
assert old in source
source=source.replace(old,'if oracle.word(node+8) not in [0x270f56e1,0x850eef66]:return')
exec(compile(source,'<preserved Score oracle; later local boundary>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x406560,198,'thug_vector_angle_exceeds_draft',3,'byte',False,False,False),
 (0x513fd0,11,'thug_skater_matrix_destroy_draft',0,'void',False,False,True),
 (0x513fe0,33,'thug_skater_matrix_delete_draft',1,'word',True,False,True),
 (0x514010,21,'thug_skater_matrix_finalize_draft',0,'void',False,False,True),
 (0x514030,16,'thug_skater_matrix_update_draft',0,'void',False,False,True),
 (0x514040,1007,'thug_skater_matrix_command_draft',3,'word',True,False,True),
 (0x514430,114,'thug_skater_matrix_create_draft',0,'word',True,False,False)]
for spec in specs:bind_new(*spec)
functions['0x406560']['float_args']=[2]
for args in [(0x45e510,'thug_composite_initialize_draft',0,'word',False,False),
 (0x45ee20,'thug_composite_add_parameters_draft',2,'void',True,True),
 (0x45db30,'thug_composite_finalize_draft',0,'void',True,True),
 (0x45d890,'thug_composite_destroy_draft',0,'void',True,True),
 (0x45d720,'thug_component_descriptor_base',3,'word',False,False),
 (0x582d90,'thug_skater_construct_matrix_prefix_draft',6,'void',True,True)]:bind(*args)
exports.append([0x64bf70,'thug_skater_matrix_methods_draft'])
function_exports.append([0x514430,'thug_skater_matrix_create_draft'])
initial=bytes(memory);oracle.initial=initial
Q=P+0x2000;A=P+0x3000;B=A+32
class MatrixGraph(ScoreGraph):
 def __init__(self):
  super().__init__();self.put(P,'<6I',0x64bf70,0xbf518e27,0,OBJ,0,0);fields.add(P)
  self.put(P+0x18,'<16f',1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1)
  self.put(P+0x58,'<2I',0,Q);self.image[Q-BASE:Q-BASE+0x200]=bytes(0x200)
  self.put(Q+4,'<I',0x5bd63b29);self.put(Q+0x18,'<16f',1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1)
  self.put(Q+0x78,'<4f',0,1,0,0);self.put(OBJ+0x100,'<I',Q)
  self.put(OBJ+0x8c,'<4f',1,0,0,1);self.put(OBJ+0xac,'<4f',0,0,10,0)
  self.script=self.alloc(244);self.image[self.script-BASE:self.script-BASE+244]=bytes(244)
  self.output=self.structure([]);self.put(self.script+0x14,'<I',self.output)
 def run(self,calls,label,changes=None):
  for reg,value in [(UC_X86_REG_FPSW,0),(UC_X86_REG_FPTAG,0xffff),(UC_X86_REG_MXCSR,0x1f80)]:oracle.cpu.reg_write(reg,value)
  try:result=super().run(calls,label,changes)
  except Exception:print('FAILED',label,flush=True);raise
  if len(labels)%50==0:print('Matrix cases',len(labels),flush=True)
  return result
 def params(self,value,kind=2):return self.structure([(0,kind,value)])
 def command(self,name,params=None):return call(0x514040,P,[name,self.structure([]) if params is None else params,self.script])
 def pair(self,x,y):
  v=self.alloc(12);self.put(v,'<I2f',0,x,y);return self.params(v,5)
# Direct helper: strict angle and 0.5 magnitude boundaries; W never participates.
for a,b in [([1,0,0],[1,0,0]),([1,0,0],[-1,0,0]),([1,0,0],[0,1,0]),
 ([.49999997,0,0],[1,0,0]),([.5,0,0],[1,0,0]),([1,0,0],[.49999997,0,0]),
 ([1,0,0],[.5,0,0]),([0,0,0],[1,2,3]),([1,2,3],[0,0,0]),
 ([3,-4,12],[-2,1,9]),([1e20,2e20,-3e20],[-1e20,2e20,3e20])]:
 for angle in [-180,-90,-0.,0.,45,90,180,270,360]:
  g=MatrixGraph();g.put(A,'<4f',*a,123);g.put(B,'<4f',*b,-456)
  g.run([call(0x406560,args=[A,B,bits(angle)])],f'angle lengths/threshold/{a}/{b}/{angle}')
for lane,value in itertools.product([0,1,2],[1,0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc12345,0xffc12345]):
 for which in [A,B]:
  g=MatrixGraph();g.put(A,'<4f',1,2,3,0);g.put(B,'<4f',3,2,1,0);g.put(which+lane*4,'<I',value)
  g.run([call(0x406560,args=[A,B,bits(45)]),call(0x406560,args=[A,B,bits(135)])],f'wide/unordered angle/{which}/{lane}/{value:x}')
for value in [0x7f800000,0xff800000,0x7fc12345,0xffc12345,0x7f7fffff,1]:
 g=MatrixGraph();g.put(A,'<4f',1,0,0,0);g.put(B,'<4f',-1,0,0,0)
 g.run([call(0x406560,args=[A,B,value])],f'angle bits/{value:x}')
# Factory, virtual initialization, late Physics lookup and ordinary destruction.
for flags in [0,1,2,255,256,257,0xffffffff]:
 g=MatrixGraph();g.run([call(0x514430),call(0x513fe0,HEAP,[flags])],f'factory/delete/{flags}')
for fill,flags in itertools.product([0,0xa5,255],[0,2,3,0xffffffff]):
 g=MatrixGraph();g.image[P-BASE:P-BASE+0x60]=bytes([fill])*0x60;g.put(P+8,'<I',flags)
 g.run([call(0x513fd0,P)]*2,f'destroy preserves fields/{fill}/{flags}')
for shape in ['absent','head','middle','duplicate','wrong type']:
 g=MatrixGraph();other=g.component(0x5bd63b29 if shape=='duplicate' else 0x11)
 g.put(Q+0x10,'<I',other if shape=='duplicate' else 0)
 if shape=='middle':g.put(other+0x10,'<I',Q)
 g.put(OBJ+0x100,'<I',0 if shape=='absent' else other if shape in ['middle','wrong type'] else Q)
 g.run([call(0x514010,P)]*2,f'late physics lookup/{shape}')
for delta in [-64,-16,-4,0,4,16,64,0x2000]:
 g=MatrixGraph();source=P+delta
 for i in range(16):g.put(source+0x18+4*i,'<I',[0x80000000,0x7fa12345,0x7fc12345,0xffffffff,0x3f800000,0][i%6])
 g.put(P+0x5c,'<I',source)
 g.run([call(0x514030,P)]*2,f'matrix raw forward copy/{delta}')
for reversed_ in [False,True]:
 g=MatrixGraph();g.registry([(0xbf518e27,0x514430),(0x5bd63b29,0x505440)]);g.symbol(0x78f80ec4,2,bits(.125))
 descriptors=[g.structure([(0xb6015ea8,13,t)]) for t in ([0x5bd63b29,0xbf518e27] if reversed_ else [0xbf518e27,0x5bd63b29])]
 g.run([call(0x45e510,OBJ)]+[call(0x45ee20,OBJ,[d,0]) for d in descriptors]+[call(0x45db30,OBJ),call(0x45d890,OBJ)],f'real shared factory/init/finalize/disposal/{reversed_}')
# All eight command branches and the two unhandled search-tree exits.
for n in [0,0x97201738,0xa745c081,0xffffffff]:
 g=MatrixGraph();s=g.run([g.command(n)],f'unhandled/{n:x}');assert s[0]['result']==2
for x,z in itertools.product([-1,-.5,-0.,0.,.5,1],[-1,-0.,0.,1]):
 g=MatrixGraph();g.put(OBJ+0x8c,'<4f',x,.25,z,1)
 g.run([g.command(0x8e7833be)]*2,f'heading/replaced outputs/{x}/{z}')
for xyz,old in itertools.product([(1,0,0),(0,1,0),(1,1,0),(0,-1,1),(1,-1,1),(0,0,0),(1e20,-2e20,3e20)],[-45,0,90]):
 g=MatrixGraph();g.put(OBJ+0x8c,'<4f',*xyz,1);g.put(P+0x58,'<f',old)
 g.run([g.command(0x97201739)]*2,f'pitch and retained delta/{xyz}/{old}')
for n in [0x5e269b2b,0xa0551543,0xd3313e92]:
 for angle,up in itertools.product([0,45,90,135,180,270],[(0,1,0),(.5,.5,.5),(0,-1,0)]):
  g=MatrixGraph();g.put(P+0x28,'<4f',*up,0);g.put(P+0x18,'<4f',1,1,0,0)
  g.run([g.command(n,g.params(bits(angle)))],f'tilt/{n:x}/{angle}/{up}')
for velocity,normal in itertools.product([(1,0,1),(-1,0,1),(0,0,0),(0,2,0),(1e10,-1e10,1e10)],[(0,1,0),(1,0,0),(.6,.8,0)]):
 g=MatrixGraph();g.put(OBJ+0xac,'<4f',*velocity,0);g.put(P+0x28,'<4f',*normal,0)
 g.run([g.command(0xa745c080),g.command(0xc8c4d2f4)]+[g.command(0xb992f3cc,g.pair(x,y)) for x,y in [(0,90),(45,135),(90,180),(135,45)]],f'projected turn/range/{velocity}/{normal}')
for n,offset in [(0x5e269b2b,P+0x2c),(0xa0551543,Q+0x7c),(0xa745c080,OBJ+0xac),(0xc8c4d2f4,OBJ+0xac),(0xd3313e92,P+0x18)]:
 for value in [0x7fc12345,0x7f800000,0xff800000]:
  g=MatrixGraph();g.put(offset,'<I',value);g.run([g.command(n,g.params(bits(45)))],f'unordered predicate/{n:x}/{value:x}')
# Dispatch through the original base descriptor and recovered concrete vtable.
for n in [0x8e7833be,0x97201739,0x5e269b2b,0xa0551543,0xa745c080,0xc8c4d2f4,0xd3313e92,0xb992f3cc,0xdeadbeef]:
 g=MatrixGraph();desc=g.alloc(24);g.put(desc,'<6I',n,0xbf518e27,0,0,0,0)
 params=g.pair(0,90) if n==0xb992f3cc else g.params(bits(45))
 g.run([call(0x45d720,P,[desc,params,g.script])],f'original virtual command/{n:x}')
# Original constructor; local branch advances, remote branch keeps its boundary.
prefix_records=[]
for heap_index,local,id_ in itertools.product([0,1,2,0xffffffff],[0,1,256,257],[0,0xffffffff]):
 g=ScoreGraph();g.registry([(0xce0ca665,0),(0xb87c8e43,0),(0x43686585,0x519740),(0xf27a294d,0x51bd80),(0x27d7cd28,0x41eec0),(0xd262802f,0x518b60),(0xbf518e27,0x514430)])
 mutate=bool(len(prefix_records)%2)
 if mutate:g.put(DLOG+4,'<2I',OBJ+0x14,0x77700000+len(prefix_records))
 stages=g.run([],f'skater through MatrixQueries/{heap_index}/{local}/{id_}',{0x690fa0:0xfffffffe})
 before=bytes(oracle.cpu.mem_read(BASE,len(initial)));cpu=oracle.cpu;sp=oracle.stack+0x18000
 args=[17,MANAGER,local,id_,heap_index,0x12345678]
 cpu.mem_write(sp,struct.pack('<7I',oracle.stop,*args));cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,OBJ);cpu.reg_write(UC_X86_REG_FPCW,0x7f)
 try:cpu.emu_start(0x582d90,oracle.stop,count=500000)
 except Exception:print('PREFIX FAILED',hex(cpu.reg_read(UC_X86_REG_EIP)),args,flush=True);raise
 assert cpu.reg_read(UC_X86_REG_EIP)==0x45ee20 and oracle.word(BOUNDARY+8)==OBJ
 chain=[];c=oracle.word(OBJ+0x100)
 while c:chain.append((c,oracle.word(c+4)));c=oracle.word(c+16)
 assert [t for _,t in chain]==[0xce0ca665,0xb87c8e43,0x43686585,0xf27a294d]+([0x27d7cd28] if local&255 else [])+[0xd262802f]+([0xbf518e27] if local&255 else [])
 component=chain[-2 if local&255 else -1][0];score=oracle.word(component+0x18);player=int.from_bytes(cpu.mem_read(score+8,2),'little')
 assert oracle.word(OBJ+0x278)==component and player==(oracle.word(OBJ+0x14)&65535)
 params=oracle.word(BOUNDARY+4);next_type=oracle.word(oracle.word(params+4)+8)
 assert next_type==(0x270f56e1 if local&255 else 0x850eef66)
 after=bytes(cpu.mem_read(BASE,len(initial)));outputs=[];known={row[0] for row in exports}
 for page in range(0,len(initial),4096):
  if before[page:page+4096]!=after[page:page+4096]:
   for j in range(page,min(page+4096,len(initial)),4):
    if before[j:j+4]!=after[j:j+4]:
     outputs.append([BASE+j,after[j:j+4].hex()])
     if int.from_bytes(after[j:j+4],'little') in known:fields.add(BASE+j)
 stages.append({'fn':'0x582d90','this':OBJ,'args':args+[DIAG],'result':None,'outputs':outputs,'globals':[oracle.global_read(x) for x in globals_],'callbacks':0,'expected_trap':True})
 oracle.counts['thug_skater_construct_matrix_prefix_draft']+=1
 prefix_records.append({'arguments':args,'components':chain,'boundary':list(struct.unpack('<4I',cpu.mem_read(BOUNDARY,16))),
  'next_type':hex(next_type),'score':{'component':component,'state':score,'player_id':player},'diagnostics_mutate_id':mutate})
scope='Seven complete routines recover SkaterMatrixQueries factory, destruction/delete, late physics lookup, raw matrix update, all eight checksum commands and406560 angle predicate. The original shared builder creates, initializes, finalizes and disposes real MatrixQueries and Physics in either order; original base-descriptor virtual dispatch executes every command. Direct numeric cases include strict thresholds, small-vector rejection, wide exponents and unordered predicates. Whole arena/globals/heap and completed-call preserved registers compare exactly, with no NaN masks. The original582d90 constructor now creates local MatrixQueries and stops before270f56e1; nonlocal850eef66 boundary is unchanged. Existing SDK transcendental adapter is not physical x87 validation. Input graphs are explicit fixtures; no new original-asset loader or playable frame is claimed.'
extra={**extra,'direct_initializer_prefix':True,'boundary_address':BOUNDARY,'boundary_factory':0x45ee20,
 'native_callbacks':[{'module':'skater-construction-diagnostic-fixture.wasm','export':'fixture_skater_print','slots':[DIAG+4]}]}
saved_coverage=coverage.copy();coverage.clear();finish('skater-matrix',scope,{},extra);coverage.update(saved_coverage)
report_path=folder/'skater-matrix-original.json';report=json.loads(report_path.read_text())
report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
code=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(0x182d90,1639),0x582d90))
report['partial_constructor']={'address':'0x582d90','covered':sum(bool(prefix_hits[i.address]) for i in code),'total':len(code),'boundary':'0x45ee20','interrupted_calls':len(prefix_records),'records':prefix_records}
report_path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k in ['cases','calls','instruction_coverage']}),flush=True)

fixture_path=folder/'skater-matrix-fixtures.json';fixture=json.loads(fixture_path.read_text())
corrections=[]
for i,c in enumerate(fixture['cases']):
 if len(c['steps'])==1:
  step=c['steps'][0]
  if step['fn']=='0x406560' and step['args'][2] in [0x7f800000,0xff800000]:
   corrections.append({'case_index':i,'angle_bits':step['args'][2],'raw_emulator_result':step['result'],'adapter_result':0})
assert len(corrections)==2 and [row['raw_emulator_result'] for row in corrections]==[1,0]
spec={'source':'https://cdrdv2-public.intel.com/868137/325462-089-sdm-vol-1-2abcd-3abcd-4.pdf',
 'rule':'Intel SDM Vol1 table8-10: FCOS infinity with masked invalid yields QNaN. At406560 both later ordered comparisons then fail. The unmodified Unicorn execution instead returns1 for the positive-infinity case. SDK adapter returns0 for both signs. Raw original fixture values remain unchanged.', 'cases':corrections}
fixture['fcos_infinity_specification']=spec;fixture['scope']+=' Two deliberate infinite-angle calls are checked against the declared SDK/Intel masked-invalid boundary, retaining raw Unicorn returns; positive infinity differs. All other returns and every arena/global/heap byte remain original comparisons.'
fixture_path.write_text(json.dumps(fixture,separators=(',',':')))
report['fcos_infinity_specification']=spec;report['scope']=fixture['scope'];report_path.write_text(json.dumps(report,indent=2)+'\n')
(folder/'skater-matrix-emulator-differences.json').write_text(json.dumps(spec,indent=2)+'\n')
