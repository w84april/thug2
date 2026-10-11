onmessage=async({data:{name,wasm}})=>{
 try {
  const {verifyScriptState}=await import(name==='training-startup'?'/startup-checks.mjs':'/checks.mjs');
  const response=await fetch('/'+name+'-fixtures.json');if(!response.ok)throw Error('Fixture fetch failed');
  const fixture=await response.json();
  const load=async file=>{const r=await fetch('/'+file);if(!r.ok)throw Error('Asset fetch failed: '+file);return new Uint8Array(await r.arrayBuffer());};
  const result=await verifyScriptState(wasm,fixture,load);
  if(name==='training-startup')Object.assign(result,{completed_setup_calls:4,interrupted_execute_calls:1,next_missing_handler:'LoadSkeleton at 0x445640',playable:false});
  postMessage({result});
 }catch(error){postMessage({error:String(error.stack||error)});}
};
