"""Compare recovered rigid moving collision with original x86 instructions.

Transforms are constructed test inputs applied to every training collision object.
Only hit callbacks are instrumented; constructors, coordinate transforms, radius
rejection, BSP/triangle queries, normals and result selection all execute in x86.
"""
import hashlib
import json
import math
import random
import struct
import subprocess
from collections import Counter
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_ECX, UC_X86_REG_EIP, UC_X86_REG_ESP, UC_X86_REG_FPCW
from specimen import ROOT, SHA256, load

out = ROOT / 'local/validation/collision'
report_path = out.parent / 'moving.json'
report_path.unlink(missing_ok=True)
data = (out / 'training-relocated.bin').read_bytes()
geometry = json.loads((out / 'geometry-fixtures.json').read_text())
vertices, normals = [(out / name).read_bytes() for name in ['vertices.bin', 'normals.bin']]
DATA, INSTANCE, SEGMENT, DELTA, BOUNDS, RESULT = 0x1000000, 0x2000000, 0x2000100, 0x2000140, 0x2000180, 0x2000200
CONTROL, STATE, MATRIX, VECTOR, OUTPUT, LOG = 0x2000400, 0x2000500, 0x2000800, 0x2000a00, 0x2000b00, 0x2100000
STACK, STOP, CALLBACK, SELECT, QUERY_STATE = 0x3000000, 0x3f00000, 0x3f00100, 0x691910, 0x691968
pe = load(); cpu = Uc(UC_ARCH_X86, UC_MODE_32)
cpu.mem_map(0x400000, (pe.OPTIONAL_HEADER.SizeOfImage + 4095) & ~4095)
cpu.mem_write(0x400000, pe.get_memory_mapped_image())
for at, size in [(0, 4096), (DATA, 0x200000), (INSTANCE, 0x200000), (STACK, 0x20000), (STOP, 4096)]: cpu.mem_map(at, size)
cpu.mem_write(DATA, data); cpu.mem_write(CALLBACK, b'\xc3')
cpu.mem_write(0x67c6b8, struct.pack('<2048H', *range(2048)))
fixture = {'addresses': {'data': DATA, 'instance': INSTANCE, 'segment': SEGMENT, 'delta': DELTA,
    'bounds': BOUNDS, 'result': RESULT, 'control': CONTROL, 'state': STATE, 'matrix': MATRIX,
    'vector': VECTOR, 'output': OUTPUT, 'log': LOG, 'callback': CALLBACK}, 'matrices': [], 'helpers': [], 'cases': []}
counts = Counter(); rng = random.Random(0x414460); callbacks = []


def word(at): return struct.unpack('<I', cpu.mem_read(at, 4))[0]
def raw(at, size): return bytes(cpu.mem_read(at, size))
def f32(n): return struct.unpack('<f', struct.pack('<f', n))[0]
def floats(values): return struct.pack('<' + 'f' * len(values), *values)


def call(fn, this=0, args=(), cleanup=0):
    sp = STACK + 0x18000
    cpu.mem_write(sp, struct.pack('<' + 'I' * (len(args) + 1), STOP, *args))
    cpu.reg_write(UC_X86_REG_ESP, sp); cpu.reg_write(UC_X86_REG_ECX, this); cpu.reg_write(UC_X86_REG_FPCW, 0x007f)
    cpu.emu_start(fn, STOP, count=2000000)
    assert cpu.reg_read(UC_X86_REG_EIP) == STOP, hex(fn)
    assert cpu.reg_read(UC_X86_REG_ESP) == sp + 4 + cleanup, hex(fn)
    return cpu.reg_read(UC_X86_REG_EAX)


def callback(uc, address, size, context):
    assert word(uc.reg_read(UC_X86_REG_ESP) + 4) == RESULT
    value = raw(RESULT, 80); callbacks.append(value)
    mode = word(CONTROL)
    if mode & 1:
        uc.mem_write(RESULT, bytes(byte ^ 0x5a if i < 0x3c or i >= 0x40 else byte for i, byte in enumerate(value)))
    if mode & 2: uc.mem_write(SELECT, bytes([raw(SELECT, 1)[0] ^ 1]))


cpu.hook_add(UC_HOOK_CODE, callback, begin=CALLBACK, end=CALLBACK)
identity = [float(i % 5 == 0) for i in range(16)]
for i in range(256):
    matrix = floats(identity if i == 0 else [rng.uniform(-10, 10) for _ in range(16)])
    vector = floats([rng.uniform(-10000, 10000) for _ in range(4)])
    cpu.mem_write(MATRIX, matrix); cpu.mem_write(VECTOR, vector + b'\xad' * 16); cpu.mem_write(OUTPUT, b'\xad' * 32)
    target = VECTOR if i % 2 else OUTPUT
    assert call(0x40b090, MATRIX, [target, VECTOR], 8) == target
    assert raw(target + 16, 16) == b'\xad' * 16 and raw(MATRIX, 64) == matrix
    fixture['matrices'].append({'matrix': matrix.hex(), 'input': vector.hex(), 'alias': bool(i % 2), 'output': raw(target, 16).hex()})


