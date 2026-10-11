import {verifyScriptState} from './script_state_wasm_checks.mjs';
export async function verifyDecalPrerequisites(wasm,fixture,load) {
  const initial_globals={thug_decal_reserved_slots:128,thug_decal_fade_step:8,thug_decal_area_threshold:0x47a20000};
  {
    const {instance:{exports:e}}=await WebAssembly.instantiate(wasm),v=new DataView(e.memory.buffer);
    for(const [name,word] of Object.entries(initial_globals))
      if(v.getUint32(e[name].value,true)!==word)throw new Error('Original initial global: '+name);
  }
  const results={};
  for(const name of ['storage','grid','geometry','lifetime','lighting'])results[name]=await verifyScriptState(wasm,fixture[name],load);
  const values=Object.values(results),counts=Object.assign({},...values.map(r=>r.counts));
  return {result:'pass',cases:values.reduce((s,r)=>s+r.cases,0),calls:values.reduce((s,r)=>s+r.calls,0),
    functions:Object.keys(counts).length,counts,device_callbacks:results.storage.device_callbacks,
    nan_fields_classification_only:values.reduce((s,r)=>s+r.nan_fields_classification_only,0),initial_globals,...results};
}
