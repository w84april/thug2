"""Original complete SkaterRotate behavior and the extended skater prefix."""
from pathlib import Path
source=Path('local/analysis/probe-skater-trick.py').read_text().split('for fill,offset in itertools.product')[0]
old="source=source.replace(old,'if oracle.word(node+8) not in [0x52d61a0d,0x850eef66]:return')";assert old in source
source=source.replace(old,"source=source.replace(old,'if oracle.word(node+8) not in [0x11b4c67f,0x850eef66]:return')")
exec(compile(source,'<preserved Trick oracle; later boundary>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x404ec0,142,'thug_matrix_rotation_coordinate_draft',3,'word',False,False,False),
 (0x4057b0,157,'thug_matrix_rotate_z_draft',1,'word',False,False,True),
 (0x406260,106,'thug_vector_dominant_coordinate_draft',1,'double',False,False,True),
 (0x4062d0,387,'thug_matrix_direction_angle_draft',4,'double',False,False,False),
 (0x517cc0,11,'thug_skater_rotate_destroy_draft',0,'void',False,False,True),
 (0x517cd0,20,'thug_skater_rotate_initialize_draft',1,'void',False,False,True),
 (0x517cf0,33,'thug_skater_rotate_delete_draft',1,'word',True,False,True),
 (0x517d20,21,'thug_skater_rotate_finalize_draft',0,'void',False,False,True),
 (0x517d40,114,'thug_skater_rotate_create_draft',0,'word',True,False,False),
 (0x517dc0,224,'thug_skater_rotate_update_draft',0,'void',False,False,True),
 (0x517ea0,927,'thug_skater_rotate_command_draft',3,'word',False,False,True)]
for row in specs:bind_new(*row)
functions['0x404ec0']['float_args']=[2];functions['0x4057b0']['float_args']=[0]
for args in [(0x45e510,'thug_composite_initialize_draft',0,'word',False,False),
 (0x45ee20,'thug_composite_add_parameters_draft',2,'void',True,True),
 (0x45db30,'thug_composite_finalize_draft',0,'void',True,True),
 (0x45d890,'thug_composite_destroy_draft',0,'void',True,True),
 (0x45d720,'thug_component_descriptor_base',3,'word',False,False),
 (0x582d90,'thug_skater_construct_rotate_prefix_draft',6,'void',True,True)]:bind(*args)
exports.append([0x64c018,'thug_skater_rotate_methods_draft']);function_exports.append([0x517d40,'thug_skater_rotate_create_draft'])
global_default('thug_frame_length_scale',0x684fc8,bits(1));oracle.setword(0x684fe4,0x5df4ac)
initial=bytes(memory);oracle.initial=initial
Q=P+0x2000;A=P+0x4000;B=P+0x4100;OUT=P+0x4300
IDENTITY=[1 if i%5==0 else 0 for i in range(16)]
class RotateGraph(ScoreGraph):
 def __init__(self):
  super().__init__();self.image[P-BASE:P-BASE+0x58]=bytes(0x58);self.put(P,'<6I',0x64c018,0x52d61a0d,0,OBJ,0,0);fields.add(P)
  self.image[Q-BASE:Q-BASE+0x1540]=bytes(0x1540);self.put(Q,'<6I',0x64bc48,0x5bd63b29,0,OBJ,0,0);fields.add(Q)
  self.put(P+0x54,'<I',Q);self.put(OBJ+0x100,'<I',Q)
  self.put(OBJ+0x4c,'<4f',1,2,3,1);self.put(OBJ+0x6c,'<16f',*IDENTITY);self.put(Q+0x18,'<16f',*IDENTITY)
  self.put(A,'<16f',*IDENTITY);self.put(B,'<4f',1,0,0,1);self.symbol(0x78f80ec4,2,bits(.125))
  self.script=self.alloc(244);self.image[self.script-BASE:self.script-BASE+244]=bytes(244)
 def run(self,calls,label,changes=None):
  for reg,value in [(UC_X86_REG_FPSW,0),(UC_X86_REG_FPTAG,0xffff),(UC_X86_REG_MXCSR,0x1f80)]:oracle.cpu.reg_write(reg,value)
  try:result=super().run(calls,label,changes)
  except Exception:print('FAILED',label,flush=True);raise
  if len(labels)%50==0:print('Rotate cases',len(labels),flush=True)
  return result
 def command(self,items=(),name=0xc876adf3,params=None):return call(0x517ea0,P,[name,self.structure(items) if params is None else params,self.script])
 def axis(self,axis,target=1,rate=1,progress=0,active=1):self.put(P+0x18+20*axis,'<4fB',target,1,rate,progress,active)
 def target(self,xyz,legacy=False,missing=False):
  key=0x72345678;_,nodes=self.nodes([(key,None,[])])
  items=[(0xa1dc81f9,13,key)]+([] if missing else [(0xb9d31b0a if legacy else 0x7f261953,6,self.vector([bits(v) for v in xyz]))])
  s=self.structure(items);self.put(nodes[0]+4,'<I',self.word(s+4));return key
# Math helpers: finite angles, coordinate selection, aliasing and signed results.
for axis,angle in itertools.product([-1,0,1,2,3,4,5],[0.,-0.,.125,-.5,1.5707963267948966,-3.,10.,-100.]):
 g=RotateGraph();g.run([call(0x404ec0,args=[A,axis,bits(angle)])]*2,f'coordinate matrix/{axis}/{angle}')
for angle,kind in itertools.product([0.,-0.,.125,-.5,1.5707963267948966,-3.,10.,-100.],['identity','dense']):
 g=RotateGraph()
 if kind=='dense':g.put(A,'<16f',*[i*.125-1 for i in range(16)])
 g.run([call(0x4057b0,A,[bits(angle)])]*3,f'Z premultiply/{angle}/{kind}')
for xyz in itertools.product([-2.,-0.,0.,1.,2.],repeat=3):
 g=RotateGraph();g.put(B,'<4f',*xyz,123)
 g.run([call(0x406260,B,[OUT]),call(0x406260,B,[0])],f'dominant ties/sign/{xyz}')
for lane,value in itertools.product(range(3),[1,0x7f7fffff,0x7f800000,0xff800000,0x7fc12345,0xffc12345]):
 g=RotateGraph();g.put(B,'<4f',1,-2,3,0);g.put(B+lane*4,'<I',value)
 g.run([call(0x406260,B,[OUT])],f'dominant unordered/wide/{lane}/{value:x}')
for off in [0,4,8,12]:
 g=RotateGraph();g.put(B,'<4f',-2,3,-4,1);g.run([call(0x406260,B,[B+off])]*2,f'dominant aliased index/{off}')
for normal,forward in itertools.permutations(range(3),2):
 for v in [(0,0,0),(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1),(1,2,-3),(.005,.005,.005),(.01,0,0),(1e20,-2e20,3e20)]:
  g=RotateGraph();g.put(B,'<4f',*v,7);g.run([call(0x4062d0,args=[A,B,forward,normal])],f'projected angle/{normal}/{forward}/{v}')
for scale,v in itertools.product([.5,1,2,-2],[(1,0,1),(1,0,-1),(-1,0,1),(-1,0,-1),(0,0,1),(0,0,-1)]):
 g=RotateGraph();g.put(A+0x28,'<f',scale);g.put(B,'<4f',*v,1)
 g.run([call(0x4062d0,args=[A,B,2,1])],f'angle clamp/sign/{scale}/{v}')
# Lifecycle and late Physics lookup, with untouched bytes checked.
for fill,flags in itertools.product([0,0xa5,255],[0,1,2,3,255,256,257,0xffffffff]):
 g=RotateGraph();g.image[P-BASE:P-BASE+0x58]=bytes([fill])*0x58;g.put(P+8,'<I',flags)
 g.run([call(0x517cd0,P,[0])]*2+[call(0x517cc0,P)],f'initialize/destroy fields/{fill}/{flags}')
for flags in [0,1,2,255,256,257,0xffffffff]:
 g=RotateGraph();g.run([call(0x517d40),call(0x517cf0,HEAP,[flags])],f'factory/delete/{flags}')
for shape in ['absent','head','middle','duplicate','wrong']:
 g=RotateGraph();other=g.component(0x5bd63b29 if shape=='duplicate' else 1)
 g.put(Q+16,'<I',other if shape=='duplicate' else 0)
 if shape=='middle':g.put(other+16,'<I',Q)
 g.put(OBJ+0x100,'<I',0 if shape=='absent' else other if shape in ['middle','wrong'] else Q)
 g.run([call(0x517d20,P)]*2,f'late Physics link/{shape}')
# Every immediate branch, parameter priority, and distinct Physics owner.
for name in [0,0xc876adf2,0xc876adf4,0xffffffff]:
 g=RotateGraph();r=g.run([g.command(name=name)],f'unhandled/{name:x}');assert r[0]['result']==2
axes=[0x7323e97c,0x0424d9ea,0x9d2d8850]
for mask,angle,other_owner in itertools.product(range(8),[-180.,-30.,-0.,0.,45.,90.,360.],[False,True]):
 g=RotateGraph();items=[(key,2,bits(angle+(i*15 if angle else 0))) for i,key in enumerate(axes) if mask&(1<<i)]
 if other_owner:g.put(Q+12,'<I',OBJ+0x400);g.put(OBJ+0x46c,'<16f',*[i*.25 for i in range(16)])
 g.put(Q+0x34c,'<B',2)
 g.run([g.command(items)]*2,f'immediate priority/physics owner/{mask}/{angle}/{other_owner}')
# Timed setup preserves inactive axes, accepts QB int/float and flag synonyms.
units=[[],[0xd029f619],[0x49e0ee96],[0x019176c5],[0x4a07c332],[0x019176c5,0xd029f619]]
for unit,kind,duration in itertools.product(units,[1,2],[0,1,125,-250]):
 g=RotateGraph();g.axis(1,2,-3,.5)
 items=[(0x79a07f3f,kind,duration&0xffffffff if kind==1 else bits(duration)),(axes[0],2,bits(-90)),(axes[2],1,45)]+[(0,13,u) for u in unit]
 g.run([g.command(items)]*2,f'timed units/types/{unit}/{kind}/{duration}')
for mask in range(8):
 g=RotateGraph();items=[(0x79a07f3f,2,bits(1000))]+[(key,2,bits((-1 if i%2 else 1)*90)) for i,key in enumerate(axes) if mask&(1<<i)]
 g.run([g.command(items)]+[call(0x517dc0,P)]*5,f'timed frame integration/{mask}',{0x684fc8:bits(20)})
for mode in ['wrong duration','included','indirect','empty seconds']:
 g=RotateGraph();items=[(0x79a07f3f,3,g.text('wrong')),(axes[0],2,bits(30))] if mode=='wrong duration' else [(0x79a07f3f,2,bits(1)),(0,13,0xd029f619)]
 if mode!='empty seconds':items += [(axes[1],2,bits(-45))]
 params=g.structure(items)
 if mode=='included':g.symbol(0x76665555,10,params);params=g.structure([(0,13,0x76665555)])
 if mode=='indirect':g.symbol(0x76665555,2,bits(1));params=g.structure([(0x79a07f3f,13,0x76665555),(axes[1],2,bits(60)),(0,13,0xd029f619)])
 g.run([g.command(params=params),call(0x517dc0,P)],'QB routing/'+mode)
# Per-frame clipping, negative/zero duration scales, and suspension flags.
for axis,rate,target,progress,scale in itertools.product(range(3),[-2.,0.,2.],[0.,.125,1.],[0.,.125],[0.,1.,30.,-1.]):
 g=RotateGraph();g.axis(axis,target,rate,progress);g.put(P+8,'<I',0x80000002)
 g.run([call(0x517dc0,P)]*2,f'frame clip/{axis}/{rate}/{target}/{progress}/{scale}',{0x684fc8:bits(scale)})
for mask in range(8):
 g=RotateGraph()
 for i in range(3):g.axis(i,.25,(-1 if i==1 else 1),.125,255 if mask&(1<<i) else 0)
 g.run([call(0x517dc0,P)]*3,f'frame active bytes/{mask}',{0x684fc8:bits(10)})
# Real named-node lookup feeds the signed target-angle helper.
for xyz,legacy,missing in itertools.product([(1,2,3),(1,2,13),(11,2,3),(-9,2,3),(1,2,-7),(8,5,9)],[False,True],[False,True]):
 g=RotateGraph();node=g.target(xyz,legacy,missing)
 items=[(0x79a07f3f,2,bits(1)),(0,13,0xd029f619),(axes[1],2,bits(25)),(0x7a8017ba,13,node)]
 g.run([g.command(items)]+[call(0x517dc0,P)]*4,f'node target/{xyz}/{legacy}/{missing}',{0x684fc8:bits(20)})
# Original base descriptor invokes the concrete recovered command.
for items,name in [([],0xc876adf3),([(axes[2],2,bits(30))],0xc876adf3),([(0x79a07f3f,2,bits(1000)),(axes[1],2,bits(90))],0xc876adf3),([],0xdeadbeef)]:
 g=RotateGraph();desc=g.alloc(24);g.put(desc,'<6I',name,0x52d61a0d,0,0,0,0)
 g.run([call(0x45d720,P,[desc,g.structure(items),g.script]),call(0x517dc0,P)],f'virtual descriptor/{name:x}/{items}')
# Shared builder creates both components, then actual commands, updates and disposal.
shared_records=[]
for reversed_ in [False,True]:
 g=RotateGraph();registry=[(0x52d61a0d,0x517d40),(0x5bd63b29,0x505440)];g.registry(registry)
 order=registry[::-1] if reversed_ else registry;descriptors=[g.structure([(0xb6015ea8,13,t)]) for t,_ in order]
 calls=[call(0x45e510,OBJ)]+[call(0x45ee20,OBJ,[s,0]) for s in descriptors]+[call(0x45db30,OBJ)]
 g.run(calls,f'shared startup/{reversed_}');components={};node=oracle.word(OBJ+0x100)
 while node:components[oracle.word(node+4)]=node;node=oracle.word(node+16)
 rotate=components[0x52d61a0d];assert oracle.word(rotate+0x54)==components[0x5bd63b29]
 params=g.structure([(0x79a07f3f,2,bits(500)),(axes[1],2,bits(-90))]);desc=g.alloc(24);g.put(desc,'<6I',0xc876adf3,0x52d61a0d,0,0,0,0)
 g.run(calls+[call(0x45d720,rotate,[desc,params,g.script])]+[call(0x517dc0,rotate)]*4+[call(0x45d890,OBJ)],f'shared command/frame/disposal/{reversed_}',{0x684fc8:bits(15)})
 shared_records.append({'reverse_order':reversed_,'components':{hex(k):v for k,v in components.items()},'frame_calls':4})
prefix_records=[]
for heap_index,local,id_ in itertools.product([0,1,2,0xffffffff],[0,1,256,257],[0,0xffffffff]):
 g=ScoreGraph();g.symbol(0x78f80ec4,2,bits(.125));g.registry([(0xce0ca665,0),(0xb87c8e43,0),(0x43686585,0x519740),(0xf27a294d,0x51bd80),(0x27d7cd28,0x41eec0),(0xd262802f,0x518b60),(0xbf518e27,0x514430),(0x270f56e1,0x523490),(0xd9151d4d,0x517830),(0x5bd63b29,0x505440),(0x52d61a0d,0x517d40)])
 mutate=bool(len(prefix_records)%2)
 if mutate:g.put(DLOG+4,'<2I',OBJ+0x14,0x77700000+len(prefix_records))
 stages=g.run([],f'skater through Rotate/{heap_index}/{local}/{id_}',{0x690fa0:0xfffffffe})
 before=bytes(oracle.cpu.mem_read(BASE,len(initial)));cpu=oracle.cpu;sp=oracle.stack+0x18000
 args=[17,MANAGER,local,id_,heap_index,0x12345678]
 cpu.mem_write(sp,struct.pack('<7I',oracle.stop,*args));cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,OBJ);cpu.reg_write(UC_X86_REG_FPCW,0x7f)
 try:cpu.emu_start(0x582d90,oracle.stop,count=500000)
 except Exception:print('PREFIX FAILED',hex(cpu.reg_read(UC_X86_REG_EIP)),args,flush=True);raise
 assert cpu.reg_read(UC_X86_REG_EIP)==0x45ee20 and oracle.word(BOUNDARY+8)==OBJ
 chain=[];c=oracle.word(OBJ+0x100)
 while c:chain.append((c,oracle.word(c+4)));c=oracle.word(c+16)
 assert [t for _,t in chain]==[0xce0ca665,0xb87c8e43,0x43686585,0xf27a294d]+([0x27d7cd28] if local&255 else [])+[0xd262802f]+([0xbf518e27,0x270f56e1,0xd9151d4d,0x5bd63b29,0x52d61a0d] if local&255 else [])
 component=next(c for c,t in chain if t==0xd262802f);score=oracle.word(component+0x18);player=int.from_bytes(cpu.mem_read(score+8,2),'little')
 assert oracle.word(OBJ+0x278)==component and player==(oracle.word(OBJ+0x14)&65535)
 params=oracle.word(BOUNDARY+4);next_type=oracle.word(oracle.word(params+4)+8)
 assert next_type==(0x11b4c67f if local&255 else 0x850eef66)
 if local&255:
  links={t:c for c,t in chain}
  assert oracle.word(OBJ+0x258)==links[0x270f56e1] and oracle.word(OBJ+0x284)==links[0xd9151d4d] and oracle.word(OBJ+0x280)==links[0x5bd63b29]
  assert oracle.cpu.mem_read(links[0xd9151d4d]+0x18,1)==b'\x00'
 after=bytes(cpu.mem_read(BASE,len(initial)));outputs=[];known={row[0] for row in exports}
 for page in range(0,len(initial),4096):
  if before[page:page+4096]!=after[page:page+4096]:
   for j in range(page,min(page+4096,len(initial)),4):
    if before[j:j+4]!=after[j:j+4]:
     outputs.append([BASE+j,after[j:j+4].hex()])
     if int.from_bytes(after[j:j+4],'little') in known:fields.add(BASE+j)
 stages.append({'fn':'0x582d90','this':OBJ,'args':args+[DIAG],'result':None,'outputs':outputs,'globals':[oracle.global_read(x) for x in globals_],'callbacks':0,'expected_trap':True})
 oracle.counts['thug_skater_construct_rotate_prefix_draft']+=1
 prefix_records.append({'arguments':args,'components':chain,'boundary':list(struct.unpack('<4I',cpu.mem_read(BOUNDARY,16))),
  'next_type':hex(next_type),'score':{'component':component,'state':score,'player_id':player},'diagnostics_mutate_id':mutate})
