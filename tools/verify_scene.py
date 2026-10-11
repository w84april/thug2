"""Differential scene-query checks. Grids/caches are test fixtures, not a recovered loader."""
import hashlib
import json
import random
import struct
import subprocess
from collections import Counter

from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_ECX, UC_X86_REG_EIP, UC_X86_REG_ESP, UC_X86_REG_FPCW
from specimen import ROOT, SHA256, load

out = ROOT / "local/validation/collision"
report_path = out.parent / "scene.json"
report_path.unlink(missing_ok=True)
data = (out / "training-relocated.bin").read_bytes()
geometry = json.loads((out / "geometry-fixtures.json").read_text())
layout = json.loads((out / "fixtures.json").read_text())["datasets"][0]["layout"]
vertices, normals = [(out / name).read_bytes() for name in ("vertices.bin", "normals.bin")]
DATA, INSTANCES, GRID, LISTS, SCENES, NODES, CACHE = 0x1000000, 0x1100000, 0x1200000, 0x1300000, 0x1400000, 0x1402000, 0x1410000
SEGMENT, BOUNDS, RESULT, CONTROL, STATE, COUNT = 0x2000100, 0x2000180, 0x2000200, 0x2000400, 0x2000500, 0x2000600
STACK, STOP, CALLBACK = 0x3000000, 0x3f00000, 0x3f00100
SELECT, QUERY_STATE, GRID_OUTPUT, STAMP = 0x691910, 0x691968, 0x691998, 0x693998
SCENE_OUTPUT, GRID_SELECTION, SCENE_HEAD = 0x6fa738, 0x6fa778, 0x6fa7ec
pe = load()
cpu = Uc(UC_ARCH_X86, UC_MODE_32)
cpu.mem_map(0x400000, (pe.OPTIONAL_HEADER.SizeOfImage + 4095) & ~4095)
cpu.mem_write(0x400000, pe.get_memory_mapped_image())
for address, size in [(DATA, 0x500000), (0x2000000, 0x200000), (STACK, 0x20000), (STOP, 4096)]: cpu.mem_map(address, size)
cpu.mem_write(CALLBACK, b"\xc3")
cpu.mem_write(0x67c6b8, struct.pack("<2048H", *range(2048)))
fixture = {"addresses": {"data": DATA, "instances": INSTANCES, "grid": GRID, "scenes": SCENES,
                        "nodes": NODES, "cache": CACHE, "segment": SEGMENT, "bounds": BOUNDS,
                        "result": RESULT, "control": CONTROL, "state": STATE, "count": COUNT,
                        "log": 0x2100000, "callback": CALLBACK}, "helpers": [], "datasets": []}
counts = Counter()
rng = random.Random(0x4188c0)
callback_results = []


def callback_hook(uc, address, size, context):
    pointer = struct.unpack("<I", uc.mem_read(uc.reg_read(UC_X86_REG_ESP) + 4, 4))[0]
    assert pointer == RESULT
    value = bytes(uc.mem_read(pointer, 80))
    callback_results.append(value)
    mode = struct.unpack("<I", uc.mem_read(CONTROL, 4))[0]
    if mode & 1:
        uc.mem_write(pointer, bytes(v ^ 0x5a if i < 0x3c or i >= 0x40 else v for i, v in enumerate(value)))
    if mode & 2: uc.mem_write(SELECT, bytes([uc.mem_read(SELECT, 1)[0] ^ 1]))


cpu.hook_add(UC_HOOK_CODE, callback_hook, begin=CALLBACK, end=CALLBACK)


def call(address, this, args, cleanup=0):
    stack = STACK + 0x18000
    cpu.mem_write(stack, struct.pack("<" + "I" * (len(args) + 1), STOP, *args))
    cpu.reg_write(UC_X86_REG_ESP, stack)
    cpu.reg_write(UC_X86_REG_ECX, this)
    cpu.reg_write(UC_X86_REG_FPCW, 0x007f)
    cpu.emu_start(address, STOP, count=8000000)
    assert cpu.reg_read(UC_X86_REG_EIP) == STOP, hex(address)
    assert cpu.reg_read(UC_X86_REG_ESP) == stack + 4 + cleanup, hex(address)
    return cpu.reg_read(UC_X86_REG_EAX)


