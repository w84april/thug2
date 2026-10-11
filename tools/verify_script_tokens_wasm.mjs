import {readFileSync,writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {verifyScriptTokens} from './script_tokens_wasm_checks.mjs';
const directory=process.argv[2];
const result=await verifyScriptTokens(readFileSync(resolve(directory,'../../build/thug-core.wasm')),
  JSON.parse(readFileSync(resolve(directory,'script-tokens-fixtures.json'),'utf8')),name=>readFileSync(resolve(directory,name)));
writeFileSync(resolve(directory,'../script-tokens-wasm.json'),JSON.stringify(result,null,2)+'\n');
console.log('WebAssembly script tokens:',result);
