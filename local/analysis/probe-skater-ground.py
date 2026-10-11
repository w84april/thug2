"""Original complete AdjustPhysics frame and surface lighting, real queries."""
from pathlib import Path
exec(compile(Path('local/analysis/probe-skater-adjust.py').read_text().split('# Exact lifecycle')[0],'<preserved Adjust oracle>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x5b9760,3,'collision_accepts_light',0,'byte',False,False,True),(0x417120,18,'collision_probe_accepts_light',0,'byte',False,False,True),
 (0x48e660,197,'model_light_recalculate',0,'void',False,False,True),(0x48e830,111,'model_light_approach',2,'byte',False,False,True),
 (0x48e8a0,22,'model_light_set',1,'byte',False,False,True),(0x4b67e0,98,'light_write_ambient',0,'byte',False,False,False),
 (0x4b6860,116,'light_write_direction',1,'byte',False,False,False),(0x4b6900,25,'light_write_all',0,'void',False,False,False),
 (0x48edb0,334,'light_approach',1,'byte',False,False,False),(0x420670,140,'model_surface_light',3,'void',False,False,True),
 (0x4f82f0,290,'skater_adjust_light',1,'void',False,False,True),(0x4f8aa0,405,'skater_adjust_escape',0,'void',True,True,True),
 (0x4f8420,1655,'skater_adjust_ground',0,'void',True,True,True),(0x4f8c40,131,'skater_adjust_update',0,'void',True,True,True)]
for a,n,name,argc,result,heap,diag,this in specs:bind_new(a,n,'thug_'+name+'_draft',argc,result,heap,diag,this)
for a,indices in [(0x48e830,[0,1]),(0x48e8a0,[0]),(0x48edb0,[0]),(0x420670,[2])]:functions[hex(a)]['float_args']=indices
LOW,HIGH,FACTOR,COLOR,MODELFACTOR=P+0x6000,P+0x6100,P+0x6200,P+0x6300,P+0x6400
LIGHT,PH,STATE,CONTACT,MODEL,RENDER,SHADOW,MODE=P+0x1000,P+0x2000,P+0x4000,P+0x5000,P+0x7000,P+0x7400,P+0x7800,P+0x7900
NAME,INPUT,SOUND=P+0xa000,P+0xc000,P+0xc800
def addglobal(name,a,value=0,offset=0):
 if a not in index:glob(name,a,value,4,offset)
 else:assert globals_[index[a]][0]==name,(hex(a),globals_[index[a]],name);defaults[index[a]]=value
for name,a,value in [('light_current',0x67dc8c,bits(.4)),('light_target',0x67dc90,bits(.1)),('light_ambient_factor',0x67dc94,bits(.8)),
 ('light_ambient_color',0x67dc98,0xaa3980ff),('light_direction_colors',0x67dca0,COLOR),('light_lower_ambient',0x67dca4,bits(.6)),
 ('light_upper_ambient',0x67dca8,bits(.9)),('light_lower_factors',0x67dcac,LOW),('light_upper_factors',0x67dcb0,HIGH),
 ('light_minimum',0x6faae8,bits(.05)),('light_factors',0x6faaec,FACTOR),('adjust_initialized',0x7ccdb0,0)]:addglobal('thug_'+name+'_draft',a,value)
addglobal('thug_model_light_factor_count_draft',0x6faae0,3)
addglobal('thug_skater_orientation_context',0x7ce5d8,MODE)
for name,a,count in [('light_ambient_rgb',0x786f38,3),('light_direction_rows',0x786f48,31*8),('adjust_offsets',0x7ccd60,20)]:
 for i in range(count):addglobal('thug_'+name+'_draft',a+i*4,0x3eaaaaab,i*4)
for a,name in [(0x64a440,'thug_model_light_methods_draft'),(0x64ba0c,'thug_adjust_escape_message_draft')]:
 if not any(row[0]==a for row in exports):exports.append([a,name])
olddebug=debug.__code__
def ground_debug(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);fmt=bytes(cpu.mem_read(oracle.word(sp+4),64)).split(b'\0')[0];file=bytes(cpu.mem_read(oracle.word(sp+8),48)).split(b'\0')[0]
 assert (fmt,file)==(b'M:%s:%i: %s\n',b'mponents\\SkaterAdjustPhysicsComponent.cpp'),(fmt,file)
 count=oracle.word(DLOG);oracle.setword(DLOG,count+1);row=bytearray(128);row[:len(fmt)]=fmt;row[64:64+len(file)]=file
 row[112:120]=cpu.mem_read(sp+12,8);cpu.mem_write(DLOG+16+128*count,bytes(row))
 if oracle.word(DLOG+4):oracle.setword(oracle.word(DLOG+4),oracle.word(DLOG+8))
 cpu.reg_write(UC_X86_REG_EAX,0xffffffff);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
debug.__code__=ground_debug.__code__
initial=bytes(memory);oracle.initial=initial
exec(compile('def triangle'+Path('local/analysis/probe-particle-emission.py').read_text().split('def triangle',1)[1].split('for small_faces in [',1)[0],'<preserved actual triangle/light formats>','exec'))
class GroundGraph(AdjustGraph):
 def __init__(self):
  super().__init__();self.put(OBJ,'<I',0x647650);fields.add(OBJ);self.put(OBJ+0x14,'<I',0x100);self.put(EM+8,'<I',self.table([(0x100,OBJ)]))
  for address,size in [(LIGHT,0x30),(PH,0x1550),(STATE,0x128),(CONTACT,0x80),(MODEL,0x238),(RENDER,0x48),(SHADOW,0x40),(MODE,0x48),(NAME,0x1bc0),(INPUT,0x500),(SOUND,0x24)]:self.image[address-BASE:address-BASE+size]=bytes(size)
  self.put(LIGHT,'<I',0x64a440);fields.add(LIGHT);self.put(LIGHT+8,'<3fI',.4,.2,.8,MODELFACTOR)
  for i in range(31):
   self.put(LOW+i*4,'<f',.1+i*.07);self.put(HIGH+i*4,'<f',.15+i*.12);self.put(FACTOR+i*4,'<f',.25+i*.01);self.put(MODELFACTOR+i*4,'<f',.75+i*.02);self.put(COLOR+i*4,'<4B',i*8,255-i*3,i*7,0xaa)
  self.put(P+0x20,'<5I',PH,MODEL,SHADOW,CONTACT,STATE);self.put(PH+12,'<I',OBJ);self.put(STATE+12,'<I',OBJ);self.put(STATE+0x18,'<I',1)
  self.put(PH+0x150c,'<5I',INPUT,0,SOUND,NAME,0);self.put(PH+0x1528,'<I',STATE);self.put(NAME+0x28,'<I',OBJ)
  self.put(MODEL+0x208,'<I',RENDER);self.put(RENDER+0x2c,'<I',LIGHT)
  self.put(OBJ+0x4c,'<4f',0,4,0,1);self.put(OBJ+0x5c,'<4f',0,3,0,1);self.put(OBJ+0x6c,'<16f',*IDENTITY);self.put(OBJ+0xac,'<4f',2,-1,3,1)
  self.put(PH+0x98,'<4f',0,3,0,1);self.symbol(0x801c9cb6,2,bits(1));self.symbol(0x3eede4d3,2,bits(30))
 def run(self,calls,label,changes=None):
  result=super().run(calls,label,changes)
  if len(labels)%25==0:print('Ground cases',len(labels),flush=True)
  return result
# Arithmetic and actual light virtual call, including both clamps and count reloads.
for current,target,rate in itertools.product([-.75,0,.49,.5,.51,1,2],[0,.5,1],[-.2,0,.02,.8]):
 g=GroundGraph();g.put(LIGHT+8,'<f',current)
 g.run([call(0x48e830,LIGHT,[bits(target),bits(rate)]),call(0x48e660,LIGHT)],f'model approach/{current}/{target}/{rate}',{0x6faae0:3})
for count,current in itertools.product([0,1,3,31],[-3,0,.5,1,3]):
 g=GroundGraph();g.run([call(0x48e8a0,LIGHT,[bits(current)])]*2,f'model set/{count}/{current}',{0x6faae0:count})
for current,target,minimum in itertools.product([-.75,0,.49,.5,.51,1,2],[0,.5,1],[-.25,.05,1.25]):
 g=GroundGraph();g.run([call(0x48edb0,args=[bits(target)])]*2,f'global approach/{current}/{target}/{minimum}',{0x67dc8c:bits(current),0x6faae8:bits(minimum)})
for count in [0,1,31]:
 g=GroundGraph();g.run([call(0x4b67e0),call(0x4b6860,args=[0]),call(0x4b6860,args=[30]),call(0x4b6900)],f'color writers fixed count/{count}',{0x6faae0:count})
for current in [0x80000000,1,0x7f7fffff,0xff7fffff,0x7fc12345,0xffc12345]:
 g=GroundGraph();g.run([call(0x48e8a0,LIGHT,[current])],f'light raw float/{current:x}')
# Original static/moving mesh virtual predicates and per-vertex interpolation.
for small_faces,small_vertices,moving,local,smooth in itertools.product([False,True],repeat=5):
 g=GroundGraph();actor,probe,vertices,points=triangle(g,small_faces,small_vertices,moving)
 g.put(probe+0x34,'<3f',*[sum(p[j] for p in points)/3 for j in range(3)]);g.put(RENDER+0x2c,'<I',LIGHT if local else 0)
 g.run([call(0x5b9760,actor),call(0x417120,probe),call(0x420670,MODEL,[probe,int(smooth),bits(1)])]*2,f'surface light/{small_faces}/{small_vertices}/{moving}/{local}/{smooth}')
for local,smooth in itertools.product([False,True],[0,1,256,257]):
 g=GroundGraph();g.put(RENDER+0x2c,'<I',LIGHT if local else 0)
 g.run([call(0x417120,PH+0xa8),call(0x420670,MODEL,[PH+0xa8,smooth,bits(-2)])],f'light miss/{local}/{smooth}')
# All game callees run. These graphs provide state, not collision answers.
for state,mode,offset in itertools.product([0,1,2,3,4],[0,0xd443a2bc],[0,4,5,6]):
 g=GroundGraph();g.put(STATE+0x18,'<I',state);g.put(MODE+0x40,'<I',mode);g.put(P+0x18,'<I',offset)
 g.run([call(0x4f8420,P,[Q])]*2,f'ground miss/{state}/{mode:x}/{offset}')
for moving,height,state in itertools.product([False,True],[-7,0,3.9999,4,10],[0,1,4]):
 g=GroundGraph();g.plane(height,moving=moving,flags=1);g.put(STATE+0x18,'<I',state)
 g.run([call(0x4f8420,P,[Q])]*2,f'ground hit/{moving}/{height}/{state}')
for state,flag,velocity,gate in itertools.product([0,1,4],[0,1,2],[-1,0,1],[0,1]):
 g=GroundGraph();g.put(STATE+0x18,'<I',state);g.put(STATE+0x60,'<B',flag);g.put(STATE+0x88,'<B',gate);g.put(OBJ+0xb0,'<f',velocity)
 g.run([call(0x4f8c40,P,[Q])]*2,f'frame miss/{state}/{flag}/{velocity}/{gate}')
for old,state,velocity in itertools.product([(1000,3,0,1),(0,4,0,1),(0,50,0,1)],[0,1,4],[(0,0,0,0),(3000,0,0,0)]):
 g=GroundGraph();g.plane(40,velocity=velocity,flags=1);g.put(PH+0x98,'<4f',*old);g.put(STATE+0x18,'<I',state)
 g.run([call(0x4f8aa0,P,[Q]),call(0x4f8c40,P,[Q])],f'moving escape/frame/{old}/{state}/{velocity}')
for kind in ['empty','static','moving','two']:
 g=GroundGraph()
 if kind!='empty':g.plane(0,moving=kind=='moving',flags=1)
 if kind=='two':g.plane(5,moving=False,flags=0x20)
 g.put(PH+0xa8,'<8f',0,4,0,1,0,-4,0,1)
 g.run([call(0x4f82f0,P,[PH+0xa8,Q])]*2,'secondary light/'+kind)
# Contacts release through the original allocated reference object.
bind(0x43eb80,'thug_skater_moving_contact_set_owner',1,'void',True)
for surface,state,locked,held in itertools.product(['static','same moving','other moving','dead'],[0,1,2],[0,1],[0,1]):
 g=GroundGraph();_,owner=g.plane(0,moving=surface!='static',flags=1,velocity=(7,-2,4,1))
 if surface not in ['same moving']:
  old=g.alloc(0x100);g.image[old-BASE:old-BASE+0x100]=bytes(0x100);g.put(old+0xac,'<4f',11,3,-9,1)
 else:old=owner
 g.put(STATE+0x18,'<I',state);g.put(STATE+0x88,'<B',locked);g.put(STATE+0x78,'<B',held)
 if surface=='dead':
  ref=g.alloc(0xb0);g.image[ref-BASE:ref-BASE+0xb0]=bytes(0xb0);g.put(CONTACT+0x18,'<I',ref);calls=[]
 else:calls=[call(0x43eb80,CONTACT,[old])]
 g.run(calls+[call(0x4f8420,P,[Q])],f'ground contact/{surface}/{state}/{locked}/{held}')
# Roof obstruction: near, far, short-motion and restored-position branches.
for moving,roof,old,state,mode in itertools.product([False,True],[9,20,50],[(0,3.75,0,1),(0,1,0,1)],[1,4],[0,0xd443a2bc]):
 g=GroundGraph();g.plane(0,moving=False,flags=1);g.plane(roof,moving=moving,flags=1)
 if roof==9:g.put(OBJ+0x7c,'<4f',0,-400,0,0) # Unusual finite up-vector isolates the near-distance branch.
 g.put(PH+0x98,'<4f',*old);g.put(STATE+0x18,'<I',state);g.put(MODE+0x40,'<I',mode)
 g.run([call(0x4f8420,P,[Q])],f'roof correction/{moving}/{roof}/{old}/{state}/{mode:x}')
# The actual owner dispatcher reaches the recovered Adjust virtual slot.
bind(0x45d920,'thug_object_update_components',0,'void',True,True)
for kind,mode in itertools.product(['stationary','falling','floor','moving roof'],[1,4]):
 g=GroundGraph();g.put(OBJ+0x100,'<I',P);g.put(STATE+0x18,'<I',mode)
 if kind=='stationary':g.put(PH+0x98,'<4f',0,4,0,1)
 if kind in ['floor','moving roof']:g.plane(0,moving=False,flags=1)
 if kind=='moving roof':g.plane(40,moving=True,flags=1)
 g.run([call(0x45d920,OBJ,[Q])]*3,f'original owner virtual frame/{kind}/{mode}')
# Overlapping model factors exercise the original live current/array reads.
for destination,count in itertools.product([LIGHT+8,LOW,HIGH],[1,3]):
 g=GroundGraph();g.put(LIGHT+20,'<I',destination)
 g.run([call(0x48e660,LIGHT)]*2,f'model factors overlap/{destination:x}/{count}',{0x6faae0:count})
for count,target in itertools.product([0,31],[0,.5,1]):
 g=GroundGraph();g.run([call(0x48edb0,args=[bits(target)])]*2,f'global factor bounds/{count}/{target}',{0x6faae0:count})
scope='Fourteen original routines recover complete SkaterAdjustPhysics update, moving escape/contact reacquisition, grounded position correction and secondary surface lighting, plus actual mesh light predicate, model/global approach and color writes. Real geometry queries, state changes, event delivery, light virtual and reference cleanup execute. Synthetic initialized graphs are not a playable training skater. Whole arena/globals/heap and preserved registers compare; no numeric exceptions. Full startup, other skater behavior, camera/rendering and playability remain unfinished.'
extra={**extra,'native_callbacks':[{'module':'skater-construction-diagnostic-fixture.wasm','export':'fixture_skater_print','slots':[DIAG+4]}]}
saved=coverage.copy();coverage.clear();finish('skater-ground',scope,{},extra);coverage.update(saved)
p=folder/'skater-ground-original.json';report=json.loads(p.read_text());report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()};p.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k in ['cases','calls','instruction_coverage']}),flush=True)
