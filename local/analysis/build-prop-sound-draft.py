import hashlib,json,subprocess
from pathlib import Path
root=Path.cwd();p=root/'local/analysis';sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
build=json.loads((p/'prop-lifecycle-draft.build.json').read_text())
for name,digest in {**build['source_hashes'],**build['draft_source_hashes']}.items():assert sha(root/name)==digest,name
# Preserve the immutable lifecycle source; derive a translation unit with only
# the two Sound frame slots filled by newly recovered behavior.
old=p/'prop-lifecycle-draft.c';derived=p/'prop-sound-lifecycle-derived.c'
text=old.read_text();anchor='const ThugComponentMethods thug_object_sound_methods_draft={.dispose='
assert text.count(anchor)==1
declarations='void thug_object_sound_frame_draft(void *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);\nvoid thug_object_sound_moved_draft(void *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);\n'
text=text.replace(anchor,declarations+'const ThugComponentMethods thug_object_sound_methods_draft={.update=thug_object_sound_frame_draft,.moved=thug_object_sound_moved_draft,.dispose=')
derived.write_text('/* Derived from the pinned lifecycle source; see build-prop-sound-draft.py. */\n'+text)
source=p/'prop-sound-draft.c';output=p/'prop-sound-draft.wasm';command=build['command'][:]
command[command.index(str(old))]=str(derived);command.insert(command.index('-o'),str(source));command[command.index('-o')+1]=str(output)
subprocess.run(command,check=True)
drafts={n:h for n,h in build['draft_source_hashes'].items() if n!=str(old.relative_to(root))}
drafts.update({str(s.relative_to(root)):sha(s) for s in [derived,source]})
output.with_suffix('.build.json').write_text(json.dumps({'command':command,'sha256':sha(output),'source_hashes':build['source_hashes'],'draft_source_hashes':drafts,'derived_from':{str(old.relative_to(root)):sha(old)}},indent=2)+'\n')
print(output.name,output.stat().st_size,sha(output))
