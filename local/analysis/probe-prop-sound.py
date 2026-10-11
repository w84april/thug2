"""Original Sound update with concrete geometry, voice and playback callees."""
from pathlib import Path
source=Path('local/analysis/probe-prop-lifecycle.py').read_text().split('# Constructor/reset fields')[0]
exec(compile(source,'<preserved prop setup>','exec'))
import random,math,hashlib,subprocess
from unicorn.x86_const import UC_X86_REG_EIP,UC_X86_REG_FPSW,UC_X86_REG_FPTAG
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.coverage.clear()
specs=[(0x404010,72,'approach_number',3,'double',False),(0x4025a0,92,'bounds_contains_point',1,'word',True),
 (0x403bb0,67,'bounds_center',1,'word',True),(0x403c00,406,'bounds_nearest_surface',2,'void',True),
 (0x41f470,139,'sound_transform',3,'word',False),(0x412060,4,'moving_collision_orientation',0,'word',True),
 (0x4123b0,6,'static_collision_orientation_get',0,'word',True),(0x49e740,20,'geometry_orientation',0,'word',True),
 (0x468120,124,'sound_volume_contains',1,'byte',True),(0x4681a0,270,'sound_volume_nearest',2,'word',True),
 (0x46aec0,784,'proximity_nearest',2,'word',True),(0x432e50,94,'object_sound_origin',2,'word',True),
 (0x432f10,90,'object_sound_range_origin',2,'byte',True),(0x432f70,113,'sound_parameters_approach',1,'void',False),
 (0x432d40,65,'object_sound_queue',2,'void',True),(0x47ae20,107,'sound_register_owner',3,'void',True),
 (0x47b6f0,98,'sound_active_id',2,'byte',True),(0x47ba00,94,'sound_owner_parameters',3,'word',True),
 (0x47c140,535,'object_sound_play',5,'word',True),(0x433480,329,'object_sound_pending_update',0,'void',True),
 (0x4335d0,95,'object_sound_update',0,'void',True)]
for a,n,name,argc,result,this in specs:bind_new(a,n,'thug_'+name+'_draft',argc,result,this=this)
functions['0x404010']['float_args']=[0,1,2];functions['0x432f70']['cleanup']=4
for a in [0x4123b0,0x49e740,0x47ba00]:functions[hex(a)]['pointer_result']=True
bind(0x432d90,'thug_object_sound_construct_draft',0,'word')
bind(0x47bb50,'thug_sound_remove_owner_draft',1)
bind(0x45f3a0,'thug_composite_create_from_array_draft',3,'word',True,True)
bind(0x45d890,'thug_composite_destroy_draft',0,heap=True,diag=True)
bind(0x45db30,'thug_composite_finalize_draft',0,heap=True,diag=True)
exports.append([0x691928,'thug_static_collision_orientation_draft'])
function_exports += [[0x412060,'thug_moving_collision_orientation_draft'],[0x4123b0,'thug_static_collision_orientation_get_draft']]
for off in range(0,64,4):glob('thug_static_collision_orientation_draft',0x691928+off,bits(1) if off%20==0 else 0,offset=off)
pointer_globals=[index[0x6f85b0]]
for i in range(128):
 exports.append([0x6f3668+i*24,'thug_sound_pending_pool_draft',i*24])
 for j in range(6):
  at=0x6f3668+i*24+j*4;glob('thug_sound_pending_pool_draft',at,0,offset=i*24+j*4)
  if j>=3:pointer_globals.append(index[at])
for i in range(48):
 exports += [[0x6f7a68+i*60,'thug_sound_voices',i*60],[0x6f7a74+i*60,'thug_sound_voices',i*60+12],
  [0x6f85c8+i*24,'thug_audio_slots',i*24],[0x6f85cc+i*24,'thug_audio_slots',i*24+4]]
 pointer_globals.append(index[0x6f7a70+i*60])