def matrix_for(index):
    # Orthonormal X/Y composition, rounded to the original float fields.
    x, y = (index % 13) * 0.17, (index % 19) * -0.23
    cx, sx, cy, sy = math.cos(x), math.sin(x), math.cos(y), math.sin(y)
    return [f32(v) for v in [cy, 0, -sy, 0, sy*sx, cx, cy*sx, 0, sy*cx, -sx, cy*cx, 0, 0, 0, 0, 1]]


def transformed(point, matrix, position):
    return [f32(f32(f32(f32(point[2]*matrix[8+i]) + f32(point[1]*matrix[4+i])) + f32(point[0]*matrix[i])) + position[i]) for i in range(3)]


for index, obj in enumerate(geometry['objects']):
    original = bytes(rng.randrange(256) for _ in range(0xd4))
    cpu.mem_write(INSTANCE, original + b'\xad' * 16)
    assert call(0x413000, INSTANCE, [DATA + obj['object']], 4) == INSTANCE
    assert word(0) == 0
    initialized = raw(INSTANCE, 0xd4)
    position = floats([125.25, -79.5, 31.75, (index % 3) - 1])
    matrix = floats(matrix_for(index))
    cpu.mem_write(VECTOR, position); cpu.mem_write(MATRIX, matrix)
    call(0x412f90, INSTANCE, [VECTOR], 4)
    assert call(0x412070, INSTANCE, [MATRIX], 4) == INSTANCE + 0x60
    call(0x40ae40, INSTANCE, [0x12345678], 4)
    assert call(0x40ae50, INSTANCE) == 0x12345678
    positioned = raw(INSTANCE, 0xd4)
    call(0x40b390, INSTANCE)
    updated = raw(INSTANCE, 0xd4)
    bounds = floats([-10, -10, -10, 7, 10, 10, 10, 9])
    cpu.mem_write(BOUNDS, bounds)
    overlap = call(0x411810, INSTANCE, [BOUNDS], 4) & 255
    final = raw(INSTANCE, 0xd4)
    assert raw(INSTANCE + 0xd4, 16) == b'\xad' * 16
    local_input = floats([rng.uniform(-10000, 10000) for _ in range(8)])
    cpu.mem_write(SEGMENT, local_input + b'\xad' * 16); cpu.mem_write(OUTPUT, b'\xad' * 48)
    target = SEGMENT if index % 2 else OUTPUT
    call(0x4122c0, INSTANCE, [SEGMENT, target], 8)
    assert raw(target + 32, 16) == b'\xad' * 16
    fixture['helpers'].append({'object': obj['object'], 'initial': original.hex(), 'initialized': initialized.hex(),
        'position': position.hex(), 'matrix': matrix.hex(), 'positioned': positioned.hex(), 'updated': updated.hex(),
        'bounds': bounds.hex(), 'overlap': overlap, 'final': final.hex(), 'local_input': local_input.hex(),
        'local_output': raw(target, 32).hex(), 'alias': bool(index % 2)})

    def check(start, end, transform, mode=-1, farthest=0, fraction=None, excluded=0, required=0, no_tree=False):
        callbacks.clear()
        mat = identity if transform == 0 else matrix_for(index + transform)
        pos = [0, 0, 0, 1] if transform == 0 else [125.25, -79.5, 31.75, 1]
        cpu.mem_write(INSTANCE, initialized)
        cpu.mem_write(VECTOR, floats(pos)); cpu.mem_write(MATRIX, floats(mat))
        call(0x412f90, INSTANCE, [VECTOR], 4); call(0x412070, INSTANCE, [MATRIX], 4)
        instance = raw(INSTANCE, 0xd4)
        start, end = [transformed(p, mat, pos) for p in [start, end]]
        segment = floats([*start, 1, *end, 1])
        # Poison ignored arguments to detect accidental dependence on them.
        cpu.mem_write(DELTA, b'\xad' * 16); cpu.mem_write(BOUNDS, b'\xad' * 32)
        prior = bytearray((i * 17 + 3) & 255 for i in range(80))
        struct.pack_into('<8fIfHH', prior, 0, 1,2,3,4,5,6,7,8,0x12345678,
                         (-0.01 if farthest else 1.01) if fraction is None else fraction, excluded, required)
        struct.pack_into('<I', prior, 0x3c, CALLBACK if mode >= 0 else 0)
        state = struct.pack('<3I', 0x12345678, 0xabcdef01, 0x13579bdf)
        cpu.mem_write(RESULT - 16, b'\xad' * 16 + bytes(prior) + b'\xad' * 16)
        cpu.mem_write(SEGMENT, segment); cpu.mem_write(QUERY_STATE, state)
        cpu.mem_write(SELECT, bytes([farthest])); cpu.mem_write(CONTROL, struct.pack('<I', max(0, mode)))
        tree_at = DATA + obj['object'] + 0x34; tree = raw(tree_at, 4)
        if no_tree: cpu.mem_write(tree_at, b'\0' * 4)
        returned = call(0x414460, INSTANCE, [SEGMENT, DELTA, RESULT, BOUNDS], 16) & 255
        cpu.mem_write(tree_at, tree)
        assert returned in (0,1)
        assert raw(RESULT - 16, 16) == raw(RESULT + 80, 16) == b'\xad' * 16
        assert raw(INSTANCE, 0xd4) == instance and raw(SEGMENT, 32) == segment
        assert raw(DELTA, 16) == b'\xad' * 16 and raw(BOUNDS, 32) == b'\xad' * 32
        fixture['cases'].append({'object': obj['object'], 'instance': instance.hex(), 'segment': segment.hex(),
            'initial': bytes(prior).hex(), 'callback_mode': mode, 'farthest': farthest, 'no_tree': no_tree,
            'initial_state': state.hex(), 'state': raw(QUERY_STATE, 12).hex(), 'returned': returned,
            'result': raw(RESULT, 80).hex(), 'callbacks': b''.join(callbacks).hex(), 'final_farthest': raw(SELECT, 1)[0]})
        counts['queries'] += 1; counts['hits'] += returned; counts['callbacks'] += len(callbacks)
        counts['fallback_queries'] += int(no_tree)
        if callbacks and not returned: counts['callbacks_without_selected_hit'] += 1

    if obj['faces']:
        face_base = struct.unpack_from('<I', data, obj['object'] + 12)[0] - DATA
        small = data[obj['object'] + 10]
        for face in sorted(set([0, obj['faces'] // 2, obj['faces'] - 1])):
            record = face_base + face * (8 if small else 10)
            indices = struct.unpack_from('<3B' if small else '<3H', data, record + 4)
            points = [struct.unpack_from('<3f', vertices, obj['vertex_start'] + vertex * 16) for vertex in indices]
            center = [sum(p[i] for p in points) / 3 for i in range(3)]
            normal = struct.unpack_from('<3f', normals, obj['normal_start'] + face * 16)
            front, back = [[center[i] + normal[i] * d for i in range(3)] for d in [64, -64]]
            for transform in range(3): check(front, back, transform, mode=transform-1, farthest=transform&1)
            check(back, front, 1, mode=2)
        check(front, back, 2, mode=3, fraction=0.1)
        check(front, back, 1, mode=0, excluded=0xffff)
        check(front, back, 1, mode=0, required=0xffff)
        check(front, back, 2, mode=0, no_tree=True)
        check(center, center, 1)
    else: check([0, 64, 0], [0, -64, 0], 1)
    check([100000, 100000, 100000], [100001, 100000, 100000], 1)
    if index % 100 == 0: print(index, 'objects;', dict(counts), flush=True)

assert raw(DATA, len(data)) == data
fixture_path = out / 'moving-fixtures.json'
fixture_path.write_text(json.dumps(fixture, separators=(',', ':')))
subprocess.run(['node', str(ROOT / 'tools/verify_moving_wasm.mjs'), str(out)], check=True)
report = {'result': 'pass', 'specimen_sha256': SHA256, 'counts': dict(counts),
    'constructors': len(fixture['helpers']), 'matrix_cases': len(fixture['matrices']),
    'x87_control_word': '0x007f', 'runtime_control_word_observed_in_game': False,
    'scope': 'Rigid moving collision on all training objects under constructed transforms; callbacks instrumented; no moving scene list or physics update yet.',
    'wasm_sha256': hashlib.sha256((ROOT / 'local/build/thug-core.wasm').read_bytes()).hexdigest(),
    'fixture_sha256': hashlib.sha256(fixture_path.read_bytes()).hexdigest(),
    'callback_sha256': hashlib.sha256((out / 'callback-fixture.wasm').read_bytes()).hexdigest(),
    'source_hashes': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT / 'src').rglob('*')) if p.is_file()},
    'byte_matching': 'not attempted'}
report_path.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'result': 'pass', 'counts': dict(counts)}, indent=2))
