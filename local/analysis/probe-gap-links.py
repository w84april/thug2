"""Compare linked-node command and genuine EndGap/score dependencies."""
from pathlib import Path
exec(compile(Path('local/analysis/probe-gap-start.py').read_text().split('# Strings:')[0],'<preserved gap creation setup>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear();command_hits.clear()
specs=[(0x45c3a0,60,'node_named_link_count',1,'word',False,False,False),
 (0x45c460,75,'node_link_at',2,'word',False,False,False),
 (0x45c4b0,107,'node_links_to',2,'byte',False,False,False),
 (0x45c520,51,'node_names_linked',2,'byte',False,False,False),
 (0x5612a0,47,'score_escape_spaces',2,'void',False,False,False),
 (0x5614d0,123,'score_entries_append',1,'void',True,False,True),
 (0x5628b0,107,'score_map_append',2,'byte',True,False,True),
 (0x561550,230,'score_range_value',2,'word',False,False,True),
 (0x51c9d0,38,'timed_tricks_record_name',3,'void',False,False,True),
 (0x5638a0,234,'score_notify_trick',1,'void',True,True,True),
 (0x584110,25,'level_gap_state',1,'word',False,False,True),
 (0x5656c0,11,'game_gap_state',0,'word',False,False,True),
 (0x578bc0,176,'gap_history_record',9,'void',False,False,True),
 (0x578c70,123,'gap_history_increment',1,'void',False,False,True),
 (0x578670,5,'gap_secondary_mark',0,'void',False,False,True),
 (0x49f4c0,5,'gap_array_score_count',2,'word',False,False,True)]
for a,n,name,argc,result,heap,diag,this in specs:bind_new(a,n,'thug_'+name+'_draft',argc,result,heap,diag,this)
functions['0x5612a0']['cleanup']=8
for a,name,argc,result,heap in [(0x45e510,'thug_composite_initialize_draft',0,'void',False),
 (0x512cc0,'thug_skater_gap_command_prefix_draft',3,'word',False),(0x45d720,'thug_component_descriptor_base',3,'word',False),
 (0x561430,'thug_objective_find',1,'word',False)]:bind(a,name,argc,result,heap)
class LinksGraph(StartGraph):
 def run(self,calls,label,changes=None):
  try:result=case(calls,self.patches(),changes,label)
  except Exception:print('FAILED',label,flush=True);raise
  if len(labels)%50==0:print('Gap links cases',len(labels),flush=True)
  return result
 def level_nodes(self,rows):
  nodes=[self.structure([(0xa1dc81f9,13,name),*items]) for name,items in rows]
  self.put(NODETABLE+0x10004,'<3I',0,0,self.array(10,nodes))
  for i,(name,_) in enumerate(rows):
   slot=name&0x3fff
   while self.word(NODETABLE+slot*4)>>16!=0xffff:slot=(slot+1)&0x3fff
   self.put(NODETABLE+slot*4,'<HH',0,i)
  return nodes

# Resolve Links through collision/wrap slots and included QB structures.
for names in [[KEY,OTHER,0x23456789],[0x3fff,0x7fff,0xbfff],[0xffffffff,0,0x4000]]:
 for shape in ['absent','empty','single','duplicate','multiple','missing target','included','negative count']:
  g=LinksGraph();values=[] if shape in ['absent','empty','negative count'] else [names[1]] if shape=='single' else [names[1],names[1]] if shape=='duplicate' else [names[2],names[1],0x11112222]
  a=g.array(13,values)
  if shape=='negative count':g.put(a+4,'<I',0xffffffff)
  items=[] if shape=='absent' else [(0x2e7d5ee7,12,a)]
  if shape=='included':g.symbol(0x86667777,10,g.structure(items));items=[(0,13,0x86667777)]
  nodes=g.level_nodes([(names[0],items),*[(name,[]) for name in names[1:]]])
  calls=[call(0x45c3a0,args=[names[0]])]
  for target in [*nodes,0]:calls.append(call(0x45c4b0,args=[nodes[0],target]))
  calls += [call(0x45c520,args=[names[0],name]) for name in [*names,0x11112222]]
  calls += [call(0x45c460,args=[names[0],i]) for i in range(len(values))]
  g.run(calls,f'node Links/{names}/{shape}')
# Link dispatch runs actual owner/script setup and bytecode, both directly and
# through the existing component descriptor. Earlier routes run in regression.
for route in ['zero owner','no Links','empty','negative count','no scripts','first','last','duplicates','included script']:
 for descriptor in [False,True]:
  g=LinksGraph();a=g.array(13,[0x30000001,0x30000002,0x30000003]);items=[(0x2e7d5ee7,12,a)]
  if route=='no Links':items=[]
  if route in ['empty','negative count']:g.put(a+4,'<I',0 if route=='empty' else 0xffffffff)
  rows=[(KEY,items)]
  for i in range(3):
   use=(route in ['first','duplicates','included script'] and i==0) or (route in ['last','duplicates'] and i==2)
   sub=[(0x2ca8a299,13,5)] if use else []
   if use and route=='included script':g.symbol(0x85555555,10,g.structure(sub));sub=[(0,13,0x85555555)]
   rows.append((0x30000001+i,sub))
  g.level_nodes(rows);g.put(SCRIPTS+0xb8,'<I',0 if route=='zero owner' else KEY)
  # Preserve the known cache table layout for key five from gap-start.
  g.put(CACHETABLE+8,'<I',1);g.put(CACHETABLE+32+12,'<3I',5,CACHE+128,0);g.put(CACHE+128,'<5I',5,CACHE+192,1,0,0)
  g.image[CACHE+192-BASE:CACHE+194-BASE]=b'\x01\x24'
  d=g.alloc(16);g.put(d,'<4I',0x4562e4a6,0,0,0)
  entry=call(0x45d720,P,[d,0,SCRIPTS]) if descriptor else call(0x512cc0,P,[0x4562e4a6,0,SCRIPTS])
  g.run([call(0x45e510,OBJ),entry],f'linked script dispatch/{route}/{descriptor}')

for text in ['', ' ', 'a', 'ab', 'a b  c', '\\_ space', 'tab\tline\n', 'a'*63]:
 for offset in [0,1,3]:
  g=LinksGraph();out=g.alloc(256)+offset;source=g.text(text);g.run([call(0x5612a0,args=[out,source])],f'escape/{text!r}/{offset}')
for text in ['abc','abcdef','a b','ab  cd']:
 g=LinksGraph();out=g.alloc(128);source=out+16;g.image[source-BASE:source-BASE+len(text)+1]=text.encode()+b'\0'
 g.run([call(0x5612a0,args=[out,source])],f'escape overlap/{text}')
for capacity,count,growth in [(0,0,1),(0,0,8),(1,0,0),(1,1,1),(3,2,0),(3,3,1),(4,4,4),(8,3,0)]:
 for null_old in ([True,False] if capacity==0 else [False]):
  g=LinksGraph();p=g.alloc(16);old=0 if null_old else g.alloc(max(capacity*4,4))
  if old:
   for i in range(capacity):g.put(old+i*4,'<I',0x76543210+i)
  g.put(p,'<4I',old,capacity,count,growth)
  g.run([call(0x5614d0,p,[0]),call(0x5614d0,p,[p])] if growth else [call(0x5614d0,p,[p])],f'append array/{capacity}/{count}/{growth}/{null_old}')
for count in [0,1,3]:
 for alias in ['separate','count','new value']:
  g=LinksGraph();p=g.alloc(20);g.put(p,'<5I',0,0,0,0x12345678,0xffffffff);key=g.alloc(4);g.put(key,'<I',KEY)
  calls=[call(0x5628b0,p,[key,0x81100000+i]) for i in range(count)]
  incoming=p if alias=='count' else HEAP+count*16+4 if alias=='new value' else key
  calls += [call(0x5628b0,p,[incoming,0x92345678]),call(0x561430,p,[incoming])]
  g.run(calls,f'append score map/{count}/{alias}')

rng=random.Random(0x561550)
for number in range(180):
 g=LinksGraph();length=rng.randrange(1,18);entries=[]
 for i in range(length):
  p=g.alloc(0x9c);g.put(p,'<7I',rng.choice([0,1,99,200,0x7fffffff,0x80000000,0xffffffff,rng.getrandbits(32)]),rng.randrange(9),rng.randrange(10),0,0,rng.choice([0,1,4,0xffffffff]),rng.choice([0,2,0x100,0x102]));entries.append(p)
 items=g.alloc(length*4);g.put(items,'<'+'I'*length,*entries);g.put(SCORE+0x4c,'<I',items)
 start=rng.randrange(length+1);end=rng.randrange(start,length+1)
 g.run([call(0x561550,SCORE,[start,end]),call(0x561550,SCORE,[0,length])],f'range score/{number}/{start}/{end}')
for available,career,enabled,excluded,profile in [(0,1,1,False,0x0a7be964),(1,0,1,False,0x0a7be964),(1,1,0,False,0x0a7be964),(1,1,1,True,0x0a7be964),(1,1,1,False,0),(1,1,1,False,0x0a7be964)]:
 for equal in [False,True]:
  g=LinksGraph();p=g.alloc(0xa94);g.image[p-BASE:p-BASE+0xa94]=bytes(0xa94);g.put(p+0xa90,'<I',available);g.put(p+0x9f4,'<B',enabled);g.put(p+0xa14,'<I',123)
  settings=g.structure([(0x1ded1ea4,1,career)]);g.put(SETTINGS+4,'<2I',0,g.word(settings+4))
  params=g.structure([(0xa1dc81f9,13,profile)]);g.put(PROFILE+0x5c,'<2I',0,g.word(params+4));g.put(GAME+0x378,'<I',0xe92ecafe if excluded else 0)
  g.run([call(0x51c9d0,p,[g.text('Kickflip'),123 if equal else 456,0xffffffff])],f'timed name gate/{available}/{career}/{enabled}/{excluded}/{profile}/{equal}')

for level in [0,1,7,0xffffffff]:
 g=LinksGraph();p=g.alloc(0x680);game=g.alloc(0x24);g.put(game+0x20,'<I',p);g.put(p+0x630,'<I',7)
 for i in range(8):g.put(p+0x63c+4*i,'<I',g.alloc(8))
 g.run([call(0x584110,p,[level]),call(0x5656c0,game)],f'gap level lookup/{level}')
for names in [[],[''],['a'],['a','ab','abc'],['same','same','other'],['first','middle','last']]:
 for target in ['', 'a','ab','abc','same','middle','last','missing','\xff']:
  g=LinksGraph();p=g.alloc(0x20);sentinel=g.alloc(0x50);g.put(sentinel+4,'<I',0xffffffff);nodes=[g.alloc(0x50) for _ in names];g.put(p+0x10,'<I',nodes[0] if nodes else sentinel)
  for i,node in enumerate(nodes):
   g.put(node+4,'<I',i);g.put(node+12,'<I',nodes[i+1] if i+1<len(nodes) else sentinel);g.put(node+0x48,'<I',g.text(names[i]));g.put(node+0x34,'<I',0xffffffff)
  name=g.text(target);args=[name,0,1,0x7fffffff,0x80000000,0xffffffff,p,name,0xdeadbeef]
  g.run([call(0x578bc0,p,args),call(0x578c70,p,[name])]*2,f'gap history/{names}/{target}')
for fill,offset in itertools.product([0,0xa5,255],[0,1,3]):
 g=LinksGraph();p=g.alloc(64)+offset;g.image[p-BASE:p-BASE+52]=bytes([fill])*52
 g.run([call(0x578670,p)]*2+[call(0x49f4c0,p,[0,0xffffffff])],f'mark secondary/{fill}/{offset}')

# The UI notification exercises owned parameters and the real terminating QB VM.
# Its cache structure uses the same manager convention as the earlier fixtures.
for screen,pooled,script in itertools.product([0,1,0xffffffff],[False,True],[False,True]):
 g=LinksGraph();changes={}
 if pooled:
  pool,blocks=g.pool(10);changes={0x6f3614:0,0x6f361c:pool}
 if script:
  name=0x3bd51fe5;g.symbol(name,7,0)
  g.put(CACHETABLE+8,'<I',1);g.put(CACHETABLE+32+(name&3)*12,'<3I',name,CACHE+128,0);g.put(CACHE+128,'<5I',name,CACHE+192,1,0,0)
  g.image[CACHE+192-BASE:CACHE+194-BASE]=b'\x01\x24'
 g.run([call(0x5638a0,0,[screen])],f'score UI notify/{screen}/{pooled}/{script}',changes)

scope='Sixteen complete original routines recover level Links lookup/predicate, score-history storage and range arithmetic, timed-trick name recording, synchronous score UI script notification, level-specific gap state and named gap-history writes. The fifth Gap command follows Links and runs the first linked script through actual owner/setup/QB execution; direct and component-descriptor paths compare. Full arena/globals/heap and preserved registers compare, with no numeric masks. EndGap, full score insertion, remaining skater startup and playable training are still unfinished; the dispatcher is partial and not counted complete.'
saved=coverage.copy();coverage.clear();finish('gap-links',scope,{},extra);coverage.update(saved)
report=json.loads((folder/'gap-links-original.json').read_text());report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
report['partial_command_dispatch']={'covered':sum(bool(command_hits[i.address]) for i in command_code),'total':len(command_code),'missing':[hex(i.address) for i in command_code if not command_hits[i.address]],'incomplete_routes':['EndGap e5399fb2'],'counted_as_complete':False}
(folder/'gap-links-original.json').write_text(json.dumps(report,indent=2)+'\n')
(folder/'gap-links-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':'thug_'+name+'_draft'} for a,n,name,*_ in specs},indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k in ['cases','calls','instruction_coverage']}),flush=True)
