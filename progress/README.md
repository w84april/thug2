# Recovery reporting

This project recovers Windows x86 behavior for WebAssembly. It has **406 verified
native matching bytes across eight individual functions** and is not playable yet.
Scoped behavioral recovery, native binary matching and original-target linked
progress have separate evidence. Current verified original-target linked credit
is zero; the 18.57% behavioral total remains in
[behavioral-recovery.json](behavioral-recovery.json).

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
Our repository is public and the project is registered. On 2026-10-13, an
independent browser check of the [PC progress page](https://decomp.dev/w84april/thug2/pc)
showed the exact imported commit
[`a03871003c8f9d2ece2fd6580e460b50a6b072df`](https://github.com/w84april/thug2/commit/a03871003c8f9d2ece2fd6580e460b50a6b072df),
rounded 0.02% matching, and the hidden-until-0.5% notice. Its
[Actions run](https://github.com/w84april/thug2/actions/runs/38411458360) passed
all ten job steps. The downloaded `pc_report` artifact (`11822605905`) contains
only `report.json`, byte-for-byte equal to the committed report and accepted by
the pinned objdiff parser. Report SHA-256:
`7f1b7db36932f13e38e3c15bf0df88ea1309bcb130cf8ef8141d35c7c073a785`.
Matching remains 406 bytes; original-target linked bytes and units remain zero.

Earlier reports through `0e9f1b2` incorrectly encoded behavioral coverage as
linked completion. Their historical imports do not prove original-target
build/link integration. The corrected `060efffb` import and upload/download
equality remain preserved as earlier evidence; the current observation above
verifies the reviewed Warehouse source checkpoint. Behavioral coverage stays in
the separate recovery report and does not increase decomp.dev matching.

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

`complete_code`, `complete_code_percent`, `complete_units` and each unit's
`metadata.complete` describe original-target linked-unit progress, not behavioral
coverage. They stay zero/false because this project has no selected proof that an
original-target native unit is built and included in the target link. Browser
WebAssembly linking and isolated native COFF function comparisons do not establish
that integration. There is no positive linked credit or linked-evidence selection.

Objdiff's [schema](https://github.com/encounter/objdiff/blob/0c48d711c7bd51f791b353d7d85ba948b277e2f2/objdiff-core/protos/report.proto)
and [report generator](https://github.com/encounter/objdiff/blob/0c48d711c7bd51f791b353d7d85ba948b277e2f2/objdiff-cli/src/cmd/report.rs)
keep matching and completed/linked unit measures independent. The generator copies
unit completion metadata and credits a whole unit only when it is marked complete;
matching comes from object comparisons separately. A unit can therefore have
matching functions without linked completion, or linked completion before exact
matching. Our synthetic behavioral unit previously used `complete=true`, causing
the misleading site percentage. Reports through `0e9f1b2` are historical records
of that mistake; their successful schema/arithmetic checks did not prove linking.
The correction preserves their immutable evidence and all recovered code.

[behavioral-recovery.json](behavioral-recovery.json) keeps deduplicated original
routine counts, original body bytes, the fixed `.text` denominator and test-scope
limitations outside objdiff's linked fields. The address ledger remains the
behavioral evidence index. No routine recovery is discarded or converted to
additional binary matching.

Matching credit
requires selected positive per-function native proof, complete original body
sizes and exact raw or declared-relocation-resolved bytes. The accepted proof
is [matching/selection.json](../matching/selection.json), which pins the immutable
[trial proof](../matching/proof.json), source, comparator and manifest hashes.
Five functions match raw COFF bytes (189 bytes); three checksum functions match
after DIR32 table address resolution (217 bytes). No instructions or operands are
masked. Two mismatches earn zero. No graded fuzzy comparison was performed:
the eight exact items use objdiff's 100% item field, all other items use zero,
and aggregate fuzzy fields contain only that conservative exact-byte fraction.
Data matching and original-target linking remain zero. This does not establish a full PE link.
Behavioral recovery does not mean exhaustive input coverage, hardware parity, complete
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

`ledger.json` links **2,070 distinct original addresses** to source hashes and
preserved positive original-execution evidence. The separate behavioral record
credits **439,230 original
function-body bytes / 2,375,378 original `.text` virtual bytes (18.49%)**.
Native matching separately credits **406 / 2,375,378 bytes (0.01709%)**, across
eight already behaviorally verified addresses. Objdiff original-target linked
code and units remain zero; matching does not award linked credit.
The initial reporting commit reconciled existing
evidence. Subsequent audited checkpoint selections add 106 distinct addresses,
totaling 12,181 original body bytes. The two latest camera batches add 551 factory/constructor bytes and 384
QB-initialization/final-link bytes. Three remapped prior addresses earn no repeated
credit. The earlier camera reset/FOV routines add 947 bytes and the preceding Animation state storage routines add 244 bytes.
The earlier Animation component storage routines added 248 bytes. The preceding three viewport routines added 279 bytes, thirteen camera
mappings added 988 bytes, four mappings
added 451 bytes, and the earlier 22 mappings
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

decomp.dev registration and import of the viewport report at `2c5bec00` are
independently verified on the project page. Its exact commit link, 18.39%
“fully linked” and 0.02% “decompiled” display were observed; the latter
rounds the verified 406 / 2,375,378 matching bytes (0.01709%). That report also
passed all hosted upload/download steps and independent ZIP retrieval, byte
comparison, regeneration and pinned-parser checks. The zero-credit rendering
commit `52c53e5` uploaded the same report, independently retrieved and verified.
The viewport report's hosted artifact was independently downloaded and verified.
The 18.40% Animation/Warehouse report at `1e62a168` passed
[run 38303198059](https://github.com/w84april/thug2/actions/runs/38303198059).
Independent retrieval of artifact `11770993069` confirmed a ZIP containing only
`report.json`, identical to committed/regenerated bytes and accepted by the pinned
parser. The later 18.45% Animation-state/camera-reset report at `07e803e8` passed
[run 38308989489](https://github.com/w84april/thug2/actions/runs/38308989489).
Independent retrieval of artifact `11774545506` confirmed only `report.json`,
byte-identical to committed/regenerated bytes and accepted by the pinned parser.
An actual browser observation confirms `07e803e8` / 18.45% fully linked and
0.02% matched. These are historical pre-correction linked displays. The corrected report keeps
the behavioral 18.49% total separate, reports zero original-target linked credit,
and requires its own hosted artifact verification and observed site import.
The visible notice
confirms that the project stays hidden from the public listing until 0.5%
matched code. The site labels unit completion
“fully linked” and matching “decompiled”; neither establishes a playable browser
engine, and behavioral coverage must not populate the linked fields. A later upload still needs its own artifact verification.

A separate [rendering integration record](rendering-preview.json) preserves the
earlier full-bundle exterior preview and the corrected indoor Warehouse view.
Original whole QB loading confirms `TRAINING` → `load_TR` with the `TR` prefix;
the bundle contains Warehouse and New Jersey exterior sectors. The earlier title
and image overstated the playable-area presentation. The new WebGL adapter selects
672 original `CreatedAtStart` static sectors (2,028 meshes) and adapts its camera
from a Warehouse restart node. That node is not verified as the default gameplay
spawn. All 7,024 vertex/index/mip storage buffers still compare to original
references, and actual zoom, orbit, bundle overview and reset controls pass.
The preview preserves its 202-suite engine checkpoint; the latest separately
audited engine checkpoint passes 206 suites. The preview adds
no completed functions, bytes or native matches. The isolated raw-input arena and
comparison storage remain private bootstrap dependencies. Original visibility,
transforms (including 56 flagged billboard sectors), sorting, blending, lighting,
animations and frame equivalence remain unverified. Full scene/sector/skater
startup and playable gameplay remain unfinished.

The preview can be reopened in the existing private workspace with
`python3 local/analysis/serve-training-warehouse-v2.py`; use the printed loopback URL.
Its source is published; raw assets, binaries, snapshots and screenshots remain
private. The public source-only reporting check does not reproduce the preview.
The adapter follows [Direct3D vertex layout](https://learn.microsoft.com/en-us/windows/win32/direct3d9/d3dfvf),
[triangle strips](https://learn.microsoft.com/en-us/windows/win32/direct3d9/triangle-strips)
and [WebGL S3TC upload formats](https://registry.khronos.org/webgl/extensions/WEBGL_compressed_texture_s3tc/);
those platform mappings receive no original-function credit.

The latest audited startup checkpoint and its selected complete routine maps are
recorded in [verified-recovery.json](verified-recovery.json). It preserves 206
passing Node/actual Chromium suites and 106 newly reconciled distinct addresses.
The latest QB initialization/final-link checkpoint verifies seven mappings through
423 cases/918 calls and all 165 instructions. Five new addresses add 384 bytes;
already selected target bindings `4fa3c0` and `524c50` add no repeated credit.
Exactly three read-only Ghidra extents enter the inventory; the `.text` denominator
stays fixed. The preceding factory/constructor/direct-link checkpoint verifies six
mappings through 81 cases/165 calls and 150/151 instructions, excluding only the
initialized-service cold bootstrap call. Five new addresses add 551 bytes; the
previously selected three-byte `5902e0` helper earns no repeated credit. All 205
predecessor result objects are unchanged. Original camera composite startup/frame
updates and complete profile startup remain unfinished.

The latest camera reset/FOV routines compare 333 cases and 924 completed calls,
adding 947 original body bytes with all 276 instructions exercised. Previous
constructor setup calls receive no repeated address/body-byte credit. Original
Physics QB loading resolves three five-entry arrays and 13 named presets; finite
preset indices 1–4, interpolation, split layouts, defaults and unaligned storage
compare. Additional angle branches use explicitly bounded caller arrays extended
with an existing preset checksum; those cases establish no original gameplay mode.
The existing SDK projection contract remains; physical x87 transcendental accuracy
is unverified. All 203 predecessor result objects are unchanged. Complete camera
composite startup/update, frame equivalence and full profile startup remain unfinished.

The preceding Animation state storage routines compare 504 cases and 1,008 calls,
adding 244 body bytes and exercising all 77 instructions. Original empty-gap-list
and Script wait clearing execute with sentinel, low-byte and overlapping-head
cases. The pointer-argument and unaligned-pointer fixture failures are retained;
only declarations were corrected, with no checker or C change. The first browser
object capture was truncated at 200 entries; the immutable full proof uses the
complete rendered DOM text and compares all 203 suites, preserving all 202 prior
result objects. Original startup discovery now reaches Animation configuration
with a valid state object; it earns no full-initializer credit. Configuration,
clip loading and full profile startup remain unfinished.

The earlier Animation component storage routines compared 24 cases and 42 calls,
adding 248 body bytes. Coverage was 66/67 instructions, with only the reviewed
cold allocator bootstrap call excluded under the initialized-service contract.
Allocation failure, embedded sentinel links and unaligned writes passed; the
identity-only vtables earned no virtual behavior credit. All 201 predecessor
result objects remain unchanged in that immutable checkpoint.

The preceding three viewport routines compare 75 cases and 344 completed calls,
exercising all 104 original instructions. Actual camera deletion, intrusive
reference updates and forced owner-state synchronization execute unchanged.
Registration has separate owner-key and viewport-index arguments followed by a
low-byte force flag. All 200 predecessor result objects are unchanged; no new
numeric allowance or checker change. Bounded initialized mappings/UI services
remain required. Retained allocator storage permits raw same-owned-pointer
behavior comparisons; that case does not establish a valid gameplay lifetime.
Full profile startup and complete camera-specific initialization/update remain.

The preceding thirteen camera dependencies compare 97 cases and 271 completed
calls, exercising all 276 original instructions. They cover object/component
storage and cleanup, projection, raw owner-state copying and WalkCamera links.
No new numeric tolerance or checker changes were introduced. Projection uses
the existing SDK transcendental adapters; physical x87 accuracy is unverified.
All 199 predecessor result objects are unchanged. Camera-specific QB
initialization/commands and full profile startup remain.

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
the corrected report with zero original-target linked credit. Later pushes use
the same upload/download checks and preserve the separate behavioral record.

The old chat's goal and the publishing automation remain paused. Preserve
`HANDOFF.txt`, all checkpoints and their private evidence. Refresh the ledger
only after new complete behavior has its own verification; do not merely carry
the historical routine estimate into objdiff completion fields.

## Original QB camera assembly

The immutable camera composite checkpoint verifies the actual five component
type descriptors from the original skutils script through shared creation,
merged initialization, node naming, priority and optional finalization. There
are 36 original full assembly cases within 72 cases/108 direct calls. The new
generic Camera initializer `41b7f0` covers all eight instructions and contributes
24 unique original bytes; previously verified creation roots earn no repeated
credit. All 207 Node and Chromium suites pass, with every one of the 206
predecessor result objects unchanged. Complete rendered browser results were
independently compared with Node.

Derived method tables expose verified startup initialization/finalization/moved
slots. Camera frame, disposal and command methods remain unfinished. The host
ABI bridge scopes existing memory services; it is authored integration and
receives no original-function credit. The checkpoint preserves earlier failed
caller fixtures and the first metadata revision. This does not complete full
profile initialization or make the Warehouse preview playable. Behavioral
coverage is 439,254/2,375,378 bytes across 2,071 addresses (18.49%). Native matching
remains eight functions/406 bytes and original-target linking remains zero.

## Animation channel startup

Four channel creation and fade dependencies pass 295 original cases and 828
direct calls, covering 152/154 instructions under initialized allocation and
valid live channel graph contracts. The two exclusions are the literal cold
allocator bootstrap and an unchecked internal allocation failure that faults
before returning. Direct allocation-wrapper failures compare. The original
channel constructor, destructor and allocator callees execute and earn no
repeated credit. All 208 Node and actual Chromium suites pass, with all 207
predecessor result objects unchanged and complete rendered results equal to Node.
The immutable checkpoint preserves 26,655 artifacts including all 26,226 parent
artifacts and the rejected earlier sentinel fixture and field-offset draft.

The four addresses add 416 unique body bytes: behavioral coverage is now
439,670/2,375,378 bytes across 2,075 addresses (18.51%). Native matching remains
eight functions/406 bytes and original-target linked credit remains zero. Clip
playback startup, full Animation/profile initialization, a controllable rendered
skater and gameplay remain unfinished. The Warehouse is still a static preview.

## Original animation clip startup

Two further routines pass 256 original cases and 2,264 direct calls: channel
clip startup `4823c0` and optional owner-parameter merge `4616f0`. Original
controller factories, command methods, archive clips, readers, cache ownership,
pooled temporary structures and event-array disposal execute. The comparison
also loads and starts the actual 400-byte THPS6_Basics/Default animation with
checksum `1ca1ff20`; its decoded archive contents equal the extracted file.
The earlier private “dummy” label was incorrect. This direct clip proof does
not establish original asset registration, profile bootstrap or pose rendering.

All 209 Node and actual Chromium suites pass, with all 208 predecessor result
objects unchanged and complete rendered results equal to Node. Coverage is
433/450 instructions, with seven literal cold-bootstrap calls, nine mandatory
allocation-null instructions and one failed selected-pool membership instruction
excluded under initialized successful allocation and stable valid ownership.
The selected checkpoint preserves 27,036 artifacts, including all 26,655 parent
artifacts. The first scoped proof and rejected metadata revision remain private.

The two addresses add 1,467 unique original body bytes. Behavioral recovery is
441,137/2,375,378 bytes across 2,077 addresses (18.57%). The clip's 1,442-byte
body was absent from the old inventory; its independently exported extent
raises known functions to 11,894 and leaves 403,916 text bytes unassigned.
The denominator and earlier address records are unchanged. Native matching
remains eight functions/406 bytes and original-target linked credit remains zero.
Full Animation/profile initialization, skater control, pose rendering and
playable gameplay remain unfinished. The Warehouse remains a static preview.


### Reviewed Warehouse movement source checkpoint

The latest [browser movement record](browser-movement-preview.json)
adds the reviewed Hawk, board, skeleton, animation sampler and bounded movement
source through the v9/C6 trigger repair. All 216 earlier Node/Chromium suite
objects are unchanged. Original comparisons cover 536 goal-predicate cases, two
180-frame jump/release sequences and a 1,200-frame transfer route. Real browser
push, jump, landing, steering, braking and fresh reset checks pass.

This fixes the reproduced turning/jumping trigger failure. The exact earlier
human-reported error is unknown, and reset after a forced engine failure has not
been tested. Camera, input/time/bootstrap, jump-action mapping, CPU skinning and
WebGL presentation retain their authored adapters; complete original gameplay
and rendering startup remain unfinished. The original assets, game modules,
fixture outputs, screenshots and private compiler material are omitted. Public
source alone cannot run the preview.

No new recovery, matching or original-target linking is claimed: behavioral
recovery remains 2,077 unique routines / 441,137 original body bytes (18.57%);
matching remains eight functions / 406 bytes; linked credit remains zero.
Reviewed source commits and pushes are authorized. Only the retired publishing
automation remains paused.
