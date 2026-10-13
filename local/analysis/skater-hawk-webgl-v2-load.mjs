// Fixture-backed integration prototype. Only raw serialized assets are inputs;
// no original output snapshots or decoded geometry are loaded here. Packed rest storage is used before original pose skinning.
export async function loadHawk(wasm, runtime, loadBinary) {
  const {instance:{exports:e}} = await WebAssembly.instantiate(wasm);
  const memory = new Uint8Array(e.memory.buffer), view = new DataView(e.memory.buffer);
  const u32 = p => view.getUint32(p,true), set = (p,n) => view.setUint32(p,n,true);
  const symbols = new Map();
  for (const [original,name,offset=0] of runtime.pointer_exports) symbols.set(original,e[name].value+offset);
  const {instance:{exports:ports}} = await WebAssembly.instantiate(await loadBinary(runtime.ports),{env:{memory:e.memory}});
  const slots = [];
  for (const spec of runtime.callbacks) {
    const slot = e.__indirect_function_table.grow(1);
    e.__indirect_function_table.set(slot,ports[spec.export]);
    for (const at of spec.slots??[]) slots.push([at,slot]);
    if (spec.original!==undefined) symbols.set(spec.original,slot);
  }
  for (const [i,name] of runtime.memory_exports.entries()) {
    const slot=e.__indirect_function_table.grow(1);e.__indirect_function_table.set(slot,ports[name]);
    slots.push([runtime.memory_adapter+4*(i+1),slot]);
  }
  const relocated = n => symbols.get(n)??n;
  memory.set(new Uint8Array(await loadBinary(runtime.memory)),runtime.base);
  for (const [at,n] of slots) set(at,n);
  for (const [name,n,offset=0] of runtime.pointer_initializers) set(e[name].value+offset,relocated(n));
  runtime.globals.forEach(([name,width,offset,n],i)=> {
    const value=runtime.pointer_globals.includes(i)?relocated(n):n;
    view[width===1?'setUint8':'setUint32'](e[name].value+offset,value,true);
  });
  // Resolve the material header from this run, rather than trusting the fixed
  // address in the original isolated input arena.
  set(runtime.header+24,0);
  const dictionary=e.thug_texture_dictionary_get_buffer_draft(0x12345678,runtime.texture_data,runtime.texture_bytes,0,0,0,0,runtime.memory_adapter);
  const textureTable=u32(dictionary+12);
  const materialTable=e.thug_material_file_parse_draft(runtime.file,textureTable,runtime.memory_adapter);
  set(runtime.header+24,materialTable);
  const meshes=[];
  for (const [i,descriptor] of runtime.meshes.entries()) {
    const at=runtime.mesh_base+i*216;
    e.thug_render_mesh_initialize(at);
    e.thug_mesh_file_parse_draft(at,runtime.file,descriptor.key,runtime.header,0,descriptor.dynamic,runtime.memory_adapter);
    const vb=u32(at+0xcc),bytes=u32(vb);
    if(!(u32(at+0x78)&1)||!u32(at+0x94))throw Error('Expected original packed Hawk rest vertices');
    const stride=view.getUint8(at+0x18), vertices=view.getUint16(at+0x22,true),fvf=u32(at+0x38);
    if(bytes!==stride*vertices||stride!==descriptor.stride||vertices!==descriptor.vertices||fvf!==descriptor.fvf)throw Error('Mesh vertex layout differs from original trace');
    const packed=u32(at+0x94),vertexData=memory.slice(packed,packed+vertices*76);
    const strips=[];
    for(let slot=0;slot<8;slot++) {
      const count=view.getUint16(at+0x24+slot*2,true);
      if(!count)continue;
      const ib=u32(at+0x54+slot*4),indexGPU=u32(ib+12),indexCPU=u32(ib+16);
      const data=memory.slice(indexCPU,indexCPU+count*2);
      if(!data.every((n,j)=>n===memory[indexGPU+256+j]))throw Error('Index upload mismatch');
      strips.push({slot,count,data});
    }
    const material=u32(at+0x14);
    const texture=u32(material+0x30),textureHandle=texture?u32(texture+16):0;
    meshes.push({at,stride:76,originalStride:stride,vertices,fvf,vertexData,strips,material,materialKey:u32(material),passes:u32(material+8),texture,textureHandle,flags:u32(at)});
  }
  if(u32(runtime.file)!==u32(runtime.file+4))throw Error('Unconsumed serialized scene input');
  if(u32(textureTable+8)!==20||u32(materialTable+8)!==19)throw Error('Incomplete original Hawk texture/material tables');
  const textures=new Map();
  for(let i=0;i<u32(runtime.base+0x1008);i++) {
    const at=runtime.base+0xa00000+i*64;
    if(u32(at)!==1)continue;
    const pointer=u32(at+40),width=u32(at+8),height=u32(at+12),levels=u32(at+16),format=u32(at+24),mips=[];
    for(let level=0;level<levels;level++) {
      const p=u32(pointer+16+level*12),n=u32(pointer+20+level*12);
      mips.push(memory.slice(p,p+n));
    }
    textures.set(pointer,{pointer,width,height,levels,format,mips});
  }
  const summary={meshes:meshes.length,vertices:meshes.reduce((n,m)=>n+m.vertices,0),indices:meshes.reduce((n,m)=>n+m.strips.reduce((s,x)=>s+x.count,0),0),textures:textures.size,materials:u32(materialTable+8),loader_calls:2+runtime.meshes.length*2,decoded_output_inputs:0,playable:false};
  return {exports:e,memory,view,meshes,textures,summary,memoryAdapter:runtime.memory_adapter};
}
