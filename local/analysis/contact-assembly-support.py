"""Exact fixture ABI for Rigidbody contact assembly and its real collision callees."""
import importlib.util,struct
from unicorn import UC_HOOK_CODE
from specimen import ROOT
spec=importlib.util.spec_from_file_location('sphere_query_support',ROOT/'local/analysis/sphere-query-support.py');s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
s.FUNCTIONS.clear();s.FUNCTIONS['0x42c950']={'name':'thug_rigidbody_collect_contacts_draft','this':True,'result':'byte','stack_args':[],'cleanup':0,'pointer_args':[0]}
class Assembly(s.Queries):
 def __init__(self,memory,base,scene,pointer_fields,moving):
  super().__init__(memory,base,scene,pointer_fields)
  def glob(name,at,values,width=4):
   for i,value in enumerate(values):self.globals.append([name,at+i*width,width,i*width]);self.defaults.append(value)
  glob('thug_rigidbody_contact_cache_draft',0x6939e0,[0xa5a5a5a5]*(0xfcc//4))
  glob('thug_rigidbody_collision_contacts_draft',0x6949b0,[0xa5a5a5a5]*(24*48//4))
  glob('thug_rigidbody_rotated_points_draft',0x694e30,[0]*(24*4))
  glob('thug_rigidbody_rotated_spheres_draft',0x694fb0,[0]*(24*4))
  glob('thug_moving_collision_list',0x691984,[moving])
  glob('thug_collision_default_cache',0x691974,[0])
  glob('thug_collision_select_farthest',0x691910,[0],1)
  self.global_index={g[1]:i for i,g in enumerate(self.globals)}
  for at in [0x42c950,0x402600,0x40aba0,0x417760,0x4172f0,0x4637e0,0x418330]:self.oracle.cpu.hook_add(UC_HOOK_CODE,self.oracle.observe,begin=at,end=at)
 def changes(self,points=(),spheres=(),extra=None):
  values={}
  for base,rows in [(0x694e30,points),(0x694fb0,spheres)]:
   for i,row in enumerate(rows):
    for j,value in enumerate(struct.unpack('<4I',struct.pack('<4f',*row))):values[self.global_index[base+i*16+j*4]]=value
  for at,value in (extra or {}).items():values[self.global_index[at]]=value
  return values
patch=s.patch;words=s.words;floats=s.floats;Q=s.Q