def f32(x): return struct.unpack("<f", struct.pack("<f", x))[0]
def box(lower, upper): return struct.pack("<8f", *lower, 1, *upper, 1)

assert call(0x48c0b0, 0, []) == SCENE_OUTPUT


# Box helpers: real bounds, equal and disjoint boxes, and unordered comparisons.
boxes = [data[obj["object"] + 16:obj["object"] + 48] for obj in geometry["objects"]]
for index in range(1000):
    center = [rng.uniform(-10000, 10000) for _ in range(3)]
    boxes.append(box(center, [v + rng.uniform(0, 500) for v in center]))
base = box([-1, -1, -1], [1, 1, 1])
for offset in (0, 4, 8, 16, 20, 24):
    for bits in (0x7fc01234, 0x7f801234, 0x7f800000, 0xff800000):
        value = bytearray(base); struct.pack_into("<I", value, offset, bits); boxes.append(bytes(value))
for index, a in enumerate(boxes):
    for b in (a, boxes[(index * 37 + 17) % len(boxes)]):
        cpu.mem_write(SEGMENT, a)
        cpu.mem_write(BOUNDS, b)
        overlap = call(0x40b170, SEGMENT, [BOUNDS], 4) & 255
        contains = call(0x40b1d0, SEGMENT, [BOUNDS], 4) & 255
        fixture["helpers"].append({"a": a.hex(), "b": b.hex(), "overlap": overlap, "contains": contains})
    cpu.mem_write(BOUNDS, b"\xad" * 48)
    assert call(0x403410, BOUNDS, [SEGMENT], 4) == BOUNDS
    assert bytes(cpu.mem_read(BOUNDS + 32, 16)) == b"\xad" * 16
    fixture["helpers"][-1]["point_bounds"] = bytes(cpu.mem_read(BOUNDS, 32)).hex()


def make_dataset(name, synthetic=False):
    memory = bytearray(CACHE + 0x2000 - DATA)
    memory[:len(data)] = data
    real = geometry["objects"]
    number = 2080 if synthetic else len(real)
    boxes = [struct.unpack_from("<8f", data, o["object"] + 16) for o in real if o["faces"]]
    lower = [-100.0] * 3 if synthetic else [min(b[i] for b in boxes) - 1 for i in range(3)]
    upper = [100.0] * 3 if synthetic else [max(b[i + 4] for b in boxes) + 1 for i in range(3)]
    columns = rows = 2 if synthetic else 20
    width, depth = f32((upper[0] - lower[0]) / columns), f32((upper[2] - lower[2]) / rows)
    struct.pack_into("<8f2f2i", memory, GRID - DATA, *lower, 1, *upper, 1, width, depth, columns, rows)
    radii = DATA + layout["extra"]
    entries = []
    for index in range(number):
        obj = real[0] if synthetic else real[index]
        offset = obj["object"]
        ptr = INSTANCES + index * 24
        struct.pack_into("<5I", memory, ptr - DATA, 0x645c18, struct.unpack_from("<I", data, offset)[0], 0, DATA + offset, radii)
        memory[ptr - DATA + 20:ptr - DATA + 24] = data[offset + 60:offset + 64]
        entries.append({"pointer": ptr, "geometry": DATA + offset, "faces": obj["faces"]})
        if not synthetic and not data[offset + 10]: radii += obj["faces"]
    lists_at = LISTS
    for x in range(columns):
        for z in range(rows):
            if synthetic:
                indices = {(0, 0): list(range(120)) * 2, (0, 1): list(range(120, 2040)),
                           (1, 0): list(range(2000, 2080)), (1, 1): []}[x, z]
            else:
                x0, x1 = lower[0] + x * width, lower[0] + (x + 1) * width
                z0, z1 = lower[2] + z * depth, lower[2] + (z + 1) * depth
                indices = []
                for i, obj in enumerate(real):
                    b = struct.unpack_from("<8f", data, obj["object"] + 16)
                    if obj["faces"] and b[0] <= x1 and b[4] >= x0 and b[2] <= z1 and b[6] >= z0:
                        indices.append(i)
            cell = GRID - DATA + 0x30 + (x * 20 + z) * 0x30
            struct.pack_into("<iII", memory, cell + 0x24, len(indices), 0, lists_at)
            for i in indices:
                struct.pack_into("<I", memory, lists_at - DATA, INSTANCES + i * 24); lists_at += 4
    for i in range(20): struct.pack_into("<I", memory, SCENES - DATA + i * 0x100 + 0xd4, GRID)
    struct.pack_into("<4I", memory, NODES - DATA + 20 * 16, 0, 0xffffffff, 0, NODES + 20 * 16)
    result = {"name": name, "objects": entries, "cases": [], "lower": lower, "upper": upper}
    (out / (name + ".bin")).write_bytes(memory)
    cpu.mem_write(DATA, bytes(memory))
    return result


