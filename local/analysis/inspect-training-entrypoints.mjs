/* Static discovery only: token inspection is not gameplay execution. */
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const fixture=JSON.parse(readFileSync('local/validation/collision/script-tokens-fixtures.json'));
const report=JSON.parse(readFileSync('local/validation/script-tokens.json'));
const names=JSON.parse(readFileSync('local/analysis/training-checksum-names.json')).names;
const data=readFileSync('local/validation/collision/'+fixture.memory);
const {instance:{exports:e}}=await WebAssembly.instantiate(readFileSync('local/build/thug-core.wasm'));
const bytes=new Uint8Array(e.memory.buffer);bytes.set(data,fixture.base);const v=new DataView(e.memory.buffer);
const label=key=>names[key.toString(16).padStart(8,'0')]?.[0]??'0x'+key.toString(16);
const selected=new Set(['TR_Setup','TR_Initializer','TR_Initailizer','TR_startup','TR_LoadingSounds']);
const scripts=[],references=[];
for(const a of report.assets){
 const asset=data.subarray(a.address-fixture.base,a.address-fixture.base+a.size);
 if(createHash('sha256').update(asset).digest('hex')!==a.sha256)throw Error('asset hash');
 let p=a.address,end=p+a.size,current=null,record=null;
 while(p<end&&bytes[p]){
  const t=bytes[p],next=e.thug_script_next_token(p)>>>0;if(next<=p||next>end)throw Error('token boundary');
  if(t===0x23&&bytes[p+1]===0x16){
   current=label(v.getUint32(p+2,true));record=selected.has(current)?{name:current,member:a.member,asset_sha256:a.sha256,offset:p-a.address,tokens:[]}:null;
   if(record)scripts.push(record);
  }
  let value;
  if(t===0x16){value=label(v.getUint32(p+1,true));if(selected.has(value))references.push({member:a.member,script:current,offset:p-a.address,name:value});}
  else if(t===0x17||t===0x18)value=v.getInt32(p+1,true);
  else if(t===0x1a)value=v.getFloat32(p+1,true);
  else if(t===0x1b||t===0x1c)value=Buffer.from(bytes.subarray(p+5,next)).toString('latin1').replace(/\0$/,'');
  if(record)record.tokens.push({offset:p-a.address,token:t,...(value===undefined?{}:{value})});
  if(t===0x24){if(record)record.bytes=next-(a.address+record.offset);current=null;record=null;}
  p=next;
 }
}
const result={scope:'Static token discovery only, not executed startup order or recovered functions.',scripts,references};
writeFileSync('local/analysis/training-entrypoints-discovery.json',JSON.stringify(result,null,2)+'\n');
for(const s of scripts)console.log(s.name,s.member,s.bytes,s.tokens.map(t=>t.value??(t.token===1?'\n':'['+t.token.toString(16)+']')).join(' '));
console.log('References:',references);
