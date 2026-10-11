"""Inspect actual registered GameObject parameters without changing the QB files."""
from pathlib import Path
s=Path('local/analysis/probe-training-prop-script.py').read_text().split('# Preparation')[0]
exec(compile(s,'<script setup>','exec'))
steps=oracle.case(prefix)
nodes=oracle.word(TABLE+0x1000c);items=oracle.word(nodes+8)
rows=[]
for row in json.loads((folder/'training-prop-components-original.json').read_text())['props']:
 node=oracle.word(items+row['index']*4);at=oracle.word(node+4);values=[]
 while at:
  kind=oracle.cpu.mem_read(at,1)[0]>>1;key=oracle.word(at+4);value=oracle.word(at+8);r={'key':hex(key),'kind':kind,'value':hex(value)}
  if kind in [3,4] and BASE<=value<BASE+len(memory):r['text']=bytes(oracle.cpu.mem_read(value,160)).split(b'\0')[0].decode('latin1')
  values.append(r);at=oracle.word(at+12)
 rows.append({'index':row['index'],'fields':values})
(folder/'training-prop-script-node-discovery.json').write_text(json.dumps(rows,indent=2)+'\n')
for row in rows:print(row['index'],[v for v in row['fields'] if v['key'] in ['0x286a8d26','0x9794932','0x2d7e583b','0xb990d003','0x81c98276']])