def check(dataset, kind, start, end, *, cache=False, scene_count=1, farthest=0,
          callback=-1, stamp=0, optional_count=True, patches=()):
    callback_results.clear()
    raw = struct.pack("<8f", *start, 1, *end, 1)
    start, end = struct.unpack("<8f", raw)[:3], struct.unpack("<8f", raw)[4:7]
    patches = list(patches)
    # Rebuild a valid sentinel-terminated scene list, including the empty-list case.
    links = bytearray(20 * 16)
    for i in range(20):
        next_node = NODES + (i + 1) * 16 if i + 1 < scene_count else NODES + 20 * 16
        struct.pack_into("<4I", links, i * 16, 0, SCENES + i * 0x100, 0, next_node)
    patches.append((NODES, bytes(links)))
    if cache:
        lower, upper = [[min(a, b) - 1 for a, b in zip(start, end)], [max(a, b) + 1 for a, b in zip(start, end)]]
        payload = bytearray(0xfcc)
        payload[:32] = box(lower, upper)
        candidates = []
        for obj in dataset["objects"]:
            b = struct.unpack("<8f", cpu.mem_read(obj["geometry"] + 16, 32))
            if all(lower[i] <= b[i + 4] and b[i] <= upper[i] for i in range(3)):
                candidates.append(obj)
        assert len(candidates) <= 500
        for i, obj in enumerate(candidates): struct.pack_into("<II", payload, 32 + i * 8, obj["pointer"], obj["geometry"] + 16)
        struct.pack_into("<i", payload, 0xfc4, len(candidates))
        if cache == "miss": payload[:32] = box([1e8] * 3, [1e8 + 32] * 3)
        elif cache == "empty": struct.pack_into("<i", payload, 0xfc4, 0)
        elif cache == "tight": payload[:32] = box([min(a, b) for a, b in zip(start, end)], [max(a, b) for a, b in zip(start, end)])
        patches.append((CACHE, bytes(payload)))
    for address, value in patches: cpu.mem_write(address, value)
    head = NODES if scene_count else NODES + 20 * 16
    cpu.mem_write(SCENE_HEAD, struct.pack("<I", head))
    for at, size in [(SCENE_OUTPUT, 64), (GRID_SELECTION, 64), (GRID_OUTPUT, 8192)]: cpu.mem_write(at, b"\xad" * size)
    cpu.mem_write(STAMP, bytes([stamp]))
    cpu.mem_write(SELECT, bytes([farthest]))
    cpu.mem_write(SEGMENT, raw)
    cpu.mem_write(COUNT, b"\xad" * 4)
    state = struct.pack("<3I", 0x12345678, 0xabcdef01, 0x13579bdf)
    cpu.mem_write(QUERY_STATE, state)
    cpu.mem_write(CONTROL, struct.pack("<I", max(callback, 0)))
    prior = bytearray((i * 17 + 3) & 255 for i in range(80))
    struct.pack_into("<8fIfHH", prior, 0, 1, 2, 3, 4, 5, 6, 7, 8, 0x12345678, 0.5, 0, 0)
    struct.pack_into("<I", prior, 0x3c, 0)
    cpu.mem_write(RESULT - 16, b"\xad" * 16 + bytes(prior) + b"\xad" * 16)
    pointer = CALLBACK if callback >= 0 else 0
    if kind == "grid": returned = call(0x4188c0, GRID, [SEGMENT, COUNT if optional_count else 0], 8)
    elif kind == "scenes": returned = call(0x48c980, 0, [SEGMENT])
    else: returned = call(0x410930 if kind == "farthest" else 0x4106c0, 0,
                          [SEGMENT, RESULT, pointer, CACHE if cache else 0]) & 255
    assert bytes(cpu.mem_read(SEGMENT, 32)) == raw
    assert bytes(cpu.mem_read(RESULT - 16, 16)) == b"\xad" * 16
    assert bytes(cpu.mem_read(RESULT + 80, 16)) == b"\xad" * 16
    if kind == "grid": assert returned == GRID_OUTPUT
    elif kind == "scenes": assert returned in (0, GRID_SELECTION)
    else: assert returned in (0, 1)
    item = {"kind": kind, "segment": raw.hex(), "patches": [(a, b.hex()) for a, b in patches],
            "head": head, "cache": cache, "farthest": farthest, "callback_mode": callback,
            "stamp": stamp, "optional_count": optional_count, "initial": prior.hex(), "initial_state": state.hex(),
            "returned": returned, "result": bytes(cpu.mem_read(RESULT, 80)).hex(),
            "count": bytes(cpu.mem_read(COUNT, 4)).hex(), "state": bytes(cpu.mem_read(QUERY_STATE, 12)).hex(),
            "scene_output": bytes(cpu.mem_read(SCENE_OUTPUT, 64)).hex(),
            "grid_selection": bytes(cpu.mem_read(GRID_SELECTION, 64)).hex(),
            "grid_output": bytes(cpu.mem_read(GRID_OUTPUT, 8192)).hex(),
            "final_stamp": cpu.mem_read(STAMP, 1)[0], "final_farthest": cpu.mem_read(SELECT, 1)[0],
            "stamps": bytes(cpu.mem_read(o["pointer"] + 10, 1)[0] for o in dataset["objects"]).hex(),
            "callbacks": b"".join(callback_results).hex()}
    dataset["cases"].append(item)
    counts[kind] += 1
    if cache: counts["cached"] += 1
    counts["callbacks"] += len(callback_results)


