"""Compare the complete release-input matcher against original instructions."""
from pathlib import Path

prefix = Path(__file__).with_name('verify_trick_input.py').read_text().split('for key in DIRECTIONS+')[0]
prefix = prefix.replace("report_path=out.parent/'trick-input.json'",
                        "report_path=out.parent/'release-input.json'")
exec(compile(prefix, '<existing input history arena>', 'exec'))
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
from specimen import load

functions.clear()
bind(0x51fb90, 'thug_skater_match_release_input', 3)
oracle.cpu.hook_add(UC_HOOK_CODE, oracle.observe, begin=0x51fb90, end=0x51fb90)
instruction_hits = Counter()
def trace(cpu, at, size, user):
    instruction_hits[at] += 1
oracle.cpu.hook_add(UC_HOOK_CODE, trace, begin=0x51fb90, end=0x51fd99)

keys = [0x20689278, 0x2b489a86, 0x321c9756, K[0], 0, 0xffffffff]
for key, alternate, commit, head in itertools.product(
        keys, [0, 1, 0x100, 0x101, 0xffffffff], [0, 1, 0x100, 0x101], [0, 99]):
    rows = [row(key, 2), row(key), row(key)]
    stages = case([call(0x51fb90, [key, alternate, commit])], history(rows, head),
                  label='mode and commit low bytes, raw matched arguments, allowed keys')
    expected = not (alternate & 255) or key in keys[:3]
    assert stages[0]['result'] == int(expected)

for alternate, length, head in itertools.product([0, 1], range(4), [0, 1, 50, 99]):
    rows = [row(keys[0], 2), row(keys[0]), row(keys[0])][:length]
    case([call(0x51fb90, [keys[0], alternate, 1])], history(rows, head),
         label='partial patterns preserve marks and wrap the history ring')
for alternate, position, extra in itertools.product([0, 1], range(4), [
        row(77), row(77, 2), row(keys[0], 3), row(keys[0], mask=1),
        row(keys[0], 2, mask=0xffffffff), row(77, 0, marked=255)]):
    rows = [row(keys[0], 2), row(keys[0]), row(keys[0])]
    rows.insert(position, extra)
    case([call(0x51fb90, [keys[0], alternate, 1])], history(rows),
         label='skip unrelated records, preserve preexisting marks on commit')
for alternate, position, age in itertools.product([0, 1], range(3),
                                                 [0, 999, 1000, 1001, 0x80000000, 0xffffffff]):
    rows = [row(keys[0], 2), row(keys[0]), row(keys[0])]
    old = rows[position]
    rows[position] = (*old[:3], age, old[4])
    case([call(0x51fb90, [keys[0], alternate, 1])], history(rows),
         label='unsigned strict age cutoff, including partial-match expiry')
for now, alternate, commit in itertools.product([0, 1, 0x7fffffff, 0x80000000, 0xffffffff],
                                               [0, 1], [0, 1]):
    rows = [row(keys[0], 2), row(keys[0], age=1), row(keys[0], age=999)]
    case([call(0x51fb90, [keys[0], alternate, commit]) for _ in range(2)],
         history(rows, now=now), {0: now}, label='wrapped clock and repeated matches')
for head, alternate, commit in itertools.product([0, 1, 50, 99], [0, 1], [0, 1]):
    rows = [row(77, 3, marked=i % 2) for i in range(97)]
    rows += [row(keys[0], 2), row(keys[0]), row(keys[0])]
    case([call(0x51fb90, [keys[0], alternate, commit])], history(rows, head),
         label='complete 100-entry ring and mark commits outside matched records')
for index in range(120):
    key = rng.choice(keys)
    rows = [row(rng.choice(keys), rng.choice([0, 1, 2, 3]), rng.choice([0, 0, 1]),
                rng.choice([0, 999, 1000]), rng.choice([0, 1, 255]))
            for _ in range(rng.randrange(20))]
    case([call(0x51fb90, [key, rng.choice([0, 1, 255]), rng.choice([0, 1, 255])])],
         history(rows, rng.randrange(100)), label=f'seeded mixed history {index}')

instructions = {i.address for i in Cs(CS_ARCH_X86, CS_MODE_32).disasm(
    load().get_data(0x51fb90 - 0x400000, 524), 0x51fb90)}
assert set(instruction_hits)==instructions
scope = ('Complete 0051fb90 release-input matcher through original timing, mark '
         'commit and matched-argument helpers. Exact full-arena and global comparisons; '
         'valid 100-entry history rings are an internal contract. Integrated with the main browser build; not the complete movement dispatcher.')
fixture = {'base': BASE, 'memory': 'release-input-memory.bin', 'memory_adapter': ADAPTER,
           'memory_fixture': 'script-values-memory.wasm',
           'memory_exports': ['fixture_values_allocate', 'fixture_values_release', 'fixture_values_scope'],
           'globals': globals_, 'functions': functions, 'float_fields': [],
           'cases': oracle.cases, 'case_labels': labels, 'scope': scope}
path = out / 'release-input-fixtures.json'
path.write_text(json.dumps(fixture, separators=(',', ':')))
(out / fixture['memory']).write_bytes(initial)
report = {'result': 'original pass; Wasm comparison pending', 'specimen_sha256': SHA256,
          'cases': len(labels), 'counts': dict(oracle.counts), 'callee_coverage': dict(oracle.coverage),
          'parent_instructions': len(instructions), 'parent_instructions_executed': len(instruction_hits),
          'missing_instructions': [hex(at) for at in sorted(instructions - set(instruction_hits))], 'scope': scope}
report_path.write_text(json.dumps(report, indent=2) + '\n')
print('Original release input:', len(labels), dict(oracle.counts), report['missing_instructions'], flush=True)
subprocess.run(['node', str(ROOT / 'tools/verify_release_input_wasm.mjs'), str(out)], check=True)
report['result'] = 'pass'
report['wasm_sha256'] = hashlib.sha256((ROOT / 'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['artifact_hashes'] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [path, out / fixture['memory']]}
report['source_hashes'] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}
report_path.write_text(json.dumps(report, indent=2) + '\n')
print('PASS release input', len(labels), sum(oracle.counts.values()), flush=True)
