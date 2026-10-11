"""Build the recovered engine subset as a freestanding wasm32 library."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SDK = ROOT / ".tools/wasi-sdk-34.0-arm64-macos"
output = ROOT / "local/build/thug-core.wasm"
output.parent.mkdir(parents=True, exist_ok=True)
sources = sorted((ROOT / "src").rglob("*.c"))
math_library = SDK / "share/wasi-sysroot/lib/wasm32-wasip1/libc.a"
math_objects = []
# Link only the required math implementations and helpers. Linking the full SDK libc
# with --export-all also exposes WASI system services that this engine does not use.
for name in ("sin", "cos", "tan", "__sin", "__cos", "__tan", "__rem_pio2", "__rem_pio2_large", "scalbn", "atan", "atan2", "log2", "log2_data", "__math_invalid", "__math_divzero"):
    path = output.parent / (name + ".c.obj")
    path.write_bytes(subprocess.check_output([str(SDK / "bin/llvm-ar"), "p", str(math_library), name + ".c.obj"]))
    math_objects.append(path)
command = [str(SDK / "bin/clang"), "--target=wasm32-unknown-unknown",
           "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
           "-fno-builtin", "-ffp-contract=off", "-nostdlib",
           "-Wl,--no-entry,--export-all,--export-memory,--export-table,--growable-table,--stack-first",
           "-Wl,-z,stack-size=1048576,--initial-memory=67108864,--max-memory=134217728",
           *map(str, sources), *map(str, math_objects), "-o", str(output)]
subprocess.run(command, check=True)
report = {"compiler": subprocess.check_output([str(SDK / "bin/clang"), "--version"], text=True),
          "command": command, "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
          "static_math_library_sha256": hashlib.sha256(math_library.read_bytes()).hexdigest(),
          "static_math_object_hashes": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in math_objects},
          "source_hashes": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in sorted((ROOT / "src").rglob("*")) if p.is_file() and p.name != ".DS_Store"},
          "scope": "Recovered engine subset only; no game entry point or rendering yet"}
output.with_suffix(".json").write_text(json.dumps(report, indent=2) + "\n")
print(str(output.relative_to(ROOT)), output.stat().st_size, "bytes")
