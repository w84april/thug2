"""Original-only first-frame exploration after all31 actual prop constructions."""
from pathlib import Path
source=Path('local/analysis/particle-create-scene-setup.py').read_text().split("f=json.loads((folder/'level-collision-load-fixtures.json')")[0]
assert '.write_text(' not in source
exec(compile(source,'<preserved isolated fullscene platform setup>','exec'))
if 0x684fc8 in index:defaults[index[0x684fc8]]=0x3f800000
else:glob('thug_frame_length_scale',0x684fc8,0x3f800000)
functions['0x430e20']={'name':'UNRECOVERED_rigidbody_update','this':True,'result':'void','cleanup':0}
functions['0x45d920']={'name':'thug_object_update_components','this':True,'result':'void','cleanup':0}
prior=json.loads((folder/'rigidbody-initialize-training-fixtures.json').read_text())['cases'][0]['steps']
objects=json.loads((folder/'rigidbody-initialize-training-original.json').read_text())['objects']
rigids=[c['address'] for o in objects for c in o['components'] if c['type']==0xffb39248]
# Extra original QB and original native bindings reside above all scene buffers.
PARTICLE,NSLOTS,UICTX,CUTSCENE,GETID=0x5f00000,0x5f10000,0x5f20000,0x5f21000,0x5f30000
particle_bytes=(folder/'particle-startup-archived.qb').read_bytes();particle_filename=PARTICLE+0x10000-256
memory[PARTICLE-BASE:PARTICLE-BASE+len(particle_bytes)]=particle_bytes
name=b'scripts\\fx\\particle_scripts.qb\0';memory[particle_filename-BASE:particle_filename-BASE+len(name)]=name
memory[UICTX-BASE:UICTX-BASE+0x6a4]=bytes(0x6a4);memory[CUTSCENE-BASE:CUTSCENE-BASE+0x100]=bytes(0x100)
glob('thug_ui_manager',0x701440,UICTX);glob('thug_cutscene_context_draft',0x6fa7c0,CUTSCENE)
metadata={e['name']:e for e in json.loads((folder/'script-bindings.json').read_text())}
for i,name in enumerate(['GlobalExists','MangleChecksums','ObjectExists','CutsceneDestroyListActive','StructureContains','CreateCompositeObject']):
 key=crc(name.encode());value=int(metadata[name]['address'],16);slot=NSLOTS+i*20;bucket=BUCKETS+(key&4095)*4
 put(slot,'<BBH4I',0,8,0,key,0,value,int.from_bytes(memory[bucket-BASE:bucket-BASE+4],'little'));put(bucket,'<I',slot)
put(GETID,'<6I',0x500eb224,0x57525413,0x460940,0,0,0)
slot=NSLOTS+6*20;bucket=BUCKETS+(0x500eb224&4095)*4
put(slot,'<BBH4I',0,9,0,0x500eb224,0,GETID,int.from_bytes(memory[bucket-BASE:bucket-BASE+4],'little'));put(bucket,'<I',slot)
# The particle's LockObj uses an already recovered real component factory.
component_count=int.from_bytes(memory[OBJECTS+0x44-BASE:OBJECTS+0x48-BASE],'little')
put(OBJECTS+0x44,'<I',component_count+2);put(OBJECTS+0x48+component_count*8,'<4I',0x5cb5cb7e,0x41ff20,0xc5bceb9e,0x41e1e0)
# LockObj initialization calls the already recovered manager priority virtual.
object_methods=int.from_bytes(memory[OBJECTS-BASE:OBJECTS-BASE+4],'little');put(object_methods+0x10,'<I',0x4619d0)
initial=bytes(memory);oracle.initial=initial
calls=[(int(s['fn'],16),s['this'],s['args']) for s in prior]
calls += [(0x472420,0,[particle_filename,PARTICLE,0,1,0])]
particle_settings=next(a for a in assets if a['member'].lower()=='levels\\tr\\tr_level_particle_data.qb')
calls += [(0x472420,0,[particle_settings['filename'],particle_settings['address'],0,1,0])]
calls += [(0x45d920,objects[7]['object'],[])]
