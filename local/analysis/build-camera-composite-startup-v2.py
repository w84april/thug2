"""Derive startup tables without modifying any selected predecessor sources."""
import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
b=json.loads((p/'skater-camera-initialization-v2.build.json').read_text())
for n,h in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/n)==h,n
out=p/'camera-composite-startup-v2.wasm';assert not out.exists()
factory=p/'skater-camera-factories-v1.c';derived_factory=p/'camera-composite-factories-v2.c';assert not derived_factory.exists()
s=factory.read_text().replace('/* Camera descriptor storage candidates; initialized heap required.\n * Pending tables are identity-only and establish no virtual lifecycle. */','/* Derived camera startup tables. Only initialization/finalization/moved\n * slots are exercised; unverified frame/command/disposal slots stay unavailable. */')
declarations='''void thug_skater_camera_initialize_v1(void *,const ThugScriptStructure *);
void thug_skater_camera_object_initialize_v1(void *,const ThugScriptStructure *);
void thug_skater_camera_roll_initialize_v1(void *,const ThugScriptStructure *);
void thug_skater_camera_bind_object_v1(void *);
void thug_skater_camera_object_finalize_v1(void *);
void thug_skater_camera_roll_finalize_v1(void *);
'''
tables='''const ThugComponentMethods thug_skater_camera_pending_methods_v1={.initialize=thug_skater_camera_initialize_v1,.finalize=thug_skater_camera_bind_object_v1,.moved=thug_component_empty_frame_bridge};
const ThugComponentMethods thug_skater_camera_object_pending_methods_v1={.initialize=thug_skater_camera_object_initialize_v1,.finalize=thug_skater_camera_object_finalize_v1,.moved=thug_component_empty_frame_bridge};
const ThugComponentMethods thug_skater_camera_roll_pending_methods_v1={.initialize=thug_skater_camera_roll_initialize_v1,.finalize=thug_skater_camera_roll_finalize_v1,.moved=thug_component_empty_frame_bridge};'''
old='\n'.join('const uint32_t '+n+'[13]={0};' for n in ['thug_skater_camera_pending_methods_v1','thug_skater_camera_object_pending_methods_v1','thug_skater_camera_roll_pending_methods_v1']);assert old in s
s=s.replace(old,declarations+tables)
for n in ['thug_skater_camera_pending_methods_v1','thug_skater_camera_object_pending_methods_v1','thug_skater_camera_roll_pending_methods_v1']:s=s.replace('(uintptr_t)'+n,'(uintptr_t)&'+n)
derived_factory.write_text(s)
camera=p/'camera-startup-v2.c';derived_camera=p/'camera-composite-camera-v2.c';assert not derived_camera.exists()
s=camera.read_text();old='static void pending_initialize(void *p,const ThugScriptStructure *s){(void)p;(void)s;__builtin_trap();}';assert old in s
s=s.replace(old,'void thug_generic_camera_initialize_bridge_v1(void *,const ThugScriptStructure *);').replace('.initialize=pending_initialize','.initialize=thug_generic_camera_initialize_bridge_v1').replace('.refresh=thug_component_refresh,','.moved=thug_component_empty_frame_bridge,.refresh=thug_component_refresh,')
derived_camera.write_text(s)
cmd=b['command'][:];draft=dict(b['draft_source_hashes']);derived=dict(b['derived_from'])
for old,new in [(factory,derived_factory),(camera,derived_camera)]:
 assert str(old) in cmd;cmd[cmd.index(str(old))]=str(new);oldkey=str(old.relative_to(r));newkey=str(new.relative_to(r));draft.pop(oldkey);draft[newkey]=sha(new);derived[oldkey]=sha(old)
source=p/'camera-composite-startup-v1.c';cmd.insert(cmd.index('-o'),str(source));cmd[cmd.index('-o')+1]=str(out);subprocess.run(cmd,check=True)
draft[str(source.relative_to(r))]=sha(source)
out.with_suffix('.build.json').write_text(json.dumps({**b,'command':cmd,'sha256':sha(out),'draft_source_hashes':draft,'derived_from':derived},indent=2)+'\n')
print(out.name,out.stat().st_size,sha(out))
