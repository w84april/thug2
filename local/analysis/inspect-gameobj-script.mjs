// Static discovery only: use the verified token walker, never execute the script.
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const base='local/analysis/',path='local/game-files/Game/Data/scripts/game/ped.qb';
const data=readFileSync(path),wasm=readFileSync(base+'prop-sound-draft.wasm');
const {instance:{exports:e}}=await WebAssembly.instantiate(wasm);
const start=data.indexOf(Buffer.from([0x23,0x16,0xa6,0x4d,0xb8,0xf3]));
if(start<0)throw Error('Missing actual gameobj_add_components definition');
const at=0x1000000;new Uint8Array(e.memory.buffer,at,data.length).set(data);
const crc=bytes=>{let c=0xffffffff;for(const b of bytes){c^=b;for(let i=0;i<8;i++)c=(c>>>1)^((c&1)?0xedb88320:0);}return c>>>0;};
const names=new Map();
for(const filename of ['ped.qb','skutils.qb']){
 const bytes=readFileSync('local/game-files/Game/Data/scripts/game/'+filename);
 for(let i=0;i<bytes.length-6;i++)if(bytes[i]===0x2b){
  const end=bytes.indexOf(0,i+5);if(end<0||end-i>160)continue;
  const text=bytes.subarray(i+5,end).toString('latin1'),key=bytes.readUInt32LE(i+1);
  if(/^[\x20-\x7e]+$/.test(text)&&crc(Buffer.from(text.toLowerCase().replaceAll('/','\\'),'latin1'))===key)names.set(key,{text,file:filename,offset:i});
 }
}
const tokens=[];let cursor=at+start;
for(let i=0;i<2000;i++){
 const offset=cursor-at,token=data[offset],next=e.thug_script_next_token(cursor);
 if(next<=cursor||next>at+data.length)throw Error('Invalid token boundary');
 const row={offset,token:'0x'+token.toString(16),bytes:next-cursor};
 if(token===0x16){const key=data.readUInt32LE(offset+1);Object.assign(row,{checksum:'0x'+key.toString(16),name:names.get(key)?.text??null});}
 if(token===0x17)row.integer=data.readInt32LE(offset+1);
 if(token===0x1b||token===0x1c)row.text=data.subarray(offset+5,next-at-1).toString('latin1');
 tokens.push(row);cursor=next;if(token===0x24)break;
}
if(tokens.at(-1).token!=='0x24')throw Error('Unterminated script');
const report={result:'static discovery only',asset:{path,bytes:data.length,sha256:createHash('sha256').update(data).digest('hex')},
 script:'gameobj_add_components',checksum:'0xf3b84da6',offset:start,tokens,verified_names:Object.fromEntries([...names].map(([k,v])=>['0x'+k.toString(16),v])),
 scope:'Token boundaries use the recovered46f690 walker in the verified module. Readable names require a matching token2b record and recomputed checksum. This inspects the real script without executing it or claiming complete prop assembly.'};
writeFileSync(base+'gameobj-add-components-script.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({script:report.script,tokens:tokens.length,names:[...new Set(tokens.map(t=>t.name).filter(Boolean))]}));
