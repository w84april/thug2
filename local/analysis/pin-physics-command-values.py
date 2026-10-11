"""Pin only after actual Chromium PASS and the full canonical DOM fingerprint."""
import hashlib,json,sys
from pathlib import Path
root=Path.cwd();folder=root/'local/analysis'
target=folder/'physics-command-values-checkpoint.json';browser_path=folder/'physics-command-values-browser.json'
assert not target.exists() and not browser_path.exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((folder/n).read_text())
candidate=read('physics-command-values-browser-candidate.json');build=read('physics-movement-members-draft.build.json')
canonical=json.dumps(candidate,ensure_ascii=False,sort_keys=True,separators=(',',':'));h=14695981039346656037
for c in canonical:h=((h^ord(c))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}'=='ca9c086f5f903598'
assert int(sys.argv[2])==len(canonical)==6158 and int(sys.argv[3])==len(candidate)==5
assert candidate['wasm_sha256']==build['sha256']==sha(folder/'physics-movement-members-draft.wasm')=='4da635ca28fece46c2afe9033e8ebc74306d7743078a6576a2037738032b0307'
assert (candidate['wasm_bytes'],candidate['runtime_imports'])==(489405,0)
assert sum(v['cases'] for v in candidate['suites'].values())==5510 and sum(v['calls'] for v in candidate['suites'].values())==12515
for n,r in candidate['suites'].items():
 assert r==read(n.replace('_','-')+'-result.json') and r['result']=='pass' and r['nan_fields_classification_only']==0,n
prior=read('physics-parameter-flags-checkpoint.json')
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for n,v in prior[group].items():assert sha(root/n)==v,(group,n)
for n,v in {**build['source_hashes'],**build['draft_source_hashes']}.items():assert sha(root/n)==v,n
assert build['source_hashes']==prior['source_hashes']
coverage={}
for n in ['physics-airtime','physics-script-outputs','physics-movement-members']:
 report=read(n+'-original.json')
 for at,v in report['instruction_coverage'].items():
  assert at not in coverage and v['covered']==v['total'] and not v['missing'];coverage[at]=v
assert len(coverage)==12 and sum(v['covered'] for v in coverage.values())==218
context=read('physics-command-values-context-original.json')
assert (context['cases'],context['calls'])==(12,72)
assert len(context['member_calls'])==16 and set(context['member_calls'].values())=={12}
assert sum(context['native_qb_calls'].values())==196
assert candidate['suites']['physics_command_values_context']['native_qb_callbacks']==392
proof=dict(candidate);proof.update({'recorded_at':sys.argv[4],'observed_via':'Chromium DOM at '+sys.argv[5]+'; PASS; all five suite summaries and complete canonical DOM fingerprint inspected','browser_dom_fingerprint':{'algorithm':'FNV-1a-64 over canonical sorted JSON characters','value':sys.argv[1],'characters':int(sys.argv[2])},'scope':'Twelve additional original routines: eleven physics members and the airtime-unit helper. Combined experiment includes the prior five members, for sixteen named members and seventeen unpromoted routines. All five suites execute the combined module. Original training remains unplayable; main159-suite checkpoint unchanged.'})
browser_path.write_text(json.dumps(proof,indent=2)+'\n')
artifacts=set(prior['artifact_hashes']);artifacts.add('local/analysis/physics-parameter-flags-checkpoint.json')
names=['physics-script-values-draft.c','physics-script-values-draft.wasm','physics-script-values-draft.build.json','build-physics-script-values-draft.py','physics-movement-members-draft.c','physics-movement-members-draft.wasm','physics-movement-members-draft.build.json','build-physics-movement-members-draft.py','physics-script-outputs-memory.c','physics-script-outputs-memory.wasm','physics-command-values-browser.html','serve-physics-command-values.py','verify-physics-command-values.mjs','physics-command-values-browser-candidate.json','physics-command-values-browser.json','physics-command-values-status.json','pin-physics-command-values.py']
artifacts.update('local/analysis/'+n for n in names)
for n in ['physics-airtime','physics-script-outputs','physics-movement-members','physics-command-values-context']:
 artifacts.update('local/analysis/'+f for f in ['probe-'+n+'.py','verify-'+n+'.mjs',n+'-original.json',n+'-result.json',n+'-fixtures.json'])
 fixture=read(n+'-fixtures.json');artifacts.add('local/analysis/'+fixture['memory'])
 deps={row['module'] for row in fixture.get('native_callbacks',[])}
 if fixture.get('memory_fixture'):deps.add(fixture['memory_fixture'])
 for filename in deps:
  p=folder/filename
  if not p.exists():p=root/'local/validation/collision'/filename
  artifacts.add(str(p.relative_to(root)))
checkpoint={'result':'isolated original, Node and Chromium pass; not yet in maintained main counts','new_functions':12,'new_members':11,'combined_unpromoted_functions':17,'combined_unpromoted_members':16,'specimen_sha256':context['specimen_sha256'],'wasm_sha256':candidate['wasm_sha256'],'main_wasm_sha256':prior['main_wasm_sha256'],'wasm_bytes':489405,'browser_suites':5,'browser_cases':5510,'browser_calls':12515,'native_qb_observations':405,'instruction_coverage':coverage,'context_original_cases':12,'context_wasm_cases':24,'context_wasm_calls':144,'context_original_member_calls':192,'context_wasm_member_calls':384,'context_nested_qb_calls':8,'source_hashes':build['source_hashes'],'artifact_hashes':{n:sha(root/n) for n in sorted(artifacts)},'harness_hashes':prior['harness_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],'browser_dom_fingerprint':proof['browser_dom_fingerprint'],'scope':proof['scope']}
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('Pinned12new routines;17unpromoted total;5Chromium suites,5510cases12515calls')
