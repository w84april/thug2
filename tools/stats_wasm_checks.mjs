export async function verifyStats(wasm,fixture,loadBinary){
  const {instance:{exports:e}}=await WebAssembly.instantiate(wasm);
  const memory=new Uint8Array(e.memory.buffer),v=new DataView(e.memory.buffer);
  const initial=Uint8Array.from(await loadBinary(fixture.memory)),base=fixture.base;
  const unhex=text=>Uint8Array.from(text.match(/../g)??[],b=>parseInt(b,16));
  for(const [name,,value] of fixture.globals)v.setUint32(e[name].value,value,true);
  let nanFields=0,pairQuietingChecks=0;const counts={},pairQuietingDifferences=[];
  for(const [i,c] of fixture.cases.entries()){
    const expected=initial.slice(),info=fixture.functions[c.fn];
    for(const [at,data] of c.patches)expected.set(unhex(data),at-base);
    memory.set(expected,base);memory[e.thug_last_gameplay_flag.value]=0xad;
    const args=info.this?[c.this,...c.args]:c.args;
    const actual=e[info.name](...args);
    if(info.result==='double'){
      const wanted=new DataView(unhex(c.result).buffer).getFloat64(0,true);
      if(Number.isNaN(actual)&&Number.isNaN(wanted))nanFields++;
      else if(!Object.is(actual,wanted))throw new Error(`${info.name} case ${i}: ${actual} != ${wanted}`);
    }else if((actual>>>0)!==c.result)throw new Error(`${info.name} case ${i}: ${actual>>>0} != ${c.result}`);
    for(const [at,data] of c.outputs)expected.set(unhex(data),at-base);
    if(c.fn==='0x476df0'){
      // Intel FLD with masked invalid quiets an SNaN. Unicorn's copied words
      // retain the signaling bit in these cases; retain those raw oracle values
      // in the fixture and report each specification-based exception explicitly.
      const ev=new DataView(expected.buffer),output=c.args[1];
      for(const at of [output+4,output+8]){
        const word=ev.getUint32(at-base,true);
        if((word&0x7f800000)===0x7f800000&&(word&0x7fffff)){
          pairQuietingChecks++;
          const wanted=(word|0x400000)>>>0,actualWord=v.getUint32(at,true);
          if(actualWord!==wanted)throw new Error(`pair quieting case ${i}: ${actualWord} != ${wanted}`);
          if(word!==wanted)pairQuietingDifferences.push({case:i,address:at,oracle:word,specification:wanted});
          ev.setUint32(at-base,wanted,true);
        }
      }
    }
    for(let j=0;j<expected.length;j++)if(memory[base+j]!==expected[j])throw new Error(`${info.name} case ${i} byte ${j}: ${memory[base+j]} != ${expected[j]}`);
    if(memory[e.thug_last_gameplay_flag.value]!==c.flag)throw new Error(`${info.name} case ${i}: flag side effect`);
    counts[info.name]=(counts[info.name]??0)+1;
  }
  return {result:'pass',cases:fixture.cases.length,functions:Object.keys(counts).length,counts,
    nan_fields_classification_only:nanFields,pair_nan_quieting_checks:pairQuietingChecks,
    pair_nan_documented_oracle_differences:pairQuietingDifferences,
    scope:'Complete stat getter, evaluator and named lookup; constructed script/object/player graphs; no QB loader or full movement loop'};
}
