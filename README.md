# THUG2 recovery

Recover the PC game's behavior from its executable, then port enough of the engine
to play the original training level in a browser. This repository is at the early
source-recovery stage. Recovered collision code runs in the browser, but the game
is not playable yet.

Disassembly exposes machine instructions. Decompilation reconstructs higher-level
code from those instructions. A browser port additionally needs a working engine
build and replacements for Windows graphics, input, sound, and file services.
Generated decompiler pseudocode alone does not supply that build.

## Progress and Git checkpoints

**Reconciled behavioral completion: 18.38% of original `.text` bytes** —
436,577 / 2,375,378 bytes attributed to 2,051 distinct original addresses with
linked source and scoped behavioral evidence. **Verified native binary matching:
406 bytes across eight functions (0.01709%).**
The game is not playable. Unidentified code, jump tables and padding remain in
the code denominator; data and assets are unmeasured. This metric combines the
reconciled baseline with 87 newly reconciled startup/lifecycle/camera addresses.
Shared original routines and C aliases receive no additional credit. It does
not measure playability. See
[reporting policy and verification](progress/README.md),
[address ledger](progress/ledger.json) and [objdiff report](progress/report.json).
The native matching proof compares complete individual function bodies, with
189 raw COFF-equal bytes and 217 bytes equal after declared address resolution.
It does not establish a linked executable. See [the proof and scope](matching/README.md).

**Historical decompilation estimate: 17.41%** — 2,026 reported recovered routines divided
by the initial 11,637-function Ghidra inventory. This comprises 1,156 maintained
routines (9.93% of that baseline) and 870 experimental routines: 853 in the latest
module and 17 in a separate physics experiment. **The game is not playable.**

This is a preliminary bookkeeping metric, not compiler byte matching or a
percentage of the work needed for a browser game. The counts inherit the existing
checkpoint reports; they have not been independently reconciled into a single
deduplicated address ledger. The initial function inventory is also incomplete.
Do not interpret two decimal places as that level of measurement accuracy.
Partial routines, test helpers and generated pseudocode do not earn new progress.

The historical checkpoint bookkeeping is [progress/recovery.json](progress/recovery.json).
It records the checkpoint hash, validation summary, scope, remaining work and
hashes of published checkpoint files. Existing checkpoint files and the original
executable remain unchanged locally. That historical integrity audit passed for all
21,854 pinned artifacts and 185 Node/Chromium suites. The newer startup
checkpoint preserves all prior evidence and passes 200 suites; all 199 preceding
result objects remain unchanged. See
[the current verified checkpoint selection](progress/verified-recovery.json).

The source, harnesses and selected build metadata under `local/analysis/` are
explicitly tracked using [progress/publication-files.txt](progress/publication-files.txt).
The rest of `local/` remains ignored: original executables, discs, extracted game
assets, generated disassembly/pseudocode, memory fixtures and compiled outputs.
A fresh clone therefore does not contain everything needed to reproduce the
original-executable comparisons. Existing experimental builders also use local
build manifests with machine-specific paths; this is a recovery-source archive,
not a portable playable release. See the setup and validation notes below.

The historical routine estimate in `recovery.json` is preserved as a snapshot.
For current publication, audit the immutable checkpoint, update the complete
routine selections in `progress/verified-recovery.json`, then regenerate the
address ledger and objdiff report. The local specimen/evidence are required:

```sh
python3 tools/reconcile_progress.py
python3 tools/generate_progress_report.py --local-evidence
python3 tools/test_progress_report.py local/build/progress-validator/debug/thug2-progress-validator
git add README.md tools progress
git add -f --pathspec-from-file=progress/publication-files.txt
```

Review the staged source/metadata allowlist before committing. Complete routines
receive one original address and their original body bytes; duplicates, partial
roots and test adapters receive no additional credit. Keep the code denominator
fixed for this specimen and keep matching fields at zero without binary-match
evidence. Run the default-branch upload/download workflow for each publication.
The retired chat and its publishing automation remain paused; direct publication
of verified checkpoints is authorized in the current recovery chat.

## Current evidence

- Thirteen camera dependencies now pass 97 original/Wasm cases and 271 completed
  calls, exercising all 276 instructions and adding 988 original body bytes.
  Camera object/component storage and cleanup, projection setup, raw owner-state
  copying and WalkCamera binding compare exactly. All 200 Node/actual Chromium
  suites pass, with all 199 preceding result objects unchanged and no new numeric
  tolerance or checker changes. Projection uses the existing SDK transcendental
  adapters; physical x87 accuracy remains unverified. Camera-specific QB
  initialization, viewport assignment, full profile startup and rendering remain.

- Eight reconstructed C++ helpers now have independently replayed native byte
  matches under MSVC 13.10.3077. Every byte is compared; three checksum routines
  use their declared table-address relocations and five vector methods match raw
  object bytes. Two string-checksum candidates remain mismatched and receive no
  credit. This changes only the separate matching metric; behavioral completion
  and the original code denominator stay unchanged. Public checks validate the
  selected proof metadata; CI does not run the private compiler or original.

- Four initialization dependencies now pass 55 original/Wasm cases and 131
  completed calls: the Light constructor, shared-component construction, camera
  owner binding and Walk camera binding. They add four distinct addresses and
  451 original body bytes, with 127/132 instructions exercised and five documented
  unchecked allocation-fault exclusions. Callback order, ownership, appended
  component chains, repeated binding and null-camera resets compare exactly.
  All 199 Node/actual Chromium suites pass, preserving all 198 previous result
  objects. The original camera descriptor file has also been inspected with the
  original QB loader; that discovery earns no completion credit. Full profile
  initialization, camera integration, rendering and the playable level remain.

- Both original skater constructor branches now return successfully, including
  tag/sticker texture loading and cloning, the final component, and temporary QB
  cleanup. The new checks compare 332 cases and 412 completed calls, including
  80 complete constructor calls and 40 real pooled structure allocations. Actual
  tag/sticker RGBA copies, pitched GPU storage, deletion order, heap scopes and
  component ownership compare exactly. The 22 selected mappings add 21 new
  original addresses and 4,093 conservative body bytes; shared `49f3b0` receives
  zero extra credit. Coverage is 1,280/1,296 scoped instructions, with sixteen
  documented allocator, allocation-fault and unreachable-alignment exclusions.
  Two incorrect copy controls are rejected. All 198 Node/actual Chromium suites
  pass and all 195 predecessor result objects are unchanged. Historical partial
  `582d90` is resolved explicitly; its earlier interrupted evidence is preserved.
  Complete component finalization/frame integration, actual GPU rendering, cold
  startup and a playable level remain unfinished.

- SkaterLoopingSound lifecycle and its voice-stop wrapper now pass 121 original/Wasm
  comparison cases and 291 completed calls, including 42 native stop callbacks
  that test mutation and clear-after-callback order. Eight complete routines
  exercise all 156 original instructions with no new comparison allowances.
  A control that clears the voice before the callback is rejected. All 193
  Node/actual Chromium suites pass, preserving all 191 previous result objects.
  Existing voice lookup, device stop and volume initialization receive no new
  address credit. These eight addresses add 549 original body bytes; all 33
  recently reconciled routines add 1,861 bytes. The skater constructor advances
  at that checkpoint to 309/463 instructions and stops before component `1859f772`; it remains
  partial and earns no completion credit. Component frame/command paths, actual
  audio output, later startup, rendering and the playable level remain unfinished.

- The preceding BalanceTrick checkpoint passes 115 original/Wasm comparison
  cases and 328 completed calls, including 28 real QB fixture callbacks that
  test conditional constructor script ordering. Its ten complete routines
  cover all 185 original instructions; shared helpers receive no new credit.
  The latest checkpoint preserves this evidence and its result objects.

- The walking component now calls the complete dispatcher through the original
  object update loop. All 168 cases and 797 original calls match, including
  571 object updates, 492 walking frames and 27 real script callbacks. Tests
  cover suspension, component order, scripts that change traversal, and eight
  climb completions inside the owner loop. Five cases construct, attach,
  initialize and bind Walk before running frames. Both existing routines
  exercise all 183 instructions; this integration adds no routine count.
  The preceding module fails the first new integration case at its preserved
  partial entry. All 185 Node and Chromium suites pass, preserving all 184
  earlier results, with no numeric allowances or checker changes. The 283
  probe-word and 762 existing network-padding byte comparisons retain
  original-write provenance. Evidence is in
  `local/analysis/walk-component-checkpoint.json`. Other component frames are
  suspended in these integration fixtures. Full skater construction still stops
  before the local networking component; startup, rendering and playable
  training remain unfinished.

- Hanging now connects to the complete five-state walking dispatcher, including
  sideways traversal, corners, blocked movement, dropping and climbing out.
  Ten complete routines match across 888 cases and 2,127 original calls,
  including 38 real script callbacks. The dispatcher exercises all 142
  instructions across 391 frames, covering all five states, out-of-range
  fallthrough, cancellation and continued movement after climbing or dropping.
  Combined coverage is 1,600/1,615 instructions with no exclusions; unexercised
  reference-cleanup and contact-update failure branches remain in the count.
  No numeric allowances or checker changes are added; 303 probe-word and 510
  existing network-padding byte comparisons retain original-write provenance.
  All 184 Node and Chromium suites pass, preserving all 179 earlier result
  objects. Evidence is in `local/analysis/walk-hanging-checkpoint.json`; the
  module contains 853 unpromoted routines. At that checkpoint, startup still
  used the partial walking entry; the component integration above connects it.
  Full engine startup, rendering and playable training remain unfinished.

- Rail climbing now connects to the shared movement loop, exit animations and
  the actual script commands that finish those animations. Eight complete
  routines recover the exit-floor query, lower/upper exits, ground/air completion
  callbacks, climbing and the rail frame. All 369 cases and 1,286 original calls
  complete and match, including 48 real script callbacks and eight connected exit
  sequences. Coverage exercises all 716 instructions without exclusions. Four
  no-floor continuation cases preserve the original automatic rail re-entry.
  The common loop exercises 133/142 instructions across 400 frames and remains
  uncounted while hanging is unfinished. No numeric allowances or checker changes
  are added; 177 probe-word and 324 existing network-padding byte comparisons
  retain original-write provenance. All 179 Node and Chromium suites pass,
  preserving all 176 earlier result objects. Evidence is in
  `local/analysis/walk-rail-climb-checkpoint.json`; the latest module contains
  843 unpromoted routines. Hanging, startup, rendering and playable training
  remain unfinished.

- The complete airborne walking update now connects to the shared movement loop.
  Tests cover falls, landings, continued ground movement, ramp transfers,
  projectile scripts, and the normal pose, animation, camera and shadow updates.
  All 266 cases and 1,000 original calls complete and match, including 40 real
  script callbacks. The new airborne routine exercises all 296 instructions.
  The common loop exercises 129/142 instructions and remains uncounted because
  hanging and rail frames are unfinished. No numeric allowances are added;
  1,324 indeterminate probe-word and 378 network-padding byte comparisons use
  the unchanged checker and original-write provenance. All 176 Node and Chromium
  suites pass, preserving all 174 prior result objects. Evidence is in
  `local/analysis/walk-air-flight-checkpoint.json`; the latest module contains
  835 unpromoted routines. A successful wallplant script still has separate
  helper evidence only. Hanging/rail frames, startup, rendering and playable
  training remain unfinished.

- Six complete helpers recover ballistic lip clearance, wall-contact jumps,
  rail-target copying, airborne rail eligibility, weighted rail selection and
  direct rail catches. All 431 cases and 548 original calls complete and match,
  including 12 real collision-script callbacks. Coverage is 988/998 instructions
  with no exclusions; unexercised release, unsigned-cooldown and alignment
  instructions remain counted. No numeric, indeterminate-word or padding-byte
  allowances are added. All 174 Node and Chromium suites pass, preserving all
  171 previous result objects. Evidence is in
  `local/analysis/walk-air-catch-checkpoint.json`; the latest module contains
  834 unpromoted routines. Full airborne-frame validation and integration,
  hanging/rail updates, startup, rendering and playable training remain open.

- Three complete airborne transitions now recover swept landing/sliding,
  wallplant qualification with a synchronous script, and fixed/moving ledge
  catches. All 274 cases and 382 original calls complete and match, including
  108 real script callbacks. Coverage is 659/674 instructions with no exclusions;
  unexercised reference-release and alignment instructions remain counted.
  There are no numeric or padding-byte allowances. Landing retains 75 comparisons
  of original-write-proven indeterminate probe words; 114 ledge collision caches
  are compared at destruction. All 171 Node and Chromium suites pass, preserving
  all 168 prior result objects. Evidence is in
  `local/analysis/walk-air-transitions-checkpoint.json`; the latest module contains
  828 unpromoted complete routines. Contact jump, rail entry, full airborne
  frames, startup, rendering and playable training remain unfinished.
- Four complete airborne helpers now recover steering, plane correction,
  transfer eligibility and overhead collisions. All 551 cases and 1,204 original
  calls complete and match, exercising all 546 instructions with no exclusions,
  numeric allowances or indeterminate-field allowances. Tests cover input locks,
  forward/sideways response, preserved momentum, fixed/moving transfer geometry,
  moving-contact replacement and ceiling collision correction. Eighty ceiling
  hits include 36 velocity projections; the second query hits another surface
  24 times and misses 56 times. Sixty-four temporary collision caches are checked
  at destruction. All 168 Node and Chromium suites pass, preserving all 164 prior
  result objects. Evidence is in `local/analysis/walk-air-motion-checkpoint.json`;
  the latest module contains 825 unpromoted complete routines. These are helper
  routines, not complete airborne frames. Landing, remaining airborne transitions,
  full state integration, startup, rendering and playable training remain open.
- Ground-mode walking now completes 242 original frames across 82 cases,
  including 56 connected sequences, flat ground, walls, steps, fixed/moving
  surfaces, event callbacks, lighting, shadows, pose, animation speed and camera.
  Twelve integrated transfer cases include four successful transitions to air.
  Two complete supporting routines recover transfer eligibility and ground
  validation: 266 direct cases and 342 calls exercise 285/287 instructions with
  no exclusions. Together, the three new suites match 348 cases and 584 completed
  calls, with no numeric allowances. The partial dispatcher exercises 131/142
  instructions and earns no new routine count. Separate Node checks pass 168
  animation frames through the same export and preserve 80 unfinished-state
  boundaries. Original-write-proven probe fields receive 731 word comparisons;
  32 queued messages retain exact defined bytes with 240 padding-byte comparisons
  and 12 controls. Eight automatic collision caches are compared at destruction,
  before later calls reuse their storage; five controls check that observation.
  All 164 Node and Chromium suites pass, preserving all 161 prior result objects.
  Evidence is in `local/analysis/walk-ground-frame-checkpoint.json`; the latest
  module contains 821 unpromoted complete routines. Airborne, hanging and rail
  updates, full startup, rendering and playable training remain unfinished.
- The original walking dispatcher now reaches its return in animation state 4.
  Forty-eight connected sequences match 168 complete frames, including moving
  contact, collision correction, pose/events, animation speed, camera updates,
  cancellation and counters. The complete animation-speed parent adds one
  recovered routine: 189 direct cases and 308 calls. Together, the new suites
  compare 237 cases and 644 completed calls, with no numeric allowances.
  The parent exercises 211/216 instructions; the partial frame exercises
  114/142. Other movement states remain explicit boundaries, checked separately
  in 96 original interrupted comparisons, and the dispatcher earns no routine
  count. Thirty-three queued messages retain exact defined bytes, with 462
  comparisons of original-write-proven padding bytes and 12 protective controls.
  All 161 Node and Chromium suites pass; 159 earlier results remain unchanged.
  Evidence is in `local/analysis/walk-frame-speed-checkpoint.json`; the latest
  module contains 819 unpromoted complete routines. Ground transfer/validation,
  remaining movement states, startup, rendering and playable training remain
  unfinished. The original constructor prefix is unchanged.
- Two complete routines now recover animation-channel speed changes and component
  forwarding. All 267 cases and 547 original calls complete and match, including
  32 populated-queue cases that enqueue 40 messages. Individual/all-channel and
  relative-length behavior, low-byte flags, player/client gates, repeated updates,
  queue links and heap events are checked. The corpus exercises 157 of 171
  instructions with no exclusions; the remaining instructions include alignment
  and null-link return paths. Defined payload bytes remain exact. Three original
  uninitialized payload bytes receive byte-specific, write-traced allowances;
  12 negative/control tests prevent those allowances from hiding defined changes.
  All 159 Node and Chromium suites pass, preserving all 158 prior results.
  Evidence is in `local/analysis/walk-speed-checkpoint.json`; this module contains
  818 unpromoted complete routines. Separate original tracing established that
  the walking parent's legacy command returns unhandled before its distinct speed
  update. Its implementation is still an unpublished integration candidate.
  Full walking frames, startup, rendering and playable training remain unfinished.
- Three complete routines now recover critical-point displacement and collision
  correction, event-driven camera facing and its setter. Across three comparison
  suites, all 300 cases and 1,896 original calls complete and match: 856 calls to
  new routines and 1,040 existing dependency calls. The corpora together exercise
  all 376 new instructions without exclusions or new numeric or indeterminate
  allowances. Forty-eight three-step sequences carry static/moving collision
  corrections through pose and camera updates; eight four-frame sequences connect
  advancing animation to pose and camera updates. Limiting planes, timed rotations
  and original diagnostic arguments are checked. All 158 Node and Chromium suites
  pass, preserving all 155 preceding results. Evidence is in
  `local/analysis/walk-tail-checkpoint.json`; this module contains 816 unpromoted
  complete routines. Shared walking still needs transfer, ground validation and
  animation integration helpers, plus full state dispatch. The constructor and
  shared-frame prefixes remain unchanged; the training level is not playable.
- The preceding pose build recovered model-offset decay, up-vector restoration,
  speed/event filtering, and publication and rotation of the character's pose.
  All 358 cases and 1,168 original calls complete and match: 1,040 calls to the
  new routines and 128 existing animation calls. All 402 new instructions execute,
  with no exclusions or new numeric or indeterminate-field allowances. Sixteen
  connected four-frame sequences advance animation forward and backward, then
  publish position, orientation, velocity and model offsets with moving contacts,
  tilted up vectors and temporary rotations. The indexed state-dispatch table is
  independently checked against the complete function extent. All 155 Node and
  Chromium suites pass, preserving all 154 preceding results. Evidence is in
  `local/analysis/walk-common-checkpoint.json`; this module contains 813
  unpromoted complete routines. These are connected recovered parts of the frame;
  the full shared frame still needs collision and event helpers. Shared Walk stays
  51 / 142 and the constructor 277 / 463; the training level is not playable.
- The preceding animation build recovered animation-time access, the walking
  transition frame, final-pose commit and its script completion command.
  Twenty-four connected selection/frame/script sequences reach hanging or rail
  states. Six advance actual animation time through four frames, forward and
  reverse, before the completion script runs; five rail script callbacks fire.
  The Walk component now forwards extended commands through the original member
  dispatch path. All 129 cases and 354 original calls complete and match.
  Coverage is 282 / 285 instructions; three translated contact-failure
  instructions remain unexercised and stay in the denominator without exclusions.
  No numeric or indeterminate-field allowances were added. All 154 Node and
  Chromium suites pass, preserving all 153 preceding results. Evidence is in
  `local/analysis/walk-animation-checkpoint.json`; this module contains 808
  unpromoted complete routines. Animation channels are initialized fixture data;
  full scheduling and original asset setup remain unfinished. Shared Walk stays
  51 / 142 and the constructor 277 / 463; the training level is not playable.
- The preceding floor and ground build recovered surface probing, real
  leave/enter/fall scripts, material and moving-contact changes, step height,
  escape from moving objects, and falling/grind/rail/hang transitions. All 164
  cases and 262 original calls complete, including 38 real script callbacks.
  Coverage is 394 / 410 instructions: floor 276 / 276 and ground 118 / 134.
  Sixteen translated event-branch instructions remain unexercised because the
  preceding acceleration overwrites the event in all observed valid graphs;
  they stay in the denominator without exclusions. Defined memory, globals and
  preserved registers compare exactly. There are 512 four-byte comparisons of
  probe fields proven uninitialized by original write tracing, with later-write
  revocation and six negative checker tests. No numeric allowances were added.
  All 153 Node and Chromium suites pass and all 152 inherited result objects
  remain unchanged. Evidence is in `local/analysis/walk-grounded-checkpoint.json`;
  this module contains 803 unpromoted complete routines. Shared Walk remains
  51 / 142 instructions and the constructor 277 / 463; other movement states,
  animation/script flow, startup and browser rendering remain unfinished.
- The preceding ledge-grab build recovered five complete routines for side
  clearance, usable-side selection, weighted segment search and hanging
  transitions on fixed and moving rails. Its 894 cases and 1,256 original calls
  exercised all 1,832 new instructions without exclusions. Eighteen explicit
  grab-to-callback sequences reach hanging state, with twelve real script
  callbacks; these sequences do not establish the intervening animation flow.
  Evidence is preserved in `local/analysis/walk-grab-checkpoint.json`.
- The preceding experimental build recovers twelve helpers for upper rail entry,
  hanging, vertical clearance, moving-rail grind selection and following
  adjoining ledges. Real collision, QB callbacks and connected, disconnected,
  reversed and rejected ledge joins match the original in 559 cases and 811
  completed calls, including 60 existing probe initializations. All 1,145 new
  instructions execute without exclusions; this is not exhaustive input or
  branch coverage. Defined memory, globals and preserved registers compare
  exactly, with no new numeric or indeterminate-field allowances. All 151 Node
  and Chromium suites pass, preserving all 150 earlier result objects.
  Evidence is in `local/analysis/walk-floor-checkpoint.json`; this module
  contains 796 unpromoted complete routines. Full ledge selection and floor
  handling remain unfinished. Ground coverage remains 63 / 134, shared Walk
  coverage 51 / 142 and constructor coverage 277 / 463. The original training
  level is not playable.
- The preceding experimental build recovers the full ledge-jump and eight-probe
  walking-contact routines. Ledge-height scans, moving-wall response, velocity
  constraints, rail entry and real script cancellation match the original in
  503 cases and 680 calls: 671 complete and nine explicitly interrupted ground
  updates. Coverage is 1,241 / 1,244 instructions; three skipped alignment
  instructions remain in the denominator without exclusions. The ground parent
  now reaches 63 / 134 instructions, up from 18, and stops before floor handling;
  genuine state/control exits return normally. It is not counted as a completed
  routine. All defined memory compares exactly, including retained stack-pointer
  identities. There are 820 four-byte comparisons of copied probe fields proven
  uninitialized by original write tracing: 784 unknown fields and 36 unset scene
  fields. Any later defining write removes the allowance; six corruption checks
  verify the comparison rejects changed defined data or provenance. No numeric
  masks, NaN classification or quieting are added. All 150 Node and Chromium
  suites pass, preserving all 149 earlier result objects. Evidence is in
  `local/analysis/walk-ledge-checkpoint.json`; this module contains 784 unpromoted
  complete routines. Shared Walk frame coverage remains 51 / 142 and constructor
  coverage 277 / 463. Floor handling, full walking/rail frames, remaining startup,
  rendering and original playable training remain unfinished.
- The preceding experimental build recovers eleven Walk helpers for gravity,
  state changes, buffered input, moving-platform velocity, facing/probe
  directions and vertical-rail selection and entry. Real collision, gameplay
  flags, QB/math/timing and contact cleanup match the original in 825 cases and
  1,399 completed calls. Coverage is 1,011 / 1,014 instructions; three reference
  cleanup instructions have documented unreachable-path proofs after a false
  collision query. The defensive cleanup remains implemented. There are no new
  numeric masks, NaN classification, quieting or uninitialized-byte allowances.
  Twelve explicit rail-selection-to-callback-target sequences reach state 3;
  the intervening animation/movement frame remains unrecovered. All 149 Node
  and Chromium suites pass, preserving all 148 earlier result objects. Evidence
  is in `local/analysis/walk-transition-checkpoint.json`; this module contains
  782 unpromoted complete routines. Ground-parent coverage remains 18 / 134,
  shared Walk frame coverage 51 / 142 and constructor coverage 277 / 463.
  Full walking/rail frames, ledge jumps, remaining startup, rendering and
  original playable training remain unfinished.
- The preceding experimental build recovers seven Walk ground helpers: platform
  motion, collision-cache preparation, velocity-facing interpolation, analog
  target speed, slope attenuation, acceleration/steering and two-probe step
  height. Real static and moving geometry, reference cleanup and QB/math helpers
  execute in 485 cases and 953 calls: 941 complete and 12 explicitly interrupted
  ground-parent calls. Coverage is 1,249 / 1,259 instructions; ten unexercised
  instructions have documented unreachable-path proofs under the initialized,
  single-threaded graph contracts. Their defensive paths remain implemented.
  The suite adds no numeric masks, NaN classification, quieting or uninitialized
  byte allowances. All 148 Node and Chromium suites pass, with all 147 earlier
  result objects unchanged. Evidence is in
  `local/analysis/walk-ground-checkpoint.json`; this module contains 771
  unpromoted complete routines. The ground parent reaches 18 / 134 instructions,
  running platform motion, cache preparation and acceleration in the original
  order before stopping at transition handler `52c2c0`. The parent is not counted
  as recovered. Constructor coverage remains 277 / 463 and shared Walk frame
  coverage remains 51 / 142. Ground transitions, other movement states, remaining
  startup, rendering and original playable training remain unfinished.
- The preceding experimental build recovers eleven Walk routines: construction,
  disposal, camera initialization, dependency binding, camera-relative input,
  owner orientation and score-dependent decay. The shared component builder
  creates, links and disposes Walk; skater construction now proceeds through it
  to the next component. All 505 new instructions are exercised across 848
  cases and 1,474 calls: 1,330 complete, 32 interrupted constructor calls and
  112 interrupted frame-prefix calls. Allocation failure is checked explicitly.
  There are no numeric masks, NaN classification or uninitialized-byte allowances
  in this suite. All 147 Node and Chromium suites pass, with all 146 earlier
  result objects unchanged. Evidence is in
  `local/analysis/skater-walk-checkpoint.json`; this module contains 764
  unpromoted complete routines. The partial constructor reaches 277 / 463
  instructions and stops before component `7cd3e6d5`. The partial Walk frame
  reaches 51 / 142 instructions and stops before its five movement-state handlers
  or remaining common tail; neither partial routine counts toward the estimate.
  Walking movement/collision, remaining startup, rendering and playable training
  remain unfinished.
- The preceding experimental build recovers SkaterCleanupState and extends local
  skater construction through it to Walk. Twenty complete routines handle its
  lifecycle and full frame, light direction virtuals, camera setters, shadow
  direction and keyed projection matrices. Real look-at and orthographic math,
  state transitions, signed blend counters and component dispatch run in 441
  cases: 882 completed calls and 32 interrupted constructor calls. All 557 new
  instructions are exercised; this is not exhaustive input or branch coverage.
  Two declared global float-store lanes require precise physical x87 quieting
  for 28 signaling words, retaining their signs and payloads; five corruption
  checks confirm the comparison rejects changed results. No NaN classification,
  numeric masks or uninitialized-byte allowances are added. All 146 Node and
  Chromium suites pass with all 145 earlier results unchanged. Evidence is in
  `local/analysis/skater-cleanup-checkpoint.json`; the module contains 753
  unpromoted complete routines. The partial constructor reaches 265 / 463
  instructions and stops before Walk. Renderer creation/rendering, remaining
  startup/frames, later score linkage and original playable training remain
  unfinished.
- The preceding experimental build recovers SkaterFinalizePhysics and extends local
  skater construction through it. Seven complete routines handle lifecycle,
  dependency binding, the full frame, degenerate matrix repair and animation
  speed clamping. Real stat lookup and matrix operations match the original in
  354 cases: 632 completed calls and 32 interrupted constructor calls. Tests
  cover movement thresholds, sound/animation state, dirty flags, matrix repairs,
  actual owner dispatch and shared construction/disposal. Coverage is 375 / 381
  instructions; six allocation-failure instructions remain unexercised, without
  exclusions or numeric allowances. The experimental shared vector normalizer
  now preserves the original negative NaN encoding for infinity times zero.
  All 145 Node and Chromium suites pass, preserving all 144 earlier results.
  Evidence is in `local/analysis/skater-finalize-checkpoint.json`; the module
  contains 733 unpromoted complete routines. The partial skater constructor
  reaches 257 / 463 instructions and stops before SkaterCleanupState. Remaining
  startup/frames, later score linkage, camera/rendering and playable training
  remain unfinished.
- The preceding experimental build recovers the Trigger component and connects it
  to local skater construction. Eight complete routines handle creation, disposal,
  initialization, event-mask commands, saved collision records and movement
  callbacks. Actual static/moving collision queries and QB scripts run in 307
  cases: 481 completed calls and 32 intentionally interrupted constructor calls.
  Callback changes to owners, positions and records match the original. Coverage
  is 293 / 294 instructions; one skipped alignment instruction remains in the
  denominator, without exclusions, numeric masks or new unknown-byte allowances.
  All 144 Node and Chromium suites pass, preserving all 143 earlier results.
  Evidence is in `local/analysis/trigger-checkpoint.json`; the module contains
  726 unpromoted complete routines. The partial skater constructor reaches
  249 / 463 instructions and stops before SkaterFinalizePhysics. Remaining
  startup/frames, later score linkage, camera/rendering and playable training
  remain unfinished.
- The preceding experimental build completes EndGap and connects all six Gap commands
  through the real component dispatcher. Gap awards, predicate scripts, required
  tricks, history, success events and callback-driven list changes match the
  original in 188 cases / 359 calls. Full start-gap, trick-score, finish-gap and
  secondary-script sequences run in controlled tests. Coverage is 527 / 529
  instructions, including the complete dispatcher; heap initialization and one
  null-successor exit remain unexercised, without exclusions or numeric masks.
  Twelve retained pointers to temporary formatted text are checked by original
  formatter provenance, Wasm stack bounds and exact contents. This preserves the
  original dangling-pointer behavior; it does not establish safe text ownership.
  All 143 Node and Chromium suites pass, preserving all 142 earlier results.
  Evidence is in `local/analysis/gap-end-checkpoint.json`; the module contains
  718 unpromoted complete routines. Tests still supply initialized graphs and the
  later score-state link. Skater construction stops before Trigger; remaining
  startup/frames, camera/rendering and original playable training are unfinished.
- The preceding experimental build recovers full score insertion and bounded history
  compression. Repeated-trick multipliers, score-limit handling, formatted text,
  combo events and live script callback changes match the original in 369 cases /
  1,904 calls. Coverage is 553 / 556 instructions; one platform heap initialization
  and two skipped alignment instructions remain unexercised, without exclusions
  or numeric masks. Compression copies 112 uninitialized string-tail bytes per
  record: only those proven bytes have a definedness allowance, removed as later
  writes define them. All defined values compare exactly. All 142 Node and
  Chromium suites pass, preserving all 141 earlier results. Evidence is in
  `local/analysis/score-insert-checkpoint.json`; the module contains 716 unpromoted
  complete routines. EndGap, remaining skater startup/frames, camera/rendering and
  original playable training remain unfinished.
- The preceding experimental build connects the fifth Gap command: it follows level
  node links and executes the first linked script through the real owner and QB
  interpreter. Sixteen complete routines also recover score storage, range
  calculation, timed-trick name recording, synchronous score UI notification and
  level-specific gap-history updates. They match the original in 360 cases /
  998 calls, without numeric allowances. Coverage is 508 / 520 instructions;
  heap initialization, allocation failure and null-successor exits remain
  unexercised. Required initialized lists terminate at sentinel nodes. The two
  gap command suites together exercise 121 / 126 dispatcher instructions; the
  remaining EndGap route is unavailable and the dispatcher is not counted
  complete. All 141 Node and Chromium suites pass, preserving all 140 earlier
  result objects. Evidence is in `local/analysis/gap-links-checkpoint.json`;
  the module contains 714 unpromoted complete routines. Full score insertion,
  history compression, EndGap, remaining skater startup/frames, camera/rendering
  and original playable training remain unfinished.
- The preceding experimental build recovers full StartGap, secondary trick
  registration and checking, concrete gap nodes, owned strings and list cleanup.
  Fifteen complete routines match the original-instruction oracle in 396 cases /
  984 calls. Four commands are connected through the actual component descriptor;
  the dispatcher remains partial and does not earn a recovered-routine count.
  EndGap and linked-node trigger dispatch are still unavailable. All 140 Node and
  Chromium suites pass; all 139 earlier results are unchanged. Coverage is
  810 / 813 instructions, with two platform heap-initialization calls and one
  allocation-failure branch unexercised, without exclusions or numeric allowances.
  Signaling-NaN payloads match the emulator; physical x87 behavior for those
  encodings has not been established. Evidence is in
  `local/analysis/gap-start-checkpoint.json`; the module contains 698 unpromoted
  complete routines. Tests use initialized graphs with an explicit score-state
  link. Skater construction still stops before Trigger; remaining behavior,
  camera, rendering and playable training remain unfinished.
- The preceding experimental build recovers nine profile and score-history queries
  needed by gap start and end commands. Named tricks, profile bindings, created
  tricks, repeated taps, spin checks and trailing-match subtraction match the
  original in 498 cases / 1,408 calls. All returns, arena bytes, globals and
  preserved registers compare exactly, with no numeric allowances. Coverage is
  501 / 502 instructions; one skipped alignment instruction remains unexercised,
  with no exclusions. All 139 Node and Chromium suites pass; all 138 previous
  result objects are unchanged. Evidence is in
  `local/analysis/gap-score-checkpoint.json`; the module contains 683 unpromoted
  complete routines. These queries are not yet connected to the gap commands.
  Gap start/end, concrete node and string ownership, remaining skater behavior,
  camera, rendering and playable training remain unfinished. Skater construction
  still stops before Trigger.
- The preceding experimental build completes the SkaterAdjustPhysics frame:
  ground correction, moving-object escape and contact reacquisition, shadow
  placement, state transitions, and surface-dependent model/global lighting.
  Fourteen complete routines match the original in 478 cases / 1,032 calls.
  The real owner dispatcher reaches the recovered component in 24 frames;
  original callees perform 842 collision queries and emit 65 events. Coverage
  is 955 / 960 instructions: two skipped alignment and three secondary-probe
  cleanup instructions remain unexercised, with no exclusions. The new suite
  compares all returns, arena bytes, globals and heap effects exactly, including
  quiet-NaN payloads and overlapping factor arrays. All 138 Node and Chromium
  suites pass; all 137 previous result objects are unchanged. Evidence is in
  `local/analysis/skater-ground-checkpoint.json`; the module contains 674
  unpromoted complete routines. The component update slot now calls the full
  recovered frame. These tests use synthetic geometry and initialized graphs,
  not a playable training skater. Construction still stops before Trigger.
  Gap scoring/commands, other skater behavior, camera, rendering and playability
  remain unfinished.
