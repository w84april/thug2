import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {verifyScriptState} from './skater-walk-checks.mjs';
const p='local/analysis/',fixture=JSON.parse(readFileSync(p+'skater-startup-tail-fixtures.json'));
const controls={};
for(const name of ['clear-toggle','cache-difficulty']){
 let failure='';try{await verifyScriptState(readFileSync(p+'skater-startup-tail-negative-'+name+'.wasm'),fixture,n=>readFileSync(existsSync(p+n)?p+n:'local/validation/collision/'+n));}catch(error){failure=String(error);}
 if(!failure||!failure.includes('thug_stats_manager_initialize_draft'))throw Error('Unrejected or unrelated control '+name+': '+failure);
 controls[name]={rejected:true,failure};
}
const result={result:'pass',controls,scope:'Wrong unconditional toggle clear and wrong cached pre-callback difficulty are rejected by the frozen original-memory comparator.'};
writeFileSync(p+'skater-startup-tail-negative.json',JSON.stringify(result,null,2)+'\n');console.log(result);