extra['pointer_globals']=pointer_globals
AUD=BASE+0x1c0000;AUDLOG=AUD+128;CB=0x3f02000;TLS=0x2000800
VIEW=BASE+0x1d0000;CAM=VIEW+0x200;MAP=VIEW+0x400;CONFIG=VIEW+0x500
SAMPLE=VIEW+0x600;PCM=VIEW+0x700;DEVICE=VIEW+0x800;BUFFER=DEVICE+16;BUFFER2=DEVICE+32;SPATIAL=DEVICE+48;LISTENER=DEVICE+64
BM=VIEW+0x900;SM=VIEW+0xa00;LM=VIEW+0xb00;DM=VIEW+0xc00;CONTROLS=VIEW+0xd00;CHUNK1=VIEW+0xe00;CHUNK2=VIEW+0xf00
for name,a,val,width in [('thug_viewport_mode',0x70134c,0,4),('thug_viewport_mapping',0x67e540,MAP,4),
 ('thug_sound_configuration',0x6f85a8,CONFIG,4),('thug_sound_device',0x7d6a38,DEVICE,4),
 ('thug_sound_asset_count_a',0x6f85b8,1,4),('thug_sound_asset_count_b',0x6f85b4,0,4),
 ('thug_audio_slot_count',0x6f8a50,1,4),('thug_audio_slot_cursor',0x6f8a54,0,4),
 ('thug_audio_spatial_enabled',0x6f8a4c,0,1),('thug_audio_frequency_enabled',0x67da40,1,1),
 ('thug_sound_debug_mode',0x684fa8,0,1),('thug_audio_master_volume',0x67db08,bits(100),4),
 ('thug_audio_play_attempts',0x6f8a48,0,4),('thug_audio_listener',0x6f85c0,LISTENER,4),
 ('thug_frame_counter',0x7d1ec8,60,4),('thug_frame_rate',0x684fd0,bits(60),4),
 ('thug_frame_length_scale',0x684fc8,bits(1),4),('thug_sound_default_distance',0x67da34,bits(1020),4),
 ('thug_sound_suppressed_a',0x6fc49c,0,1),('thug_sound_suppressed_b',0x6fa7d4,0,1),('thug_math_errno',TLS+8,0,4)]:
 if a in index:defaults[index[a]]=val
 else:glob(name,a,val,width)
# Actual addresses below are checked against the existing audio/camera fixture.
prior_audio=json.loads((ROOT/'local/validation/collision/audio-device-fixtures.json').read_text())
prior_by_name={g[0]:g for g in prior_audio['globals'] if g[3]==0}
for g in globals_:
 if g[0] in prior_by_name and g[3]==0:
  assert (g[1],g[2])==tuple(prior_by_name[g[0]][1:3]),(g,prior_by_name[g[0]])
for i in range(10):glob('thug_viewports',0x701350+4*i,VIEW if i==0 else 0,offset=4*i)
ASSET=0x6f5e68;exports += [[ASSET,'thug_sound_assets_a'],[0x666b34,'thug_audio_spatial_iid'],[0x6f8a48,'thug_audio_play_attempts'],[0x67db08,'thug_audio_master_volume'],[0x6f8a4c,'thug_audio_spatial_enabled']]
for j,v in enumerate([0x12345678,0,bits(100),bits(100),bits(1020),SAMPLE,1]):glob('thug_sound_assets_a',ASSET+4*j,v,offset=4*j)
names=['orientation','commit','min','max','position','volume','pan','frequency','stop','release','release_spatial','create','query','lock','unlock','seek','play']
argc=[8,1,3,3,5,2,2,2,1,1,1,4,3,8,5,2,4]
slots={LM+0x34:0,LM+0x44:1,SM+0x40:2,SM+0x44:3,SM+0x4c:4,BM+0x3c:5,BM+0x40:6,BM+0x44:7,BM+0x48:8,BM+8:9,SM+8:10,DM+12:11,BM:12,BM+0x2c:13,BM+0x4c:14,BM+0x34:15,BM+0x30:16}
oracle.cpu.mem_map(CB,4096);oracle.cpu.mem_map(0x2000000,0x10000)
def callback(cpu,address,size,user):
 kind=(address-CB)//16;sp=cpu.reg_read(UC_X86_REG_ESP);a=[oracle.word(sp+4+i*4) for i in range(argc[kind])];c=[oracle.word(AUD+4*i) for i in range(32)]
 assert c[0]<200
 args=a[1:] if kind!=13 else [a[1],a[2],a[7],c[6],c[7],c[8],c[9]]
 record=[kind,a[0],*args,*([0]*(7-len(args))),*[oracle.word(c[16]+4*i) for i in range(6)],oracle.word(c[18]),oracle.word(c[17]),oracle.word(c[17]+4),oracle.word(c[19]),cpu.mem_read(c[20],1)[0]]
 at=AUDLOG+c[0]*80;cpu.mem_write(at,struct.pack('<20I',*record));oracle.setword(AUD,c[0]+1)
 if kind==11:fields.add(at+12)
 if kind==12:fields.update([at+8,at+12])
 if c[10]==kind:
  if c[13]==1:cpu.mem_write(c[11],bytes([c[12]&255]))
  else:oracle.setword(c[11],c[12])
 if kind==11:oracle.setword(a[2],c[4])
 if kind==12:oracle.setword(a[2],c[5])
 if kind==13:
  for at,v in zip(a[3:7],c[6:10]):oracle.setword(at,v)
 cpu.reg_write(UC_X86_REG_EAX,c[2] if c[1]==kind else 0);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4+argc[kind]*4)
