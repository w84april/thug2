"""Add full gap creation and wire only recovered command routes."""
import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
b=json.loads((p/'gap-score-draft.build.json').read_text())
for name,digest in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==digest,name
old=p/'skater-gap-draft.c';new=p/'gap-start-component-derived.c';s=old.read_text()
needle='static uint32_t pending_command(void *p,uint32_t n,ThugScriptStructure *s,ThugScriptInstance *i){(void)p;(void)n;(void)s;(void)i;__builtin_trap();}'
assert s.count(needle)==1
s=s.replace(needle,'uint32_t thug_skater_gap_command_prefix_draft(void *,uint32_t,ThugScriptStructure *,ThugScriptInstance *);\nstatic uint32_t pending_command(void *p,uint32_t n,ThugScriptStructure *s,ThugScriptInstance *i){return thug_skater_gap_command_prefix_draft(p,n,s,i);}')
new.write_text(s);cmd=b['command'][:];matches=[i for i,v in enumerate(cmd) if Path(v).resolve()==old];assert len(matches)==1
cmd[matches[0]]=str(new);source=p/'gap-start-draft.c';output=p/'gap-start-draft.wasm'
cmd.insert(cmd.index('-o'),str(source));cmd[cmd.index('-o')+1]=str(output)
subprocess.run(cmd,check=True)
draft=b['draft_source_hashes'].copy();draft.pop(str(old.relative_to(r)));draft.update({str(f.relative_to(r)):sha(f) for f in [new,source]})
output.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(output),'draft_source_hashes':draft,'derived_from':{**b['derived_from'],str(old.relative_to(r)):sha(old)}},indent=2)+'\n')
print(output.name,output.stat().st_size,sha(output))