- The preceding experimental build recovers SkaterAdjustPhysics startup and the
  moving-surface containment and escape helpers. Eight complete routines match
  the original in 313 cases / 565 calls. Real collision queries check one-sided
  surfaces, repeated probes, reference cleanup and the three escape choices:
  previous position, velocity-based position, or the surface fallback. Overlaps,
  raw endpoint words and wide velocity exponents compare exactly. Coverage is
  355 / 376 new instructions; seven allocation-failure and fourteen probe-cleanup
  instructions remain unexercised, with no exclusions. Local skater construction
  creates AdjustPhysics and stops before Trigger; 32 interrupted constructor
  calls cover 241 / 463 instructions without counting it complete. The shared
  builder creates AdjustPhysics, State and Physics in either order and disposes
  them. All 137 Node and Chromium suites pass; all 136 previous result objects
  are unchanged. Evidence is in `local/analysis/skater-adjust-checkpoint.json`;
  the module contains 660 unpromoted complete routines. The new collision cases
  use synthetic geometry. Full AdjustPhysics frame, ground correction and
  lighting integration remain unfinished, with an explicit trap in its update
  slot. Gap scoring/commands, remaining skater assembly, camera, rendering and
  playable training remain unfinished.
- The preceding experimental build recovers SkaterGap startup, dependency linking,
  frame cancellation and secondary-list cleanup. Eleven complete routines match
  the original in 364 cases / 708 calls, including skating, walking and vehicle
  states, overlapping outputs, counter wrap and real list-node destruction.
  Coverage is 343 / 348 new instructions; five factory allocation-failure
  instructions remain unexercised, with no exclusions. All returns, arena bytes,
  globals and heap effects compare exactly, without NaN allowances. The shared
  object builder creates Gap, State, PhysicsControl and Physics in either order,
  links and destroys them. Local skater construction now creates Gap and stops
  before SkaterAdjustPhysics; 32 interrupted constructor calls cover 233 / 463
  instructions without counting it complete. All 136 Node and Chromium suites
  pass; all 135 previous result objects are unchanged. Evidence is in
  `local/analysis/skater-gap-checkpoint.json`; the module contains 652 unpromoted
  complete routines. Gap start/end scoring and script commands remain unfinished,
  as do remaining skater assembly, Trick/PhysicsControl frame and commands,
  Score frame/commands/disposal, Input binding, camera, rendering and playability.
- The preceding experimental build recovers the complete SkaterRotate component:
  immediate turns, timed rotation, turning toward named level points, creation,
  physics linking and disposal. Eleven complete routines, including four math
  helpers, match the original in 809 cases / 1,646 calls. The shared object
  builder creates Rotate and Physics in either order, runs commands and frame
  updates, then destroys them. Local skater construction now creates Rotate and
  stops before SkaterGap; 32 interrupted constructor calls exercise 221 / 463
  instructions without counting the constructor as complete. New routine
  coverage is 679 / 685 instructions; six factory allocation-failure instructions
  remain unexercised, with no exclusions. Memory, globals and heap effects
  compare exactly; 366 double returns, including two NaN payloads, are checked
  as raw bits. All 135 Node and Chromium suites pass, with all 134 previous
  result objects unchanged. Evidence is in
  `local/analysis/skater-rotate-checkpoint.json`; the module contains 641
  unpromoted complete routines. The existing SDK trigonometric boundary remains
  explicit; active rotation checks use finite angles. Remaining skater assembly,
  Trick/PhysicsControl frame and commands, Score frame/commands/disposal,
  Input binding, camera, rendering and playable training remain unfinished.
- The preceding experimental build recovers Trick and PhysicsControl startup and
  disposal. Local skater construction creates both, initializes Physics, and
  stores their owner links; it now stops before SkaterRotate. Twelve complete
  routines match the original in 167 cases / 326 calls, including 32 interrupted
  skater-constructor calls. The shared object builder also creates, links and
  destroys State, MatrixQueries, Trick, PhysicsControl and Physics in both
  creation orders. Coverage is 258 / 269 new instructions; eleven factory
  allocation-failure instructions remain unexercised, with no exclusions.
  The new suite compares all returns, arena bytes, globals and heap effects
  exactly, without NaN allowances. All 134 Node and Chromium suites pass;
  all 133 previous result objects, including the declared MatrixQueries math
  boundary, are unchanged. Evidence is in
  `local/analysis/skater-trick-checkpoint.json`; the module contains 630
  unpromoted complete routines. The partial skater constructor now covers
  213 / 463 instructions and is not counted complete. Trick and PhysicsControl
  frame/commands, Score frame/commands/disposal, Input binding, remaining
  skater assembly, camera, rendering and playable training remain unfinished.
- The preceding experimental build recovers SkaterMatrixQueries: all eight
  heading, slope, pitch, roll and yaw commands, plus creation, physics lookup,
  matrix copying and disposal. Local skater construction now creates this
  component and stops before Trick; the remote-player boundary is unchanged.
  Seven complete routines cover 422 / 428 original instructions, with six
  allocation-failure instructions unexercised and no exclusions. There are
  355 cases / 557 calls, including 32 interrupted skater-constructor calls.
  All memory, globals and heap effects compare exactly. Two deliberately
  infinite-angle calls use the declared Intel/SDK math boundary, retaining
  raw emulator results and one documented positive-infinity discrepancy.
  All other returns compare with the original, without NaN masks.
  All 133 Node and Chromium suites pass; all 132 earlier result objects are
  unchanged. Evidence is in `local/analysis/skater-matrix-checkpoint.json`;
  the module contains 618 unpromoted complete routines. The skater constructor
  remains partial, with 177 / 463 instructions exercised. Trick startup,
  Score frame/commands/disposal, Input binding, remaining skater assembly,
  camera, rendering and playable training remain unfinished.
- The preceding experimental build advances the original skater constructor
  through Score creation and player-ID assignment. Seven recovered routines
  cover Score storage, balance configuration and component initialization.
  The unit suite matches the original in 268 cases / 484 calls, including
  32 interrupted constructor calls. A separate four-case / twelve-call
  comparison loads the original `physics.qb` and `panelstuff.qb`, then creates
  Score with their seven-point balance curve and normal/split-screen layouts.
  New instruction coverage is 301 / 311, with three alignment instructions
  and seven allocation-failure instructions unexercised, without exclusions.
  All 132 Node and Chromium suites pass, with all 130 earlier results
  unchanged. Evidence is in `local/analysis/skater-score-checkpoint.json`;
  the module contains 611 unpromoted routines. The constructor stops before
  SkaterMatrixQueries or SkaterNonLocalNetLogic.
  Score frame/commands/disposal, remaining skater startup, camera, rendering
  and playability remain unfinished.
- An earlier experimental build begins the original skater constructor: it
  registers the player and creates Suspend, bounds, State, attachment and,
  for a local player, Input components. It explicitly stops before Score
  creation; no complete constructor or playable scene is claimed. Eight
  complete helper routines and this partial path match the original in
  114 cases / 228 calls, including 32 interrupted constructor calls. Helper
  coverage is 161 / 175 instructions, with fourteen allocation-failure
  instructions unexercised and no exclusions. The constructor separately
  covers 145 / 463 instructions. All 130 Node and Chromium suites pass, with
  all 129 earlier results unchanged. Evidence is in
  `local/analysis/skater-construction-checkpoint.json`; the module contains
  604 unpromoted routines, and the main recovery count is unchanged.
  Input binding, remaining skater assembly, camera, rendering and playability
  remain unfinished.
- The preceding experimental build completes all fourteen Input script commands
  and their registration, adding fifteen recovered routines. All 856 cases /
  1,090 calls match the original exactly, covering all 339 new instructions
  without exclusions. Every descriptor and named QB dispatch is checked.
  Actual Chromium keyboard and script actions verify input gating, event
  toggles, stick outputs and task cleanup. All 129 Node and Chromium suites
  pass, with all 128 previous results unchanged. Evidence is in
  `local/analysis/input-command-checkpoint.json`. The module contains 596
  unpromoted routines; the main recovery count is unchanged. Debug output and
  SDK trigonometry use explicit platform adapters. Full skater startup, camera,
  rendering, production platform services and playability remain unfinished.
- The preceding experimental build recovers 28 Input lifecycle and device-task
  routines. The original shared object builder creates Input, registers both
  controller tasks, runs the original events and pad decoder, and removes the
  tasks during owner destruction. All 460 cases / 1,252 calls match exactly;
  coverage is 700 / 707 instructions, with seven allocation-failure instructions
  unexercised and no exclusions. Actual Chromium keyboard presses verify all
  eight bindings through this startup path, followed by successful task cleanup.
  All 128 Node and Chromium suites pass, with all 127 previous results unchanged.
  Evidence is in `local/analysis/input-lifecycle-checkpoint.json`. The module
  contains 581 unpromoted routines; the main recovery count is unchanged.
  Force-feedback calculations are compared at an explicit test hardware boundary.
  Twelve Input commands, full skater startup, camera, rendering, production
  platform services and playability remain unfinished.
- The preceding experimental build recovers eight Input callback routines, including
  ordered button events, menu blocking and both controller slots. All 481 cases /
  978 calls match the original exactly, including script wake-up and real QB
  event handlers. Coverage is 418 / 419 instructions; one allocation-failure
  instruction remains unexercised, with no exclusions. Actual Chromium keyboard
  presses verify all eight bindings through the original device callback,
  event dispatcher and pad decoder. All 127 Node and Chromium suites pass;
  all 126 earlier results are unchanged. Evidence is in
  `local/analysis/input-callbacks-checkpoint.json`. The module contains 553
  unpromoted routines; the main recovery count is unchanged. The live check uses
  initialized test objects. Input task registration, component initialization,
  skater startup, camera, rendering and playability remain unfinished.
- The preceding experimental build recovers nine controller-pad routines, including
  the complete packet decoder at `0x46bda0`. All 971 cases / 2,197 calls match
  the original exactly, covering all 675 instructions without exclusions.
  Checks include every raw stick byte, button edges, suppression deadlines,
  digital directions, overlapping input storage and the original reset quirks.
  The first browser keyboard adapter is in `src/platform/browser_input.mjs`.
  Actual Chromium key events verify all eight bindings through the recovered
  decoder; focus-loss and cleanup checks also pass. All 126 Node and Chromium
  suites pass, with all 125 earlier results unchanged. Evidence is in
  `local/analysis/input-pad-checkpoint.json`. The module contains 545 unpromoted
  routines; the main recovery count is unchanged. The live input check uses a
  separate controller state, so full skater startup, scene integration, camera,
  rendering and playability remain unfinished.
- The preceding experimental build recovers the complete Rigidbody update at
  `0x430e20`, debug traversal at `0x42d9d0`, and scene manager update at
  `0x45f4a0`, and connects them to the real component tables. All 455 unit
  cases / 871 calls match exactly. Coverage is 585 / 594 instructions; nine
  unexercised instructions are documented, with no exclusions. The original
  63-call training startup now continues through four complete manager passes,
  visiting 32 objects and 19 physics props per pass. A separate test wakes those
  19 props and verifies two further passes against the original level geometry,
  including movement, contacts and settling. All 125 Node and Chromium suites
  pass; all 122 earlier results are unchanged. Evidence is in
  `local/analysis/rigidbody-update-checkpoint.json`. The module contains 536
  unpromoted routines; the main count is unchanged. The wake input is explicit
  test setup. Skater controls, rendered frames, production platform services
  and playable integration remain unfinished.
- The preceding experimental build recovers the complete skater-to-prop kick at
  `0x42c140` and its ordinary-scene lookup helper at `0x48c770`. All 395 cases /
  407 calls match the original exactly, covering all 431 instructions without
  exclusions. Checks include reference order, contact thresholds, activation,
  real attached scripts, shadow geometry flags, sound playback, and wrapped
  cooldown timers. All 122 Node and Chromium suites pass; all 121 earlier
  results are unchanged. Evidence is in
  `local/analysis/rigidbody-kick-checkpoint.json`. The module contains 533
  unpromoted routines; the main count is unchanged. Full Rigidbody and scene
  updates, controls, rendering and playable integration remain unfinished.
  The existing 63-call scene trace is preserved without extension.
- The preceding experimental build recovers full Rigidbody contact assembly at
  `0x42c950`, using the original cache builder, segment probes and sphere queries.
  All 1,833 unit cases / 1,870 calls match exactly, including coincident normals
  and recorded but inactive contacts. Coverage is 363 / 369 instructions; six
  unexercised instructions are documented, with no exclusions. Tests using all
  19 original training props add 95 cases / 285 calls for real shape rotation
  and contact assembly at five vertical placements. All 121 Node and Chromium
  suites pass; all 119 earlier results are unchanged. Evidence is in
  `local/analysis/contact-assembly-checkpoint.json`. The module contains 531
  unpromoted routines; the main count is unchanged. Full Rigidbody and scene
  updates, controls, rendering and playable integration remain unfinished.
  The existing 63-call scene trace is preserved without extension.
- The preceding experimental build connects sphere contacts to complete static-object,
  scene and probe queries, including cache fallback and the original spatial grid.
  All 533 unit cases / 635 calls match the original exactly, covering all 560
  instructions in four new routines without exclusions. Queries on the original
  training grid and 605 collision instances add 1,122 cases / 3,366 calls, using
  stationary and swept spheres near 561 original triangles. All 119 Node and
  Chromium suites pass, with all 117 earlier results unchanged. Evidence is in
  `local/analysis/sphere-query-checkpoint.json`. The module contains 530 unpromoted
  routines; the main count is unchanged. Full Rigidbody contact assembly,
  complete object updates and playable integration remain unfinished. The
  63-call scene trace is unchanged.
- The preceding experimental build recovers the full swept sphere/triangle routine
  at `0x40ec90`, its moving-segment and vertex-edge helpers, and array construction.
  All 7,370 unit cases / calls match the original exactly. Every one of the
  swept-triangle routine's 992 instructions is covered; total coverage is
  1,576 / 1,593. Seventeen defensive instructions in the segment helper remain
  unexercised and are explicitly recorded, with no coverage exclusions.
  Four trajectories on each of 561 original training triangles pass another
  2,244 cases / 11,220 calls, including two approaching-sphere misses in the
  original. All 117 Node and Chromium suites pass; all 115 earlier results are
  unchanged. Evidence is in `local/analysis/sphere-contact-checkpoint.json`.
  The module contains 526 unpromoted routines; the main count is unchanged.
  Scene contact queries, full contact assembly, complete object updates and
  playable integration remain unfinished. The 63-call scene trace is unchanged.
- The preceding experimental build recovers eight segment, capsule and moving-contact
  geometry routines. All 5,832 cases / 6,332 calls match the original exactly,
  covering all 1,150 instructions without exclusions or NaN classification.
  Tests on 561 actual training-level edges add 1,683 cases / 8,415 calls using
  the original vertex accessor, capsule tests and segment/sphere intersections.
  All 115 Node and Chromium suites pass, with all 113 earlier results unchanged.
  Evidence is in `local/analysis/sphere-sweep-checkpoint.json`. This module now
  contains 522 unpromoted routines; the main recovery count remains unchanged.
  These are prerequisites for full moving-sphere/triangle collision, which still
  needs three larger routines. Scene contact queries, complete object updates
  and playable integration remain unfinished. The 63-call scene trace is unchanged.
- The preceding experimental build recovers four sphere-geometry routines: sphere
  and probe construction, point-to-triangle distance and stationary sphere
  contact. All 2,259 cases / 2,662 calls match the original, covering every one
  of their 614 instructions. Exact comparisons include degenerate return bits.
  A separate integration check reads original vertices from 561 training-level
  triangles and passes 1,683 cases / 8,415 calls, preserving an original failure
  on a very thin triangle. All 113 Node and Chromium suites pass, with all 111 earlier
  results unchanged. Evidence is in `local/analysis/sphere-geometry-checkpoint.json`.
  This module contains 514 unpromoted routines; the main count remains unchanged.
  Moving-sphere collision, full scene contact detection and complete Rigidbody
  updates remain unfinished. The existing 63-call scene trace is unchanged.
- The preceding experimental build recovered the complete Rigidbody contact solver
  at `0x430140`: normal impulses, directional friction, penetration correction,
  the iteration-limit fallback and actual impact scripts/Sound dependencies.
  Its 338 cases / 418 calls match the original exactly, covering all 688
  executable instructions; two unreachable alignment instructions are excluded.
  All 111 Node and Chromium suites pass, with all 110 earlier results unchanged.
  Evidence is in `local/analysis/rigidbody-solver-checkpoint.json`. This module
  contains 510 unpromoted routines; the main recovery count remains unchanged.
  The existing 63-call training trace is preserved without extension. Full
  contact detection, Rigidbody updates and playable scene integration remain.
- The preceding experimental build recovered six routines: the three Motion
  rotation commands, their shared direction helper, and the complete command-table
  initializer and registration. Its 621 unit cases / 1,275 calls match the original
  instructions, covering all 722 instructions without exclusions. All 110 Node
  and Chromium suites pass, with all 108 earlier results unchanged. Evidence is in
  `local/analysis/motion-rotation-checkpoint.json`. This module contains
  509 unpromoted routines; the main recovery count below remains unchanged.
  The other 45 members of this Motion table remain explicit unavailable stops;
  they are not counted as recovered bodies.
- The verified browser training trace now completes 63 calls with no interrupted
  calls. It preserves the startup, barrel and fire-effect updates, then loads the
  original archived level script and runs both training fans through `TR_Fan01`
  and `Obj_Rotx`. Each fan completes four object updates with changing matrices
  that match the original exactly. The earlier fire effect still emits two
  particles and releases its setup script. These checks verify simulation state,
  not rendered frames. A separate original-code scene-manager pass completes all
  32 current objects, including 19 idle Rigidbody owners; that complete pass has
  not been ported to the browser. Full Rigidbody updates, complete scene updates,
  skater control, rendering, input, audio, and playability remain unfinished.
- Restored 10,696 installed files from the supplied three BIN/CUE discs, without
  running the Windows installer. Extraction details are in
  `local/extraction-manifest.json`.
- Pinned an unpacked, **modified** PC executable by SHA-256 in `tools/specimen.py`.
  It is not a pristine retail reference. The protected disc executable is preserved
  separately and differs from the installer's executable metadata.
- Verified the executable's table of 1,254 script bindings, representing 1,163
  distinct function addresses. These names help locate level and skater behavior.
- Imported the executable into Ghidra. Its analysis currently identifies 11,637
  functions. Generated pseudocode remains under ignored `local/ghidra-export/`;
  it is not counted as recovered, buildable source.
- Recovered 1,156 engine and runtime functions as C. They are behavior-tested
  against the pinned x86 instructions, **not** byte-matched to the original compiler.
- Integrated 65 physics script commands and two registration routines into the main
  engine. The six added browser suites pass 18,928 cases / 38,558 calls, including
  actual named-script dispatch through the original physics descriptor table.
  The complete main Chromium run passes all 159 suites.
- A separate experimental build verifies 17 additional routines, including 16
  physics script commands for parameters, airtime, script outputs, kick eligibility
  and grind-off events. Its five Chromium suites pass 5,510 cases / 12,515 calls,
  including invocation of all 16 commands by name. These routines are not included
  in the main recovery count. Evidence is in
  `local/analysis/physics-command-values-browser.json`.
- The native `Change` command was recovered in a separate experiment, with
  616 cases / 1,229 calls matching the original. After loading the original
  time-of-day and training QB files, Chromium executes `TR_startup` far enough
  to change `tod_manager_inactive` from 0 to 1. It then deliberately stops before
  the unrecovered `LoadSkeleton` handler, with matching memory and arguments for
  `skeletons/CS_Cardboard.ske`. This is a partial startup trace with an initialized
  script runtime, not a completed level boot. Evidence is in
  `local/analysis/training-startup-browser.json`; the main recovery count is unchanged.
- Four more routines now recover the skeleton buffer parser, construction and
  cleanup, and quaternion-to-matrix conversion. All 58 extracted skeletons,
  including the training script's 34-bone prop, match the original arithmetic
  exactly. Chromium passes 463 cases / 809 calls, plus the earlier `Change` and
  partial-startup checks. Only arithmetic NaNs produced by deliberately overlapping
  test buffers use classification comparisons. This experimental build still
  needed the asset and file-loading path before `LoadSkeleton` could run in startup.
  Evidence is in `local/analysis/skeleton-buffer-browser.json`; these four routines
  are not included in the main recovery count.
- The skeleton asset class now adds 13 recovered routines for file/buffer loading,
  parsing, state changes and cleanup. Chromium passes 310 cases / 1,220 calls
  using all 58 skeletons, including deferred read completion, missing-file handling
  and ownership checks. File access uses an explicit comparison interface with
  resident bytes; a production browser filesystem and archive lookup remain.
  At that checkpoint the asset factory and native `LoadSkeleton` command were
  pending. Evidence is in
  `local/analysis/skeleton-asset-browser.json`; the main recovery count is unchanged.
- The next experimental build recovers 22 asset-factory, lifetime and native
  routines. Its 738 cases / 790 calls compare all factory type branches, failure
  disposal, dependency links and waiting behavior. The unchanged `TR_startup`
  script now completes in both the original instruction emulator and Chromium:
  it changes the time-of-day value, loads the 34-bone `CS_Cardboard` skeleton,
  registers the ready asset and releases its temporary file buffer. All five
  Chromium suites pass. This starts from initialized runtime services and uses
  original resident file bytes; cold boot, production archive access, `TR_Setup`
  scene creation and playable level integration remain. Evidence is in
  `local/analysis/asset-factory-browser.json`. These 22 routines are not included
  in the main recovery count; this build contains 40 experimental routines,
  while the 17 physics routines remain in their separate build.
- Four more experimental routines recover `GameModeEquals`, node-prefix lookup
  and the checksum-or-text scene-name getter. Their 985 cases / 1,091 calls match
  the original, covering all 174 instructions. After loading the original
  `gamemode.qb`, Chromium runs `TR_Setup` through its career and free-skate
  decisions. Both traces deliberately stop before the unrecovered `Kill`
  command, with matching arguments and memory. Prefix lookup uses populated
  indexes; building those indexes and implementing scene-object changes remain.
  All nine suites pass, including the completed `TR_startup` and earlier asset
  checks. Evidence is in `local/analysis/training-mode-browser.json`. This build
  now contains 44 experimental routines; the main recovery count is unchanged.
- Nine additional experimental routines recover scene-state dependencies: rail
  and emitter enabling, collision flags and render dispatch, light removal,
  lookup-table clearing, scene/network getters and reentrant object traversal.
  Their 1,144 cases / 2,105 calls match the original across all 350 instructions,
  including removal during traversal and nested callbacks. All twelve Chromium
  suites pass, retaining the earlier training traces. Rendering callbacks in
  these comparisons are test witnesses; the actual renderer and remaining
  `Kill` dispatch/lifetime paths are still unfinished. The training setup trace
  still stops before `Kill`. Evidence is in `local/analysis/scene-state-browser.json`.
  This build contains 53 experimental routines; the main recovery count remains
  unchanged, and the game is not playable.
- Eleven further routines recover direct/deferred object deletion, the actual
  `Kill` object callback, dead-object queuing/flushing, event subscription/waiting
  and proximity-trigger shutdown. Their 271 cases / 1,035 calls include real
  registry removal, base-object destructors, owned-script cleanup and cached-QB
  spawning. All fifteen Chromium suites pass. The remaining scene dispatcher,
  geometry bookkeeping and node loading still prevent the full training setup
  from running; this is not a playable build. Evidence is in
  `local/analysis/scene-lifetime-browser.json`. The experimental build now has
  64 additional routines; none are added to the main recovery count yet.
- Five more experimental entry points now recover the complete `Kill` command,
  its class dispatch and auxiliary geometry enabling. All 148 cases / 279 calls
  match the original, covering all 205 instructions in those entry points.
  Tests exercise actual object deletion and scene-state changes, name/prefix
  selection and multiplayer filtering. The shared dispatcher is specialized for
  `Kill`; its other operations are not claimed. All sixteen Chromium suites pass.
  Separately, the original index builder successfully registers the training
  file's 1,917 nodes and finds five targets for its first career-mode prefix.
  Porting that builder, creating scene objects and connecting rendering remain;
  the prior `TR_Setup` trace still stops before `Kill`. Evidence is in
  `local/analysis/scene-kill-browser.json` and
  `local/analysis/training-node-index-discovery.json`. This experimental build
  contains 69 additional routines. The main count is unchanged; the game is not
  playable yet.
- Twelve additional routines now build node-name indexes and prefix lists and
  convert links between nodes. Across 94 cases / 133 calls, the recovered code
  matches the original, including loading and indexing all 1,917 nodes from the
  unchanged training QB file. It finds the five career-mode skateboard targets
  in their original order and the free-skate wall at index 1,436. All eighteen
  Chromium suites pass. These checks start with caller-bound array metadata;
  complete node registration, coordinate conversion and optional link-group
  processing remain. They do not advance the earlier `TR_Setup` trace. Evidence
  is in `local/analysis/node-index-browser.json`. This experimental build contains
  81 additional routines; the 17 physics routines remain in a separate build.
  The main recovery count is unchanged, and training is not playable yet.
- Full node-array registration is now recovered in twelve further routines,
  including iteration, coordinate conversion, reference cleanup and link-group
  assignment. The unchanged training file registers all 1,917 nodes and produces
  ten link groups; repeated registration is correctly rejected. The 153 new
  cases / 403 calls pass alongside all earlier checks, for twenty passing
  Chromium suites. Synthetic signaling-NaN coordinates use exact x87 quiet-bit
  checks with raw emulator differences recorded. Evidence is in
  `local/analysis/node-registration-browser.json`. This build contains 93
  experimental routines, separate from the 17 physics routines. Scene-object
  creation, rendering and further `TR_Setup` execution remain; the game is not
  playable, and the main recovery count is unchanged.


