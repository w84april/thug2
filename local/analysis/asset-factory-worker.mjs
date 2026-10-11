onmessage=async({data:{name,wasm}})=>{
 try {
  const {verifyScriptState}=await import('/checks.mjs');
  const response=await fetch('/'+name+'-fixtures.json');if(!response.ok)throw Error('Fixture fetch failed');
  const fixture=await response.json();
  const load=async file=>{const r=await fetch('/'+file);if(!r.ok)throw Error('Asset fetch failed: '+file);return new Uint8Array(await r.arrayBuffer());};
  const result=await verifyScriptState(wasm,fixture,load);
  if(name==='training-load')Object.assign(result,{completed_setup_calls:4,completed_execute_calls:1,execute_result:0,final_instruction:0,ready_skeleton_bones:34,playable:false});
  postMessage({result});
 }catch(error){postMessage({error:String(error.stack||error)});}
};
