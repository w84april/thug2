from pathlib import Path
import hashlib,json,subprocess
r=Path.cwd();p=r/'local/analysis';source=p/'level-collision-load-unit-ports.c';output=source.with_suffix('.wasm')
cmd=[str(r/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang'),'--target=wasm32-unknown-unknown','-O2','-nostdlib','-Wl,--no-entry,--export-all,--import-memory',str(source),'-o',str(output)]
subprocess.run(cmd,check=True);sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
output.with_suffix('.build.json').write_text(json.dumps({'command':cmd,'source_sha256':sha(source),'sha256':sha(output)},indent=2)+'\n')
print(output.name,sha(output))
