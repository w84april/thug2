"""Reuse the immutable, initialized registry oracle without running old tests
or removing/writing any maintained reports. New fixtures live in analysis."""
from pathlib import Path
source=Path('tools/verify_ui_registry.py').read_text().split('labels=[];branches=')[0]
source=source.replace('report_path.unlink(missing_ok=True)','None')
exec(compile(source,'<preserved registry oracle setup>','exec'))
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
from unicorn.x86_const import UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP
from specimen import load
folder=ROOT/'local/analysis';pe=load();labels=[];coverage={};hits=Counter()
put(ALLOCATOR+0x124,'<I',ALLOCATOR+0x200)
initial=bytes(memory);oracle.initial=initial
exports += [[0x6478dc,'thug_script_listener_list_methods'],[0x6478d8,'thug_script_listener_methods']]
oracle.scope_entries[ALLOCATOR+0x200]=1
registers=[UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP]
def bind_new(at,size,name,argc=0,result='void',heap=False,diag=False,this=True):
    bind(at,name,argc,result,heap,diag,this)
    coverage[at]=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(at-0x400000,size),at))
    oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:hits.update([at]),begin=at,end=at+size-1)
def call(at,this=0,args=()):return at,this,[v&0xffffffff for v in args]+([0] if functions[hex(at)].get('diagnostics') else [])
def case(calls,patches=(),changes=None,label='scene lifetime'):
    before=[oracle.cpu.reg_read(r) for r in registers]
    stages=oracle.case(calls,patches,{index[k]:v for k,v in (changes or {}).items()})
    assert before==[oracle.cpu.reg_read(r) for r in registers],label
    labels.append(label);known={row[0] for row in exports}
    for s in stages:
        for at,data in s['outputs']:
            if int.from_bytes(bytes.fromhex(data),'little') in known:fields.add(at)
    return stages
def finish(name,scope,excluded=None,extra=None):
    report_coverage={}
    for a,code in coverage.items():
        missing=[hex(i.address) for i in code if not hits[i.address]]
        assert set(missing)<=set(excluded or {}),(hex(a),missing)
        report_coverage[hex(a)]={'covered':len(code)-len(missing),'total':len(code),'missing':missing,
          'excluded':{k:excluded[k] for k in missing}}
    used={s['fn'] for c in oracle.cases for s in c['steps']}
    fixture={'base':BASE,'memory':name+'-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm',
     'memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],
     'globals':globals_,'functions':{k:v for k,v in functions.items() if k in used},'float_fields':[],
     'cases':oracle.cases,'case_labels':labels,'scope':scope,'pointer_exports':exports,'pointer_fields':sorted(fields),**(extra or {})}
    (folder/fixture['memory']).write_bytes(initial);(folder/(name+'-fixtures.json')).write_text(json.dumps(fixture,separators=(',',':')))
    report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(oracle.counts.values()),
      'instruction_coverage':report_coverage,'counts':dict(oracle.counts),'callees':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'scope':scope}
    (folder/(name+'-original.json')).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['callees','counts','scope']}))
