import {verifyScriptState} from './model-initialize-prefix-checks.mjs';
// Only two deliberately invalid infinite-angle inputs use the Intel specified
// masked-invalid result. Preserve the raw emulator record and every memory byte.
export async function verifySkaterMatrix(wasm,fixture,loadBinary){
 const copy=structuredClone(fixture),corrections=fixture.fcos_infinity_specification.cases;
 if(corrections.length!==2)throw Error('Missing infinity boundary cases');
 let differences=0;
 for(const row of corrections){
  const c=copy.cases[row.case_index],s=c.steps[0];
  if(c.steps.length!==1||s.fn!=='0x406560'||s.args[2]!==row.angle_bits||
     ![0x7f800000,0xff800000].includes(row.angle_bits)||s.result!==row.raw_emulator_result||row.adapter_result!==0)
   throw Error('Infinity correction does not describe this exact original step');
  differences+=s.result!==row.adapter_result;s.result=row.adapter_result;
 }
 return {...await verifyScriptState(wasm,copy,loadBinary),fcos_infinity_cases:corrections.length,fcos_infinity_emulator_differences:differences};
}
