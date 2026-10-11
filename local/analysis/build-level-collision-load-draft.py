import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
b=json.loads((p/'level-object-startup-draft.build.json').read_text())
for n,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/n)==h,n
old_load=r/'src/collision/load.c';new_load=p/'level-collision-load-load-derived.c';body=old_load.read_text();assert body.count('temp_scope(memory->context, 1)')==1;body=body.replace('#include "load.h"','#include "../../src/collision/load.h"').replace('#include "../core/number.h"','#include "../../src/core/number.h"').replace('temp_scope(memory->context, 1)','temp_scope(memory->context, 2)');new_load.write_text(body)
source=p/'level-collision-load-draft.c';output=p/'level-collision-load-draft.wasm';cmd=b['command'][:]
cmd[cmd.index(str(old_load))]=str(new_load);cmd.insert(cmd.index('-o'),str(source));cmd[cmd.index('-o')+1]=str(output)
subprocess.run(cmd,check=True)
drafts={**b['draft_source_hashes'],str(source.relative_to(r)):sha(source),str(new_load.relative_to(r)):sha(new_load)}
output.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(output),'draft_source_hashes':drafts,'derived_from':{**b['derived_from'],str(old_load.relative_to(r)):sha(old_load)}},indent=2)+'\n')
print(output.name,output.stat().st_size,sha(output))
