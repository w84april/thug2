# Windows x86 matching feasibility trial

Trial started 2026-10-12 17:12 UTC. The first comparison established eight
complete reconstructed C++ function matches within 16 minutes. The bounded trial
stops after verification and packaging; it does not start a continuing recovery
goal. The recovery chat subsequently read the complete diff and independently
replayed the private object, original bytes, compiler/source hashes and corruption
controls. [selection.json](selection.json) now accepts the eight matches into
the shared report, with fail-closed metadata validation. Behavioral completion
and its original denominator remain unchanged. This is a separate source
representation for native matching.
Verification and packaging took approximately 25 minutes of engaged session
time, including compiler setup and tool waits. A separate hands-on/CPU timer was
not available. The model/effort reported by the manager was gpt-6.1-sol/xhigh.

## Result

**406 original body bytes match across eight functions (0.01709% of 2,375,378).**
Five functions have raw COFF byte equality, totaling **189 bytes**. Three checksum
functions require normal COFF address resolution, totaling **217 bytes**. Every
byte after that resolution equals the original; no instructions or operands are
masked. These are individual functions, not a linked executable or playable game.
These counts are now integrated into the shared reporting system. Public CI
validates the hashed proof and deterministic report; it does not run the private
compiler or repeat the original-byte comparison.

| Recovered function | Address | Bytes | Proof |
|---|---|---:|---|
| `thug_crc32_buffer` | `00401aa0` | 71 | DIR32 at body offset 48 |
| `thug_crc32_extend_buffer` | `00401af0` | 55 | DIR32 at body offset 37 |
| `thug_crc32_normalized_buffer` | `00401b30` | 91 | DIR32 at body offset 68 |
| `thug_vector_copy` | `00402320` | 31 | Raw equality |
| `thug_vector_add` | `00402340` | 42 | Raw equality |
| `thug_vector_subtract` | `00406050` | 42 | Raw equality |
| `thug_vector_scale` | `00402370` | 43 | Raw equality |
| `thug_vector_length_squared` | `004023a0` | 31 | Raw equality |

`thug_crc32_string` at `00401b90` and `thug_crc32_extend_string` at `00401be0`
remain mismatched: compiled sizes 72/75 versus original sizes 73/78, first byte
differences at offsets 16/1. Both earn zero bytes. Their behavior is retained;
source/optimizer representation still needs work.

[proof.json](proof.json) pins source, compiler files, reference, object, inventory,
and per-function hashes, including both mismatches. [manifest.json](manifest.json)
maps the trial symbols to original addresses. Original bodies must equal the
complete contiguous spans in `progress/function-inventory.tsv`; shortened claims,
duplicates and overlaps are rejected. Inter-function padding earns no credit.
Alignment instructions inside a body are compared exactly.

## Compiler and environment evidence

The supplied modified/unpacked reference is pinned by `tools/specimen.py`:
`52fc88849654b34839ec2f96bff3a8c0b7a855df9a207aab9f2fca2e6bd440f3`.
Its PE machine is i386 (`014c`), image base `00400000`, linker version 7.10.
Its Rich records include tool 96/build 3077 with count 483, and tool 95/build
3077 with count 228, alongside older library/tool records. The freshly compiled
C++ object independently records `@comp.id = 00600c05`: tool 96/build 3077.
The running compiler banner identifies **13.10.3077 for 80x86**. This establishes
a compiler that reproduces these functions; it does not identify every library
compiler or prove the exact project-wide command line.