| Source | Original addresses | Validation |
| --- | --- | --- |
| `src/core/checksum.c` | `401aa0`, `401af0`, `401b30`, `401b90`, `401be0` | 23,251 comparisons, including installed asset paths and script names |
| `src/core/lzss.c` | `4014f0` | 415 comparisons; output, dictionary state, return pointer and preserved registers |
| `src/core/bounds.c` | `4033e0`, `403450`, `4034d0` | 17,333 comparisons; special float values and all 605 training collision objects |
| `src/core/bounds.c` | `403410`, `40b170`, `40b1d0` | 6,516 overlap/containment comparisons and 1,629 point-bound initializations, including NaNs and infinities |
| `src/collision/tree.c` | `416000`, `4169c0`, `414d30`, `4160e0`, `416320` | Full relocation of 605 real + 4 synthetic objects; 7,567 ordered face-list queries, including 1,227 fallback queries |
| `src/collision/geometry.c` | `40b230`, `40b2d0`, `414d80` | Both accessors for all 24,845 vertices, plus all 19,934 face normals, compared bit for bit |
| `src/collision/geometry.c` | `40b420` | 164,905 segment/triangle comparisons, including eight probes per training face; hit flags, output writes, and finite fraction bits match |
| `src/core/vector.c` | `4023f0` | 1,004 normalization comparisons; also exercised by complete static-object queries |
| `src/collision/segment.c` | `410bf0`, `411750`, `4f8160`, `4131f0`, `413b50` | Both surface fields for all 19,934 faces; 128 result copies; 16,890 hit selections; 22,222 complete static-object queries; 19,531 callback observations |
| `src/collision/segment.c`, `src/collision/scene.c` | `410c70`, `48c980`, `48c0b0`, `4188c0`, `4106c0`, `410930` | 802 complete scene queries, 322 grid queries, 13 scene-selection checks; cache paths, candidate limits, ordering and stamp wrap |
| `src/collision/segment.c` | `412730`, `40b370`, `410bc0`, `412750` | 31 independent constructor/binding cases, plus all instances in the loader checks |
| `src/collision/load.c` | `49cbb0`, `4183b0`, `418440`, `418bd0` | Four complete loads; 1,211 instances, 1,600 cells, 85 allocations, and 1,126 scene queries through loader-built grids |
| `src/core/matrix.c` | `40b090` | 256 finite matrix/vector comparisons, including aliased input/output |
| `src/collision/moving.c` | `411780`, `413000`, `412f90`, `412070`, `40ae40`, `40ae50`, `40b390`, `411810`, `4122c0`, `414460` | Constructors and transforms for all 605 training objects; 9,794 rigid moving-object queries, 561 fallback queries and 5,441 callbacks |
| `src/collision/moving.c` | `4118c0`, `411ae0` | 124 moving-scene queries, plus the moving stage of the complete probe checks |
| `src/collision/probe.c` | `4637c0`, `4637e0`, `417110`, `4172f0` | 496 complete probes through static and moving collision; reference-list contents, cache choice, callbacks, final results and copied fields |
| `src/collision/probe.c` | `417760`, `4171d0`, `417250` | 192 constructor/point-setter cases, including every untouched byte |
| `src/core/vector.c` | `42bbf0` | 517 vector-length cases; zero, finite and nonfinite inputs |
| `src/script/params.c` | `478cf0`, `4764b0`, `4766d0` | 79 symbol lookups and 4,760 parameter cases; aliases, nested structures, precedence and integer-to-float conversion |
| `src/game/skater.c` | `4fe1f0`, `4fe730`, `5009c0`, `4fd660` | 2,083 drag and 2,083 friction cases; 1,815 nearby-obstacle and 1,815 forward-obstruction queries through the training collision grid |
| `src/script/params.c`, `src/collision/probe.c` | `478f00`, `4170f0` | 2,615 global numeric getter cases and 256 flag-setter cases |
| `src/game/skater.c` | `5003a0` | 1,815 complete surface queries and 21,314 classification cases; three documented emulator differences for infinite angles, detailed below |
| `src/core/vector.c`, `src/core/matrix.c` | `4a86d0`, `405170` | 1,073 four-lane vector comparisons and 1,560 matrix repairs across all three fixed axes |
| `src/game/skater.c` | `4fe860` | 2,484 up-vector updates; 1,262 obstruction probes, 596 probe hits, 1,851 matrix updates and 633 unchanged targets |
| `src/script/params.c`, `src/game/parameters.c` | `479020`, `45db90`, `5802e0`, `580400`, `4fe6a0` | 158 global structure lookups, 105 component lookups, 2,162 parameter-set selections, 960 numeric lookups and 3,072 configured drag updates |
| `src/script/params.c` | `478f60`, `476630`, `476cb0`, `4767c0`, `476950`, `47ac00`, `476df0` | 810 global integer lookups, 720 member lookups/copies and 64 pair initializations; documented signaling-NaN oracle differences below |
| `src/game/stats.c` | `456f90`, `44e4f0`, `543320`, `543490`, `5433b0`, `537010`, `53aea0`, `5651f0`, `5a1180` | 2,276 stored player/network-state checks, including hidden players, null nodes, sentinels and 16-bit identifiers |
| `src/game/stats.c` | `553220`, `5532a0`, `553190`, `564d90`, `559050`, `584cc0` | 157 settings, difficulty and gameplay-bit checks, including missing values and the global flag side effect |
| `src/game/stats.c` | `462050`, `462120`, `4619f0` | 458 object lookups; collisions, null values, secondary-table fallback and masked shift counts |
| `src/game/stats.c` | `580490`, `5805b0`, `580790` | 2,048 stat getter cases, 4,096 full evaluations and 512 named parameter lookups |
| `src/core/matrix.c` | `404090`, `404c60`, `405950`, `5df4ac` | 96 overlapping word copies, 885 axis-angle matrices, 885 rotations and 2,048 SSE-backend multiplies |
| `src/core/timing.c`, `src/collision/probe.c` | `5be970`, `44ece0`, `41c350` | 3,072 paired timer checks; five reference-release graphs, each released twice |
| `src/game/skater.c` | `504b40` | 3,630 complete ground updates; 2,420 probes, 1,504 hits, 726 rotations and 2,004 timer reads |
| `src/game/motion.c`, `src/game/stats.c` | `4fe320`, `4fe420`, `4fe490`, `4fe530`, `5019e0`, `4ff590`, `4ff470`, `5843a0` | 6,307 movement/flag cases; real stat and parameter callees, branch boundaries, overlapping vectors and gravity side effects |
| `src/core/vector.c` | `4023f0`, `42bbf0` (additional coverage) | 192 normalization/length cases spanning tiny and large finite inputs, signed zero, NaNs and infinities |
| `src/core/vector.c`, `src/core/matrix.c`, `src/game/motion.c` | `406080`, `406630`, `404e20`, `501b00`, `506df0` | 6,400 plane projection, signed-angle, Y-rotation, slope-turn and complete resistance cases; documented double-precision math differences below |
| `src/core/vector.c`, `src/core/number.c`, `src/core/matrix.c`, `src/game/repulsion.c` | `4060f0`, `405fd0`, `405710`, `501c90`, `5055b0` | 2,826 math-helper cases, 3,025 individual probes and 3,630 complete four-direction repulsion updates through training collision |
| `src/core/vector.c`, `src/game/input.c`, `src/game/low_speed.c` | `406200`, `46b920`, `503b30` | 2,048 axis projections, 1,536 button-timer cases and 5,032 complete low-speed correction updates; 1,601 accepted position changes |
| `src/core/number.c`, `src/game/wall.c` | `403ef0`, `5039f0` | 3,087 heading-approximation cases and 3,072 wall-turn cases; independent body/cache matrices and overlapping output pointers; documented infinity differences below |
| `src/script/params.c`, `src/game/nodes.c`, `src/game/stats.c`, `src/collision/probe.c` | `46cc30`, `476b40`, `45be40`, `45cfc0`, `45c1b0`, `565bb0`, `417140`, `417210`, `417240` | 2,552 array, flag, node-name/table, multiplayer-gate and collision-owner cases; real original callees and complete fixture-memory comparisons |
| `src/script/runtime.c`, `src/core/timing.c` | `4738e0`, `4728c0`, `4728d0`, `4728f0`, `472940`, `4739a0`, `473050`, `5beaa0` | 4,162 cases / 8,423 calls covering construction, list access, wait setup/update and frame duration; 168 instrumented virtual callbacks |
| `src/core/random.c`, `src/script/branches.c` | `403de0`, `403e30`, `46f7a0`, `46f8a0`, `470bb0`, `470c60` | 2,038 cases / 5,486 calls covering both PRNGs, jump/random-token resolution, cache lookup/allocation/eviction and shuffling; 128 allocations and 39 releases |
| `src/script/values.c` | `476410`, `46d140`, `46caa0`, `46cb00`, `476340`, `46cab0`, `477140`, `4772a0`, `477090`, `477130`, `477920`, `476bc0` | 2,131 cases / 3,946 calls covering construction, recursive ownership cleanup, insertion/replacement and containment; 3,508 releases with payload/link snapshots |
| `src/script/copy.c` | `476260`, `4763a0`, `47abf0`, `46cc50`, `4773e0`, `478480`, `478540`, `4787a0`, `478a60` | 1,724 cases / 3,002 calls (including existing cleanup routines), covering interning, storage resizing, deep copying, borrowing and merging; 697 allocations, 5,476 releases and 566 temporary-scope events |
| `src/script/construct.c` | `4779d0`, `477ac0`, `477b80`, `477c60`, `477d40`, `477e20`, `477fc0`, `4780d0`, `4781b0`, `478290`, `478650`, `476430`, `4739d0` | 950 cases / 2,172 calls (including existing cleanup), covering typed setters, assignment, member lookup and aliased-argument snapshots; 2,115 allocations and 9,166 releases |
| `src/script/tokens.c` | `46f690`, `46f7e0`, `46fd60`, `46f920` | 123,493 boundary/read comparisons, including all 86,208 tokens of eight archived training QB files, 3,407 compound-value skips and 651 script-end skips |
| `src/script/ranges.c` | `46fbd0` | 4,506 cases / 5,076 random-value decodes through both original PRNGs and the real CRT integer converter; all 19 training range occurrences, numeric boundaries, byte selector and overlapping output; 277 typed NaN results checked by classification |
| `src/script/operators.c` | `476490`, `4776b0`, `477790`, `477860`, `4791a0`, `479410`, `4795a0`, `476c10`, `49f4b0`, `46cb70`, `46cbf0`, `47a910`, `46d160`, `46d180`, `46d1a0`, `46d280` | 4,685 cases / 10,889 calls (including existing cleanup), covering comparison, removal, array access and ownership/truth tags; 76 allocations and 9,168 releases; 30 numeric NaN returns by classification and four documented signaling-NaN store differences |
| `src/script/expression.c` | `46d1c0`, `46d220`, `46d250`, `46d260`, `46d2b0`, `46d310`, `46d370`, `46d380`, `46d3c0`, `46d450`, `46eb70`, `46ebf0`, `46ec40` | 7,392 cases / 8,309 calls covering complete binary evaluation, precedence, parentheses, final copying and stack lifecycle; 1,715 allocations, 9,203 releases and 626 scope events; 283 typed arithmetic NaNs checked by classification |
| `src/script/parser.c`, `src/script/operators.c` | `470130`, `4706f0`, `470f30`, `471860`, `471b00`, `4712b0`, `479730` | 1,087 cases / 1,894 calls covering mutually recursive QB value/structure/array/parameter/expression parsing and symbol resolution; 815 real definitions across eight archived training files, 15 native-predicate callbacks, 22,194 allocations and 213 releases; one typed global NaN checked by classification |
| `src/script/symbols.c` | `478cc0`, `478dc0`, `478d60`, `478e50`, `479110`, `4711d0`, `472240`, `46f960` | 1,198 cases / 3,349 calls (including existing alias resolution), covering global symbol lookup/linking/iteration, creation/disposal, value registration and script checksums; all 164 ordinary training definitions registered and disposed, all 651 script bodies hashed; 40,080 allocations and 20,762 releases |
| `src/core/compress.c` | `401600`, `401290`, `4013e0`, `401700` | 764 cases / 1,310 calls covering encoder initialization, tree insertion/removal and complete LZSS encoding; all 651 archived training script bodies; 761 decoder roundtrips over 604,391 bytes, 243 diagnostic callbacks, exact output/tree/global/heap comparisons |
| `src/core/memory_state.c`, `src/core/lookup.c`, `src/script/tokens.c`, `src/script/cache.c` | `5ba3b0`, `5ba3d0`, `5ba400`, `5bc530`, `5ba4f0`, `49fd90`, `462740`, `5b80d0`, `46fb30`, `46ff00`, `475a40`, `475a70`, `475ac0`, `475b00`, `475b60`, `475bd0`, `475d60`, `475e80`, `475fd0`, `46fe40` | 1,646 cases / 7,325 calls (including existing table lookup); fixed pools, heap metrics, lookup mutation, bytecode preparation, cache lifetime and compressed-script registration; all 651 archived training bodies registered, cached and reloaded; 11,198 heap allocations, 7,919 releases and 6,560 scope events |
| `src/script/load.c` | `46cf60`, `470010`, `46f9f0`, `46fa60`, `4727b0`, `4727f0`, `472830`, `472420` | 103 cases / 276 calls (including existing symbol lookup/cache acquisition); 131 complete QB-buffer loads, readable-name maps, definition replacement and journal undo; whole loads of eight archived files with 815 definitions, individual undo and a combined load sequence; 113,973 allocations, 45,350 releases and 23,284 scope events |
| `src/script/tokens.c`, `src/script/control.c` | `46f800`, `46f850`, `472a70`, `473220`, `472ab0`, `472b50`, `473c60`, `473e70` | 369 cases / 407 calls; halfword/line helpers, loop begin/repeat/break, nested-switch selection/skipping and script return; 34 archived loop starts and four archived switches; 328 allocations, 622 releases and 134 scope events |
| `src/core/lookup.c`, `src/script/events.c` | `588190`, `4624d0`, `462530`, `462550`, `462710`, `4626b0`, `463450`, `462b90`, `45fa60`, `45fe60`, `473010` | 1,167 cases / 2,405 calls; shared table iteration, listener lifetime, event unsubscription, group disposal and script-event cleanup; both concrete virtual destructors execute; 4,010 generic releases and 88 pool releases |
| `src/script/execute.c` | `46d0c0`, `46d110`, `460ad0`, `472950`, `4729e0`, `472980`, `4731a0`, `4731e0`, `473880`, `473a80`, `474540`, `4748e0`, `475750`, `474b40`, `475050`, `4750b0` | 556 cases / 920 calls (including existing compressed-script registration); complete recursive setup/call/cleanup/execution, native/member/component dispatch and debug names; 862 allocations, 1,512 releases, 258 scope events and 297 instrumented command/output callbacks |
| `src/collision/probe.c`, `src/script/branches.c`, `src/script/events.c`, `src/script/lifetime.c` | `463820`, `463870`, `463880`, `46f870`, `45fb70`, `449970`, `4499b0`, `474420`, `4752f0`, `4753c0`, `4756c0`, `475700`, `4742b0`, `474350`, `4756f0` | 862 cases / 957 calls (including existing construction); reference clearing/destruction, branch ownership detachment, event-table disposal, script pools and complete instance destruction, execute/copy/dispose, deferred spawned stopping, finished collection and owner/current-or-stack checksum stopping; 528 generic allocations, 2,224 generic releases, 64 scope events, 102 pool allocations and 50 pool releases |
| `src/script/params.c`, `src/script/tokens.c`, `src/script/serialize.c` | `479070`, `46f810`, `46f840`, `479840`, `4798f0`, `479a50`, `479ac0`, `479b20`, `479b80`, `479e20` | 4,665 cases / 5,159 calls (including existing parsers); global array lookup, word/half writers and compact named headers, integers, floats, strings and recursive array/structure encoding; real 252-entry byte and 30-entry halfword name tables parsed from `compress.qb` and all 164 ordinary archived training definitions encoded; 38 serialization callbacks and exact output/partial-write comparisons |
| `src/core/memory.c`, `src/network/messages.c`, `src/network/queue.c` | `401cc0`, `4549f0`, `454a60`, `454e30`, `454fa0`, `455040`, `4550f0`, `456d90`, `4555f0`, `455b50`, `455170`, `4557c0`, `455620`, `455b70`, `4551b0`, `4557f0`, `455650`, `455b90`, `4551f0`, `455820`, `457350`, `54b6b0`, `457910`, `457c80`, `457eb0`, `459e50`, `532ea0` | 3,329 cases / 4,718 calls; zero allocation, message descriptors, RLE/LZSS payload compression, message/node ownership, all six concrete virtual destructors, signed priority insertion, reverse iteration, peer lookup/removal, shared enqueue and first-peer forwarding; 6,344 allocations, 4,746 releases, 3,240 scope events and 742 diagnostic callbacks |
| `src/script/schedule.c`, `src/game/collision_events.c` | `473350`, `473420`, `475420`, `475790`, `475920`, `461480`, `434a60`, `434bf0` | 1,693 cases / 2,547 calls (including existing spawned stopping); both network wrappers, native/bytecode spawning, synchronous dispatch, frame scheduling/completion/deferred stops and complete collision-node/probe-to-script dispatch; 5,423 allocations, 5,180 releases, 1,194 scope events and 470 command/activity/node-provider callbacks; three undefined packet-padding bytes normalized, as documented below |
| `src/script/delivery.c`, `src/script/runtime.c`, `src/script/execute.c`, `src/script/values.c`, `src/script/construct.c`, `src/collision/probe.c`, `src/core/vector.c` | `409070`, `416dd0`, `41a820`, `42b580`, `45f7f0`, `45f9b0`, `460150`, `460470`, `4609f0`, `4620a0`, `4627c0`, `462b10`, `462f00`, `472e20`, `472ed0`, `472ee0`, `4734b0`, `473800`, `4747a0`, `4783c0`, `4a1090` | 1,506 cases / 1,954 calls (including existing construction/destruction); direct/receiver/broadcast delivery, radius filtering, event waits, reentrant handlers and actual recipient deletion, parameter ownership, logs/names, structure-pool release, references and supporting script accessors; 1,598 allocations, 1,557 generic releases and 778 event/command callbacks; 15 returned NaNs checked by classification |
| `src/core/vector.c`, `src/core/number.c`, `src/game/wall.c` | `402320`, `402340`, `402370`, `4023c0`, `4024d0`, `402530`, `402550`, `406050`, `4196b0`, `4ff670` | 7,393 cases / 8,225 calls; complete rebound selection/response, event cancellation, reflection, speed adjustment and orientation/timestamp updates, plus vector/scalar prerequisites; 1,937 full rebound calls, 812 successful responses, 991 event/command callbacks and 127 training face normals; 1,368 arithmetic NaN outputs/returns checked by classification |
| `src/script/params.c`, `src/audio/sound.c` | `476590`, `476860`, `476a90`, `476af0`, `444310`, `444360`, `4443b0`, `444400`, `444480`, `444760`, `444830`, `4445b0`, `47b010`, `47b030`, `47ac50`, `47acf0`, `47b2c0`, `47b760` | 2,336 cases / 8,874 calls; material/event lookup and fallback, impact/weighted clip selection, descriptor construction, text/array/name access, volume state and loaded-asset distance lookup; original callees, iterator/PRNG state and preserved bytes; 757 arithmetic NaN outputs/returns checked by classification |
| `src/core/vector.c`, `src/game/camera.c`, `src/audio/spatial.c` | `402470`, `402500`, `423680`, `485a00`, `485a10`, `4a09e0`, `47b080`, `47be10` | 2,873 cases / 3,197 calls; complete positional sound and nearest-camera selection, camera field access, maximum-magnitude volume and vector helpers; 1,407 full positional calls, six viewport modes, four attenuation curves, output preservation, aliases and nonfinite arithmetic; 322 arithmetic NaN outputs/returns checked by classification |
| `src/audio/voices.c`, `src/game/camera.c` | `47c7e0`, `47c720`, `47bab0`, `47bb20`, `47af40`, `47b480`, `4a0950` | 1,957 cases / 6,142 calls; device-slot activity/selection, voice and pending-ID availability, wrapping ID search, parameter initialization, asset volume/pitch settings and direct viewport camera lookup; all slot counts 1..48, overlaps and preserved fields; 817 derived/arithmetic NaN fields checked by classification and five exact x87 quiet-bit corrections |
| `src/core/vector.c`, `src/audio/device.c` | `406460`, `420a90`, `47cd70`, `47d130`, `47bd20` | 1,255 cases / calls; normalized vector angle, Y rotation, stereo/positional device settings, buffer cache/create/upload/play and game playback through voice setup; 3,226 instrumented OS audio calls including failures and mutations, full memory/globals and returns; 175 arithmetic NaN comparisons; documented logarithm-domain oracle limitation below |
| `src/audio/events.c` | `444bb0`, `518dd0` | 555 cases / 590 calls; complete material-impact dispatcher and component wrapper through real selection, attenuation, device playback, voice setup and message queuing; 3,128 OS audio callbacks, 838 allocations, 40 releases and 572 scope events; full fixture/global/queue bytes and returns; one undefined packet-padding byte explicitly zeroed |
| `src/game/wall.c` | `5059d0` | 559 complete wall-response comparisons; 555 second probes through training collision, 257 hits, 105 turn reversals, 43 displacement-gated events and four rebound returns; 178 event/command callbacks, 614 OS audio calls, actual QB execution and message queuing; 600 typed arithmetic NaN outputs checked by classification |
| `src/game/wall.c` | `506e50` | 748 complete movement sweeps; 620 first hits, 108 skateable corrections, 512 collision-event deliveries and 429 wall responses; actual QB execution, six moving-owner node-provider calls and 698 event/audio observations; 74 typed arithmetic NaN outputs checked by classification |
| `src/core/matrix.c`, `src/game/moving_contact.c`, `src/collision/probe.c` | `416d80`, `416df0`, `40af60`, `416e70`, `416f00`, `427c70`, `427cb0`, `427cd0`, `5021d0`, `43a930` | 1,360 cases / 2,512 calls; complete contact construction, transport, acquisition/reuse/release, relative-velocity adjustment and saved-probe assignment through actual matrix/reference/timer callees; 72 allocations, 328 releases, 738 typed arithmetic NaNs and three exact x87 quiet-bit corrections |
| `src/core/vector.c`, `src/game/skater.c` | `40aed0`, `43d990`, `4fea50` | 1,547 cases / 1,904 calls; ordered vector equality, overlapping interpolation and complete orientation blend through real QB lookup, normalization and cached-basis repair; repeated updates, training normals, wide decrement thresholds and matrix aliasing; 2,395 typed arithmetic NaN fields checked by classification |
| `src/game/skater.c`, `src/script/delivery.c` | `519660`, `5196a0`, `460a20` | 164 cases / 246 calls; state-mode/material setters and object broadcast through actual event delivery, cached QB execution and protected listener snapshots; 168 callback observations, 292 allocations and 292 releases; full memory/global comparison |
| `src/game/skater.c` | `4feba0`, `4fc4a0` | 720 cases / 1,059 calls; complete floor-transition preparation and tracking through actual QB, speed-preserving projection, orientation and timer callees; 708 transitions, 481 basis repairs and 125 diagnostic callbacks; 904 arithmetic-derived NaN comparisons, two exact float and six exact double quiet-bit corrections |
| `src/game/motion.c`, `src/game/input.c` | `503560`, `4ff920`, `4ffb10`, `46b7f0` | 756 cases / 1,268 calls; steering, backward-motion response, input release and pending-word clear through actual parameter, timer, CRC, matrix, script and event callees; 256 callbacks, 470 allocations/releases, 230 arithmetic NaN comparisons and eight exact quiet-bit corrections |
| `src/game/attachment.c`, `src/game/input.c`, `src/core/vector.c` | `501db0`, `51ba70`, `51bc70`, `469340`, `469350`, `5480f0`, `46b7e0`, `402440`, `4023a0` | 963 cases / 1,222 calls; complete attachment movement, nearest/indexed projected points, concrete virtual provider, transform helpers, input latch and vector helpers; 435 full movement calls, 78 event/command callbacks and 441 arithmetic NaN comparisons |
| `src/game/objectives.c`, `src/script/params.c` | `588380`, `588180`, `5591b0`, `553e90`, `557f10`, `561430`, `584130`, `559110`, `554220`, `5541e0`, `554280`, `5764b0`, `566520`, `476a00` | 716 cases / 1,052 calls; objective lookup/cache, availability, state and event parameters, notification reset, local skater and text-key checksum access; actual QB and CRC callees, complete byte comparisons, aliases and retained missing outputs |
| `src/game/objectives.c`, `src/game/stats.c`, `src/script/construct.c` | `553f90`, `553f50`, `553f60`, `5519f0`, `554460`, `555590`, `554110`, `553ea0`, `557f90`, `555540`, `5372c0`, `533070`, `45a540`, `55dbe0`, `5566d0`, `478670` | 843 cases / 2,216 calls; full flat/grouped state construction, completion/timer checks, concrete objective methods, parent traversal, ordered insertion, player iteration and owned structure copy; 453 allocations and 401 releases with exact memory/event comparisons |
| `src/game/objective_text.c`, `src/game/profile.c`, `src/script/params.c`, `src/script/construct.c` | `556a00`, `555b50`, `554890`, `57b630`, `57b640`, `564f80`, `586110`, `5860a0`, `587100`, `586630`, `476620`, `476ec0`, `476f10`, `478b00`, `46cb10` | 269 cases / 428 calls; complete objective text update, binding table construction, marker expansion, profile access and legacy QB/owned-array helpers; 1,273 allocations, 1,044 releases, 1,428 scope events; three undefined binding-padding bytes normalized per returned record |
| `src/game/objectives.c` | `557270` | 198 cases / 426 calls: 396 complete objective initializations and 30 existing parser calls; actual difficulty merge, state construction, synchronous QB execution, text conversion and flag mutations, including all 30 archived training goal-flag arrays |
| `src/game/objectives.c` | `557560`, `554bd0`, `553e50`, `554030`, `554070` | 231 cases / 605 calls across five new routines and three existing prerequisites; full deactivation, recursive uninitialization, child/state reset, actual virtual methods and 30 archived training goal lifecycles; separate bounded checks preserve the original reserved-member loop |
| `src/game/score.c`, `src/game/ui.c` | `566600`, `57fec0`, `562920`, `563020`, `562970`, `5633e0`, `5612d0`, `518390`, `4020e0`, `48d6a0`, `48d760`, `4aae20`, `4a8f40`, `4a8940` | 670 cases / 1,138 calls across fourteen new routines and one existing reference destructor; score ownership cleanup, special-meter settings, skater/font/widget lookup, character/button mapping, visibility and actual event delivery; 156 allocations and 239 releases |
| `src/game/font.c`, `src/game/ui.c`, `src/platform/text.c` | `402170`, `402200`, `5f3120`, `5bcd50`, `4b2160`, `4cecb0`, `4b3d10`, `48d060`, `4a92d0`, `4a94a0`, `4af8c0`, `6254eb`, `62569c` | 3,155 cases / 6,341 calls across eleven engine and two CRT routines; complete text setting, font measurement/dispatch, key labels, splitting/formatting, wide conversion and size/scale updates; 136 allocations, 88 releases, 272 scope events and 1,330 explicit OS calls |
| `src/game/drawing.c`, `src/game/font.c`, `src/game/ui.c` | `4af720`, `4df900`, `4df950`, `4dfa70`, `4ceed0`, `4dfae0`, `4dfb20`, `4dfb70`, `5480a0`, `48d220`, `4b3f50`, `4b3db0`, `4b3da0`, `48d1b0`, `4b3e70`, `4b3fd0`, `48d1d0`, `4a8b80`, `4a8bb0`, `4a8730`, `4b0620` | 1,119 cases / 4,731 calls across twenty-one new routines and existing reference destruction; full word wrapping, drawable ordering/construction, concrete virtual style updates, pools, widget style arrays, ancestor lookup and overlapping state copies; 314 allocations and 148 UI scope events |
| `src/collision/probe.c`, `src/game/ui.c`, `src/game/drawing.c` | `4637b0`, `41d1d0`, `4a8f60`, `460b80`, `4611e0`, `461970`, `4a8f90`, `4a8f20`, `4aa390`, `4aa470`, `4aa8e0`, `4b0920`, `48d5a0`, `48d5f0`, `4b0760` | 624 cases / 1,392 calls across fifteen new routines and four existing lifecycle helpers; full object/UI/text construction, pooled parameters, intrusive reference assignment, parent changes, inherited owner/depth propagation and drawing-style cleanup/reuse; 332 allocations, 214 releases and 334 UI scope events |
| `src/game/object_registry.c`, `src/game/ui.c`, `src/game/drawing.c`, `src/script/runtime.c` | `461bc0`, `4621d0`, `462590`, `462980`, `462a20`, `461930`, `461a00`, `461a50`, `4619a0`, `4619d0`, `472f00`, `460af0`, `460b20`, `460b40`, `461b20`, `461b50`, `461b80`, `4615d0`, `461900`, `4aab30`, `4aac90`, `4b1830`, `4b2030` | 429 cases / 998 calls across twenty-three new routines and eight existing helpers; complete ID/alias registration, renaming, priority changes, manager lifecycle and base/UI/Text destruction; actual virtual methods, script cancellation/cleanup, selected and alternate pools, deferred QB execution and lifecycle logs; 479 allocations, 232 releases and 138 scope events |
| `src/game/ui_manager.c`, `src/game/ui.c`, `src/game/input.c`, `src/script/delivery.c`, `src/script/runtime.c`, `src/script/params.c` | `45faa0`, `45fac0`, `460170`, `45fb30`, `461fe0`, `462000`, `4ab990`, `4abb00`, `4acb40`, `4ab250`, `4ab330`, `4ab4d0`, `4ab7c0`, `4abbe0`, `4aaff0`, `4ac400`, `4ad100`, `4abd40`, `461140`, `473be0`, `4a8f00`, `4a86c0`, `45f9e0`, `45f980`, `462b40`, `479090`, `44e630` | 349 cases / 7,654 calls across twenty-seven new routines and seven existing helpers; actual UI manager and receiver lifecycle, controller subscriptions, focus/device filtering, nested event forwarding, live list mutation/restart, recursive widget deletion and caller-owner detach; 694 allocations, 176 releases, two scope events and four real QB handler executions |
| `src/game/font.c`, `src/game/score.c`, `src/game/ui_manager.c` | `4b0810`, `4b08b0`, `4b0b30`, `4b0cd0`, `561670` | 211 cases / 2,706 calls across five new routines and eight existing helpers; complete multiline construction/destruction, text-child replacement and combo-text updates through actual wrapping, font measurement, style reuse, automatic IDs, recursive deletion, event delivery and cached QB execution; exact memory, globals, returns and heap/scope records |
| `src/game/score.c`, `src/platform/text.c` | `561890`, `564a10` | 426 cases / 3,196 calls across two new engine routines and seven existing helpers; complete numeric score display and full reset through actual localized grouping, UI replacement, history/list cleanup, mode lookup, special-meter configuration/broadcast and guarded QB handlers; bounded legacy CRT formatting adapters; exact memory and 153 diagnostic callbacks |
| `src/game/objectives.c` | `557360` | 235 cases / 2,186 calls across complete objective activation and nine existing helpers; actual player score/UI resets, parent lookup/uninitialization, difficulty/text initialization, inherited timer, unnamed-flag removal, QB activation and ordered queue insertion; all 30 archived training flag arrays; exact memory and 163 diagnostic callbacks |
| `src/game/objectives.c` | `557fc0`, `559230`, `559290`, `5592f0` | 169 cases / 1,208 calls across manager activation, native goal start/stop/clear commands and ten existing helpers; actual symbolic/direct QB dispatch, expression predicates, synchronous/spawned native calls, nested goal handlers and all 30 archived training flag arrays; exact memory and 103 diagnostic callbacks |
| `src/game/objectives.c`, `src/game/score.c`, `src/game/stats.c`, `src/core/lookup.c`, `src/script/values.c` | `557e40`, `555df0`, `555fb0`, `5588d0`, `557a40`, `554a80`, `556050`, `5555e0`, `5845c0`, `584620`, `561b40`, `533f90`, `588400`, `5b8060`, `588120`, `5576d0`, `558030`, `559310`, `409030` | 529 cases / 1,399 calls across nineteen new routines and nine existing helpers; complete goal wins, child progression, records, rewards, unlocks, parent propagation, progress counters and network queues; original native QB commands and all 30 training flag arrays; selected/empty structure pools and shared ownership cleanup; exact bytes and 36 diagnostic callbacks |
| `src/game/objectives.c`, `src/game/skater.c` | `556330`, `559670`, `576520`, `559150`, `588a20`, `5232a0`, `522370`, `4fded0` | 501 cases / 2,038 calls across eight new routines and nine existing helpers; native goal flags, automatic completion, gameplay event/score gates, notification ring and complete skating-state change; all 57 flags in 30 archived training arrays; real QB handlers and score/UI reset; exact bytes and 43 diagnostic callbacks |
| `src/core/vector.c`, `src/game/input.c`, `src/game/side.c` | `4024a0`, `40af20`, `44e5a0`, `51ecf0`, `51f6b0`, `506ba0`, `508140`, `50a2c0`, `50c930` | 504 cases / 1,583 calls across nine new routines and nine existing helpers; complete side corrections and wall transitions, named and buffered input, saved contact and vector support; actual training geometry, original QB/native goal callbacks and moving-contact release; 11 diagnostic callbacks |
| `src/collision/cache.c`, `src/collision/moving.c`, `src/game/transfer.c` | `402600`, `40aa00`, `40aa40`, `40ab40`, `40ab50`, `40aba0`, `412fc0`, `43daa0`, `502240` | 349 cases / 551 calls across nine new routines and two existing helpers; complete transfer scan and ballistic clearance, temporary cache lifetime/build, moving bounds and speed interpolation; 222 parent calls and 66 successful transfers |
| `src/core/matrix_inverse.c`, `src/script/events.c`, `src/game/transfer.c` | `404120`, `4041e0`, `4043a0`, `405600`, `405310`, `405990`, `45fdf0`, `473690`, `4607a0`, `502f20` | 407 cases / 761 calls across ten new routines and eleven existing helpers; complete transfer application, matrix inversion/axis-angle/interpolation setup and event removal; 44 application calls, nine training-mesh search/application sequences including a moving mesh, owned listener/parameter cleanup and two diagnostic body/state mutations through real QB/native goal activation |
| `src/core/quaternion.c`, `src/core/matrix_inverse.c`, `src/game/input.c`, `src/game/parameters.c`, `src/game/transfer.c`, `src/game/floor.c` | `46b900`, `580440`, `404dd0`, `420140`, `420ac0`, `420b50`, `4058e0`, `405a20`, `4fee10`, `505f70`, `507120`, `509bd0` | 940 cases / 1,846 calls across twelve new routines and eight existing helpers; complete floor contact/departure, alternate transfer scan/application and transition exit; original training collision, 113 floor calls, six completed alternate applications, eighteen blocked/deferred returns and six QB/native callbacks mutating sound, state or response gate |
| `src/game/score.c`, `src/game/ui.c` | `562760`, `562e40`, `564270`, `4607c0`, `4616d0`, `4a9100` | 813 cases / 1,682 calls across six new routines and five existing helpers; complete balance score accumulation, trick-score recalculation, special-meter events, UI attributes and positioning; 63 complete balance-score calls, 36 accepted updates, and 12 QB/native callback mutation cases |
| `src/game/drawing.c`, `src/game/score.c` | `49ed60`, `4dfc50`, `4c70e0`, `4b2a80`, `48bf30`, `4af1a0`, `4c71b0`, `4c70b0`, `4c70c0`, `4b3d80`, `49ec90`, `4af240`, `563080`, `563370`, `563390` | 555 cases / 2,162 calls across fifteen new routines and five existing helpers; sprite construction, concrete draw-data/ordering/visibility, rotation and complete normal/manual balance display; 963 complete display executions, sixteen QB/native mutation cases and two constructor-to-display sequences |
| `src/game/balance.c`, `src/game/input.c`, `src/game/profile.c`, `src/game/stats.c` | `4f90a0`, `5807f0`, `51c950`, `51ce80`, `51d6a0`, `46c270`, `564fc0`, `5480c0`, `543300`, `5434b0` | 498 cases / 1,118 calls across ten new routines; balance parameter selection, complete timed-trick enable/completion/scan, ordered button lookup and profile/network getters; 245 full scans, 173 completion writes, 210 native callback observations and eight QB/native mutation cases |
| `src/game/animation.c`, `src/game/assets.c` | `481650`, `481430`, `481710`, `481730`, `481740`, `4819d0`, `481760`, `419ab0`, `419ad0`, `4a49f0`, `4a4af0`, `5b9770`, `5b68c0`, `5b6a50`, `407910`, `4071a0`, `590250`, `407610`, `407680`, `4076a0`, `407710`, `407c00`, `48cf50`, `48cf70`, `4b3990`, `48bfc0`, `48cfa0`, `48cfd0` | 763 cases / 1,545 calls across 28 routines; complete balance-animation controller construction and commands, timing, asset lookup, reader pools and asynchronous completion pumping; 193 real file callbacks, 36 diagnostic observations, 102 arithmetic NaNs and 30 explicit x87 quiet-bit corrections |
| `src/game/animation.c`, `src/game/animation_events.c`, `src/game/assets.c`, `src/core/memory.c` | `4015d0`, `4645e0`, `48d000`, `4b22a0`, `48bfd0`, `4814b0`, `4816b0`, `481830`, `481690`, `4816e0`, `481a30`, `481a80`, `4818b0`, `4a4a80`, `4a50e0`, `4a4610`, `481a20`, `486150`, `4865d0`, `486560`, `481db0`, `4819f0`, `4860c0`, `486160`, `486440`, `481bb0`, `481c00`, `4819a0`, `481e10` | 1,311 cases / 1,915 calls across 29 new routines and one existing constructor; full timing, ordered controllers, reader/controller cleanup and owned animation events; actual object routing and cached QB with 224 instrumented native callbacks; 12 arithmetic NaN returns |
| `src/game/animation_controllers.c`, `src/game/animation.c`, `src/script/params.c`, `src/core/vector.c` | `481640`, `4813f0`, `476fb0`, `405ef0`, `47d620`, `419af0`, `487770`, `4877e0`, `4a5350`, `4a4d50`, `4a5400`, `4a4dd0`, `4a54a0`, `4a5010`, `4a4820`, `4a50b0`, `4a4890`, `4e2c50`, `4e2c80`, `4e2cf0`, `4e2c90`, `4a5730`, `4a4d20`, `4a5320`, `51adc0`, `488300`, `487d40`, `4880d0`, `487d60`, `487d90`, `487dc0`, `487de0`, `488170`, `488220`, `488950`, `488b20`, `488b40` | 1,257 cases / 1,913 calls across 37 new routines and three existing list routines; five concrete controller lifecycles and commands, timing, range parsing, vector parameters and bone settings; real virtual cleanup and QB setters; 93 arithmetic NaNs and 32 strict x87 quiet-bit corrections |
| `src/game/animation_cache.c` | `5be8e0`, `482c20`, `482e70`, `482a70`, `483d00`, `480660`, `480800`, `4805e0`, `4805f0`, `480600`, `480610`, `480620`, `480630`, `480640`, `480670`, `480a70`, `480ad0`, `480bf0`, `480c90`, `480df0`, `480db0`, `480e30`, `480e80`, `480940`, `480810`, `480980`, `4806c0`, `480ed0`, `482ba0`, `482bd0`, `482b90`, `485270` | 2,003 cases / 2,447 calls across 32 new routines; packed keyframe decoding, quaternion expansion, full throttled cache builds, pin/release/eviction and 64-bit ticks; whole memory/globals/heap/returns compare exactly, with explicitly initialized undefined padding |
| `src/game/animation_loading.c` | `4819e0`, `486460`, `486490`, `486680`, `482af0`, `482b30`, `484200`, `484370`, `4856c0`, `4809f0` | 2,217 cases / 5,780 calls; both file formats, seven embedded-event types, lifetime cleanup and 50-block cache initialization; all 1,707 installed clips plus 36 complete real skater precache builds |
| `src/game/animation_playback.c` | `4a4500`, `4a4590`, `4a4f30`, `4a5600`, `4a55e0`, `4a4670`, `481fb0`, `481870`, `481f20`, `482360`, `482340`, `482200`, `481ac0`, `4a4620`, `4a4ef0`, `4a5180`, `4a52e0`, `488100` | 1,120 cases / 2,334 calls; seven concrete factory types, standard clip/cache ownership, channel routing/fading and virtual frame updates; two real clips, 98 native QB observations and 336 typed arithmetic NaN comparisons |
| `src/game/balance.c`, `src/game/animation_playback.c` | `579cc0`, `47e280`, `419bd0` | 649 cases / 1,432 calls; complete balance frames through original scoring, timed tricks, failure-event QB delivery, animation commands, network queues and concrete sprite meters; 423 native QB observations and 154 typed arithmetic NaN comparisons |
| `src/game/grounded.c` | `50ee70` | 358 cases / 1,525 calls, including 385 complete grounded frames; actual balance, moving platforms, attachment, floor/sweep, steering and QB callbacks; 18 movement retries and four eight-frame sequences |
| `src/game/air_motion.c`, `src/core/vector.c`, `src/core/matrix.c`, `src/core/timing.c`, `src/game/moving_contact.c` | `4061a0`, `4fc370`, `420250`, `4fc400`, `4fc470`, `404e70`, `405670`, `504910`, `504a60`, `504df0` | 670 cases / 1,510 calls; complete pitch, transfer orientation and upright correction, vector/rotation/timer helpers and material events with component replacement |
| `src/game/air_motion.c`, `src/collision/probe.c`, `src/game/moving_contact.c` | `4ffdb0`, `504ee0`, `4f8200`, `43eb80` | 752 cases / 3,131 calls; complete raised-path and overhead collision through actual training geometry, translated moving surfaces, distinct contact normals and reference ownership |
| `src/game/air_motion.c`, `src/game/input.c` | `4ffb90`, `420730`, `420520`, `51ebd0`, `51f9b0` | 675 cases / 1,651 calls; complete airborne flip input, rotation queues, three-key matching and mark consumption; 16 cases parse the archived flip table, with real network queues and 101 native QB observations |
| `src/audio/events.c` | `518cf0` | 357 cases / 369 calls; ordinary, grind and slide landing sounds through actual event lookup, material fallback, positional audio and network queues; 2,916 device observations |
| `src/game/score.c`, `src/game/animation.c`, `src/game/balance.c`, `src/core/number.c` | `563f30`, `564be0`, `419c70`, `51cac0`, `4022c0` | 493 cases / 3,395 calls; complete spin scoring and guarded entry, Cab labels, both score displays, blend flip flags, timed-spin storage and ordered clamp; 197 diagnostic/native QB observations |
| `src/game/air_motion.c` | `504060` | 405 cases / 3,729 calls including 486 complete airborne spin updates; tap/shoulder/directional input, automatic turning, both matrices, scoring gates and actual score/UI/QB callbacks |
| `src/game/input.c` | `51ea40`, `51eb80`, `51ec40`, `51ecc0`, `51f7a0`, `51fda0` | 3,518 cases / 3,959 calls; all 18 trick-input selectors, held states, press/release ordering, ring wrap, partial marks, masks and scaled windows; eight matches parse the archived Wallplant_Trick table first |
| `src/graphics/decal.c`, `src/collision/scene.c` | `490cd0`, `490d20`, `490d50`, `490d80`, `490e40`, `4b7f30`, `4d1a90`, `4d4be0`, `4a2ba0`, `49f540`, `4d4090`, `4d42f0`, `528560`, `49cb00`, `48c510`, `418710`, `4b7fa0`, `4b88d0`, `4b8220`, `490ec0`, `48f620`, `4b87b0` | 3,582 cases / 5,248 calls; decal storage and lookup, buffer access, real training grid bounds, original intersection predicates, full triangle subdivision, lifetime/fade and lighting; 336 external device callbacks |
| `src/core/d3dx.c`, `src/core/sort.c`, `src/core/random.c`, `src/graphics/material.c`, `src/graphics/decal.c` | `5e17ed`, `5e16ea`, `5c0b39`, `5c0985`, `4ce960`, `4ce9a0`, `4ce9d0`, `4ceb30`, `4ce1d0`, `4ce250`, `4cda60`, `4cd9d0`, `4ce9f0`, `6242a0`, `624230`, `623ba3`, `4b9a60` | 2,209 cases / 3,618 calls; projection math, complete material group/table lifecycles, exact CRT sorting/random recurrence and decal buffer allocation/reuse; 548 typed computed NaNs compared by classification |
| `src/graphics/mesh.c`, `src/graphics/projection.c` | `4d69e0`, `4d3be0`, `4b9c30` | 347 cases / 371 calls; complete mesh destruction, vertex unregister and surface-mark projection; 141 installed training faces repacked into render strips, repeated buffer exhaustion, exact heap/GPU callback order; 486 typed computed NaNs by classification |
| `src/graphics/decal_scene.c`, `src/game/wall_marks.c` | `4928a0`, `51dbc0` | 178 cases / 207 calls; full scene selection, tracked-point expiry/reuse, projection and wall-mark emission through actual queued network messages; complete 605-object training collision grid with 70 sampled faces; 342 typed computed NaNs by classification |
| `src/game/wall_marks.c` | `51ddf0` | 249 cases / 383 calls including existing moving-collision setup; full wall contact, cooldown/arming/emission, sloped and moving surfaces, and 114 training-geometry cases; exact fixture bytes |
| `src/game/wallplant.c` | `503710` | 188 cases / 189 calls; complete vertical wallplant through input, both collision probes, marks, object/collision events, objective notifications and timers; 76 training cases and 15 native QB observer callbacks; exact fixture bytes |
| `src/game/wallplant.c` | `507500` | 303 cases / 631 calls including 304 standard wallplant attempts; late/check-only/forced modes, outgoing clearance, moving contacts, complete event/state changes, 76 training cases and 12 native QB observers; exact fixture bytes |
| `src/game/air_wall.c` | `508780` | 287 cases / 320 calls including 288 airborne wall resolutions; actual raised/step probes, wallplants, wall transitions, moving surfaces, scripts and sound; 76 training cases, ten native QB observers and 548 OS audio callbacks; exact fixture bytes |
| `src/game/airborne.c` | `50ca00` | 308 cases / 473 calls including 337 complete airborne frames; shipped flip definitions, real training collision/transfer/landing paths, full scoring and text widgets, 48 native QB and 300 OS audio callbacks; 18 typed arithmetic NaNs by classification |
| `src/game/frame.c` | `500670`, `500710`, `5007a0`, `501850` | 544 cases / 909 calls; collision-cache setup, speed limits, revert recovery and focus input, including 59 complete airborne frames; 270 diagnostic/native QB/OS audio callbacks, all 227 parent instructions, 40 typed arithmetic NaNs by classification |
| `src/game/input.c` | `51fb90` | 512 cases / 532 calls; complete release-input matcher, all 159 instructions, exact history/global bytes, partial marks and raw argument copying |
| `src/game/frame.c`, `src/game/air_motion.c`, `src/game/animation.c`, `src/game/stats.c`, `src/script/params.c` | `500820`, `500900`, `500bc0`, `478fb0`, `4fc3c0`, `4fc420`, `580480`, `4208d0`, `47dc40`, `419c10`, `5114f0` | 382 cases / 1,795 calls including 1,146 existing object-setup calls; full projectile, rotation-completion and special-expiration paths; 75 native QB observations, 199 queued packets and 49 computed NaNs by classification |
| `src/game/skater.c`, `src/game/moving_contact.c` | `45f2d0`, `57c4f0`, `42ba10`, `427dd0` | 115 cases / 115 calls; type registry, world transform and contact-relative position; all 117 parent instructions and 28 computed NaNs by classification |
| `src/game/attachment.c`, `src/game/frame.c`, `src/core/number.c` | `503ec0`, `4ff200`, `487ad0` | 1,154 cases / 2,201 calls, including 930 existing setup/reference calls; full attachment acquisition and post-transfer speed updates; 11 native QB and 13 diagnostic callbacks, 125 computed NaNs by classification |
| `src/game/wallplant.c` | `509050` | 239 cases / 968 calls, including 251 complete wallplant-state updates and 717 existing setup calls; real training probes, moving contacts and four native QB callbacks; 168/173 instructions, with five unreachable defensive release instructions retained |
| `src/game/rail.c` | `500020`, `57cb60` | 253 cases / 253 calls; rail adjacency, retry timing, all four endpoint-distance checks, transformed points and aliased copies; all 241 instructions |
| `src/game/moving_contact.c` | `427a00` | 204 cases / 204 calls; retained-owner world position, original rotation, translation and aliases; all 54 instructions; 32 exact x87 quiet-bit corrections on untranslated X/Y |
| `src/game/lip.c`, `src/game/rail.c` | `50bf50`, `5092e0` | 232 cases / 984 calls; 272 lip/event and 712 existing setup calls, 115 native QB callbacks; 299/302 instructions, with three unreachable defensive release instructions retained |
| `src/core/quaternion.c`, `src/game/wallride.c` | `421440`, `5051b0` | 258 cases / 258 calls; axis rotation, raised head probe, overhead correction and velocity projection; all 182 instructions |
| `src/core/line.c`, `src/collision/probe.c` | `57c210`, `57c260`, `402f00` | 670 cases / calls; probe reversal, endpoint bounds and closest segment points with clamping and aliases; all 341 instructions; 166 exact x87 quiet-bit corrections |
| `src/game/rail_search.c` | `57c600`, `57cc30` | 862 cases / 2,474 calls; 1,724 clearance/side calls and 750 original moving-object setup calls; real training collision and ownership; 525/528 instructions with defensive cleanup retained |
| `src/game/rail_search.c`, `src/core/line.c` | `57e2d0`, `5902e0` | 626 cases / calls; full point/segment rail selection, distance/angle/side ranking, ordered candidates, numerical edges and output aliases; all 436 instructions |
| `src/game/grind.c` | `5799d0`, `4f8ee0`, `4f8f20`, `5627b0`, `43da70`, `46ba50` | 646 cases / 1,078 calls; balance stopping/selection, rail repetition score, walk parameter and trick variant; all 163 instructions |
| `src/game/grind.c` | `4fe120`, `511390`, `511570` | 210 cases / 1,032 calls; orientation reversal, board rotation packets and pending flip completion; all 151 instructions; 256 exact x87 quiet-bit corrections |
| `src/game/grind.c` | `5004b0` | 211 cases / 844 calls; actual grind-script selection, fixed-pool/heap allocation, pending flips and QB execution; 126/128 instructions |
| `src/game/grind.c` | `511e50`, `511e70`, `511e90`, `511ed0`, `511f60` | 317 cases / 554 calls; concrete list unlink/delete and pending-trick cancellation, matching and release order; all 140 instructions |
| `src/game/grind.c` | `461350`, `522e80` | 157 cases / 676 calls; object script setup, direct/slot/template trick selection, original parameters and completion events; 235/237 instructions |
| `src/game/rail_entry.c` | `50a770` | 420 cases / 2,100 calls; complete point kick, Natas, lip and grind entry; actual scripts, collision, sound, material, score, network and live component changes; 1,629/1,630 instructions |
| `src/game/rail_acquisition.c` | `50dae0` | 100 cases / 500 calls; fixed and moving rail search, eligibility, entry, transforms and contact ownership; 63 native QB callbacks; all 232 instructions |
| `src/game/wallride.c` | `50f830` | 169 cases / 855 calls; complete wallride update, moving surfaces, landing, rail catches, wall exits, release impulses and actual prior-contact events; 11 native QB callbacks; 1,124/1,127 instructions |
| `src/game/rail_state.c` | `504730`, `50c200` | 123 cases / 615 calls; complete Natas balance/spin state and connected-rail transition, actual scripts and live component changes; 122 native QB callbacks; all 452 instructions |
| `src/game/rail_state.c` | `50ddf0` | 116 cases / 685 calls; full rail update, moving rails, slope reversal, corners, endpoint scoring, training collisions and retained frames; 213 native QB callbacks; 1,173/1,179 instructions with defensive failed-contact paths retained |
| `src/game/movement.c` | `510830` | 88 cases / 813 calls; all six movement states, fixed/moving rail acquisition, landing, frame actions and script mutations, including eight retained frames; 202 native QB callbacks; all 350 instructions |
| `src/game/physics_startup.c` | `4fc5c0`, `4fc690` | 77 cases / 129 calls; actual parameter selection, repeated initialization and ordered lookup of 12 component links; all 120 instructions |
| `src/script/component_waits.c` | `472d20`, `472e70` | 77 cases / 143 calls; current/saved wait ownership, signed depth and live script traversal; 50/54 instructions, with alignment and unreachable restart excluded |
| `src/game/physics_reset.c` | `4317c0`, `4317e0`, `580880`, `511420` | 98 cases / 415 calls; shadow word copies, global camera lookup, animation flip synchronization and actual network queue behavior; all 54 instructions |
| `src/game/object_frame.c` | `45d920`, `45e4c0` | 112 cases / 264 calls; object script and component update order, live list changes, moved notifications and actual physics through virtual dispatch; all 59 instructions |
| `src/game/node_vectors.c` | `45c050`, `45c560`, `45c180` | 241 cases / 482 calls; node positions, fallback Z conversion and angles; typed/nested values, aliases and exact payload bits; all 54 instructions |
| `src/game/motion_orientation.c` | `425970` | 87 cases / 174 calls; node-angle orientation in original X/Y/Z order, with actual trigonometric and matrix dependencies; all 93 instructions |
| `src/game/motion_commands.c` | `461410`, `424020`, `4269f0`, `426c10`, `4274d0` | 224 cases / 753 calls; attached script spawning, node arrival, movement timing/speed/acceleration and command dispatch; three native QB callbacks; 330/333 instructions |
| `src/game/physics_commands.c` | `501600` | 104 cases / 423 calls; node movement through the real Motion command, body/reset/shadow/flip/network effects and camera-object QB; four native QB callbacks; all 183 instructions |
| `src/game/components.c` | `45d730`, `45d740`, `45d780`, `45d760`, `4e3f90`, `48dcd0`, `5bab90`, `45d720`, `42bb20`, `500ca0`, `4fc500`, `500db0`, `505440` | 194 cases / 498 calls; base/physics construction, wait cleanup, destruction, suspension, descriptor forwarding and zeroed allocation; eight native QB callbacks; 203/208 instructions |
| Component host-context integration | No additional recovered functions | 30 original cases / 114 calls replayed with both null and existing host contexts: 60 browser cases / 228 calls, 36 native QB callbacks; actual startup/object-frame QB, command effects and nested context restoration |
| `src/audio/jump.c` | `518d60`, `518ee0` | 381 cases / 417 calls; explicit/stored state selection, actual material/event lookup, playback and network queues; 3,300 OS audio observations; all 43 instructions |
| `src/game/jump.c` | `5002d0` | 160 cases / 320 calls; directional input priority, exact degree conversion, horizontal velocity and separate owner/cached basis rotation; all 70 instructions |
| `src/game/jump.c` | `509450`, `509a40` | 253 cases / 792 calls; complete jump and command wrapper through stats, floor/rail events, impulses, sound and final broadcast; 53 native QB and 2,356 OS audio observations; all 342 instructions |
| `src/script/registration.c` | `46f060` | 138 original cases / 330 calls replayed under two host scopes; stride, terminators, duplicate symbols and named Jump dispatch; all 19 instructions |
| `src/game/component_registration.c` | `45f270` | 129 cases / 135 calls; ordered count reloads, wrapped offsets and 75 initialization observations; all 14 instructions |
| `src/game/physics_flags.c` | 58 distinct member entries annotated in source | 18,127 cases / 36,350 calls; raw flags, stance, autokick, projectile state and flip threshold; all 257 instructions |
| `src/game/physics_state_actions.c` | `4fc840`, `4fcf90`, `4fcfc0`, `4fcff0`, `4fd630`, `4fd040`, `509a80` | 276 cases / 693 calls; timed flags, rail sound and full state changes through real events and orientation repair; all 184 instructions |
| Physics registration and named-command integration | No additional recovered functions | Full 109-entry table, named Jump and all 65 members through actual startup/object-frame QB; two prior host scopes and 1,560 command observations |