for i in range(17):oracle.cpu.hook_add(UC_HOOK_CODE,callback,begin=CB+16*i,end=CB+16*i)
GET_ERROR,GET_TLS,SET_ERROR=oracle.stop+0x600,oracle.stop+0x610,oracle.stop+0x620
for a,t in [(0x6450d4,GET_ERROR),(0x7db10c,GET_TLS),(0x64516c,SET_ERROR)]:oracle.setword(a,t)
oracle.setword(0x68ef14,7);last_error=0x12345678
def os_service(cpu,address,size,user):
 global last_error
 sp=cpu.reg_read(UC_X86_REG_ESP)
 if address==GET_ERROR:cpu.reg_write(UC_X86_REG_EAX,last_error)
 elif address==GET_TLS:assert oracle.word(sp+4)==7;cpu.reg_write(UC_X86_REG_EAX,TLS)
 else:last_error=oracle.word(sp+4)
for a,n in [(GET_ERROR,0),(GET_TLS,4),(SET_ERROR,4)]:
 oracle.cpu.mem_write(a,b'\xc2'+struct.pack('<H',n));oracle.cpu.hook_add(UC_HOOK_CODE,os_service,begin=a,end=a)
extra['native_callbacks']=[{'module':'prop-sound-audio-callbacks.wasm','export':'fixture_audio_'+name,'original':CB+16*i} for i,name in enumerate(names)]
fields.update(slots);fields.update(AUD+4*i for i in [11,16,17,18,19,20])
class SoundGraph(PropGraph):
 def __init__(self):
  super().__init__();self.image[AUD-BASE:AUD-BASE+0x20000]=bytes(0x20000)
  self.put(P,'<48I',*([0]*48));self.put(P+12,'<I',OBJ);self.put(OBJ+0x4c,'<4f',25,10,30,1)
  self.put(P+0x98,'<4f',25,10,30,1);self.put(VIEW+24,'<I',CAM);self.put(MAP,'<10i',0,*([-1]*9))
  self.put(CAM+0x5c,'<4f',0,0,0,1);self.put(CAM+0x6c,'<16f',*[1 if i%5==0 else 0 for i in range(16)])
  self.put(CONFIG,'<2I',0,0);self.put(SAMPLE,'<16I',0,22050,0,0,0,36,0,13,0,PCM+128,1,2,3,4,0,PCM)
  self.put(CONTROLS,'<4I',bits(75),bits(85),bits(1020),0)
  for i in range(128):self.image[PCM-BASE+i]=(i*37+11)&255
  for a,m in [(DEVICE,DM),(BUFFER,BM),(BUFFER2,BM),(SPATIAL,SM),(LISTENER,LM)]:self.put(a,'<I',m)
  for a,i in slots.items():self.put(a,'<I',CB+16*i)
  self.put(AUD,'<32I',0,0xffffffff,0x80004005,0,BUFFER2,SPATIAL,CHUNK1,7,CHUNK2,6,0xffffffff,0,0,4,0,0,0x6f85c8,0x6f7a68,0x6f8a48,0x67db08,0x6f8a4c,*([0]*11))
  self.symbol(0x6d2e270e,1,0);self.symbol(0xd7bb618d,1,1)
 def vec(self,values):
  p=self.alloc(16);self.put(p,'<4f',*values);return p
 def bounds(self,mins=(-10,-20,-30,1),maxs=(10,20,30,1)):
  p=self.alloc(32);self.put(p,'<8f',*mins,*maxs);return p
 def geometry(self,moving=True,render=False):
  p=self.alloc(32);c=self.alloc(0xd4);vt=self.alloc(40);m=0x412060 if moving else 0x4123b0
  self.put(vt+32,'<I',m);fields.add(vt+32);self.put(c,'<I',vt);self.put(c+0x20,'<16f',*[1 if i%5==0 else 0 for i in range(16)])
  self.put(p+0x14,'<2I',1 if render else 0,c);return p,c
 def volume(self,shape=2,proximity=False):
  p=self.alloc(0xa8);self.image[p-BASE:p-BASE+0xa8]=bytes(0xa8)
  self.put(p+4,'<4f',5,10,15,1)
  if proximity:
   self.put(p+0x6c,'<3I',shape,bits(10),0);geom,c=self.geometry();self.put(p+0x78,'<I',geom)
   self.put(p+0x14,'<16f',*[1 if i%5==0 else 0 for i in range(16)]);self.put(p+0x7c,'<8f',-5,-10,-15,1,15,30,45,1)
  else:self.put(p+0x28,'<3I',shape,bits(10),bits(100));self.put(p+0x38,'<8f',-5,-10,-15,1,15,30,45,1)
  return p
