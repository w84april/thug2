from pathlib import Path
import hashlib,json,subprocess
r=Path.cwd();p=r/'local/analysis';old=p/'training-level-register-ports.c';s=old.read_text()
s=s.replace('#include "../../tools/script_values_memory.c"','#include "../../tools/script_loader_memory.c"')
start=s.index('void *fixture_training_allocate');end=s.index('static uint32_t *event',start)
s=s[:start]+'''uint32_t fixture_training_scope(const void *p){uint32_t a=(uintptr_t)p;if(a<0x2400000||a>=0x4000000)__builtin_trap();put(CONTROL+12,word(CONTROL+12)+1);return 1;}
'''+s[end:]
changes={'(BASE+0x1000)':'(BASE+0xf1300)','(BASE+0x1100)':'(BASE+0xf2200)','(BASE+0x800000)':'(BASE+0x1700000)','(BASE+0xb00000)':'(BASE+0x1a00000)','(BASE+0xa00)':'(BASE+0xf1200)',
 'BASE+0x2600000':'BASE+0x5800000','BASE+0x500000':'BASE+0x1400000','(BASE+0x1200)':'(BASE+0xf2300)','(BASE+0x3000)':'(BASE+0xf2400)','0x2400000u':'0x4800000u','0x2800000u':'0x5000000u','BASE+0x800':'BASE+0xf1000','BASE+0x2100':'BASE+0xf2100','BASE+0x2000':'BASE+0xf2000'}
for a,b in changes.items():s=s.replace(a,b)
s+='\nvoid *fixture_collision_factory_boundary(void *m){(void)m;volatile uint32_t *p=(void *)0x80e000;p[0]=0x41c920;p[1]=*(uint32_t *)0x80c010;p[2]=0x80c000;p[3]=1;__builtin_trap();}\n'
source=p/'level-object-startup-ports.c';output=p/'level-object-startup-ports.wasm';source.write_text(s)
clang=r/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang';cmd=[str(clang),'--target=wasm32-unknown-unknown','-O2','-nostdlib','-Wl,--no-entry,--export-all,--import-memory',str(source),'-o',str(output)]
subprocess.run(cmd,check=True);sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
output.with_suffix('.build.json').write_text(json.dumps({'command':cmd,'source_sha256':sha(source),'derived_from':{str(old.relative_to(r)):sha(old)},'sha256':sha(output)},indent=2)+'\n');print('Comparison ports built',output.stat().st_size)
