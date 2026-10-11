"""Pin original gap completion only after original instructions, Node and Chromium agree."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
prior_path=p/'score-insert-checkpoint.json';assert sha(prior_path)=='ddb0a44210dadbcb84af60434f822966ea04a49e4c18010f371e432164f69156'
prior=read(prior_path);target=p/'gap-end-checkpoint.json';assert not target.exists()
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
b=read(p/'gap-end-draft.build.json');module=p/'gap-end-draft.wasm'
assert sha(module)==b['sha256']=='349f25417089fc44cb604c367456159692c75df7296ede2ecc4d6ef76944833c'
assert module.stat().st_size==839437 and b['source_hashes']==prior['source_hashes']
for name,digest in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==digest,name
previous=read(p/'score-insert-browser.json')['observed']['suites']
suites={name:read(p/('gap-end-checkpoint-'+name.replace('_','-')+'-result.json')) for name in ['gap_end',*previous]}
assert len(suites)==143
for name,result in suites.items():
 assert result['result']=='pass',name
 if name in previous:assert result==previous[name],name
unit=read(p/'gap-end-original.json');fixture=read(p/'gap-end-fixtures.json');coverage=unit['instruction_coverage']
assert (unit['cases'],unit['calls'],suites['gap_end']['cases'],suites['gap_end']['calls'])==(188,359,188,359)
assert unit['counts']==suites['gap_end']['counts'] and suites['gap_end']['nan_fields_classification_only']==0
assert set(coverage)==set(read(p/'gap-end-routines.json'))=={'0x512770','0x512cc0'}
assert [(x['covered'],x['total']) for x in coverage.values()]==[(401,403),(126,126)]
assert coverage['0x512770']['missing']==['0x512885','0x512c08']
assert not any(x['excluded'] for x in coverage.values()) and not fixture['float_fields']
stack_texts=0
for case in fixture['cases']:
 for step in case['steps']:
  assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','quiet_double_fields','global_bit_masks','float_fields','global_float_indices','indeterminate_bytes','compression_records'])
  for text in step['stack_texts']:
   data=bytes.fromhex(text['text'])
   assert text['slot']==0x1925a10 and 0x3000000<=text['original']<0x3018000
   assert text['buffer_capacity']==256 and text['observed_formatter_destination'] is True
   assert data.startswith(b'\\c1') and data.endswith(b'\\c0\0') and len(data)<=256 and b'\0' not in data[:-1]
   stack_texts+=1
assert stack_texts==suites['gap_end']['retained_stack_texts_verified']==12
assert suites['gap_end']['virtual_wait_callbacks']==7
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
proof=read(p/'gap-end-browser.json');assert proof['observed']==candidate and proof['status'].startswith('PASS')
def fingerprint(value):
 canonical=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
 for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
 return {'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(value)}
assert proof['rendered_dom_fingerprint']==fingerprint(candidate)
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
paths=set(p.glob('*gap-end*'))|{prior_path,p/'score-insert-audit.json'}
for f in paths:
 if f.is_file() and f not in [target,p/'gap-end-next.txt',p/'gap-end-audit.json']:
  artifacts[str(f.relative_to(r))]=sha(f)
  if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={**prior,'result':'original comparisons, Node and actual Chromium pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':2,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':718,'unpromoted_functions_across_separate_experiments':735,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'browser_suites':143,
 'new_cases':188,'new_calls_including_existing_dependencies':359,'new_interrupted_calls':0,
 'instruction_coverage':coverage,
 'retained_stack_texts_verified':stack_texts,'new_uninitialized_byte_allowances':0,
 'coverage_limit':'527/529 instructions exercised, including all126dispatcher instructions. One platform heap-initialization call and one null-successor exit after an unchecked read remain unexercised. No exclusions, numeric masks or uninitialized-byte allowances in the new suite. Retained stack text has verified formatter provenance, stack bounds and exact contents; the original dangling-pointer lifetime is preserved. Required initialized graphs, predicate boolean output, fitting text and successful allocations are caller contracts.',
 'scope':fixture['scope'],
 'unrecovered_lifecycle':'All six Gap commands, including EndGap, are connected through the actual component descriptor. Full skater construction remains at Trigger; remaining startup/frames, camera/rendering and original playable training remain unfinished.',
 'partial_command_dispatch':{**coverage['0x512cc0'],'incomplete_routes':[],'counted_as_complete':True},
 'combined_command_coverage':{'covered':126,'total':126,'missing':[],'source_suites':['gap-end'],'counted_as_complete':True},
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':fingerprint(candidate),'playable':False}
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
