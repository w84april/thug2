"""Original StartGap, concrete ownership and real secondary script dispatch."""
from pathlib import Path
exec(compile(Path('local/analysis/probe-gap-score.py').read_text().split('# Seeded missing output')[0],'<preserved score-history setup>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x401da0,37,'owned_string_destroy',0,'void',True,False,True),
 (0x401dd0,253,'owned_string_range',3,'void',True,False,True),(0x401ed0,51,'owned_string_assign',1,'word',True,False,True),
 (0x408fd0,91,'gap_array_free',1,'void',True,False,False),
 (0x578740,172,'gap_primary_node_construct',0,'word',True,False,True),
 (0x5787f0,79,'gap_secondary_node_construct',0,'word',False,False,True),
 (0x579570,130,'gap_primary_node_destroy',0,'void',True,False,True),
 (0x579630,91,'gap_secondary_node_destroy',0,'void',True,False,True),
 (0x579820,33,'gap_primary_node_delete',1,'word',True,False,True),
 (0x579600,33,'gap_secondary_node_delete',1,'word',True,False,True),
 (0x57a2f0,49,'gap_list_clear',0,'void',True,False,True),
 (0x512030,20,'skater_gap_clear',0,'void',True,False,True),
 (0x512050,225,'skater_gap_register_trick',2,'void',True,False,True),
 (0x512140,91,'skater_gap_check_tricks',1,'void',True,True,True),
 (0x512360,1035,'skater_gap_start',2,'void',True,False,True)]
for a,n,name,argc,result,heap,diag,this in specs:bind_new(a,n,'thug_'+name+'_draft',argc,result,heap,diag,this)
for a,name,argc,heap in [(0x401d80,'thug_skater_handle_construct_draft',0,False),(0x45e510,'thug_composite_initialize_draft',0,False),
 (0x512320,'thug_skater_gap_update_draft',0,True),(0x5121a0,'thug_skater_gap_clear_secondary_draft',1,True)]:bind(a,name,argc,'void',heap)
bind(0x512cc0,'thug_skater_gap_command_prefix_draft',3,'word')
bind(0x45d720,'thug_component_descriptor_base',3,'word')
command_hits=Counter();command_code=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(0x112cc0,356),0x512cc0))
oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:command_hits.update([at]),begin=0x512cc0,end=0x512e23)
exports += [[0x64ec80,'thug_gap_primary_node_methods_draft'],[0x64ec84,'thug_gap_secondary_node_methods_draft']]
for name,a,value,offset in [('thug_gap_array_pool_index_draft',0x6f22b4,0,0),('thug_gap_array_pools_draft',0x6f22bc,0,0),('thug_gap_array_pools_draft',0x6f22c0,0,4)]:
 assert a not in index;glob(name,a,value,offset=offset)
