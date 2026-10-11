import {readFileSync,writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {verifyDecalProjection} from './decal_projection_wasm_checks.mjs';
const directory=process.argv[2];
const fixture=Object.fromEntries([['lifecycle','mesh-lifecycle'],['projection','decal-projection']].map(([key,name])=>[key,JSON.parse(readFileSync(resolve(directory,name+'-fixtures.json'),'utf8'))]));
const result=await verifyDecalProjection(readFileSync(resolve(directory,'../../build/thug-core.wasm')),fixture,name=>readFileSync(resolve(directory,name)));
writeFileSync(resolve(directory,'../decal-projection-wasm.json'),JSON.stringify(result,null,2)+'\n');
console.log('WebAssembly complete decal projection:',result);
