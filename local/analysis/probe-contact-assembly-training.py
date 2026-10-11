"""Original initialized training props against the actual training collision grid."""
import hashlib,importlib.util,json,struct
from collections import Counter
from unicorn import UC_HOOK_CODE
from specimen import ROOT
spec=importlib.util.spec_from_file_location('contact_support',ROOT/'local/analysis/contact-assembly-support.py');s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
p=ROOT/'local/analysis';prior=json.loads((p/'sphere-query-checkpoint.json').read_text());sha=lambda data:hashlib.sha256(data).hexdigest();sources={}
def read(name):
 path=p/name;data=path.read_bytes();key=str(path.relative_to(ROOT));assert sha(data)==prior['artifact_hashes'][key];sources[key]=sha(data);return data
source_fixture=json.loads(read('motion-rotation-training-fixtures.json'));source_base=source_fixture['base'];source=bytearray(read(source_fixture['memory']))
for case in source_fixture['cases']:
 for at,text in case['patches']:source[at-source_base:at-source_base+len(text)//2]=bytes.fromhex(text)
 for step in case['steps']:
  for at,text in step['outputs']:source[at-source_base:at-source_base+len(text)//2]=bytes.fromhex(text)
objects=json.loads(read('rigidbody-initialize-training-original.json'))['objects']
training=json.loads(read('sphere-query-training-original.json'));fixture=json.loads(read('sphere-query-training-fixtures.json'));BASE=fixture['base'];memory=bytearray(read(fixture['memory']))
memory.extend(b'\xa5'*(0xe8000-len(memory)));MOVING=BASE+0xbc000
struct.pack_into('<I',memory,MOVING-BASE+4,0xffffffff)
components=[];relocations=[]
for obj in objects:
 for c in obj['components']:
  if c['type']!=0xffb39248:continue
  old=c['address'];new=BASE+0xbc100+len(components)*0x800;memory[new-BASE:new-BASE+0x1a0]=source[old-source_base:old-source_base+0x1a0];cursor=new+0x200
  counts=[]
  for pointer_offset,count_offset,stride in [(0x60,0x8c,16),(0x90,0x94,20),(0x98,0x9c,36)]:
   count=struct.unpack_from('<H',source,old-source_base+count_offset)[0];counts.append(count)
   pointer=struct.unpack_from('<I',source,old-source_base+pointer_offset)[0]
   if count:
    size=count*stride;assert source_base<=pointer and pointer+size<=source_base+len(source)
    memory[cursor-BASE:cursor-BASE+size]=source[pointer-source_base:pointer-source_base+size]
    struct.pack_into('<I',memory,new-BASE+pointer_offset,cursor);relocations.append([new+pointer_offset,pointer,cursor,size]);cursor+=(size+15)&~15
  assert cursor<=new+0x800
  components.append({'name':obj['text'],'original':old,'address':new,'points':counts[0],'spheres':counts[1],'auxiliary_contacts':counts[2],
   'position':list(struct.unpack_from('<4f',memory,new-BASE+0x110)),'radius':struct.unpack_from('<f',memory,new-BASE+0x198)[0]})
assert len(components)==19
scene=fixture['cases'][0]['globals'][0];q=s.Assembly(memory,BASE,scene,fixture['pointer_fields'],MOVING)
s.s.FUNCTIONS['0x42bf00']={'name':'thug_rigidbody_rotate_draft','this':True,'result':'void','stack_args':[],'cleanup':0}
q.oracle.cpu.hook_add(UC_HOOK_CODE,q.oracle.observe,begin=0x42bf00,end=0x42bf00)
outcomes=Counter();records=[]
for component in components:
 at=component['address']
 for height in [0.,-.25,-2.,-16.,32.]:
  position=component['position'][:];position[1]+=height
  q.check([(0x42bf00,at,[]),(0x42c950,at,[s.Q]),(0x42c950,at,[s.Q])],[s.floats(at+0x110,*position)],f'actual prop {component["name"]}/vertical offset{height}')
  count,active=q.oracle.cpu.mem_read(at+0x190,2);assert count<=24
  outcomes[f'height{height}/contacts{count}/active{active}']+=1;records.append({'name':component['name'],'height':height,'contacts':count,'active':active})
scope='Actual19 initialized training Rigidbody components and original shape arrays reconstructed from the immutable63-call training snapshot, compactly copied with documented shape-pointer relocation. Original42bf00 transforms their real shapes; full42c950 twice builds its real cache and assembles contacts against the original605-instance training grid. Five vertical placements per prop include the unchanged original placement and controlled penetration/miss positions. Snapshot/file/GPU setup is not rerun by these new calls; moving-scene list is an empty fixture. Entire arena/globals/returns compare exactly, without substituted collision callees, tolerance or NaN classification. Full Rigidbody/object/scene update, rendering and original browser playability remain unfinished.'
q.save('contact-assembly-training',scope,{'source_hashes':sources,'shape_relocations':relocations,'components':components,'contact_results':records,'contact_outcomes':dict(outcomes),
 'preserved_snapshot_calls':63,'original_collision_objects':training['original_collision_objects'],'grid_cell_references':training['grid_cell_references'],'grid_nonempty_cells':training['grid_nonempty_cells']})
