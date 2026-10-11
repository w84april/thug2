import {readFileSync,writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {verifyDecalPrerequisites} from './decal_prerequisites_wasm_checks.mjs';
const directory=process.argv[2];
const fixture=Object.fromEntries(['storage','grid','geometry','lifetime','lighting'].map(key=>[key,JSON.parse(readFileSync(resolve(directory,'decal-'+key+'-fixtures.json'),'utf8'))]));
const result=await verifyDecalPrerequisites(readFileSync(resolve(directory,'../../build/thug-core.wasm')),fixture,name=>readFileSync(resolve(directory,name)));
writeFileSync(resolve(directory,'../decal-prerequisites-wasm.json'),JSON.stringify(result,null,2)+'\n');
console.log('WebAssembly decal prerequisites:',result);