training = make_dataset("scene-training")
for index, obj in enumerate(geometry["objects"]):
    if not obj["faces"]: continue
    offset = obj["object"]
    face = struct.unpack_from("<I", data, offset + 12)[0] - DATA
    indices = struct.unpack_from("<3B" if data[offset + 10] else "<3H", data, face + 4)
    points = [struct.unpack_from("<3f", vertices, obj["vertex_start"] + i * 16) for i in indices]
    center = [sum(p[a] for p in points) / 3 for a in range(3)]
    normal = struct.unpack_from("<3f", normals, obj["normal_start"])
    start, end = [[center[i] + normal[i] * distance for i in range(3)] for distance in (64, -64)]
    mode = 2 if index % 7 == 0 else 0 if index % 3 == 0 else -1
    check(training, "scene", start, end, callback=mode, stamp=index % 256)
    if index % 5 == 0:
        check(training, "scene", start, end, cache=True, callback=mode)
        check(training, "farthest", start, end, callback=mode, farthest=255)
    if index < 5:
        for cache_mode in ("miss", "empty", "tight"):
            check(training, "scene", start, end, cache=cache_mode, callback=1)
    if index % 100 == 0: print("training object", index, dict(counts), flush=True)
lo, hi = training["lower"], training["upper"]
for n in (0, 1, 14, 15, 16, 20):
    for start, end in [(lo, hi), ([1e8] * 3, [1e8 + 32] * 3)]:
        check(training, "scenes", start, end, scene_count=n)
