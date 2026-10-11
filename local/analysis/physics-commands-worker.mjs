import {verifyScriptState} from '/checks.mjs';
const binary=async name=>{const response=await fetch('/'+name);if(!response.ok)throw Error('Failed to load '+name);return new Uint8Array(await response.arrayBuffer());};
onmessage=async({data:{name,wasm}})=>{
 try{
  const response=await fetch('/'+name+'-fixtures.json');if(!response.ok)throw Error('Fixture fetch failed');
  const fixture=await response.json();const empty=await verifyScriptState(wasm,fixture,binary);
  let result=empty;
  if(name.endsWith('-context')){
   const nested=await verifyScriptState(wasm,{...fixture,scoped_event_services:{...fixture.scoped_event_services,pointer:fixture.outer_scope}},binary);
   result={result:'pass',original_cases:empty.cases,cases:empty.cases+nested.cases,calls:empty.calls+nested.calls,native_qb_callbacks:empty.native_qb_callbacks+nested.native_qb_callbacks,nan_fields_classification_only:empty.nan_fields_classification_only+nested.nan_fields_classification_only,null_scope:empty,outer_scope:nested};
  }
  postMessage({result});
 }catch(error){postMessage({error:String(error.stack||error)});}
};
