# Recovery reporting

This project recovers Windows x86 behavior for WebAssembly. It has **no verified
binary matches** and is not playable yet. Behavioral comparisons do not establish
that rebuilt x86 bytes match the original executable.

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
Our repository is public; registration has not been performed.

There is a material limitation: the current public listing hides projects below
**0.5% matched code**. Completion progress alone does not meet that threshold.
Our report can be format-compatible while the project remains hidden. We will
not turn recovery completion into matching credit to bypass that restriction.
Hosted acceptance/visibility of this non-matching project remains unverified.

Authoritative implementation references:

- [Artifact discovery and parsing](https://github.com/encounter/decomp.dev/blob/e9c086adb74d2fe569541cd715cd9312d7641313/crates/github/src/lib.rs)
- [Registration checks](https://github.com/encounter/decomp.dev/blob/e9c086adb74d2fe569541cd715cd9312d7641313/crates/web/src/handlers/manage.rs)
- [Windows platform and visibility rule](https://github.com/encounter/decomp.dev/blob/e9c086adb74d2fe569541cd715cd9312d7641313/crates/core/src/models.rs)
- [objdiff report schema used by that revision](https://github.com/encounter/objdiff/blob/0c48d711c7bd51f791b353d7d85ba948b277e2f2/objdiff-core/protos/report.proto)
- [objdiff parser and version migration](https://github.com/encounter/objdiff/blob/0c48d711c7bd51f791b353d7d85ba948b277e2f2/objdiff-core/src/bindings/report.rs)

## Metric policy

`complete_code` will represent original code bytes attributed to recovered
functions with linked source and passing behavioral evidence. All `matched_*`
and `fuzzy_match_percent` values remain zero: no binary matching was attempted.
Completion does not mean exhaustive input coverage, hardware parity, complete
engine integration, or playability. Existing test scopes and numeric allowances
remain part of the evidence and must not be hidden by the aggregate metric.

The old 2,026/11,637 (17.41%) figure in `recovery.json` is historical checkpoint
bookkeeping. It is not an input to the new report. The address ledger must be
reconciled independently; uncertain mappings remain uncounted.

Original executables, game assets, disassembly, generated pseudocode, fixture
memory and compiled game modules stay local. CI can check the published metadata,
source hashes, arithmetic and report format. It cannot rerun original-executable
comparisons without the local specimen and fixtures. A schema-valid report alone
is not new behavioral evidence.

The retired publishing automation remains paused. The user has authorized direct
publication of verified work from the current recovery chat.

## Reconciled report

`ledger.json` links **1,997 distinct original addresses** to source hashes and
preserved positive original-execution evidence. It credits **428,910 original
function-body bytes / 2,375,378 original `.text` virtual bytes (18.06%)**. Every
binary-matching measure is zero. The initial reporting commit reconciled existing
evidence. A subsequent audited
checkpoint adds 33 complete LocalNet, EndRun, BalanceTrick and SkaterLoopingSound
routines, totaling 1,861 original body bytes; constructor progress remains partial
and uncredited.

The inventory contains 11,876 discovered entries: 11,641 entries in the later
read-only Ghidra export, 228 supplied recovery entries, and one additional tested
SSE matrix entry and six entries from later startup discovery exports. These
are discovered entries,
not an exhaustive or authoritative count of original source functions. Their
non-overlapping bodies total 1,966,911 bytes. The remaining **408,467 bytes** stay
in the denominator with zero completion, including unidentified code, padding
and jump tables. The denominator includes runtime/library code present in the
specimen. Raw file-alignment bytes beyond `.text`'s virtual size are excluded.
The executable is the supplied modified/unpacked build, not pristine retail.

The 19 initial evidence gaps were resolved using existing nested original
counters, coverage, and the maintained decal fixture maps. Four checkpoint
claims now have source and execution links. Aliases at `0042bb20`, `004a2ba0`
and `005480a0` earn one address and one body each. Ten linear extents exceed the
Ghidra body union; only the smaller body union receives byte credit. Five current
partial roots receive no credit. The Gap command's old `prefix` name remains for
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
objdiff parser. The parser also rejects matching credit in aggregate, unit,
category and item fields and verifies unit totals and completion metadata.

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

decomp.dev registration and hosted acceptance remain unverified. Workflow and
parser acceptance do not establish public visibility. With zero matching credit,
the referenced 0.5% rule still
hides this project from the public listing.

The latest audited startup checkpoint and its selected complete routine maps are
recorded in [verified-recovery.json](verified-recovery.json). It preserves 193
passing Node/actual Chromium suites and 33 newly reconciled routine addresses.
The latest eight routines add 549 original body bytes, passing 121 comparison
cases and 291 completed calls with 42 native stop callbacks. A clear-before-stop
control is rejected. Previously recovered voice lookup, device stop and volume
initialization earn no new credit. The skater constructor reaches 309/463
instructions and stops before component `1859f772`; it receives zero completion
credit. Balance and looping-sound commands, component frame paths, audio output,
later startup, rendering and the playable level remain unfinished. Private continued
work is recorded in `local/analysis/continued-recovery-next.txt`.

The first upload verification record identifies the original 17.98% report, not
the current 18.06% report. Later pushes use the same upload/download checks.

The old chat's goal and the publishing automation remain paused. Preserve
`HANDOFF.txt`, all checkpoints and their private evidence. Refresh the ledger
only after new complete behavior has its own verification; do not merely carry
the historical routine estimate into objdiff completion fields.
