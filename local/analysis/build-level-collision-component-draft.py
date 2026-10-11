import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
b=json.loads((p/'level-collision-load-draft.build.json').read_text())
for n,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/n)==h,n
source=p/'level-collision-component-draft.c';output=p/'level-collision-component-draft.wasm';cmd=b['command'][:]
old=r/'src/collision/moving.c';new=p/'level-collision-component-moving-derived.c';body=old.read_text();body=body.replace('#include "moving.h"','#include "../../src/collision/moving.h"').replace('#include "../core/', '#include "../../src/core/');body=body.replace('const ThugCollisionMethods thug_moving_collision_methods = {','void thug_moving_collision_orientation_set_bridge_draft(void *,const float *);\nconst ThugCollisionMethods thug_moving_collision_methods = {\n    .unknown_14_to_24={(uintptr_t)thug_moving_collision_set_position,(uintptr_t)thug_moving_collision_orientation_set_bridge_draft},\n    .unknown_2c_to_30={(uintptr_t)thug_moving_collision_set_owner},');new.write_text(body)
cmd[cmd.index(str(old))]=str(new);cmd.insert(cmd.index('-o'),str(source));cmd[cmd.index('-o')+1]=str(output);subprocess.run(cmd,check=True)
drafts={**b['draft_source_hashes'],str(source.relative_to(r)):sha(source),str(new.relative_to(r)):sha(new)}
output.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(output),'draft_source_hashes':drafts,'derived_from':{**b['derived_from'],str(old.relative_to(r)):sha(old)}},indent=2)+'\n');print(output.name,output.stat().st_size,sha(output))