def check(g,calls,label,changes=None,floats=()):
 oracle.cpu.reg_write(UC_X86_REG_FPSW,0);oracle.cpu.reg_write(UC_X86_REG_FPTAG,0xffff)
 try:stages=case(calls,g.patches(),changes,label)
 except Exception:print('Failed:',label,flush=True);raise
 for s in stages:s['float_fields']=list(floats)
 assert last_error==0x12345678
 if len(labels)%50==0:print('Sound cases',len(labels),flush=True)
 return stages

# Exact arithmetic, boundary selection and input/output aliasing.
rng=random.Random(0x433480)
for target,current,step in itertools.product([-100.,0.,100.],[-100.,0.,100.],[-1000.,-1.,0.,1.,1000.]):
 check(SoundGraph(),[call(0x404010,args=[bits(x) for x in [target,current,step]])],f'approach {target}/{current}/{step}')
for point in itertools.product([-40.,0.,40.],repeat=3):
 g=SoundGraph();b=g.bounds();v=g.vec([*point,2]);out=g.alloc(16)
 check(g,[call(0x4025a0,b,[v]),call(0x403c00,b,[v,out]),call(0x403bb0,b,[out])],f'box surface {point}')
for point in [(9,0,0),(0,19,0),(0,0,29),(-9,0,0),(0,-19,0),(0,0,-29),(10,20,30),(0,0,0)]:
 for offset in [0,4,-4,64]:
  g=SoundGraph();b=g.bounds();v=g.vec([*point,2]);out=v+offset
  check(g,[call(0x403c00,b,[v,out])],f'box closest alias {point}/{offset}')
for i in range(40):
 g=SoundGraph();m=g.alloc(64);v=g.vec([rng.uniform(-100,100) for _ in range(4)]);g.put(m,'<16f',*[rng.uniform(-10,10) for _ in range(16)])
 out=v if i%3==0 else m+4 if i%3==1 else g.alloc(16)
 check(g,[call(0x41f470,args=[out,v,m])],f'transform order/alias {i}')
for moving,render in itertools.product([False,True],repeat=2):
 g=SoundGraph();p,c=g.geometry(moving,render)
 check(g,[call(0x49e740,p),call(0x412060,c),call(0x4123b0,c)],f'actual collision matrix getter {moving}/{render}')
for shape,point in itertools.product([0,2,3],[(5,10,15,1),(15,10,15,1),(50,50,50,1),(-50,-50,-50,0)]):
 g=SoundGraph();p=g.volume(shape);v=g.vec(point);out=g.alloc(16);calls=[call(0x468120,p,[v])]
 if shape!=3:calls += [call(0x4681a0,p,[out,v])]
 check(g,calls,f'volume {shape}/{point}')
