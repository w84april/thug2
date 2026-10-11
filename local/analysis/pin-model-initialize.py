"""Pin the observed original, Node and Chromium model-initialization progress."""
import hashlib
import json
import sys
from pathlib import Path

r = Path.cwd()
p = r / 'local/analysis'
sha = lambda f: hashlib.sha256(f.read_bytes()).hexdigest()
read = lambda f: json.loads(f.read_text())
pin_path = p / 'model-initialize-checkpoint.json'
proof_path = p / 'model-initialize-browser.json'
assert not pin_path.exists() and not proof_path.exists()
prior_path = p / 'model-component-checkpoint.json'
assert sha(prior_path) == '13fa94c0ada61b967b61ed8864a9cd8a73ebe7cabdcbf0c5f88aae7e6bbe6612'
prior = read(prior_path)
for group in ['artifact_hashes', 'source_hashes', 'harness_hashes', 'checker_dependency_hashes']:
    for name, digest in prior[group].items():
        assert sha(r / name) == digest, (group, name)

build = read(p / 'model-initialize-draft.build.json')
module = p / 'model-initialize-draft.wasm'
assert build['source_hashes'] == prior['source_hashes']
for name, digest in {**build['source_hashes'], **build['draft_source_hashes'], **build['derived_from']}.items():
    assert sha(r / name) == digest, name
assert build['derived_from'] == {'local/analysis/model-component-draft.c': prior['artifact_hashes']['local/analysis/model-component-draft.c']}
assert sha(module) == build['sha256'] == 'e6ab0f3b8dc37fe952f14c165e1e5ead5bc085ef307466579d5ebc002e929fc6'
assert module.stat().st_size == 545127
names = ['model-initialize', 'model-initialize-prefix', 'training-model-initialize',
         'model-component', 'training-model-component', 'prop-command', 'training-prop-script',
         'prop-sound', 'training-prop-components', 'prop-lifecycle', 'composite-math',
         'composite-construction', 'node-registration', 'training-node-registration',
         'node-index', 'training-node-index', 'scene-kill', 'scene-subscribe', 'scene-lifetime',
         'scene-proximity', 'scene-state', 'scene-disposal', 'scene-visitor', 'training-mode',
         'node-prefix', 'scene-name', 'training-setup', 'asset-factory', 'training-load',
         'skeleton-asset', 'skeleton-buffer', 'script-change']
suites = {name.replace('-', '_'): read(p / ('model-initialize-checkpoint-' + name + '-result.json')) for name in names}
assert len(suites) == 32
for name in names:
    summary = suites[name.replace('-', '_')]
    assert summary['result'] == 'pass'
    if name not in names[:3]:
        assert summary == read(p / ('model-component-checkpoint-' + name + '-result.json')), name
for name, cases, calls in [('model_initialize', 127, 309), ('model_initialize_prefix', 36, 198), ('training_model_initialize', 2, 22)]:
    summary = suites[name]
    assert (summary['cases'], summary['calls'], summary['nan_fields_classification_only']) == (cases, calls, 0)
candidate = {'result': 'pass', 'wasm_sha256': sha(module), 'wasm_bytes': module.stat().st_size,
             'runtime_imports': 0, 'suites': suites}
