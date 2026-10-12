import {readFileSync,writeFileSync} from 'node:fs';
import {verifyScriptState} from '../../tools/script_state_wasm_checks.mjs';
const p='local/analysis/',fixture=JSON.parse(readFileSync(p+'skater-tag-texture-fixtures.json')),controls={};
for(const name of ['ignore-pitch','source-buffer-test']){
 let rejected=false,message='';try{await verifyScriptState(readFileSync(p+'skater-tag-texture-negative-'+name+'.wasm'),fixture,n=>readFileSync(p+n));}catch(e){rejected=true;message=String(e);}
 if(!rejected)throw Error('Accepted wrong '+name);controls[name]={rejected,message};console.log(name,message);
}
writeFileSync(p+'skater-tag-texture-negative.json',JSON.stringify({result:'pass',controls},null,2)+'\n');
