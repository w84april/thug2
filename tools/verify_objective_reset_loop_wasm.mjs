// A terminating control precedes each bounded nontermination observation.
// Dedicated workers keep preserved original loops off the browser main thread.
import {Worker} from 'node:worker_threads';
import {readFileSync,writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
const directory=process.argv[2],wasm=readFileSync(resolve(directory,'../../build/thug-core.wasm'));
const allocator=readFileSync(resolve(directory,'script-values-memory.wasm'));
async function workerBody(){
  const {parentPort,workerData}=require('node:worker_threads');
  const {instance:{exports:e}}=await WebAssembly.instantiate(workerData.wasm);
  const {instance:{exports:a}}=await WebAssembly.instantiate(workerData.allocator,{env:{memory:e.memory}});
  const v=new DataView(e.memory.buffer),base=0x1800000,flat=base+0x100,group=base+0x200,nodes=base+0x300,params=base+0x600,context=base+0x1000,adapter=base+0x1040;
  const word=(at,n)=>v.setUint32(at,n>>>0,true);
  word(context,base+0x4000);word(context+4,base+0xf000);word(context+12,base+0x2000);word(context+16,base);word(context+20,base+0x10000);word(adapter,context);
  for(const [i,name] of ['fixture_values_allocate','fixture_values_release','fixture_values_scope'].entries()){
    const slot=e.__indirect_function_table.grow(1);e.__indirect_function_table.set(slot,a[name]);word(adapter+4*(i+1),slot);
  }
  function setup(reserved){
    word(flat+4,nodes);
    for(let i=0;i<3;i++){const p=nodes+i*16;word(p,2);word(p+4,i===1&&reserved?0xb3790f33:0x11111111+i);word(p+8,7+i*2);word(p+12,i<2?p+16:0);}
    word(group+4,base+0x400);word(base+0x400,26);word(base+0x404,0);word(base+0x408,0xe462e527);word(base+0x40c,base+0x410);
    word(base+0x410,20);word(base+0x414,1);word(base+0x418,flat);word(base+0x41c,0);
    word(base+0x1c,params);word(base+0x20,group);
  }
  const invoke=()=>workerData.fn==='thug_objective_clear_members'?e[workerData.fn](flat):e[workerData.fn](base,adapter);
  setup(false);invoke();const control=[0,1,2].map(i=>v.getUint32(nodes+i*16+8,true));
  if(control.some(x=>x!==0))throw Error('Terminating reset control failed');
  setup(true);parentPort.postMessage({phase:'entered',control});invoke();parentPort.postMessage({phase:'unexpected_return'});
}
const results=[];
for(const fn of ['thug_objective_clear_members','thug_objective_clear_state']){
  const worker=new Worker(`(${workerBody.toString()})()`,{eval:true,workerData:{wasm,allocator,fn}});
  results.push(await new Promise((resolve_,reject)=>{
    let timer=setTimeout(()=>{worker.terminate();reject(Error('Reset control did not finish'));},10000);
    worker.on('error',error=>{clearTimeout(timer);reject(error);});
    worker.on('message',message=>{
      clearTimeout(timer);
      if(message.phase!=='entered'){worker.terminate();reject(Error('Reserved-member loop returned'));return;}
      timer=setTimeout(async()=>{const exit=await worker.terminate();resolve_({function:fn,control_member_values:message.control,result:'no return observed after entering reserved-member case',observation_ms:500,worker_termination_exit:exit});},500);
    });
  }));
}
writeFileSync(resolve(directory,'../objective-reset-loop-wasm.json'),JSON.stringify({result:'pass',functions:results,scope:'Bounded nontermination observations after positive controls; source preserves the original same-member cycle. No browser main-thread hang tests.'},null,2)+'\n');
console.log('Bounded Wasm reset-loop controls:',results);