MODE=P+0xe000
if 0x7ce5d8 not in index:glob('thug_skater_orientation_context',0x7ce5d8,MODE)
else:defaults[index[0x7ce5d8]]=MODE
initial=bytes(memory);oracle.initial=initial
class StartGraph(HistoryGraph):
 def __init__(self,mode='direct'):
  super().__init__(mode);self.put(P+0x44,'<I',SCORE);self.put(MODE+0x40,'<I',0);self.put(SCRIPTS+0xb8,'<I',0x12345678)
  self.history([(CHECKS[0],1,180,0),(CHECKS[1],2,360,0),(CHECKS[0],1,180,0)])
  self.reference=self.alloc(0xb0);self.image[self.reference-BASE:self.reference-BASE+0xb0]=bytes(0xb0)
  self.put(self.reference+0x4c,'<4f',1.25,-2.5,3.75,1);self.put(self.reference+0x8c,'<4f',0,-0.0,1,.5)
  self.put(EM+8,'<I',self.table([(0x824c6a24,VO),(0x967c138c,self.reference),(0xe17b231a,self.reference)]))
 def run(self,calls,label,changes=None):
  try:result=case(calls,self.patches(),changes,label)
  except Exception:print('FAILED',label,flush=True);raise
  if len(labels)%50==0:print('Gap start cases',len(labels),flush=True)
  return result
 def pool(self,count=3):
  pool=self.alloc(0x5c);blocks=self.alloc(max(1,count)*16);self.image[pool-BASE:pool-BASE+0x5c]=bytes(0x5c)
  self.put(pool,'<6I',blocks,blocks+count*16,0,0,0,blocks if count else 0)
  for i in range(count):self.put(blocks+i*16,'<I',blocks+(i+1)*16 if i+1<count else 0)
  return pool,blocks
 def nodes(self,count,secondary=False,payload=False):
  sentinel=P+(0x2c if secondary else 0x18);nodes=[self.alloc(0x34 if secondary else 0x64) for _ in range(count)]
  self.put(sentinel+12,'<2I',nodes[0] if nodes else sentinel,nodes[-1] if nodes else sentinel)
  for i,node in enumerate(nodes):
   self.image[node-BASE:node-BASE+(0x34 if secondary else 0x64)]=bytes(0x34 if secondary else 0x64)
   self.put(node,'<5I',0x64ec84 if secondary else 0x64ec80,node,0,nodes[i+1] if i+1<count else sentinel,nodes[i-1] if i else sentinel);fields.add(node)
   if secondary:
    self.put(node+0x14,'<7I',i,self.text('old string') if payload else 0,20,KEY,0x12345678,5,0)
   else:self.put(node+0x14,'<3I',KEY,0,0x12345678);self.put(node+0x60,'<I',self.array(3,[self.text('one'),self.text('two')]) if payload else 0)
  return nodes
# Strings: null/empty, owned-buffer reuse/growth, serial wrap, poisoned fields,
# inclusive subranges and overlapping forward copies.
for fill,old,cap,text in itertools.product([0,0xa5],[False,True],[0,4,16],[None,'','A','gap name','x'*31]):
 g=StartGraph();p=g.alloc(16);g.image[p-BASE:p-BASE+16]=bytes([fill])*16
 buffer=g.alloc(64);g.image[buffer-BASE:buffer-BASE+64]=b'z'*63+b'\0';g.put(p+4,'<2I',buffer if old else 0,cap)
 incoming=0 if text is None else g.text(text)
 g.run([call(0x401ed0,p,[incoming]),call(0x401da0,p)],f'string assign/{fill}/{old}/{cap}/{text}',{0x690fa0:0})
for start,end in [(0,-1),(4,2),(-2,0),(0,0),(0,1),(1,3),(2,7),(5,5),(8,8)]:
 for reuse in [False,True]:
  g=StartGraph();p=g.alloc(12);buffer=g.alloc(48);g.image[buffer-BASE:buffer-BASE+48]=bytes(48);g.image[buffer-BASE:buffer-BASE+12]=b'abcdefghijk\0';g.put(p,'<3I',99,buffer if reuse else 0,48)
  g.run([call(0x401dd0,p,[buffer+2,start,end]),call(0x401da0,p)],f'string range/{start}/{end}/{reuse}',{0x690fa0:0xffffffff})
for selected,count in itertools.product([0,1],[0,1,3]):
 for fill in [0,0xa5,255]:
  g=StartGraph();p=g.alloc(0x68)+1;g.image[p-BASE:p-BASE+0x64]=bytes([fill])*0x64;fields.add(p);pool,blocks=g.pool(count)
  g.run([call(0x578740,p),call(0x579570,p)],f'primary constructor pool/{selected}/{count}/{fill}',{0x6f22b4:selected,0x6f22bc+4*selected:pool})
for secondary,fill,flags in itertools.product([False,True],[0,0xa5,255],[0,1,2,255,256,257,0xffffffff]):
 g=StartGraph();p=g.alloc(0x68)+1;g.image[p-BASE:p-BASE+0x64]=bytes([fill])*0x64;fields.add(p)
 g.run([call(0x5787f0 if secondary else 0x578740,p),call(0x579600 if secondary else 0x579820,p,[flags])],f'node constructor/delete/{secondary}/{fill}/{flags}',{0x690fa0:0xffffffff})
