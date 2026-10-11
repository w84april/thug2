import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
b=json.loads((p/'prop-sound-draft.build.json').read_text())
for n,h in {**b['source_hashes'],**b['draft_source_hashes']}.items():assert sha(r/n)==h,n
old=p/'composite-construction-draft.c';derived=p/'prop-command-composite-derived.c';text=old.read_text()
anchor='    uint32_t unavailable_4[4];'
assert text.count(anchor)==1
text=text.replace(anchor,'''    void (*parameters)(void *,ThugScriptStructure *);
    uint32_t (*descriptor)(void *,const ThugScriptCommand *,ThugScriptStructure *,ThugScriptInstance *);
    uint32_t (*checksum)(void *,uint32_t,ThugScriptStructure *,ThugScriptInstance *);
    void (*empty)(void *,void *);''')
anchor='const CompositeMethodsDraft thug_composite_methods_draft={'
assert text.count(anchor)==1
text=text.replace(anchor,'''void thug_object_apply_parameters_draft(void *,ThugScriptStructure *);
uint32_t thug_composite_descriptor_draft(void *,const ThugScriptCommand *,ThugScriptStructure *,ThugScriptInstance *);
uint32_t thug_composite_checksum_draft(void *,uint32_t,ThugScriptStructure *,ThugScriptInstance *);
const CompositeMethodsDraft thug_composite_methods_draft={
    .parameters=thug_object_apply_parameters_draft,.descriptor=thug_composite_descriptor_draft,
    .checksum=thug_composite_checksum_draft,.empty=thug_component_empty_one,''')
text=text.replace('/* The command/descriptor virtuals remain unavailable, not success replacements.\n * These recovered slots support construction/finalization/lifetime only. */','/* Command slots are supplied by prop-command-draft.c; other original slots are preserved. */')
derived.write_text('/* Derived from pinned composite-construction-draft.c; see build script. */\n'+text)
source=p/'prop-command-draft.c';output=p/'prop-command-draft.wasm';cmd=b['command'][:]
cmd[cmd.index(str(old))]=str(derived);cmd.insert(cmd.index('-o'),str(source));cmd[cmd.index('-o')+1]=str(output)
subprocess.run(cmd,check=True)
drafts={n:h for n,h in b['draft_source_hashes'].items() if n!=str(old.relative_to(r))}
drafts.update({str(s.relative_to(r)):sha(s) for s in [source,derived]})
output.with_suffix('.build.json').write_text(json.dumps({'command':cmd,'sha256':sha(output),'source_hashes':b['source_hashes'],'draft_source_hashes':drafts,'derived_from':{str(old.relative_to(r)):sha(old)}},indent=2)+'\n')
print(output.name,output.stat().st_size,sha(output))
