"""Exact local binary used by this decompilation; never launch or patch it."""
import hashlib
from pathlib import Path
import pefile

ROOT = Path(__file__).resolve().parents[1]
EXE = ROOT / "local/discs/cd3/Crack/THUG2.exe"
SHA256 = "52fc88849654b34839ec2f96bff3a8c0b7a855df9a207aab9f2fca2e6bd440f3"


def load():
    data = EXE.read_bytes()
    if hashlib.sha256(data).hexdigest() != SHA256:
        raise ValueError("Wrong executable: the address map is specific to the recorded modified build")
    return pefile.PE(data=data)
