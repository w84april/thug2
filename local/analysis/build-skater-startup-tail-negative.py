import json,subprocess
from pathlib import Path
p=Path('local/analysis');s=(p/'skater-startup-tail-draft.c').read_text();b=json.loads((p/'skater-startup-tail-parent-draft.build.json').read_text())
variants={'clear-toggle':s.replace('((uint8_t *)p)[0x9f6]=0;','((uint8_t *)p)[0x9f6]=0;((uint8_t *)p)[0x9f5]=0;'),'cache-difficulty':s.replace('word(p,0xa18)','difficulty')}
for name,source in variants.items():
 assert source!=s;path=p/('skater-startup-tail-negative-'+name+'.c');path.write_text(source);cmd=[str(path.resolve()) if str(Path(x))==str((p/'skater-startup-tail-draft.c').resolve()) else x for x in b['command']];cmd[cmd.index('-o')+1]=str((p/('skater-startup-tail-negative-'+name+'.wasm')).resolve());subprocess.run(cmd,check=True)
