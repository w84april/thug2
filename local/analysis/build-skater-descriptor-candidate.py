import hashlib,json,subprocess,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();b=json.loads((p/'skater-end-run-startup-draft.build.json').read_text());cmd=b['command'][:]
for n,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/n)==h,n
negative='--negative' in sys.argv;draft=dict(b['draft_source_hashes'])
if not negative:
 for name in ['skater-local-net','skater-end-run']:
  old=p/(name+'-draft.c');new=p/(name+'-descriptor-corrected.c');cmd[cmd.index(str(old))]=str(new);draft.pop(str(old.relative_to(r)));draft[str(new.relative_to(r))]=sha(new)
probe=p/'component-base-descriptor-probe.c';cmd.insert(cmd.index('-o'),str(probe));draft[str(probe.relative_to(r))]=sha(probe)
out=p/('skater-descriptor-negative.wasm' if negative else 'skater-descriptor-corrected.wasm');cmd[cmd.index('-o')+1]=str(out)
subprocess.run(cmd,check=True);out.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(out),'draft_source_hashes':draft},indent=2)+'\n');print(out.name,out.stat().st_size,sha(out))
