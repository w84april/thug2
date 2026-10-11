"""Complete original GameModeEquals with real iteration and settings lookup."""
from pathlib import Path
prefix=Path('local/analysis/probe-script-change.py').read_text().split('labels=[];KEY=')[0]
exec(compile(prefix,'<preserved graph/oracle helpers>','exec'))
functions.clear();functions['0x5a11d0']={'name':'thug_game_mode_equals_draft','this':False,'result':'byte','cleanup':0}
settings_index=len(globals_);globals_.append(['thug_game_settings',0x7ce470,4]);defaults.append(0)
instructions=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(0x1a11d0,79),0x5a11d0));hits=Counter();saved=[]
returns={i.address for i in instructions if i.mnemonic=='ret'}
def mode_trace(cpu,at,size,user):
    hits[at]+=1
    if at==0x5a11d0:saved[:]=[cpu.reg_read(r) for r in registers]
    if at in returns:assert saved==[cpu.reg_read(r) for r in registers]
oracle.cpu.hook_add(UC_HOOK_CODE,mode_trace,begin=0x5a11d0,end=0x5a121e)
for a in [0x553220,0x476cb0]:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=a,end=a)
labels=[];KEY=0x1ded1ea4;OTHER=0x55667788

def setting(g,items):
    p=g.structure(items);s=g.alloc(12);g.put(s,'<3I',0xcccccccc,0xdddddddd,g.word(p+4));return s

def run(g,params,settings,label,expected):
    result=oracle.case([(0x5a11d0,0,[params,0xdeadbeef])],g.patches(),{settings_index:settings})
    assert result[0]['result']==expected,(label,result[0]['result']);assert result[0]['outputs']==[]
    labels.append(label)

# Every raw tag byte: borrowed flag is ignored, all other bits participate.
for raw in range(256):
    for named in [False,True]:
        g=Graph();s=setting(g,[(KEY,1,1)]);p=g.structure([(KEY if named else 0,0,KEY)])
        g.put(g.word(p+4),'<B',raw)
        run(g,p,s,f'raw tag{raw},named{named}',int(not named and raw&0xfe==0x1a))
for value in [0,1,2,255,256,0x7fffffff,0x80000000,0xffffffff]:
    g=Graph();s=setting(g,[(KEY,1,value)]);run(g,g.structure([(0,13,KEY)]),s,f'boolean word{value:x}',int(value!=0))
for shape in ['empty params','no candidate','missing setting','false then true','true then false','all false','named true skipped','include not expanded']:
    g=Graph();s=setting(g,[(KEY,1,1),(OTHER,1,0)])
    items={'empty params':[],'no candidate':[(0,1,KEY)],'missing setting':[(0,13,99)],
           'false then true':[(0,13,OTHER),(0,13,KEY)],'true then false':[(0,13,KEY),(0,13,OTHER)],
           'all false':[(0,13,OTHER)]*4,'named true skipped':[(123,13,KEY),(0,13,OTHER)],'include not expanded':[(0,13,99)]}[shape]
    if shape=='include not expanded':g.symbol(99,10,g.structure([(0,13,KEY)]))
    run(g,g.structure(items),s,shape,int(shape in ['false then true','true then false']))
# Settings use their real nested inclusion/alias resolution, unlike params.
for depth in [1,2,4]:
    for value in [0,1,0xffffffff]:
        g=Graph();g.symbol(OTHER,1,value)
        for i in range(depth):g.symbol(OTHER+i+1,13,OTHER+i)
        inside=g.structure([(KEY,13,OTHER+depth)]);g.symbol(0x666,10,inside)
        s=setting(g,[(0,13,0x666)])
        run(g,g.structure([(0,13,KEY)]),s,f'actual settings aliases{depth}/{value:x}',int(value!=0))
for first,second in [(0,1),(1,0),(0xffffffff,1)]:
    g=Graph();s=setting(g,[(KEY,1,first),(KEY,1,second)])
    run(g,g.structure([(0,13,KEY)]),s,f'duplicate last setting{first}/{second}',int(second!=0))
for truth_at in [0,1,7,31]:
    g=Graph();s=setting(g,[(KEY,1,1),(OTHER,1,0)]);p=g.structure([(0,13,OTHER)]*truth_at+[(0,13,KEY)])
    c=g.word(p+4)
    for _ in range(truth_at):c=g.word(c+12)
    g.put(c+12,'<I',0xfefefefe)
    run(g,p,s,f'first true short circuit{truth_at}',1)
g=Graph();run(g,g.structure([]),0,'empty does not touch settings',0)
missing=[hex(i.address) for i in instructions if not hits[i.address]];assert not missing,missing
scope='Complete native GameModeEquals5a11d0. All256 raw component tag bytes, unnamed-only filtering, borrowed flags, stored boolean bits, duplicate precedence, multi-candidate order, real settings inclusion/alias resolution and first-truthy short circuit compare against original instructions. Empty parameters do not access settings. The entire arena and globals stay unchanged; returns and callee-saved registers match exactly. This does not initialize game mode or create scene objects.'
fixture={'base':BASE,'memory':'training-mode-memory.bin','globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'training-mode-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(oracle.counts.values()),'instruction_coverage':{'0x5a11d0':{'covered':len(instructions),'total':len(instructions),'missing':[]}},'callee_calls':dict(oracle.coverage),'scope':scope}
(folder/'training-mode-original.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
