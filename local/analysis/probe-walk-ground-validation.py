"""Original ground/shadow validation with the already recovered light methods."""
from pathlib import Path
exec(compile(Path('local/analysis/probe-walk-transfer.py').read_text().split('records=[]')[0],'<preserved Walk transfer graph>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x527080,921,'thug_walk_validate_ground_draft',0,'void',False,True,True)]
for row in specs:
 bind_new(*row);oracle.cpu.hook_add(UC_HOOK_CODE,observe_cache,begin=row[0],end=row[0])
LIGHTLOW,LIGHTHIGH,LIGHTFACTOR,LIGHTCOLOR,MODELLIGHTFACTOR=P+0x22000,P+0x22100,P+0x22200,P+0x22300,P+0x22400
LIGHT,RENDER,SHADOW=P+0x22500,P+0x22600,P+0x22700
DLOG=P+0x23000
template=json.loads((folder/'skater-ground-fixtures.json').read_text())
pointer_defaults={'thug_light_direction_colors_draft':LIGHTCOLOR,'thug_light_lower_factors_draft':LIGHTLOW,'thug_light_upper_factors_draft':LIGHTHIGH,'thug_light_factors_draft':LIGHTFACTOR}
for row,value in zip(template['globals'],template['cases'][0]['globals']):
 name,at,width,offset=row
 if not (name.startswith('thug_light_') or name=='thug_model_light_factor_count_draft'):continue
 value=pointer_defaults.get(name,value)
 if at not in index:glob(name,at,value,width,offset)
 else:
  assert globals_[index[at]][0]==name;defaults[index[at]]=value
if not any(x[0]==0x64a440 for x in exports):exports.append([0x64a440,'thug_model_light_methods_draft'])
def validate_debug(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);fmt=bytes(cpu.mem_read(oracle.word(sp+4),64)).split(b'\0')[0]
 file=bytes(cpu.mem_read(oracle.word(sp+8),32)).split(b'\0')[0];message=bytes(cpu.mem_read(oracle.word(sp+16),88)).split(b'\0')[0]
 assert (fmt,file,message)==(b'M:%s:%i: %s\n',b'mponents\\WalkComponent.cpp',b'applying uber frig')
 count=oracle.word(DLOG);assert count<32;oracle.setword(DLOG,count+1);row=bytearray(192);row[:len(fmt)]=fmt;row[64:64+len(file)]=file;row[96:96+len(message)]=message;row[188:192]=cpu.mem_read(sp+12,4)
 cpu.mem_write(DLOG+16+192*count,bytes(row))
 if oracle.word(DLOG+4):oracle.setword(oracle.word(DLOG+4),oracle.word(DLOG+8))
 cpu.reg_write(UC_X86_REG_EAX,0xffffffff);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
debug.__code__=validate_debug.__code__
class ValidationGraph(TransferGraph):
 def __init__(self,local=True,state=0,depth=1):
  super().__init__();self.symbol(0x801c9cb6,2,bits(depth))
  self.put(P+0x1788,'<I',STATE);self.put(P+0x18,'<I',state);self.put(P+0x24,'<4f',0,4,0,1);self.put(P+0x68,'<4f',10,5,6,1);self.put(P+0x71c,'<4f',0,0,0,0)
  self.put(P+0x34,'<4f',2,0,3,1);self.put(P+0x44,'<f',4);self.put(P+0x48,'<4f',.6,0,.8,1)
  self.put(OBJ+0x100,'<I',SHADOW);self.image[SHADOW-BASE:SHADOW-BASE+0x40]=bytes(0x40);self.put(SHADOW+4,'<I',0x8a897dd2)
  self.image[LIGHT-BASE:RENDER-BASE+0x48]=bytes(RENDER-LIGHT+0x48);self.put(LIGHT,'<I',0x64a440);fields.add(LIGHT);self.put(LIGHT+8,'<3fI',.4,.2,.8,MODELLIGHTFACTOR)
  self.put(MODEL+0x208,'<I',RENDER);self.put(RENDER+0x2c,'<I',LIGHT if local else 0)
  for i in range(31):
   self.put(LIGHTLOW+i*4,'<f',.1+i*.07);self.put(LIGHTHIGH+i*4,'<f',.15+i*.12);self.put(LIGHTFACTOR+i*4,'<f',.25+i*.01);self.put(MODELLIGHTFACTOR+i*4,'<f',.75+i*.02);self.put(LIGHTCOLOR+i*4,'<4B',i*8,255-i*3,i*7,0xaa)
  self.put(DIAG,'<I',DLOG);self.image[DLOG-BASE:DLOG-BASE+16+32*192]=bytes(16+32*192)

records=[]
for shape,local,state in itertools.product(['empty','ground','moving ground','two surfaces','light only','moving both','moving light above','moving excluded light'],[False,True],[0,1]):
 g=ValidationGraph(local,state)
 if shape!='empty':g.plane(8 if shape=='moving light above' else 0,moving=shape.startswith('moving'),flags=0x30 if shape=='moving excluded light' else 0x20 if shape in ['light only','moving both','moving light above'] else 0)
 if shape=='two surfaces':g.plane(8,moving=False,flags=0x20)
 stages=g.run([call(0x527080,P,[Q])]*2,f'ground validation/{shape}/{local}/{state}')
 records.append({'shape':shape,'local_light':local,'state':state,'diagnostics':oracle.word(DLOG),'final_state':oracle.word(P+0x18)})
 print(records[-1],flush=True)
for moving,height,depth,offset in itertools.product([False,True],[-8,-7.999,0,4,5,5.001,8],[0,1,3],[(0,0,0,0),(1,2,3,1)]):
 g=ValidationGraph(depth=depth);g.plane(height,moving=moving,flags=0x20);g.put(P+0x71c,'<4f',*offset)
 stages=g.run([call(0x527080,P,[Q])],f'ground ray height/depth/offset/{moving}/{height}/{depth}/{offset}')
 records.append({'moving':moving,'height':height,'depth':depth,'offset':offset,'diagnostics':oracle.word(DLOG)})
for state,mutation in itertools.product([0,1,2,4],['none','previous position','velocity','facing']):
 g=ValidationGraph(state=state)
 at,value={'none':(0,0),'previous position':(P+0x68,bits(99)),'velocity':(P+0x34,bits(-7)),'facing':(P+0x48,bits(-.25))}[mutation]
 g.put(DLOG+4,'<2I',at,value)
 g.run([call(0x527080,P,[Q])]*2,f'ground fallback diagnostic/live state/{state}/{mutation}',{0x7d1ec8:0xffffffff,0x696d60:1})
 assert oracle.word(P+0x18)==0 and oracle.word(DLOG)==2
scope='Candidate complete ground validation with real first/secondary surface queries, local/global light adjustment, shadow writes and missing-ground fallback. Full shared ground frame and playable training remain unfinished.'
extra={**extra,'pointer_globals':sorted(set(extra.get('pointer_globals',[])+[index[0x6918ec+i*4] for i in range(8)])),
 'native_callbacks':[{'module':'walk-critical-diagnostics.wasm','export':'fixture_walk_critical_print','slots':[DIAG+4]}]}
saved=coverage.copy();coverage.clear();finish('walk-ground-validation',scope,{},extra);coverage.update(saved)
report=json.loads((folder/'walk-ground-validation-original.json').read_text());report['records']=records
report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
(folder/'walk-ground-validation-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n')
(folder/'walk-ground-validation-original.json').write_text(json.dumps(report,indent=2)+'\n');print(report['instruction_coverage'])
