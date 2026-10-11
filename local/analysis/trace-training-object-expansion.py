"""Find the next original training constructor dependency without substitutions."""
from pathlib import Path
source=Path('local/analysis/probe-training-model-transform.py').read_text().split('steps=oracle.case(prefix);array=')[0]
exec(compile(source,'<preserved full original training setup>','exec'))
steps=oracle.case(prefix);array=steps[-1]['result'];nodes=oracle.word(TABLE+0x1000c);items=oracle.word(nodes+8)
selected=[(i,oracle.word(items+i*4)) for i in [276,573,582,1233,1234]]
for node_index,node in selected:
 native_hits.clear();factory_hit.clear();active_model.clear();oracle.cases.clear()
 try:
  steps=oracle.case(prefix+[(0x468cb0,0,[node,1,0])]);obj=steps[-1]['result']
  print('COMPLETE',node_index,hex(obj),'flags',hex(oracle.word(obj+0x104)),'calls',dict(native_hits),flush=True)
 except Exception as error:
  print('STOP',node_index,'PC',hex(oracle.cpu.reg_read(UC_X86_REG_EIP)),'error',repr(error),'factory',factory_hit,'model',active_model,'calls',dict(native_hits),flush=True)
  if active_model:
   item=oracle.word(active_model['parameters']+4);params=[]
   while item:
    kind=oracle.cpu.mem_read(item,1)[0]>>1;value=oracle.word(item+8)
    text=bytes(oracle.cpu.mem_read(value,256)).split(b'\0',1)[0].decode('ascii',errors='replace') if kind in [3,4] else None
    params.append({'name':hex(oracle.word(item+4)),'kind':kind,'value':hex(value),'text':text});item=oracle.word(item+12)
   print('PARAMETERS',params,flush=True)
  raise
