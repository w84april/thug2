"""Load original physics/panel QB files, then execute the real Score constructor."""
from pathlib import Path
source=Path('tools/verify_script_load.py').read_text().split('labels=[];max_heap=HEAP')[0]
source=source.replace(';report_path.unlink(missing_ok=True)','').replace(";(out/'script-load-memory.bin').write_bytes(initial)",'')
assert '.write_' not in source and '.unlink(' not in source
exec(compile(source,'<preserved whole-file QB loader>','exec'))
folder=ROOT/'local/analysis';SCORE,GAME,SETTINGS,NET=BASE+0xc000,BASE+0x9000,BASE+0x9500,BASE+0x9800
for at,size in [(SCORE,0x1550),(GAME,0x400),(SETTINGS,0x200),(NET,0x200)]:memory[at-BASE:at-BASE+size]=bytes(size)
put(GAME+0x28,'<4I',0,0xffffffff,0,GAME+0x28)
put(SETTINGS+4,'<2I',0,SETTINGS+0x40)
put(SETTINGS+0x40,'<4I',2,0x6dc3d6f1,1,SETTINGS+0x50)
put(SETTINGS+0x50,'<4I',26,0xa1dc81f9,0,0)
for name,at,value in [('thug_game_context',0x7ce478,GAME),('thug_game_settings',0x7ce470,SETTINGS),
 ('thug_network_state',0x7cce14,NET),('thug_score_split_layout_draft',0x70134c,0)]:
 assert at not in index;index[at]=len(globals_);globals_.append([name,at,4]);defaults.append(value)
functions={'0x472420':functions['0x472420'],
 '0x563440':{'name':'thug_score_construct_draft','this':True,'result':'word','cleanup':0,'memory':True,'stack_args':[]}}
oracle.functions=functions;oracle.globals=globals_;oracle.defaults=defaults
sources=[];loads=[]
for relative,program,filename in [('scripts/game/skater/physics.qb',PROGRAM,FILENAME),('scripts/game/menu/panelstuff.qb',BASE+0x40000,FILENAME+256)]:
 path=ROOT/'local/game-files/Game/Data'/relative;data=path.read_bytes();text=relative.encode()+b'\0'
 assert len(data)<0x10000
 memory[program-BASE:program-BASE+len(data)]=data;memory[filename-BASE:filename-BASE+len(text)]=text
 sources.append({'path':str(path.relative_to(ROOT)),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
 loads.append((0x472420,0,[filename,program,0,0,0]))
initial=bytes(memory);oracle.initial=initial
def symbol(name):
 at=oracle.word(BUCKETS+(name&4095)*4)
 while at and oracle.word(at+4)!=name:at=oracle.word(at+16)
 return at
def read_array(a):
 count=oracle.word(a+4);assert count<=20
 pointers=[oracle.word(a+8)] if count==1 else [oracle.word(oracle.word(a+8)+i*4) for i in range(count)]
 return [list(struct.unpack('<3I',oracle.cpu.mem_read(p,12))) for p in pointers]
records=[];max_events=0
for players,mode,layout in [(1,0,0),(2,0,1),(2,0,2),(2,0x9d65d0e7,1)]:
 patches=[patch(SETTINGS+0x48,'<I',players),patch(SETTINGS+0x58,'<I',mode)]
 steps=oracle.case(loads+[(0x563440,SCORE,[0])],patches,{index[0x70134c]:layout})
 max_events=max(max_events,oracle.word(CONTEXT+8))
 assert steps[-1]['result']==SCORE
 for step in steps:
  step['global_float_indices']=[]
  for at in [0x6f2348,0x6f2568,*range(0x6f2370,0x6f24b0,16)]:
   if step['globals'][index[at]]&0xfe==4:step['global_float_indices'].append(index[at+8])
 config=oracle.word(symbol(0x91cb3c33)+12);node=oracle.word(config+4);arrays={}
 while node:
  if oracle.cpu.mem_read(node,1)[0]>>1==12:arrays[hex(oracle.word(node+4))]=read_array(oracle.word(node+8))
  node=oracle.word(node+12)
 count=oracle.word(SCORE+0x90);assert count==len(arrays['0xf716442a'])
 actual=[list(struct.unpack('<3I',oracle.cpu.mem_read(SCORE+0x94+i*12,12))) for i in range(count+1)]
 assert actual==arrays['0xf716442a']+[arrays['0xf716442a'][-1]]
 key='0xf314312a' if players==1 or mode==0x9d65d0e7 else '0x44e39bb5' if layout==1 else '0xbeeca6d6'
 positions=[list(struct.unpack('<3I',oracle.cpu.mem_read(SCORE+0x198+i*12,12))) for i in range(2)]
 assert positions==arrays[key]
 records.append({'players':players,'mode':hex(mode),'layout':layout,'curve_count':count,'curve':actual,
  'positions_field':key,'positions':positions,'step_bits':hex(oracle.word(SCORE+0x184)),
  'number_bits':hex(oracle.word(SCORE)),'integer_word':hex(oracle.word(SCORE+4)),
  'debug':oracle.cpu.mem_read(SCORE+0x8c,1)[0]})
scope='Original physics.qb and panelstuff.qb load through472420 and the actual parser. Original563440 constructs Score from their resident definitions and arrays, including normal and split-screen positions. Four cases compare complete memory/globals/heap and returned receiver. Memory and initialized CRT TLS are established host boundaries. Parser arithmetic globals retain the existing typed NaN classification; Score output words compare exactly. No skater scene, platform rendering or playability is claimed.'
fixture={'base':BASE,'memory':'skater-score-assets-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-loader-memory.wasm',
 'memory_exports':['fixture_loader_allocate','fixture_loader_release','fixture_values_scope'],'globals':globals_,'functions':functions,
 'float_fields':[],'cases':oracle.cases,'case_labels':['original Score assets/'+str(i) for i in range(len(records))],
 'scope':scope,'pointer_symbols':parser['pointer_symbols'],'pointer_globals':[index[0x6f2560]],'pointer_exports':[[0x6f2364,'thug_script_loading_file']],
 'pointer_fields':[CONTEXT+24]+[LOG+i*48+36 for i in range(max_events)]}
(folder/fixture['memory']).write_bytes(initial);(folder/'skater-score-assets-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(oracle.cases),'calls':sum(oracle.counts.values()),
 'counts':dict(oracle.counts),'sources':sources,'records':records,'scope':scope,'heap_events':dict(oracle.heap_events)}
(folder/'skater-score-assets-original.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
