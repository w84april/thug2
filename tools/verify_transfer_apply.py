"""Compare complete transfer application, matrix arithmetic and event removal."""
from pathlib import Path
prefix=Path(__file__).with_name('verify_transfer.py').read_text().split('# Raw forward copies')[0]
exec(compile(prefix.replace("'transfer.json'","'transfer-apply.json'"),str(Path(__file__).with_name('verify_transfer.py')),'exec'))
# CRT thread-local errno is an explicit platform global, outside game fixtures.
TLS=0x2600800
oracle.cpu.mem_map(0x2600000,0x10000)
glob('thug_math_errno',TLS+8,0)
M0,M1,MOUT,INTERP,EVTABLE,EVENT_ENTRIES,SCRIPT0,LIST_TABLE,LIST_BUCKETS,LIST_HEAD,LIST_NODES,CODE2=0x1638000,0x1638100,0x1638200,0x1639000,0x163a000,0x163a100,0x163b000,0x163b400,0x163b500,0x163b600,0x163b800,0x163c000
NEW=[(0x404120,'thug_matrix_scale',1,'word',False,False,True),(0x4041e0,'thug_matrix_determinant',0,'double',False,False,True),(0x4043a0,'thug_matrix_adjugate',1,'void',False,False,True),(0x405600,'thug_matrix_inverse',0,'word',False,False,True),(0x405310,'thug_matrix_to_axis_angle',2,'void',False,False,True),(0x405990,'thug_matrix_interpolation_initialize',2,'void',False,False,True),(0x45fdf0,'thug_script_events_remove',1,'void',True,False,True),(0x473690,'thug_script_remove_event',1,'void',True,False,True),(0x4607a0,'thug_object_remove_event',1,'void',True,False,True),(0x502f20,'thug_skater_apply_transfer',1,'void',True,True,True)]
for row in NEW:
 bind(*row);oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=row[0],end=row[0])
functions['0x404120']['float_args']=[0]
glob('thug_matrix_small_angle',0x67c648,0x3d0efa35)
for j in range(4):glob('thug_skater_transfer_velocity',0x7ccdbc+j*4,0xa5a5a5a5,offset=j*4)
exports += [[0x6478d8,'thug_script_listener_methods'],[0x6478dc,'thug_script_listener_list_methods']]
for i in range(8):fields.add(LIST_NODES+i*20)
fields.add(LIST_HEAD)
for at,name in {0x40538d:'zero_axis',0x4053cc:'near_pi',0x4053e4:'largest_x',0x405410:'largest_y',0x405430:'largest_z',0x405628:'inverse_scaled',0x405652:'unit_determinant',0x503053:'negative_transfer_discriminant',0x503354:'flip_surface',0x5034e9:'spawn_transfer_script',0x503539:'remove_release_handler',0x45fe10:'matching_event_removed',0x503525:'post_script_flag_timestamp'}.items():
 branch_at[at]=name;oracle.cpu.hook_add(UC_HOOK_CODE,branch,begin=at,end=at)
for at in [0x463450,0x477130,0x409070,0x461480,0x474b40,0x623630]:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
identity=[1.,0,0,0,0,1.,0,0,0,0,1.,0,0,0,0,1.]
rng=random.Random(0x502f20)
matrices=[identity,[0.]*16,[-x for x in identity],[float(i-8) for i in range(16)]]
for scale in [1e-30,1e-10,1,1e10,1e30]:
 for i in range(6):matrices.append([rng.uniform(-scale,scale) for _ in range(16)])
for axis in range(3):
 for angle in [0,.00001,.005,.01,.1,1,math.pi-1e-4,math.pi,math.pi+1e-4,-math.pi/2]:
  m=identity[:];a,b=[j for j in range(3) if j!=axis];m[a*4+a]=m[b*4+b]=math.cos(angle);m[a*4+b]=math.sin(angle);m[b*4+a]=-math.sin(angle);matrices.append(m)
for lane in [0,5,10,15]:
 for val in [math.inf,math.nan]:m=identity[:];m[lane]=val;matrices.append(m)
