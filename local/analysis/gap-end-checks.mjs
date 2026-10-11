export async function verifyScriptState(wasm,fixture,loadBinary) {
  const {instance:{exports:e}}=await WebAssembly.instantiate(wasm);
  const memory=new Uint8Array(e.memory.buffer),v=new DataView(e.memory.buffer),base=fixture.base;
  const initial=Uint8Array.from(await loadBinary(fixture.memory));
  const unhex=text=>{
    const bytes=new Uint8Array(text.length/2);
    for(let i=0;i<bytes.length;i++)bytes[i]=parseInt(text.slice(i*2,i*2+2),16);
    return bytes;
  };
  const pointerSymbols=new Map();
  for(const [original,name,text] of fixture.pointer_symbols??[]){
    const address=e[name].value,bytes=new TextEncoder().encode(text+'\0');
    if(!bytes.every((b,i)=>memory[address+i]===b))throw new Error(`Relocated literal ${name}`);
    pointerSymbols.set(original,address);
  }
  for(const [original,name,offset=0] of fixture.pointer_exports??[])pointerSymbols.set(original,e[name].value+offset);
  const pointerFields=new Set(fixture.pointer_fields??[]);
  const relocated=value=>pointerSymbols.get(value)??value;
  const replacements=[];
  for(const [original,name] of fixture.function_exports??[]){
    // A recovered routine may register this callback itself. Reuse its linked
    // table identity so pointers written by C and relocated fixture inputs agree.
    const table=e.__indirect_function_table;let slot=-1;
    for(let i=0;i<table.length;i++)if(table.get(i)===e[name]){slot=i;break;}
    if(slot<0){slot=table.grow(1);table.set(slot,e[name]);}
    pointerSymbols.set(original,slot);
  }
  for(const spec of fixture.native_callbacks??(fixture.native_callback?[fixture.native_callback]:[])){
    const engineImports=Object.fromEntries((spec.engine_imports??[]).map(name=>[name,e[name]]));
    const {instance:{exports:callback}}=await WebAssembly.instantiate(await loadBinary(spec.module),{env:{memory:e.memory,...engineImports}});
    const slot=e.__indirect_function_table.grow(1);
    e.__indirect_function_table.set(slot,callback[spec.export]);
    for(const at of spec.slots??[])replacements.push([at,slot]);
    if(spec.original!==undefined)pointerSymbols.set(spec.original,slot);
  }
  if(fixture.method_slot!==undefined){
    const {instance:{exports:callback}}=await WebAssembly.instantiate(await loadBinary('script-wait-fixture.wasm'),{env:{memory:e.memory}});
    const slot=e.__indirect_function_table.grow(1);
    e.__indirect_function_table.set(slot,callback.fixture_script_wait);
    replacements.push([fixture.method_slot,slot]);
  }
  if(fixture.memory_adapter){
    const {instance:{exports:allocator}}=await WebAssembly.instantiate(await loadBinary(fixture.memory_fixture??'script-branch-memory.wasm'),{env:{memory:e.memory}});
    const names=fixture.memory_exports??['fixture_branch_allocate','fixture_branch_release'];
    for(const [index,name] of names.entries()){
      const slot=e.__indirect_function_table.grow(1);e.__indirect_function_table.set(slot,allocator[name]);
      replacements.push([fixture.memory_adapter+4*(index+1),slot]);
    }
  }
  let nanFields=0,quietedFields=0,quietedDoubles=0,indeterminateBytes=0,stackTexts=0,callbacks=0,steps=0;const counts={};
  // Pass float inputs as integer bits until they are inside Wasm. JavaScript
  // argument arrays may canonicalize NaN payloads during JIT optimization.
  // This adapter only reinterprets arguments and calls the real engine export.
  const floatCalls=new Map();
  async function floatCall(f,argc) {
    const key=f.name+':'+argc;
    if(floatCalls.has(key))return floatCalls.get(key);
    const leb=n=>{const b=[];do{const x=n&127;n>>>=7;b.push(x|(n?128:0));}while(n);return b;};
    const section=(id,data)=>[id,...leb(data.length),...data];
    const floats=new Set(f.float_args.map(i=>i+(f.this===false?0:1)));
    const result=f.result==='void'?[]:[f.result==='double'?0x7c:0x7f];
    const type=params=>[0x60,...leb(params.length),...params,result.length,...result];
    const params=Array.from({length:argc},(_,i)=>floats.has(i)?0x7d:0x7f);
    const body=[0];
    for(let i=0;i<argc;i++){body.push(0x20,...leb(i));if(floats.has(i))body.push(0xbe);}
    body.push(0x10,0,0x0b);
    const bytes=Uint8Array.from([0,97,115,109,1,0,0,0,
      ...section(1,[2,...type(params),...type(params.map(()=>0x7f))]),
      ...section(2,[1,3,101,110,118,6,116,97,114,103,101,116,0,0]),
      ...section(3,[1,1]),...section(7,[1,3,114,117,110,0,1]),
      ...section(10,[1,...leb(body.length),...body])]);
    const {instance}=await WebAssembly.instantiate(bytes,{env:{target:e[f.name]}});
    floatCalls.set(key,instance.exports.run);return instance.exports.run;
  }
  function checkMemory(expected,label,floatFields=fixture.float_fields,quietFields=[],quietDoubleFields=[],indeterminate=[],compressions=[]) {
    for(const [at,value] of replacements)new DataView(expected.buffer).setUint32(at-base,value,true);
    // Only bytes proven to come from compression's uninitialized automatic
    // string tails may differ. Later original writes remove those bytes from
    // the allowance. Never copy oracle padding into the running Wasm memory.
    const unknown=new Set(),proven=new Set();
    for(const record of compressions){
      const p=record.destination,wanted=[[p+0x23,57],[p+0x65,55]];
      if(!Number.isInteger(p)||p<base||p+0x9c>base+expected.length||JSON.stringify(record.indeterminate_tails)!==JSON.stringify(wanted))
        throw Error('Invalid compression provenance');
      for(const [at,n] of wanted)for(let k=0;k<n;k++)proven.add(at+k);
    }
    for(const [at,length] of indeterminate){
      if(at<base||at+length>base+expected.length||length<1)throw Error('Invalid indeterminate-byte range');
      for(let k=0;k<length;k++){if(!proven.has(at+k)||unknown.has(at+k))throw Error('Unproven or overlapping indeterminate byte');unknown.add(at+k);expected[at+k-base]=memory[at+k];}
      indeterminateBytes+=length;
    }
    const ev=new DataView(expected.buffer),exceptions=new Set();
    for(const at of pointerFields){
      if([0,1,2,3].some(k=>unknown.has(at+k)))continue;
      // Reused heap storage may hold a method pointer in one case and a float
      // in another. Relocate only registered identities; other words still
      // receive the exact byte comparison or an explicitly typed float check.
      const raw=ev.getUint32(at-base,true);
      if(!pointerSymbols.has(raw))continue;
      if(v.getUint32(at,true)!==relocated(raw))throw new Error(`${label} pointer ${at.toString(16)}: ${v.getUint32(at,true)} != ${relocated(raw)}`);
      exceptions.add(at);
    }
    for(const at of quietFields){
      const raw=ev.getUint32(at-base,true),wanted=((raw&0x7f800000)===0x7f800000&&(raw&0x7fffff)?raw|0x400000:raw)>>>0;
      if(v.getUint32(at,true)!==wanted)throw new Error(`${label} quieted float ${at.toString(16)}`);
      if(wanted!==raw)quietedFields++;exceptions.add(at);
    }
    // Unicorn can preserve a signaling payload during FLD/FSTP promotion.
    // Require every double bit exactly, with only the physical x87 quiet bit set.
    for(const at of quietDoubleFields){
      const raw=ev.getBigUint64(at-base,true),wanted=(raw&0x7ff0000000000000n)===0x7ff0000000000000n&&(raw&0xfffffffffffffn)?raw|0x8000000000000n:raw;
      if(v.getBigUint64(at,true)!==wanted)throw new Error(`${label} quieted double ${at.toString(16)}`);
      if(wanted!==raw)quietedDoubles++;exceptions.add(at);exceptions.add(at+4);
    }
    for(const at of floatFields){
      if(!exceptions.has(at)&&Number.isNaN(v.getFloat32(at,true))&&Number.isNaN(ev.getFloat32(at-base,true))){nanFields++;exceptions.add(at);}
    }
    // Compare every byte with word reads for aligned arenas. An unaligned
    // relocated pointer or float affects only its two intersecting words;
    // compare the uncovered bytes there instead of rescanning the whole arena.
    if(base%4===0&&expected.length%4===0){
      const aligned=[...exceptions].every(at=>at%4===0),covered=new Set(),words=aligned?exceptions:new Set();
      if(!aligned)for(const at of exceptions)for(let k=0;k<4;k++){covered.add(at+k);words.add((at+k)&~3);}
      const actualWords=new Uint32Array(e.memory.buffer,base,expected.length/4),wantedWords=new Uint32Array(expected.buffer);
      for(let j=0;j<wantedWords.length;j++){
        if(actualWords[j]!==wantedWords[j]){
          const at=base+j*4;
          if(!words.has(at))throw new Error(`${label} word ${at.toString(16)}: ${actualWords[j]} != ${wantedWords[j]}`);
          if(!aligned)for(let k=0;k<4;k++)if(!covered.has(at+k)&&memory[at+k]!==expected[j*4+k])throw new Error(`${label} byte ${(at+k).toString(16)}`);
        }
      }
    }else{
      for(let j=0;j<expected.length;){
        const at=base+j;
        if(exceptions.has(at)){j+=4;continue;}
        if(memory[at]!==expected[j])throw new Error(`${label} byte ${at.toString(16)}: ${memory[at]} != ${expected[j]}`);
        j++;
      }
    }
  }

  function globals(values,label,write=false,floatIndices=[]) {
    fixture.globals.forEach(([name,,width,offset=0],i)=>{
      // Some embedded PC tables are lifted to host-owned storage of dynamic size.
      const origin=e[name].value,at=(fixture.indirect_globals?.includes(name)?v.getUint32(origin,true):origin)+offset,method=width===1?'Uint8':'Uint32';
      const wanted=(fixture.pointer_globals??[]).includes(i)?relocated(values[i]):values[i];
      if(write)v['set'+method](at,wanted,true);
      else if(floatIndices.includes(i)&&Number.isNaN(v.getFloat32(at,true))&&(wanted&0x7f800000)===0x7f800000&&(wanted&0x7fffff))nanFields++;
      else if(v['get'+method](at,true)!==wanted)throw new Error(`${label} global ${name}+${offset.toString(16)}: ${v['get'+method](at,true)} != ${wanted}`);
    });
  }
  for(const [i,c] of fixture.cases.entries()){
    const expected=initial.slice();for(const [at,text] of c.patches)expected.set(unhex(text),at-base);
    memory.set(expected,base);for(const [at,value] of replacements)v.setUint32(at,value,true);
    for(const [name,value,offset=0] of fixture.pointer_initializers??[])v.setUint32(e[name].value+offset,relocated(value),true);
    globals(c.globals,'initial',true);
    const services=fixture.scoped_event_services;
    if(services)v.setUint32(e[services.symbol].value,services.pointer,true);
    for(const at of pointerFields)v.setUint32(at,relocated(v.getUint32(at,true)),true);
    for(const [j,s] of c.steps.entries()){
      const f=fixture.functions[s.fn],label=`${f.name} case ${i} step ${j}`;
      const callArgs=s.args.map((value,index)=>{
        return (f.pointer_args??[]).includes(index)?relocated(value):value;
      });
      const args=f.this===false?callArgs:[s.this,...callArgs];
      if(f.memory)args.push(fixture.memory_adapter);
      const invoke=f.float_args?.length?await floatCall(f,args.length):e[f.name];
      const result=invoke(...args);
      // Some original destructors retain an inactive automatic object's
      // address. Check its identity, stack bounds, live bit, and defined fields
      // before relocating that pointer; never compare uninitialized storage.
      for(const object of s.stack_objects??[]){
        const [name,offset]=object.global;
        const actual=v.getUint32(e[name].value+offset,true);
        if(actual<e.__stack_low.value||actual+object.size>e.__stack_high.value)
          throw new Error(`${label} automatic object outside stack`);
        const [maskName,bit,live]=object.mask;
        if(Boolean(v.getUint32(e[maskName].value,true)&(1<<bit))!==Boolean(live))
          throw new Error(`${label} automatic object registry lifetime`);
        pointerSymbols.set(object.original,actual);
        for(const [offset,text,pointers=[]] of object.blocks){
          const data=new DataView(unhex(text).buffer);
          for(let k=0;k<data.byteLength;k+=4){
            const raw=data.getUint32(k,true),wanted=pointers.includes(k)?relocated(raw):raw;
            if(v.getUint32(actual+offset+k,true)!==wanted)
              throw new Error(`${label} automatic object +${(offset+k).toString(16)}`);
          }
        }
      }
      if(services&&v.getUint32(e[services.symbol].value,true)!==services.pointer)throw new Error(`${label} leaked event services`);
      if(f.result==='wide'){
        if(BigInt.asUintN(64,result)!==BigInt(s.result))throw new Error(`${label} wide return: ${result} != ${s.result}`);
      }else if(f.result==='double'){
        const wanted=new DataView(unhex(s.result).buffer).getFloat64(0,true);
        if(Number.isNaN(result)&&Number.isNaN(wanted))nanFields++;
        else if(!Object.is(result,wanted))throw new Error(`${label} return: ${result} != ${wanted}`);
      }else if(f.result!=='void'&&(result>>>0)!==(f.pointer_result?relocated(s.result):s.result))throw new Error(`${label} return: ${result>>>0} != ${s.result}`);
      for(const [at,text] of s.outputs)expected.set(unhex(text),at-base);
      for(const text of s.stack_texts??[]){
        const actual=v.getUint32(text.slot,true),bytes=unhex(text.text),raw=new DataView(expected.buffer).getUint32(text.slot-base,true);
        if(text.buffer_capacity!==256||text.observed_formatter_destination!==true||raw!==text.original||!bytes.length||bytes.length>256||bytes.at(-1)!==0||actual<e.__stack_low.value||actual+bytes.length>e.__stack_high.value)
          throw Error(`${label} retained stack-text identity/bounds`);
        if(!bytes.every((b,k)=>memory[actual+k]===b))throw Error(`${label} retained stack-text contents`);
        pointerSymbols.set(text.original,actual);pointerFields.add(text.slot);stackTexts++;
      }
      checkMemory(expected,label,s.float_fields??fixture.float_fields,s.quiet_float_fields??[],s.quiet_double_fields??[],s.indeterminate_bytes??[],s.compression_records??[]);globals(s.globals,label,false,s.global_float_indices??[]);
      callbacks+=s.callbacks;steps++;counts[f.name]=(counts[f.name]??0)+1;
    }
  }
  return {result:'pass',cases:fixture.cases.length,calls:steps,functions:Object.keys(counts).length,counts,
    [fixture.callback_counter??'virtual_wait_callbacks']:callbacks,nan_fields_classification_only:nanFields,
    ...(quietedFields?{signaling_nan_words_quieted_per_x87:quietedFields}:{}),
    ...(quietedDoubles?{signaling_nan_doubles_quieted_per_x87:quietedDoubles}:{}),...(indeterminateBytes?{indeterminate_compression_bytes_compared_by_definedness:indeterminateBytes}:{}),...(stackTexts?{retained_stack_texts_verified:stackTexts}:{}),scope:fixture.scope};
}