for selected,route in itertools.product([0,1],['none','selected','alternate','miss','both']):
 g=StartGraph();a,aa=g.pool(2);b,bb=g.pool(2);target=g.alloc(20);changes={0x6f22b4:selected}
 if route!='none':changes.update({0x6f22bc+4*selected:a,0x6f22bc+4*(selected^1):b})
 if route in ['selected','both']:target=aa+1
 if route=='alternate':target=bb
 if route=='both':g.put(b,'<2I',aa,aa+32)
 g.run([call(0x408fd0,args=[target])],f'array free route/{selected}/{route}',changes)
for primary,secondary,payload in itertools.product([0,1,3],[0,1,3],[False,True]):
 g=StartGraph();g.nodes(primary,payload=payload);g.nodes(secondary,True,payload)
 g.run([call(0x512030,P)]*2,f'clear concrete lists/{primary}/{secondary}/{payload}')
for text,owner,counter in itertools.product([None,'','Gap name'],[0,0x12345678,0xffffffff],[0,0xffffffff]):
 g=StartGraph();g.put(SCRIPTS+0xb8,'<I',owner);g.put(P+0x40,'<I',counter)
 params=g.structure([(0x3b442e26,13,KEY),(0xa26994e6,13,5)]+([] if text is None else [(0x3eafa520,3,g.text(text))]))
 g.run([call(0x512050,P,[params,SCRIPTS])]*2+[call(0x512030,P)],f'register secondary/{text}/{owner}/{counter}')
# Full StartGap. Tests explicitly provide the later-skater-setup Score+44 link.
for variant,mode in itertools.product(['plain','bound','named','array','none'],['direct','integer','missing']):
 for angle in [None,0,179,180,-180,0x7fffffff,0x80000000]:
  g=StartGraph(mode);items=[(0x3b442e26,13,KEY)]
  if variant!='plain':items.append((0xa26994e6,13,5))
  if variant=='bound':items.append((0x95e16467,13,KEY))
  if variant=='named':items.append((0x3eafa520,3,g.text('Kickflip')))
  if variant=='array':items.append((0x1e26fd3e,12,g.array(13,CHECKS)))
  if angle is not None:items.extend([(0xedf5db70,1,angle&0xffffffff),(0,13,0x1c39f1b9)])
  params=g.structure(items)
  g.run([call(0x512360,P,[params,SCRIPTS])]*2+[call(0x512030,P)],f'StartGap scoring/{variant}/{mode}/{angle}')
# Same-key replacement respects the script owner, including later duplicates.
for count,match in itertools.product([1,3,6],['all','none','mixed']):
 g=StartGraph();nodes=g.nodes(count,payload=True)
 for i,node in enumerate(nodes):
  g.put(node+0x14,'<I',KEY if match=='all' or (match=='mixed' and i%2) else OTHER)
  g.put(node+0x1c,'<I',0x12345678 if i%3 else 0)
 params=g.structure([(0x3b442e26,13,KEY)])
 g.run([call(0x512360,P,[params,SCRIPTS]),call(0x512030,P)],f'StartGap replacement/{count}/{match}')
for shape,flags,kind,mode in itertools.product(['absent','checksum','array empty','array'],[[],[0xc442e33d],[0xe3ed4ade]],['skate','walk','vehicle'],[0,0xd443a2bc]):
 g=StartGraph();g.mode(kind,1);g.put(MODE+0x40,'<I',mode);items=[(0x3b442e26,13,KEY),(0xa26994e6,13,5),(0x2760de9e,13,0x20002)]+[(0,13,f) for f in flags]
 g.symbol(0x83300000,1,0x202);g.symbol(0x83300001,1,0x804)
 if shape=='checksum':items.append((0xf4fabe45,13,0x83300000))
 if shape.startswith('array'):items.append((0xf4fabe45,12,g.array(13,[] if shape=='array empty' else [0x83300000,0x83300001])))
 params=g.structure(items)
 g.run([call(0x512360,P,[params,SCRIPTS]),call(0x512320,P),call(0x512030,P)],f'StartGap masks/{shape}/{flags}/{kind}/{mode}')
