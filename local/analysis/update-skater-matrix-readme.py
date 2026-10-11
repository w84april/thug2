from pathlib import Path
import json
p=Path('local/analysis');c=json.loads((p/'skater-matrix-checkpoint.json').read_text())
assert c['browser_suites']==133 and c['new_cases']==355
f=Path('README.md');s=f.read_text();old='- The latest experimental build advances the original skater constructor\n'
assert s.count(old)==1
s=s.replace(old,'- The preceding experimental build advances the original skater constructor\n',1)
s=s.replace('- The preceding experimental build begins the original skater constructor:', '- An earlier experimental build begins the original skater constructor:',1)
new='''- The latest experimental build recovers SkaterMatrixQueries: all eight
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
'''
s=s.replace('## Current evidence\n\n','## Current evidence\n\n'+new,1);f.write_text(s)
