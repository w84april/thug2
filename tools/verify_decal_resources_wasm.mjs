import {readFileSync,writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {verifyDecalResources} from './decal_resources_wasm_checks.mjs';
const directory=process.argv[2];
const fixture=Object.fromEntries(['math','resources'].map(key=>[key,JSON.parse(readFileSync(resolve(directory,'decal-'+key+'-fixtures.json'),'utf8'))]));
const result=await verifyDecalResources(readFileSync(resolve(directory,'../../build/thug-core.wasm')),fixture,name=>readFileSync(resolve(directory,name)));
writeFileSync(resolve(directory,'../decal-resources-wasm.json'),JSON.stringify(result,null,2)+'\n');
console.log('WebAssembly decal resources:',result);