for i,m in enumerate(matrices):
 p=[patch(M0,'<16f',*m)]
 stages=case([call(0x4041e0,M0),call(0x4043a0,MOUT,[M0]),call(0x405600,M0)],p,label=f'matrix determinant/adjugate/inverse {i}')
 for s in stages[1:]:s['float_fields']=[MOUT+j*4 for j in range(16)]+([M0+j*4 for j in range(16)] if s['fn']=='0x405600' else [])
 for factor in ([1,-1,0,.7] if i<4 else [1]):
  s=case([call(0x404120,M0,[bits(factor)])],p,label='matrix scaling and identity no-write')[0]
  if factor!=1:s['float_fields']=[M0+j*4 for j in range(16)]
 s=case([call(0x405310,M0,[MOUT,MOUT+16])],p,label=f'matrix rotation axis/angle {i}')[0];s['float_fields']=[MOUT+j*4 for j in range(5)]
 if i<12 or i>=34:
  s=case([call(0x405990,INTERP,[M0,M1])],p+[patch(M1,'<16f',*identity)],label=f'matrix interpolation {i}')[0];s['float_fields']=[INTERP+j*4 for j in range(32,37)]
for shift in [0,4,8,20,60]:
 m=matrices[8]
 s=case([call(0x4043a0,M0+shift,[M0])],[patch(M0,'<16f',*m)],label='adjugate forward overlap')[0];s['float_fields']=[M0+shift+j*4 for j in range(16)]
 for axis,angle in [(M0,MOUT),(M0+16,M0+32),(MOUT,MOUT+4)]:
  s=case([call(0x405310,M0,[axis,angle])],[patch(M0,'<16f',*m)],label='axis/angle aliases matrix or each other')[0];s['float_fields']=[axis+j*4 for j in range(4)]+[angle]
for source,target in [(INTERP,INTERP+64),(M0,INTERP),(INTERP+64,INTERP)]:
 s=case([call(0x405990,INTERP,[source,target])],[patch(M0,'<16f',*matrices[8]),patch(INTERP,'<32f',*(identity+matrices[5]))],label='interpolation input aliases state')[0];s['float_fields']=[INTERP+j*4 for j in range(32,37)]
for threshold in [0,1e-20,-1,math.inf,math.nan]:
 case([call(0x405990,INTERP,[M0,M1])],[patch(M0,'<16f',*identity),patch(M1,'<16f',*identity)],{0x67c648:bits(threshold)},label='small-angle strict equality and unordered threshold')
case([call(0x404120,M0,[bits(1)])],[patch(M0,'<16I',0x7f800001,0xff800001,0x7fc12345,0x80000000,*range(12))],label='identity scale preserves signaling NaN payloads')

# Actual circular listeners plus owned nested parameter graphs.
def event_patches(b,events=(0x8ffefb28,0x123,0x8ffefb28),listeners=(),count=None,table=True):
 p=[raw(SCRIPT0,bytes(0x13c)),patch(SCRIPT0+0xe0,'<I',EVTABLE if table else 0),patch(BODIES+0x10,'<I',SCRIPT0),patch(EVTABLE,'<2I',EVENT_ENTRIES,len(events) if count is None else count),patch(EM+16,'<I',LIST_TABLE),patch(LIST_TABLE,'<6I',2,LIST_BUCKETS,1,0xffffffff,0,0),raw(LIST_BUCKETS,bytes(48))]
 for i,event in enumerate(events):
  params=b.structure([(0x111,3,b.text(b'owned transfer event')),(0x222,10,b.structure([(0x333,1,i)]))])
  p.append(patch(EVENT_ENTRIES+20*i,'<5I',event,0xdead0000+i,0x400+i,params,0xaa0000+i))
 p.append(patch(LIST_BUCKETS+(0x8ffefb28&3)*12,'<3I',0x8ffefb28,LIST_HEAD,0))
 chain=[LIST_HEAD]+[LIST_NODES+20*i for i in range(len(listeners))]
 for i,node in enumerate(chain):
  p.append(patch(node,'<5I',0x6478dc if not i else 0x6478d8,0xffffffff if not i else listeners[i-1],0,chain[(i+1)%len(chain)],chain[(i-1)%len(chain)]))
 return p
