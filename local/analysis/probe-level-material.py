"""Original streaming material parser, with exact observable read/seek requests."""
from pathlib import Path
level_material_source=Path('local/analysis/probe-material-buffer.py').read_text()
preamble=level_material_source.split('\nfor fill in [0,0xa5,0xff]:')[0]
preamble=preamble.replace('0x4d2cb0,1746,\'thug_material_buffer_parse_draft\'','0x4d3390,2086,\'thug_material_file_parse_draft\'')
exec(compile(preamble,'<preserved material fixture builders>','exec'))
IOCTRL,IOLOG=BASE+0x1a000,BASE+0x110000
put(IOCTRL,'<I',0);initial=bytes(memory);oracle.initial=initial
globals_ += [['thug_scene_file_read_draft',0x340,4],['thug_scene_file_seek_draft',0x344,4]];defaults += [0x5b9ee0,0x5b9fa0]
def file_port(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);arg=lambda i:oracle.word(sp+4+i*4)
 if at==0x5b9ee0:
  out,width,count,file=[arg(i) for i in range(4)];start=oracle.word(file);n=width*count
  assert BASE<=start<=start+n<=BASE+0x100000
  cpu.mem_write(out,bytes(cpu.mem_read(start,n)));oracle.setword(file,start+n);kind=1;result=n
 else:
  file,width,count=[arg(i) for i in range(3)];assert count==1;start=oracle.word(file);oracle.setword(file,start+width);kind=2;result=start+width
 i=oracle.word(IOCTRL);assert i<40000;oracle.setword(IOCTRL,i+1)
 cpu.mem_write(IOLOG+i*24,struct.pack('<6I',kind,file,width,count,start,oracle.word(file)))
 cpu.reg_write(UC_X86_REG_EAX,result);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
for at in [0x5b9ee0,0x5b9fa0]:oracle.cpu.hook_add(UC_HOOK_CODE,file_port,begin=at,end=at)
# Reuse the same material boundary/animation/duplicate/collision cases, now
# executing2086-byte4d3390; old fixture writers are deliberately excluded.
body=level_material_source.split('\nfor fill in [0,0xa5,0xff]:',1)[1].split('missing={hex(a):')[0]
exec(compile('for fill in [0,0xa5,0xff]:'+body.replace('0x4d2cb0','0x4d3390'),'<streaming material cases>','exec'))
coverage={hex(a):{'total':len(c),'covered':sum(bool(hits[i.address]) for i in c),'missing':[hex(i.address) for i in c if not hits[i.address]]} for a,c in code.items()}
excluded={hex(a):'allocator bootstrap; initialized allocator contract' for a in [0x4d33ec,0x4d343d,0x4d36d3,0x4d375b,0x4d3786,0x4d3804,0x4d3881,0x4d392e]}
excluded.update({hex(a):'allocation failure; successful allocation contract' for a in [0x4d3417,0x4d3465,0x4d3703]})
excluded.update({hex(a):'alignment instruction bypassed by predecessors' for a in [0x4d395d,0x4d3a1d]})
for a,c in coverage.items():
 c['excluded']=excluded if a=='0x4d3390' else {};assert set(c['missing'])==set(c['excluded']),(a,c)
print('COVERAGE',json.dumps(coverage),flush=True)
clang=ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang';port=folder/'level-material-ports.c';output=folder/'level-material-ports.wasm'
cmd=[str(clang),'--target=wasm32-unknown-unknown','-O2','-nostdlib','-Wl,--no-entry,--export-all,--import-memory',str(port),'-o',str(output)];subprocess.run(cmd,check=True)
output.with_suffix('.build.json').write_text(json.dumps({'command':cmd,'source_sha256':hashlib.sha256(port.read_bytes()).hexdigest(),'sha256':hashlib.sha256(output.read_bytes()).hexdigest()},indent=2)+'\n')
prior=json.loads((folder/'material-buffer-fixtures.json').read_text())
callbacks=[{**c,'module':'level-material-ports.wasm'} for c in prior['native_callbacks']]
callbacks += [{'module':'level-material-ports.wasm','export':'fixture_scene_read','original':0x5b9ee0},{'module':'level-material-ports.wasm','export':'fixture_scene_seek','original':0x5b9fa0}]
scope='Original file-stream material parser4d3390, preserving each read size/count and seek, exact file position, retained bytes, allocations, lookup results, animated material channels/UV/texture records and duplicate handling. Same bounded material cases and actual Letter S texture/material bytes used by the earlier buffer parser. File/GPU providers are comparison fixtures; Windows file handles and drawing are not supplied.'
fixture={**prior,'memory':'level-material-memory.bin','memory_fixture':'level-material-ports.wasm','globals':globals_,'pointer_globals':[len(globals_)-2,len(globals_)-1],'functions':functions,'cases':oracle.cases,'case_labels':labels,'pointer_fields':sorted(fields),
 'pointer_initializers':prior['pointer_initializers']+[['thug_scene_file_read_draft',0x5b9ee0],['thug_scene_file_seek_draft',0x5b9fa0]],'native_callbacks':callbacks,'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'level-material-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(oracle.counts.values()),'instruction_coverage':coverage,'actual_asset':actual,'scope':scope}
(folder/'level-material-original.json').write_text(json.dumps(report,indent=2)+'\n')
print('REPORT',len(labels),'cases',sum(oracle.counts.values()),'calls',flush=True)
