// Independent original-instruction fixture comparison; reference is never engine input.
const bytes=s=>Uint8Array.from(s.match(/../g)??[],x=>parseInt(x,16));
const hex=b=>Array.from(b,x=>x.toString(16).padStart(2,'0')).join('');
export async function verifyGoalActive(wasm,reference){
 const module=await WebAssembly.compile(wasm);if(WebAssembly.Module.imports(module).length)throw Error('Unexpected runtime imports');
 const {exports:e}=await WebAssembly.instantiate(module),m=new Uint8Array(e.memory.buffer),v=new DataView(e.memory.buffer),results=[];
 const relocations=new Map(reference.pointer_relocations.map(([name,native])=>[native,e[name].value]));
 function relocateGoalPointers(raw){const b=bytes(raw),d=new DataView(b.buffer);for(let at=0;at<b.length;at+=128){const pointer=d.getUint32(at,true);if(!relocations.has(pointer))throw Error('Unknown original goal table');d.setUint32(at,relocations.get(pointer),true);}return b;}
 for(const c of reference.cases){
  for(const [name,p] of reference.regions)m.set(name==='goals'?relocateGoalPointers(c.before[name]):bytes(c.before[name]),p);
  for(const [name,,value] of reference.globals)v.setUint32(e[name].value,value,true);
  const params=reference.regions.find(x=>x[0]==='parameters')[1],result=e.thug_script_goal_is_active_v1(params,0);
  if(result!==c.result)throw Error('Original byte result differs '+c.label);
  for(const [name,p,n] of reference.regions){const expected=name==='goals'?relocateGoalPointers(c.after[name]):bytes(c.after[name]);if(hex(m.subarray(p,p+n))!==hex(expected))throw Error('Original memory differs '+c.label+'/'+name);}
  results.push({label:c.label,result,all_declared_bytes_equal:true});
 }
 return {result:'pass',cases:results.length,true_results:results.filter(x=>x.result===1).length,missing_and_inactive_results:results.filter(x=>x.result===0).length,original_wrapper_bytes:reference.original_wrapper_bytes,original_wrapper_instructions:reference.wrapper_instruction_count,scope:reference.scope,byte_abi_result_and_memory_equal:true,method_table_relocations:reference.pointer_relocations,runtime_imports:0,completion_credit:0,matching_credit:0,playable:false,results};
}
