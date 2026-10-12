"""Pin ledge jumps, full Walk contacts and an explicitly partial ground update."""
import hashlib,json
from collections import Counter
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
prior_path=p/'walk-transition-checkpoint.json';assert sha(prior_path)=='57a220b40e27aa3c9bc00af074f838dab3fbd4eaa3e690c2f3d48a0f223fa78f'
prior=read(prior_path);target=p/'walk-ledge-checkpoint.json';assert not target.exists()
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
b=read(p/'walk-ledge-draft.build.json');module=p/'walk-ledge-draft.wasm'
assert sha(module)==b['sha256']=='32f8442295b75bbb36656ca2b5adf63cbc723c78033cc5253d8eabc8533e264c'
assert module.stat().st_size==876288 and b['source_hashes']==prior['source_hashes']
for name,digest in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==digest,name
previous=read(p/'walk-transition-browser.json')['observed']['suites']
suites={name:read(p/('walk-ledge-checkpoint-'+name.replace('_','-')+'-result.json')) for name in ['walk_ledge',*previous]}
assert len(suites)==150
for name,result in suites.items():
 assert result['result']=='pass',name
 if name in previous:assert result==previous[name],name
original=read(p/'walk-ledge-original.json');fixture=read(p/'walk-ledge-fixtures.json');coverage=original['instruction_coverage'];routines=read(p/'walk-ledge-routines.json')
unit=suites['walk_ledge']
assert (original['cases'],original['calls'],unit['cases'],unit['calls'])==(503,680,503,680)
assert original['counts']==unit['counts'] and unit['nan_fields_classification_only']==0
assert unit['counts']=={'thug_walk_ledge_jump_draft':302,'thug_walk_resolve_contacts_draft':363,'thug_walk_ground_contacts_prefix_draft':15}
assert len(coverage)==2 and set(coverage)==set(routines)=={'0x52bc70','0x52c2c0'}
extents=read(p/'walk-ledge-extents.json');assert extents['result']=='pass' and extents['routines_sha256']==sha(p/'walk-ledge-routines.json')
assert set(extents['checked'])==set(routines)
assert (sum(x['covered'] for x in coverage.values()),sum(x['total'] for x in coverage.values()))==(1241,1244)
assert {at:row['missing'] for at,row in coverage.items()}=={'0x52bc70':['0x52c0ba'],'0x52c2c0':['0x52c8d8','0x52c8df']}
assert all(not row['excluded'] for row in coverage.values()) and not fixture['float_fields']
undefined=Counter();interrupted=0
for case in fixture['cases']:
 copied_probes=set()
 for step in case['steps']:
  # A retained contact may survive another call without being copied again.
  # Its undefined provenance remains valid until the original writes it.
  copied_probes.update((x['field'],x['original'],x['size']) for x in step.get('stack_pointer_fields',[]))
  interrupted+=bool(step.get('expected_trap'))
  if step.get('expected_trap'):assert step['fn']=='0x52d300' and step['boundary_factory']==0x52b370
  assert not any(step.get(k) for k in ['quiet_float_fields','quiet_double_fields','global_quiet_float_indices','global_bit_masks','float_fields','global_float_indices','indeterminate_bytes','compression_records'])
  provenance=step.get('indeterminate_provenance',[]);words=step.get('indeterminate_words',[])
  assert len(set(words))==len(words)==len(provenance)
  assert set(words)=={row['destination'] for row in provenance}
  for row in provenance:
   offset=row['source_offset'];assert offset in [0x70,0xa8]
   assert row['copy_instruction']=={0x70:'0x4f81f1',0xa8:'0x43aa0f'}[offset] and row['source_writes_before_copy']==0
   assert row['destination'] in fixture['indeterminate_word_addresses'] and row['destination']%4==0
   field=row['destination']-offset+0x64
   assert field in fixture['stack_probe_pointer_fields']
   assert (field,row['source_probe'],0xb0) in copied_probes
   undefined[hex(offset)]+=1