1,147 recovered functions are compiled to wasm32 and
tested against original x86 results, in both Node and the Codex Chromium browser. The module has no
runtime imports. The nine earlier core helpers retain their native C comparisons;
compiling them into this module does not itself verify them on WebAssembly.

The training BSP contains 6,217 nodes and 3,411 leaves. The recovered code retains
child ordering, tag bits, duplicate triangle references, and the original fallback
to all faces when a query overflows the candidate list. The recovered triangle
test rejects backfaces, uses the original determinant cutoff of `0.03`, and
retains its `1.00001` upper barycentric tolerance. It accepts both segment
endpoints. Some misses write an out-of-range fraction; earlier rejections leave
the output untouched.

The static-object segment query now combines BSP candidates, radius rejection,
triangle intersections, normals, surface flags, and nearest/farthest hit selection.
Tests cover all 605 training objects, including 44 empty objects and 996 queries
using the no-tree fallback. Equal-distance hits replace earlier hits. Filtered-in
hits can invoke a callback even when their distance is not selected, after which
the previous result is restored. The recovered result-copy helper preserves three
padding bytes, including callback changes to those bytes. Callback tests exercise
that rollback and changes to the selection global.

The static scene query now selects intersected scenes, collects grid candidates,
and invokes those object queries. It retains the original 15-scene limit, single-
cell duplicate behavior, multi-cell 2,047-candidate limit, and 8-bit stamp wrap.
It also handles cached candidates and the farthest-hit wrapper. The scene tests
include 127 queries with caches (including unusable and empty caches) and 3,312
callback observations. All global query arrays, object stamps, result bytes and
callback records match the original instructions.

Those scene tests use deliberately constructed grids and caches containing the
training geometry. A separate end-to-end check now runs the recovered collision-file
loader, cell constructors, and grid initialization/population before querying the
result. It covers the training file with normal and pre-expanded bounds, a zero-object
file, and a file with an empty object. The normal training grid has 905 object
references across its cells. Relocated file bytes, instance contents, every cell,
object-list order, allocation events, and final query results match the x86 oracle.
All 1,126 queries match, including 1,121 hits.

This loader expands the caller's existing bounds, initializes radius pointers,
and preserves untouched instance bytes. Grid boundaries use repeated floating-point
addition, as in the executable. The PC heap calls and exception machinery are
replaced by a platform memory adapter; the original memory manager is not recovered.
The full scene-loading wrapper, including render-sector binding, remains separate
work. Cache building, other collision classes, and the full skating update also remain.

Rigid moving-object collision now converts segments to local coordinates, tests
the original mesh and BSP, and rotates hit normals back to world coordinates.
Its constructor, geometry/radius binding, position/orientation changes, owner
accessors, and lazy sphere-based bounds are recovered. Tests rotate and translate
the training meshes; these are constructed test transforms, not recovered moving
objects from a running level. Large faces bypass the small-face radius rejection,
as in the original. The shared object prefix is 16 bytes; static instances remain
24 bytes, and the rigid moving class retains its original 212-byte layout.

The collision probe at `004172f0`, called throughout the skater code, now combines
the static and moving scene paths. It preserves nearest/farthest selection,
default versus per-probe cache choice, callback dispatch, and the intrusive
references to moving objects. The end-to-end checks use the loader-built training
grid and three moving instances. They cover prior static hits, disabled objects,
empty lists, cache misses, null cache entries and owners, callback mutations, and
removing existing references from the head, middle or tail of their lists. The
620 scene/probe checks include 496 full probes, 2,241 callback observations and
257 final attachments to moving objects; result bytes and reference graphs match.
The probe constructors and point setter are also recovered. They initialize only
the original fields; the checks poison all other bytes and verify that they remain
untouched. Constructors are not safe substitutes for resetting a linked probe.

The first four skater routines are recovered: quadratic drag, friction, a four-way
nearby-obstacle query, and the script-facing forward-obstruction query. The latter
uses the recovered script parameter accessors to read its optional distance.
The collision checks use all 605 training objects and three constructed moving
instances. Temporary moving-object references are removed exactly as in the x86
code; body bytes, physics-component writes, object lists and collision state match.
The velocity checks cover small speeds, saturation, negative coefficients and time
steps, and nonfinite inputs. Forty-seven NaN fields are compared by classification.
These are individual routines tested with constructed states. The complete skater
movement update, controller input, tricks and camera remain unrecovered.

The surface query at `005003a0` now probes the component's segment, applies its
collision filters and updates three surface classifications. Flag precedence is
1, 2, 8, then 4; absent those flags, the surface normal is compared with the sine
of script parameter `0x3eede4d3`. Misses preserve the previous classification. The
full-query checks cover filtered misses, static/moving hits and replacement of an
existing moving-object reference. All 1,815 full-query results match the x86
oracle, including 572 hits. The classification suffix is tested separately with
flag combinations and adjacent float normals around angle thresholds. That suffix
and the platform math adapter are not counted as additional recovered functions.

The up-vector update at `004fe860` is also recovered. It probes 72 units along an
upward requested vector unless context identifier `0xd443a2bc` bypasses the probe.
A hit substitutes `(0, 1, 0, 1)`. If any of the four vector components differs from
the stored target, the routine saves the source vector, sets its blend field to
one, installs the up vector in the body's matrix and rebuilds the other two axes.
The fixed axis is preserved verbatim; the rebuilt axes are normalized and their W
components become zero. Translation is untouched. Equal alignment scores and NaNs
retain the original branch choice.

The orientation checks use every training collision object and constructed moving
objects, plus degenerate matrices, signed zeros and nonfinite vectors. All body,
component, collision-state and reference-list writes match; 129 NaN fields are
compared by classification. Read-only x86 hooks supply the probe/matrix coverage
counts; those hooks do not substitute any game calls. The context identifier's
meaning remains unknown, and this is still an individual update routine rather
than the full skater loop.

Configured drag (`004fe6a0`) now follows the original component/script path. The
component lookup returns the first matching entry. The selector (`005802e0`)
chooses one of eight parameter structures from the body's enable flag and the
core-physics component's mode fields; unrecognized modes select the default.
Numeric lookup (`00580400`) tries that structure before the global symbol. Local
integers convert through a float, while a global integer fallback remains exact
until its caller rounds it. The drag routine reads both coefficients before
applying its override and chooses between them using the state component's flag.

Eight constructed script graphs exercise direct values, aliases, nested values,
wrong types, missing members and integer rounding. The full-chain checks verify
3,072 velocity updates and preserve all other body/component bytes; 668 NaN fields
are compared by classification. Read-only hooks verify the original's 6,144
parameter reads and the order of the two lookups before each drag call. Enabled
bodies require a core-physics component, and numeric lookup requires the selected
structure to be loaded. Whole archived training QB loading is now checked separately;
the skating parameter tests still use constructed graphs rather than runtime startup.

The stat-dependent parameter chain (`00580490`, `005805b0`, `00580790`) is now
recovered together with its script, settings, player-state and object-lookup
dependencies. It selects local or global parameter structures, interpolates a
pair using a stat, applies the conditional modifier and difficulty scale, and
limits the result in the original direction. Stored player flags can override
the stat; a gameplay bit overrides it again before the final +3 modifier. The
gameplay-bit query preserves the original two successive checksum lookups and
its global byte write. These routines inspect network state without performing
network I/O.

The 11,141 checks run the actual x86 callees on constructed graphs. They preserve
every byte outside the observed output/iterator/global writes and cover optional
members, aliases, duplicate object keys, missing players, split-screen state,
modifier clamping, ascending/descending limits, signed zeros and nonfinite values.
Read-only hooks verify the original call sequence. Pair padding is preserved;
missing pair values write zeros, whereas missing scalar values preserve output.
One settings getter retains its original pointer-valued fallback because PUSH ECX
initializes the stack slot before the disabled assert. The stat arithmetic adapter
retains a 24-bit significand between the original float-store boundaries, including
the wider intermediates and subnormal cases tested here. These are recovered
calculations, not a complete movement update or a loaded script runtime.

The downward ground update (`00504b40`) now uses the recovered collision, stat,
timer and matrix paths. It casts 500 units downward unless its state/gate flags
skip the probe, rejects surface flag 8 and normals below 0.2, updates two timed
state flags, and can rotate the skater upright. It copies the resulting matrix
into the physics component and releases temporary moving-object references.
The call site also establishes that the stat fields belong to the skater body
itself; the body and stat views now share that recovered layout.

The tests use all 605 training collision objects and constructed moving objects.
They observe 1,452 accepted ground hits, 36 surface-flag rejections, 16 normal
rejections and 436 reference unlinks. Whole body/component/state bytes, timestamps,
collision state and reference lists are checked. The timing helpers preserve
unsigned wrap, signed FILD conversion and the original rounding order; the
frame-counter producer and real browser clock integration remain unrecovered.

Rotation uses the executable's SSE D3DX matrix-multiply routine (`005df4ac`),
selected explicitly through the lifted dispatch slot. Its outer rows use pairwise
addition while its middle rows accumulate sequentially. Input/output aliasing is
preserved. The original CPU/registry selector and other multiply backends remain
unrecovered; this validates the selected SSE path. Axis-angle construction retains
its asymmetric float stores and intermediate precision. Sine and cosine still
use the platform adapter with the hardware-accuracy limit described below.

Script symbol lookup and parameter access now preserve alias chains, anonymous
nested structures, integer-to-float conversion and last-successful-match precedence.
Missing values leave the output untouched. Tests construct symbol/component graphs;
they do not yet load or execute QB scripts. Valid graphs must be acyclic.
This is still an engine library, not a game.

The grounded movement path's braking decision, braking-inhibition predicate,
acceleration eligibility, acceleration and braking operations are now recovered.
They execute their real stat and script-parameter callees in the x86 comparisons.
The acceleration threshold includes equality and unordered values; braking stops
only strictly below twice the per-step decrement. The non-stopping brake path
retains the original fourth-coordinate behavior, doubling velocity W. The velocity
alignment helper preserves its sequential copy behavior even with partial overlap
with the skater's forward axis. Gravity selection preserves the state-dependent
divisor, gameplay-bit access and optional falling multiplier.

These checks exposed underflow in the earlier float-only vector normalization and
length helpers. Those helpers now retain the x87 exponent range through length
and scale, rounding the significand after each operation and storing float only
at the original coordinate writes. The new motion suite has 6,499 cases, including
192 direct vector-helper cases; 1,415 NaN fields are compared by classification.
All prior browser comparisons still pass. Input states and script graphs are
constructed fixtures: the full movement update and controller sampling remain
unrecovered. QB-buffer loading is verified separately below.

The resistance wrapper (`00506df0`) now runs configured drag, slope turning and
friction as one recovered chain. The slope turn projects downhill onto the slope,
measures a signed angle and limits the turn by the per-step script rate. It
premultiplies the body and cached matrices independently, preserving any difference
between them. Of 1,536 resistance cases, 61 skip the whole chain, 1,475 apply drag,
301 perform slope rotations, and 1,174 apply friction. Another 1,536 cases call
the slope-turn routine directly. Matrix and velocity writes match the original
instructions, with NaNs compared by classification. These are still constructed
states; the larger grounded update and collision response remain incomplete.

The obstacle-repulsion chain (`005055b0`, `00501c90`) now probes along both signs
of the skater's side and forward axes. It combines hit normals, scales the push
by penetration fraction, restores velocity to the skating plane while preserving
speed, and can turn away from the last retained surface normal. Its timestamp
loop repeatedly checks the opposite direction's timestamp; the recovered code
preserves that behavior, unsigned wrap and the inclusive 500-unit window.

The checks cover all 605 training collision objects, constructed moving objects,
previously attached probes, zero and negative settings, the timestamp boundary,
and overlapping segment inputs. They observe 539 repulsion responses, 862 matrix
rotations, 1,376 attachments and 1,632 unlinks. Complete state and reference-list
writes match the original instructions; 352 NaN fields compare by classification.
The projection helper also covers overlapping normals and degenerate vectors.
All earlier browser suites pass against the same current module. The existing
signed-angle and hardware-accuracy limits still apply. The larger movement sweep and wall response are covered below; the complete
skating loop remains unfinished.

Low-speed side correction (`00503b30`) now uses the held-button timer (`0046b920`)
to choose a probe distance. If both buttons are pressed, button 0x60 supplies the
timestamp while button 0x80 reverses the direction. The first collision proposes
a displacement along the hit normal; a second probe checks that displacement.
Only a clear second probe changes the position. The 5,032 complete cases observe
1,927 first hits, 326 blocking second hits and 1,601 position updates. They check
all body/component writes, unchanged input state, timestamps and moving-object
references, including timer wrap and nonfinite script values. NaNs compare by
classification in 9,952 fields; the browser-input producer remains unrecovered.

An extreme-distance case exposed premature overflow in the earlier static-object
radius test and grid direction normalization. These now retain PC24's wider
intermediates and the original float-store boundaries. The retained failing case
and every earlier browser suite pass with the correction. This expands tested
coverage; it does not establish arbitrary-input or physical x87 parity.

Wall-tangent turning (`005039f0`) now rotates the horizontal velocity and both
orientation matrices. It returns the folded, unscaled angle while storing the
scaled turn through an output pointer. Velocity uses the wider intermediate angle;
each matrix rotation rereads the stored float. The checks preserve that distinction
even when the output overlaps a velocity or matrix field. The heading helper
(`00403ef0`) uses the game's own polynomial approximation, with its original
rounding sequence and unclamped input domain. These routines are prerequisites of
the grounded update and the wall response covered below; the grounded parent
remains unfinished.

Collision-event prerequisites now include the node-name table and its global
wrapper, inline/sized script-array access, recursive unnamed flags, the multiplayer
gate, and three collision-owner accessors. Node-table collisions use linear probing
with wrap at 16,384 slots. The first matching node wins; missing name fields yield
zero. Unnamed flags test literal equality before resolving structure inclusions.
The moving-reference check clears stale identifiers only when a previous moving
identity remains after its reference disappears; otherwise it preserves the hit
checksum. The 2,552 comparisons cover all stored flag-type bytes, nested aliases,
hash wrap/collisions, ignored inline-array indices, connection state, unsigned
player counts, and poisoned probe bytes. All writes and integer results match
exactly. Table population and collision-event dispatch remain work; the QB executor
is verified separately below.

The script instance constructor (`004738e0`) now clears its original 244-byte
layout, inserts the instance at the global list head, advances the count/serial,
and selects its embedded control/call storage. Current-instance and list access,
the instruction-pointer predicate, wait clearing and object-wait setup are also
recovered. Construction is not a reset of a linked, running script.

The complete wait-state updater (`00473050`) handles frame counters, scaled tick
durations, elapsed-time deadlines, the shared gate and virtual component waits.
Tick-duration equality remains waiting at zero; a short duration cannot finish
on its first update. Unordered comparisons take the subtraction branch, as shown
by the instructions rather than the generated pseudocode. The elapsed-time path
retains exact signed integer loads before the high-half unsigned conversion.
Tests include adjacent thresholds, counter wrap, nonfinite values, changed owners
between callbacks and overlapping object-wait setup. They compare all instance,
list, owner, log and global bytes; 166 NaN fields compare by classification.
Virtual wait handlers are explicit recording/mutation fixtures, not recovered
game components. Clock production and gate reset remain separate work; the script
setup/call/cleanup/execution paths are checked separately below.

Bytecode branch resolution (`00470c60`) now follows long and short relative jumps,
weighted random choices using either original PRNG stream, choices that avoid a
previous result, and shuffled choice sequences. The PRNGs retain the original
32-bit wrap, arithmetic shifts and three-word state updates. Random-choice cache
records match on the offset table, type, count and script ownership. New records
prepend to the allocation list; at 100 records the oldest allocation is released.
Lookup does not promote a record. Avoid-repeat choices permit at most 100 retry
draws. Shuffled choices preserve the original index advance before selection,
ten swaps per item, and the optional swap at a cycle boundary.

The branch suite compares 2,726 complete resolver calls, including repeated visits,
backward/chained jumps, zero and signed weights with valid totals, cache reuse and
ownership mismatches, and the allocation cap. It executes 71,018 primary and 1,440
alternate PRNG calls across the full suite. Heap allocation/release are platform
adapters; the original generic heap route runs with those services instrumented.
Pool routing, allocation failure and malformed/nonterminating bytecode are outside
this check. The 2,038 constructed cases match every integer result, global and
memory byte. They do not establish loading or executing an original QB file.

Script value ownership and copying are now recovered. Constructors preserve the
original untouched padding. Array storage keeps one value inline and uses a
separate buffer for multiple values. Recursive cleanup disposes owned strings,
pairs, vectors, structures and arrays while preserving borrowed references and
pooled strings. Insertion removes all matching name/type entries, treats integer
and float members as replacements for each other, and compares checksum literals
when replacing unnamed flags. Remaining members retain their order. Structure
containment follows owned structure members, excluding borrowed references and
arrays. The 2,131 ownership cases compare all memory and release-time payloads
and list links, including repeated clearing and every stored type/flag byte.

Copying reconstructs owned nested values and preserves borrowed values. The
optional borrowing mode converts owned structures/arrays to reference types.
Clearing precedes source reads, including destructive self-copy behavior.
Scalar array copies use sequential raw words, preserving signaling-NaN bits and
the original overlap behavior; null owned source elements leave destination
words untouched. Structure merging deep-copies members through the recovered
insertion rules. Interning compares the raw string CRC alone and returns the
first matching entry, even when its text differs. Empty strings retain their
special zero checksum. The 1,724 copying cases compare every byte exactly, with
no NaN classification allowance. Allocator pools and failures remain outside
these checks; heap allocation/release and temporary scopes use the explicit
platform adapter. QB-buffer loading and the command executor are checked separately
below; native gameplay handlers still require their own implementations.

The typed parameter setters now allocate and insert real components, copying text
before replacing its old owner and transferring ownership of supplied arrays and
structures. Float, pair and vector setters preserve raw coordinate words. Blob
allocation/copy uses the full 32-bit size while its stored length truncates to
16 bits; checks cover both sides of that boundary. Structure assignment clears
before merging, except for self-assignment. Member lookup returns the last matching
component and traverses anonymous global structure inclusions. The instance's
argument-snapshot routine deep-copies a source only when it belongs to an owned
structure reachable from current parameters or arguments. Borrowed references and
array-held structures do not trigger that containment rule. These 950 cases compare
all bytes, constructor padding, heap snapshots and disposal order exactly.

The bytecode helpers now decode unaligned words, advance individual tokens and
skip compound values or script bodies. Unknown tokens leave the cursor unchanged;
nested structures and arrays balance their own delimiter type. Script skipping
consumes END_SCRIPT and exactly one following numbered-line token, if present.
The original instructions supplied every expected offset. Checks traverse all
374,236 bytes of eight archived training QB files to each file's final EOF byte,
including embedded payload delimiters and the real compound/script boundaries.
This is bytecode traversal, not parsing values into a loaded symbol table or
executing the scripts. External bytecode still needs bounds and termination
validation before calling these unchecked internal helpers.

Random-range value decoding preserves the original choice between inclusive
integer ranges and floating ranges. Integer candidates use a signed 0.1 bias
followed by the CRT conversion; a 1e-5 tolerance selects the integer path, including
the original unordered-comparison behavior. Floating ranges retain PC24 rounding
at each arithmetic step and a wider intermediate exponent. Both PRNG states,
integer results and finite float words match exactly across 5,076 calls, including
repeated evaluation of all 19 range occurrences in the training scripts. Only
typed float NaNs compare by classification (277 results); integer payloads never
receive that allowance. The selector explicitly uses its low byte at the browser
entry point. Running-game FPU settings and x87 exception flags remain unverified.

The expression value helpers preserve mixed integer/float comparison precision,
symbol resolution, string-length ordering and structure member inclusion. Equal
structures can satisfy both less-than and greater-than: those operations implement
non-strict inclusion. Array equality accepts identical pointers; the fallback for
different arrays at `0049f4b0` really returns false unconditionally in the pinned,
modified executable. It is not an implementation placeholder. Array-to-component
access supports owned copies and borrowed containers; local-string elements are
unsupported by this routine. Four signaling-NaN stores differ from Unicorn's raw
result: the port requires the exact Intel quiet bit, and both words are retained
in the oracle report. Other copied words are compared exactly.

The expression evaluator now executes all eleven binary operator tokens supported
by `0046d450`, with its original precedence table, parentheses and final value
copying. It handles arithmetic, comparisons, integer truth-word AND/OR, string
concatenation, pair/vector operations, array indexing/concatenation, and structure
lookup, merging and subtraction. Multiplication has higher precedence than division
in this table. String results are limited to 199 characters. The tests include
complete nested and two-operator expressions, type errors, stack overflow, borrowed
results and the original allocation/disposal order. Error strings are real relocated
C data; their text and pointer fields are verified separately from numeric words.

Both evaluator error paths are retained: initial guard errors stop after clearing,
while errors inside operator dispatch still run finalization and underflow the
value index. Arithmetic retains exact integer loads and PC24 rounding with a wider
exponent. Residuals preserve halfway-rounding decisions that a double intermediate
can otherwise lose. Finite results are exact in these checks; 283 typed NaN fields
compare by classification. Invalid pointers/indices, allocation failures and integer
division overflow are outside the returning-call fixtures; the latter explicitly
traps in the port. The evaluator is now connected to the QB bytecode parser;
the script command executor is checked separately below.

Six mutually recursive QB parsers now construct named values, individual
components, parameter lists, structures, arrays and expressions. Structures merge
anonymous braces into the current target and permit line breaks around `=`;
parameter lists stop before line terminators. Empty arrays preserve their old
target. Nonempty arrays first count and choose a type, then revisit the bytecode
to construct values. Both passes resolve random choices independently, including
cached avoid-repeat and shuffled choices. Mixed integer/float arrays convert
integers only during construction; copied float words retain their raw bits.

Expression parsing retains the original shared evaluator and scratch component
even during recursive structure parsing and native-predicate parameters. Native
predicates receive the parsed parameter graph and current script; only their low
return byte is used. The callback fixture records those arguments, mutates a real
integer parameter and checks cleanup after the call. It is test instrumentation,
not a recovered native command. In-place checksum resolution preserves component
metadata and ignores unsupported symbol types. Adjacent negative numeric literals,
early expression termination and the scratch state left behind are also checked.

The parser suite constructs all 815 top-level definitions from the eight archived
training files: 651 stored script bodies, 159 structures, three arrays and two
integers. This includes the full 183,123-byte training node array. The expected
definition boundaries come independently from the original token-helper oracle.
All returned cursors, fixture bytes, observed globals, allocation/release order and
6,366 temporary-scope events match, with one typed global NaN checked by
classification. This parser suite copies script bodies rather than executing them.
QB-buffer loading and script setup/call/cleanup/execution are checked separately below. These
unchecked internal parsers require valid terminating grammar and successful
allocation; browser-facing file validation still needs to be built.

