"""Discovery only: observe the original Walk speed parent and concrete checksum route.

This does not award a recovered routine or replace a virtual game method.
"""
from pathlib import Path
exec(compile(Path('local/analysis/probe-walk-speed.py').read_text().split('for count,direction')[0],'<speed graph>','exec'))
case=speed_base_case
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
bind_new(0x52a2c0,760,'unrecovered_walk_animation_speed',0,'void',True,True,True)
oracle.cpu.hook_add(UC_HOOK_CODE,observe_cache,begin=0x52a2c0,end=0x52a2c0)
commands=[];speed_calls=[];records=[]
def dispatch(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP)
 if at==0x419950:
  params=oracle.word(sp+8);node=oracle.word(params+4)
  commands.append({'method':hex(at),'caller_return':hex(oracle.word(sp)),'command':hex(oracle.word(sp+4)),'script':oracle.word(sp+12),'parameter_name':hex(oracle.word(node+4)),'parameter_bits':oracle.word(node+8)})
  assert oracle.word(sp+4)==0xbd4edd44 and oracle.word(sp+12)==0
 elif at==0x419967:
  assert cpu.reg_read(UC_X86_REG_EAX)==2;commands[-1]['return']=2
 else:
  assert at==0x419b90;speed_calls.append({'speed_bits':oracle.word(sp+4),'send':oracle.word(sp+8),'all':oracle.word(sp+12),'relative':oracle.word(sp+16)})
for at in [0x419950,0x419967,0x419b90]:oracle.cpu.hook_add(UC_HOOK_CODE,dispatch,begin=at,end=at)
for mode,control,network,speed,previous in itertools.product([0,1,2,3,4],[0,1],[0,1],[0,2,30],[0,1]):
 g=SpeedGraph();g.parameters(overrides={**required_parameters,0x1a47ffab:2,0x0ab2db54:4})
 g.put(AP,'<I',0x645d8c);g.put(P+0x700,'<If',mode,speed);g.put(P+0x17b0,'<f',2);g.put(P+0x18e0,'<f',previous);g.put(CONTROL+0x24,'<B',control)
 # The original activity query reads its real connection flag; speed messages
 # stay blocked in AS so this discovery does not add another queue fixture.
 g.put(NET,'<3I',4 if network else 0,CLIENT,0);g.put(CLIENT+0x1e84,'<I',0)
 commands.clear();speed_calls.clear();g.run([call(0x52a2c0,P)],f'walk speed parent/{mode}/{control}/{network}/{speed}/{previous}',{0x7cce14:NET})
 assert len(commands)==int(mode in [2,3] or (mode==1 and control))
 assert all(x['return']==2 for x in commands)
 assert len(speed_calls)==int(mode in [1,2,3])
 records.append({'mode':mode,'control':control,'network':network,'speed':speed,'previous':previous,'commands':list(commands),'speed_calls':list(speed_calls),'channel_speed_bits':oracle.word(CHANNELS+0x20),'retained_network_speed_bits':oracle.word(P+0x18e0)})
report={'result':'original discovery only; no recovered routine claimed','specimen_sha256':SHA256,'cases':len(records),'component_vtable':'0x645d8c','checksum_slot':'0x30','checksum_entry':'0x419950','unhandled_return':2,'records':records,
 'instruction_coverage':{hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()},
 'next':'Recover52a2c0 and the actual checksum dispatch419950/forwarder4198d0. This parent uses bd4edd44, which419950 returns2 for. Do not substitute controller-level command forwarding.'}
(folder/'walk-speed-parent-discovery.json').write_text(json.dumps(report,indent=2)+'\n');print('DISCOVERED',len(records),'original parent cases; commands returned2')
