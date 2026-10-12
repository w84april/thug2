import ctypes,hashlib,json,re,struct,zlib
from pathlib import Path
from prx import entries,decoded_size
keys={0xe594f0a2,0x3a717382,0x9b373e58,0xd8cc3428,0x726e85aa}
pattern=re.compile(re.escape(b'\x2b')+b'('+b'|'.join(re.escape(struct.pack('<I',k)) for k in sorted(keys))+b')([\x20-\x7e]+)\x00')
found={}
def scan(data,source):
 for m in pattern.finditer(data):
  key=struct.unpack('<I',m[1])[0];name=m[2].decode('ascii')
  crc=(zlib.crc32(m[2].lower().replace(b'/',b'\\'))^0xffffffff)&0xffffffff
  assert crc==key,(source,m.start(),key,name,crc)
  found.setdefault(f'{key:08x}',[]).append({'name':name,'source':source,'offset':m.start(),'decoded_sha256':hashlib.sha256(data).hexdigest()})
for p in sorted(Path('local/game-files/Game/Data').rglob('*.qb')):scan(p.read_bytes(),str(p))
p=Path('local/game-files/Game/Data/pre/qb_scripts.prx');archive=p.read_bytes()
lzss=ctypes.CDLL(str(Path('local/validation/lzss.dylib').resolve()));decode=lzss.thug_lzss_decode_unchecked
decode.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_void_p,ctypes.c_uint32];decode.restype=ctypes.c_void_p
for entry in entries(archive):
 if not entry.name.lower().endswith('.qb'):continue
 data=entry.payload
 if entry.compressed:
  assert decoded_size(data)==entry.size
  dictionary=ctypes.create_string_buffer(4096);output=ctypes.create_string_buffer(entry.size)
  decode(dictionary,data,output,len(data));data=output.raw
 scan(data,str(p)+':'+entry.name)
Path('local/analysis/trigger-component-names.json').write_text(json.dumps(found,indent=2)+'\n')
for key in sorted(keys):print(f'{key:08x}',sorted({v['name'] for v in found.get(f'{key:08x}',[])}))
