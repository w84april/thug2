"""Compile the isolated MSVC trial and retain its build/comparison provenance."""
import argparse
import json
import os
import subprocess
from pathlib import Path

from native_match import Coff, ROOT, compare, sha


def windows(path):
    return 'Z:' + str(path.resolve()).replace('/', '\\')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--wine', type=Path, required=True)
    parser.add_argument('--compiler', type=Path, required=True)
    parser.add_argument('--prefix', type=Path, required=True)
    parser.add_argument('--exe', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    out, prefix = args.out.resolve(), args.prefix.resolve()
    out.relative_to(ROOT)
    prefix.relative_to(ROOT)
    out.mkdir(parents=True, exist_ok=True)
    source = ROOT / 'matching/functions.cpp'
    manifest_path = ROOT / 'matching/manifest.json'
    source_hash = sha(source.read_bytes())
    obj = out / 'functions.obj'
    env = dict(os.environ, WINEPREFIX=str(prefix), WINEDEBUG='-all', MVK_CONFIG_LOG_LEVEL='0',
               WINEDLLOVERRIDES='mscoree,mshtml=;winemenubuilder.exe=d')
    for key in ('CL', '_CL_', 'INCLUDE', 'LIB', 'LIBPATH'):
        env.pop(key, None)
    flags = ['/nologo', '/c', '/O2', '/Gy']
    command = [str(args.wine.resolve()), str(args.compiler.resolve()), *flags,
               '/Fo' + windows(obj), windows(source)]
    # Never let a failed compile reuse an earlier candidate.
    if obj.exists():
        obj.unlink()
    with (out / 'compile.log').open('w') as log:
        subprocess.run(command, cwd=ROOT, env=env, stdout=log, stderr=log, check=True, timeout=90)
    if sha(source.read_bytes()) != source_hash:
        raise ValueError('Source changed during compilation')
    coff = Coff(obj.read_bytes())
    comp_id = next(s['value'] for s in coff.symbols.values() if s['name'] == '@comp.id')
    build = {'source': str(source.relative_to(ROOT)), 'source_sha256': source_hash,
             'manifest_sha256': sha(manifest_path.read_bytes()), 'command': command,
             'compiler_files': {name: sha((args.compiler.resolve().parent / name).read_bytes())
                                for name in ('cl.exe', 'c1.dll', 'c1xx.dll', 'c2.dll', 'msvcr71.dll')},
             'wine_sha256': sha(args.wine.read_bytes()), 'wine_prefix': str(prefix),
             'object_sha256': sha(obj.read_bytes()), 'compiler_options': flags,
             'compiler_record': {'tool_id': comp_id >> 16, 'build': comp_id & 65535}}
    (out / 'build.json').write_text(json.dumps(build, indent=2) + '\n')
    report = compare(args.exe, obj, json.loads(manifest_path.read_text()))
    report['build'] = build
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f"{report['credited_bytes']} exact bytes after relocation; {report['raw_equal_bytes']} raw object bytes")


if __name__ == '__main__':
    main()