The compiler came from Microsoft Visual C++ Toolkit 2003 **1.01**. Its bundled
release notes identify the compiler files as the VS .NET 2003 Professional files.
Microsoft's [toolkit announcement](https://devblogs.microsoft.com/buckh/download-the-vc-toolkit/)
documents the free optimizing compiler. The installer was retrieved from the
[university mirror](https://www.lysator.liu.se/~andro/exjobb/extras-win32/).
The archive SHA-256 and extracted compiler hashes are in `proof.json`.
The embedded PKCS#7 signature verifies mathematically, and its signed SHA-1
equals an independently calculated Authenticode PE digest. The signer certificate
identifies Microsoft Corporation. Current independent certificate trust and
revocation were not established.

Installer files were extracted using the documented format in the open-source
[ISx extractor](https://github.com/lifenjoiner/ISx), then the embedded MSI's
`Data1.cab` using official 7-Zip 23.01. Compiler and archive files remain private
under `.tools/matching/`, including the supplied license. No game executable was
run, served, modified or copied into the worktree.

The host is an ARM64 Mac. The existing Game Porting Toolkit Wine 7.7 runner hung
on these 32-bit tools. The working runner is
[Wine 11.0_1](https://github.com/Gcenx/macOS_Wine_builds/releases/tag/11.0_1),
with its published archive SHA-256 verified before extraction. Wine and both
prefixes are worktree-local. An initial bundled-launcher version check created
`~/.wine`; its creation was observed, and that new trial directory was moved into
`.tools/matching/wine-prefix`. No pre-existing Wine prefix was moved or deleted.

The supported baseline is `/c /O2 /Gy`, default x86 target and default signed
`char`. Checksums use `__cdecl`; the vector representation restores MSVC
`__thiscall`, with the receiver in ECX, stack arguments and callee argument
cleanup. The generated vector arithmetic uses x87. This preserves the recovered
lane ordering, raw copy behavior and original caller-controlled precision; no
host floating-point approximation helper is substituted in these matched bodies.

| Setting control (with `/c /Gy`) | Matching bytes |
|---|---:|
| `/O2` | 406 |
| `/Ox` | 406 |
| `/O1` | 189 |
| `/O2 /Oy-` | 31 |
| `/O2 /G7` | 189 |

The controls support an optimization/target family, with frame-pointer omission
on relevant routines. `/O2` and `/Ox` are indistinguishable here. Runtime-library,
exception, structure-packing, whole-program and other project-wide settings
remain unresolved. An early `/GS-` probe was rejected by this compiler's option
parser; that option is absent from the final build. Final compilation is clean.
Microsoft documents the [optimization options](https://learn.microsoft.com/en-us/cpp/build/reference/o-options-optimize-code?view=msvc-170),
but the actual legacy compiler and controls determine this trial's result.

## Address resolution

The checksum table is declared external in the trial source. Each successful
checksum has exactly one emitted `IMAGE_REL_I386_DIR32` relocation, addend zero,
to `?crc_table@@3QBIB`. It resolves to independently identified data address
`0067c248`. All other bytes remain as emitted by the compiler. The comparator
implements normal DIR32/REL32 arithmetic; it does not zero either side or ignore
relocation bytes. No REL32 relocation is needed by the eight successful bodies.

The reconstructed table in `src/core/crc_table.inc` independently equals all
1,024 original table bytes, SHA-256
`12f3e0576d447eb37b36d82ba0c1c5481b8f0d12fdc70347ce4a076b229d4c86`.
This validates the target's identity; **no data-matching credit is claimed**.
The COFF object is resolved at original function addresses for comparison. A full
PE link, loader relocation and original executable layout are outside this trial.
Raw object equality is reported separately from resolved-byte equality.

## Reproduction

From this worktree on the trial Mac, with the private reference and extracted
compiler/runtime still present:

```sh
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=/Users/daniilpolienko/Documents/GitHub/thug/.tools/python:tools \
python3 tools/build_native_match.py \
  --wine '.tools/matching/wine11/Wine Stable.app/Contents/Resources/wine/bin/wine' \
  --compiler .tools/matching/vc2003/cl.exe \
  --prefix .tools/matching/wine11-prefix \
  --exe /Users/daniilpolienko/Documents/GitHub/thug/local/discs/cd3/Crack/THUG2.exe \
  --out local/matching-trial/reproduction

PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=/Users/daniilpolienko/Documents/GitHub/thug/.tools/python:tools \
python3 tools/test_native_match.py \
  --exe /Users/daniilpolienko/Documents/GitHub/thug/local/discs/cd3/Crack/THUG2.exe \
  --object local/matching-trial/reproduction/functions.obj

python3 tools/test_progress_report.py
python3 tools/generate_progress_report.py --check
```

Expected native output: `406 exact bytes after relocation; 189 raw object bytes`.
The build wrapper clears inherited compiler option/include/library variables,
records the command, source/manifest/compiler/runner hashes and object compiler
record, and refuses to reuse an object after a failed compile. Outputs are private
in the selected worktree directory. Use another output directory to preserve
separate runs. A fresh clone needs privately acquired compiler/runtime files and
the pinned reference; `pefile` is already pinned in `tools/requirements.txt`.

`tools/native_match.py` can also compare an existing object with explicit
`--exe`, `--object`, `--manifest` and `--output` paths. The public corruption test
runs without the reference; its optional local mode replays the real proof.
An altered vector opcode loses its full 31-byte claim; an incorrect table target
loses all 217 checksum bytes; shortened and duplicate claims fail. Synthetic
DIR32/REL32, unresolved/unsupported relocations and truncated objects are checked.
At the isolated trial checkpoint, the public report tests passed with 2,013
behavioral addresses and zero shared matching credit. The later coordinated
integration credits these eight native matches without changing gameplay source,
behavioral completion or the denominator. The original proof snapshot is retained.

Final private evidence is in `local/matching-trial/final/{build,report}.json` and
`compile.log`; earlier/repeated comparisons and option controls remain in the
same trial tree. Object timestamps can change full-object hashes between builds;
the emitted function bytes and all eight equality results reproduced unchanged.

## Recommendation

The native matching route is feasible. The shared validator now accepts only
the selected, hashed positive proof and rejects altered identities, sizes,
relocation targets, unequal bodies, duplicate claims and fabricated report credit.
The native worker remains stopped; expansion needs its separate authorization.

The 0.5% threshold requires **11,877 bytes**. This trial supplies 406 candidate
bytes, leaving **11,471** after their acceptance. Continue with recovered vector,
matrix and other self-contained helpers under this compiler, then test larger
recovered checksum/codec/table routines. The restored member conventions already
worked for five vector methods, so they are the best evidenced next source family.
Do not infer that another 11.5 KB will match at the same rate: the two string
checksums already show source-shape differences, and larger functions introduce
calls, layout, global data and compiler settings not resolved here. No compiler
availability blocker remains on this Mac.

The account-wide usage snapshots stayed at 95% of the weekly allowance during
the trial; the returned credit balance was unchanged. These coarse account
snapshots do not measure this chat's token use or monetary cost. Per-chat billing
and token totals were unavailable; no monetary estimate is provided.
