"""Pin score insertion only after original instructions, Node and Chromium agree."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
prior_path=p/'gap-links-checkpoint.json';assert sha(prior_path)=='cfd900141181f7625cf7a3e03415be868fe660a16e8f0af95d012025f417ef5e'
prior=read(prior_path);target=p/'score-insert-checkpoint.json';assert not target.exists()
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
b=read(p/'score-insert-draft.build.json');module=p/'score-insert-draft.wasm'
assert sha(module)==b['sha256']=='3b1cdb8be0decee55a3810a7e7a93df4c1ce80823dbb97f83086b27c27ff944d'
assert module.stat().st_size==837925 and b['source_hashes']==prior['source_hashes']
for name,digest in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==digest,name
previous=read(p/'gap-links-browser.json')['observed']['suites']
suites={name:read(p/('score-insert-checkpoint-'+name.replace('_','-')+'-result.json')) for name in ['score_insert',*previous]}
assert len(suites)==142
for name,result in suites.items():
 assert result['result']=='pass',name
 if name in previous:assert result==previous[name],name
unit=read(p/'score-insert-original.json');fixture=read(p/'score-insert-fixtures.json');coverage=unit['instruction_coverage']
assert (unit['cases'],unit['calls'],suites['score_insert']['cases'],suites['score_insert']['calls'])==(369,1904,369,1904)
assert unit['counts']==suites['score_insert']['counts'] and suites['score_insert']['nan_fields_classification_only']==0
assert set(coverage)==set(read(p/'score-insert-routines.json'))=={'0x5629d0','0x563990'}
assert [(x['covered'],x['total']) for x in coverage.values()]==[(108,108),(445,448)]
assert coverage['0x563990']['missing']==['0x563af5','0x563c2d','0x563c6d']
assert not any(x['excluded'] for x in coverage.values()) and not fixture['float_fields']
allowance=0;copies=0
for case in fixture['cases']:
 for step in case['steps']:
  assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','quiet_double_fields','global_bit_masks','float_fields','global_float_indices'])
  proven=set()
  for record in step['compression_records']:
   a=record['destination'];ranges=[[a+0x23,57],[a+0x65,55]]
   assert record['indeterminate_tails']==ranges and fixture['base']<=a and a+156<=fixture['base']+3670016
   for at,n in ranges:proven.update(range(at,at+n))
  used=set()
  for at,n in step['indeterminate_bytes']:
   span=set(range(at,at+n));assert n>0 and span<=proven and not used&span;used|=span
  allowance+=len(used)
 copies+=len(case['steps'][-1]['compression_records'])
assert allowance==suites['score_insert']['indeterminate_compression_bytes_compared_by_definedness']==2688
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
proof=read(p/'score-insert-browser.json');assert proof['observed']==candidate and proof['status'].startswith('PASS')
def fingerprint(value):
 canonical=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
 for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
 return {'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(value)}
assert proof['rendered_dom_fingerprint']==fingerprint(candidate)
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
paths=set(p.glob('*score-insert*'))|{prior_path,p/'gap-links-audit.json'}
for f in paths:
 if f.is_file() and f not in [target,p/'score-insert-next.txt',p/'score-insert-audit.json']:
  artifacts[str(f.relative_to(r))]=sha(f)
  if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={**prior,'result':'original comparisons, Node and actual Chromium pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':2,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':716,'unpromoted_functions_across_separate_experiments':733,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'browser_suites':142,
 'new_cases':369,'new_calls_including_existing_dependencies':1904,'new_interrupted_calls':0,
 'instruction_coverage':coverage,
 'indeterminate_storage':{'routine':'0x5629d0','record_bytes':156,'tails':[[35,57],[101,55]],'copies':copies,'bytes_across_compared_steps':allowance,'basis':'Uninitialized automatic string tails after their NUL terminators; later original writes remove the allowance. All defined bytes and numeric values compare exactly. No oracle padding is copied into Wasm.'},
 'coverage_limit':'553/556 instructions exercised. One platform heap-initialization call and two jumped-over alignment instructions remain unexercised; no exclusions or numeric masks. Successful allocations, fitting strings, valid repeat/spin indices and initialized graphs are caller contracts. Higher raw repeat variants use sufficiently large existing records. Compression requires a surviving entry zero.',
 'scope':fixture['scope'],
 'unrecovered_lifecycle':'Score insertion and history compression are recovered as complete routines. EndGap remains unavailable; its partial command dispatcher is not counted complete. Remaining skater construction/frames, camera/rendering and original playable training remain unfinished. Skater construction remains at Trigger.',
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':fingerprint(candidate),'playable':False}
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
