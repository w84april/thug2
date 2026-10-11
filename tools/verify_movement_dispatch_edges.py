"""Retained frames and native QB mutations in the original whole dispatcher."""
from pathlib import Path
dispatch_edge_source=Path('tools/verify_movement_dispatch.py').read_text()
dispatch_edge_prefix=dispatch_edge_source.split('for mode in [0,1,2,3,4,5,6,0xffffffff]:')[0].replace('movement-dispatch','movement-dispatch-edges')
exec(compile(dispatch_edge_prefix,'<complete movement runtime>','exec'))
dispatch_edge_config=config_entry
def config_entry(trigger=False):
 b=dispatch_edge_config(trigger);b.symbol(crc('projectile_control'),1,0x20689278)
 for name in [0xd7196d01,0x0ce5b783,0x3f356c63,0x266b570c]:
  code=b.alloc(b'\x01\x43'+struct.pack('<I',NATIVE)+b'\x01\x24');fields.add(code+2)
  entry=b.alloc(struct.pack('<5I',name,code,1,0,0));slot=CACHETABLE+32+(name&3)*12
  previous=next((bytes.fromhex(data) for at,data in reversed(b.extra) if at==slot),initial[slot-BASE:slot-BASE+12])
  link=b.alloc(previous);b.extra.append(patch(slot,'<3I',name,entry,link));b.symbol(name,7,code)
 return b
for target,value,width in [(PHYS+0x1528,SKATER_STATE2,4),(PHYS+0x4f0,255,1),(SKATER_STATE+0x18,1,4),(SKATER_STATE+0x30,1,1),(PHYS+0x14c1,0,1)]:
 frame(6,[patch(INPUT+0xe0,'<B3xI',1,0),patch(GOBS+4,'<4I',target,value,width,0xd7196d01)],label='focus QB mutation')
 assert path_results[-1]['qb_callbacks']>0
for target,value,width in [(PHYS+0x301,0,1),(GMODIFIER,bits(5),4),(GMODOWNER+0x18,0,4)]:
 frame(6,[patch(PHYS+0x301,'<B',1),patch(GMODIFIER,'<f',0),patch(GOBS+4,'<4I',target,value,width,0x266b570c)],label='special expiry QB mutation')
 assert path_results[-1]['qb_callbacks']>0
for mode in [0,1,4,6]:
 frame(mode,[patch(PHYS+0x2db,'<2B',1,1),patch(PHYS+0x2e0,'<f',0),patch(PHYS+0x2e8,'<f',1)],label='rotation completion and network flip')
for mode in [0,1]:
 history_patches=[[at+(TRICK-NAME_CONTEXT),data] for at,data in history()]
 frame(6,history_patches+[patch(MODE+0x1c,'<I',mode),patch(GOBS+4,'<4I',PHYS+0x2f8,0,4,0)],label='projectile input and QB mutation')
 assert path_results[-1]['qb_callbacks']>0
bind(0x402320,'thug_vector_copy',1,'word')
def compare(calls,p,changes=None,label='retained movement'):
 sequence=[call(0x40ab50,PHYS+0x4f4)]+[item for _ in range(8) for item in [call(0x402320,BODIES+0x5c,[BODIES+0x4c]),calls[-1]]]
 return dispatch_prior_compare(calls[:-1]+sequence,p,{**(changes or {}),**{index[k]:v for k,v in dispatch_changes.items()}},label)
for mode,scale in itertools.product(range(6),[.5,1.,2.]):
 frame(mode,label='eight consecutive frames',changes={0x684fc8:bits(scale)})
frame(4,[patch(RAILS+0x40,'<I',0),patch(GCONTEXT+0x18,'<I',0xa549b57b),patch(PHYS+0x2ec,'<B',1)],label='eight Natas dispatch frames')
dispatch_edge_source=Path('tools/verify_movement_dispatch.py').read_text()
tail=dispatch_edge_source[dispatch_edge_source.index("\nscope=")+1:].replace('movement-dispatch','movement-dispatch-edges').replace('movement_dispatch','movement_dispatch_edges')
exec(compile(tail,'<save movement edge observations>','exec'))