assert interrupted==9 and undefined=={'0xa8':784,'0x70':36}
assert unit['indeterminate_word_comparisons']==sum(undefined.values())==820 and unit['virtual_wait_callbacks']==16
callbacks=original['callback_records'];assert len(callbacks)==14 and all(x['callbacks']==1 for x in callbacks)
parents=original['parent_records'];assert len(parents)==6
assert all(x['return']==0 and x['state']==(4 if x['route'].startswith('rail') else 0 if x['mutation']=='cancel' else 1) for x in parents)
ground=original['ground_prefix_coverage'];assert (ground['covered'],ground['total'])==(63,134)
assert len(set(ground['addresses']))==63
records=original['ground_prefix_records'];assert len(records)==15 and sum(x['interrupted'] for x in records)==9
negative=read(p/'walk-ledge-checker-negative.json')
assert negative['result']=='pass' and negative['corruptions_rejected']==6 and negative['undefined_word_mutation_accepted']
assert len(negative['checks'])==6 and all(x['rejected'] for x in negative['checks'])
for name in prior['artifact_hashes']:
 if name.endswith('-routines.json'):
  old=read(r/name)
  if isinstance(old,dict):assert not set(routines).intersection(old),name
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
proof=read(p/'walk-ledge-browser.json');assert proof['observed']==candidate and proof['status'].startswith('PASS')
def fingerprint(value):
 canonical=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
 for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
 return {'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(value)}
assert proof['rendered_dom_fingerprint']==fingerprint(candidate)
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
paths=set(p.glob('walk-ledge-*'))|{prior_path,p/'walk-transition-audit.json'}
paths.update(p/name for name in ['audit-walk-ledge.py','build-walk-ledge-draft.py','pin-walk-ledge.py','probe-walk-ledge.py','serve-walk-ledge.py','verify-walk-ledge-checkpoint.mjs'])
for f in paths:
 if f.is_file() and f.suffix!='.log' and f not in [target,p/'walk-ledge-next.txt',p/'walk-ledge-audit.json']:
  artifacts[str(f.relative_to(r))]=sha(f)
  if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={**prior,'result':'original comparisons, Node and actual Chromium pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':2,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':784,'unpromoted_functions_across_separate_experiments':801,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'browser_suites':150,
 'new_cases':503,'new_calls_including_existing_dependencies':680,'new_interrupted_calls':9,'instruction_coverage':coverage,
 'coverage_limit':'1241/1244 new instructions exercised; three skipped alignment instructions remain in the denominator without exclusions. Of680 comparison calls,671 complete and9 stop explicitly before floor handler52b370. All defined arena/global values compare;820 four-byte field comparisons are indeterminate only with original source-write and exact copier provenance (784 unknown_a8,36 unset scene). No numeric masks, NaN classification or quieting. Initialized graphs, finite inputs and valid cache/rail capacities are contracts. Existing trigonometric and PC24 arithmetic retain the established emulator model; physical processor transcendental accuracy is not newly established.',
 'scope':fixture['scope'],
 'unrecovered_lifecycle':'Ledge jumps and full eight-probe contact response are recovered. Ground parent52d300 now reaches63/134 and stops explicitly before floor handler52b370; genuine state/control exits return normally. Floor handling, full ground/Walk and intervening rail animation frames, remaining startup, renderer creation/rendering and original playable training remain unfinished. Constructor277/463 and common Walk frame51/142 are unchanged.',
 'walk_ledge_evidence':{'completed_calls':671,'interrupted_calls':9,'callback_records':callbacks,'contact_transition_records':parents,'ground_prefix_coverage':ground,'ground_prefix_records':records,
  'unexercised_alignment_instructions':['0x52c0ba','0x52c8d8','0x52c8df'],'unreachable_exclusions':{},'undefined_word_comparisons':820,'undefined_source_offsets':dict(undefined),
  'undefined_field_contract':'Only automatic probe+0xa8 and conditionally probe+0x70, tracked from initialization through exact copy instructions; any defining write ends the allowance. Stored probe pointers retain original-to-Wasm stack identity. No numeric field allowances.',
  'checker_corruptions_rejected':6,'undefined_word_mutation_accepted':True},
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':fingerprint(candidate),'playable':False}
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
