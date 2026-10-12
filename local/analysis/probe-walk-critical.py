"""Original critical-point offset recovery, real collision and diagnostic arguments."""
from pathlib import Path
source=Path('local/analysis/probe-walk-common.py').read_text().split('for state,offset,rate')[0]
exec(compile(source,'<preserved common Walk graph>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x5278d0,772,'thug_walk_critical_point_draft',0,'void',False,True,True)]
for row in specs:
 bind_new(*row);oracle.cpu.hook_add(UC_HOOK_CODE,observe_cache,begin=row[0],end=row[0])
DLOG=P+0x1a000
extra={**extra,'native_callbacks':[*[x for x in extra.get('native_callbacks',[]) if DIAG+4 not in x.get('slots',[])],{'module':'walk-critical-diagnostics.wasm','export':'fixture_walk_critical_print','slots':[DIAG+4]}]}
def critical_debug(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);fmt=bytes(cpu.mem_read(oracle.word(sp+4),64)).split(b'\0')[0]
 count=oracle.word(DLOG);assert count<32;oracle.setword(DLOG,count+1);row=bytearray(192);row[:len(fmt)]=fmt
 file=bytes(cpu.mem_read(oracle.word(sp+8),32)).split(b'\0')[0];assert file==b'mponents\\WalkComponent.cpp'
 row[64:64+len(file)]=file;row[188:192]=cpu.mem_read(sp+12,4)
 if fmt.startswith(b'D:'):
  assert fmt in [b'D:%s:%i: required_pos_adjustment = %g, %g, %g\n',b'D:%s:%i: m_critical_point_offset = %g, %g, %g\n']
  row[96:120]=cpu.mem_read(sp+16,24)
 else:
  assert fmt==b'M:%s:%i: %s\n';message=bytes(cpu.mem_read(oracle.word(sp+16),88)).split(b'\0')[0];assert message==b'adjusting position due to bad critical point';row[96:96+len(message)]=message
 cpu.mem_write(DLOG+16+192*count,bytes(row))
 if oracle.word(DLOG+4):oracle.setword(oracle.word(DLOG+4),oracle.word(DLOG+8))
 cpu.reg_write(UC_X86_REG_EAX,0xffffffff);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
debug.__code__=critical_debug.__code__
class CriticalGraph(CommonGraph):
 def __init__(self):
  super().__init__();self.put(P+0x18,'<I',0);self.put(P+0x24,'<4f',0,0,0,1);self.put(P+0x68,'<4f',0,0,-4,1)
  self.put(DIAG,'<I',DLOG);self.image[DLOG-BASE:DLOG-BASE+16+32*192]=bytes(16+32*192)
for state,offset,dt in itertools.product([0,1,2,3,4,0xffffffff],[(0,0,0,1),(0,0,8,1),(.3,.4,0,1),(-3,-4,5,-1),(1e-30,0,0,1)],[0,.0005,.002,1]):
 g=CriticalGraph();g.put(P+0x18,'<I',state);g.put(P+0x71c,'<4f',*offset);g.put(P+0x80,'<f',dt)
 g.run([call(0x5278d0,P,[Q])]*2,f'critical decay/{state}/{offset}/{dt}')
records=[]
for shape,dt,plane in itertools.product(['wall','moving wall','floor','moving floor'],[0,.001,.02],[False,True]):
 g=CriticalGraph();g.put(P+0x71c,'<4f',0,0,8,1);g.put(P+0x80,'<f',dt)
 if 'wall' in shape:g.obstacle('z',5,moving=shape.startswith('moving'))
 else:
  g.put(P+0x71c,'<4f',0,8,0,1);g.put(P+0x68,'<4f',0,-4,0,1);g.plane(5,moving=shape.startswith('moving'),up=False)
 if plane:g.put(P+0x18b0,'<B',1);g.put(P+0x18b4,'<5f',.6,0,.8,1,0)
 g.run([call(0x5278d0,P,[Q])]*2,f'critical collision/{shape}/{dt}/{plane}')
 records.append({'shape':shape,'duration':dt,'plane':plane,'diagnostics':oracle.word(DLOG)})
scope='Candidate for full critical-point displacement decay, real static/moving collision correction, limiting plane and original diagnostics. Shared walking frame remains unfinished; not playable.'
saved=coverage.copy();coverage.clear();finish('walk-critical',scope,{},extra);coverage.update(saved)
report=json.loads((folder/'walk-critical-original.json').read_text());report['collision_records']=records;report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
(folder/'walk-critical-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n')
(folder/'walk-critical-original.json').write_text(json.dumps(report,indent=2)+'\n');print(report['instruction_coverage']);print(records)
