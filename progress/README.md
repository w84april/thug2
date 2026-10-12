# Recovery reporting

This project recovers Windows x86 behavior for WebAssembly. It has **406 verified
native matching bytes across eight individual functions** and is not playable yet.
Behavioral completion and native binary matching have separate evidence.

## decomp.dev requirements checked on 2026-10-12

The public implementation at
[`encounter/decomp.dev`, revision `e9c086a`](https://github.com/encounter/decomp.dev/tree/e9c086adb74d2fe569541cd715cd9312d7641313)
supports the `win32` platform. It imports objdiff v2 reports from GitHub Actions
artifacts named `<version>_report` (or `<version>-report`). The archive must contain
`report.json`, `report.pb`, or an equivalent recognized report filename. It does
not accept an arbitrary progress JSON with a percentage field.

Registration requires a public GitHub repository, an authenticated repository
administrator, and an Actions workflow with a readable report artifact. The
GitHub App is an additional integration for automatic refresh and PR reporting.
Our repository is public. The user registered the project, and its
[decomp.dev page](https://decomp.dev/w84april/thug2) was independently checked in
the browser on 2026-10-12. It displayed commit `4adce8e`, 18.15% fully linked
completion and 0.00% decompiled (matching), confirming import of that report.

There is a material limitation: the current public listing hides projects below
**0.5% matched code**. Completion progress alone does not meet that threshold.
Our report can be format-compatible while the project remains hidden. We will
not turn recovery completion into matching credit to bypass that restriction.
Hosted import is verified for the displayed commit. Public listing visibility
remains unavailable while the matching threshold is unmet.

Authoritative implementation references:

- [Artifact discovery and parsing](https://github.com/encounter/decomp.dev/blob/e9c086adb74d2fe569541cd715cd9312d7641313/crates/github/src/lib.rs)
- [Registration checks](https://github.com/encounter/decomp.dev/blob/e9c086adb74d2fe569541cd715cd9312d7641313/crates/web/src/handlers/manage.rs)
- [Windows platform and visibility rule](https://github.com/encounter/decomp.dev/blob/e9c086adb74d2fe569541cd715cd9312d7641313/crates/core/src/models.rs)
- [objdiff report schema used by that revision](https://github.com/encounter/objdiff/blob/0c48d711c7bd51f791b353d7d85ba948b277e2f2/objdiff-core/protos/report.proto)
- [objdiff parser and version migration](https://github.com/encounter/objdiff/blob/0c48d711c7bd51f791b353d7d85ba948b277e2f2/objdiff-core/src/bindings/report.rs)

## Metric policy

`complete_code` will represent original code bytes attributed to recovered
functions with linked source and passing behavioral evidence. Matching credit
requires selected positive per-function native proof, complete original body
sizes and exact raw or declared-relocation-resolved bytes. The accepted proof
is [matching/selection.json](../matching/selection.json), which pins the immutable
[trial proof](../matching/proof.json), source, comparator and manifest hashes.
Five functions match raw COFF bytes (189 bytes); three checksum functions match
after DIR32 table address resolution (217 bytes). No instructions or operands are
masked. Two mismatches earn zero. No graded fuzzy comparison was performed:
the eight exact items use objdiff's 100% item field, all other items use zero,
and aggregate fuzzy fields contain only that conservative exact-byte fraction.
Data matching and completion remain zero. This does not establish a full PE link.
Completion does not mean exhaustive input coverage, hardware parity, complete
engine integration, or playability. Existing test scopes and numeric allowances
remain part of the evidence and must not be hidden by the aggregate metric.

The old 2,026/11,637 (17.41%) figure in `recovery.json` is historical checkpoint
bookkeeping. It is not an input to the new report. The address ledger must be
reconciled independently; uncertain mappings remain uncounted.

Original executables, game assets, disassembly, generated pseudocode, fixture
memory and compiled game modules stay local. CI can check the published metadata,
source hashes, arithmetic and report format. It cannot rerun original-executable
comparisons without the local specimen and fixtures, or replay native matching
without the private object/compiler environment. Public matching metadata is a
hashed record of independently replayed local proof, not a CI compiler build.
A schema-valid report alone is not new behavioral or matching evidence.

The retired publishing automation remains paused. The user has authorized direct
publication of verified work from the current recovery chat.

## Reconciled report

`ledger.json` links **2,051 distinct original addresses** to source hashes and
preserved positive original-execution evidence. It credits **436,577 original
function-body bytes / 2,375,378 original `.text` virtual bytes (18.38%)**.
Native matching separately credits **406 / 2,375,378 bytes (0.01709%)**, across
eight already complete addresses, so completion receives no additional credit.
The initial reporting commit reconciled existing
evidence. Subsequent audited checkpoint selections add 87 distinct addresses,
totaling 9,528 original body bytes. The latest thirteen camera mappings add 988
bytes. The preceding four mappings added 451 bytes, and the earlier 22 mappings
added 21 addresses (4,093 bytes); shared
`49f3b0` earned no extra bytes. Constructor
`582d90` now has explicit return and temporary cleanup verification; its earlier
partial checkpoints remain immutable.

The inventory contains 11,889 discovered entries: 11,641 entries in the later
read-only Ghidra export, 228 supplied recovery entries, and one additional tested
SSE matrix entry and nineteen entries from later startup discovery exports. These
are discovered entries,
not an exhaustive or authoritative count of original source functions. Their
non-overlapping bodies total 1,969,695 bytes. The remaining **405,683 bytes** stay
in the denominator with zero completion, including unidentified code, padding
and jump tables. The denominator includes runtime/library code present in the
specimen. Raw file-alignment bytes beyond `.text`'s virtual size are excluded.
The executable is the supplied modified/unpacked build, not pristine retail.

The 19 initial evidence gaps were resolved using existing nested original
counters, coverage, and the maintained decal fixture maps. Four checkpoint
claims now have source and execution links. Aliases at `0042bb20`, `004a2ba0`
and `005480a0`, plus `004fbda0` and `0049f3b0`, earn one address and one body each.
Thirteen linear extents exceed the
Ghidra body union; only the smaller body union receives byte credit. Four current
partial roots receive no credit. The fifth historical partial, `582d90`, has an
explicit audited resolution linked to 80 completed original/Wasm constructor
calls, successful returns, real pooled allocations and temporary cleanup. The Gap command's old `prefix` name remains for
immutable tests, but its pinned complete-dispatch evidence covers all routes.
The wallplant helper's older oracle lacks a status field; its enclosing pinned
checkpoint records the complete routine and passing Node/Chromium comparisons.
Successful wallplant integration into the airborne root remains unfinished.

Early native-only comparisons are identified explicitly; a browser check is not
invented for them. Uncredited source definitions are listed in the ledger, and
the separate historical physics experiment remains outside this active-build
ledger pending reconciliation. Original counters may measure calls, comparison
cases or observed instructions; their exact field and scope are retained.
Completion requires a complete implementation and appropriate scoped evidence,
not 100% instruction coverage. Unexercised branches and the existing numeric,
NaN, indeterminate-word and network-padding comparison allowances remain part
of those scopes. No allowance or original result was changed for this report.

`report.json` is objdiff v2, with three explicitly synthetic accounting buckets:
verified recovery, known unrecovered bodies and unassigned `.text` bytes. These
do not claim reconstructed original translation units. Data/assets are unmeasured
and receive zero completion and matching credit.

```sh
# Local reconciliation requires the preserved private discovery and evidence.
python3 tools/reconcile_progress.py
python3 tools/generate_progress_report.py --local-evidence
# A public clone needs only the ledger, inventory and selected source files.
python3 tools/test_progress_report.py
python3 tools/generate_progress_report.py --check
CARGO_TARGET_DIR=local/build/progress-validator cargo +1.97.0 run --locked \
  --manifest-path tools/progress-validator/Cargo.toml -- progress/report.json
```

CI does not replay original comparisons. Its checks enforce source identity,
unique addresses and non-overlapping ranges, sizes, partial exclusions,
denominator arithmetic, deterministic regeneration and the actual pinned
objdiff parser. The parser checks aggregate/unit matching arithmetic and exact
item totals, then requires deterministic regeneration against the validated
selected proof. A matching claim moved to an unproved routine is rejected even
when its aggregate arithmetic is correct. Aggregate, unit, category, item and
provenance corruptions are tested. Run this project validator from the repository
root. The trial pins an earlier inventory hash; every trial body must still equal
the current full original range, despite later unrelated discovery additions.

## Upload verification and registration

`.github/workflows/progress.yml` validates and uploads only `report.json` as
`pc_report`, then downloads that same artifact, compares it byte-for-byte with
the generated report and validates it again. No original executable, assets,
memory fixtures, pseudocode or compiled game module are included. The workflow
has read-only repository permissions and runs on `main` pushes, PRs and manual
dispatch. Artifact expiration remains a practical limit (90-day retention).

The referenced decomp.dev implementation's registration check looks for a
completed **push event on the repository's default branch**. A successful PR or
manual-dispatch run alone does not establish registration eligibility. The first
default-branch push workflow passed on 2026-10-12 at
[commit `8541949`](https://github.com/w84april/thug2/commit/85419493580a0699635fc3ad9fb82c488102280d).
[Run 38260633281](https://github.com/w84april/thug2/actions/runs/38260633281)
uploaded and downloaded `pc_report` successfully. Independent artifact retrieval
confirmed a ZIP containing only `report.json`, byte-identical to the committed
report; local regeneration and the pinned objdiff parser passed again. See
[the verification record](upload-verification.json) for hashes and artifact expiry.

decomp.dev registration and import of the matching report at `b42fb04` are
verified on the project page. The manager independently observed its exact
commit link, 18.34% “fully linked” and 0.02% “decompiled” display; the latter
rounds the verified 406 / 2,375,378 matching bytes (0.01709%). That report also
passed all hosted upload/download steps and independent ZIP retrieval, byte
comparison, regeneration and pinned-parser checks. The newer 18.38% camera
report needs its own upload and site-import verification. The visible notice
confirms that the project stays hidden from the public listing until 0.5%
matched code. The site labels completion
“fully linked” and matching “decompiled”; neither label establishes a playable
browser engine. A later upload still needs its own artifact verification.

A separate [rendering integration record](rendering-preview.json) preserves the
first private Chromium frame of the original training geometry. Its new WebGL
adapter draws the preserved Wasm loaders' 2,269 meshes and 2,486 original texture
mips; all 7,024 vertex/index/mip storage payloads compare to original references.
Actual orbit, zoom and reset controls pass. The 200 original/Wasm parity suites
remain the engine checkpoint count; this preview adds no completed functions,
bytes or native matches. Its isolated raw-input arena and comparison storage
remain private bootstrap dependencies. First-pass drawing does not establish
original visibility, sorting, blending, lighting, animations or frame equivalence.
Full scene/sector/skater startup and playable gameplay remain unfinished.

The preview can be reopened in the existing private workspace with
`python3 local/analysis/serve-training-webgl-v1.py`; use the printed loopback URL.
Its source is published; raw assets, binaries, snapshots and screenshots remain
private. The public source-only reporting check does not reproduce the preview.
The adapter follows [Direct3D vertex layout](https://learn.microsoft.com/en-us/windows/win32/direct3d9/d3dfvf),
[triangle strips](https://learn.microsoft.com/en-us/windows/win32/direct3d9/triangle-strips)
and [WebGL S3TC upload formats](https://registry.khronos.org/webgl/extensions/WEBGL_compressed_texture_s3tc/);
those platform mappings receive no original-function credit.

The latest audited startup checkpoint and its selected complete routine maps are
recorded in [verified-recovery.json](verified-recovery.json). It preserves 200
passing Node/actual Chromium suites and 87 newly reconciled distinct addresses.
The latest thirteen camera dependencies compare 97 cases and 271 completed
calls, exercising all 276 original instructions. They cover object/component
storage and cleanup, projection, raw owner-state copying and WalkCamera links.
No new numeric tolerance or checker changes were introduced. Projection uses
the existing SDK transcendental adapters; physical x87 accuracy is unverified.
All 199 predecessor result objects are unchanged. Camera-specific QB
initialization/commands, viewport assignment and full profile startup remain.

The preceding four complete dependencies cover Light construction, shared-component
construction, camera owner binding and Walk camera binding. They pass 55 cases
and 131 completed calls, covering 127/132 instructions with five unchecked
allocation-fault exclusions. All 198 predecessor result objects are unchanged.
Original QB loading of the camera descriptor file is discovery evidence only;
it does not establish runtime camera integration or earn routine credit.

The preceding 22 checked mappings add 21 new addresses and 4,093 original body
bytes; shared `49f3b0` is an alias with zero additional credit. Across 332 cases
and 412 completed calls, 1,280/1,296 scoped instructions compare exactly with no
new numeric allowances or checker changes. Sixteen exclusions cover initialized
allocator bootstrap, unchecked allocation-fault paths and unreachable alignment;
the resource destructor receives its 73-byte body union rather than its 82-byte
linear extent. Wrong row-pitch handling and a changed original buffer condition
are rejected by the unchanged comparator. All 195 predecessor result objects are
unchanged. Constructor `582d90` returns successfully in 80 local/remote calls,
including 40 real pooled structure allocations, actual tag/sticker RGBA copies
and temporary QB cleanup. Its historical partial status is resolved through a
separate audited declaration; earlier checkpoints are preserved. Complete
component finalization/frames, cold startup, actual rendering and the playable
level remain unfinished. GPU fixtures record storage operations, not rendered
frames. Private continued work is recorded in
`local/analysis/continued-recovery-next.txt`.

The first upload verification record identifies the original 17.98% report, not
the current 18.38% report. Later pushes use the same upload/download checks.

The old chat's goal and the publishing automation remain paused. Preserve
`HANDOFF.txt`, all checkpoints and their private evidence. Refresh the ledger
only after new complete behavior has its own verification; do not merely carry
the historical routine estimate into objdiff completion fields.
