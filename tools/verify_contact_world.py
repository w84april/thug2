"""Compare contact-relative to world coordinates with original 00427a00."""
from pathlib import Path
prefix=Path('tools/verify_post_frame.py').read_text().split('for count in [0,1,2,17,128]:')[0]
prefix=prefix.replace("'post-frame.json'","'contact-world.json'")
exec(compile(prefix,'<initialized contact graph>','exec'))
bind(0x427a00,'thug_skater_contact_world_position',1,'word')
oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=0x427a00,end=0x427a00)
oracle.cpu.hook_add(UC_HOOK_CODE,hit,begin=0x427a00,end=0x427aa7)
ranges={0x427a00:168}
words=[0,0x80000000,0x3f800000,0xbf800000,1,0x80000001,0x7f7fffff,0x7f800000,0xff800000,0x7fa12345,0xffa12345,0x7fc12345]
for word,contact,destination in itertools.product(words,[0,GCONTACT],[TRANS_OUT,GROUND_GATE+0x1c,GROUND_GATE+0x20,GROUND_GATE+0x18]):
    # With no retained owner, X/Y quiet and Z/W stay raw, even with a live contact.
    step=compare(0x427a00,GROUND_GATE,[destination],
        [patch(GROUND_GATE+0x6c,'<I',0),patch(GROUND_GATE+0x18,'<I',contact),patch(GROUND_GATE+0x1c,'<4I',word,word,word,word)],
        label='raw retained-owner absence, quiet X/Y, raw Z/W, overlap')
    # Unicorn retains signaling payloads across FLD/FSTP. Require the physical
    # x87 quiet bit exactly on these two lanes, preserving payload and sign.
    step['quiet_float_fields']=[destination,destination+4]
matrices=[identity,[2.,0,0,0,0,3.,0,0,0,0,4.,0,10.,20.,30.,1.],
          [0,0,1.,0,0,1.,0,0,-1.,0,0,0,0,0,0,1.],
          [1.,.1,0,0,.2,1.,0,0,0,.3,1.,0,3.,4.,5.,1.],
          [0.]*16,[1e-20,0,0,0,0,1e-20,0,0,0,0,1e-20,0,0,0,0,1.]]
for matrix,contact,destination in itertools.product(matrices,[0,GCONTACT],[TRANS_OUT,GROUND_GATE+0x1c,GROUND_GATE+0x20,GOWNER+0x4c,GOWNER+0x6c]):
    compare(0x427a00,GROUND_GATE,[destination],
        [patch(GROUND_GATE+0x6c,'<I',GOWNER),patch(GROUND_GATE+0x18,'<I',contact),patch(GOWNER+0x6c,'<16f',*matrix),
         patch(GOWNER+0x4c,'<4f',10,20,30,1),patch(GROUND_GATE+0x1c,'<4f',40,55,70,1)],
        label='retained owner rotation and translation with aliased output',floats=range(destination,destination+16,4))
for word,owner_word in itertools.product(words,[0,1,0x7f7fffff,0x7fa12345]):
    compare(0x427a00,GROUND_GATE,[TRANS_OUT],
        [patch(GROUND_GATE+0x1c,'<4I',word,word,word,word),patch(GOWNER+0x4c,'<4I',owner_word,owner_word,owner_word,owner_word)],
        label='computed finite, nonfinite, tiny and overflow lanes',floats=range(TRANS_OUT,TRANS_OUT+16,4))
coverage={};pe=load();md=Cs(CS_ARCH_X86,CS_MODE_32)
for at,n in ranges.items():
    instructions=list(md.disasm(pe.get_data(at-0x400000,n),at));missing=[hex(i.address) for i in instructions if not hits[i.address]]
    coverage[hex(at)]={'total':len(instructions),'covered':len(instructions)-len(missing),'missing':missing}
    assert not missing,missing
scope='Complete contact-to-world427a00; retained owner independent of live contact, original matrix/vector callees, input/output aliases. Computed NaNs classify; untranslated X/Y require exact physical x87 quiet-bit correction for Unicorn, Z/W and all other defined bytes compare exactly.'
fixture={'base':BASE,'memory':'contact-world-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm',
         'memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,
         'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,
         'pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),
         'native_callbacks':[{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},
                            {'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]}
path=out/'contact-world-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
(out/fixture['memory']).write_bytes(initial)
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'counts':dict(oracle.counts),
        'callee_coverage':dict(oracle.coverage),'instruction_coverage':coverage,'scope':scope}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('Original contact-world',len(labels),coverage,flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_contact_world_wasm.mjs')],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory']]}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS contact-world',len(labels),sum(oracle.counts.values()))
