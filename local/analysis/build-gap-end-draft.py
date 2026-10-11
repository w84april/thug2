"""Derive a full Gap dispatcher and append original EndGap to the pinned module."""
import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
b=json.loads((p/'score-insert-draft.build.json').read_text())
for name,digest in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==digest,name
old=p/'gap-links-start-derived.c';derived=p/'gap-end-start-derived.c';s=old.read_text()
s=s.replace('/* Partial 00512cc0: five recovered routes. EndGap remains unavailable. */','/* 00512cc0: full dispatcher; exported name retained for descriptor ABI. */\nextern void thug_skater_gap_end_draft(void *,ThugScriptStructure *,ThugScriptInstance *,const ThugDiagnostics *,const ThugMemory *);')
s=s.replace('case 0x4562e4a6:break;case 0xe5399fb2:__builtin_trap();','case 0x4562e4a6:case 0xe5399fb2:break;')
s=s.replace('case 0x65b9ec39:thug_skater_gap_start_draft','case 0xe5399fb2:thug_skater_gap_end_draft(p,params,script,thug_event_services?thug_event_services->diagnostics:thug_component_services->diagnostics,m);break;\n case 0x65b9ec39:thug_skater_gap_start_draft')
assert s!=old.read_text() and '__builtin_trap' not in s;derived.write_text(s)
source=p/'gap-end-draft.c';output=p/'gap-end-draft.wasm';cmd=b['command'][:];cmd[cmd.index(str(old))]=str(derived)
cmd.insert(cmd.index('-o'),str(source));cmd[cmd.index('-o')+1]=str(output);subprocess.run(cmd,check=True)
draft={k:v for k,v in b['draft_source_hashes'].items() if k!=str(old.relative_to(r))};draft.update({str(f.relative_to(r)):sha(f) for f in [source,derived]})
output.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(output),'draft_source_hashes':draft,'derived_from':{**b['derived_from'],str(old.relative_to(r)):sha(old)}},indent=2)+'\n')
print(output.name,output.stat().st_size,sha(output))
