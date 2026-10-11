import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
b=json.loads((p/'input-callbacks-draft.build.json').read_text())
for n,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/n)==h,n
old=p/'level-collision-component-draft.c';derived=p/'input-lifecycle-level-collision-derived.c'
needle='const uintptr_t thug_task_base_methods_draft[3]={0},thug_task_node_methods_draft[1]={0};'
s=old.read_text();assert s.count(needle)==1
derived.write_text(s.replace(needle,'extern const uintptr_t thug_task_base_methods_draft[3],thug_task_node_methods_draft[1];'))
source=p/'input-lifecycle-draft.c';output=p/'input-lifecycle-draft.wasm';cmd=b['command'][:]
assert str(old) in cmd;cmd[cmd.index(str(old))]=str(derived)
cmd.insert(cmd.index('-o'),str(source));cmd[cmd.index('-o')+1]=str(output)
subprocess.run(cmd,check=True)
output.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(output),
 'draft_source_hashes':{**b['draft_source_hashes'],**{str(f.relative_to(r)):sha(f) for f in [source,derived]}},
 'derived_from':{**b['derived_from'],str(old.relative_to(r)):sha(old)}},indent=2)+'\n')
print(output.name,output.stat().st_size,sha(output))
