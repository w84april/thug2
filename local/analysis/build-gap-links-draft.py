"""Preserve gap-start evidence and add the real linked-node command route."""
import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
b=json.loads((p/'gap-start-draft.build.json').read_text())
for name,digest in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==digest,name
old=p/'gap-start-draft.c';new=p/'gap-links-start-derived.c';s=old.read_text()
needle='/* Partial 00512cc0 integration: four recovered routes and the original unknown\n * result. EndGap and prefix-trigger dispatch still trap and are not counted. */'
assert s.count(needle)==1
s=s.replace(needle,'/* Partial 00512cc0: five recovered routes. EndGap remains unavailable. */\nextern uint32_t thug_node_named_link_count_draft(uint32_t);\nextern ThugScriptStructure *thug_node_link_at_draft(uint32_t,int32_t);')
s=s.replace('case 0xe5399fb2:case 0x4562e4a6:__builtin_trap();','case 0x4562e4a6:break;case 0xe5399fb2:__builtin_trap();')
needle=' switch(name){\n case 0x65b9ec39:';assert s.count(needle)==1
s=s.replace(needle,''' switch(name){
 case 0x4562e4a6:{
  uint32_t owner=word(script,0xb8);if(!owner)break;
  int32_t count=(int32_t)thug_node_named_link_count_draft(owner);
  for(int32_t i=0;i<count;i++){
   ThugScriptStructure *node=thug_node_link_at_draft(owner,i);uint32_t name=0;
   if(thug_script_get_checksum_legacy(node,0x2ca8a299,&name,0)){
    thug_object_spawn_script(ptr(p,12),name,word(script,0xb8),0,0,0,
      thug_event_services?thug_event_services->diagnostics:thug_component_services->diagnostics,m);break;
   }
  }break;
 }
 case 0x65b9ec39:''')
new.write_text(s);cmd=b['command'][:];matches=[i for i,v in enumerate(cmd) if Path(v).resolve()==old];assert len(matches)==1
cmd[matches[0]]=str(new);source=p/'gap-links-draft.c';output=p/'gap-links-draft.wasm'
cmd.insert(cmd.index('-o'),str(source));cmd[cmd.index('-o')+1]=str(output)
subprocess.run(cmd,check=True)
draft=b['draft_source_hashes'].copy();draft.pop(str(old.relative_to(r)));draft.update({str(f.relative_to(r)):sha(f) for f in [new,source]})
output.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(output),'draft_source_hashes':draft,'derived_from':{**b['derived_from'],str(old.relative_to(r)):sha(old)}},indent=2)+'\n')
print(output.name,output.stat().st_size,sha(output))
