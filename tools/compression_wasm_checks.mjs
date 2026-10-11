export async function verifyCompression(wasm,fixture,loadBinary,verifyState) {
  const checked=await verifyState(wasm,fixture,loadBinary);
  const {instance:{exports:e}}=await WebAssembly.instantiate(wasm);
  const memory=new Uint8Array(e.memory.buffer),base=fixture.base;
  const unhex=text=>Uint8Array.from(text.match(/../g)??[],s=>parseInt(s,16));
  const input=base+0x1000,output=base+0x50000,state=base+0x71000;
  let bytes=0;
  for(const [index,stream] of fixture.roundtrips.entries()){
    const encoded=unhex(stream.encoded),original=unhex(stream.original);
    memory.set(encoded,input);memory.fill(0xcd,output,output+original.length+32);
    for(let j=0;j<4096;j++)memory[state+j]=(j*31+index*7)&255;
    const end=e.thug_lzss_decode_unchecked(state,input,output,encoded.length)>>>0;
    if(end!==output+original.length)throw new Error(`Compression roundtrip ${index} length`);
    if(!original.every((b,i)=>memory[output+i]===b))throw new Error(`Compression roundtrip ${index} data`);
    if(!memory.subarray(end,end+32).every(b=>b===0xcd))throw new Error(`Compression roundtrip ${index} guard`);
    bytes+=original.length;
  }
  return {...checked,decoder_roundtrips:fixture.roundtrips.length,roundtrip_bytes:bytes};
}