scope='Eleven complete original routines recover SkaterRotate creation, initialization, Physics linking, disposal, full frame update and the rotate checksum command, plus coordinate matrix construction, Z premultiplication, dominant vector coordinate and projected signed direction angle. Immediate X/Y/Z/reversal, timed duration unit synonyms, named node targets, completion clipping and suspension run through original callees and the base virtual descriptor. Shared builder creates Rotate/Physics in both orders, runs commands and frames, then destroys the owner. Original582d90 now creates Rotate and stops before SkaterGap11b4c67f; nonlocal850eef66 is unchanged. All returns, arena/globals/heap and completed-call preserved registers compare without NaN masks. Successful allocation, valid graphs, defined basis indices and finite active rotation angles are fixture contracts; SDK trigonometry remains a declared platform boundary without physical x87 accuracy claims. Zero-duration command setup is checked separately from its nonfinite frame path. This is not a complete skater, cold boot, rendered frame or playable level.'
extra={**extra,'direct_initializer_prefix':True,'boundary_address':BOUNDARY,'boundary_factory':0x45ee20,
 'native_callbacks':[{'module':'skater-construction-diagnostic-fixture.wasm','export':'fixture_skater_print','slots':[DIAG+4]}]}
saved_coverage=coverage.copy();coverage.clear();finish('skater-rotate',scope,{},extra);coverage.update(saved_coverage)
report_path=folder/'skater-rotate-original.json';report=json.loads(report_path.read_text())
report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
code=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(0x182d90,1639),0x582d90))
report['partial_constructor']={'address':'0x582d90','covered':sum(bool(prefix_hits[i.address]) for i in code),'total':len(code),'boundary':'0x45ee20','interrupted_calls':len(prefix_records),'records':prefix_records}
report['shared_startup_records']=shared_records
report_path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k in ['cases','calls','instruction_coverage']}),flush=True)
