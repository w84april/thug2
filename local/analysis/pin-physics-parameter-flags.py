"""Pin the five-command experiment after its Chromium proof and main integration."""
import hashlib,json
from pathlib import Path
root=Path.cwd();folder=root/'local/analysis';target=folder/'physics-parameter-flags-checkpoint.json'
assert not target.exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((folder/n).read_text())
proof=read('physics-parameter-flags-browser.json');candidate=read('physics-parameter-flags-browser-candidate.json')
build=read('physics-parameter-flags-draft.build.json')
assert all(proof[k]==v for k,v in candidate.items())
canonical=json.dumps(candidate,ensure_ascii=False,sort_keys=True,separators=(',',':'));h=14695981039346656037
for c in canonical:h=((h^ord(c))*1099511628211)&((1<<64)-1)
assert f'{h:016x}'==proof['browser_dom_fingerprint']['value']=='e3753724c0e9d135' and len(canonical)==2814
assert proof['wasm_sha256']==build['sha256']==sha(folder/'physics-parameter-flags-draft.wasm')=='704a2fa08330c62cf37b6aaee4ad7d6fbeb6a2ab6913abeaadaac2ec4899a17f'
assert (proof['wasm_bytes'],proof['runtime_imports'])==(486073,0)
for n,v in {**build['source_hashes'],**build['draft_source_hashes']}.items():assert sha(root/n)==v,n
direct=read('physics-parameter-flags-original.json');context=read('physics-parameter-flags-context-original.json')
assert (direct['cases'],direct['calls'])==(2377,4754)
assert len(direct['instruction_coverage'])==5 and sum(v['covered'] for v in direct['instruction_coverage'].values())==79
assert all(v['total']==v['covered'] and not v['missing'] for v in direct['instruction_coverage'].values())
assert (context['cases'],context['calls'])==(12,72)
assert len(context['member_calls'])==5 and set(context['member_calls'].values())=={12}
for n,r in candidate['suites'].items():assert r==read(n.replace('_','-')+'-result.json') and r['result']=='pass' and r['nan_fields_classification_only']==0
assert sum(v['cases'] for v in candidate['suites'].values())==2401 and sum(v['calls'] for v in candidate['suites'].values())==4898
main=json.loads((root/'local/validation/collision-browser.json').read_text())
assert main['source_hashes']==build['source_hashes'] and len(main['source_hashes'])==207
assert main['wasm_sha256']==sha(root/'local/build/thug-core.wasm')=='8d1341809131c6f76b676e8aa330151fac7c25b774a8d31074b01df2e266fed0'
assert main['browser_dom_fingerprint']['value']=='835a35d106e46c62' and len(main['oracle_reports'])==160
artifacts=set(main['artifact_hashes'])
artifacts.update(['local/build/thug-core.wasm','local/build/thug-core.json','local/validation/collision-browser.json'])
for n,v in main['artifact_hashes'].items():assert sha(root/n)==v,n
names=['physics-parameter-flags-draft.c','physics-parameter-flags-draft.wasm','physics-parameter-flags-draft.build.json','build-physics-parameter-flags-draft.py','probe-physics-parameter-flags.py','verify-physics-parameter-flags.mjs','physics-parameter-flags-original.json','physics-parameter-flags-result.json','probe-physics-parameter-flags-context.py','verify-physics-parameter-flags-context.mjs','physics-parameter-flags-context-original.json','physics-parameter-flags-context-result.json','physics-parameter-flags-browser.html','serve-physics-parameter-flags.py','physics-commands-worker.mjs','physics-parameter-flags-browser.json','physics-parameter-flags-browser-candidate.json','pin-physics-parameter-flags.py','physics-command-integration-status.json']
artifacts.update('local/analysis/'+n for n in names)
for n in ['physics-parameter-flags','physics-parameter-flags-context']:
 p=folder/(n+'-fixtures.json');artifacts.add(str(p.relative_to(root)));fixture=json.loads(p.read_text())
 artifacts.add('local/analysis/'+fixture['memory'])
 dependencies={row['module'] for row in fixture.get('native_callbacks',[])}
 if fixture.get('memory_fixture'):dependencies.add(fixture['memory_fixture'])
 for filename in dependencies:
  p=folder/filename
  if not p.exists():p=root/'local/validation/collision'/filename
  artifacts.add(str(p.relative_to(root)))
checkpoint={'result':'isolated original, Node and Chromium pass; five routines not yet in main counts','new_functions':5,'specimen_sha256':direct['specimen_sha256'],'wasm_sha256':proof['wasm_sha256'],'main_wasm_sha256':main['wasm_sha256'],'direct_cases':2377,'direct_calls':4754,'context_original_cases':12,'context_wasm_cases':24,'context_wasm_calls':144,'context_member_observations':120,'instruction_coverage':direct['instruction_coverage'],'browser_dom_fingerprint':proof['browser_dom_fingerprint'],'scope':direct['scope'],'context_scope':context['scope'],'source_hashes':build['source_hashes'],'artifact_hashes':{n:sha(root/n) for n in sorted(artifacts)},'harness_hashes':{str(p.relative_to(root)):sha(p) for p in sorted((root/'tools').glob('*.py'))},'checker_dependency_hashes':{'tools/script_state_wasm_checks.mjs':sha(root/'tools/script_state_wasm_checks.mjs')}}
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('Pinned five additional commands; 79original instructions; two Chromium suites,2401cases/4898calls')
