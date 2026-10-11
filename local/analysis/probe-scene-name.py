"""Original checksum-or-text parameter getter used by scene commands."""
from pathlib import Path
prefix=Path('local/analysis/probe-script-change.py').read_text().split('labels=[];KEY=')[0]
exec(compile(prefix,'<preserved graph/oracle helpers>','exec'))
functions.clear();functions['0x476a30']={'name':'thug_script_get_scene_name_draft','result':'byte','cleanup':12}
instructions=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(0x76a30,90),0x476a30));hits=Counter();saved=[]
returns={i.address for i in instructions if i.mnemonic=='ret'}
def scene_trace(cpu,at,size,user):
    hits[at]+=1
    if at==0x476a30:saved[:]=[cpu.reg_read(r) for r in registers]
    if at in returns:assert saved==[cpu.reg_read(r) for r in registers]
oracle.cpu.hook_add(UC_HOOK_CODE,scene_trace,begin=0x476a30,end=0x476a89)
for a in [0x476590,0x401b90]:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=a,end=a)
KEY=0x6c4e7971;OUT=BASE+0x6801;labels=[]
def run(g,p,name=KEY,required=0,out=OUT,label='scene name'):
    oracle.case([(0x476a30,p,[name,out,required])],g.patches());labels.append(label)
for raw in range(256):
    g=Graph();kind=raw>>1;value=g.text(b'WH_Classic/Sk8brd_') if kind in [3,4] else 0xabc123
    p=g.structure([(KEY,0,value)]);g.put(g.word(p+4),'<B',raw);run(g,p,label=f'raw tag{raw}')
for required in [0,1,255,256,0xffffffff]:
    for text in [b'',b'WH_Classic_Sk8brd_',b'UPPER/Path',b'upper\\path',b'\xff\xfe/MiXeD',b'a'*300]:
        for kind in [3,4]:
            g=Graph();run(g,g.structure([(KEY,kind,g.text(text))]),required=required,label=f'text type{kind}/required{required:x}/size{len(text)}')
for shape in ['absent','checksum then text','text then checksum','localized then ordinary','ordinary then localized','duplicate checksum','duplicate text','wrong type','included','anonymous structure skipped']:
    g=Graph();text=g.text(b'first');other=g.text(b'second')
    items={'absent':[],'checksum then text':[(KEY,13,42),(KEY,3,text)],'text then checksum':[(KEY,3,text),(KEY,13,42)],
      'localized then ordinary':[(KEY,4,other),(KEY,3,text)],'ordinary then localized':[(KEY,3,text),(KEY,4,other)],
      'duplicate checksum':[(KEY,13,42),(KEY,13,43)],'duplicate text':[(KEY,3,text),(KEY,3,other)],'wrong type':[(KEY,1,42)],
      'included':[(0,13,0x123)],'anonymous structure skipped':[(0,13,0x123)]}[shape]
    if shape in ['included','anonymous structure skipped']:g.symbol(0x123,10,g.structure([(KEY,3,text)]))
    run(g,g.structure(items),name=0 if shape=='anonymous structure skipped' else KEY,label=shape)
for depth in [1,2,4]:
    g=Graph();g.symbol(0x123,3,g.text(b'Alias/Name'))
    for i in range(depth):g.symbol(0x124+i,13,0x123+i)
    # The literal checksum still wins; do not resolve this into text first.
    run(g,g.structure([(KEY,13,0x123+depth)]),label=f'checksum priority over text alias{depth}')
for offset in [0,1,2,3]:
    g=Graph();p=g.structure([(KEY,3,g.text(b'Name/Aliased'))]);run(g,p,out=p+offset,label=f'output overlaps unused structure prefix{offset}')
# A checksum write can change a later component's name during the getter scan.
g=Graph();p=g.structure([(KEY,13,KEY),(123,13,99)]);second=g.word(g.word(p+4)+12)
run(g,p,out=second+4,label='output aliases later member name')
missing=[hex(i.address) for i in instructions if not hits[i.address]];assert not missing,missing
scope='Complete476a30 scene-name getter preserves checksum-first lookup, normal/localized text fallback, case/slash-normalized hashing, failed-output preservation, duplicate and included values, unaligned output and output alias effects. All256 raw component tags and multiple assertion words match original instructions with full memory/globals and preserved registers. This is a real dependency of the shared scene command dispatcher; it does not implement Kill/Create.'
fixture={'base':BASE,'memory':'scene-name-memory.bin','globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'scene-name-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(oracle.counts.values()),'instruction_coverage':{'0x476a30':{'covered':len(instructions),'total':len(instructions),'missing':[]}},'callee_calls':dict(oracle.coverage),'scope':scope}
(folder/'scene-name-original.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
