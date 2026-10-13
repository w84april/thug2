import {loadSkinnedModel} from './skinned-model-webgl-v1-load.mjs';
import {createOriginalPhaseTraversal} from './warehouse-original-physics-jump-traversal-v4.mjs';
import {verifyJumpActionBootstrap} from './skater-jump-action-bootstrap-v6-checks.mjs';
import {bindKeyboardInput} from './browser_input.mjs';
import {createSkaterPose,skinVertices} from './skater-animation-preview-v1-pose.mjs';
import {loadHawk} from './skater-hawk-webgl-v2-load.mjs';
import {loadTraining} from './training-webgl-v1-load.mjs';
const canvas=document.querySelector('#world'),status=document.querySelector('#status');
const cached=new Map();
const load=n=>{if(!cached.has(n))cached.set(n,(async()=>{const r=await fetch('/'+n);if(!r.ok)throw Error('Cannot load '+n);return new Uint8Array(await r.arrayBuffer());})());return cached.get(n);};
let stopped=false,verification=null,movementSnapshot=null;const previewErrors=[];
const fail=(error,phase='startup')=>{
 stopped=true;const detail={phase,message:String(error.message??error),stack:String(error.stack??error),last_completed_movement:verification?.movement_state??null,keyboard_packet:verification?.keyboard_packet??null};
 try{detail.current_movement=movementSnapshot?.()??null;}catch(snapshotError){detail.snapshot_error=String(snapshotError);}
 previewErrors.push(detail);
 if(verification){verification.preview_error=detail;verification.preview_errors=previewErrors;document.querySelector('#verification').textContent=JSON.stringify(verification);}
 else document.querySelector('#verification').textContent=JSON.stringify({preview_error:detail,preview_errors:previewErrors,playable:false,completion_credit:0});
 document.querySelector('#error').textContent=phase==='startup'?'Preview could not load. Reload the preview.':'Movement preview stopped. Reset skater to continue; reload if the error persists.';
 status.textContent='Preview paused';
};
try {
  const started=performance.now(),runtime=JSON.parse(new TextDecoder().decode(await load('training-webgl-v1-runtime.json')));
  for(const [name,wanted] of Object.entries(runtime.input_sha256)) {
    const bytes=await load(name),digest=await crypto.subtle.digest('SHA-256',bytes);
    const actual=Array.from(new Uint8Array(digest),x=>x.toString(16).padStart(2,'0')).join('');
    if(actual!==wanted)throw Error('Changed preserved input '+name);
  }
  const world=await loadTraining(await load(runtime.wasm),runtime,load);
  const storageProof=JSON.parse(new TextDecoder().decode(await load('training-webgl-v1-storage-proof-v2.json')));
  const digest=async bytes=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),x=>x.toString(16).padStart(2,'0')).join('');
  const stored=[];for(const m of world.meshes){stored.push(m.vertexData);for(const s of m.strips)stored.push(s.data);}for(const t of world.textures.values())stored.push(...t.mips);
  const storageHashes=await Promise.all(stored.map(digest));
  if(storageHashes.length!==storageProof.ordered_storage_buffers||await digest(new TextEncoder().encode(storageHashes.join('\n')))!==storageProof.ordered_storage_sha256)throw Error('Browser storage differs from original execution');
  const gl=canvas.getContext('webgl2',{antialias:true,preserveDrawingBuffer:true});
  if(!gl)throw Error('WebGL 2 is unavailable');
  const compressed=gl.getExtension('WEBGL_compressed_texture_s3tc');
  if(!compressed)throw Error('S3TC textures are unavailable');
  const shader=(type,source)=>{const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s;};
  const program=gl.createProgram();
  gl.attachShader(program,shader(gl.VERTEX_SHADER,`#version 300 es
    precision highp float;layout(location=0) in vec3 p;layout(location=1) in vec4 c;layout(location=2) in vec2 uv;
    uniform mat4 projection;uniform mat4 camera;uniform mat4 model;out vec4 color;out vec2 texcoord;
    void main(){gl_Position=projection*camera*model*vec4(p,1);color=c.bgra;texcoord=uv;}`));
  gl.attachShader(program,shader(gl.FRAGMENT_SHADER,`#version 300 es
    precision highp float;in vec4 color;in vec2 texcoord;uniform sampler2D image;out vec4 pixel;
    void main(){vec4 t=texture(image,texcoord);if(t.a<0.2)discard;pixel=vec4(t.rgb*color.rgb,1);}`));
  gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(program));gl.useProgram(program);
  const modelUniform=gl.getUniformLocation(program,'model');
  const identity=new Float32Array([1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]);
  const projectionUniform=gl.getUniformLocation(program,'projection'),cameraUniform=gl.getUniformLocation(program,'camera');
  const textureObjects=new Map(),white=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,white);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,1,1,0,gl.RGBA,gl.UNSIGNED_BYTE,new Uint8Array([255,255,255,255]));gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);
  let uploadedMips=0;
  for(const t of world.textures.values()) {
    const object=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,object);
    if(t.format!==0x31545844&&t.format!==0x35545844)throw Error('Unsupported original texture format '+t.format.toString(16));
    const format=t.format===0x31545844?compressed.COMPRESSED_RGBA_S3TC_DXT1_EXT:compressed.COMPRESSED_RGBA_S3TC_DXT5_EXT;
    for(const [level,bytes] of t.mips.entries()) {gl.compressedTexImage2D(gl.TEXTURE_2D,level,format,Math.max(1,t.width>>level),Math.max(1,t.height>>level),0,bytes);uploadedMips++;}
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,t.levels>1?gl.LINEAR_MIPMAP_LINEAR:gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAX_LEVEL,t.levels-1);textureObjects.set(t.pointer,object);
  }
  const viewBytes=await load('training-warehouse-v2-view.json');
  if(await digest(viewBytes)!=='3d477762d9e9f5159379e833368c9b16001dca9f0dd424393a921fec8ac973cc')throw Error('Changed original Warehouse view metadata');
  const view=JSON.parse(new TextDecoder().decode(viewBytes)),selected=new Set(view.mesh_indices);
  const low=[Infinity,Infinity,Infinity],high=[-Infinity,-Infinity,-Infinity],draws=[];
  for(const [meshIndex,m] of world.meshes.entries()) {
    if(!selected.has(meshIndex))continue;
    const data=new DataView(m.vertexData.buffer);
    for(let i=0;i<m.vertices;i++)for(let axis=0;axis<3;axis++){const x=data.getFloat32(i*m.stride+axis*4,true);if(!Number.isFinite(x))throw Error('Nonfinite original vertex');low[axis]=Math.min(low[axis],x);high[axis]=Math.max(high[axis],x);}
    const vao=gl.createVertexArray();gl.bindVertexArray(vao);const vb=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,vb);gl.bufferData(gl.ARRAY_BUFFER,m.vertexData,gl.STATIC_DRAW);
    if((m.fvf&0xff)!==0x52)throw Error('Unsupported original vertex layout');
    gl.enableVertexAttribArray(0);gl.vertexAttribPointer(0,3,gl.FLOAT,false,m.stride,0);gl.enableVertexAttribArray(1);gl.vertexAttribPointer(1,4,gl.UNSIGNED_BYTE,true,m.stride,24);
    if((m.fvf>>8)&15){gl.enableVertexAttribArray(2);gl.vertexAttribPointer(2,2,gl.FLOAT,false,m.stride,28);}else{gl.disableVertexAttribArray(2);gl.vertexAttrib2f(2,0,0);}
    const texture=m.textureHandle?textureObjects.get(m.textureHandle):white;if(!texture)throw Error('Unresolved original material texture');
    // Slot zero is the full-detail strip. Higher slots are LOD alternatives;
    // drawing all slots together would double the original surface geometry.
    const strip=m.strips.find(s=>s.slot===0);if(!strip)continue;
    const ib=gl.createBuffer();gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,ib);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,strip.data,gl.STATIC_DRAW);draws.push({vao,texture,count:strip.count});
  }
  const hawkRuntime=JSON.parse(new TextDecoder().decode(await load('skater-hawk-webgl-v1-runtime.json')));
  for(const [name,wanted] of Object.entries(hawkRuntime.input_sha256))if(await digest(await load(name))!==wanted)throw Error('Changed Hawk raw input '+name);
  const hawk=await loadHawk(await load('skater-animation-sample-v1.wasm'),hawkRuntime,load);
  const poseInputs=JSON.parse(new TextDecoder().decode(await load('skater-animation-preview-v1-inputs.json')));
  for(const spec of Object.values(poseInputs.inputs))if(await digest(await load(spec.file))!==spec.sha256)throw Error('Changed raw animation input');
  const skaterPose=await createSkaterPose(hawk,poseInputs,load);
  const nativePoseProof=JSON.parse(new TextDecoder().decode(await load('skater-animation-preview-v1-matrix-proof.json'))),nodePoseProof=JSON.parse(new TextDecoder().decode(await load('skater-animation-preview-v1-node.json'))),verifiedPoses=[];
  for(const original of nativePoseProof.poses){
    skaterPose.select(original.clip);const state=skaterPose.seek(original.seconds);
    if(await digest(state.matrixBytes)!==original.matrix_sha256||await digest(state.poseBytes)!==original.pose_sha256)throw Error('Original integrated pose differs');
    const skins=hawk.meshes.map(mesh=>skinVertices(mesh,state.matrixData,skaterPose.bones,mesh.vertexData.slice())),skinHash=await digest(new TextEncoder().encode((await Promise.all(skins.map(digest))).join('\n')));
    const expected=nodePoseProof.verified_poses.find(x=>x.clip===original.clip&&x.seconds===original.seconds);if(skinHash!==expected.adapted_skin_sha256)throw Error('Node/browser skin adapter differs');
    verifiedPoses.push({...original,adapted_skin_sha256:skinHash});
  }
  skaterPose.select('Idle');let poseState=skaterPose.sample(),playing=true,lastAnimationTime=null;
  const hawkProof=JSON.parse(new TextDecoder().decode(await load('skater-hawk-webgl-v1-storage-proof.json'))),hawkStorage=[];
  for(const m of hawk.meshes){hawkStorage.push(m.vertexData);for(const strip of m.strips)hawkStorage.push(strip.data);}for(const t of hawk.textures.values())hawkStorage.push(...t.mips);
  const hawkHashes=await Promise.all(hawkStorage.map(digest));
  if(hawkHashes.length!==hawkProof.ordered_storage_buffers||await digest(new TextEncoder().encode(hawkHashes.join('\n')))!==hawkProof.ordered_storage_sha256)throw Error('Hawk rest storage differs from original execution');
  const hawkTextures=new Map(),hawkDraws=[];
  for(const t of hawk.textures.values()){
    const texture=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,texture);
    const format=t.format===0x31545844?compressed.COMPRESSED_RGBA_S3TC_DXT1_EXT:t.format===0x35545844?compressed.COMPRESSED_RGBA_S3TC_DXT5_EXT:0;
    if(!format&&t.format!==0x15)throw Error('Unsupported Hawk texture');
    for(const [l,bytes] of t.mips.entries()){
      const w=Math.max(1,t.width>>l),h=Math.max(1,t.height>>l);
      if(format)gl.compressedTexImage2D(gl.TEXTURE_2D,l,format,w,h,0,bytes);
      else{
        if(bytes.length!==w*h*4)throw Error('Invalid original A8R8G8B8 mip');
        const rgba=bytes.slice();for(let i=0;i<rgba.length;i+=4){rgba[i]=bytes[i+2];rgba[i+2]=bytes[i];}
        gl.texImage2D(gl.TEXTURE_2D,l,gl.RGBA8,w,h,0,gl.RGBA,gl.UNSIGNED_BYTE,rgba);
      }
    }
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,t.levels>1?gl.LINEAR_MIPMAP_LINEAR:gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAX_LEVEL,t.levels-1);hawkTextures.set(t.pointer,texture);
  }
  for(const m of hawk.meshes){
    const vao=gl.createVertexArray();gl.bindVertexArray(vao);const vb=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,vb);gl.bufferData(gl.ARRAY_BUFFER,m.vertexData,gl.STATIC_DRAW);
    for(const [slot,size,type,normalized,offset] of [[0,3,gl.FLOAT,false,0],[1,4,gl.UNSIGNED_BYTE,true,24],[2,2,gl.FLOAT,false,28]]){gl.enableVertexAttribArray(slot);gl.vertexAttribPointer(slot,size,type,normalized,m.stride,offset);}
    const strip=m.strips.find(s=>s.slot===0);if(!strip)throw Error('Missing full-detail Hawk strip');const ib=gl.createBuffer();gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,ib);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,strip.data,gl.STATIC_DRAW);
    const texture=m.textureHandle?hawkTextures.get(m.textureHandle):white;if(!texture)throw Error('Unresolved original Hawk texture');hawkDraws.push({vao,vb,mesh:m,posed:m.vertexData.slice(),texture,count:strip.count});
  }
  const boardRuntime=JSON.parse(new TextDecoder().decode(await load('skater-board-webgl-v1-runtime.json')));
  for(const [name,wanted] of Object.entries(boardRuntime.input_sha256))if(await digest(await load(name))!==wanted)throw Error('Changed board input '+name);
  const board=await loadSkinnedModel(await load(boardRuntime.wasm),boardRuntime,load),boardReference=JSON.parse(new TextDecoder().decode(await load('skater-board-preview-v1-node.json'))),boardStorage=[];
  for(const m of board.meshes){boardStorage.push(m.vertexData);for(const strip of m.strips)boardStorage.push(strip.data);}for(const t of board.textures.values())boardStorage.push(...t.mips);
  const boardStorageHash=await digest(new TextEncoder().encode((await Promise.all(boardStorage.map(digest))).join('\n')));
  if(boardStorage.length!==boardReference.original_board_rest_storage_buffers||boardStorageHash!==boardReference.original_board_rest_storage_sha256)throw Error('Original board rest buffers differ');
  const verifiedBoardPoses=[];
  for(const original of nativePoseProof.poses){
    skaterPose.select(original.clip);const state=skaterPose.seek(original.seconds);
    if(await digest(state.matrixBytes)!==original.matrix_sha256||await digest(state.poseBytes)!==original.pose_sha256)throw Error('Original board pose matrix differs');
    const skins=board.meshes.map(mesh=>skinVertices(mesh,state.matrixData,skaterPose.bones,mesh.vertexData.slice())),low=[Infinity,Infinity,Infinity],high=[-Infinity,-Infinity,-Infinity];
    for(const [i,bytes] of skins.entries()){const v=new DataView(bytes.buffer,bytes.byteOffset,bytes.byteLength);for(let j=0;j<board.meshes[i].vertices;j++)for(let k=0;k<3;k++){const x=v.getFloat32(j*76+k*4,true);if(!Number.isFinite(x))throw Error('Nonfinite board vertex');low[k]=Math.min(low[k],x);high[k]=Math.max(high[k],x);}}
    const actual={...original,adapted_board_skin_sha256:await digest(new TextEncoder().encode((await Promise.all(skins.map(digest))).join('\n'))),adapted_bounds:[low,high]};
    const expected=boardReference.verified_poses.find(x=>x.clip===original.clip&&x.seconds===original.seconds);
    if(JSON.stringify(actual)!==JSON.stringify(expected))throw Error('Node/browser board skin adapter differs');verifiedBoardPoses.push(actual);
  }
  skaterPose.select('Idle');poseState=skaterPose.sample();
  const boardTextures=new Map(),boardDraws=[];
  for(const t of board.textures.values()){
    const texture=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,texture);
    const format=t.format===0x31545844?compressed.COMPRESSED_RGBA_S3TC_DXT1_EXT:t.format===0x35545844?compressed.COMPRESSED_RGBA_S3TC_DXT5_EXT:0;
    if(!format&&t.format!==0x15)throw Error('Unsupported board texture');
    for(const [l,bytes] of t.mips.entries()){
      const w=Math.max(1,t.width>>l),h=Math.max(1,t.height>>l);
      if(format)gl.compressedTexImage2D(gl.TEXTURE_2D,l,format,w,h,0,bytes);
      else{
        if(bytes.length!==w*h*4)throw Error('Invalid original A8R8G8B8 mip');
        const rgba=bytes.slice();for(let i=0;i<rgba.length;i+=4){rgba[i]=bytes[i+2];rgba[i+2]=bytes[i];}
        gl.texImage2D(gl.TEXTURE_2D,l,gl.RGBA8,w,h,0,gl.RGBA,gl.UNSIGNED_BYTE,rgba);
      }
    }
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,t.levels>1?gl.LINEAR_MIPMAP_LINEAR:gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAX_LEVEL,t.levels-1);boardTextures.set(t.pointer,texture);
  }
  for(const m of board.meshes){
    const vao=gl.createVertexArray();gl.bindVertexArray(vao);const vb=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,vb);gl.bufferData(gl.ARRAY_BUFFER,m.vertexData,gl.STATIC_DRAW);
    for(const [slot,size,type,normalized,offset] of [[0,3,gl.FLOAT,false,0],[1,4,gl.UNSIGNED_BYTE,true,24],[2,2,gl.FLOAT,false,28]]){gl.enableVertexAttribArray(slot);gl.vertexAttribPointer(slot,size,type,normalized,m.stride,offset);}
    const strip=m.strips.find(s=>s.slot===0);if(!strip)throw Error('Missing full-detail board strip');const ib=gl.createBuffer();gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,ib);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,strip.data,gl.STATIC_DRAW);
    const texture=m.textureHandle?boardTextures.get(m.textureHandle):white;if(!texture)throw Error('Unresolved original board texture');boardDraws.push({vao,vb,mesh:m,posed:m.vertexData.slice(),texture,count:strip.count});
  }
  const phaseRuntime=JSON.parse(new TextDecoder().decode(await load('skater-jump-action-bootstrap-v6-inputs.json'))),motionWasm=await load(phaseRuntime.module);
  const motionRuntime=JSON.parse(new TextDecoder().decode(await load('skater-browser-motion-v1-inputs.json'))),collisionRuntime=JSON.parse(new TextDecoder().decode(await load('skater-shared-ground-v1-inputs.json')));
  for(const inputs of [phaseRuntime,motionRuntime,collisionRuntime])for(const [name,wanted] of Object.entries(inputs.input_sha256))if(await digest(await load(name))!==wanted)throw Error('Changed movement startup input '+name);
  const traversalProof=await verifyJumpActionBootstrap(motionWasm,motionRuntime,collisionRuntime,phaseRuntime,JSON.parse(new TextDecoder().decode(await load('skater-jump-action-live-v3-original.json'))),load,digest),nodeTraversal=JSON.parse(new TextDecoder().decode(await load('skater-level-trigger-jump-v1-node.json')));
  if(JSON.stringify(traversalProof)!==JSON.stringify(nodeTraversal))throw Error('Node/browser original grounded/air phases differ');
  let traversal=await createOriginalPhaseTraversal(motionWasm,motionRuntime,collisionRuntime,phaseRuntime,load),skaterPosition=traversal.position;
  const skaterModel=identity.slice();skaterModel.set(skaterPosition,12);
  let lastMovementTime=null,movementAccumulator=0;

  const normalize=a=>{const l=Math.hypot(...a);return a.map(x=>x/l);},cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]],dot=(a,b)=>a.reduce((s,x,i)=>s+x*b[i],0);
  let target=skaterPosition.map((x,i)=>x+(i===1?45:0));
  const radius=Math.hypot(...low.map((x,i)=>high[i]-x))/2;
  let yaw=view.camera.yaw,pitch=.25,distance=320,drag=null,frame=0,viewMode='Warehouse';
  const cameraPointer=0x6100000,e=world.exports,v=world.view;
  v.setFloat32(e.thug_camera_default_fov_v2.value,60,true);v.setFloat32(e.thug_camera_display_ratio_v2.value,1,true);e.thug_camera_object_construct_v2(cameraPointer);
  gl.enable(gl.DEPTH_TEST);gl.disable(gl.CULL_FACE);gl.clearColor(.045,.08,.105,1);
  verification={...world.summary,original_hawk_rest_storage_hashes_equal:true,hawk_rest_storage_sha256:hawkProof.ordered_storage_sha256,hawk_meshes:hawk.meshes.length,hawk_vertices:hawk.summary.vertices,hawk_textures:hawk.summary.textures,original_skin_pose_verified:false,original_pose_matrix_hashes_equal:true,original_integrated_poses:18,pose_stage_bones:50,verified_poses:verifiedPoses,skin_renderer_adapter:'Authored CPU WebGL adapter uses three original packed weights; original GPU shader/frame equivalence unverified',original_controller_frame_verified:false,animation_clip:'Idle',animation_seconds:0,animation_playing:true,skater_position:skaterPosition,skater_placement_adapter:'Original Warehouse restart node115; default original spawn not verified',result:'drawing pending',original_gpu_storage_hashes_equal:true,ordered_storage_buffers:stored.length,ordered_storage_sha256:storageProof.ordered_storage_sha256,uploaded_mips:uploadedMips,draw_calls:draws.length,bounds:[low,high],renderer_adapter:'original CreatedAtStart LevelGeometry; first material pass/full-detail strips; no original visibility/transforms/render-state/frame equivalence',view_metadata_sha256:'3d477762d9e9f5159379e833368c9b16001dca9f0dd424393a921fec8ac973cc',initial_static_sectors:view.initial_static_sector_count,original_gameplay_camera_verified:false,completion_credit:0,frame_equivalence_verified:false,load_ms:Math.round(performance.now()-started)};
  verification.board_browser_proof={...boardReference,verified_poses:verifiedBoardPoses};verification.original_board_rest_storage_hashes_equal=true;verification.board_texture_appearance='Default board textures; original Hawk deck/grip replacement not yet verified';verification.traversal_browser_proof={...traversalProof,frames:undefined};verification.traversal_full_proof_file='skater-level-trigger-jump-v1-browser-full.json';verification.original_bounded_ground_and_air_phases_verified=true;verification.original_bounded_physics_update_entry_verified=true;verification.authored_grounded_jump_mapping=true;verification.original_jump_script_controller_verified=false;verification.authored_position_floor_wall_updates=false;verification.original_full_frame_dispatcher=false;verification.motion_collision_share_engine_memory=true;verification.keyboard_events=0;verification.keyboard_packet=Array.from(new Uint8Array(32),n=>n.toString(16).padStart(2,'0')).join('');verification.movement_adapter_scope=traversal.scope;
  let resetting=false;movementSnapshot=()=>traversal.snapshot();
  function render(now=performance.now()){
    if(stopped||resetting)return;
    if(document.activeElement===canvas){
      if(lastMovementTime!==null)movementAccumulator+=Math.min(.1,Math.max(0,(now-lastMovementTime)/1000));
      while(movementAccumulator>=1/60){traversal.step(keyboard.packet);movementAccumulator-=1/60;}
      lastMovementTime=now;
    }else{lastMovementTime=null;movementAccumulator=0;}
    const movement=traversal.snapshot();skaterModel.set(movement.orientation);skaterModel.set(skaterPosition,12);skaterModel[15]=1;
    if(viewMode==='Warehouse')target=skaterPosition.map((x,i)=>x+(i===1?45:0));
    verification.movement_state=movement;verification.skater_position=skaterPosition;verification.keyboard_focused=document.activeElement===canvas;

    if(playing&&lastAnimationTime!==null)poseState=skaterPose.advance((now-lastAnimationTime)/1000);lastAnimationTime=now;
    for(const d of [...hawkDraws,...boardDraws]){skinVertices(d.mesh,poseState.matrixData,skaterPose.bones,d.posed);gl.bindBuffer(gl.ARRAY_BUFFER,d.vb);gl.bufferSubData(gl.ARRAY_BUFFER,0,d.posed);}
    verification.animation_clip=poseState.clip;verification.animation_seconds=poseState.seconds;verification.animation_playing=playing;document.querySelector('#seek').max=poseState.duration;document.querySelector('#seek').value=poseState.seconds;
    frame++;canvas.width=Math.round(canvas.clientWidth*Math.min(devicePixelRatio,2));canvas.height=Math.round(canvas.clientHeight*Math.min(devicePixelRatio,2));gl.viewport(0,0,canvas.width,canvas.height);
    v.setFloat32(e.thug_camera_display_ratio_v2.value,canvas.height/canvas.width,true);e.thug_camera_projection_v2(cameraPointer);
    const fov=v.getFloat32(cameraPointer+0xb0,true)*Math.PI/180,near=12,far=radius*10,f=1/Math.tan(fov/2),aspect=canvas.width/canvas.height;
    gl.uniformMatrix4fv(projectionUniform,false,new Float32Array([f/aspect,0,0,0,0,f,0,0,0,0,(far+near)/(near-far),-1,0,0,2*far*near/(near-far),0]));
    const eye=[target[0]+Math.sin(yaw)*Math.cos(pitch)*distance,target[1]+Math.sin(pitch)*distance,target[2]+Math.cos(yaw)*Math.cos(pitch)*distance];
    const z=normalize(eye.map((x,i)=>x-target[i])),x=normalize(cross([0,1,0],z)),y=cross(z,x);
    gl.uniformMatrix4fv(cameraUniform,false,new Float32Array([x[0],y[0],z[0],0,x[1],y[1],z[1],0,x[2],y[2],z[2],0,-dot(x,eye),-dot(y,eye),-dot(z,eye),1]));
    gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
    gl.uniformMatrix4fv(modelUniform,false,identity);
    for(const d of draws){gl.bindVertexArray(d.vao);gl.bindTexture(gl.TEXTURE_2D,d.texture);gl.drawElements(gl.TRIANGLE_STRIP,d.count,gl.UNSIGNED_SHORT,0);}
    gl.uniformMatrix4fv(modelUniform,false,skaterModel);
    for(const d of [...hawkDraws,...boardDraws]){gl.bindVertexArray(d.vao);gl.bindTexture(gl.TEXTURE_2D,d.texture);gl.drawElements(gl.TRIANGLE_STRIP,d.count,gl.UNSIGNED_SHORT,0);}
    const error=gl.getError();if(error)throw Error('WebGL error '+error);
    // Inspect pixels after the real draw. A clear buffer alone cannot pass.
    const pixels=new Uint8Array(64*64*4);gl.readPixels(Math.floor(canvas.width/2)-32,Math.floor(canvas.height/2)-32,64,64,gl.RGBA,gl.UNSIGNED_BYTE,pixels);
    const colors=new Set();for(let i=0;i<pixels.length;i+=4)colors.add(pixels[i]+','+pixels[i+1]+','+pixels[i+2]);
    verification.result=colors.size>1?'rendered original geometry':'clear-buffer only';verification.center_pixel_colors=colors.size;verification.frames=frame;verification.yaw=yaw;verification.pitch=pitch;verification.distance=distance;verification.eye=eye;verification.target=target.slice();verification.view_mode=viewMode;
    document.querySelector('#verification').textContent=JSON.stringify(verification);status.textContent=`${viewMode} · ${movement.grounded?'Grounded':'Air'} · movement prototype`;
    if(playing||document.activeElement===canvas)schedule();
  }
  let pendingFrame=false;
  const schedule=()=>{if(pendingFrame)return;pendingFrame=true;requestAnimationFrame(now=>{pendingFrame=false;try{render(now);}catch(error){fail(error,'frame');}});};
  canvas.addEventListener('pointerdown',event=>{canvas.focus();drag=[event.clientX,event.clientY];canvas.setPointerCapture(event.pointerId);});
  canvas.addEventListener('pointerup',()=>{drag=null;});canvas.addEventListener('pointercancel',()=>{drag=null;});
  canvas.addEventListener('pointermove',event=>{if(!drag)return;yaw-=(event.clientX-drag[0])*.006;pitch=Math.max(-1.4,Math.min(1.4,pitch+(event.clientY-drag[1])*.006));drag=[event.clientX,event.clientY];schedule();});
  canvas.addEventListener('wheel',event=>{event.preventDefault();distance=Math.max(24,Math.min(radius*8,distance*Math.exp(event.deltaY*.001)));schedule();},{passive:false});
  document.querySelector('#reset').addEventListener('click',()=>{target=skaterPosition.map((x,i)=>x+(i===1?45:0));yaw=view.camera.yaw;pitch=.25;distance=320;viewMode='Warehouse';schedule();});
  document.querySelector('#overview').addEventListener('click',()=>{target=low.map((x,i)=>(x+high[i])/2);yaw=.8;pitch=.6;distance=radius*1.9;viewMode='Entire TR bundle';schedule();});document.querySelector('#clip').addEventListener('change',event=>{skaterPose.select(event.target.value);poseState=skaterPose.sample();lastAnimationTime=null;schedule();});
  document.querySelector('#pause').addEventListener('click',()=>{playing=!playing;document.querySelector('#pause').textContent=playing?'Pause':'Play';lastAnimationTime=null;schedule();});
  document.querySelector('#seek').addEventListener('input',event=>{playing=false;document.querySelector('#pause').textContent='Play';poseState=skaterPose.seek(Number(event.target.value));lastAnimationTime=null;schedule();});
  const keyboard=bindKeyboardInput(canvas,packet=>{
   verification.keyboard_events++;verification.keyboard_packet=Array.from(packet,n=>n.toString(16).padStart(2,'0')).join('');
   if(stopped||resetting)return;
   try{traversal.step(packet);lastMovementTime=null;schedule();}catch(error){fail(error,'keyboard');}
  });
  const restart=document.querySelector('#restart');
  restart.addEventListener('click',async()=>{
   if(resetting)return;resetting=true;restart.disabled=true;
   try{
    const fresh=await createOriginalPhaseTraversal(motionWasm,motionRuntime,collisionRuntime,phaseRuntime,load);fresh.snapshot();
    traversal=fresh;skaterPosition=traversal.position;lastMovementTime=null;movementAccumulator=0;
    stopped=false;delete verification.preview_error;document.querySelector('#error').textContent='';
   }catch(error){fail(error,'reset');}
   finally{resetting=false;restart.disabled=false;}
   schedule();
  });
  window.addEventListener('resize',schedule);render();
}catch(error){fail(error);}