check(training, "scene", [1e8] * 3, [1e8 + 32] * 3, callback=0)
check(training, "scene", lo, hi, scene_count=0)
# Null scene collision pointer is skipped; no match preserves the output arrays.
check(training, "scenes", lo, hi, patches=[(SCENES + 0xd4, b"\0" * 4)])
fixture["datasets"].append(training)
(out / "scene-training-after.bin").write_bytes(cpu.mem_read(DATA, CACHE + 0x2000 - DATA))

synthetic = make_dataset("scene-synthetic", True)
for index in range(300):
    start = [rng.uniform(-250, 250) for _ in range(3)]
    end = start if index % 3 == 0 else [rng.uniform(-250, 250) for _ in range(3)]
    check(synthetic, "grid", start, end, stamp=index % 256, optional_count=index % 2 == 0)
for stamp in (0, 1, 254, 255):
    tags = [(o["pointer"] + 10, bytes([(stamp + 1) & 255 if i % 5 == 0 else stamp])) for i, o in enumerate(synthetic["objects"])]
    check(synthetic, "grid", [-99, 0, -99], [99, 0, 99], stamp=stamp, patches=tags)
    flags = [(o["pointer"] + 8, bytes([2 if i % 3 == 0 else 4 if i % 3 == 1 else 0])) for i, o in enumerate(synthetic["objects"])]
    check(synthetic, "grid", [-99, 0, -99], [-50, 0, -50], stamp=stamp, patches=flags)
for delta in (-0.50001, -0.5, -0.49999, -0.0, 0, 0.49999, 0.5, 0.50001):
    check(synthetic, "grid", [delta, 0, -50], [delta, 0, 50], stamp=254)
for offset in (-0.00001, 0, 0.00001):
    check(synthetic, "grid", [-20, 0, -50], [-0.5 + offset, 0, -50], stamp=255)
    check(synthetic, "grid", [-50, 0, -20], [-50, 0, -0.5 + offset], stamp=255)
fixture["datasets"].append(synthetic)
(out / "scene-synthetic-after.bin").write_bytes(cpu.mem_read(DATA, CACHE + 0x2000 - DATA))
grid_counts = [bytes.fromhex(c["grid_output"]).find(b"\0\0\0\0") // 4 for c in synthetic["cases"]]
assert 2047 in grid_counts, "Candidate cap must be exercised"

fixture_path = out / "scene-fixtures.json"
fixture_path.write_text(json.dumps(fixture, separators=(",", ":")))
subprocess.run(["node", str(ROOT / "tools/verify_scene_wasm.mjs"), str(out)], check=True)
report = {"result": "pass", "specimen_sha256": SHA256, "counts": dict(counts),
          "box_comparisons": len(fixture["helpers"]) * 2, "point_bounds_cases": len(boxes),
          "scope": "Recovered queries on constructed scene grids/caches containing real training geometry; the original grid/cache builders and loader are not yet recovered.",
          "x87_control_word": "0x007f", "runtime_control_word_observed_in_game": False,
          "wasm_sha256": hashlib.sha256((ROOT / "local/build/thug-core.wasm").read_bytes()).hexdigest(),
          "source_hashes": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in sorted((ROOT / "src").rglob("*")) if p.is_file()},
          "fixture_hashes": {name: hashlib.sha256((out / name).read_bytes()).hexdigest()
                             for name in ("scene-fixtures.json", "scene-training.bin", "scene-synthetic.bin",
                                          "scene-training-after.bin", "scene-synthetic-after.bin", "callback-fixture.wasm")},
          "byte_matching": "not attempted"}
report_path.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({"result": "pass", "counts": dict(counts)}, indent=2))