Global value registration now allocates symbols, records the normalized source
filename checksum, and transfers parsed payload ownership into the global name
table. It prepends duplicate names; removing an old definition is the outer
loader's responsibility. Unsupported value tokens still create an empty symbol
and leave the input cursor unchanged. Direct lookup does not follow aliases;
the existing resolver does. Unlinking matches pointer identity, preserves absent
entries, and clears a removed entry's next link. Shared iteration visits bucket
chains in order and resets both globals at exhaustion. Its original final read
requires one readable slot after the 4,096-bucket table.

Symbol disposal unlinks first. Flag bit 2 preserves the detached entry and payload;
other entries release owned strings, pairs, vectors, structures, arrays and script
storage before releasing the entry. Constructors retain the original high flag
bits and untouched header bytes. Checks cover every stored flag/type byte, duplicate
names, collision-chain positions, missing names, null/pooled values, and complete
registration/disposal of all 164 non-script definitions in the archived training
files. Return values, fixture bytes, globals and 8,788 scope events match exactly.

Script-body hashing now matches all 651 archived training scripts. It ignores line
tokens and excludes END_SCRIPT, while retaining identical byte values inside token
payloads. Compressed script registration, cache lifetime and the complete QB-buffer
loader and script setup/invocation are now tested separately below. Runtime startup
and file I/O integration remain separate recovery work.

The LZSS encoder now retains the original 4,096-byte ring window, 18-byte maximum
match, tree insertion/replacement order and deletion rules. Sentinel-parent writes
and untouched allocator bytes are preserved. Initialization selects the original
compression temporary-heap category, allocates four buffers, and initializes only
the original root/parent ranges. Encoding frees those buffers in reverse allocation
order while retaining their addresses in the shared globals. Empty input still
allocates and frees, preserves the old match state, and emits no diagnostics.

All compressed output bytes match the original instructions, including group
boundaries, short tails, window wrap, long repetition and incompressible input.
Every archived training script body is included with the exact terminator and
optional numbered-line bytes supplied by the loader. All 761 complete encode calls
also pass through the existing decoder in WebAssembly and reconstruct the input.
The tests compare the entire tree, window, fixture memory, globals and heap events.
Verbose logging uses only the low argument byte; 243 calls compare format strings
and raw integer/double arguments exactly. Formatting and OS debug output are a
platform boundary, not recovered CRT code. The original PC24 arithmetic is retained
for its printed compression ratio. Allocator pools/failures, overlapping or invalid
buffers, and concurrent use remain outside the internal codec contract.

Compressed script registration now creates the symbol, tries compression in the
original 20,000-byte scratch buffer, and stores a checksum/size header followed by
either compressed or raw bytes. It reloads an existing cache entry before recording
the filename checksum. Cache acquisition resolves symbol aliases, rejects non-script
symbols, decompresses or copies the body, prepares command tokens, and increments
references. Release looks up the supplied name directly. Zero-reference entries
either become idle or are immediately evicted according to the cache flag.

The cache preserves the original idle-list order and both eviction thresholds:
the largest heap block must cover the request plus a 128-byte reserve, then idle
entries are discarded while the active pool contains at least 100 entries. Reload
restores the old reference count, including the original quirk that a reloaded
zero-reference entry is not returned to the idle list. Fixed-pool membership,
free-list allocation/release, signed peak-count updates, heap gap/block metrics,
and lookup-table construction/insertion/removal execute recovered code. Generic
heap storage remains a platform adapter; tests use a finite release schedule to
change available space and exercise the actual eviction loops.

All 651 archived training bodies pass both cache lifecycles and registration with
active reload. Checks compare every fixture/global byte and heap event. Bytecode
preparation rewrites only command names at line/conditional starts, using the
verified native-binding table as data; it does not execute those native functions.
Their addresses must be relocated to real target implementations before execution.
Cache construction/destruction and runtime startup remain unrecovered. Command
invocation and the executor are checked separately below. Internal routines require initialized
instances, successful allocation, sufficient idle entries and well-formed bytecode.

The complete QB-buffer loader (`00472420`) now runs both original passes. The first
collects readable checksum names; the second loads values and compressed scripts,
skips or enters debug sections, and switches temporary heaps. Ordinary values
replace existing symbols on every load. Scripts with matching body checksums keep
the original symbol, stored line bytes and source filename, even when the newly
supplied file uses different line numbers. Every in-flight source-file checksum
is checked through allocation/release observations, not just at the final return.

The global readable-name map retains the first spelling for each checksum. Local
name tables retain duplicate entries and release collision nodes before their
inline bucket text. The original duplicate-name CRT comparison runs in the x86
oracle with initialized C-locale TLS; all 691 comparisons leave game state and the
modeled Windows last-error value unchanged. Its unused result and Windows locale/TLS
bookkeeping are omitted from the port. Locale changes are outside these checks.

The change journal records created or replaced symbols, preserving padding, and
undoes entries in forward order. Replaced scripts can reload an active cache both
before unlinking and after replacement or restoration. As in the original, undo
inspects a symbol's type/name after releasing it; the memory adapter must retain
those bytes until allocation reuses them. These internal routines do not add
capacity checks to the original 500-entry journal or readable-name storage.

Whole-file tests load all eight archived training QB files, verify their symbol
names, script checksums and source filenames, undo each file's definitions, and
load all eight in sequence into one symbol table. All 815 definitions are covered,
including 651 scripts. Synthetic cases cover every ordinary value family, changed
and unchanged scripts, debug sections, duplicate names and cached replacement.
The test heap reuses top-of-arena scratch, while all concrete game callees execute.
This recovers loading from a supplied buffer; it does not yet connect filesystem
or archive loading, initialize the runtime or execute script commands.

Script loop, switch and return handlers now execute recovered code. A second active
loop moves the inline loop frame into ten heap slots and repairs loop pointers saved
in suspended callers. Repeat counts are parsed only on the first visit; missing
counts loop indefinitely, and a zero count underflows as in the original. Break
skips nested loops and parses the matching repeat without caller arguments. Switch
selection owns a copy of its selector, follows the original unsigned offsets and
parses grouped labels before entering their shared body.

Returning releases the callee's cached script before restoring its caller, including
argument ownership, object-reference links, loop position, deferred script, wait
state and flag bits. Raw wait-time bits, including signaling NaNs, are preserved.
The return value is the callee's incoming flag bit, not the restored caller's bit.
Checks compare all fixture/global bytes and heap events, including 34 real loop
starts and four nested-switch skips from archived training scripts. Repeat counts
and switch selection use synthetic cases; native commands are not executed.
Call setup, command dispatch, stack cleanup and the complete executor are now
checked separately below. These internal handlers require valid initialized frames, bounded
stacks, terminating bytecode and successful allocation.

Script-event cleanup (`00473010`), required by failed script setup, now runs its
complete concrete call chain. It unregisters the explicit event table, disables
its handlers and disposes their owned parameters. Flag `0x10` additionally removes
subscriptions outside that table. The event-table pointer and flag survive cleanup.
Listener removal deletes only the first matching subscription; empty sentinels are
removed even if no listener matched. The shared hash iterator advances before the
current entry is deleted, including entries in collision chains.

Both virtual deleting destructors are recovered and relocated into actual callable
WebAssembly method tables. They restore the base methods, unlink the node and use
the generic heap when deletion is requested. Empty list sentinels instead use the
original selected/alternate pool membership checks before generic release. Tests
exercise those distinct paths, duplicate listeners, empty buckets, signed counts,
wildcard groups, owned strings, repeated cleanup and all fixture/global bytes.
This is event unsubscription/disposal; event registration and event delivery are
not yet recovered. The script executor's mutually recursive setup, cleanup, call
push, deferred-script and command-dispatch paths are checked below.

The complete script executor (`004750b0`) now runs together with its mutually
recursive setup, call push, immediate calls and deferred cleanup. Setup snapshots
aliased arguments before disposing the previous script, loads defaults, merges
caller arguments and handles a missing script through event cleanup. A third
suspended call copies the two inline call frames into sixteen heap slots. Saved
frames retain packed flag padding and raw wait-time bits. Deferred scripts execute
before state disposal, in reverse order for suspended callers.

Command invocation handles prepared native/member/component calls, named and
argument-derived commands, object-qualified calls, expressions and assignments.
It preserves the original return-width distinction: object descriptor handlers
use their low byte, while component descriptor handlers test the full word.
Native and virtual calls are real function-pointer calls with explicit relocated
interfaces. Tests supply recording/mutation callbacks at those boundaries; they
do not claim recovery of the game's gameplay handlers. Missing-command diagnostics
retain their original format and arguments. The original CRT formatter executes
20 times in the oracle; its fixed unknown-name buffer matches all 20 bytes.

The executor tests cover nested bytecode calls through stack expansion, cleanup
of sixteen owned frames, both waiting return codes and resume, loops, switch,
if/else, long/short jumps, returned parameters and deferred calls. Two end-to-end
cases register/compress a script, acquire/decode it through the cache, set it up,
execute its bytecode and clean up. Ordinary completion and waiting clear the
current-script global; immediate return code 5 deliberately retains it. All
fixture/global bytes and heap events match the original instructions exactly.
This executes synthetic programs through the recovered interpreter. Training
gameplay still requires native/virtual handlers,
runtime startup, asset integration, movement, rendering, input and sound.


Script instance destruction (`00474420`) now executes its whole concrete chain:
deferred scripts and owned stack cleanup, event unsubscription, completion-argument
disposal, list unlinking, random-branch ownership detachment, event-table lifetime,
external reference clearing and script-count updates. An event table with active
calls is marked dead for its caller to dispose later. Otherwise its entries and
allocation are released immediately. The destructor retains stale own list/event
pointers, as the original does; it is not an idempotent cleanup API.

The referenced base and both of its destructor variants are recovered, with a
callable relocated method table. Unowned reference nodes keep their links; owned
ones are detached using their actual object. Script allocation uses the selected
fixed pool even when it is exhausted, and release checks both pools before the
ordinary heap. The host still supplies initialized generic memory services.

The one-shot wrapper (`004752f0`) now allocates and constructs an instance, sets
up and executes its script once, copies its current arguments to the output,
then destroys and frees it even when execution yielded. Tests run this complete
chain with pooled and ordinary allocation, nested bytecode, missing scripts,
aliased output and native waits. The spawned-script stop, individual deletion,
and finished-ordinary-script collection walks are recovered too. Mass stopping
sets a pending flag during a frame update; the update itself remains unrecovered.
Owner stopping searches suspended owners, with separate current-checksum and
whole-stack-checksum variants. Matching owner and checksum may occur in different
frames. Callback-insertion checks distinguish walks that capture the next link
before destruction from walks that read it afterward. All fixture/global bytes,
21 native-command callback observations and memory events match the original x86
and WebAssembly results. General object-event registration/delivery and actual gameplay handlers remain
necessary; the frame scheduler, spawn/network wrappers and collision-event
dispatch are now recovered below.


Compact parameter serialization (`00479e20` / `00479b80`), needed by synchronous
script dispatch, is now recovered with all of its concrete encoding helpers.
Headers first search the byte-index name table, then the halfword-index table,
then emit the full checksum. Integer encodings distinguish zero, positive unsigned
byte/halfword, negative signed byte/halfword and full-width values. Float magnitudes
below the original double constant `0.0001` use a zero tag; other floats preserve
their raw payload bits, including signaling NaNs. Strings, pairs, vectors, checksums,
structures and arrays retain their exact output tags. Script bodies encode the
original fixed placeholder checksum. Unsupported structure components return zero;
unsupported array types still emit the array header.

Capacity behavior is preserved rather than made transactional. The integer helper
stages its result before checking the exact size; other helpers conservatively
budget for full checksums, even for compact names. Arrays and nested structures
can leave partial bytes when they return zero. Array counts serialize as halfwords
while full-word counts drive traversal. Callback tests verify changes made before
component inspection and suppression of callbacks inside nested values.

The checks parse the supplied `scripts/game/misc/compress.qb` through the recovered
array parser: its actual tables contain 252 byte-index names and 30 halfword-index
names. Those tables are then used while parsing and serializing every one of the
164 ordinary definitions from all eight archived training QB files. Synthetic
checks cover boundary capacities, every array type byte, every component type,
truncated name indexes, negative table counts, nested structures, strings and exact
NaN payload bytes. All 4,665 cases / 5,159 calls match the original instructions.
The compression QB is explicitly the extracted loose file, with its source hash
recorded; archive precedence for global startup scripts is still separate work.
The dependent message queue, script-spawn wrappers and frame update are now
recovered too. The actual gameplay handlers remain separate work.

The network-message enqueue routine (`00457eb0`) now runs its complete concrete
call chain. It creates one shared payload and queues a destination node for each
eligible peer. Full-word `0xff` broadcasts; other recipients with the low-byte
high bit set exclude the corresponding identifier. Ordinary messages require an
exact peer state of one, except direct message ID nine; reliable and sequenced
messages instead reject state bit eight. Ordinary/reliable replacement removes
matching message IDs before creating a new node. Sequenced messages preserve
per-group counters, explicit sequence overrides, wraparound and their original
broadcast-priority quirk. Queue insertion uses signed ascending priorities and
inserts ties before existing nodes; enumeration follows the reverse links.

Message creation retains padding, copies payload ownership and optionally runs
the original RLE or recovered LZSS encoder. The RLE routine preserves its empty
output for a one-byte input. Compression compares encoded size before adding the
outer three-byte header, and unsupported compression modes retain the original
empty candidate behavior. The last destination's removal frees the payload and
message before invoking the node's concrete virtual deleting destructor. These
calls create queues only; they do not provide sockets or receive/acknowledgement
processing.

The 3,329 queue cases / 4,718 calls cover exhaustive short binary RLE inputs,
run/literal limits, all peer flag bytes, recipient modes, priority ties, group
boundaries, sequence/time wrap, compressed sharing, replacement and reference
underflow. All output, padding, list links, heap records, codec globals and 742
raw diagnostic calls match the pinned x86 instructions and WebAssembly. Valid
circular lists, existing direct recipients, successful allocation and fitting
payload buffers remain internal preconditions, as in the original engine.

Script spawning (`00475420`), synchronous dispatch (`00475790`) and the spawned
frame update (`00475920`) are now recovered. Native spawning constructs a temporary
instance, calls the configured native handler once, destroys the instance and
returns null. Bytecode spawning sets up an owned instance without executing it,
copies optional completion arguments and retains the original low-bit flag rules.
Synchronous bytecode dispatch repeatedly calls the real executor until completion;
it does not bypass waits. Native and member synchronous dispatch instead pass a
null script pointer to their actual relocated handler interfaces.

The frame scheduler captures the next spawned instance before callbacks, resets
the shared wait gate, checks pause and owner-activity conditions, runs completion
commands before disposal and applies requested mass stopping after the update.
Newly inserted instances and ordinary-to-spawned flag changes obey the captured
traversal order. The owner wrapper (`00461480`) broadcasts first when requested,
binds the spawned instance's reference to its owner and executes it once. Both
message wrappers (`00473350` / `00473420`) use the actual recovered serializer and
message queue, with original IDs, sequence group, recipient choice and payload
lengths. Failed parameter serialization still queues the two-word header.

There is one explicit portability difference: the PC spawn wrapper copies three
unwritten stack bytes into the tail of its 16-byte packet. The port zeros those
three padding bytes. The x86 oracle seeds exactly those preexisting stack bytes
to zero at wrapper entry; the original instructions then execute unchanged. No
defined message field or other output byte is excluded from comparison. This is
not a claim that arbitrary original stack residue is reproduced.

The collision-event wrappers (`00434a60` / `00434bf0`) now reach this executor path.
Global or reverse-searched local node data supplies the script and network flags;
on a local search miss, the original uses the first element. Moving-owner node
data supplies optional arguments. The multiplayer gate precedes the event-mask
write. Mask terms are added rather than ORed, retaining duplicate-bit carries and
masked shift counts. Callback ownership takes precedence over a persistent moving
reference; node-provider callbacks can change the owner/checksum before they are
reread. Script ownership belongs to the event component's owner.

The combined 1,693 cases / 2,547 calls compare full output, fixture/global state,
heap ordering and 470 configured command/activity/node-provider callbacks. They
cover all frame flag bytes, finite synchronous waits, shared frame waits, mixed
lists, completion commands, deferred stops, callback insertions/mutations, global
and local collision nodes, duplicate names, probe-owner precedence and network
gates. The exact node-provider and native gameplay handlers are interfaces in
these checks; their actual implementations, runtime startup and the complete
skating/rendering loop remain separate work.

General object-event delivery (`00462f00`) and its owner wrapper (`004609f0`)
now run the full recovered dispatch chain. Direct events visit receivers before
object or spawned-script delivery. Broadcasts use a single-recipient fast path or
snapshot recipients with intrusive references, allowing earlier callbacks to
remove later recipients safely. Spatial listeners use strict squared-distance
comparison against the captured source position; negative or NaN radii disable
the radius restriction. Event waits wake both active and saved script frames.

Handler tables merge event parameters over stored parameters, then execute an
immediate call, spawn an owner-bound script, or replace the active script after
its interruption handler. Reentrant delivery preserves stop state; destroying a
script during delivery marks its table dead until its final active call returns.
Logging retains lazy readable-name loading, duplicate checksum buckets, ring wrap,
depth arithmetic and consecutive phase coalescing. This specimen's log printer
only prints headers. Owned event parameters use the recovered two-pool release
routine. Integrated executor checks keep value pools disabled; standalone release
checks cover both pools. Runtime startup and event registration remain unfinished.

The 1,506 cases / 1,954 calls compare complete memory and global state, including
778 configured event/command callbacks and six actual recipient-deletion chains.
They cover nested manager/table delivery, receiver mutation of the target or next
link, duplicate broadcast recipients, strict radius boundaries, missing waiter
serials and handler/table retirement. All finite squared-distance results match
exactly; 15 returned arithmetic NaNs compare by classification. Native and object
virtual handlers remain explicit test boundaries, not recovered gameplay behavior.
These checks establish event delivery, not a playable training level.

The wall-rebound path (`004ff670`) now uses the complete event dispatcher. It
checks the input at offset `0x1a0`, two cooldown timestamps and a strict impact-
angle condition before emitting event `0x4c03635b`. The state is reread afterward:
a handler can request cancellation, replace the active body/state or change
physics data before reflection. Cancellation clears its flag and records its own
timestamp without rebuilding orientation.

Successful rebound reflects velocity across the contact normal, applies the
configured reduction/minimum-speed choice, projects onto the target-up plane,
rebuilds the forward/side axes, copies the resulting matrix and saves the rebound
time. Near-zero or unordered speed uses the original opposite-forward fallback.
The scalar maximum selects its second operand on equality or unordered input,
which matters for NaNs and signed zeros. Vector copy/add/subtract retain sequential
partial-overlap behavior; scaled-copy and cross-product snapshot their inputs.

The 7,393 cases / 8,225 calls include 1,937 complete rebound calls, 812 successful
responses, 127 sampled training collision normals and 991 event/command callbacks.
Three cases redirect the event to an actual cached QB handler whose native command
requests cancellation. Timers, parameter getters, event delivery and script execution
run their recovered implementations. Full memory/global state and finite outputs
match; 1,368 arithmetic NaN outputs/returns compare by classification. Impact-angle
parameters cover finite values and NaNs; infinite-angle FSIN behavior has the
previously documented adapter/oracle difference and is outside these full-branch
comparisons. No physical x87 transcendental-accuracy claim is made. The enclosing
wall response, sound chain and movement sweep (`00506e50`) are covered below.

The material/impact sound-selection prerequisites are now recovered in
`src/audio/sound.c`. Material and event searches preserve the shared table
iterator. Missing material properties fall back to the default structure. Impact
bands select the first entry whose limit is at least the impact value, or whose
limit is absent; equality selects, while unordered comparisons advance. Weighted
selection traverses backwards and preserves the original wrapping integer
arithmetic and PRNG state. Direct structure choices bypass randomness, while
empty weighted arrays still advance it.

Descriptor construction retains defaults, untouched path bytes and optional
parameter precedence. It hashes the basename after the last slash or backslash.
The CRC thunk is an alias of the existing checksum function and is not counted
again. Text access prefers normal strings over localized strings. The newly
recovered name-or-flag lookup returns the first match, unlike the earlier
last-matching named-component lookup.

Volume initialization, scaling and silence checks preserve the original channel
format rules, including format 3 never reporting silence. Loaded sound lookup
checks the first asset array before the second, with signed counts and first-match
precedence. Missing assets return distance zero; a loaded zero distance and
disabled audio use the configured default.

The 2,336 cases / 8,874 calls compare the full 64-KiB fixture arena, return values,
table and random state, configuration globals and populated asset records. All
original callees execute without configured callbacks or allocations. Raw
descriptor values remain bit-exact; 757 arithmetic NaN outputs/returns compare
by classification. Caller contracts include registered event IDs, acyclic script
graphs, required arrays and weights, bounded asset counts and filenames fitting
the original buffer. Audio initialization, asset loading and the browser audio
backend remain separate work. The parent impact dispatcher is recovered below.
These prerequisites alone do not complete wall response or make the training playable.

Positional sound (`0047be10`) now runs its complete recovered call chain. It
selects the nearest camera through the active viewport mapping when the caller
does not supply one, computes distance attenuation with one of four curves, and
updates stereo volumes plus the source position and range. Disabled audio leaves
the output untouched. Other early exits clear channel values but preserve the
remaining fields. The optional alternate range origin and the outer range margin
retain their original arithmetic and comparison behavior.

Nearest-camera selection (`004a09e0`) supports the six original viewport modes,
sparse mappings and null camera slots. Equal-distance ties retain the first
camera; the optional distance output is untouched when none exists. Its squared
distance accumulation differs from the spatial routine and standalone vector
distance helper, so their operation orders and float spills remain separate.
Camera field accessors are recovered, but camera creation and frame updates are
not completed by this work.

The positional checks cover 2,873 cases / 3,197 calls, including 1,407 full
calculations with real original callees and no callbacks or allocations. Full
fixture memory, globals, return values and untouched bytes compare exactly,
except 322 arithmetic NaN outputs/returns checked by classification. Cases include
all viewport modes, range boundaries, arbitrary orientation axes, overlapping
input/output, signed zeros and wide/nonfinite arithmetic. The routine sets format
3 before panning; its later format-1 subbranch is unreachable in these synchronous
calls. Playback (`0047bd20`) is now recovered through the device boundary, as
described below. The parent impact dispatcher is recovered too; complete wall
response is still pending.

Playback preparation now has recovered sound-slot and voice-ID handling. Slot
selection (`0047c720`) first reuses an inactive slot caching the same asset,
otherwise keeps the last inactive slot in its circular scan. When all slots are
active, it uses the slot after the prior cursor. The unsigned cursor wraps before
the remainder operation. Slot activity requires both the flag and a buffer.

Voice-ID availability examines only the first matching voice record. Pending IDs
remain reserved even when audio is disabled and can reserve zero. Available-ID
search increments with 32-bit wrap and does not reserve its result. Parameter
initialization preserves the original partial writes, including fields left
untouched on the default path. Asset settings first halve channel volumes, then
apply the asset's volume and pitch percentages. Direct viewport-camera lookup
retains mapping holes rather than skipping them.

The 1,957 cases / 6,142 calls cover every initialized slot count from 1 through
48, cursor wrap, cached matches, all-busy fallback, duplicate voices, pending IDs,
parameter overlaps, untouched bytes, and volume/pitch settings. Original callees
execute without device callbacks or allocations. Full fixture memory, tracked
voice IDs/device-slot records/configuration/cursor globals and return values are
compared. Derived/arithmetic NaNs account for 817 classification comparisons.

Five alias cases propagate a signaling NaN from an x87-written floating field
into the final raw flags word. These require the exact quieted payload, correcting
the already documented Unicorn FLD/FSTP difference; arbitrary flags do not get a
NaN-class exception. Original and required words are retained in
`local/validation/sound-voices.json` under
`propagated_signaling_nan_corrections`.

Device-buffer playback (`0047d130`), its settings update (`0047cd70`) and the game
playback parent (`0047bd20`) now run their recovered call chains. Buffer creation
preserves the original release order, cached-sample reuse, split lock/copy/unlock
and seek/play sequence. A failed lock still caches the sample and proceeds to
playback. A failed play still marks the slot active and increments the attempt
counter. The parent then assigns the voice name, available ID, asset and parameters
only when playback succeeds.

Settings retain separate stereo and positional branches. Stereo applies the
original logarithmic volume/pan and conditional frequency updates. Positional
settings choose and orient the listener, rotate the relative position when the
nearest camera differs from the primary one, set source distances/position, and
commit deferred changes without adjusting frequency. Buffer/global state is
reread at the original points after device callbacks. The two supporting vector
functions retain the original x87 arithmetic order and float stores. The SDK
logarithm wrapper is a platform adapter, not an additional recovered function.

The 1,255 cases compare full fixture memory, tracked globals, return values and
3,226 instrumented OS device calls, including callback mutations and failed
creation/query/lock/play. The 175 arithmetic NaN results compare by classification.
Windows TLS and last-error services are instrumented for the real CRT calls.
These tests do not implement the browser audio backend or load audio assets.

