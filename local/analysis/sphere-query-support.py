"""Fixture ABI for complete sphere queries, with no substituted game callees."""
import json,struct
from collections import Counter
from unicorn.x86_const import UC_X86_REG_FPSW,UC_X86_REG_FPTAG
from script_heap_oracle import ScriptHeapOracle
from specimen import ROOT,SHA256
P=ROOT/'local/analysis';Q=0x1ff0000
FUNCTIONS={
 '0x48c940':{'name':'thug_collision_first_grid_draft','this':False,'result':'word','stack_args':[],'cleanup':0},
 '0x4110b0':{'name':'thug_static_collision_sphere_draft','this':True,'result':'byte','stack_args':[0,1,2],'cleanup':12,'pointer_args':[3]},
 '0x410240':{'name':'thug_collision_scene_sphere_draft','this':False,'result':'byte','stack_args':[0,1,2],'cleanup':0,'pointer_args':[3]},
 '0x418300':{'name':'thug_sphere_probe_query_draft','this':True,'result':'byte','stack_args':[0],'cleanup':4,'pointer_args':[1]}}
RANGES={0x48c940:56,0x4110b0:631,0x410240:1137,0x418300:42}
OBSERVE=[*RANGES,0x416320,0x4160e0,0x40b2d0,0x40f9e0,0x40ec90,0x403410,0x403450,0x40b1d0,0x418710,0x48c980,0x4188c0,0x410c70]
def patch(at,fmt,*v):return [at,struct.pack(fmt,*v).hex()]
def words(at,*v):return patch(at,'<'+'I'*len(v),*v)
def floats(at,*v):return patch(at,'<'+'f'*len(v),*v)
class Queries:
 def __init__(self,initial,base,scene,pointer_fields):
  self.initial=bytes(initial);self.base=base;self.pointer_fields=pointer_fields;self.labels=[];self.outcomes=Counter()
  self.globals=[];self.defaults=[]
  def add(name,at,values,width=4):
   start=len(self.globals)
   for i,value in enumerate(values):self.globals.append([name,at+i*width,width,i*width]);self.defaults.append(value)
   return start
  self.scene_index=add('thug_collision_scene_list',0x6fa7ec,[scene])
  add('thug_collision_selected_scenes',0x6fa738,[0xaaaa0000+i for i in range(16)])
  add('thug_collision_selected_grids',0x6fa778,[0xbbbb0000+i for i in range(16)])
  add('thug_collision_grid_output',0x691998,[0xcccc0000+i for i in range(2048)])
  self.stamp_index=add('thug_collision_grid_stamp',0x693998,[17],1)
  self.cache_index=add('thug_sphere_default_cache_draft',0x691990,[0])
  add('thug_sphere_query_fixture_state',0x691968,[base+0x800,0x12345678,0x87654321])
  add('thug_collision_fallback_indices',0x67c6b8,[2*i|((2*i+1)<<16) for i in range(1024)])
  self.oracle=ScriptHeapOracle(initial,base,base+32,base+256,self.globals,self.defaults,FUNCTIONS,observe=OBSERVE,instruction_limit=12000000)
 def check(self,calls,patches,label,changes=None):
  cpu=self.oracle.cpu;cpu.reg_write(UC_X86_REG_FPSW,0);cpu.reg_write(UC_X86_REG_FPTAG,0xffff)
  try:steps=self.oracle.case(calls,patches,changes)
  except Exception:print('Failed',len(self.labels),label,flush=True);raise
  self.labels.append(label);self.outcomes[str(steps[-1]['result'])]+=1
  if len(self.labels)%100==0:print('Original sphere queries',len(self.labels),flush=True)
  return steps
 def save(self,name,scope,extra=None):
  fixture={'base':self.base,'memory':name+'-memory.bin','globals':self.globals,'functions':FUNCTIONS,
   'pointer_exports':[[Q,'thug_sphere_query_fixture_state'],[0x645c18,'thug_static_collision_methods']],
   'pointer_fields':self.pointer_fields,'float_fields':[],'cases':self.oracle.cases,'case_labels':self.labels,'scope':scope}
  (P/fixture['memory']).write_bytes(self.initial);(P/(name+'-fixtures.json')).write_text(json.dumps(fixture,separators=(',',':')))
  report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(self.labels),'calls':sum(self.oracle.counts.values()),
   'counts':dict(self.oracle.counts),'callees':dict(self.oracle.coverage),'heap_events':dict(self.oracle.heap_events),'outcomes':dict(self.outcomes),
   'scope':scope,'playable':False,**(extra or {})}
  assert not report['heap_events']
  (P/(name+'-original.json')).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
