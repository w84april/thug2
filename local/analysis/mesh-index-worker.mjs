onmessage=async({data:{name,wasm}})=>{
 try {
  const {verifyScriptState}=await import(['training-texture-asset','training-model-file','training-material-buffer','training-scene-construction','training-mesh-index'].includes(name)?'/training-texture-checks.mjs':name==='training-setup'?'/setup-checks.mjs':name==='training-prop-script'?'/prop-script-checks.mjs':['model-initialize-prefix','model-configuration-prefix'].includes(name)?'/prefix-checks.mjs':['training-model-component','training-model-initialize','training-model-configuration'].includes(name)?'/model-checks.mjs':'/checks.mjs');
  const response=await fetch('/'+name+'-fixtures.json');if(!response.ok)throw Error('Fixture fetch failed');
  const fixture=await response.json();
  const load=async file=>{const r=await fetch('/'+file);if(!r.ok)throw Error('Asset fetch failed: '+file);return new Uint8Array(await r.arrayBuffer());};
  const result=await verifyScriptState(wasm,fixture,load);
  if(name==='training-load')Object.assign(result,{completed_setup_calls:4,completed_execute_calls:1,execute_result:0,final_instruction:0,ready_skeleton_bones:34,playable:false});
  if(name==='training-setup')Object.assign(result,{completed_setup_calls:10,interrupted_execute_calls:2,next_missing_handler:'Kill at 0x5a5030',playable:false});
  postMessage({result});
 }catch(error){postMessage({error:String(error.stack||error)});}
};