for shape,point in itertools.product([0,1,2,4],[(5,10,15,1),(50,50,50,1),(-50,-50,-50,0),(0,0,0,1)]):
 g=SoundGraph();p=g.volume(shape,True);v=g.vec(point);out=g.alloc(16)
 check(g,[call(0x46aec0,p,[out,v])],f'proximity {shape}/{point}')
for i in range(48):
 g=SoundGraph();shape=[0,1,2,4][i%4];p=g.volume(shape,True);v=g.vec([rng.uniform(-10000,10000) for _ in range(4)]);out=v if i%3==0 else g.alloc(16)
 if shape in [2,4]:
  # Nontrivial inverse/world rotations exercise the actual moving-collision
  # matrix getter, not a callback that supplies the expected point.
  angle=(i-24)*.17;c=math.cos(angle);s=math.sin(angle)
  g.put(p+0x14,'<16f',c,0,s,0,0,1,0,0,-s,0,c,0,0,0,0,1)
  geom=g.word(p+0x78);collision=g.word(geom+0x18)
  g.put(collision+0x20,'<16f',c,0,-s,0,0,1,0,0,s,0,c,0,0,0,0,1)
 check(g,[call(0x46aec0,p,[out,v])],f'rotated/aliased proximity {i}')
for volume,camera,prox in itertools.product([False,True],repeat=3):
 g=SoundGraph();p=g.volume();q=g.volume(1,True);g.put(P+0xb8,'<2I',p if volume else 0,q if prox else 0);out=g.alloc(16)
 check(g,[call(0x432e50,P,[out,CAM if camera else 0]),call(0x432f10,P,[CAM if camera else 0,out])],f'Sound origins {volume}/{camera}/{prox}')
for values in [(0,0,0,0,1,1),(20,40,80,10,1,2),(20,40,10,80,-2,-4),(1e20,-1e20,-1e20,1e20,1e19,1e19)]:
 g=SoundGraph();p=g.alloc(48)
 for o,x in zip([8,12,24,28,32,36],values):g.put(p+o,'<f',x)
 check(g,[call(0x432f70,args=[p])]*3,'parameter approach '+str(values))
for scale in [0.,.125,1.,1.001,10.,-1.]:
 for i in range(4):
  g=SoundGraph();p=g.alloc(48)
  for o in [8,12,24,28,32,36]:g.put(p+o,'<f',rng.uniform(-10000,10000))
  check(g,[call(0x432f70,args=[p])]*3,f'frame-scaled approach {scale}/{i}',{0x684fc8:bits(scale)})
for occupied,time in itertools.product([0,1,2],[0,1000,0xffffff00]):
 g=SoundGraph();parameters=g.alloc(48);g.put(parameters,'<12I',*range(1,13))
 for i in range(occupied):g.put(P+0x38+i*0x30,'<I',0x7777)
 check(g,[call(0x432d40,P,[parameters,time])]*3,f'queue occupied{occupied}/time{time}')
for fill,count,id_ in [(0,0,1),(1,127,2),(128,0,3),(128,128,1),(0,129,1),(0,0,0)]:
 g=SoundGraph();changes={0x6f85bc:count}
 for i in range(fill):changes[0x6f3668+24*i+8]=1
 check(g,[call(0x47ae20,CONFIG,[id_,0x12345678,P])]*2+[call(0x47bb50,CONFIG,[P])],f'pending pool {fill}/{count}/{id_}',changes)
for slot,active,device in itertools.product([0,47],[0,1],[0,1]):
 g=SoundGraph();out=g.alloc(4);node=g.alloc(24);g.put(node,'<6I',123,456,1,P,0,0)
 changes={0x6f7a68+slot*60:123,0x6f85c8+slot*24:BUFFER,0x6f85d8+slot*24:active,0x7d6a38:DEVICE if device else 0,0x6f85b0:node}
 calls=[call(0x47b6f0,CONFIG,[123,out]),call(0x47b6f0,CONFIG,[123,0]),call(0x47b6f0,CONFIG,[0,out])]
 for flag in [0,1,256,257]:calls.append(call(0x47ba00,CONFIG,[P,456 if flag&255 else 123,flag]))
 calls += [call(0x47ba00,CONFIG,[P+4,123,0]),call(0x47ba00,CONFIG,[P,999,0])]
 check(g,calls,f'owner active {slot}/{active}/{device}',changes)

