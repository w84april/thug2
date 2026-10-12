import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
b=json.loads((p/'skater-finalize-draft.build.json').read_text())
for n,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/n)==h,n
cmd=b['command'][:];output=p/'skater-cleanup-draft.wasm';sources=[p/'skater-cleanup-draft.c',p/'skater-cleanup-constructor-prefix.c']
old=p/'skater-ground-model-derived.c';new=p/'skater-cleanup-model-derived.c';s=old.read_text()
s=s.replace('    uintptr_t unavailable_2c;','    uintptr_t unavailable_2c;\n    uint32_t (*direction_enabled)(void *,uint32_t);')
s=s.replace('static void light_refresh(', 'extern float *thug_light_direction_pc_draft(void *,uint32_t);\nextern uint32_t thug_light_direction_enabled_draft(void *,uint32_t);\nstatic void light_refresh(')
s=s.replace('.unavailable_4_to_20={[7]=(uintptr_t)light_refresh}', '.unavailable_4_to_20={[4]=(uintptr_t)thug_light_direction_pc_draft,[7]=(uintptr_t)light_refresh},.direction_enabled=thug_light_direction_enabled_draft')
new.write_text(s);cmd[cmd.index(str(old))]=str(new);sources.append(new)
for f in sources:
 if str(f) not in cmd:cmd.insert(cmd.index('-o'),str(f))
cmd[cmd.index('-o')+1]=str(output);subprocess.run(cmd,check=True)
output.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(output),'draft_source_hashes':{**b['draft_source_hashes'],**{str(f.relative_to(r)):sha(f) for f in sources}}},indent=2)+'\n')
print(output.name,output.stat().st_size,sha(output))
