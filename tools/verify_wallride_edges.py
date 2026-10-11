"""Original wallride rail catches and callbacks from real prior contact."""
from pathlib import Path
wallride_source_text=Path('tools/verify_wallride_paths.py').read_text()
prefix=wallride_source_text.split('for dt in [')[0].replace('wallride-paths.json','wallride-edges.json')
prefix=prefix.replace("def wallride(extra=(),label='wallride'):","def wallride(extra=(),label='wallride',trigger=False):").replace('acquire(extra=p+list(extra),label=label)','acquire(extra=p+list(extra),label=label,trigger=trigger)')
exec(compile(prefix,'<wallride complete engine graph>','exec'))
# Approach a real flat training surface with the held grind input. Only the rail
# data is supplied, as in the existing rail-search oracle; collisions stay real.
data=bytes.fromhex(loader['queries'][46]['result']);point=list(struct.unpack_from('<4f',data,16));normal=list(struct.unpack_from('<4f',data))
for height in [0.,1.,4.,12.]:
 p=[patch(BODIES+0x4c,'<4f',*point),patch(BODIES+0x5c,'<4f',point[0]-20,point[1]+1,point[2],1),patch(PHYS+0x38c,'<4f',*normal),patch(INPUT+0x1a0,'<B',1)]
 for i in range(3):
  start=[point[0]-1,point[1]+height,point[2]+i*100-50,1];end=[start[0],start[1],start[2]+100,1]
  p += [patch(RAILS+i*0x54,'<12f',*(start+end+start))]
 wallride(p,label='landing rail capture height '+str(height),trigger=True)
 print('rail case',height,path_results[-1]['state'],path_results[-1]['qb_callbacks'],flush=True)
# Generate the saved probe by executing the original query, not by replacing a
# collision result. Register the real contacted object's name in a valid node
# table and supply a terminating QB trigger with the recorded native boundary.
bind(0x5003a0,'thug_skater_query_surface',2,'byte');bind(0x43a930,'thug_collision_probe_assign',1,'word')
ROOTS.add(0x5003a0)
query_instructions=list(md.disasm(pe.get_data(0x1003a0,320),0x5003a0))
for at in [0x5003a0]+[i.address for i in query_instructions if i.mnemonic=='ret']:
 oracle.cpu.hook_add(UC_HOOK_CODE,floor_observe,begin=at,end=at)
prior_compare=compare
capture_previous=False
def compare(calls,p,changes=None,label='wallride edge'):
 if capture_previous:calls=calls[:-1]+[call(0x5003a0,PHYS,[0,0,QUERY]),call(0x43a930,PHYS+0x158,[PHYS+0xa8])]+calls[-1:]
 return prior_compare(calls,p,changes,label)
prior_config=config_entry
prior_query=loader['queries'][34];prior_name=struct.unpack_from('<I',bytes.fromhex(prior_query['result']),52)[0]
def config_entry(trigger=False):
 b=prior_config(trigger)
 if capture_previous:
  names=[0x1800,0x1801,0x1802,prior_name]
  entries=[b.structure([(0xa1dc81f9,13,n),(0x2ca8a299,13,0xa7662059)]) for n in names]
  b.extra.append(patch(NODE_TABLE+0x1000c,'<I',b.array(10,entries)))
  b.extra += [patch(NODE_TABLE+(n&0x3fff)*4,'<Hh',0,i) for i,n in enumerate(names)]
 return b
capture_previous=True
for target,value,width in [(0,0,0),(GATE+0x26,1,1),(PHYS+0x1528,SKATER_STATE2,4),(PHYS+0x1514,SOUND2,4),(PHYS+0x38c,bits(1),4)]:
 p=[raw(PHYS+0x208,bytes.fromhex(prior_query['segment'])),patch(GOBS+4,'<4I',target,value,width,0xa7662059)]
 wallride(p,label='real prior-contact QB callback mutates '+hex(target))
 assert path_results[-1]['qb_callbacks']>0,path_results[-1]
 print('event case',hex(target),path_results[-1]['state'],path_results[-1]['qb_callbacks'],flush=True)
tail=wallride_source_text[wallride_source_text.index("\nscope=")+1:].replace('wallride-paths','wallride-edges').replace('wallride_paths','wallride_edges')
exec(compile(tail,'<save original wallride edge observations>','exec'))