# Full playback goes through the maintained mixer/device code and explicit OS
# callbacks; no successful game-level playback stub is substituted.
for mode in ['normal','queue','queue second','queue full','missing asset','disabled','no camera','play failure','detached','silent detached','silent nonloop','forced silent','volume origin','proximity origin','both origins','debug']:
 g=SoundGraph();changes={};detached=mode in ['detached','silent detached'];force=mode=='forced silent'
 if mode in ['queue','queue second','queue full','forced silent','silent detached','silent nonloop']:g.put(P+0x98,'<4f',5000,0,0,1)
 if mode=='silent nonloop':changes[ASSET+24]=0
 for i in range(2 if mode=='queue full' else 1 if mode=='queue second' else 0):g.put(P+0x38+0x30*i,'<I',7)
 if mode=='missing asset':changes[0x6f85b8]=0
 if mode=='disabled':changes[0x7cefa8]=2
 if mode=='no camera':g.put(VIEW+24,'<I',0)
 if mode=='play failure':g.put(AUD+4,'<I',16)
 if mode in ['volume origin','both origins']:g.put(P+0xb8,'<I',g.volume())
 if mode in ['proximity origin','both origins']:g.put(P+0xbc,'<I',g.volume(1,True))
 if mode=='debug':changes[0x684fa8]=1
 check(g,[call(0x47c140,CONFIG,[0x12345678,CONTROLS,P,int(detached),int(force)])],f'play {mode}',changes)
for mode in ['empty','future','near','far','default range','failure','two records','full owner pool']:
 g=SoundGraph();changes={}
 if mode!='empty':
  for i in range(2 if mode=='two records' else 1):
   g.put(P+0x38+0x30*i,'<12I',0x12345678,bits(0 if mode=='default range' else 1020),bits(75),bits(85),bits(75),bits(85),bits(80),bits(90),bits(1),bits(2),0,2000 if mode=='future' else 0)
 if mode=='far':g.put(OBJ+0x4c,'<4f',5000,0,0,1)
 if mode=='failure':g.put(AUD+4,'<I',16)
 if mode=='full owner pool':changes[0x6f85bc]=128
 check(g,[call(0x4335d0,P)]*2,f'full Sound update {mode}',changes)
for distance in [1259.999,1260.,1260.001,1500.,1e6]:
 for count in [0,60,0x7fffffff,0xffffffff]:
  g=SoundGraph();g.put(P+0x98,'<4f',distance,0,0,1)
  g.put(P+0x38,'<12I',0x12345678,bits(1020),bits(75),bits(85),bits(75),bits(85),bits(80),bits(90),0,0,0,0)
  check(g,[call(0x433480,P)],f'retry boundary/wrapped timer {distance}/{count}',{0x7d1ec8:count})
for mutation in ['next queued sound','current rate','owner']:
 g=SoundGraph()
 for i in range(2):g.put(P+0x38+0x30*i,'<12I',0x12345678,bits(1020),bits(75),bits(85),bits(75),bits(85),bits(80),bits(90),0,0,0,0)
 destination,value={'next queued sound':(P+0x68,0),'current rate':(P+0x54,bits(12.5)),'owner':(P+12,OBJ+16)}[mutation]
 g.put(AUD+40,'<4I',16,destination,value,4)
 check(g,[call(0x433480,P)],'device callback mutates '+mutation)
g=SoundGraph();g.registry([(kind,factory) for name,kind,size,vt,ctor,factory,destroy,delete in classes[:4]])
a=g.array(10,[g.structure([(0xb6015ea8,13,kind)]) for name,kind,*rest in classes[:4]])
node=g.structure([(0xa1dc81f9,13,0x12345678)])
check(g,[call(0x45f3a0,MANAGER,[a,node,1]),call(0x45db30,HEAP),call(0x45d890,HEAP)],'four real prop factories and full finalize/moved/destruction')
excluded={}
scope='Twenty-one new original Sound update, playback, queue, ownership and spatial support routines. Actual shared prop construction/finalization uses the concrete Sound moved/update callback. Platform audio methods and CRT TLS are explicit host boundaries. Defined volume kinds and initialized camera state for due queued sounds are contracts: original unsupported shapes/no-camera retry read uninitialized stack outputs. Full scene assembly/scripts/rendering remain incomplete.'
finish('prop-sound',scope,excluded,extra)
