"""Pin a zero-credit rendering integration result and all preceding evidence."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';read=lambda f:json.loads(f.read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
previous=p/'camera-startup-v2-checkpoint.json';prior=read(previous)
assert sha(previous)=='63a639d3ea500f7009f9c0b692a9be15417d541cf2ad5b2ca5a5d00bb83c52f6'
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,h in prior[group].items():assert sha(r/name)==h,(group,name)
runtime=read(p/'training-webgl-v1-runtime.json');storage=read(p/'training-webgl-v1-storage-proof-v2.json');node=read(p/'training-webgl-v1-node-v2.json')
for name,h in runtime['input_sha256'].items():assert sha(p/name)==h,name
assert sha(p/runtime['wasm'])==prior['wasm_sha256']
assert storage['runtime_sha256']==sha(p/'training-webgl-v1-runtime.json')
assert node['result']=='pass' and node['original_gpu_storage_hashes_equal'] and not node['missing_texture_references']
observed={name:read(p/('training-webgl-v1-browser-storage-'+name+'.json')) for name in ['initial','zoom','orbit','reset']}
for state in observed.values():
 assert state['result']=='rendered original geometry' and state['original_gpu_storage_hashes_equal']
 assert state['ordered_storage_buffers']==storage['ordered_storage_buffers']==7024
 assert state['ordered_storage_sha256']==storage['ordered_storage_sha256']
 assert (state['meshes'],state['vertices'],state['indices'],state['textures'],state['materials'],state['loader_calls'],state['uploaded_mips'],state['draw_calls'])==(2269,50814,77029,596,870,4540,2486,2269)
 assert state['center_pixel_colors']>1 and not state['playable'] and state['completion_credit']==0 and not state['frame_equivalence_verified']
initial,zoom,orbit,reset=[observed[name] for name in ['initial','zoom','orbit','reset']]
assert zoom['distance']<initial['distance'] and orbit['yaw']!=initial['yaw'] and orbit['pitch']!=initial['pitch']
for key in ['yaw','pitch','distance','center_pixel_colors']:assert reset[key]==initial[key],key
baseline=p/'training-webgl-v1-reporting-baseline-report.json';assert not baseline.exists();baseline.write_bytes((r/'progress/report.json').read_bytes())
report=read(baseline);assert (int(report['measures']['complete_code']),int(report['measures']['matched_code']))==(436577,406)
paths={previous,p/'camera-startup-v2-audit.json',baseline}
for pattern in ['training-webgl-v1*','prepare-training-webgl-v1*','check-training-webgl-v1*','serve-training-webgl-v1*','pin-training-webgl-v1*','audit-training-webgl-v1*']:
 paths.update(f for f in p.glob(pattern) if f.is_file())
artifacts=dict(prior['artifact_hashes'])
for f in paths:artifacts[str(f.relative_to(r))]=sha(f)
out=p/'training-webgl-v1-checkpoint.json';assert not out.exists()
checkpoint={'schema':1,'result':'private rendering integration passes; original frame equivalence and gameplay unverified','prior_checkpoint':str(previous.relative_to(r)),'prior_checkpoint_sha256':sha(previous),'specimen_sha256':prior['specimen_sha256'],'artifact_hashes':dict(sorted(artifacts.items())),'source_hashes':prior['source_hashes'],'platform_source_hashes':prior['platform_source_hashes'],'harness_hashes':prior['harness_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],'preserved_artifacts':len(prior['artifact_hashes']),'wasm':prior['wasm'],'wasm_sha256':prior['wasm_sha256'],'main_wasm_sha256':prior['main_wasm_sha256'],'browser_engine_parity_suites':200,'browser_preview':observed,'original_gpu_storage_buffers':7024,'original_gpu_storage_sha256':storage['ordered_storage_sha256'],'screenshot':'local/analysis/training-webgl-v1-storage-verified.jpg','report_at_verification':{'path':str(baseline.relative_to(r)),'sha256':sha(baseline)},'new_complete_addresses':[],'new_complete_body_bytes':0,'new_matched_bytes':0,'scope':runtime['scope'],'limitations':['Fixture-backed raw-input arena and SDK comparison storage are bootstrap dependencies; production file/device adapters and full scene/sector boot remain','First material pass and strip zero; original pass sorting, visibility, blending, culling, animations and render-state/frame equivalence unverified','Orbit controls are a new preview interface, not recovered skater gameplay','All proprietary raw assets, binaries, snapshots and screenshots remain private'],'playable':False}
out.write_text(json.dumps(checkpoint,indent=2)+'\n');print('Pinned',len(artifacts),'artifacts, preserving',len(prior['artifact_hashes']),'; rendering integration adds zero completion bytes;',sha(out))
