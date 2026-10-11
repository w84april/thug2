"""Whole original training QB -> real node name/prefix indexes and link names.
The caller's one-array registration entry is explicit initialized fixture state;
the full45d520 registration/position/postprocessing path is not substituted or claimed.
"""
from pathlib import Path
source=Path('tools/verify_script_load.py').read_text().split('labels=[];max_heap=HEAP')[0]
source=source.replace(';report_path.unlink(missing_ok=True)','').replace(";(out/'script-load-memory.bin').write_bytes(initial)",'')
assert '.write_' not in source and '.unlink(' not in source
exec(compile(source,'<preserved whole-file loader setup>','exec'))
from unicorn.x86_const import UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP
folder=ROOT/'local/analysis';TABLE,COUNT=BASE+0x90000,BASE+0xe100
asset=next(a for a in assets if a['member'].lower()=='levels\\tr\\tr.qb');key=crc(b'TR_NodeArray')
# Determine the deterministic allocation address using the ORIGINAL loader.
# This is only fixture preparation; it supplies no implementation of indexing.
oracle.case([(0x472420,0,[asset['filename'],asset['address'],0,1,0])])
symbol=oracle.word(BUCKETS+(key&4095)*4)
while symbol and oracle.word(symbol+4)!=key:symbol=oracle.word(symbol+16)
assert symbol and oracle.cpu.mem_read(symbol+1,1)[0]==12
array=oracle.word(symbol+12);assert oracle.word(array+4)==1917
memory=bytearray(initial)
for i in range(16384):put(TABLE+i*4,'<HH',0,65535)
put(TABLE+0x10002,'<H',65535);put(TABLE+0x10004,'<4I',1,key,array,0)
initial=bytes(memory);oracle.initial=initial
oracle.cases.clear();oracle.counts.clear();oracle.coverage.clear();oracle.heap_events.clear()
for name,address,value in [('thug_node_table',0x6f0d84,TABLE),('thug_node_prefix_manager_draft',0x6f0d80,0)]:
    index[address]=len(globals_);globals_.append([name,address,4]);defaults.append(value)
for off in range(0,4000,4):
    index[0x6efde0+off]=len(globals_);globals_.append(['thug_node_prefix_results_draft',0x6efde0+off,4,off]);defaults.append(0)
functions['0x45d3a0']={'name':'thug_node_table_index_array_draft','this':True,'result':'void','cleanup':4}
functions['0x45c900']={'name':'thug_node_prefix_build_global_draft','this':False,'result':'void','cleanup':0,'memory':True}
functions['0x45d480']={'name':'thug_node_links_resolve_draft','this':False,'result':'void','cleanup':4}
functions['0x45bf90']={'name':'thug_node_prefix_find_global_draft','this':False,'result':'word','cleanup':0,'pointer_result':True}
functions['0x45c1b0']={'name':'thug_node_find','this':False,'result':'word','cleanup':0}
for address in [0x45d3a0,0x45ce60,0x45c900,0x45c700,0x45c650,0x45bda0,0x45c240,0x46f9b0,0x45d480,0x46caf0]:
    oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=address,end=address)
regs=[UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP];before=[oracle.cpu.reg_read(r) for r in regs]
calls=[(0x472420,0,[asset['filename'],asset['address'],0,1,0]),(0x45d3a0,TABLE,[0]),
       (0x45c900,0,[key]),(0x45d480,0,[array]),(0x45bf90,0,[crc(b'WH_Classic_Sk8brd_'),COUNT]),
       (0x45c1b0,0,[crc(b'g_wall_break_pre'),1])]
steps=oracle.case(calls)
assert [oracle.cpu.reg_read(r) for r in regs]==before
assert oracle.word(symbol+12)==array
names=[oracle.word(0x6efde0+i*4) for i in range(5)]
assert int.from_bytes(oracle.cpu.mem_read(COUNT,2),'little')==5
assert names==[0xe3d37c93,0x0ab0d9a6,0x94d44c05,0x7ada2d29,0x7db7e930]
assert steps[-1]['result']==oracle.word(oracle.word(array+8)+1436*4)
slots=sum(int.from_bytes(oracle.cpu.mem_read(TABLE+i*4+2,2),'little')!=65535 for i in range(16384))
assert slots==1917
fields={CONTEXT+24}
for i in range(oracle.word(CONTEXT+8)):fields.add(LOG+i*48+36)
for step in steps:
    step['global_float_indices']=[]
    for at in [0x6f2348,0x6f2568,*range(0x6f2370,0x6f24b0,16)]:
        if step['globals'][index[at]]&0xfe==4:step['global_float_indices'].append(index[at+8])
    merged=[];chunks=[];start=end=0
    for at,data in step['outputs']:
        if chunks and at!=end:merged.append([start,''.join(chunks)]);chunks=[]
        if not chunks:start=at
        chunks.append(data);end=at+len(data)//2
    if chunks:merged.append([start,''.join(chunks)])
    step['outputs']=merged
scope='The unchanged archived266174-byte TR.qb is loaded with its local readable names, then recovered original name indexing, full prefix building and link conversion run across all1917nodes. Caller-bound single-array registration metadata is explicit initialized test state; no45d520 registration, coordinate conversion or optional postprocessing is claimed. The actual prefix lookup returns the five career skateboard targets in original order, and real name lookup resolves freeskate wall index1436. Entire30MiB arena, loaded structures and links, hash/prefix storage, globals, allocator events and original preserved registers compare. This advances data preparation, not TR_Setup execution or playable training.'
used={s['fn'] for s in steps}
fixture={'base':BASE,'memory':'training-node-index-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-loader-memory.wasm',
 'memory_exports':['fixture_loader_allocate','fixture_loader_release','fixture_values_scope'],'globals':globals_,
 'functions':{k:v for k,v in functions.items() if k in used},'float_fields':[],'cases':oracle.cases,
 'case_labels':['original TR.qb name/prefix indexes and link conversion'],'scope':scope,
 'pointer_symbols':parser['pointer_symbols'],'pointer_globals':[index[0x6f2560]],
 'pointer_exports':[[0x6f2364,'thug_script_loading_file'],[0x6efde0,'thug_node_prefix_results_draft']],
 'pointer_fields':sorted(fields)}
(folder/fixture['memory']).write_bytes(initial)
(folder/'training-node-index-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':1,'calls':len(calls),
 'asset':{k:asset[k] for k in ['member','size','sha256']},'nodes':1917,'occupied_name_slots':slots,'prefix_names':[hex(n) for n in names],
 'freeskate_node_index':1436,'counts':dict(oracle.counts),'callees':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'scope':scope}
(folder/'training-node-index-original.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['scope','callees','heap_events','counts']}))
