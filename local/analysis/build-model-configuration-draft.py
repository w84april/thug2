import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
b=json.loads((p/'model-initialize-draft.build.json').read_text())
for n,h in {**b['source_hashes'],**b['draft_source_hashes']}.items():assert sha(r/n)==h,n
source=p/'model-configuration-draft.c';output=p/'model-configuration-draft.wasm';cmd=b['command'][:]
old=p/'model-initialize-draft.c';derived=p/'model-configuration-initialize-derived.c';s=old.read_text()
needle='void (*thug_model_configuration_pending_draft)(void *,const ThugScriptStructure *);'
assert s.count(needle)==1
s=s.replace(needle,'void thug_model_configuration_prefix_draft(void *,const ThugScriptStructure *);\nvoid (*thug_model_configuration_pending_draft)(void *,const ThugScriptStructure *)=thug_model_configuration_prefix_draft;')
derived.write_text('/* Derived from pinned initializer prefix; bind the next recovered configuration prefix. */\n'+s)
cmd[cmd.index(str(old))]=str(derived)
cmd.insert(cmd.index('-o'),str(source));cmd[cmd.index('-o')+1]=str(output)
subprocess.run(cmd,check=True)
drafts={n:h for n,h in b['draft_source_hashes'].items() if n!=str(old.relative_to(r))}
drafts.update({str(f.relative_to(r)):sha(f) for f in [source,derived]})
output.with_suffix('.build.json').write_text(json.dumps({'command':cmd,'sha256':sha(output),'source_hashes':b['source_hashes'],'draft_source_hashes':drafts,'derived_from':{**b['derived_from'],str(old.relative_to(r)):sha(old)}},indent=2)+'\n')
print(output.name,output.stat().st_size,sha(output))