canonical = json.dumps(candidate, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
fingerprint = 14695981039346656037
for char in canonical:
    fingerprint = ((fingerprint ^ ord(char)) * 1099511628211) & ((1 << 64) - 1)
assert sys.argv[1] == f'{fingerprint:016x}'
assert int(sys.argv[2]) == len(canonical) and int(sys.argv[3]) == len(candidate) == 5

original = read(p / 'model-initialize-original.json')
coverage = original['instruction_coverage']
assert (original['cases'], original['calls']) == (127, 309)
assert len(coverage) == 20
assert sum(item['covered'] for item in coverage.values()) == 314
assert sum(item['total'] for item in coverage.values()) == 324
for item in coverage.values():
    assert set(item['missing']) == set(item['excluded'])
prefix = read(p / 'model-initialize-prefix-original.json')
assert (prefix['cases'], prefix['calls']) == (36, 198)
assert prefix['instruction_coverage'] == {}
assert prefix['partial_initializer'] == {
    'address': '0x4214f0', 'covered_instructions': 69, 'total_instructions': 74,
    'not_reached': ['0x4215da', '0x4215db', '0x4215dc', '0x4215dd', '0x4215de'],
    'boundary': '0x420d10', 'interrupted_calls': 36,
}
training = read(p / 'training-model-initialize-original.json')
assert (training['cases'], training['calls']) == (2, 22)
assert training['nodes'][0]['execute_result'] == 0 and training['nodes'][0]['final_instruction'] == '0x0'
node = training['nodes'][1]
assert node['node_index'] == 1289 and node['first_missing_routine'] == '0x420d10'
assert node['completed_calls'] == 10 and node['interrupted_calls'] == 1
for address in ['0x421490', '0x420bf0', '0x48bfa0', '0x4b29c0', '0x4bad90', '0x494c40',
                '0x4214f0', '0x532eb0', '0x492e90']:
    assert node['native_entries'][address] == 1
assert node['model_state']['owner_components'] == ['0xce0ca665', '0xa015e17', '0x1d5b1ae6', '0x7713c7b', '0x286a8d26']
assert node['model_state']['renderer_flags'] == 2
assert node['model_state']['lights'] == node['model_state']['skeleton_data'] == '0x0'
assert original['specimen_sha256'] == prefix['specimen_sha256'] == training['specimen_sha256'] == prior['specimen_sha256']
scope = (
    'Twenty additional original routines recover lighting construction/destruction and array ownership, '
    'generic virtual deletion, ambient/directional flags, renderer skeleton binding and light propagation. '
    'The PC geometry light slot executes its real shared bare-RET4 implementation. The Model initializer '
    'is only partially recovered and is NOT counted among those20 routines. Its36 controlled cases cover '
    'all69 instructions through the call to420d10, including optional lighting creation/removal/retention, '
    'position/key assignment, absent/new/already-bound skeleton data and full-word optional flags. '
    'The five return-tail instructions cannot execute while configuration/loading420d10 remains unavailable. '
    'A test-only dependency breakpoint records actual arguments and traps without supplying a replacement '
    'configuration result. New165 cases529 calls include37 interrupted calls; all new arena/global/heap '
    'comparisons are exact with no NaN allowances. Full helper coverage314/324 has10 explicit allocator '
    'bootstrap, successful-allocation and unreachable-alignment exclusions. Lighting counts are bounded '
    'initialized fixture values; graphics startup remains unrecovered. All32 actual Chromium suites pass; '
    'all29 previous summaries are unchanged. Untouched training QB files register all1917nodes percase. '
    'Node204 still completes. Node1289 SKATE letter S executes actual Model construction, owner attachment '
    'and the initializer prefix, then reaches configuration/loading420d10. Direct and interpreter service '
    'scopes are checked at their respective traps. Full initialization, asset loading, drawing and gameplay '
    'remain incomplete; no rendered or playable level is claimed. Main and separate physics builds remain unchanged.'
)
proof = {**candidate, 'recorded_at': sys.argv[4],
         'observed_via': 'Actual Chromium PASS at ' + sys.argv[5] + '; all32 suite summaries and complete DOM fingerprint inspected',
         'browser_dom_fingerprint': {'algorithm': 'FNV-1a-64 over canonical sorted JSON characters',
                                     'value': sys.argv[1], 'characters': len(canonical)}, 'scope': scope}
files = [
    'model-initialize-draft.c', 'model-initialize-component-derived.c', 'model-initialize-draft.wasm',
    'model-initialize-draft.build.json', 'build-model-initialize-draft.py',
    'probe-model-initialize.py', 'model-initialize-fixtures.json', 'model-initialize-memory.bin',
    'model-initialize-original.json', 'model-initialize-probe.log', 'model-initialize-focus.tsv',
    'model-initialize-discovery.txt', 'model-initialize-instructions.txt', 'model-initialize-methods.json',
    'probe-model-initialize-prefix.py', 'model-initialize-prefix-fixtures.json', 'model-initialize-prefix-memory.bin',
    'model-initialize-prefix-original.json', 'model-initialize-prefix-probe.log',
    'model-initialize-prefix-boundary.c', 'model-initialize-prefix-boundary.wasm',
    'model-initialize-prefix-boundary.build.json', 'model-initialize-prefix-checks.mjs',
    'probe-training-model-initialize.py', 'training-model-initialize-fixtures.json',
    'training-model-initialize-memory.bin', 'training-model-initialize-original.json',
    'training-model-initialize-probe.log', 'training-model-initialize-boundary.c',
    'training-model-initialize-boundary.wasm', 'training-model-initialize-boundary.build.json',
    'verify-model-initialize-checkpoint.mjs', 'model-initialize-full-node.log',
    'model-initialize-browser.html', 'model-initialize-worker.mjs', 'serve-model-initialize.py',
    'model-initialize-browser.json', 'pin-model-initialize.py', 'audit-model-initialize.py',
]
files += ['model-initialize-checkpoint-' + name + '-result.json' for name in names]
files += ['model-initialize-ghidra.log'] + [str(f.relative_to(p)) for f in sorted((p / 'model-initialize-ghidra').rglob('*')) if f.is_file()]
for name in files:
    if name != 'model-initialize-browser.json':
        assert (p / name).is_file(), name
proof_path.write_text(json.dumps(proof, indent=2) + '\n')
artifacts = set(prior['artifact_hashes']) | {'local/analysis/model-component-checkpoint.json', 'local/analysis/model-component-audit.json'} | {'local/analysis/' + name for name in files}
pin = {'result': 'original, Node and actual Chromium comparisons pass; unpromoted',
       'new_functions': 20, 'original_addresses': list(coverage),
       'unpromoted_functions_in_this_module': 215, 'unpromoted_functions_across_separate_experiments': 232,
       'specimen_sha256': original['specimen_sha256'], 'wasm_sha256': sha(module),
       'wasm_bytes': module.stat().st_size, 'main_wasm_sha256': prior['main_wasm_sha256'],
       'browser_suites': 32, 'new_cases': 165, 'new_calls_including_existing_dependencies': 529,
       'new_interrupted_calls': 37, 'actual_training_model_initialize_cases': 2,
       'partial_initializer_not_counted_as_complete': prefix['partial_initializer'],
       'instruction_coverage': coverage, 'source_hashes': build['source_hashes'],
       'artifact_hashes': {name: sha(r / name) for name in sorted(artifacts)},
       'harness_hashes': prior['harness_hashes'], 'checker_dependency_hashes': prior['checker_dependency_hashes'],
       'browser_dom_fingerprint': proof['browser_dom_fingerprint'], 'scope': scope}
pin_path.write_text(json.dumps(pin, indent=2) + '\n')
assert sha(r / 'local/build/thug-core.wasm') == pin['main_wasm_sha256']
print(json.dumps({'result': 'pinned', 'artifacts': len(pin['artifact_hashes']),
                  'sources': len(pin['source_hashes']), 'checkpoint_sha256': sha(pin_path), 'main_unchanged': True}))