Logarithm comparisons cover positive arguments, including positive infinity.
[Unicorn 2.1.4's FYL2X helper](https://github.com/unicorn-engine/unicorn/blob/2.1.4/qemu/target/i386/fpu_helper.c)
does not pop its operand stack for zero, negative or NaN arguments. A traced
stereo case with channels `(0.00001, -0)` and master volume `1` consequently uses
the leftover `log10(2)` as the next operand and sends volume `-9042`. Those
logarithm-domain cases are excluded from differential equivalence; the port uses
normal logarithm behavior, consistent with the instruction's stack operation in
[Intel's instruction reference](https://cdrdv2-public.intel.com/868140/253666-089-sdm-vol-2a.pdf).
Nonfinite master/pitch values and silent nonpositive/NaN channels remain covered.
As with the existing trigonometry adapters, these comparisons do not establish
physical x87 transcendental accuracy. Rotation covers finite and NaN angles;
the previously documented infinite-angle emulator difference remains excluded.

The complete impact dispatcher (`00444bb0`) now connects material/event selection
to playback. Missing material properties use the existing default-material
fallback; a missing event uses the separate default-impact structure. Clip
selection and descriptor creation precede the optional network notification.
That notification is queued before distance attenuation or local audibility is
checked, without an additional network-active gate in this function. Volume and
pitch follow their descriptor endpoint remapping, preserving each x87 operation
and the final float store. Positional calculation's return value is ignored, as
in the original. The component wrapper (`00518dd0`) converts intensity to a
percentage, applies its volume scale, resolves the event ID, and enters the full
dispatcher with notification enabled.

The 555 cases / 590 calls use actual original selection, attenuation, playback,
voice and queue code. They cover direct/weighted/threshold choices, both fallback
levels, missing data, remapping, range rejection, suppressed audio, device
failures, peer eligibility, unloaded assets, low-byte flags, coordinate/intensity
truncation and sequential calls retaining state. Full memory, tracked globals,
3,128 OS audio calls, 838 allocations, 40 releases, 572 scope events and actual
queued payload bytes compare. There are no NaN-classification exceptions in these
final observed outputs. Internal contracts include registered events, required
fallback definitions, initialized camera/device/queue state and successful
allocations. Invalid logarithm-domain and physical x87 accuracy limits remain as
described above.

One explicit packet difference remains: the original copies an unwritten twelfth
stack byte after eleven defined payload bytes. The port writes zero to that tail
byte; the oracle seeds exactly the corresponding original stack byte to zero
before entry. No defined payload bytes or queue outputs are masked. This queues
the notification through recovered code; socket transport is separate work.
The complete wall response (`005059d0`) now connects these paths in
`src/game/wall.c`. A successful rebound returns immediately. Otherwise the routine
turns along the wall, reduces velocity according to impact angle, and selects one
of two events using the raw state byte and angle sign. Above the speed threshold,
it invokes either stat-scaled impact audio or a synchronous special-mode script.
Events may replace the current body or state, so later reads follow the original
instruction order. The body used for parameter lookup remains the one captured
before event delivery.

Position correction feeds the original second surface probe, including its
static and moving training geometry paths. A hit with the parameter flag enabled
rotates the velocity and orientation, updates the cached orientation, and halves
velocity. The final event threshold compares the original displacement length,
not the earlier speed; the generated pseudocode obscures this distinction. The
port retains separate float spills and the two successive height-offset additions
when constructing the probe segment.

The 559 complete comparisons include 555 second probes, 257 hits, 105 turn
reversals, 43 final displacement events, four rebound returns, aliasing normals,
raw state bytes, exact integer parameters, wide exponents and event mutations.
The real event, parameter, QB executor, sound, queue and collision callees run;
178 native/object event observations, 614 OS audio observations, 183 allocations,
six releases and 122 scope events compare along with the complete arena and
tracked globals. Exactly typed arithmetic NaNs compare by classification (600
fields); other bytes compare exactly after explicit pointer relocation. The
original twelve-byte collision query global maps to the port's explicit context
argument at the outer function boundary. The audio packet-padding and numeric
limits documented above also apply. Native gameplay handlers, OS interfaces and
heap services remain instrumented boundaries. Full movement, runtime startup,
rendering and browser audio are still needed for a playable training level.

The complete movement sweep (`00506e50`) now invokes the recovered collision,
collision-event and wall-response paths. It returns immediately only when all
four current and previous position lanes compare equal. Otherwise it constructs
the height-offset, extended segment and queries actual training geometry. On a
skateable surface, the orientation test rejects only an ordered dot magnitude
below 0.01; unordered values also take the position-correction branch. This
instruction-level distinction corrected an error in the generated pseudocode.

Other contacts dispatch the original event `(9, 0, 0)` and reread the suppression
gate before wall response. The wall normal stays snapshotted across event delivery,
even when a script changes the probe, replaces the body/state or redirects the
gate pointer. The query-global mapping occurs only at the outer sweep entry so
the nested wall probe receives the first query's state.

All 748 cases compare the complete memory arena and tracked globals: nine early
returns, 620 first hits, 119 misses, 108 skateable corrections, 512 event deliveries
and 429 wall responses. The latter include 146 second hits, 68 reversals and 68
displacement-gated events. Real cached QB handlers execute in 70 cases, including
six local node-provider paths on moving instances of event-marked training meshes.
There are 368 event/command/provider and 330 OS audio observations; 74 typed
arithmetic NaN fields compare by classification. Native methods and OS/heap
services remain instrumentation boundaries, with the previously documented
packet-padding and numeric limits. The complete ground and air updates are
covered by later batches below; these comparisons do not establish a playable level.

Moving-contact transport is now recovered in `src/game/moving_contact.c`.
Construction attaches an intrusive owner reference and snapshots its orientation
and position. Updates compute all four translation lanes. When any orientation
lane differs, they also calculate the relative rotation and the displacement of
the supplied point around the saved owner position. The original first checks
all sixteen matrix lanes using ordered equality, including signed zeros and NaNs.
The supporting rigid inverse and homogeneous transform preserve their distinct
arithmetic order, wider intermediates and overlapping input/output behavior.

Contact acquisition consumes the collision probe's owner reference. A matching
live contact is reused; a changed or dead owner releases the old contact before
allocating the new one. A static contact releases an existing moving contact.
The skater wrapper subtracts the moving owner's four-lane velocity only when a
new attachment is reported, and honors the state byte that suppresses acquisition.
Release detaches the reference before the allocator observes it, then clears the
component pointer and records time. The validity query also disposes dead-owner
contacts. Saved-probe assignment (`0043a930`) retains the original result padding
and reference-list behavior; self-assignment detaches its own moving reference.

The 1,360 cases / 2,512 calls cover 512 live and 32 missing-owner updates,
192 rotation transports, 72 allocations, 328 releases, 24 enclosing velocity
adjustments and 192 saved-probe assignments. Full arena bytes, tracked timer
globals, allocation payloads and release ordering compare. Exactly 738 arithmetic
NaN fields compare by classification. Three signaling-NaN words on the floating
side of inverse-matrix swaps receive the previously documented exact x87 quiet-bit
correction; raw copies remain exact. Allocation succeeds in these checks, the
recovered SSE matrix backend is selected, and the frame-counter producer remains
outside scope. These routines are ready for integration into the remaining
grounded movement and floor/contact updates; those complete parents and the
playable training level remain unfinished.

Orientation blending (`004fea50`) now follows the original target/previous-vector
comparison, global blend-rate lookup, timestep decrement and normalization. The
decrement comparison uses the wide x87 value even when its stored float has
underflowed. Interpolation (`0043d990`) preserves the original per-lane spill
differences and snapshots results before writing overlapping output. When the up
vector changes, the cached basis is repaired and its side/forward rows are then
copied from the body in the original order. This does not rotate the body itself.
The 1,547 cases include 1,312 complete blend calls, 960 cache repairs, 410 clamps,
488 interpolations and 62 equal-target short circuits. Only the listed arithmetic
NaN fields compare by classification; raw copied rows stay exact.

State mode/material setters (`00519660`, `005196a0`) store their changed value
before delivering the original event, preserving mutations made during delivery.
The material entry explicitly truncates its argument to one byte at the wasm
boundary. Equal values produce no event or owner read. Object broadcasts
(`00460a20`) capture the owner's source ID, use a wildcard target and negative
radius, and consume but ignore their third original argument. The 164 cases
include repeated setters, receiver redirection into real QB handlers, absent and
empty listener lists, single-listener delivery, reference-protected snapshots and
callback mutations. Native gameplay methods and successful heap allocation remain
instrumented boundaries. These six recovered functions are prerequisites for
floor handling; the complete floor/ground parents and playable level remain open.

Floor-transition preparation (`004feba0`) is now recovered as a complete routine.
It snapshots the previous position and target orientation, tests the horizontal
direction against the original `0.001` threshold, preserves speed while projecting
velocity, updates orientation, offsets position and timestamps changed flags. Its
tracking helper (`004fc4a0`) retains the actual QB enable flag and exact format and
promoted-double arguments. The output callback can change the body or state before
the transition rereads them. The parent always supplies horizontal up, so the
actual orientation callee never enters its upward collision probe on this path.

The 720 cases include 923 transition calls, 708 preparations, 142 horizontal
rejections, 73 disabled-surface paths, 481 basis repairs and 125 diagnostic calls.
Repeated updates retain arithmetic-derived NaN classifications through subsequent
snapshots; raw copies remain exact. Unicorn's signaling-NaN promotion requires six
explicit double quiet-bit corrections, plus two float corrections for the saved
forward Y negation. Every other bit of those values is checked. The full floor handler is now recovered as described below. Grounded/airborne
updates, game startup and playable-level integration remain incomplete.

Ground steering (`00503560`) preserves input priority, the signed elapsed-time
ramp below speed 10, wide parameter arithmetic, velocity rotation and separate
body/cached matrix multiplication. Backward-motion response (`004ff920`) follows
the original speed and direction gates, six manual-name CRC branches, ordered
four-lane basis negations and synchronous script calls. Its parameter square
handles exact 32-bit integer inputs without double rounding: two tested boundary
values would choose the wrong branch with an ordinary double multiplication.
Input release (`004ffb10`) computes elapsed time, clears and timestamps the state,
clears the button's pending word (`0046b7f0`), then delivers the original event.
Mutations made by event or command callbacks are retained.

The 756 cases cover 1,268 calls, including sequential updates, signed timer wrap,
overlapping matrices, training directions, native and cached QB dispatch, 256
callbacks, 470 allocations and 470 releases. Full arena/global bytes and callback
order compare. Only 230 listed arithmetic NaN fields compare by classification;
eight raw negation words receive the documented exact x87 quiet-bit correction.
Native gameplay commands remain instrumented boundaries, and physical x87
transcendental accuracy is not claimed. Complete grounded/floor updates and
playable integration still remain.

Moving attachment update (`00501db0`) now runs its complete point-selection and
movement paths. Four input latches determine search direction in the original
order. The nearest/indexed lookup routines (`0051ba70`, `0051bc70`) traverse
the real linked point list, transform points by the moving owner's matrix and
project them onto its plane. The concrete provider method (`005480f0`) runs
through the original virtual slot. No point or collision result is substituted.

Selection events can redirect the current skater body, change the selected index
or remove the contact. Movement retains the originally captured owner, follows
the current contact displacement, approaches or snaps to the target, and copies
the owner's cached orientation. Excessive distance and missing contacts emit the
original events. The 963 cases include 429 side-search iterations, 18 changed
indices, 113 incremental moves, 24 arrivals, 234 direct placements and 52 distance
rejections, with 78 event/command callbacks and three real QB handler executions.

The indexed helper returns success without writing output when an index is
missing; this behavior is verified explicitly. Enclosing movement checks require
a valid selected point whenever geometry executes because otherwise the original
reads an unwritten stack local. Full arena/global bytes and callback effects
compare; only 441 arithmetic-derived NaN fields use classification. The concrete
provider is recovered, while native gameplay commands and successful allocation
remain instrumented boundaries. Full ground/floor updates and playable-level
integration remain unfinished.


The objective-state prerequisites now use the recovered QB getters and CRC
routines. Cached list access preserves forward traversal, backward resets and
output writes that alias the cache or list. Key lookup clears the cache first;
availability reads the original level/grid fields. State and event parameter
access retain the executable's initialized or reused output when a field is
missing. The local-skater lookup preserves the original sentinel-list contract.

All 716 cases and 1,052 calls compare byte for byte against original instructions
in both Node and Chromium, without native callbacks or allocation substitution.
Indexed list access, required arrays and sentinel lists retain the original
valid-memory preconditions. These functions support the objective actions below;
notification delivery still needs recovery before the enclosing
state/floor/ground updates can be completed. The level is not playable yet.

Objective state construction (`005566d0`) now rebuilds flat flag lists and
named groups using the recovered script ownership routines. It clears the old
state, preserves duplicate-name replacement order, initializes group counts and
writes the target count back to the objective's parameters. The newly recovered
owned structure-copy setter (`00478670`) copies before replacing an existing
member, including when that member owns the source being copied.

The original completion predicate (`00554110`), timer reset, concrete activity/
initialization/selection/beaten methods, parent-ID traversal, descending-priority
insertion and first-player lookup are also recovered. Checks include every flag
byte, signed thresholds/counts/priorities, timer overflow, grouped early exits,
repeated initialization and source payload aliasing. The 843 cases cover 2,216
calls, 453 allocations, 401 releases and eight temporary-scope events, all
verified in Node and Chromium. Every
arena/global byte, heap event and return matches the original instructions;
there are no native gameplay callbacks or floating-point comparison exceptions.
The original required group fields, valid parent/sentinel links and successful
allocation contracts remain. Full activation now includes its text, score and
script effects below; the state-change parents remain unfinished.

The complete objective text update (`00556a00`) now resolves real profile
bindings, builds key/trick text arrays (`00555b50`) and expands the original
one- or two-digit markers (`00554890`). Integer bindings use the local skater;
checksum bindings use the global trick definitions, and unmapped entries search
the profile's special-binding array. Failed searches retain partial outputs and
the parent releases its temporary arrays through the recovered ownership code.

The update saves original fields once and preserves the executable's differences
between scalar and array main text: the scalar branch computes a formatted buffer
but stores the original input again; the array branch stores the formatted strings.
The formatter ignores its capacity argument and advances by replacement-format
length. Its argument-free `sprintf` calls permit literal text and `%%`; formats
requiring missing arguments have undefined original behavior and are outside the
contract. Callers provide valid marker indices and enough buffer space, including
the parent's 512-byte local buffer. The original CRT formatter runs in the oracle.

All 269 cases / 428 calls compare returns, complete arena/global state and heap
events. They include 93 full parent calls, 24 failed binding resolutions, repeat
updates, saved-field precedence, copied arrays and source payload aliases. Only
the original binding record's three uninitialized padding bytes are explicitly
zeroed (120 bytes over 40 returned records); both checksums and the flag compare
exactly. Required profile/string fields and successful allocation retain their
original contracts. Activation, state changes and playable integration
remain unfinished.

The full objective initialization routine (`00557270`) now joins difficulty
selection and parameter merging to the recovered state builder, synchronous
script executor and text updater. It preserves existing state when no difficulty
array is supplied, runs scripts before the final flag writes, retains the untimed
bit for zero/missing values, and still completes after a failed text update.

The 198 cases / 426 calls include 396 full initializations and the original parser
reading all 30 literal goal-flag arrays from the hash-verified archived training
scripts. Tests also cover repeated initialization, grouped/flat state, invalid
and default difficulty values, inline arrays, nested script calls and aliases.
Original x86 and Node/Wasm compare every arena/global byte and heap event:
4,324 allocations, 3,991 releases and 2,012 scope events. No native gameplay
callbacks are substituted. The full Chromium regression also passes for this new parent.
Goal activation, scoring, the movement update and rendering still need integration.

Complete goal deactivation (`00557560`) and recursive uninitialization
(`00554bd0`) now execute through the actual recovered base/event virtual methods.
They reset descendants (`00553e50`), clear state (`00554030`/`00554070`), run the
original synchronous scripts, remove owned parameters, optionally reinitialize
the root goal, and unlink the active queue node in the executable's order.

The 231 cases / 605 calls include 30 complete lifecycles using the original
archived training flag arrays. Actual dependencies execute 317 deactivations,
519 uninitializations, 911 synchronous script calls and 66 initializations.
Every arena/global byte, return and heap event compares against original x86:
9,925 allocations, 9,743 releases and 1,968 scope events. Node/Wasm and the full Chromium regression pass.

The supplied executable has a nonterminating reset case: a current member named
`num_flags` skips both zeroing and advancement. The recovered code preserves it.
Bounded original execution confirms repeated visits to that same member, while
isolated Wasm workers first pass normal reset controls and then fail to return
from the reserved-member case within 500 ms before termination. These observations
are kept outside the browser main thread. Flat training states store `num_flags`
in their parameters and complete their resets. This is faithful recovery of the
supplied specimen, not a repair of its grouped-state loop. Activation, score/UI,
movement and rendering integration remain unfinished.

Fourteen prerequisites for score reset now execute as recovered C. They find the
skater and screen, release owned trick entries and indexed records, reset combo
history, read the special-meter colors/rate, and dispatch the score event only
when the corresponding spawned script exists. UI helpers resolve fonts and
linked widget references, propagate inherited visibility, and change the event
flag while executing the original event dispatcher. Character decoding accepts
one base-32 digit; it is not a general integer parser.

The 670 cases / 1,138 calls compare complete memory, returns, globals and heap
ordering against the original instructions. Coverage includes all 256 character
bytes, aliased map keys, duplicate IDs, null payloads, negative counts, ancestor
visibility, repeated flag changes, and actual cached QB event handlers. There
are 156 allocations, 239 releases, 70 event deliveries and 39 executed QB handlers,
with no substituted native gameplay callbacks. Twelve NaN results are checked
by classification only at the special-rate float. Node/Wasm and the complete
Chromium regression pass. These prerequisites now support the complete score-reset
parent and goal activation described below.

Font measurement and both concrete dispatch wrappers now interpret ordinary,
special and button glyphs. Button labels execute the actual menu/reference and
key-binding logic. The legacy wide-character converter retains its locale,
truncation, partial-write and error paths; the host supplies the current locale
and the Windows keyboard/code-page services. Test implementations of those OS
services are instrumentation, not a browser input implementation.

The complete text setter now reuses or reallocates its owned buffer, rewrites
escaped spaces and button aliases, measures through the real font virtual method,
and updates widget size unless fixed dimensions are enabled. It retains two
escaped backslashes for the font parser. Reuse compares string lengths, so a
previously shortened string can cause reallocation even when the old allocation
was large enough. Size and scale updates preserve the different multiplication
orders and x87's 24-bit arithmetic precision with extended intermediate exponents.
The integer formatter also preserves the original doubled minus sign for INT_MIN.

The 3,155 cases / 6,341 calls compare every arena/global byte, return, heap/scope
event and explicit OS call trace. They cover all character bytes, key/menu modes,
conversion failures, wrapped widths, aliased output stores, in-place text edits,
signed zeros, extreme floats and repeated updates. There are 1,406 arithmetic NaN
comparisons restricted to typed position/relative-scale results; copied fields
remain exact. Original x86, Node/Wasm and the full Chromium regression pass.
Renderer and playable integration remain unfinished.

The complete multiline word wrapper now uses the original font lookup, tokenizer
and measurement routines. It retains deferred newlines, the 95-byte row limit,
trailing-space removal and ring-buffer reuse. Width calculations preserve x87
rounding and the intermediate float store. As in the original, wrapping an empty
row reads its preceding byte; the caller must provide valid backing storage.

Text drawing objects now retain the original sorted-list behavior, including
equal depths and unordered float comparisons, visibility changes and priority
updates. Both drawing constructors, the concrete style's three virtual updates,
style-pool creation/acquisition and widget style-array allocation are recovered.
Widget allocation uses the UI heap and assigns the ancestor's owner value only
to the first style in each array. Parent traversal retains intrusive reference
lifetimes. The 17-word layout-state copy preserves forward overlapping copies.

The 1,119 cases / 4,731 calls compare complete arena/global bytes, returns and
heap/scope events against the original instructions. Only 32 arithmetic NaN
results in accumulated row width use classification; copied fields and padding
remain exact. Original x86, Node/Wasm and the complete Chromium regression pass.
Drawable rendering/destruction and two concrete style virtual slots are still
unavailable. These drawing helpers do not render UI.

Base object, UI and text-widget constructors now preserve every untouched field,
including uninitialized words copied into both layout states. Lazy parameters use
the selected structure pool; an exhausted selected pool does not fall back to the
generic heap. The text constructor acquires its primary style before creating
its type parameter, retaining the original allocation order.

Complete parent changes now remove a child from its old sibling list, append it
to its new parent's tail and propagate owner and depth values through descendants.
Fixed-depth widgets still pass the incoming depth to their children. Both reference
assignment forms preserve the original aliasing behavior: assigning a reference
to itself clears it because its old target is removed before the source is read.

Drawing-style cleanup now releases owned storage, hides the drawable through its
real virtual method and returns the style to the pool. Widget cleanup handles
both style arrays and retains the original dangling primary-array pointer after
release. Tests also construct, release and reacquire styles to check reuse.

The 624 cases / 1,392 calls compare complete arena/global bytes, returns and
allocation/scope events. Only 62 arithmetic NaNs in descendant depth values use
classification; copied fields, constructor padding and retained pointers compare
exactly. No gameplay callbacks are substituted in this batch. Original x86,
Node/Wasm and the full Chromium regression pass.

The global object registry and local object manager now provide complete ID
assignment, alias removal, registration, renaming and priority changes. Automatic
IDs preserve signed decimal formatting, counter wrap and collision retries. The
local queue uses the original reverse traversal and equal-priority ordering.
Renaming retargets all matching event waits. Registration and removal record
lifecycle log entries; they do not dispatch script events.

Complete base-object, UI and text-widget destruction now runs parameter cleanup,
the concrete manager removal method, script destruction, owner stopping and both
reference-target destructors. The object's own deferred script calls are cancelled
before destruction, while other owned scripts retain their deferred behavior.
Text destruction preserves the optional object's unusual release–reacquire–release
style sequence. The UI destructor detaches parent links and clears references;
recursive child deletion remains the derived manager's separate responsibility.

The 429 cases / 998 calls compare every arena/global byte, return and heap/scope
record exactly, with no numeric masks or substituted gameplay callbacks. They
include full registered text-widget lifetimes, both script pools, up to 16 saved
call frames, six real deferred QB executions, log initialization/ring wrap and
all 40 event-wait slots. Original x86, Node/Wasm and the full Chromium regression
pass.

The derived UI manager now constructs and tears down its real event receiver,
subscription lists and focus references. Registration, attachment and removal
preserve original intrusive-reference order, the reverse search for a replacement
root, and the cross-controller tail retention observed in the executable.
Recursive deletion removes descendants, optionally retains the selected widget,
and detaches a requesting script's current and saved owner pointers.

Actual UI event receipt handles subscribe/unsubscribe and subtree disable/enable,
loads the pad-event array, filters input devices, and forwards controller events
using unsigned focus priorities and inherited owner/disable flags. Forwarded
events can remove subscriptions; the original dirty-list restart and handled
bits are preserved. The object's real event method invokes the QB runtime and
protects its lifetime with a temporary reference. The original two-argument
virtual ABI uses a scoped platform-service binding, restored after nested calls.

The 349 cases / 7,654 calls compare every arena/global byte, return and heap/scope
record exactly. They include real receiver mutation/restart, all 48 subscription
slots occupied, both controllers, poisoned constructors, full widget-tree deletion,
unsigned focus boundaries and four actual cached QB handlers. The service binding
is checked after every call. No gameplay callback substitutions or numeric masks
are used. Original x86, Node/Wasm and the full Chromium regression pass. Rendering
and playable training integration remain unfinished.


Complete multiline text rebuilding now disables widget events, removes existing
children through the real manager, wraps text into the original thirty-row
buffer, and constructs replacement text widgets. It retains the fixed-height
ring order, automatic-height second wrapping pass, integer line-height division,
font and scale propagation, and event re-enabling order. Constructors preserve
untouched fields; destruction releases optional storage and the base widget.

The complete combo-text caller finds the player's screen widget, builds its list
of trick strings, rebuilds the multiline widget and runs the original cached QB
notification. Clearing uses the low byte of its flag, and a missing widget skips
the update. This recovers text state; drawing those widgets is still unfinished.

The 211 cases / 2,706 calls compare every arena/global byte, return and heap/scope
record exactly. They exercise old child subtrees, real event subscriptions and
QB handlers, all thirty text rows, up to 250 trick pointers, repeated updates,
fractional scale/spacing, signed counts and full construction-to-deletion paths.
The original internal bounds still apply: at most thirty visible rows, words no
longer than 95 bytes, valid fonts/style pools, successful allocations, and nonzero
integer line height when automatic resizing divides. No gameplay callbacks or
numeric comparison masks are substituted. Original x86, Node/Wasm and the full
Chromium regression pass. Movement, startup, rendering and playable training
integration remain unfinished.


Numeric score display now finds the player's screen widget, releases the temporary
reference, formats the score/multiplier, replaces the real text buffer and runs
the cached notification script. Its Windows CRT boundary uses bounded C-locale
adapters for signed integers and one-decimal f32 values. These preserve the old
seventeen-significant-digit intermediate, rounding away from zero at decimal
halves, negative values that round to zero, and the original nonfinite text
`1.$`. The adapters are not counted as recovered general-purpose CRT functions.

Full score reset now clears both history arrays, releases owned trick entries
and map records, clears local combo/score widgets, selects the mode's initial
score, clears and broadcasts special state, restores special-meter settings and
resets the local score component through its guarded script-event path. The
null-game early return and diagnostic callback's position before clearing remain.

The 426 cases / 3,196 calls compare complete memory, globals, returns and
allocation/scope records exactly, with 153 instrumented diagnostic callbacks and
no substituted gameplay callbacks or numeric masks. They cover every float
exponent, both signs, decimal boundaries, all eight text-language settings,
integer limits, repeated resets, missing players, both initial-score branches
and four guarded score events through real QB execution. Explicit assertions
confirm the mode and event branches execute. Original x86, Node/Wasm and the full
Chromium regression pass. The complete goal activation that uses these routines
is described below; startup, movement, rendering and browser input/audio
integration remain unfinished.

Complete objective activation (`00557360`) now resets scores for visible players,
walks the parent chain, inherits or resets the timer, uninitializes the root when
needed, initializes the goal, runs its activation script and inserts it into the
manager's active queue. It retains the original manager and network pointers
across script and diagnostic calls. Timer inheritance preserves signed conversion,
the original single-precision multiplier and wrapping millisecond arithmetic.
Flag cleanup removes matching unnamed values while retaining named parameters
with that same checksum, including their owned payloads.

The 235 cases / 2,186 calls compare full memory, globals, returns and allocation/
scope records against the original instructions. Tests cover already-active
returns, parent chains, real network states, hidden players, counter/timer wrap,
actual score/UI resets, difficulty/text initialization and cached QB scripts.
All 30 hash-verified archived training flag arrays run through parsing,
activation, deactivation and reactivation. There are 11,411 allocations, 4,512
releases and 3,354 scope records including setup and callees. The only
instrumented callbacks are 163 diagnostic prints; there are no gameplay
substitutions or numeric masks. Valid parent/player/component/widget graphs,
terminating scripts and successful allocation remain original preconditions.
The manager/script entry points below now invoke this activation. Other derived
objective types, update chains and playable integration remain unfinished.

The objective manager's activation entry (`00557fc0`) now performs the real
lookup and eligibility checks, calls the concrete activation virtual method and
updates its last selected goal only after successful activation of an eligible
root. The original native `GoalManager_ActivateGoal`, `GoalManager_DeactivateGoal`
and `GoalManager_ClearLastGoal` commands retain their two-argument script ABI.
Deactivation reports whether the goal exists, even if it was already inactive.
Missing goals preserve the original lookup/cache effects and return false.

These native functions execute through the actual script interpreter using
symbolic commands, relocated direct-call tokens, expression predicates,
synchronous native dispatch and temporary spawned instances. A small port
adapter scopes the existing memory/diagnostic service binding around native
calls and command parsing, then restores it after nesting. It is not counted as
recovered game code. Tests deliberately invalidate the ambient service record
and run nested goal handlers with full score/UI resets, proving that the caller's
services are supplied and restored. Only the diagnostic print boundary is
instrumented; the goal handlers and their gameplay callees execute real code.

All 169 cases / 1,208 calls compare complete arena/global/return/heap/scope state,
including 103 diagnostic callbacks, 6,603 allocations, 2,975 releases and 2,132
scope records. Coverage includes both missing-goal flag paths, unavailable and
already-active goals, current-level availability, parent/selection conditions,
captured-manager mutation and all 30 archived training flag arrays through actual
scripted start/stop/reactivation. Native binding registration for the full engine,
notification delivery, startup and playable-level integration remain unfinished.

Complete base/event goal completion (`005576d0`) now advances child goals or
finishes a leaf goal through the original score/time records, reward templates,
unlocks, handler scripts and beaten-state propagation. Parent marking walks all
parent links, including shared ancestors. Career points and classic completion
counters retain their original wrapping and aliased writes. Manager completion
(`00558030`) updates selection/counters and queues the real online notification;
the original `GoalManager_WinGoal` command reaches it through native QB dispatch.
The score getter includes its original owned-object counting path and the table
visitor's overflow-first order and callback mutation behavior.

The 529 cases / 1,399 calls compare complete memory, globals, return values and
allocation/scope records in Node and Chromium. They include repeated wins,
signed score and unsigned timer boundaries, selective unlocks, owned nested
reward copies, child activation with real score/UI reset, and native start/win
commands using all 30 hash-verified archived training flag arrays. There are
9,381 heap allocations, 6,204 releases, 2,252 scope records and 36 diagnostic
prints, including setup and actual callees. Gameplay effects are not replaced
with test callbacks, and this batch uses no numeric masks.

Selected-pool checks exposed older structure-allocation paths that still used
the generic heap. The recovered allocator (`00409030`) now serves script setup,
copying, parsing, expressions, event delivery and objective state/rewards;
structure disposal consistently uses the existing selected/alternate-pool
release routine. Tests cover both selected pools, exhaustion without fallback,
nested reward ownership and repeated completion. The host still supplies heap
initialization/services, and other value pools remain disabled. Required goal
parameters, valid acyclic graphs, terminating handlers and successful internal
allocations remain contracts.

The shared browser checker passes float inputs as integer words through a small
WebAssembly call adapter. This prevents JavaScript argument arrays from changing
NaN payloads before the recovered function receives them. The adapter reinterprets
bits and calls the actual engine export; copied fields still compare exactly and
no output masks were added. The existing 3,155-case font/UI comparison passes
with the same result. Remaining movement parents and playable browser integration
still need recovery.

Goal flags and the full skating-state change (`004fded0`) now execute their
original dependency chain. Native `GoalManager_SetGoalFlag` preserves its two
unnamed parameters with different types. Flat and grouped updates retain the
original counters, repeated-value behavior, reentrant scripts, automatic wins
and owned copies passed to progress scripts. Event objectives use the actual
local skater/component lookup and signed score/multiplier gate, activate through
real score/UI reset, and update the matched flag. Manager iteration retains its
initial signed count; notification insertion rereads the ring count after
callbacks, with duplicate suppression and unsigned wrap.

The full state-change parent preserves saved-position restoration, timestamp
updates, input-latch resets, per-state flags and notification-before-state-event
ordering. Both notification and mode-event callbacks run actual QB/native goal
commands. Tests check component pointers and counters changed during those
callbacks, including the final sound-state write. Its event owner is an actually
registered UI object in the fixture; this exercises real event dispatch but does
not establish original skater construction.

The 501 cases / 2,038 calls pass in Node and Chromium, with complete arena,
global, defined return and allocation/scope comparisons and no numeric masks.
All 57 flag entries from the 30 hash-verified archived training arrays run
through real parsing, activation and native flag updates to automatic completion.
The suite records 12,326 allocations, 3,578 releases, 1,778 scope events and 43
diagnostic prints, including setup and actual callees. Required typed parameters,
valid components and terminating object/script graphs remain original contracts.
These routines do not complete floor handling, the overall grounded update,
startup, rendering or a playable browser game.

The side-contact chain (`0050c930` -> `0050a2c0` -> `00508140`) is now
recovered through the complete skating-state change and its original dependencies.
It preserves input-history expiry and ring traversal, signed cooldowns, the rising
probe, slope/angle/speed gates, standing and airborne corrections, wall orientation,
contact scripts, state notifications and moving-contact release. The history lookup
can consume the same entry repeatedly; the original mask controls eligibility.
Vector division retains the distinct reciprocal precision used by its fourth lane.

The 504 cases / 1,583 calls pass in Node and Chromium. Tests include contacts
from 20 training-scene segments, both signs, a third opposing probe, 73 successful
wall transitions through the state parent, and real contact/event scripts invoking
native goal activation. Callback tests change the wall gate, active state and sound
component. The oracle records 1,419 allocations, 13 releases, 610 scope events and
11 diagnostic prints. Arena/global values compare exactly except for classification
of 105 arithmetic NaN output lanes. Generic base-object construction supplies the
fixture's event owner; this does not recover skater construction. The two outer
position-restore branches are implemented from the instructions but were not
reached by this batch's geometry cases. Balance, the complete movement update, startup and playable browser integration
remain unfinished; floor handling is now recovered as described below.

The transfer-candidate search (`00502240`) now uses recovered collision-cache
construction and registration, moving-object bounds, speed interpolation and the
complete original ballistic clearance test. The 349 cases / 551 calls pass in
Node and Chromium, including 222 parent calls and 66 successful searches. Cases
cover 20 original training segments, a real moving training mesh, both trajectory
segments, blocked-path height increments, failed-transfer velocity restoration,
speed/vertical limits, jump-apex prediction, signed and zero distances, aliased
caller vectors, timer wrap and registry duplicates/full masks.

The comparison checks all defined arena/global data, plus the temporary cache's
stack identity, inactive registration bit, bounds, counts and populated entries.
Unused cache entries and uninitialized stack storage are not compared. Only 44
typed arithmetic NaN lanes use classification; ordinary values and raw copies
remain exact. Candidate arrays must fit the original 500-entry cache. The result is now
consumed by the recovered `00502f20` application routine, described below.
The containing floor handler `00509bd0` is now recovered as described below.

The complete transfer application (`00502f20`) updates the transfer velocity,
timed flags, surface basis, orientation interpolation and moving-contact flag.
It spawns the original transfer script with its height parameter, frees that
parameter structure, then removes the attached input-release event and listeners.
The recovered matrix helpers preserve the original cofactor order, singular
matrix behavior, overlapping copies and near-pi axis selection.

The 407 cases / 761 calls pass in Node and Chromium. They include 44 complete
applications, nine complete search/application sequences on training geometry
(one moving mesh), and real QB/native goal activation. Two diagnostic callbacks
replace the body or state pointer to verify the parent's later field reads.
Constructor-derived event owners provide valid fixtures; full skater construction
remains unrecovered. Event tests include duplicate listeners, nested owned
parameters, signed counts, missing tables and disabled entries.

All defined fixture memory, globals, returns and allocation/release records are
compared. The 783 typed arithmetic NaN outputs compare by classification;
ordinary values and raw matrix copies remain exact. SDK atan2 models FPATAN,
without a claim about physical x87 transcendental accuracy. CRT errno is compared
as an explicit platform global. Required configuration/components, terminating
scripts, valid event storage and successful allocations are fixture contracts.
Balance, the complete movement update, startup and browser rendering/input/audio integration still
remain; the training level is not playable.

The complete floor handler (`00509bd0`) now executes surface classification,
projected-direction and contact-distance tests, material/state events, moving
contact adjustment, saved-contact assignment and departures into the existing
transfer path. Its dependencies include alternate contact search (`004fee10`),
alternate transfer application (`00505f70`) and input-gated transition exit
(`00507120`), plus quaternion rotation and orientation interpolation.

The 940 cases / 1,846 calls pass in Node and Chromium, with 113 full floor calls
on original training geometry and in clear space. Six alternate transfers reach
the full interpolation/script path (four plane and two opposed cases); eighteen
return the original blocked/deferred result. Six real QB/native goal callbacks
replace state, sound or the response gate during floor mode/material events.
The original signed input timing, per-flag timestamps and callback rereads remain.

Full arena memory, globals, returns and heap events compare. The 632 declared
arithmetic NaN outputs compare by classification; ordinary values and raw copies
remain exact. Direct contact scans check the automatic cache's defined fields;
nested scans check its retained stack identity and inactive registry bit without
dereferencing storage whose lifetime ended. SDK tan supplies the floor FPTAN
operation after clamped acos; physical x87 transcendental accuracy is not claimed.
Valid components, initialized prior contacts, required typed parameters, bounded
caches, terminating scripts and successful allocations remain fixture contracts.
The fixture initially exposed an uninitialized saved contact and was corrected.
Review also corrected the new floor handler to compare collision-instance pointers
at probe offset `0x54`, as the original does. Full skater construction, balance,
complete movement integration and browser startup/render/input/audio remain;
the original training level is still not playable.

Balance-score accumulation (`00564270`) now executes the original trailing-trick,
point and component gates, then recalculates the trick score and refreshes both
score widgets. Recalculation (`00562e40`) preserves wrapped integer products,
signed division, repetition/spin tables, chain grouping, the special-meter bounds
and callback read order. The special-state setter (`00562760`) retains the raw
low-byte comparison and original broadcast events. Three balance-display
prerequisites now handle integer/checksum attributes and position/target updates.

All 813 cases / 1,682 calls pass in Node and Chromium, including 63 complete
balance-score calls, 36 accepted updates, and twelve cases where real QB delivery
executes an instrumented native command that changes score or multiplier state.
Those native commands and formatted diagnostic capture are test boundaries,
not recovered gameplay commands. Full memory, globals, returns and heap events
compare; 222 declared arithmetic NaNs compare by classification, while raw
coordinate and target copies remain bit-exact. Valid nonnegative table indices,
bounded entries/texts, valid object graphs and successful allocations remain
internal contracts. The next batch below recovers balance-meter rotation/display;
balance physics, complete movement, startup and browser rendering/input/audio
integration remain unfinished.

The complete balance-display routine (`00563080`) and its normal/manual wrappers
now find the registered meter, dispatch the original show/hide QB scripts, update
attributes, interpolate the balance curve, position and rotate both sprites, and
write the concrete sprite drawing records. Twelve supporting routines recover
sprite style/drawable construction and allocation, UI sprite construction, data
transfer, visibility/depth ordering, virtual update order and rotation. A null
texture preserves its prior draw handle; flag 1 selects an indirect handle.
Constructors retain the original untouched bytes and allocation order.

All 555 cases / 2,162 calls pass against the original instructions, Node and
Chromium. The 963 complete display executions cover both orientations and curve
boundaries. Sixteen cases run real QB containing an instrumented native command
that changes live display state before later reads; these commands are test
boundaries, not recovered gameplay commands. Two cases construct the actual
sprites, register their IDs, link the child and execute the complete display.
Whole arena/global/heap/return observations compare, with 209 typed arithmetic
NaNs and their subsequent coordinate/log copies checked by classification. Raw
input data, colors and direct angle copies remain exact. Derived indices must
select two of the twenty curve points; valid distinct objects, terminating scripts,
successful allocations and initialized heap services remain internal contracts.
This writes sprite records; it does not render a playable game. Unrecovered
rendering/disposal virtual slots are explicitly unavailable and were not invoked.
Balance physics, animation dispatch, complete movement/startup and browser
rendering/input/audio integration remain unfinished.

Balance parameters (`004f90a0`, `005807f0`) now select the explicit or per-mode
structure and execute the existing full stat evaluator. Missing nested parameters
do not gain a global fallback. The timed-trick enable predicate (`0051c950`)
preserves availability, career, component, game and profile gates, including the
original receiver-seeded output when the profile checksum is missing. Completion
(`0051ce80`) builds owned string/integer parameters, runs the synchronous QB
notification, marks the record afterward and releases the parameters. The complete
balance scan (`0051d6a0`) checks all seventy records, compares signed integer
thresholds without prematurely rounding them to float, rechecks eligibility in
each nested completion and sends its final aggregate notification. The button
lookup (`0046c270`) retains its non-address priority and reads names beyond the
existing button prefix without shifting any previously named input fields.

All 498 cases / 1,118 calls pass against the original instructions, Node and
Chromium, including 245 complete scans, an all-seventy-completion sequence and
eight actual QB/native mutation cases. The 210 native callback observations
capture notification parameters and state before completion; these observers
are test boundaries, not recovered game commands. Mutations affect later records
or turn off nested completion while preserving the aggregate notification.
Whole arena/global/heap/return observations compare. Only 36 arithmetic NaN
returns use classification; other values and raw copies remain exact. Valid
full-sized input/player records, stat indices, terminating scripts and successful
allocations remain internal contracts. Three stored network/player getters and
the indexed profile wrapper complete this batch. The original balance physics
parent still needs animation dispatch; complete movement/startup and browser
rendering/input/audio integration remain unfinished.

The balance-animation controller (`004a49f0`, `004a4af0`) now constructs its
reader and implements all four commands: required animation setup, refresh,
normalized balance position and atomic optional-value updates. Timeline setup
retains endpoint ordering, the raw current-time copy and single-precision x87
arithmetic. Reader allocation uses either original fixed pools or the host heap;
selection preserves both asset lookups and re-reads the name between them.

Asset lookup uses the original hash-table traversal and concrete animation-asset
readiness/data methods. The original asynchronous completion callback (`00407710`)
sets state 2 when reading finishes; state 4 means ready. Completion pumping
(`005b68c0`) swaps the two buffers, executes their actual callbacks and decrements
pending counts. The blocking wait (`005b6a50`) retains diagnostic ordering and
can drain multiple batches. Its producer and the asset parser are not recovered:
deterministic diagnostic observers supply external completion/readiness changes
in the blocking tests. This does not claim a working file loader or animation
parser. A browser host must arrange completion before entering synchronous waits.

All 763 cases / 1,545 calls pass against the original instructions, Node and
Chromium. These exercise 434 controller commands, 340 timeline setups, 752 asset
lookups and 193 actual file callbacks through their nested callers. Whole fixture,
global, heap and return observations compare. Only 102 arithmetic NaN fields use
classification; 30 signaling-NaN bound stores require the physical x87 quiet bit.
Raw copies stay exact. Required setup parameters, valid sentinels/pool indices,
completion buffers and successful controller allocation remain internal contracts.
Unrecovered virtual methods remain unavailable. Channel dispatch, animation
parsing, the balance parent, full movement/startup and playable browser integration
are still unfinished.

Animation timeline progression (`004814b0`) now preserves forward/reverse
movement, looping, clamping, direction reversal and PC24 intermediate rounding.
Offset updates temporarily stop speed and restore its exact bits. Channel
construction, linked-list removal, stable descending controller priorities,
name lookup and removal execute the original concrete balance-controller and
reader cleanup paths, including selected/alternate fixed pools and heap fallback.

Animation event tables now load from actual QB structures and arrays. Integer
frames take precedence over seconds; each record owns a deep parameter copy.
Destruction runs in reverse array order and clears the channel count before
releasing storage. Missing/empty tables preserve the same fields as the original.
Frame crossing keeps the full signed 32-bit event frame, includes the starting
boundary and optionally includes the ending boundary. Triggers disable the event
before delivery; updates retain the original wrap reset and raw start-time rule.

The 1,311 cases / 1,915 calls pass against original x86, Node and Chromium. Real
object event routing and cached QB execute a terminal instrumented native command,
with 224 observations including changes to the live array, count, owner, enabled
bytes and later frames. All memory, globals, heap records and finite return bits
compare exactly; twelve NaN arithmetic returns compare by classification. Valid
wrapping ranges must terminate, allocation must succeed, and the heap service
must be initialized. Compiler exception unwinding is not implemented. These tests
do not supply animation parsing, channel command dispatch, full movement/startup
or a playable browser game.

Five concrete animation controller types now preserve their construction,
configuration, commands and destruction: timed, weighted, flag, pose and bone
controllers. Timed controllers own a separately allocated base timeline and
expose its current time, animation name and completion through actual QB setters.
Completion uses ordered equality with the selected endpoint, and only applies
when looping is disabled. Weighted commands preserve the original name-selection
precedence and reader replacement behavior.

Range parsing supports named endpoints, numeric overrides, seconds versus
integer-truncated frames, endpoint swapping and aliased outputs. Bone setup
preserves selection precedence, per-record enabled flags, rotation/velocity
conversion, untouched constructor fields and overlapping vector copies. The
vector parameter getter captures its source lanes before writing output; X
remains a raw word while Y/Z take the original x87 quiet-bit behavior.

The common controller prefix and concrete layouts now have separate C types.
Existing balance-controller exports remain compatible, and shared virtual
methods have correctly typed adapters. All 1,257 cases / 1,913 calls pass against
original x86, Node and Chromium; the full browser suite also passes after this
shared-layout change. Whole fixture memory, globals, allocation records and
finite returns compare exactly. Ninety-three arithmetic NaNs compare by
classification and 32 signaling-NaN stores use explicit, exact quiet-bit
corrections. Required parameter fields, valid bone indices/names, terminating
time ranges and successful allocation are internal contracts. Controller
update/render methods, the standard cache controller, full factory/channel
dispatch, asset parsing, full movement/startup and playable integration remain
unfinished.

Packed animation rotations and translations now decode through the original
header, byte/halfword, shared dictionary and custom dictionary paths. Overlapping
input, output and custom dictionary buffers preserve the exact load/store order.
Quaternion expansion preserves signed components, clamped square-root arithmetic,
the identity fast path and the original late read of the sign bit.

The complete animation cache builder (`00485270`) handles packed and expanded
record formats, empty bones, per-bone offsets, space checks, eviction and the
ten-build limit per 64-bit animation tick. Cache readers use the original selected
pool, alternate-pool release and heap fallback. Reader zero stays resident after
unpinning; block cleanup executes the actual registered callback and releases its
owned storage. Eviction preserves unsigned timestamp, size and priority rules.

All 2,003 cases / 2,447 calls pass against original x86, Node and Chromium,
including 103 complete builder calls and decode/pin/unpin/evict/rebuild sequences.
The full browser suite also passes after the allocator adapter gained named-cache
heap scope and contiguous-availability services. Those heap operations are host
services, explicitly distinct from recovered game routines. Existing adapter
fields and their offsets remain unchanged; availability is required by the new
cache allocation paths.

Memory, globals, heap records and returns compare exactly, with no arithmetic
NaN exceptions in this batch. Truly uninitialized two-byte padding in expanded
records is defined as zero; only those original automatic padding bytes are
seeded in the oracle. Translation records preserve the last rotation key's bytes
from reused temporary storage, which are not treated as undefined. Tested streams
cover 1..59 bones and all stride formats. Stream lengths and allocated buffers
must be valid, managers initialized, the cleanup busy bit clear, and requested
reader allocations successful. Standard controller/factory/channel dispatch,
full movement/startup and playable browser integration remain unfinished.

The keyframe buffer loader now supports both original animation layouts,
including optional bone maps, masks, custom dictionaries and all seven embedded
file-event types. It preserves signed key counts, alignment, fixed payload sizes,
borrowed stream pointers and the partial state left by unsupported events.
Initialization preserves the original unwritten fields; destruction uses the
actual event virtual methods and cache-removal callback.

All 1,707 installed `.ska.xbx` clips load and release successfully, including the
training camera animation. Twelve original skater clips also load, build caches
and release in all three tested cache formats, using the two exact 2,048-byte
compression dictionaries from `pre/Bits.prx`. All 1,708 input files are hashed in
the loading report. The complete 2,217-case / 5,780-call batch passes against
original x86, Node and Chromium, and the full browser regression suite passes.

There are 194 typed arithmetic NaN comparisons, including values copied through
overlapping position/quaternion storage; six signaling position values require
the physical x87 quiet bit. Other memory, heap events, globals and returns compare
exactly. File-event action methods remain unavailable. The original loaders trust
file sizes and borrow their buffers; bounds validation at the production loading
boundary remains necessary before accepting arbitrary user files. The 50-block
cache initializer is recovered; named-heap startup and complete controller/channel
integration remain unfinished. These tests do not make the game playable.

The standard animation controller now selects and pins clips, builds their
caches, replaces its reader and releases ownership in the original order.
The channel factory constructs all seven controller types, applies parameters
and inserts them with the original stable priority ordering. Channel commands
create/remove controllers, reload QB event arrays and preserve normalized clip
time when requested. Channel destruction runs actual controller virtual cleanup.

Frame updates now dispatch through each concrete controller. Standard and timed
controllers advance their timelines and refresh readers on a backward time step;
standard controllers also deliver their QB events. Balance playback computes the
original nested periodic modulation and range clamps. Bone controllers track four
target positions with the original flag gates and float store order. Channel
fading and live-list iteration retain callback mutations. The shared empty
update at `005480a0` was already counted in drawing recovery and is not counted
again here.

The 1,120-case / 2,334-call batch passes against original x86, Node and Chromium,
including complete clip load/select/cache/replace/destruction sequences, selected
and alternate pools, all factory types, real QB event delivery and mutation during
frame dispatch. Both clips and the original compression dictionary archive are
hashed in the report. All memory, globals, heap records and returns compare
exactly except 336 typed arithmetic NaNs checked by classification.

Unicorn leaves infinite FSIN operands unchanged, unlike hardware and the browser
math adapter. A read-only instruction trace of that difference is retained in
`local/validation/animation-playback-infinity-trace.json`; infinite phase
frequencies are outside strict comparisons. Finite out-of-range and NaN phase
frequencies, nonfinite amplitudes and zero-width bounds remain covered. Physical
x87 transcendental accuracy is not claimed. Required parameters, live assets,
successful allocation, a maximum of six controllers and terminating timelines are
internal caller contracts. Pose interpolation, rendering, component integration
and playable training remain unfinished.

The complete balance update now applies elapsed-time growth, input, recovery
decay and random drift, then forwards the result through the actual animation
channel and balance controller. It also executes score accumulation, timed-trick
notifications, failure-event delivery, script allocation and normal/manual meter
updates. Animation forwarding retains network clamping, quantization, change
suppression and queue replacement. Post-notification reads preserve mutations
made by synchronous QB handlers.

The 649-case / 1,432-call batch passes against original x86, Node and Chromium.
It includes 354 full balance frames, 220 subsequent animation channel updates,
423 terminal native QB observations, selected parameter pools, actual score/text
updates and all nineteen observed branch targets. Whole memory, globals, heap
records and returns compare; 154 typed arithmetic NaNs use classification only.
The fixture owner is a registered UI object with skater fields, so this does not
claim recovered skater construction. Required components/buttons, successful
allocations and finite meter curve indices remain internal contracts. Nonfinite
balance cases disable the meter to avoid invalid curve indexing. Full grounded
movement, startup, rendering and playable training remain unfinished.

The complete grounded movement update (`0050ee70`) now executes its recovered
callees together: heading and gravity, acceleration/braking, balance, resistance,
repulsion, moving-platform transport, attachment, collision/floor handling,
steering, input release and notifications. Its remaining-distance retry runs at
most once. Component reads after scripts preserve live replacements.

The 358-case / 1,525-call batch passes against original x86, Node and Chromium.
It contains 385 grounded frames, four eight-frame sequences, 18 movement retries,
54 terminal native QB observations and all 27 reachable observed parent branches.
The contact-update failure return is unreachable after the non-null-owner guard
in this synchronous graph; the game callee was not replaced to force it. All
arena/global bytes, heap effects and callback observations compare exactly for
these finite valid inputs. The original locked branch writes probe endpoints
that the subsequent query replaces from the retained surface segment; both
retained-segment hits and misses are tested without changing this behavior.

The fixture still supplies required components through a generic event-owner
constructor. It does not recover skater startup or constitute a playable level.
The complete airborne update is now covered below. Overall state integration,
startup and rendering remain necessary for the original training milestone.

Ten more airborne prerequisites now run as recovered C: pitch input,
incremental transfer orientation, upright correction, X/Z rotation helpers,
vector alignment and small-vector clearing, elapsed-time wrappers, and shared
state/sound material updates. Their 670-case / 1,510-call comparison passes
against the original instructions, Node and Chromium. It includes 124 pitch
calls, 73 transfer updates, 56 upright corrections and three actual material QB
callbacks that can replace state or sound components. Four active four-frame transfer
sequences retain the preceding orientation; two more sequences exercise the gate. Raw copies and no-write paths compare
exactly; arithmetic NaNs classify only at declared outputs.

The pitch cutoff compares the exact signed integer timer before its float spill
is reloaded for ramp arithmetic. Equality remains gated, and the second pressed
button replaces both the first rate and its timestamp. Matrix order, retained
wide-exponent progress and four-lane vector behavior follow the original code.
These prerequisite checks are supplemented by the complete airborne parent
checks below. The state dispatcher remains unfinished and the original training
level is still not playable.

The raised-path collision helper (`004ffdb0`) and overhead response (`00504ee0`)
now execute their complete collision sequences, with the probe copy constructor
and explicit moving-contact owner replacement needed by their enclosing paths.
The new 752-case / 3,131-call batch passes against original x86, Node and Chromium,
including 428 raised-path attempts and 300 overhead updates. Both probes can hit
real moving meshes: training floors, walls and ceilings are moved through the
original constructors and setters, with no replacement collision answers.

The overhead response keeps the first normal for velocity projection even when
the second hit has a different plane; final position uses the second result.
Raised-path rejection and acceptance release the temporary moving reference.
Consecutive overhead updates also test the reference retained from an earlier
frame. Raw copy fields, the whole arena, globals and heap observations compare
exactly for these finite geometry inputs, with no new NaN allowances. Fresh
constructor storage, required components and successful allocation remain
internal fixture contracts. Their complete airborne caller is now covered below;
skater startup, rendering and playable training remain unfinished.

The airborne flip-input parent (`004ffb90`) now uses recovered three-key history
matching, mark consumption, six-record axis queues and rotation scheduling.
The 675-case / 1,651-call batch passes against original x86, Node and Chromium,
including 208 complete parent calls, full queues, repeated input and script
callbacks. The matcher retains failed marks and the original physical-index
proximity check across a wrapping history buffer. Rotation scheduling preserves
the selected-axis mask even when its queue is already full.

Sixteen parent cases load all four `AerialFlips` definitions through the original
array parser from `qb_scripts.prx`'s `airtricks.qb`: backflip, frontflip and both
roll directions. That archived file differs from the loose script, but their
265-byte flip arrays match. The display handler remains an explicit diagnostic
QB fixture; complete trick display and advancing the queued rotations are not
established by this batch.

Actual local-player lookup and network queuing compare the defined packet
fields and heap effects. The original packet's final byte is unwritten stack
padding; the port defines only that byte as zero, with the oracle seeding the
same byte. Nine computed arithmetic NaNs compare by classification; raw queue
words, copied start values and untouched padding remain exact. Startup,
rendering and playable training are still unfinished. The complete airborne
update is covered separately below.

Landing sound selection (`00518cf0`) now distinguishes ordinary, grind and
slide landings and executes the recovered material, clip, attenuation, device
and network paths. Its 357-case / 369-call comparison includes missing named
events with a registered default, device failures and repeated calls with
callback-mutated component state. There are 2,916 device observations and no
new numeric allowances beyond the existing sound packet's one padding byte.

The complete spin-score routine (`00563f30`) and its guarded entry (`00564be0`)
now reproduce Half Cab/Cab labels, frontside/backside selection, color escapes,
combo text, score recalculation, numeric text and the spin event. The batch also
recovers the animation blend flag predicate, timed-spin store and ordered clamp.
All 493 cases / 3,395 calls pass against original x86, Node and Chromium. Tests
include actual broadcast and UI-notification QB callbacks that change the live
entry, multiplier or timed-trick gate. Cab renaming precedes the score-increase
test, and later reads retain callback changes. Seven numeric NaN results compare
by classification; raw timed-spin words, including NaN payloads, remain exact.
Complete movement integration, startup, rendering and playable training remain
unfinished.

The complete airborne spin update (`00504060`) now handles tap turns, shoulder
and directional inputs, automatic turning, body and cached Y rotations, and
cumulative spin scoring. Its 405 cases / 3,729 calls include 486 executions of
the parent and pass against original x86, Node and Chromium. Tests preserve
unsigned shoulder ages versus signed directional ages, exact integer parameter
returns, selected/default parameter sets, tap overshoot, automatic-turn cutoff
and overshoot, and the vertical-air scoring gate. Eight training collision
normals supply orientation bases for repeated frames with independent caches.

Sixteen actual native QB callbacks exercise UI and spin-broadcast mutations
between frames. All 24 new branch observers are reached. Finite results and
non-numeric memory compare exactly; 265 numeric NaN comparisons use the existing
classification allowance. The static math adapters retain their documented
limits concerning physical x87 transcendental accuracy. Complete airborne/state integration,
startup, rendering and playable training remain unfinished.

The complete trick-input interpreter (`0051fda0`) and five helpers now handle
all 18 selectors, including held-button combinations, ordered taps/releases,
three-button sequences, directional exclusions and the scaled Press window.
The 3,518-case / 3,959-call batch includes 3,539 complete interpreter calls,
with both acceptance and rejection observed for every selector. Original x86,
Node and the full Chromium regression pass with exact memory, globals and
results; this batch needs no numeric classification allowances.

Tests preserve each selector's different rules for partial marks, expiry,
exhaustion and mask commits. They cover equal keys, full 100-record rings,
unsigned timestamp wrap, overlapping argument/output storage, placeholder
substitution, repeated matches and the original single-precision-control
window conversion. The actual archived `Wallplant_Trick` array is parsed by
the original QB parser before eight matches using the game's arguments and
its 280-unit window. Its archive bytes are pinned in the oracle report.

These routines complete input-pattern recognition, not wallplant movement.
The remaining wallplant paths also call the shared wall-mark geometry code;
that code, complete airborne/state integration, startup, rendering and playable
training remain unfinished.

Twenty-two decal prerequisites now preserve the original triangle storage,
scene and texture lookup, CPU/GPU buffer-access bookkeeping, training-grid
bounds query, segment and triangle-square predicates, triangle subdivision,
lifetime/fade and color lighting.
The 3,582-case / 5,248-call batch passes original x86, Node and full Chromium
comparisons with exact return values and memory; no numeric classification
allowances were needed in this batch.

The subdivision checks include its complete 1,412-byte body, which Ghidra
splits across two apparent functions. Seven vertex formats from 12 to 128 bytes
exercise color and UV interpolation, byte tails and unaligned fields. Full
three-level draining produces 64 triangles and compares the retained 16 KB
work stack and all six scratch vertices after every step. Degenerate predicates,
area thresholds, wide x87 intermediate values, nonfinite inputs and output
pointer aliases are covered. The bounds query uses the original training
level's 605 collision instances and their grid membership.

The lifetime checks cover 375 cases / 886 calls, including pressure-triggered
fading, timer wrap, age ties and removal one update after all six alpha bytes
are already zero. The 259 lighting cases preserve selection of at most three
lights from the original 150-entry array, RGB saturation, alpha, overlapping
colors and untouched outputs. All 256 triangle slots are exercised through the
actual color-refresh wrapper. Initial globals are checked against the executable,
including the original subdivision threshold of 82,944.

Only the external graphics-device Lock method uses an instrumented host
callback; its arguments, return status, output and permitted mutations are
checked through the recovered wrapper. This establishes geometry preparation,
not displayed wall marks. The following batch adds projection math and
material/buffer allocation. Complete projection and mesh lifetime now pass in
the subsequent batch described below; the wallplant parents, engine startup
and rendering remain unfinished.

Seventeen more graphics prerequisites now pass original x86, Node and the
full Chromium regression: four D3DX math routines, nine material-list/table
routines, the CRT quicksort and private shortsort, CRT random generation, and
complete decal material/buffer lookup and allocation. The batch covers 2,209
cases / 3,618 calls, with 310 original heap allocations and 364 releases.
Material creation, insertion, reverse-first removal and empty-group disposal
execute their actual recovered callees. Sorting preserves the original unstable
order, including equal priorities, null groups, nonfinite keys and record widths
from 4 to 32 bytes. Repeated textures reuse the first matching buffer while
retaining the original iterator state and untouched timer/UV storage.

Projection math covers output/input overlap, alignment, normalization cutoffs,
degenerate view axes, tiny homogeneous depths and wide x87 intermediate
translations. Only 548 typed computed NaN outputs use classification; other
results and arena bytes compare exactly. The new reciprocal and reciprocal-root
seed adapters deliberately implement the pinned Unicorn 2.1.4 division/sqrt
model, preserving the game's Newton refinements. This does not establish the
same approximation bits as physical Intel or AMD CPUs. Selected SSE dispatch
targets are checked in a fresh browser module. CRT TLS and initialized game
heap services remain explicit host boundaries; Windows startup and allocation
failure behavior are not established by these successful-allocation fixtures.

The complete mesh destructor, vertex-buffer unregister and surface-mark
projection now pass against the original instructions and in Chromium: 347
cases / 371 calls across three routines. Projection covers 141 real training
collision faces repacked into CPU-backed render strips, arbitrary rays,
clipping, triangle-strip order, variable vertex strides, repeated descriptors,
texture reuse and replacement after filling all 256 mark records. These are
projection inputs, not a recovered render-asset loader. Descriptor endpoint
mutation, subdivision, timers, colors, UVs, scratch storage and heap ordering
are preserved. Only 486 typed computed NaNs compare by classification; other
observed bytes and numeric results match exactly.

Mesh tests cover material-table removal, owned/shared buffers, both resource
registries, stream binding, empty slots, wrapper zeroing and callback mutations.
They compare 2,114 terminal calls, including restored device pointers that cause
a second release. The original embedded material table is explicitly relocated
to host-owned storage without inventing a capacity. CRT free and terminal GPU
methods are host services; the full game destructor runs. Initialized successful
allocation, valid resource counts and GetStreamSource output storage are explicit
fixture contracts. The new shared-checker pointer metadata is opt-in; earlier
fixtures are rerun unchanged in the full browser check.

The complete scene-selection caller (`004928a0`) and wall-mark emitter
(`0051dbc0`) now pass 178 cases / 207 calls in original-instruction comparison
and Chromium. Scene tests preserve the complete 605-object training collision
grid's bounds, flags and cell order, exposing 70 sampled collision faces as CPU
render strips. They also cover multiple scenes, previous-point hash chains,
expiry/future timestamps, the strict 66-unit distance boundary, first-point
registration, unchanged positions, and repeated fading and buffer pressure.
The original twelve-argument scene signature keeps tracking identity separate
from projection type. Texture selection tests distinguish direct and indirect
textures, named lookup, angle parameters and byte-sized flags.

Emitter tests execute the actual network gate, client lookup, first-peer send,
message allocation and queue ownership. All 38 defined packet bytes compare
exactly, including retained nonfinite vector words and signed size values.
The two packet padding bytes that the original never writes are initialized to
zero in the port and seeded at the original function's entry for comparison.
Only 342 computed NaN float fields compare by classification; no packet or
integer field uses that exception. Reused fixture heap words relocate only
registered pointer identities; other values retain exact byte or explicitly
typed float checks. The full earlier browser suite passes with this correction.

The complete wall-contact caller (`0051ddf0`) now passes 249 cases / 383 calls,
including existing moving-collision setup. Cooldown decrement, signed inhibition,
byte-sized flags, both direction sources, all three origin heights, arming and
mark emission run through their actual collision and network callees. Tests
include 48 sloped walls, 114 training cases across 38 sampled faces, moving
surfaces and existing reference chains. All arena, global and result bytes
compare exactly; this corpus needs no arithmetic NaN exception.

The vertical-wallplant caller (`00503710`) passes 188 cases / 189 calls. Script
names identify its event as `Vert_Wallplant` and distinguish it from the separate
standard wallplant (`00507500`). Held and recent input, strict expiry, early
consumption, surface distance/velocity/height gates, normal-angle limits and the
surface-flag bypass are covered. Its second collision probe runs through the
wall-contact caller, including armed mark projection and queued notifications.
The corpus includes 76 training-geometry cases, signed boost limits and timer
wrap. Real object-event delivery, collision-triggered script spawning and QB
execution invoke 15 configured native observers that change the current body,
state, notification context, velocity or suppression flag. Objective notification
insertion and both state-reset timestamps are compared. Every new fixture byte
matches exactly; only the previously documented emitter padding is seeded.
Terminal diagnostics, GPU/CRT services, the fixture allocator and native QB
observers are explicit test boundaries, not recovered gameplay functions.

The complete standard-wallplant caller (`00507500`) now passes 303 cases /
631 calls, including 304 wallplant attempts and the existing probe/moving-surface
setup. Normal, late, check-only and forced modes preserve byte-sized arguments,
input matching, saved position/velocity/normal, signed and unsigned timer gates,
reflection, minimum speed and vertical boost. Rising clearance and the outgoing
probe are actual scene queries; a second wall verifies use of the newly returned
point and normal. Moving-owner reuse, dead references, mark rejection, state
flags, notification limits and script handlers that replace live components are
covered. The corpus includes 42 sloped-surface cases, 76 training-geometry cases,
36 varied finite velocities, timer wrap and 12 native QB observer callbacks. All
new arena, global and return bytes match exactly with no arithmetic NaN allowance.
The original instruction corpus and boundaries are recorded in
`local/validation/standard-wallplant.json`.

The complete airborne wall-contact caller (`00508780`) now passes 287 cases /
320 calls, including 288 parent executions. It retains the original surface
classification, raised-path and step-search branches, ground projection,
standard wallplant and wall-transition attempts, fallback events, impact sound,
orientation changes and moving-owner response. The corpus includes 76 training
geometry cases, short walls, raised floors, signed parameters, timer wrap,
normal thresholds, repeated contacts and reference cleanup. Ten native QB
observers and 548 OS audio callbacks exercise component mutations and playback
failures. Arena, global and return bytes match exactly, without arithmetic NaN
allowances. The established two emitter-padding bytes and one audio-packet
padding byte are seeded; configured components, successful heap operations,
and instrumented OS/GPU/CRT/native QB services remain explicit boundaries.
The original instruction results are recorded in `local/validation/air-wall.json`.

The complete airborne update (`0050ca00`) now passes against the original
instructions, Node and Chromium: 308 scenarios / 473 calls, including 337 complete
airborne frames across movement and scoring arenas. It retains input handling,
pitch/spin/flip scheduling, gravity and moving transport, transition following,
wallplants, floor/ceiling collision, landing events/sound and both transfer paths.
The checks include successful transfers on training geometry, the four shipped
flip definitions parsed by the original parser, score recalculation and both text
widgets, repeated frames, timer wrap, and scripts replacing live components.
Two alternate-transfer scripts remove the moving owner before the parent's
second reference cleanup. There are 48 native QB and 300 OS audio observations.

The movement trace executes 1,128 of the parent's 1,131 instructions. The three
unexecuted instructions release a moving contact after its helper reports failure;
the caller has just checked a nonnull owner, and the current single-threaded
helper cannot fail in that case. The defensive branch remains in the recovered
source. This coverage describes one routine, not a percentage of the game.
Eighteen declared arithmetic NaN outputs compare by classification in exponent
limit and nonfinite cases; other defined arena/global/heap bytes compare exactly.
The established emitter and audio padding, OS/GPU/CRT services, successful
allocations, required components and terminal native QB observers remain explicit
test boundaries. Original evidence is in `local/validation/airborne-update.json`
and `local/validation/airborne-score.json`; the complete browser proof is in
`local/validation/collision-browser.json`.

The movement dispatcher (`00510830`), its remaining movement states, renderer,
browser audio and game startup remain unfinished. No playable training level is
claimed by these comparisons.

Four complete movement-dispatcher prerequisites now pass against the original
instructions, Node and Chromium. Collision-cache setup (`00500670`) builds the
skater's asymmetric search box and publishes its static/moving candidates. Speed
limiting (`00501850`) preserves the raw vertical velocity, applies horizontal
limits and expires overrides. Revert recovery (`00500710`) uses an unsigned
strict timer comparison; focus input (`005007a0`) uses a signed hold comparison
and invokes the actual synchronous script once per hold.

The three new suites cover 544 scenarios / 909 calls, including 130 cache builds
and 59 complete airborne frames on training geometry, plus 270 diagnostic,
native QB and OS audio callbacks. They exercise repeated frames, callbacks
changing counters and clocks, input/component replacement, timer wrap, special
override values, and finite/nonfinite arithmetic. All 227 instructions in the
four new parent routines execute. Forty declared computed NaN fields compare by
classification; vertical velocity is compared as raw bits. Existing explicit
host boundaries and successful-allocation/component contracts still apply.
Reports are `local/validation/skater-cache.json`, `cached-airborne.json` and
`frame-prerequisites.json`, alongside their browser results in the complete
`collision-browser.json` proof. These are prerequisites; the complete dispatcher,
other movement states, startup and rendering still prevent playable training.

Three more complete frame actions now pass original instructions, Node and
Chromium. Projectile handling (`00500820`) checks the real input history, commits
marks, maintains its cooldown and chooses the walking or skating QB handler.
Rotation completion (`00500900`) clears the real axis queues, toggles skater and
animation flip state and queues the original one- and two-byte messages. Special
expiration (`00500bc0`) waits until the frame after its timer crosses zero, then
calls the actual synchronous script with an owned `TimeLimit` argument. That
argument is checksum type 13 with payload 1, rather than integer type 1.

These parents and eight prerequisites are covered by 382 scenarios / 1,795
calls, including 1,146 existing object-setup calls. The separate release-input
matcher (`0051fb90`) contributes 512 scenarios / 532 calls, preserving partial
marks on failure, unsigned age limits, ring wrap and the three raw argument
words copied on commit. Together the suites observe 75 native QB calls and 199
queued messages. All 159 matcher instructions and 565 of 566 action instructions
execute. The one unexecuted instruction handles a null allocation before the
original immediately writes through that null pointer; successful allocation
remains an explicit internal contract. Forty-nine declared computed NaNs compare
by classification; other defined arena/global/heap/packet bytes compare exactly.
Reports are `local/validation/release-input.json` and `frame-actions.json`, with
their results included in the complete browser proof. These additions do not
complete the movement dispatcher, remaining states, rendering or playable level.

Attachment acquisition (`00503ec0`) now searches the original registry's separate
type chain, selects the nearest valid attachment, clears input latches, binds the
real object reference and emits both object events. Its range test uses actual
distance. Callback tests cover the first event replacing the skater body before
the second event. Post-transfer speed updates (`004ff200`) preserve the original
speed multiplier, decay, ordered minima, float spill order and signed diagnostic
counter. The diagnostic callback receives the original format and double value,
and can change limits or trigger repeated output by changing the counter.

The two new suites add seven complete routines across 1,269 cases / 2,316 calls:
1,386 calls exercise the new routines, and 930 are existing setup/reference calls.
They cover 422 of 423 parent instructions; the skipped `00503f69` instruction is
unreachable alignment padding. There are 11 native QB and 13 diagnostic callback
observations. A total of 153 declared computed NaNs compare by classification;
other defined memory, global and callback bytes compare exactly. Reports are
`local/validation/post-frame.json` and `dispatch-paths.json`, with both results in
the complete browser proof. The movement dispatcher and playable level remain
unfinished; these routine counts do not measure percent completion.

The complete wallplant state (`00509050`) now waits for the original duration,
follows moving contacts, and switches to air with the original training-surface
probe and script event. Rail eligibility retains adjacency, retry timing, force
and velocity gates, plus all four endpoint distances. The contact-world helper
uses the retained owner independently of the current contact and preserves
aliased outputs and raw coordinate lanes.

These four routines add 696 cases / 1,425 calls: 708 calls to the new routines and
717 existing setup calls. Coverage reaches 463 of 468 parent instructions; the
five remaining instructions form a defensive failed-contact-update branch that
cannot occur after the immediate live-owner guard in the current single-threaded
callee. The source retains that branch. There are four native QB observations,
160 computed NaNs compared by classification and 32 exact x87 quiet-bit corrections
for signaling NaNs retained by Unicorn. The three reports are
`local/validation/wallplant-state.json`, `rail-gate.json` and `contact-world.json`.
All three are included in the complete browser proof. The game is still not playable.

The complete lip state (`0050bf50`) now follows moving contacts, runs its original
balance and cheat checks, handles release, and emits rail script events. The rail
event helper retains predecessor traversal, cycle guards, explicit zero handling
and callback-sensitive state. Wall overhang (`005051b0`) probes above the skater,
corrects position and projects velocity against the contact normal.

These four routines add 490 cases / 1,242 calls: 530 calls to the new routines and
712 existing setup calls, with 115 native QB observations and 67 computed NaNs
compared by classification. Coverage reaches 481 of 484 parent instructions;
three instructions form a defensive failed-contact-update branch unreachable
after the immediate live-owner guard with the current single-threaded callee.
The source retains that branch. The reports are `local/validation/lip-state.json`
and `wall-overhang.json`; both are included in the full browser proof. The game
is still not playable.

Rail selection (`0057e2d0`) now searches the original 0x54-byte node array,
checks clearance and approach side against real collision geometry, and ranks
point and segment candidates by distance and angle. It preserves the original
case where a closer but unsuitable candidate invalidates an earlier selection.
The line helpers retain sequential clamping and aliased-output behavior.

These seven routines add 2,158 cases / 3,770 calls, including 750 original
moving-object constructor and setter calls. Coverage reaches 1,302 of 1,305
parent instructions. Three defensive unlink instructions after a probe miss are
unreachable because the actual query returns true whenever it retains a moving
object; the recovered cleanup remains. The tests compare 188 computed NaNs by
classification and apply 166 exact physical-x87 quiet-bit corrections. Reports
`rail-math.json`, `rail-clearance.json` and `rail-search.json` under
`local/validation/` are included in the full browser proof. Grind entry and the
remaining game integration are unfinished; the original level is not playable.

Grind prerequisites now include balance cleanup, rail repetition scoring,
orientation flips and their network messages, pending-trick cancellation, and
the routines that select and execute grind scripts. Script selection preserves
direct checksums, template-generated names, and profile slot replacements; the
parameters still come from the originally selected trick entry.

These seventeen routines add 1,541 cases / 4,184 calls, including 1,689 original
setup calls and 412 native QB callbacks. They exercise 815 of 819 instructions;
the four remaining instructions are heap-service bootstrap and null-allocation
branches outside the initialized-memory/successful-allocation test contracts.
The recovered source retains allocator selection and null assignment. Tests
compare 12 computed NaNs by classification and apply 256 exact x87 quiet-bit
corrections. All five suites are included in the browser checkpoint. The browser harness
runs each suite in a separate worker and terminates it afterward to release
large fixture datasets and Wasm memory. The full rail-entry routine is now recovered as described below; playable game integration remains unfinished.

The complete rail-entry routine (`0050a770`) now handles point-rail jumps, Natas
spins, lip tricks and ordinary grinds. Its recovered callees perform collision
queries, repetition scoring, material and sound changes, pending flips, script
selection and execution, and event/network delivery. The translation retains
the original timing, floating-point operation order, and live component reads
after scripts run.

Three maintained suites compare 420 cases / 2,100 calls, including 1,680 actual
object/meter setup calls and 292 native QB callbacks. They cover 1,629 of 1,630
parent instructions; the remaining null-allocation assignment is retained in
source but outside the successful-allocation test contract. All comparisons
pass in the complete Chromium run. Rail/Natas state and the movement dispatcher
are now recovered as described below; playable engine integration remains unfinished.

Rail acquisition (`0050dae0`) now searches both fixed and moving rails, runs
the original eligibility and entry logic, and preserves moving-contact ownership
and relative velocity. Its 100 cases / 500 calls cover all 232 instructions.

The full wallride update (`0050f830`) now handles moving surfaces, wall orientation,
continued contact, overhead exits, floor landings, rail catches and jumping away.
Three suites compare 169 cases / 855 calls, including three actual landing-to-rail
catches and five prior-contact callbacks generated from real training collision.
All 11 native QB callbacks and the complete fixture memory match. The tests cover
1,124 of 1,127 instructions; the three remaining defensive release instructions
follow a prechecked live owner and are retained in the translation. Both new
routines pass in Chromium. The training level remains unplayable.


The Natas state (`00504730`), connected-rail transition (`0050c200`) and full rail
update (`0050ddf0`) are now recovered. They preserve balance and spin scoring,
moving-contact transport, original slope and direction calculations, connected
rail selection, wall/ground probes, endpoint scoring and synchronous script events.
The combined rail corpus covers 1,173 of 1,179 parent instructions. Six defensive
failed-contact instructions cannot be reached after the live-owner checks in this
original call graph; both branches remain in the C translation.

The complete movement dispatcher (`00510830`) now calls the six original movement
states, performs fixed/moving rail acquisition and frame actions, and emits the
original vert-air events. The repeated inlined acquisition uses the same recovered
rail-acquisition implementation. Tests include training landings, callbacks that
replace live state/components, nonboolean flag bytes, and eight retained frames
across all six states at three time scales, plus retained Natas frames.

Six new suites compare 327 cases / 2,113 calls and 537 native QB callbacks with
exact defined-memory comparisons and no new NaN allowances. Of these calls, 509
are the four new routines, 208 copy previous positions, 88 initialize collision
caches, and 1,308 perform existing object setup. Natas, transition and dispatcher
cover all 127, 325 and 350 parent instructions respectively. The full 139-suite
Chromium run passed with a 467,179-byte module and no runtime imports.
The original training level remains unplayable: startup, asset integration,
camera behavior and browser rendering/input/audio still need work.


The original object update (`0045d920`) and moved notification (`0045e4c0`)
are now recovered. The update preserves suspension checks, script execution,
virtual object/component calls, callback changes to live list links, and the
different cleanup behavior of early returns and interrupted component walks.
Fourteen cases call the complete recovered physics update through this virtual
loop, including every movement state, fixed/moving rails and training landings.
Other component frame methods remain suspended in those cases; controlled test
callbacks verify traversal semantics without representing unrecovered gameplay.
The typed physics/empty-method adapters are not counted as additional recoveries.

Physics initialization and ordered linking of 12 components, component wait
invalidation, shadow vector copies, camera-object lookup and flip synchronization
are also integrated. The camera lookup preserves the original callee's use of
the global object registry, even when passed a different manager. Shadow copying
preserves overlapping forward-word copies and floating-point payload bits.

The four new suites compare 364 cases / 951 calls: 652 calls to the ten new
routines and 299 existing setup calls, with 23 native QB callbacks and exact
defined-memory comparisons. All 233 initialization, reset and object-loop
instructions are covered. Wait cleanup covers 50 of 54 instructions; two are
unused alignment instructions and two form a restart branch unreachable because
the callee preserves ECX. No new NaN allowances are used.
The complete 143-suite Chromium run passed with a 469,452-byte module and no
runtime imports. The original training level remains unplayable. Component
construction, remaining native handlers, camera behavior and the connection to
browser rendering, input, audio and level assets still need work.

The base component and physics component now have their original construction,
destruction, suspension and complete 13-slot method tables. Physics allocation
zeroes the full original object before running the constructor; cleanup releases
the collision cache, linked object references and component waits in original
order. Descriptor dispatch preserves its fixed argument layout, including direct
member calls and receiver adjustment. Abstract methods trap explicitly.

Node positions/angles, Motion orientation and node-movement commands are also
integrated. Arrival preserves script-spawn precedence, speed units, timing,
acceleration and immediate versus deferred behavior. The physics command calls
the actual Motion path and updates shadow, previous position, reset state and
animation/network effects. Camera-object lookup and QB execution are exercised;
the full camera implementation remains unfinished.

A shared host-service scope now surrounds startup script execution, object
updates, physics frames and command entry. Nested commands restore the caller's
collision query and memory/diagnostic context. This is platform integration, not
an additional recovered game routine. The context suite exercises actual QB
descriptor calls from startup and object-frame paths with both null and existing
outer scopes; other component frame methods are suspended to isolate script entry.

The five recovery suites compare 850 cases / 2,330 calls and 15 native QB
callbacks. The context checks add 60 WebAssembly cases / 228 calls and 36
callbacks. Together the six suites cover 910 cases / 2,558 calls, with no new
NaN allowances. Original instruction coverage is 863/871: three defensive
old-owner unlink instructions are unreachable after a fresh bytecode spawn,
and five allocation-failure return instructions lie outside the successful
allocator contract. Their branches remain in the translation. Win32 exception
unwinding is not claimed.

The complete 159-suite Chromium run passed with a 485,404-byte module and no
runtime imports. All prior comparison reports and pinned isolated recoveries
are preserved. The original training level remains unplayable: other component
classes and Motion frame updates, physics/native script handlers, camera behavior,
level startup and browser rendering/input/audio still need integration.

Jump and its script command (`00509450` / `00509a40`) now execute the original
charge clamp, stat interpolation, `Speed`, `NoSound` and alternate-jump parameters,
vertical and tilted impulses, rail turn, floor/rail callbacks, state changes and
final broadcast. The sound helpers (`00518d60` / `00518ee0`) and directional turn
(`005002d0`) are integrated too. Script and device callbacks can replace live
state or change velocity; the translation reloads those fields in original order.

Actual QB descriptor calls reach Jump from startup execution and object updates.
The 36 original context cases replay under two prior host scopes for 72 WebAssembly
cases, checking context restoration after every call. Other component frames are
suspended in this fixture; complete component registration and level startup remain.
Together the four new suites compare 866 WebAssembly cases / 1,889 calls with
125 native QB and 6,056 OS audio observations, zero new NaN allowances, and all
455 original instructions covered. Generic fixture construction, terminating QB,
successful allocation, positive charge limits and finite parent inputs are explicit
test contracts. This does not provide actual browser audio or a playable level.


The physics command integration adds 67 recovered routines: 65 fixed-ABI members,
command-symbol registration (`0046f060`) and component-factory registration
(`0045f270`). Direct and named-QB comparisons cover all 474 original instructions.
The six new suites pass 18,928 WebAssembly cases / 38,558 calls with no new NaN
allowances. All original test inputs and expected memory results are preserved
from the pinned experimental corpora. The optional factory initialization callback
is test instrumentation in a separate module, and factory creation is not exercised
by the registration suite.

The original initializer establishes all 109 descriptors for reference comparisons;
it has not itself been translated. Jump and 65 commands have maintained callable
members. Five more have passed isolated direct and named-script tests; 38 entries
still need binding or recovery. `IsFacingWall` already has a recovered implementation
among those 38, so adding its member adapter will not count as a new recovery.
Named-dispatch fixtures suspend other component frames and use terminating test
scripts. Actual level scripts, complete startup and browser graphics/input/audio
remain unfinished.

The LZSS checks cover all 263 compressed members of `TRscn.prx`, `TRcol.prx`,
`TRped.prx`, and `TR_scripts.prx`, plus 152 synthetic streams. There are 362 members
across these archives. Of those, 289 match loose files byte for byte, 71 have no
same-path loose copy, and two archived scripts differ from their loose counterparts
(`TR_scripts.qb` and `TR_sfx.qb`). Both decompressed scripts match the executable's
decoder output. Do not silently substitute the loose versions when reproducing
the game's archive-loading behavior.

## Reproduce the checks

With the local dependencies already installed in this workspace:

```sh
PYTHONPATH=.tools/python python3 tools/index_executable.py
PYTHONPATH=.tools/python python3 tools/verify_checksums.py
PYTHONPATH=.tools/python python3 tools/verify_lzss.py
PYTHONPATH=.tools/python python3 tools/verify_bounds.py
python3 tools/build_wasm.py
PYTHONPATH=.tools/python python3 tools/verify_collision.py
PYTHONPATH=.tools/python python3 tools/verify_geometry.py
PYTHONPATH=.tools/python python3 tools/verify_triangles.py
PYTHONPATH=.tools/python python3 tools/verify_segments.py
PYTHONPATH=.tools/python python3 tools/verify_scene.py
PYTHONPATH=.tools/python python3 tools/verify_loading.py
PYTHONPATH=.tools/python python3 tools/verify_moving.py
PYTHONPATH=.tools/python python3 tools/verify_probes.py
PYTHONPATH=.tools/python python3 tools/verify_params.py
PYTHONPATH=.tools/python python3 tools/verify_skater.py
PYTHONPATH=.tools/python python3 tools/verify_surface.py
PYTHONPATH=.tools/python python3 tools/verify_orientation.py
PYTHONPATH=.tools/python python3 tools/verify_skating_params.py
PYTHONPATH=.tools/python python3 tools/verify_stats.py
PYTHONPATH=.tools/python python3 tools/verify_ground.py
PYTHONPATH=.tools/python python3 tools/verify_motion.py
PYTHONPATH=.tools/python python3 tools/verify_resistance.py
PYTHONPATH=.tools/python python3 tools/verify_repulsion.py
PYTHONPATH=.tools/python python3 tools/verify_low_speed.py
PYTHONPATH=.tools/python python3 tools/verify_wall_turn.py
PYTHONPATH=.tools/python python3 tools/verify_contact_nodes.py
PYTHONPATH=.tools/python python3 tools/verify_script_state.py
PYTHONPATH=.tools/python python3 tools/verify_script_branches.py
PYTHONPATH=.tools/python python3 tools/verify_script_values.py
PYTHONPATH=.tools/python python3 tools/verify_script_copy.py
PYTHONPATH=.tools/python python3 tools/verify_script_construct.py
PYTHONPATH=.tools/python python3 tools/verify_script_tokens.py
PYTHONPATH=.tools/python python3 tools/verify_script_ranges.py
PYTHONPATH=.tools/python python3 tools/verify_script_operators.py
PYTHONPATH=.tools/python python3 tools/verify_script_expression.py
PYTHONPATH=.tools/python python3 tools/verify_script_parser.py
PYTHONPATH=.tools/python python3 tools/verify_script_symbols.py
PYTHONPATH=.tools/python python3 tools/verify_compression.py
PYTHONPATH=.tools/python python3 tools/verify_script_cache.py
PYTHONPATH=.tools/python python3 tools/verify_script_load.py
PYTHONPATH=.tools/python python3 tools/verify_script_control.py
PYTHONPATH=.tools/python python3 tools/verify_script_events.py
PYTHONPATH=.tools/python python3 tools/verify_script_execute.py
PYTHONPATH=.tools/python python3 tools/verify_script_lifetime.py
PYTHONPATH=.tools/python python3 tools/verify_script_serialize.py
PYTHONPATH=.tools/python python3 tools/verify_network_queue.py
PYTHONPATH=.tools/python python3 tools/verify_script_schedule.py
PYTHONPATH=.tools/python python3 tools/verify_event_delivery.py
PYTHONPATH=.tools/python python3 tools/verify_rebound.py
PYTHONPATH=.tools/python python3 tools/verify_sound_selection.py
PYTHONPATH=.tools/python python3 tools/verify_sound_spatial.py
PYTHONPATH=.tools/python python3 tools/verify_sound_voices.py
PYTHONPATH=.tools/python python3 tools/verify_audio_device.py
PYTHONPATH=.tools/python python3 tools/verify_sound_events.py
PYTHONPATH=.tools/python python3 tools/verify_wall_response.py
PYTHONPATH=.tools/python python3 tools/verify_movement_sweep.py
PYTHONPATH=.tools/python python3 tools/verify_moving_contact.py
PYTHONPATH=.tools/python:tools python3 tools/verify_orientation_blend.py
PYTHONPATH=.tools/python:tools python3 tools/verify_state_events.py
PYTHONPATH=.tools/python:tools python3 tools/verify_floor_transition.py
PYTHONPATH=.tools/python:tools python3 tools/verify_grounded_steering.py
PYTHONPATH=.tools/python:tools python3 tools/verify_attachment.py
PYTHONPATH=.tools/python:tools python3 tools/verify_objective_state.py
PYTHONPATH=.tools/python:tools python3 tools/verify_objective_actions.py
PYTHONPATH=.tools/python:tools python3 tools/verify_objective_text.py
PYTHONPATH=.tools/python:tools python3 tools/verify_objective_initialize.py
PYTHONPATH=.tools/python:tools python3 tools/verify_objective_deactivate.py
PYTHONPATH=.tools/python:tools python3 tools/verify_score_reset_prerequisites.py
PYTHONPATH=.tools/python:tools python3 tools/verify_font_text.py
PYTHONPATH=.tools/python:tools python3 tools/verify_ui_drawing.py
PYTHONPATH=.tools/python:tools python3 tools/verify_ui_construction.py
PYTHONPATH=.tools/python:tools python3 tools/verify_ui_registry.py
PYTHONPATH=.tools/python:tools python3 tools/verify_ui_manager.py
PYTHONPATH=.tools/python:tools python3 tools/verify_ui_multiline.py
PYTHONPATH=.tools/python:tools python3 tools/verify_score_display.py
PYTHONPATH=.tools/python:tools python3 tools/verify_objective_activate.py
PYTHONPATH=.tools/python:tools python3 tools/verify_objective_dispatch.py
PYTHONPATH=.tools/python:tools python3 tools/verify_objective_completion.py
PYTHONPATH=.tools/python:tools python3 tools/verify_objective_notifications.py
PYTHONPATH=.tools/python:tools python3 tools/verify_side_contact.py
PYTHONPATH=.tools/python:tools python3 tools/verify_transfer.py
PYTHONPATH=.tools/python:tools python3 tools/verify_transfer_apply.py
PYTHONPATH=.tools/python:tools python3 tools/verify_floor.py
PYTHONPATH=.tools/python:tools python3 tools/verify_balance_score.py
PYTHONPATH=.tools/python:tools python3 tools/verify_balance_display.py
PYTHONPATH=.tools/python:tools python3 tools/verify_balance_prerequisites.py
PYTHONPATH=.tools/python:tools python3 tools/verify_animation_assets.py
PYTHONPATH=.tools/python:tools python3 tools/verify_animation_events.py
PYTHONPATH=.tools/python:tools python3 tools/verify_animation_controllers.py
PYTHONPATH=.tools/python:tools python3 tools/verify_animation_cache.py
PYTHONPATH=.tools/python:tools python3 tools/verify_animation_loading.py
PYTHONPATH=.tools/python:tools python3 tools/verify_animation_playback.py
PYTHONPATH=.tools/python:tools python3 tools/verify_balance_update.py
PYTHONPATH=.tools/python:tools python3 tools/verify_grounded_update.py
PYTHONPATH=.tools/python:tools python3 tools/verify_airborne_motion.py
PYTHONPATH=.tools/python:tools python3 tools/verify_airborne_collision.py
PYTHONPATH=.tools/python:tools python3 tools/verify_airborne_rotation.py
PYTHONPATH=.tools/python:tools python3 tools/verify_landing_sound.py
PYTHONPATH=.tools/python:tools python3 tools/verify_spin_score.py
PYTHONPATH=.tools/python:tools python3 tools/verify_airborne_spin.py
PYTHONPATH=.tools/python:tools python3 tools/verify_trick_input.py
PYTHONPATH=.tools/python:tools python3 tools/verify_decal_prerequisites.py
PYTHONPATH=.tools/python:tools python3 tools/verify_decal_resources.py
PYTHONPATH=.tools/python:tools python3 tools/verify_decal_projection.py
PYTHONPATH=.tools/python:tools python3 tools/verify_wall_marks.py
PYTHONPATH=.tools/python:tools python3 tools/verify_wall_contact.py
PYTHONPATH=.tools/python:tools python3 tools/verify_wallplant.py
PYTHONPATH=.tools/python:tools python3 tools/verify_standard_wallplant.py
PYTHONPATH=.tools/python:tools python3 tools/verify_air_wall.py
PYTHONPATH=.tools/python:tools python3 tools/verify_airborne_update.py
PYTHONPATH=.tools/python:tools python3 tools/verify_airborne_score.py
PYTHONPATH=.tools/python:tools python3 tools/verify_skater_cache.py
PYTHONPATH=.tools/python:tools python3 tools/verify_cached_airborne.py
PYTHONPATH=.tools/python:tools python3 tools/verify_frame_prerequisites.py
PYTHONPATH=.tools/python:tools python3 tools/verify_release_input.py
PYTHONPATH=.tools/python:tools python3 tools/verify_frame_actions.py
PYTHONPATH=.tools/python:tools python3 tools/verify_post_frame.py
PYTHONPATH=.tools/python:tools python3 tools/verify_dispatch_paths.py
PYTHONPATH=.tools/python:tools python3 tools/verify_wallplant_state.py
PYTHONPATH=.tools/python:tools python3 tools/verify_rail_gate.py
PYTHONPATH=.tools/python:tools python3 tools/verify_contact_world.py
PYTHONPATH=.tools/python:tools python3 tools/verify_lip_state.py
PYTHONPATH=.tools/python:tools python3 tools/verify_wall_overhang.py
PYTHONPATH=.tools/python:tools python3 tools/verify_rail_math.py
PYTHONPATH=.tools/python:tools python3 tools/verify_rail_clearance.py
PYTHONPATH=.tools/python:tools python3 tools/verify_rail_search.py
PYTHONPATH=.tools/python:tools python3 tools/verify_grind_helpers.py
PYTHONPATH=.tools/python:tools python3 tools/verify_pending_flip.py
PYTHONPATH=.tools/python:tools python3 tools/verify_grind_script.py
PYTHONPATH=.tools/python:tools python3 tools/verify_trick_cleanup.py
PYTHONPATH=.tools/python:tools python3 tools/verify_pending_trick.py
PYTHONPATH=.tools/python:tools python3 tools/verify_rail_entry_paths.py
PYTHONPATH=.tools/python:tools python3 tools/verify_rail_entry_edges.py
PYTHONPATH=.tools/python:tools python3 tools/verify_rail_entry_numeric.py
PYTHONPATH=.tools/python:tools python3 tools/verify_rail_acquisition.py
PYTHONPATH=.tools/python:tools python3 tools/verify_wallride_paths.py
PYTHONPATH=.tools/python:tools python3 tools/verify_wallride_contact.py
PYTHONPATH=.tools/python:tools python3 tools/verify_wallride_edges.py
PYTHONPATH=.tools/python:tools python3 tools/verify_natas_state.py
PYTHONPATH=.tools/python:tools python3 tools/verify_rail_transition.py
PYTHONPATH=.tools/python:tools python3 tools/verify_rail_state.py
PYTHONPATH=.tools/python:tools python3 tools/verify_rail_state_edges.py
PYTHONPATH=.tools/python:tools python3 tools/verify_movement_dispatch.py
PYTHONPATH=.tools/python:tools python3 tools/verify_movement_dispatch_edges.py
PYTHONPATH=.tools/python:tools python3 tools/verify_physics_initialize.py
PYTHONPATH=.tools/python:tools python3 tools/verify_component_waits.py
PYTHONPATH=.tools/python:tools python3 tools/verify_physics_reset.py
PYTHONPATH=.tools/python:tools python3 tools/verify_object_frame.py
PYTHONPATH=.tools/python:tools python3 tools/verify_node_vectors.py
PYTHONPATH=.tools/python:tools python3 tools/verify_motion_orientation.py
PYTHONPATH=.tools/python:tools python3 tools/verify_motion_command.py
PYTHONPATH=.tools/python:tools python3 tools/verify_physics_command.py
PYTHONPATH=.tools/python:tools python3 tools/verify_component_lifecycle.py
PYTHONPATH=.tools/python:tools python3 tools/verify_component_context.py
PYTHONPATH=.tools/python:tools python3 tools/verify_jump_sound.py
PYTHONPATH=.tools/python:tools python3 tools/verify_jump_turn.py
PYTHONPATH=.tools/python:tools python3 tools/verify_jump.py
PYTHONPATH=.tools/python:tools python3 tools/verify_jump_context.py
PYTHONPATH=.tools/python:tools python3 tools/verify_command_registration.py
PYTHONPATH=.tools/python:tools python3 tools/verify_factory_registration.py
PYTHONPATH=.tools/python:tools python3 tools/verify_physics_registration_table.py
PYTHONPATH=.tools/python:tools python3 tools/verify_physics_flags.py
PYTHONPATH=.tools/python:tools python3 tools/verify_physics_state_actions.py
PYTHONPATH=.tools/python:tools python3 tools/verify_physics_state_actions_context.py
```

The verifiers compile the C with Clang, run the relevant x86 instructions in
Unicorn, and compare results. Reports go to `local/validation/`. On this Mac,
Unicorn's CPU-cache detection crashes inside the Codex sandbox; these verification
commands require approved execution with normal host CPU detection. They do not
launch the game executable as a Windows process.

Python dependencies are pinned in `tools/requirements.txt`. The native core tests
use macOS dynamic libraries. The WebAssembly compiler is the local
`.tools/wasi-sdk-34.0-arm64-macos/bin/clang`; its downloaded archive was checked
against the official release SHA-256 recorded in `local/references/wasi-sdk-release.json`.
`tools/build_wasm.py` writes `local/build/thug-core.wasm` and its build manifest.
It links thirteen SDK math objects for sine, cosine, atan2 and logarithms; their hashes are recorded
and their notices are retained in `third_party/`. These platform routines are not
recovered game functions and do not introduce browser runtime imports.
Collision structures intentionally retain the PC's 32-bit pointer layout and
cannot be compiled directly for a 64-bit native host.

For the browser checks, run `python3 tools/serve_validation.py`, then open the
loopback URL it prints. The server exposes only the validation page, test modules,
and listed fixtures. The page runs the same comparison code as Node. Browser
evidence is saved in `local/validation/collision-browser.json`.

Existing x86 fixtures can be replayed against a new WebAssembly build without
rerunning the original instructions. The browser page does this for every listed
subsystem. The latest browser report pins the current module, sources, fixtures and
checker files. Individual oracle reports retain the module hash from their own
generation run; an older hash there does not describe the latest browser replay.

`tools/collision_callback_fixture.c` is explicitly new test instrumentation, not
recovered gameplay. Its separate WebAssembly module shares the engine's memory
and is inserted into the exported function table. The x86 oracle uses a callback
hook with the same recording and mutation operations. This verifies dispatch,
call order, result contents, and rollback while testing the production engine
module unchanged; it does not verify the game's actual hit callbacks.

`tools/probe_callback_fixture.c` likewise instruments probe-level callbacks. It
records each complete probe and can change result fields, selection mode, the
probe's segment, or its cache. This checks that the original probe's local segment
and cache snapshots survive callback mutations. The reference-list helpers run as
recovered code on both sides; their effects are compared across all owner and
reference bytes.

`tools/memory_fixture.c` supplies the loader tests with a deterministic allocator,
also in a separate module sharing engine memory. The x86 heap hooks use the same
addresses and poison bytes. These checks compare allocation sizes, routes, order,
temporary-heap scope changes, release calls, and preserved bytes. Allocation failure
and the original PC memory manager are outside this test. The internal loader must
receive a validated version-10 collision file and must only relocate it once;
`tools/collision_file.py` provides host-side format validation.

### Floating-point fidelity

The device-creation instructions at `004d7cc0`–`004d7cd6` pass flags `0x24` or
`0x44`, without `D3DCREATE_FPU_PRESERVE`. Microsoft's
[Direct3D documentation](https://learn.microsoft.com/en-us/windows/win32/direct3d9/d3dcreate)
says this selects single precision with round-to-nearest. Geometry tests therefore
set the x86 control word to `0x007f`; C is built without floating-point contraction
or fast-math. Every training normal matches exactly in that mode.

This is evidence from the code and API contract, not an observed control word from
a running game. Full-game reference runs are still needed. WebAssembly's float
exponent range also differs from x87's; the checks establish fidelity for this
training mesh, not for arbitrary extreme or invalid numeric inputs. Synthetic
triangle tests include nonfinite inputs, but compare NaN outputs only by
classification; WebAssembly does not guarantee preservation of x87 NaN payloads.

Surface classification has an additional limit: [Unicorn 2.1.4's FSIN helper](https://github.com/unicorn-engine/unicorn/blob/2.1.4/qemu/target/i386/fpu_helper.c#L910)
uses host double-precision sine and leaves infinite inputs unchanged. Consequently,
matching that oracle does not independently establish the accuracy of real x87
transcendental instructions. [Intel's instruction reference](https://www.intel.com/content/dam/www/public/us/en/documents/manuals/64-ia-32-architectures-software-developer-vol-2a-manual.pdf)
specifies invalid-operation for infinite FSIN inputs; masked exceptions yield NaN.
Ten infinite-angle cases are checked against that documented behavior, with three
differences from the retained, unmodified emulator results explicitly recorded.
All other classification comparisons pass. The range includes quarter-degree
steps from -360 to 360, adjacent float normals, tiny subnormal angles, large angles,
NaNs and signed integer script values. `src/platform/math.c` preserves the x87
24-bit significand rounding without forcing its exponent into float32, avoiding
the underflow found in an initial implementation. The sine adapter still requires
validation against a running game on x86 hardware before claiming hardware parity.

Axis-angle tests exercise finite angles and NaNs, zero/large/tiny/nonfinite axes,
and 885 composed rotations. The original FSIN/FCOS instructions are compared with
the static SDK sine/cosine adapter through Unicorn; they do not establish physical
x87 transcendental accuracy. The ground checks compare 949 NaN fields by
classification. Their matrix multiply uses MXCSR `0x1f80` (round-to-nearest,
without denormal flushing); its value and the CPU dispatch choice have not been
observed in a running game. Timer checks use positive finite frame rates from
0.5 to 1,000 and test counter wrap and several scale values, not arbitrary rates.

The pair getter has a separate emulator limit. The original uses FLD/FSTP to copy
its coordinates. Intel's [instruction reference](https://www.intel.com/content/dam/www/public/us/en/documents/manuals/64-ia-32-architectures-software-developer-vol-2a-manual.pdf)
and [NaN rules, section 4.8.3.5](https://www.intel.com/content/dam/www/public/us/en/documents/manuals/64-ia-32-architectures-software-developer-vol-1-manual.pdf)
require signaling NaNs to become quiet when invalid-operation exceptions are
masked. The port explicitly sets that bit. The pair checks include 132 NaN output
words; Unicorn retains the signaling bit in 76 of them. Those 76 differences are
listed individually in `local/validation/stats.json`, retaining the raw oracle
words and checking the port against the documented result. The other pair bytes
match exactly, including overlapping copies. The stat numeric checks compare
1,501 NaN returns by classification. No x87 exception-status or hardware-parity
claim is made by these tests.

Signed-angle calculation adds an explicit math-library limit. The original CRT
acos entry (`00623630`) retains PC=24 for `(1+x)*(1-x)` and its square root, then
uses FPATAN. The port preserves those arithmetic steps and supplies the final
transcendental through the pinned SDK atan2. [Unicorn's FPATAN implementation](https://github.com/unicorn-engine/unicorn/blob/2.1.4/qemu/target/i386/fpu_helper.c#L715)
uses its host atan2. In 175 of 1,024 standalone angle cases, these differ by one
double-precision ULP; every result rounds to the same float. The checker bounds
and records each difference, and checks the adapter on the original recorded
acos input. Complete slope-turn and resistance state comparisons use no numeric
tolerance, only NaN classification (3,030 fields across the suite).

The x86 angle checks execute the original CRT math and error paths, supplying only
Windows GetLastError, SetLastError and an initialized TLS lookup. Domain errors
reach the real CRT errno store; the port's single-threaded math adapter preserves
that value. Physical x87 transcendental accuracy, exception-status behavior and
custom CRT error handlers are not verified. The adapter is platform support,
not another recovered game function.

The wall-turn suite reaches an additional FSIN/FCOS infinity case when an aliased
output overflows during the first matrix rotation and is reread by the second.
Read-only hooks record the original argument and destination at each matrix call;
they do not replace instructions or change machine state. In 44 cases, 76 such
calls require 608 matrix words to be NaNs under
[Intel's masked-invalid rules (Vol. 1, table 8-10)](https://cdrdv2-public.intel.com/868137/325462-089-sdm-vol-1-2abcd-3abcd-4.pdf).
The unmodified emulator differs in 108 of those words. Both its raw outputs and
every difference are retained; only the two mathematically affected rows receive
this specification-based check. All other fields compare with the original oracle,
with 13,174 NaN fields compared by classification. The suite also executes the
original CRT error path 26 times. It does not establish physical x87 accuracy or
exception-status parity.

The LZSS function intentionally retains the original unchecked buffer behavior.
Callers must validate the stream and output capacity. Its original global dictionary
has been lifted into an explicit state argument; the final 18 bytes persist between
calls. `tools/prx.py` is new host analysis tooling with input bounds checks, not
recovered engine source.

## Ghidra project

The saved project is `local/ghidra-projects/THUG2.gpr`. Local Ghidra 12.1.4 and JDK
21 are in `.tools/`; their archives were checked against official release hashes.
Ghidra's bundled native decompiler source was built for this Mac's ARM processor.

To export another function and its immediate callees, append hexadecimal addresses:

```sh
python3 tools/ghidra_headless.py -process THUG2.exe -noanalysis \
  -postScript ExportThugAnalysis.java local/ghidra-export local/analysis/symbols.tsv \
  49cbb0 4169c0 416000
```

The script always includes the initial checksum, script, and level-loading roots.
Its output is explicitly marked as unvalidated pseudocode. Inferred types and
calling conventions need checking against the instructions before reuse.

## Next recovery targets

The first playable milestone remains the original training level, with the game's
skater movement, collision, tricks, and camera. Required work includes:

1. Recover archive and level-loading behavior, including archive precedence and
   language patches. Anchors: `005b75a0`, `005b7c00`, `00445130`, `004b36d0`.
2. Finish collision loading and assemble the scene query used by the skater.
   BSP relocation/querying, vertex/normal decoding, and segment/triangle
   intersection, hit filtering/selection, and static-object testing are verified.
   The static scene query, grid candidate collection, and cache consumption are
   also verified, along with the collision-file loader (`0049cbb0`) and original
   grid builder (`00418440`, `00418bd0`). The probe wrapper `004172f0`, rigid
   moving-object test `00414460`, and moving-scene query `004118c0` are now
   recovered too. Still needed: scene-load wrapper `0049d590` and render-sector
   binding, cache construction, other collision classes such as the scaled
   object test `00413ff0`, and the remaining probe lifecycle.
3. Recover the script runtime and the skater/camera update paths reached by this
   level. Script parameter access, skater friction/drag, nearby-obstacle queries
   (`005009c0`) and forward-obstruction queries (`004fd660`) are recovered.
   Surface classification (`005003a0`) is recovered with the math limits above.
   The up-vector change (`004fe860`) and its matrix repair (`00405170`) are also
   recovered. Parameter-set selection (`005802e0`), numeric lookup (`00580400`)
   and configured drag (`004fe6a0`) are now recovered as a complete call chain.
   Stat-dependent skating parameters (`00580790`, `005805b0`, `00580490`) and
   their object lookup, pair/structure access, game settings and modifier reads
   are now recovered and verified as another complete call chain.
   The downward ground update (`00504b40`), timer reads (`0044ece0`, `005be970`),
   axis-angle rotation (`00404c60`, `00405950`) and SSE matrix multiply are now
   recovered too. The grounded update (`0050ee70`) is now recovered through
   its complete call chain, as is the airborne caller (`0050ca00`).
   Braking/acceleration selection and application (`004fe320`, `004fe420`,
   `004fe490`, `004fe530`, `005019e0`), velocity alignment (`004ff590`) and gravity
   (`004ff470`) are now recovered and verified. The complete resistance wrapper
   (`00506df0`), slope-turn dependency (`00501b00`), plane projection and signed
   angle are recovered too, with the numeric limits above. Four-way obstacle
   repulsion (`005055b0` / `00501c90`) and low-speed side correction (`00503b30`)
   now run their complete recovered call chains. Wall-tangent turning (`005039f0`)
   and the heading approximation (`00403ef0`) are recovered too. Node lookup,
   unnamed-flag traversal, the multiplayer event gate and collision owner accessors
   are verified prerequisites for collision-event handling. The movement sweep
   (`00506e50`) is now recovered through actual collision, event dispatch and wall
   response. Moving-contact transport, acquisition/release, relative-velocity
   adjustment and saved-probe assignment are also recovered. Orientation blending,
   state-mode/material setters, object broadcasts and complete floor-transition
   preparation (`004feba0`) are now recovered too. Ground steering (`00503560`),
   backward-motion response (`004ff920`) and input release (`004ffb10`) now run
   their complete recovered call chains. Moving attachment interaction
   (`00501db0`) and its projected point lookup/provider chain are also recovered.
   Objective lookup, availability and state/parameter access are recovered too.
   Complete base/event objective activation is now recovered through score/UI
   reset, parent lifecycles and QB scripts. Manager activation and the actual
   native start/stop/clear commands now execute through the script interpreter.
   Complete goal wins, rewards, unlocks, parent marking and native WinGoal now
   execute through real script, progress and network effects. Goal-flag updates,
   event notifications and the complete skating-state change (`004fded0`) now
   execute through their real dependencies. The complete side correction chain
   (`0050c930` through `0050a2c0` and `00508140`) is now recovered too.
   Transfer search (`00502240`) and complete application (`00502f20`) now
   execute through their collision-cache, matrix and script/event dependencies.
   Complete floor handling (`00509bd0`) and alternate transfer/transition exit
   (`004fee10`, `00505f70`, `00507120`), balance (`00579cc0`) and the complete
   grounded update (`0050ee70`) are now recovered too. The complete airborne
   update (`0050ca00`) now passes through movement, collision, transfer and score/UI
   paths. Complete rail entry (`0050a770`), rail acquisition (`0050dae0`) and
   wallriding (`0050f830`), Natas (`00504730`), rail transition (`0050c200`), full
   rail state (`0050ddf0`) and all six states of the movement dispatcher (`00510830`)
   are now recovered too. Physics initialization/linking, wait cleanup, reset
   helpers and the enclosing object update loop are integrated. Base/physics
   component lifecycles and node-movement commands are now integrated too, with
   scoped host services for startup and nested QB calls. Jump, its sound and steering
   helpers, descriptor registration and 65 additional physics commands are integrated.
   Sixteen further physics commands pass in an isolated build. A separate recovery
   of `Change`, the skeleton parser, asset class, asset factory and `LoadSkeleton`
   now lets the unchanged `TR_startup` script finish in an experimental browser
   build. All 58 extracted skeletons pass the asset/parser comparisons. The script
   loads its 34-bone prop through resident-file services. Production file/archive
   access, cold boot and the separate `TR_Setup` scene initialization remain.
   Other required work includes remaining physics members, other component
   classes and Motion frame updates, camera updates, actual level scripts/native
   handlers, derived objective types and overall engine integration. The complete rebound branch
   (`004ff670`) now runs the recovered event system and its vector/scalar callees;
   the complete wall response (`005059d0`) is now recovered and verified through
   its real second probe, impact sound and synchronous script paths.
   Material/event lookup, impact/weighted selection, descriptor construction,
   volume state and loaded-asset distance lookup are now recovered. Spatialization (`0047be10`) and nearest-listener selection
   (`004a09e0`) are now recovered too, along with slot/ID management, voice
   parameter preparation, asset volume/pitch scaling and direct viewport camera
   access. Device-buffer playback (`0047d130`), volume/pan/frequency updates
   (`0047cd70`), their math prerequisites and the playback parent (`0047bd20`)
   are now recovered through the OS device boundary. The dispatcher (`00444bb0`)
   and component wrapper (`00518dd0`) are now recovered through actual message
   queuing, attenuation and playback too. Their enclosing wall response is now
   verified. Audio initialization, asset loading and the browser audio backend
   remain.
   Collision-event setup (`00434a60`)
   and probe dispatch (`00434bf0`) now run the recovered wrappers `00461480`,
   `00475420` and `00473420` around the executor. Their actual native gameplay
   commands and object-specific node providers still need recovery to run a level. The script instance constructor (`004738e0`), wait
   update (`00473050`) and jump/random-token resolver (`00470c60`) now run as
   recovered code. Script setup (`00474540`), cleanup (`00473a80`), command
   invocation (`00474b40`), call-stack push (`004748e0`), deferred cleanup
   (`00473880`), immediate calls (`00475750`) and the executor (`004750b0`) are
   now recovered and verified together. Their structure/component ownership,
   insertion, copying and
   merging prerequisites now run as recovered code, along with typed parameter
   construction, member lookup, argument snapshots, bytecode boundary helpers and
   random-range values. Expression value operations and the complete expression
   evaluator are now recovered too, as are the mutually recursive parameter,
   structure, array and value parsers and their expression-token integration.
   Global value registration, symbol linking/lookup/iteration/disposal and script
   body checksums are now recovered too. The LZSS encoder and its complete tree
   helpers are also recovered and verified. Compressed-script registration, bytecode
   preparation, cache acquisition/release/eviction/reload, their fixed pools and lookup
   helpers are now recovered too. The complete two-pass QB-buffer loader (`00472420`),
   its name maps and reversible definition journal are also recovered and verified
   with all eight archived training files. Loop begin/repeat/break, nested-switch
   selection/skipping and script-return restoration are now recovered and verified
   too. Failed-setup event cleanup (`00473010`) and its concrete unsubscription,
   lookup iteration, listener destruction and parameter-disposal callees are also
   recovered, including both virtual deleting destructors. Recursive script execution
   is also verified, through compressed registration, cache decoding, stack spill,
   waits, returned values and cleanup. Complete instance destruction, owner stopping,
   finished-instance collection and the execute/copy/dispose wrapper (`004752f0`)
   are now recovered and verified too. Compact parameter serialization (`00479e20`)
   and its recursively nested array encoder (`00479b80`) now execute their complete
   call chains with real compression tables and archived training values. The full
   message-enqueue chain (`00457eb0`) needed by dispatch is recovered and verified
   too, including compression, shared ownership and concrete virtual node cleanup.
   Frame scheduling, synchronous dispatch, script spawning and collision-event
   wrappers are now recovered and verified too. General object-event delivery,
   radius-filtered broadcasts, event waits, handler replacement/interruption and
   reentrant event-table lifetime are now recovered and verified as well. Next are the remaining movement
   branches and actual native/virtual gameplay
   handlers and node providers. Runtime startup,
   archive/file I/O integration and native-binding relocation also remain.
   Clock production, other matrix dispatch backends and additional component
   dependencies remain. Preserve real game behavior with differential tests.
4. Build an executable engine subset, then add browser rendering, input, asset
   loading, timing, and sound adapters and validate it against a reference run.

MSVC 13.10.3077 reproduces eight complete native function bodies with `/O2 /Gy`.
Exact project-wide compiler settings, library provenance and a complete PE link
remain unverified; see [the native trial](matching/README.md).

Guidance: [Decompedia](https://decomp.wiki/) and
[Snail Mail recovery article](https://banteg.xyz/posts/snail-mail/).
Game binaries, extracted assets, generated analysis, and downloaded tools stay
under the ignored `local/` and `.tools/` directories.
