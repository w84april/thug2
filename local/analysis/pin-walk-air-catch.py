"""Pin verified wall-contact jumps, ballistic lip clearance and rail catches."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
prior_path=p/'walk-air-transitions-checkpoint.json';assert sha(prior_path)=='cbac667500b83c9363628c1775f9fbb5759a01d222ef76f072d9c7ec788c469f'
prior=read(prior_path);target=p/'walk-air-catch-checkpoint.json';assert not target.exists()
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
module=p/'walk-air-rail-draft.wasm';b=read(module.with_suffix('.build.json'))
assert sha(module)==b['sha256']=='18a9d58ff251d443ebdfa3b4cebbc7c21db6915c470c6e3abe9a09c675cfa8f1'
assert module.stat().st_size==914801 and b['source_hashes']==prior['source_hashes']
for name,digest in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==digest,name
new=['walk-air-jump-clearance','walk-air-contact-jump','walk-air-rail'];previous=read(p/'walk-air-transitions-browser.json')['observed']['suites']
suites={name:read(p/('walk-air-catch-checkpoint-'+name.replace('_','-')+'-result.json')) for name in [*[n.replace('-','_') for n in new],*previous]}
assert len(suites)==174
for name,result in suites.items():
 assert result['result']=='pass',name
 if name in previous:assert result==previous[name],name
routines={};coverage={};callback_count=0;cache_records=0
expected=[('walk-air-jump-clearance',{'0x529160':(177,180)},90,120),('walk-air-contact-jump',{'0x5293f0':(268,272)},134,152),('walk-air-rail',{'0x57c500':(21,21),'0x4413e0':(181,184),'0x57da20':(260,260),'0x442170':(81,81)},207,276)]
for name,addresses,cases,calls in expected:
 claimed=read(p/(name+'-routines.json'));assert set(claimed)==set(addresses);routines.update(claimed)
 original=read(p/(name+'-original.json'));fixture=read(p/(name+'-fixtures.json'));unit=suites[name.replace('-','_')]
 assert original['cases']==unit['cases']==cases and original['calls']==unit['calls']==calls and original['counts']==unit['counts']
 assert not fixture['float_fields'] and unit['nan_fields_classification_only']==0
 assert unit.get('indeterminate_byte_comparisons',0)==unit.get('indeterminate_word_comparisons',0)==0
 for address,(covered,total) in addresses.items():
  row=original['instruction_coverage'][address];assert (row['covered'],row['total'])==(covered,total) and not row['excluded'] and len(row['missing'])==total-covered;coverage[address]=row
 extents=read(p/(name+'-extents.json'));assert extents['result']=='pass' and extents['routines_sha256']==sha(p/(name+'-routines.json')) and set(extents['checked'])==set(addresses)
 for case in fixture['cases']:
  for step in case['steps']:
   assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','quiet_double_fields','global_quiet_float_indices','global_bit_masks','float_fields','global_float_indices','indeterminate_words','indeterminate_bytes','compression_records'])
   cache_records+=len(step.get('stack_objects',[]));callback_count+=step.get('callbacks',0)
assert len(routines)==6 and callback_count==12 and cache_records==0
for name in prior['artifact_hashes']:
 if name.endswith('-routines.json'):
  old=read(r/name)
  if isinstance(old,dict):assert not set(routines).intersection(old),name
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
proof=read(p/'walk-air-catch-browser.json');assert proof['observed']==candidate and proof['status'].startswith('PASS')
def fingerprint(value):
 canonical=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
 for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
 return {'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(value)}
assert proof['rendered_dom_fingerprint']==fingerprint(candidate)
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
paths={prior_path,p/'walk-air-transitions-audit.json',*p.glob('walk-air-catch-checkpoint-*-result.json')}
for name in new:
 for suffix in ['-draft.c','-draft.wasm','-draft.build.json','-original.json','-fixtures.json','-memory.bin','-extents.py','-extents.json','-routines.json']:paths.add(p/(name+suffix))
 for prefix,suffix in [('build-','-draft.py'),('probe-','.py'),('verify-','-unit.mjs')]:paths.add(p/(prefix+name+suffix))
for name in ['audit-walk-air-catch.py','pin-walk-air-catch.py','serve-walk-air-catch.py','verify-walk-air-catch-checkpoint.mjs','walk-air-catch-browser.html','walk-air-catch-browser.json','walk-air-catch-worker.mjs']:paths.add(p/name)
for f in paths:
 assert f.is_file(),f
 artifacts[str(f.relative_to(r))]=sha(f)
 if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={**prior,'result':'original comparisons, Node and actual Chromium pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':6,'original_addresses':list(routines),
 'unpromoted_functions_in_this_module':834,'unpromoted_functions_across_separate_experiments':851,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'browser_suites':174,
 'new_cases':431,'new_calls_including_existing_dependencies':548,'new_interrupted_calls':0,'instruction_coverage':coverage,
 'coverage_limit':'988/998 original instructions execute with no exclusions or interrupted calls. Ten unexercised instructions remain counted: three lip-clearance release instructions, two contact-jump unsigned-cooldown branches and two alignment bytes, and three rail-target miss-path release instructions. No numeric, indeterminate-word or padding-byte allowances are added. Twelve real collision QB callbacks execute in contact jumps. Full airborne frames remain unfinished.',
 'scope':'Six complete helpers recover ballistic lip clearance529160, contact jump5293f0, rail-target copy57c500, airborne rail target4413e0, weighted rail search57da20 and direct rail catch442170.431 cases and548 completed original calls match in Node and Chromium. The game is not playable.',
 'unrecovered_lifecycle':'Ground and animation partial Walk updates remain preserved. All identified52cef0 dependencies are now recovered, but the assembled full airborne frame remains unvalidated and is not counted. Hanging440bf0, rail4425b0, full dispatcher recovery, animation checksum/forward dispatch419950/4198d0, original asset startup, renderer creation/rendering and playable training remain unfinished. Constructor277/463 and maintained frame prefix51/142 are unchanged.',
 'walk_air_catch_evidence':{'completed_calls':548,'interrupted_calls':0,'complete_helpers':6,'cases':431,'covered_instructions':988,'total_instructions':998,'contact_jump_callbacks':12,'indeterminate_probe_word_comparisons':0,'new_numeric_allowances':0,'new_padding_allowances':0,'unreachable_exclusions':{}},
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':fingerprint(candidate),'playable':False}
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
