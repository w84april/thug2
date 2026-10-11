import {readFileSync,writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {verifyLowSpeed} from './low_speed_wasm_checks.mjs';
const directory=process.argv[2];
const result=await verifyLowSpeed(readFileSync(resolve(directory,'../../build/thug-core.wasm')),
  JSON.parse(readFileSync(resolve(directory,'low-speed-fixtures.json'),'utf8')),name=>readFileSync(resolve(directory,name)));
writeFileSync(resolve(directory,'../low-speed-wasm.json'),JSON.stringify(result,null,2)+'\n');console.log('WebAssembly low-speed correction:',result);
