import hashlib,json,subprocess
from pathlib import Path
p=Path('local/analysis');s=(p/'skater-tag-texture-draft.c').read_text();b=json.loads((p/'skater-full-startup-draft.build.json').read_text())
variants={'ignore-pitch':s.replace('in+=input.pitch;out+=output.pitch;','in+=bytes;out+=bytes;'),'source-buffer-test':s.replace('if(word(ptr(p,16),8))','if(word(ptr(source,16),8))')}
for name,source in variants.items():
 assert source!=s;path=p/('skater-tag-texture-negative-'+name+'.c');path.write_text(source);cmd=[str(path.resolve()) if x==str((p/'skater-tag-texture-draft.c').resolve()) else x for x in b['command']];cmd[cmd.index('-o')+1]=str((p/('skater-tag-texture-negative-'+name+'.wasm')).resolve());subprocess.run(cmd,check=True)
 print('built',name,flush=True)
