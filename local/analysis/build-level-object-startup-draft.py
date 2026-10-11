import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
b=json.loads((p/'geometry-clone-draft.build.json').read_text())
for n,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/n)==h,n
old=p/'scene-create-draft.c';new=p/'level-object-startup-create-derived.c';s=old.read_text()
a='    case 0xef59c100:thug_gameobject_create_node_prefix_draft(node);return 1;'
s=s.replace('uint8_t thug_scene_create_node_prefix_draft(ThugScriptStructure *node){','void thug_level_object_create_prefix_draft(ThugScriptStructure *);\nuint8_t thug_scene_create_node_prefix_draft(ThugScriptStructure *node){')
assert s.count(a)==1;s=s.replace(a,a+'\n    case 0xb7b3bd86:thug_level_object_create_prefix_draft(node);return 1;').replace('case 0xa0dfac98:case 0xb7b3bd86:case 0xbf4d3536:','case 0xa0dfac98:case 0xbf4d3536:')
new.write_text(s)
source=p/'level-object-startup-draft.c';output=p/'level-object-startup-draft.wasm';cmd=b['command'][:]
cmd[cmd.index(str(old))]=str(new);cmd.insert(cmd.index('-o'),str(source));cmd[cmd.index('-o')+1]=str(output)
cmd=[v.replace('--initial-memory=67108864','--initial-memory=134217728').replace('--max-memory=134217728','--max-memory=268435456') for v in cmd]
subprocess.run(cmd,check=True)
drafts={n:h for n,h in b['draft_source_hashes'].items() if n!=str(old.relative_to(r))};drafts.update({str(f.relative_to(r)):sha(f) for f in [new,source]})
output.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(output),'draft_source_hashes':drafts,'derived_from':{**b['derived_from'],str(old.relative_to(r)):sha(old)}},indent=2)+'\n')
print(output.name,output.stat().st_size,sha(output))
