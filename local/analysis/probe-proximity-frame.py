"""Original player-distance queries and complete proximity event update."""
from pathlib import Path
exec(compile(Path('local/analysis/probe-prop-lifecycle.py').read_text().split('# Constructor/reset fields')[0],'<preserved prop services>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
for a,n,name,argc,result,heap,diag in [(0x55d990,47,'proximity_list_at',1,'word',False,False),
 (0x5665c0,64,'proximity_skater_at',1,'word',False,False),(0x4ec3c0,90,'proximity_local_distance',1,'double',False,False),
 (0x4ec4b0,170,'proximity_nearest_distance',1,'double',False,False),(0x4ec560,1024,'proximity_update',0,'void',True,True)]:
 bind_new(a,n,'thug_'+name+'_draft',argc,result,heap,diag)
bind(0x461a00,'thug_object_manager_add',1,heap=True)
bind(0x4738e0,'thug_script_initialize',0,'word')
bind(0x4747a0,'thug_script_setup_named',3,heap=True,diag=True)
bind(0x4734e0,'thug_script_set_events_draft',2)
fields.add(SCRIPTS+0xec)
for name,a,off in [('thug_script_structure_pool_index',0x6f3614,0),('thug_script_structure_pools',0x6f361c,0),('thug_script_structure_pools',0x6f3620,4)]:
 if a not in index:glob(name,a,0,offset=off)
initial=bytes(memory);oracle.initial=initial
OUT=P+0x100
class ProximityGraph(PropGraph):
 def __init__(self):
  super().__init__();self.image[P-BASE:P-BASE+0x30]=bytes(0x30);self.put(P+12,'<I',OBJ)
  self.put(OBJ,'<I',0x647650);fields.add(OBJ);self.put(OBJ+0x100,'<I',0)
  self.put(OBJ+0x4c,'<4f',0,0,0,1);self.put(OUT,'<I',0xdeadbeef)
  self.players([])
 def players(self,specs):
  bodies=[];nodes=[]
  for key,position,local in specs:
   if key=='owner':body=OBJ
   elif key is None:body=0
   else:
    body=self.alloc(0x140);self.image[body-BASE:body-BASE+0x140]=bytes(0x140)
    self.put(body+0x14,'<I',key);self.put(body+0x4c,'<4f',*position,1)
   if body:self.put(body+0xbc,'<B',local)
   bodies.append(body);nodes.append(self.alloc(16))
  end=self.alloc(16);self.put(end,'<4I',0,0xffffffff,0,end)
  for i,(node,body) in enumerate(zip(nodes,bodies)):self.put(node,'<4I',0,body,0,nodes[i+1] if i+1<len(nodes) else end)
  self.put(GAME+0x34,'<I',nodes[0] if nodes else end);return bodies,nodes,end
 def pool(self,count=128):
  pool=self.alloc(92);data=self.alloc(count*8);self.put(pool,'<6I',data,data+count*8,0,0,0,data);self.put(pool+88,'<I',0)
  for i in range(count):self.put(data+8*i,'<I',data+8*(i+1) if i+1<count else 0)
  return pool
 def update(self,count=2):return [call(0x461a00,MANAGER,[OBJ])]+[call(0x4ec560,P)]*count
def run_proximity(g,calls,label,changes=None):
 try:result=case(calls,g.patches(),changes,label)
 except Exception:print('FAILED',label,flush=True);raise
 if len(labels)%25==0:print('Original proximity cases',len(labels),flush=True)
 return result
for count in [0,1,4]:
 for index_ in [0,1,3,4,0x7fffffff,0xffffffff]:
  g=ProximityGraph();g.players([(100+i,(i,2*i,3*i),0) for i in range(count)])
  run_proximity(g,[call(0x55d990,GAME+0x28,[index_]),call(0x5665c0,GAME,[index_])],f'indexed-player/{count}/{index_}')
layouts=[[],[('owner',(0,0,0),1)],[(1,(2,3,4),0)],[(1,(2,3,4),1)],
 [(1,(2,3,4),1),(2,(-2,-3,-4),1)],[(1,(20,30,40),1),(2,(2,3,4),0)],
 [(1,(2,3,4),0),(2,(1,1,1),1)],[(1,(2,3,4),0),('owner',(0,0,0),1)],
 [(1,(0,0,0),1),(2,(0,0,0),0)],[(1,(1e30,-1e30,1e30),1)],
 [(1,(.125,-.3,1.01),1),(2,(.25,-.1,1),0)]]
for i,specs in enumerate(layouts):
 g=ProximityGraph();bodies,_,_=g.players(specs)
 run_proximity(g,[call(0x4ec3c0,P,[OUT]),call(0x4ec4b0,P,[OUT])]*2,f'distance-layout/{i}')
 for target in [OBJ+0x4c]+([bodies[0]+0x4c] if bodies and bodies[0] else []):
  if i not in [0,1,9]:
   g=ProximityGraph();bodies,_,_=g.players(specs)
   run_proximity(g,[call(0x4ec3c0,P,[target]),call(0x4ec4b0,P,[target])],f'distance-output-alias/{i}/{target}')
# Nearest-distance explicitly skips null bodies; local lookup requires nonnull.
g=ProximityGraph();g.players([(None,(0,0,0),0),(1,(1,2,3),0)])
run_proximity(g,[call(0x4ec4b0,P,[OUT])],'nearest null body')
# Every threshold subset, inside/equal/outside comparisons and disabled owners.
for mask in range(32):
 for threshold in [4.,25.]:
  for flag in [0,1]:
   g=ProximityGraph();g.players([(1,(3,0,0),1),(2,(1,0,0),0)]);g.put(OBJ+8,'<I',flag)
   g.put(P+0x18,'<5f',*[threshold if mask&(1<<i) else 0 for i in range(5)])
   run_proximity(g,g.update(),f'threshold-subset/{mask}/{threshold}/{flag}')
for position in [(0,0,0),(1,0,0),(2,0,0),(-2,0,0),(3,4,0)]:
 for threshold in [-1.,1.,4.,25.]:
  g=ProximityGraph();g.players([(7,position,1)]);g.put(P+0x18,'<5f',*([threshold]*5))
  run_proximity(g,g.update(),f'equality-zero-negative/{position}/{threshold}')
for selected in [0,1]:
 for threshold in [1.,25.]:
  g=ProximityGraph();g.players([(1,(3,0,0),1),(2,(1,0,0),0)]);g.put(P+0x18,'<5f',*([threshold]*5));pool=g.pool()
  run_proximity(g,g.update(3),f'structure-pool/{selected}/{threshold}',{0x6f3614:selected,0x6f361c+4*selected:pool})
# Absent players retain their helper output; only parameter-free update branches
# are valid when no helper has produced a player ID.
for flag in [0,1]:
 g=ProximityGraph();g.put(OBJ+8,'<I',flag);g.put(P+0x24,'<2f',1,1)
 run_proximity(g,g.update(),f'absent-player-parameter-free/{flag}')
# Real cached QB handles the event and invokes the original deferred-delete
# member. Subsequent proximity branches must observe the now-disabled owner.
for event in [0x7048029a,0xd69bd3de]:
 g=ProximityGraph();g.players([(1,(1,0,0),1)]);g.put(P+0x18,'<5f',25 if event==0x7048029a else 0,0,25,1,25)
 idle,handler=0x71230001,0x71230002;entries=[]
 for key,body in [(idle,b'\x01\x24'),(handler,b'\x01\x44'+struct.pack('<I',0xc6870028)+b'\x01\x24')]:
  program=g.alloc(len(body));g.image[program-BASE:program-BASE+len(body)]=body
  entry=g.alloc(20);g.put(entry,'<5I',key,program,0,0,0);entries.append((key,entry))
 g.put(CACHE+20,'<I',g.table(entries));g.put(OBJ+0x10,'<I',SCRIPTS)
 array=g.array(10,[g.structure([(0,13,event),(0,13,handler)])])
 calls=[call(0x461a00,MANAGER,[OBJ]),call(0x4738e0,SCRIPTS),call(0x4747a0,SCRIPTS,[idle,0,OBJ]),call(0x4734e0,SCRIPTS,[array,1]),call(0x4ec560,P)]
 run_proximity(g,calls,f'actual-QB-deferred-delete/{event:x}')
 assert oracle.word(OBJ+8)&1 and oracle.word(OBJ+12)==0
missing={hex(a):[hex(i.address) for i in code if not hits[i.address]] for a,code in coverage.items()};print('MISSING',json.dumps(missing),flush=True)
excluded={**{hex(a):'initialized allocator bypasses process bootstrap' for a in [0x4ec5de,0x4ec823]},
 **{hex(a):'successful allocation contract; failed allocation cannot satisfy subsequent parameter setters' for a in [0x4ec6a8,0x4ec771,0x4ec854]}}
scope='Five complete control flows: sentinel indexed node/player lookup, local and nearest squared player distance, and Proximity component events. Original event delivery, heap/selected structure pools, parameter ownership and object registration execute. Valid nonnull sentinel lists; local lookup requires nonnull bodies; parameter-bearing events require a distance helper to supply an ID, avoiding original uninitialized-ID stack reads. Finite coordinate/threshold corpus, exact PC24 arithmetic and stores; no numerical masks. Full arena, globals, returns, preserved registers and heap effects compare. No full frame or playability claimed.'
finish('proximity-frame',scope,excluded,extra)