for fn,this in [(0x45fdf0,EVTABLE),(0x473690,SCRIPT0),(0x4607a0,BODIES)]:
 for events in [[],[0x123],[0x8ffefb28],[0x8ffefb28,0x123,0x8ffefb28],[0,0,0x8ffefb28]]:
  for listeners in [[],[SCRIPT0],[SCRIPT0,SCRIPT0+0x200,SCRIPT0]]:
   b=Build();p=event_patches(b,events,listeners)
   case([call(fn,this,[0x8ffefb28])]*2,b.patches()+p,label='event removal with duplicate listeners and owned nested parameters')
 for count in [0xffffffff,0x80000000]:
  b=Build();p=event_patches(b,count=count);case([call(fn,this,[0x8ffefb28])],b.patches()+p,label='signed event count')
for fn,this in [(0x473690,SCRIPT0),(0x4607a0,BODIES)]:
 b=Build();p=event_patches(b,table=False);case([call(fn,this,[0x8ffefb28])],b.patches()+p,label='missing event table')
case([call(0x4607a0,BODIES,[0x8ffefb28])],[patch(BODIES+0x10,'<I',0)],label='missing attached script')
b=Build();p=event_patches(b,events=(0,0,0x123));case([call(0x45fdf0,EVTABLE,[0])]*2,b.patches()+p,label='zero event removes disabled owned entries')

# A real cached QB script invokes the original native goal activation binding.
def transfer_program(b,callback=False):
 for i in range(8):
  b.goal(i,params=[(0,13,0x4599b58c)] if i==0 and isinstance(callback,tuple) else []);b.parent(i,0)
 b.queue([]);b.symbol(0x67f6e334,10,b.structure([]));b.symbol(0x20297d6f,1,4);b.symbol(0x2f507903,1,0)
 b.header(PROFILE+0x5c,b.structure([(0xac9b9eda,1,3)]))
 natives(b)
 code=b'\x01'+(command(0,fast=True)+b'\x01' if callback else b'')+b'\x24'
 b.symbol(0xc7ed5fef,7,CODE2)
 slot=CACHETABLE+32+(0xc7ed5fef&3)*12;previous=initial[slot-BASE:slot-BASE+12]
 b.extra += [raw(CODE2,code),patch(CODE2+0x100,'<5I',0xc7ed5fef,CODE2,1,0,0),raw(CODE2+0x140,previous),patch(slot,'<3I',0xc7ed5fef,CODE2+0x100,CODE2+0x140),patch(CACHETABLE+8,'<I',12)]
 if callback:fields.add(CODE2+2)

def apply(b=None,p=(),callback=False,changes=None,label='apply transfer',attached=False,before=()):
 b=b or config();transfer_program(b,callback)
 p=list(p);setup=body_setup()
 if attached:
  p=[raw(BODIES,body_base)]+event_patches(b,listeners=[SCRIPT0,SCRIPT0+0x200,SCRIPT0])+p
  setup=setup[1:]
 if isinstance(callback,tuple):
  p+=player_patches(1,0,1,1)+[patch(MOTION+16,'<I',SCORE_COMPONENTS),patch(DIAG+8,'<2I',*callback)]
  setup=ui_setup()+setup
 calls=setup+list(before)+[call(0x502f20,PHYS,[RESULT])]
 stages=case(calls,b.patches()+p,changes,label)
 stage=stages[-1]
 stage['float_fields']=[SKATER_STATE+0xe4+i*4 for i in range(4)]+[PHYS+off for off in range(0x3b0,0x4e0,4) if off!=0x484]
 stage['global_float_indices']=[index[0x7ccdbc+i*4] for i in range(4)]
 if isinstance(callback,tuple):assert oracle.word(DIAG)==1
 for s in stages:
  if s['fn']=='0x502240':assert s['result']==1,(label,s['result'])
 return stage
base_p=[patch(BODIES+0x4c,'<4f',0,100,0,1),patch(BODIES+0xac,'<4f',100,200,50,0),patch(RESULT,'<9fB',100,0,50,1,0,1,0,0,-20,1)]
for displacement in [(100,0,50),(-100,0,-50),(0,0,0),(100,200,50),(100,-1000,50)]:
 for normal in [[0,1,0,0],[.6,.8,0,0],[0,.1,-.995,0],[0,-1,0,0],[1,0,0,0]]:
  apply(p=base_p+[patch(RESULT,'<3f',*displacement),patch(RESULT+16,'<4f',*normal)],label='complete transfer distance and contact orientation')
