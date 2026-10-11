export async function verifyMotion(wasm,fixture,loadBinary){
  const {instance:{exports:e}}=await WebAssembly.instantiate(wasm);
  const memory=new Uint8Array(e.memory.buffer),v=new DataView(e.memory.buffer);
  const initial=Uint8Array.from(await loadBinary(fixture.memory)),base=fixture.base;
  const unhex=text=>Uint8Array.from(text.match(/../g)??[],b=>parseInt(b,16));
  for(const [name,,value] of fixture.globals)v.setUint32(e[name].value,value,true);
  let nanFields=0,processorNanChecks=0;const counts={},doubleDifferences=[],processorNanDifferences=[];
  const doubleBytes=new DataView(new ArrayBuffer(8));
  const doubleBits=x=>{doubleBytes.setFloat64(0,x,true);return doubleBytes.getBigUint64(0,true);};
  for(const [i,c] of fixture.cases.entries()){
    const expected=initial.slice(),info=fixture.functions[c.fn];
    for(const [at,data] of c.patches)expected.set(unhex(data),at-base);
    memory.set(expected,base);memory[e.thug_last_gameplay_flag.value]=0xad;
    if(c.errno!==undefined)v.setInt32(e.thug_math_errno.value,-123,true);
    const args=c.args.map((value,index)=>{
      if(!(info.float_args??[]).includes(index))return value;
      const bytes=new DataView(new ArrayBuffer(4));bytes.setUint32(0,value,true);return bytes.getFloat32(0,true);
    });
    const actual=e[info.name](...(info.this===false?args:[c.this,...args]));
    if(info.result==='double'){
      const wanted=new DataView(unhex(c.result).buffer).getFloat64(0,true);
      if(Number.isNaN(actual)&&Number.isNaN(wanted))nanFields++;
      else if(!Object.is(actual,wanted)){
        let difference=doubleBits(actual)-doubleBits(wanted);if(difference<0)difference=-difference;
        if(!info.double_ulp_limit||!Number.isFinite(actual)||!Number.isFinite(wanted)
            ||!Object.is(Math.fround(actual),Math.fround(wanted))||difference>BigInt(info.double_ulp_limit))
          throw new Error(`${info.name} case ${i}: ${actual} != ${wanted}`);
        doubleDifferences.push({case:i,original:c.result,port_bits:doubleBits(actual).toString(16),ulp:Number(difference)});
      }
      if(c.acos_inputs?.length){
        const input=new DataView(unhex(c.acos_inputs[0]).buffer).getFloat64(0,true);
        const adapter=e.thug_platform_acos_x87_single(input);
        if(!Object.is(Math.abs(actual),adapter)&&!(Number.isNaN(actual)&&Number.isNaN(adapter)))
          throw new Error(`${info.name} case ${i}: angle differs from adapter on original acos input`);
      }
    }else if(['byte','word'].includes(info.result)&&(actual>>>0)!==c.result)throw new Error(`${info.name} case ${i}: ${actual>>>0} != ${c.result}`);
    for(const [at,data] of c.outputs)expected.set(unhex(data),at-base);
    const ev=new DataView(expected.buffer);
    for(let j=0;j<expected.length;){
      const at=base+j;
      // Only rows 0 and 2 of a Y rotation whose original trig argument was
      // observed infinite. Intel masked-invalid yields NaN; Unicorn leaves
      // infinity unchanged. Keep and report every differing original word.
      if(at%4===0&&(c.matrix_infinity_calls??[]).some(t=>(t.angle_bits&0x7fffffff)===0x7f800000
          &&((at>=t.target&&at<t.target+16)||(at>=t.target+32&&at<t.target+48)))){
        if(!fixture.matrix_infinity_specification||!Number.isNaN(v.getFloat32(at,true)))
          throw new Error(`${info.name} case ${i}: expected documented NaN at ${at.toString(16)}`);
        processorNanChecks++;
        if(!Number.isNaN(ev.getFloat32(j,true)))processorNanDifferences.push({case:i,address:at,original_word:ev.getUint32(j,true),processor:'NaN'});
        j+=4;continue;
      }
      if(at%4===0&&fixture.float_ranges.some(([start,length])=>at>=start&&at+4<=start+length)
          &&Number.isNaN(v.getFloat32(at,true))&&Number.isNaN(ev.getFloat32(j,true))){nanFields++;j+=4;continue;}
      if(memory[at]!==expected[j])throw new Error(`${info.name} case ${i} address ${at.toString(16)}: ${memory[at]} != ${expected[j]}`);
      j++;
    }
    if(memory[e.thug_last_gameplay_flag.value]!==c.flag)throw new Error(`${info.name} case ${i}: flag side effect`);
    if(c.errno!==undefined&&v.getInt32(e.thug_math_errno.value,true)!==c.errno)throw new Error(`${info.name} case ${i}: math errno mismatch`);
    counts[info.name]=(counts[info.name]??0)+1;
  }
  return {result:'pass',cases:fixture.cases.length,functions:Object.keys(counts).length,counts,nan_fields_classification_only:nanFields,
    ...(doubleDifferences.length?{double_transcendental_differences:doubleDifferences}:{}),
    ...(processorNanChecks?{matrix_infinity_specification_checks:processorNanChecks,matrix_infinity_documented_differences:processorNanDifferences}:{}),
    scope:fixture.scope??'Original braking, acceleration, eligibility, alignment and gravity routines with real stat/parameter callees; constructed states, no full movement loop'};
}
