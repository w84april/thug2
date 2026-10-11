export async function verifyScriptTokens(wasm,fixture,loadBinary){
  const {instance:{exports:e}}=await WebAssembly.instantiate(wasm);
  const memory=new Uint8Array(e.memory.buffer),initial=Uint8Array.from(await loadBinary(fixture.memory));
  memory.set(initial,fixture.base);const counts={};
  for(const [i,[fn,pointer,expected]] of fixture.cases.entries()){
    const name=fixture.functions[fn].name,result=e[name](pointer)>>>0;
    if(result!==expected)throw new Error(`${name} case ${i} at ${pointer.toString(16)}: ${result.toString(16)} != ${expected.toString(16)}`);
    counts[name]=(counts[name]??0)+1;
  }
  for(let i=0;i<initial.length;i++)if(memory[fixture.base+i]!==initial[i])throw new Error(`Bytecode modified at ${i}`);
  return {result:'pass',calls:fixture.cases.length,functions:Object.keys(counts).length,counts,
    assets:fixture.assets.map(a=>({archive:a.archive,member:a.member,sha256:a.sha256,bytes:a.size,
      tokens:a.token_count,compound_skips:a.compound_skips,script_skips:a.script_skips,terminator_offset:a.terminator_offset})),scope:fixture.scope};
}
