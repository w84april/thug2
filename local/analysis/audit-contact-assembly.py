"""Rehash full contact assembly while keeping playable-level completion unproven."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
path=p/'contact-assembly-checkpoint.json';c=json.loads(path.read_text())
prior=json.loads((p/'sphere-query-checkpoint.json').read_text())
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in c[group].items():assert sha(r/name)==digest,(group,name)
 for name,digest in prior[group].items():assert c[group][name]==digest,(group,name)
assert sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']==prior['main_wasm_sha256']
assert c['new_functions']==1 and not c['playable']
for key in ['actual_training','particle_frame_prefix','fan_training','original_only_scene_discovery','motion_descriptor_metadata','sphere_training','sphere_sweep_training','sphere_contact_training','sphere_query_training']:
 assert c[key]==prior[key],key
assert c['browser_suites']==121 and c['unpromoted_functions_in_this_module']==531
assert c['unpromoted_functions_across_separate_experiments']==548
row=c['instruction_coverage']['0x42c950'];assert row['covered']==363 and row['total']==369 and len(row['missing'])==6 and not row['excluded']
t=c['contact_assembly_training'];assert t['cases']==95 and t['calls']==285 and len(t['components'])==19
assert len(t['shape_relocations'])==19 and t['preserved_snapshot_calls']==63
report={'result':'pass','checkpoint_sha256':sha(path),'artifacts':len(c['artifact_hashes']),
 'maintained_sources':len(c['source_hashes']),'harnesses':len(c['harness_hashes']),
 'checker_dependencies':len(c['checker_dependency_hashes']),'preserved_previous_artifacts':len(prior['artifact_hashes']),
 'main_wasm_unchanged':True,'unit_cases':1833,'unit_calls':1870,'new_instruction_coverage':'363/369; six unexercised, no exclusions',
 'training_contact_cases':95,'training_contact_calls':285,'actual_training_props':19,
 'preserved_scene_trace_calls':63,'playable':False}
(p/'contact-assembly-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
