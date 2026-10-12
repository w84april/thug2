"""Exercise actual original base descriptor dispatch, including ignored trailing fields."""
from pathlib import Path
source=Path('local/analysis/probe-skater-walk.py').read_text().split('# Real original CRT')[0]
exec(compile(source,'<preserved isolated component oracle>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
bind(0x45d720,'thug_component_descriptor_virtual_probe_draft',3,'word',False,False)
exports.extend([[0x64bef0,'thug_local_net_pending_methods_draft'],[0x64bdb8,'thug_end_run_methods_draft']])
DESC=P+0x7000
names=[0x95bdcfcd,0x69a9e37f,0x4c58771e,0xafc6a7,0x962dea01,0xea77e667,0xb866bf9b,0,0xffffffff]
for table,kind in [(0x64bef0,0x7cd3e6d5),(0x64bdb8,0xb1d5a3e1)]:
 for name,member,adjust,flags in itertools.product(names,[0,0xdeadbeef],[0,0xffffffff],[0,3,0xffffffff]):
  g=WalkGraph();g.put(P,'<7I',table,kind,0,OBJ,0,0,flags);fields.add(P)
  g.put(DESC,'<4I',name,kind,member,adjust)
  g.run([call(0x45d720,P,[DESC,0,0])]*2,f'base descriptor {kind:x}/{name:x}/{member:x}/{adjust:x}/{flags:x}')
finish('skater-base-descriptor', 'Original base45d720 ignores descriptor words8/12 and calls the component checksum virtual. Test adapter invokes each concrete LocalNet/EndRun descriptor slot. Explicit nonzero unused member/adjustment fields distinguish the original base ABI from extended42bb20 dispatch. Both lifecycle tables corrected; zero new original routine count.',{}, {**extra,'function_exports':function_exports,'memory_fixture':'skater-walk-memory.wasm'})
