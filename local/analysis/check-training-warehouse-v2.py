"""Independently check original selection and actual Chromium view observations."""
import hashlib,json,math
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';read=lambda n:json.loads((p/n).read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
v=read('training-warehouse-v2-view.json');identity=read('tr-scene-identity-v2-original.json');geometry=read('tr-warehouse-geometry-v1-discovery.json')
for name,h in v['derivation_sha256'].items():assert sha(p/name)==h,name
for name,entry in v['original_scene_assets'].items():assert sha(r/name)==entry['sha256'] and (r/name).stat().st_size==entry['bytes'],name
nodes={n['index']:n for n in identity['nodes_registered']}
selected=[s for s in identity['sectors'] if nodes[s['node_index']]['class_text']=='LevelGeometry' and nodes[s['node_index']]['flags']['CreatedAtStart']]
assert [i for s in selected for i in s['mesh_indices']]==v['mesh_indices'] and len(selected)==v['initial_static_sector_count']==672
restart=next(n for n in nodes.values() if n['text']=='TRG_G_GAP2_RESTARTNODE');assert restart==v['restart_node'] and restart['class_text']=='Restart'
eye=restart['position']['values'][:3];eye[1]+=120;assert eye==v['camera']['eye']
floor=next(s for s in geometry['sectors'] if s['text']=='SkWare_Main_9');target=[(floor['loaded_bounds'][i]+floor['loaded_bounds'][i+3])/2 for i in range(3)];target[1]+=250;target[2]+=1400
assert target==v['camera']['target'] and floor['same_axis_max_error']<.1
observed={name:read('training-warehouse-v2-browser-'+name+'.json') for name in ['initial','zoom','orbit','overview','reset']}
for state in observed.values():
 assert state['result']=='rendered original geometry' and state['center_pixel_colors']>1
 assert state['original_gpu_storage_hashes_equal'] and state['ordered_storage_buffers']==7024 and state['ordered_storage_sha256']==v['original_storage_sha256']
 assert (state['meshes'],state['draw_calls'],state['initial_static_sectors'],state['textures'],state['uploaded_mips'],state['loader_calls'],state['decoded_output_inputs'])==(2269,2028,672,596,2486,4540,0)
 assert state['view_metadata_sha256']==sha(p/'training-warehouse-v2-view.json')
 assert not state['original_gameplay_camera_verified'] and not state['frame_equivalence_verified'] and not state['playable'] and state['completion_credit']==0
a,z,o,b,last=[observed[n] for n in ['initial','zoom','orbit','overview','reset']]
for k in ['yaw','pitch','distance']:assert a[k]==v['camera'][k] and last[k]==a[k],k
for k in ['target','eye','center_pixel_colors','view_mode']:assert last[k]==a[k],k
assert a['target']==target and max(abs(x-y) for x,y in zip(a['eye'],eye))<1e-10
assert z['distance']<a['distance'] and o['yaw']!=a['yaw'] and o['pitch']!=a['pitch']
assert b['view_mode']=='Entire TR bundle' and b['distance']>a['distance'] and a['view_mode']=='Warehouse'
assert v['completion_credit']==v['matching_credit']==0 and not v['playable']
result={'result':'pass','original_level_selection_training_load_tr_verified':True,'original_nodes':1917,'original_sectors':790,'static_created_at_start_sectors':672,'static_draw_meshes':2028,'original_storage_buffers':7024,'original_storage_sha256':v['original_storage_sha256'],'actual_chromium_rendered':True,'actual_zoom_orbit_overview_reset_verified':True,'initial_center_pixel_colors':a['center_pixel_colors'],'camera_is_new_adapter':True,'original_default_spawn_verified':False,'original_visibility_transforms_frame_equivalence_verified':False,'complete_engine_suites':202,'completion_credit':0,'matching_credit':0,'playable':False}
t=p/'training-warehouse-v2-view-verification.json';assert not t.exists();t.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
