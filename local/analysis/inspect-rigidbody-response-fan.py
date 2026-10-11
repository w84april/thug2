"""Locate the missing fan script's original archived bytes and oracle hash."""
from pathlib import Path
from prx import entries,decoded_size
import hashlib,json
p=Path('local/analysis');path=Path('local/game-files/Game/Data/pre/TR_scripts.prx');data=path.read_bytes()
e=next(e for e in entries(data) if e.name.lower()=='levels\\tr\\tr_scripts.qb')
assert e.compressed and decoded_size(e.payload)==e.size
prior=json.loads(Path('local/validation/lzss.json').read_text())
expected=next(m['sha256'] for a in prior['archives'] if a['name']=='TR_scripts.prx' for m in a['members'] if m['name']==e.name)
report=json.loads((p/'rigidbody-response-fan-script.json').read_text())
report['archive']={'path':str(path),'sha256':hashlib.sha256(data).hexdigest(),'member':e.name,'size':e.size,'compressed':True,'payload_sha256':hashlib.sha256(e.payload).hexdigest(),'original_decoded_sha256':expected}
(p/'rigidbody-response-fan-compressed.bin').write_bytes(e.payload);(p/'rigidbody-response-fan-script.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report['archive']))
