"""Derive a private Warehouse view from original nodes; no camera parity claim."""
import hashlib,json,math
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';read=lambda f:json.loads(f.read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
identity=read(p/'tr-scene-identity-v2-original.json');geometry=read(p/'tr-warehouse-geometry-v1-discovery.json');selection=read(p/'tr-level-selection-v1-original.json')
entries=[]
for symbol in selection['files'][0]['symbols']:
 value=symbol['value']
 if isinstance(value,dict) and 'items' in value:
  entries.extend(item for item in value['items'] if isinstance(item,list) and any(row.get('value')=='TRAINING' for row in item))
assert len(entries)==2
for entry in entries:
 assert any(row['text']=='level' and row['value']['text']=='load_TR' for row in entry)
assert any(row['text']=='level_prefix' and row['value']=='TR' for entry in entries for row in entry)
nodes={n['index']:n for n in identity['nodes_registered']};restart=next(n for n in nodes.values() if n['text']=='TRG_G_GAP2_RESTARTNODE')
assert restart['class_text']=='Restart' and restart['flags']['CreatedAtStart']
floor=next(s for s in geometry['sectors'] if s['text']=='SkWare_Main_9');assert floor['same_axis_max_error']<.1
target=[(floor['loaded_bounds'][i]+floor['loaded_bounds'][i+3])/2 for i in range(3)]
eye=restart['position']['values'][:3];eye[1]+=120
target[1]+=250
target[2]+=1400
delta=[eye[i]-target[i] for i in range(3)];distance=math.hypot(*delta)
sectors=[s for s in identity['sectors'] if nodes[s['node_index']]['class_text']=='LevelGeometry' and nodes[s['node_index']]['flags']['CreatedAtStart']]
indices=[i for s in sectors for i in s['mesh_indices']];assert len(sectors)==672 and len(indices)==len(set(indices))==2028
view={'version':1,'label':'THUG2 Training — Warehouse interior geometry preview','original_menu_entries':entries,'original_scene_assets':identity['assets'],
 'derivation_sha256':{name:sha(p/name) for name in ['tr-scene-identity-v2-original.json','tr-warehouse-geometry-v1-discovery.json','tr-level-selection-v1-original.json']},
 'restart_node':restart,'target_sector':{k:floor[k] for k in ['index','name','text','loaded_bounds','same_axis_max_error']},
 'camera':{'eye':eye,'target':target,'yaw':math.atan2(delta[0],delta[2]),'pitch':math.asin(delta[1]/distance),'distance':distance,'eye_height_adapter':120,'look_at_offset_adapter':[0,250,1400]},
 'initial_static_sector_count':len(sectors),'mesh_indices':indices,
 'selection':'Original Class=LevelGeometry and CreatedAtStart flags only; excludes uninstantiated LevelObject/GameObject local geometry. Runtime script changes, original visibility, transforms and material render states remain unverified.',
 'view_scope':'Preview camera placed above the original Warehouse floor gap restart node, looking toward the original main-floor bounds. Node is evidence for an interior Warehouse location, not verified default gameplay spawn. Eye height and look-at are new preview choices, not recovered gameplay camera behavior.',
 'original_storage_buffers':7024,'original_storage_sha256':'e6d9940dcc4b1ac18c5776bdfe62a3fbea6def339af8b037dcfe4b90b4206423','completion_credit':0,'matching_credit':0,'original_frame_equivalence_verified':False,'playable':False}
out=p/'training-warehouse-v2-view.json';assert not out.exists();out.write_text(json.dumps(view,indent=2)+'\n')
print('Prepared',len(sectors),'static sectors /',len(indices),'meshes; Warehouse eye',eye,'target',target,'view SHA256',sha(out))
