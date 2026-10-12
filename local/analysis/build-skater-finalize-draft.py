import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
b=json.loads((p/'trigger-draft.build.json').read_text())
for n,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/n)==h,n
sources=[p/'skater-finalize-draft.c',p/'skater-finalize-constructor-prefix.c'];output=p/'skater-finalize-draft.wasm';cmd=b['command'][:]
vector=r/'src/core/vector.c';derived=p/'skater-finalize-vector-derived.c'
source=vector.read_text().replace('#include "vector.h"','#include "../../src/core/vector.h"').replace('#include "../platform/math.h"','#include "../../src/platform/math.h"')
old='''        for (unsigned i = 0; i < 3; ++i)
            vector[i] = (float)thug_platform_round_x87_single((double)vector[i] * inverse);'''
assert source.count(old)==1
source=source.replace(old,'''        for (unsigned i = 0; i < 3; ++i) {
            /* x87 infinity times zero produces the negative indefinite NaN;
             * Wasm's default NaN sign is not that original stored encoding. */
            if (__builtin_isinf(vector[i]) && inverse == 0) {
                uint32_t indefinite = UINT32_C(0xffc00000);
                __builtin_memcpy(vector+i, &indefinite, 4);
            } else vector[i] = (float)thug_platform_round_x87_single((double)vector[i] * inverse);
        }''')
derived.write_text(source);cmd[cmd.index(str(vector))]=str(derived);sources.append(derived)
for source in sources:
 if str(source) not in cmd:cmd.insert(cmd.index('-o'),str(source))
cmd[cmd.index('-o')+1]=str(output);subprocess.run(cmd,check=True)
output.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(output),'draft_source_hashes':{**b['draft_source_hashes'],**{str(f.relative_to(r)):sha(f) for f in sources}}},indent=2)+'\n')
print(output.name,output.stat().st_size,sha(output))
