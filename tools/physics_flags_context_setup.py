"""Actual named QB dispatch through the complete physics descriptor table."""
from pathlib import Path
table_probe_source=Path('tools/verify_physics_registration_table.py').read_text()
exec(compile(table_probe_source[:table_probe_source.index('loop=registration_context_source')],'<verified physics table and runtime setup>','exec'))
import re
members={int(address,16):'thug_physics_'+args.split(',')[0].strip()+'_member'
 for address,kind,args in re.findall(r'/\* ([0-9a-f]{8}) \*/ (MEMBER|SET|GET|STATE)\(([^)]*)\)',(ROOT/'src/game/physics_flags.c').read_text())}
assert len(members)==58
function_exports += [[address,name] for address,name in members.items()]
member_hits=Counter()
def member_observe(cpu,at,size,user):member_hits[at]+=1
for address in members:oracle.cpu.hook_add(UC_HOOK_CODE,member_observe,begin=address,end=address)
selected=[row for row in table_metadata['entries'] if int(row['member'],16) in members]
assert len(selected)==58
game=oracle.defaults[next(i for i,entry in enumerate(globals_) if entry[0]=='thug_game_context')]
assert BASE<=game and game+0x400<BASE+len(initial)
# for entry,reverse,seed in (context cases are defined by the caller)
