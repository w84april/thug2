import {verifyScriptState} from '../../tools/script_state_wasm_checks.mjs';
export async function verifyInputCommands(wasm,fixture,loadBinary){
 const {instance:{exports:e}}=await WebAssembly.instantiate(wasm),v=new DataView(e.memory.buffer);
 for(const [i,row] of fixture.descriptor_rows.entries()){
  for(let j=0;j<6;j++){
   const actual=v.getUint32(e.thug_input_commands_draft.value+i*24+j*4,true);
   if(j===2&&row.member){
    if(e.__indirect_function_table.get(actual)!==e[row.member])throw Error(`Input descriptor ${i} member`);
   }else if(actual!==row.words[j])throw Error(`Input descriptor ${i} word ${j}`);
  }
 }
 return {...await verifyScriptState(wasm,fixture,loadBinary),descriptor_rows_verified:fixture.descriptor_rows.length};
}
