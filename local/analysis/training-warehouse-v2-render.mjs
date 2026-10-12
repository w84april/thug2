import {loadTraining} from './training-webgl-v1-load.mjs';
const canvas=document.querySelector('#world'),status=document.querySelector('#status');
const cached=new Map();
const load=n=>{if(!cached.has(n))cached.set(n,(async()=>{const r=await fetch('/'+n);if(!r.ok)throw Error('Cannot load '+n);return new Uint8Array(await r.arrayBuffer());})());return cached.get(n);};
const fail=error=>{document.querySelector('#error').textContent=String(error.stack??error);status.textContent='Rendering preview stopped';};
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
    uniform mat4 projection;uniform mat4 camera;out vec4 color;out vec2 texcoord;
    void main(){gl_Position=projection*camera*vec4(p,1);color=c.bgra;texcoord=uv;}`));
  gl.attachShader(program,shader(gl.FRAGMENT_SHADER,`#version 300 es
    precision highp float;in vec4 color;in vec2 texcoord;uniform sampler2D image;out vec4 pixel;
    void main(){vec4 t=texture(image,texcoord);if(t.a<0.2)discard;pixel=vec4(t.rgb*color.rgb,1);}`));
  gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(program));gl.useProgram(program);
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
  const normalize=a=>{const l=Math.hypot(...a);return a.map(x=>x/l);},cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]],dot=(a,b)=>a.reduce((s,x,i)=>s+x*b[i],0);
  let target=view.camera.target.slice();
  const radius=Math.hypot(...low.map((x,i)=>high[i]-x))/2;
  let yaw=view.camera.yaw,pitch=view.camera.pitch,distance=view.camera.distance,drag=null,frame=0,viewMode='Warehouse';
  const cameraPointer=0x6100000,e=world.exports,v=world.view;
  v.setFloat32(e.thug_camera_default_fov_v2.value,60,true);v.setFloat32(e.thug_camera_display_ratio_v2.value,1,true);e.thug_camera_object_construct_v2(cameraPointer);
  gl.enable(gl.DEPTH_TEST);gl.disable(gl.CULL_FACE);gl.clearColor(.045,.08,.105,1);
  const verification={...world.summary,result:'drawing pending',original_gpu_storage_hashes_equal:true,ordered_storage_buffers:stored.length,ordered_storage_sha256:storageProof.ordered_storage_sha256,uploaded_mips:uploadedMips,draw_calls:draws.length,bounds:[low,high],renderer_adapter:'original CreatedAtStart LevelGeometry; first material pass/full-detail strips; no original visibility/transforms/render-state/frame equivalence',view_metadata_sha256:'3d477762d9e9f5159379e833368c9b16001dca9f0dd424393a921fec8ac973cc',initial_static_sectors:view.initial_static_sector_count,original_gameplay_camera_verified:false,completion_credit:0,frame_equivalence_verified:false,load_ms:Math.round(performance.now()-started)};
  function render(){
    frame++;canvas.width=Math.round(canvas.clientWidth*Math.min(devicePixelRatio,2));canvas.height=Math.round(canvas.clientHeight*Math.min(devicePixelRatio,2));gl.viewport(0,0,canvas.width,canvas.height);
    v.setFloat32(e.thug_camera_display_ratio_v2.value,canvas.height/canvas.width,true);e.thug_camera_projection_v2(cameraPointer);
    const fov=v.getFloat32(cameraPointer+0xb0,true)*Math.PI/180,near=12,far=radius*10,f=1/Math.tan(fov/2),aspect=canvas.width/canvas.height;
    gl.uniformMatrix4fv(projectionUniform,false,new Float32Array([f/aspect,0,0,0,0,f,0,0,0,0,(far+near)/(near-far),-1,0,0,2*far*near/(near-far),0]));
    const eye=[target[0]+Math.sin(yaw)*Math.cos(pitch)*distance,target[1]+Math.sin(pitch)*distance,target[2]+Math.cos(yaw)*Math.cos(pitch)*distance];
    const z=normalize(eye.map((x,i)=>x-target[i])),x=normalize(cross([0,1,0],z)),y=cross(z,x);
    gl.uniformMatrix4fv(cameraUniform,false,new Float32Array([x[0],y[0],z[0],0,x[1],y[1],z[1],0,x[2],y[2],z[2],0,-dot(x,eye),-dot(y,eye),-dot(z,eye),1]));
    gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
    for(const d of draws){gl.bindVertexArray(d.vao);gl.bindTexture(gl.TEXTURE_2D,d.texture);gl.drawElements(gl.TRIANGLE_STRIP,d.count,gl.UNSIGNED_SHORT,0);}
    const error=gl.getError();if(error)throw Error('WebGL error '+error);
    // Inspect pixels after the real draw. A clear buffer alone cannot pass.
    const pixels=new Uint8Array(64*64*4);gl.readPixels(Math.floor(canvas.width/2)-32,Math.floor(canvas.height/2)-32,64,64,gl.RGBA,gl.UNSIGNED_BYTE,pixels);
    const colors=new Set();for(let i=0;i<pixels.length;i+=4)colors.add(pixels[i]+','+pixels[i+1]+','+pixels[i+2]);
    verification.result=colors.size>1?'rendered original geometry':'clear-buffer only';verification.center_pixel_colors=colors.size;verification.frames=frame;verification.yaw=yaw;verification.pitch=pitch;verification.distance=distance;verification.eye=eye;verification.target=target.slice();verification.view_mode=viewMode;
    document.querySelector('#verification').textContent=JSON.stringify(verification);status.textContent=`${viewMode} view · ${draws.length.toLocaleString()} initial static meshes · ${world.summary.textures} original textures`;
  }
  const schedule=()=>requestAnimationFrame(()=>{try{render();}catch(error){fail(error);}});
  canvas.addEventListener('pointerdown',event=>{drag=[event.clientX,event.clientY];canvas.setPointerCapture(event.pointerId);});
  canvas.addEventListener('pointerup',()=>{drag=null;});canvas.addEventListener('pointercancel',()=>{drag=null;});
  canvas.addEventListener('pointermove',event=>{if(!drag)return;yaw-=(event.clientX-drag[0])*.006;pitch=Math.max(-1.4,Math.min(1.4,pitch+(event.clientY-drag[1])*.006));drag=[event.clientX,event.clientY];schedule();});
  canvas.addEventListener('wheel',event=>{event.preventDefault();distance=Math.max(24,Math.min(radius*8,distance*Math.exp(event.deltaY*.001)));schedule();},{passive:false});
  document.querySelector('#reset').addEventListener('click',()=>{target=view.camera.target.slice();yaw=view.camera.yaw;pitch=view.camera.pitch;distance=view.camera.distance;viewMode='Warehouse';schedule();});
  document.querySelector('#overview').addEventListener('click',()=>{target=low.map((x,i)=>(x+high[i])/2);yaw=.8;pitch=.6;distance=radius*1.9;viewMode='Entire TR bundle';schedule();});window.addEventListener('resize',schedule);render();
}catch(error){fail(error);}
