"""Original-only first-frame exploration after all31 actual prop constructions."""
from pathlib import Path
source=Path('local/analysis/trace-rigidbody-initialize-training.py').read_text().split("f=json.loads((folder/'level-collision-load-fixtures.json')")[0]
assert '.write_text(' not in source
exec(compile(source,'<preserved isolated fullscene platform setup>','exec'))
if 0x684fc8 in index:defaults[index[0x684fc8]]=0x3f800000
else:glob('thug_frame_length_scale',0x684fc8,0x3f800000)
functions['0x430e20']={'name':'UNRECOVERED_rigidbody_update','this':True,'result':'void','cleanup':0}
functions['0x45d920']={'name':'thug_object_update_components','this':True,'result':'void','cleanup':0}
prior=json.loads((folder/'rigidbody-initialize-training-fixtures.json').read_text())['cases'][0]['steps']
objects=json.loads((folder/'rigidbody-initialize-training-original.json').read_text())['objects']
rigids=[c['address'] for o in objects for c in o['components'] if c['type']==0xffb39248]
calls=[(int(s['fn'],16),s['this'],s['args']) for s in prior]
calls += [(0x430e20,p,[]) for p in rigids]
calls += [(0x45d920,o['object'],[]) for o in objects]
frame_hits=Counter();call_entries=[];frame_started=False;frame_returns=0
def record(cpu,at,size,user):
 global frame_started
 if at in [0x430e20,0x45d920]:
  frame_started=True;call_entries.append([hex(at),hex(cpu.reg_read(UC_X86_REG_ECX))]);print('FRAME',call_entries[-1],flush=True)
 if frame_started:frame_hits[at]+=1
cpu.hook_add(UC_HOOK_CODE,record,begin=0x42bb00,end=0x431240)
cpu.hook_add(UC_HOOK_CODE,record,begin=0x45d920,end=0x45da21)
read_players=[oracle.word(0x695150+i*12) for i in range(8)]
error=None;steps=[]
try:steps=oracle.case(calls)
except Exception as e:
 error=repr(e);print('STOP',error,'EIP',hex(cpu.reg_read(UC_X86_REG_EIP)),flush=True)
report={'result':'original exploration complete' if error is None else 'original exploration stopped','error':error,'eip':hex(cpu.reg_read(UC_X86_REG_EIP)),'requested_calls':len(calls),'returned_calls':len(steps),'frame_entries':call_entries,'original_initial_player_references':read_players,'executed_frame_instructions':{hex(a):n for a,n in sorted(frame_hits.items())},'recent_blocks':list(recent_blocks),'playable':False,'scope':'Original isolated instruction execution only. Actual31prop startup followed by19Rigidbody updates and31owner updates in an initialized scene without a constructed skater. No missing implementation or success is substituted.'}
(folder/'rigidbody-first-frame-exploration.json').write_text(json.dumps(report,indent=2)+'\n')
print('SAVED',report['result'],'entries',len(call_entries),flush=True)
if error:raise SystemExit(1)
