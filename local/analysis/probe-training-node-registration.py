"""Load the untouched training QB, then execute complete original registration."""
from pathlib import Path
source=Path('tools/verify_script_load.py').read_text().split('labels=[];max_heap=HEAP')[0]
source=source.replace(';report_path.unlink(missing_ok=True)','').replace(";(out/'script-load-memory.bin').write_bytes(initial)",'')
assert '.write_' not in source and '.unlink(' not in source
exec(compile(source,'<preserved whole-file loader setup>','exec'))
from unicorn.x86_const import UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP
folder=ROOT/'local/analysis';TABLE,COUNT,GROUPS,LISTS=BASE+0x90000,BASE+0xe100,BASE+0xe200,BASE+0xe300
asset=next(a for a in assets if a['member'].lower()=='levels\\tr\\tr.qb');key=crc(b'TR_NodeArray')
put(GROUPS,'<4I',LISTS,0x12345678,0xffffffff,0)
initial=bytes(memory);oracle.initial=initial
for name,address,value in [('thug_node_table',0x6f0d84,TABLE),('thug_node_prefix_manager_draft',0x6f0d80,0),('thug_node_link_groups_draft',0x6f2264,GROUPS)]:
    index[address]=len(globals_);globals_.append([name,address,4]);defaults.append(value)
for off in range(0,4000,4):
    index[0x6efde0+off]=len(globals_);globals_.append(['thug_node_prefix_results_draft',0x6efde0+off,4,off]);defaults.append(0)
functions['0x45d370']={'name':'thug_node_table_initialize_draft','this':True,'result':'word','cleanup':0}
functions['0x45d520']={'name':'thug_node_register_array_draft','this':True,'result':'byte','cleanup':8,'memory':True}
functions['0x45bf90']={'name':'thug_node_prefix_find_global_draft','this':False,'result':'word','cleanup':0,'pointer_result':True}
functions['0x45c1b0']={'name':'thug_node_find','this':False,'result':'word','cleanup':0}
for address in [0x45d370,0x45d520,0x45d3a0,0x45c900,0x45d480,0x4694e0,0x4696c0,0x469540,0x45d3f0,0x45c020,0x45c420]:
    oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=address,end=address)
regs=[UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP];before=[oracle.cpu.reg_read(r) for r in regs]
fields={CONTEXT+24};details=[];labels=[]
for flag in [0,1]:
    calls=[(0x472420,0,[asset['filename'],asset['address'],0,1,0]),(0x45d370,TABLE,[]),
       (0x45d520,TABLE,[key,flag]),(0x45d520,TABLE,[key,flag]),
       (0x45bf90,0,[crc(b'WH_Classic_Sk8brd_'),COUNT]),(0x45c1b0,0,[crc(b'g_wall_break_pre'),1])]
    steps=oracle.case(calls)
    assert [oracle.cpu.reg_read(r) for r in regs]==before
    assert steps[2]['result']==1 and steps[3]['result']==0
    assert oracle.word(TABLE+0x10004)==1 and oracle.word(TABLE+0x10008)==key
    array=oracle.word(TABLE+0x1000c);assert oracle.word(array+4)==1917
    names=[oracle.word(0x6efde0+i*4) for i in range(5)]
    assert int.from_bytes(oracle.cpu.mem_read(COUNT,2),'little')==5
    assert names==[0xe3d37c93,0x0ab0d9a6,0x94d44c05,0x7ada2d29,0x7db7e930]
    assert steps[-1]['result']==oracle.word(oracle.word(array+8)+1436*4)
    slots=sum(int.from_bytes(oracle.cpu.mem_read(TABLE+i*4+2,2),'little')!=65535 for i in range(16384));assert slots==1917
    groups=oracle.word(GROUPS+8);assert groups>0 if flag else groups==0xffffffff
    details.append({'postprocess':flag,'nodes':1917,'occupied_name_slots':slots,'prefix_names':[hex(n) for n in names],
                    'freeskate_node_index':1436,'group_count':groups,'duplicate_result':steps[3]['result']})
    labels.append('whole original training node registration, postprocess'+str(flag))
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
    print('Original training registration passed with postprocess',flag,'groups',groups,flush=True)
scope='The unchanged archived266174-byte TR.qb loads with readable local names, then the original table constructor and complete45d520 registration run for all1917nodes. Both disabled and enabled link-group postprocessing compare, including real name/prefix building, coordinate conversion, link rewriting, actual group assignment and duplicate-registration rejection. Initialized script/allocator services and an empty reference-list manager are explicit starting state; no registration metadata/indexes or gameplay implementations are substituted. Real career-prefix lookup finds five names in original order and freeskate wall lookup resolves node1436. All30MiB of arena, globals, heap effects and preserved original registers compare. This prepares actual training nodes; it does not create/render scene objects or complete TR_Setup.'
used={s['fn'] for c in oracle.cases for s in c['steps']}
fixture={'base':BASE,'memory':'training-node-registration-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-loader-memory.wasm',
 'memory_exports':['fixture_loader_allocate','fixture_loader_release','fixture_values_scope'],'globals':globals_,
 'functions':{k:v for k,v in functions.items() if k in used},'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,
 'pointer_symbols':parser['pointer_symbols'],'pointer_globals':[index[0x6f2560]],
 'pointer_exports':[[0x6f2364,'thug_script_loading_file'],[0x6efde0,'thug_node_prefix_results_draft']], 'pointer_fields':sorted(fields)}
(folder/fixture['memory']).write_bytes(initial)
(folder/'training-node-registration-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(details),'calls':sum(oracle.counts.values()),
 'asset':{k:asset[k] for k in ['member','size','sha256']},'registrations':details,
 'counts':dict(oracle.counts),'callees':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'scope':scope}
(folder/'training-node-registration-original.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['scope','callees','heap_events','counts']}))