for flag in [1,255]:
 g=StartGraph();g.put(STATE+0x70,'<B',flag);g.run([call(0x512360,P,[0,0])],f'StartGap early gate/{flag}')
for words in [[0x80000000,0,1,0x80000001],[0x7f800000,0xff800000,0x7f7fffff,0xff7fffff],[0x7fc12345,0xffc54321,0x7f812345,0xff812345]]:
 g=StartGraph();g.put(g.reference+0x8c,'<4I',*words);g.put(g.reference+0x4c,'<4I',*words);params=g.structure([])
 g.run([call(0x512360,P,[params,SCRIPTS]),call(0x512030,P)],'StartGap vector raw/'+str(words))
# CheckGapTricks runs actual spawn/setup/owner references/bytecode execution.
for count,active in itertools.product([0,1,3],['none','all','mixed']):
 g=StartGraph();nodes=g.nodes(count,True,True)
 for i,node in enumerate(nodes):g.put(node+0x2c,'<B',255 if active=='all' or (active=='mixed' and i%2) else 0)
 g.put(CACHETABLE+8,'<I',1);g.put(CACHETABLE+32+12,'<3I',5,CACHE+128,0);g.put(CACHE+128,'<5I',5,CACHE+192,1,0,0)
 g.image[CACHE+192-BASE:CACHE+194-BASE]=b'\x01\x24'
 g.run([call(0x45e510,OBJ),call(0x512140,P,[0]),call(0x512030,P)],f'CheckGapTricks actual script/{count}/{active}')
# Direct and real component-descriptor dispatch into the four recovered routes.
# The two remaining routes are explicitly unavailable, not fabricated outcomes.
for code in [0x65b9ec39,0x0196772b,0x42f80e5e,0xfc4f2009,0,0xffffffff]:
 for through_descriptor in [False,True]:
  g=StartGraph();g.nodes(2,True,True);params=g.structure([(0x3b442e26,13,KEY),(0xa26994e6,13,5),(0x3eafa520,3,g.text('Kickflip'))])
  descriptor=g.alloc(16);g.put(descriptor,'<4I',code,0,0,0)
  entry=call(0x45d720,P,[descriptor,params,SCRIPTS]) if through_descriptor else call(0x512cc0,P,[code,params,SCRIPTS])
  g.run([entry,call(0x512030,P)],f'Gap command dispatch/{code:x}/{through_descriptor}')
scope='Fifteen complete routines recover full StartGap, secondary registration and CheckGapTricks, concrete primary/secondary nodes, owned strings, pool-aware array release and both-list clearing. Real profile/history queries, script array copy, camera-object lookup, state cancellation and terminating QB script spawn execute. Explicit initialized graphs supply the later skater Score link. Full arena/globals/heap/preserved registers compare. Script value copying retains its existing disabled-pool contract; concrete node array allocation/release also tests selected and alternate pools. Four recovered command routes are wired into the real component descriptor; EndGap and prefix-trigger routes explicitly trap, so the dispatcher is partial and is not counted. No playable training scene is claimed.'
saved=coverage.copy();coverage.clear();finish('gap-start',scope,{},extra);coverage.update(saved)
report=json.loads((folder/'gap-start-original.json').read_text());report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
report['partial_command_dispatch']={'covered':sum(bool(command_hits[i.address]) for i in command_code),'total':len(command_code),'missing':[hex(i.address) for i in command_code if not command_hits[i.address]],'incomplete_routes':['EndGap e5399fb2','prefix trigger 4562e4a6'],'counted_as_complete':False}
(folder/'gap-start-original.json').write_text(json.dumps(report,indent=2)+'\n')
(folder/'gap-start-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':'thug_'+name+'_draft'} for a,n,name,*_ in specs},indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k in ['cases','calls','instruction_coverage']}),flush=True)