for flags in [0,1,2,255]:
 p=base_p+[patch(SKATER_STATE+x,'<B',flags) for x in [0x30,0x38,0x68,0x78,0xa8,0xb0]]
 apply(p=p,changes={0x7d1ec8:0xffffffff,0x696d60:0x80000000},label='transfer flags and timer wrap')
for callback in [False,True]:
 apply(p=base_p,callback=callback,label='actual transfer script and native goal activation')

# Constructor-derived fixtures allow the real parent to remove an attached event.
case([call(0x460b80,BODIES)],label='capture original event-owner constructor')
body_base=bytes(oracle.cpu.mem_read(BODIES,0x4c))
for callback in [False,True,(PHYS+0x1528,SKATER_STATE2),(PHYS+12,BODIES+0x400)]:
 apply(p=base_p+[patch(BODIES+0x410,'<I',SCRIPT0)],attached=True,callback=callback,label='transfer parent cleans actual listeners after script callback')

# Feed complete search output directly into application on original training data.
prior_transfer=json.loads((out/'transfer-fixtures.json').read_text())
seen=set()
for previous,label in zip(prior_transfer['cases'],prior_transfer['case_labels']):
 if not label.startswith('training transfer '):continue
 stage=previous['steps'][-1];segment_id=label.split()[2]
 if not stage['result'] or segment_id in seen:continue
 seen.add(segment_id)
 p=[x for x in previous['patches'] if x[0] in [FROM,ORIGIN,VELOCITY,MOTION+0x48,MODE+0x1c,MOTION+0x18]]
 vectors=dict(p);p += [[BODIES+0x4c,vectors[FROM]],[BODIES+0xac,vectors[VELOCITY]]]
 apply(p=p,attached=True,before=[call(0x502240,PHYS,[1,FROM,ORIGIN,BODIES+0xac,RESULT,QUERY])],label='search then apply '+label)
for previous,label in zip(prior_transfer['cases'],prior_transfer['case_labels']):
 if label!='real moving training mesh and owner reference':continue
 stage=previous['steps'][-1];assert stage['result']==1
 old_config=config();skip={p[0] for p in old_config.patches()}
 p=[x for x in previous['patches'] if x[0] not in skip]
 vectors=dict(p);p += [[BODIES+0x4c,vectors[FROM]],[BODIES+0xac,vectors[VELOCITY]]]
 for at in [0x413000,0x40ae40]:functions[hex(at)]=prior_transfer['functions'][hex(at)]
 before=[call(int(s['fn'],16),s['this'],s['args']) for s in previous['steps'][:-1]]
 before.append(call(0x502240,PHYS,[1,FROM,ORIGIN,BODIES+0xac,RESULT,QUERY]))
 apply(p=p,attached=True,before=before,label='moving training mesh search then application')
 assert oracle.cpu.mem_read(PHYS+0x14c0,1)==b'\x01'
assert seen
assert branches['transfer_success']==9 and branches['player_score_reset']==2
for key in ['largest_x','largest_y','largest_z','negative_transfer_discriminant','flip_surface','matching_event_removed']:
 assert branches[key]>0,key

scope='Ten original routines: complete transfer application 502f20, six matrix inverse/rotation/interpolation routines and three event-removal parents. Includes nine complete training-mesh search/application sequences, one with a real moving mesh, actual QB/native goal activation, owned event/listener cleanup, and two diagnostic callbacks replacing body/state pointers. All game callees execute; heap initialization, diagnostic output, Windows TLS and lifted query state are existing platform boundaries. Generic event-owner construction supplies valid fixtures; skater construction is not recovered. SDK atan2 replaces FPATAN without a physical x87 accuracy claim. Arithmetic NaNs compare by classification only in typed output lanes; raw matrix copies remain exact. Required components/typed configuration, terminating QB graphs, valid event lists and successful allocations are contracts. Original training remains unplayable.'
fixture={'base':BASE,'memory':'transfer-apply-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'diagnostic_callbacks','pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'pointer_globals':[index[0x6918ec+4*i] for i in range(8)],'scoped_event_services':{'symbol':'thug_event_services','pointer':SERVICES},'native_callback':{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]}}
path=out/'transfer-apply-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
print('x86 complete:',len(labels),dict(oracle.counts),dict(branches),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_transfer_apply_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'branches':dict(branches),'heap_events':dict(oracle.heap_events),'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory']]},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
