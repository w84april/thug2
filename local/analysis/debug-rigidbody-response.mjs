import {readFileSync} from 'node:fs';
const base='local/analysis/',fixture=JSON.parse(readFileSync(base+'rigidbody-response-fixtures.json')),number=Number(process.argv[2]??257);
const text=readFileSync('tools/script_state_wasm_checks.mjs','utf8').replace('const memory=new Uint8Array','globalThis.responseDebug=e; const memory=new Uint8Array');
const {verifyScriptState}=await import('data:text/javascript;base64,'+Buffer.from(text).toString('base64'));
const load=name=>{try{return readFileSync(base+name);}catch{return readFileSync('local/validation/collision/'+name);}};
console.log(number,fixture.case_labels[number]);fixture.cases=[fixture.cases[number]];
try{await verifyScriptState(readFileSync(base+'rigidbody-response-draft.wasm'),fixture,load);}catch(error){console.log(String(error));}
const expected=Buffer.from(load(fixture.memory));for(const [at,hex] of fixture.cases[0].patches)Buffer.from(hex,'hex').copy(expected,at-fixture.base);
for(const s of fixture.cases[0].steps)for(const [at,hex] of s.outputs)Buffer.from(hex,'hex').copy(expected,at-fixture.base);
const actual=new DataView(responseDebug.memory.buffer),wanted=new DataView(expected.buffer,expected.byteOffset,expected.byteLength),aud=0x19c0000;
for(let i=0;i<Math.max(actual.getUint32(aud,true),wanted.getUint32(aud-fixture.base,true));i++){
 const at=aud+128+i*80;
 console.log(i,{actual:Array.from({length:20},(_,j)=>actual.getUint32(at+j*4,true)),original:Array.from({length:20},(_,j)=>wanted.getUint32(at-fixture.base+j*4,true))});
}
