"""Restore an extracted THUG2 MSI layout and verify its recorded file hashes.

Run from the project root after extracting discs and cabinets:
    PYTHONPATH=.tools/python python3 tools/restore_game_files.py
"""

import hashlib
import json
from pathlib import Path
import shutil
import struct
import argparse

import pymsi


def restore(preserve_unverified_executable=False):
    discs = Path("local/discs")
    target = Path("local/game-files").resolve()
    if target.exists():
        raise FileExistsError(f"Refusing to overwrite {target}")
    payload = {p.name: p for p in Path("local/payload").glob("*/*") if p.is_file()}
    loose = [p for p in discs.glob("cd*/Setup/Data/**/*") if p.is_file()]
    with pymsi.Package(discs / "cd1/Tony Hawk's Underground 2.msi", strict=False) as msi:
        directories = {r["Directory"]: r for r in msi["Directory"]}
        components = {r["Component"]: r["Directory_"] for r in msi["Component"]}
        hashes = {r["File_"]: struct.pack("<4I", *(r[f"HashPart{i}"] & 0xffffffff
                  for i in range(1, 5))).hex() for r in msi["MsiFileHash"]}

        def install_path(key, seen=()):
            if key == "INSTALLDIR":
                return Path()
            if key is None:
                return None
            if key in seen:
                raise ValueError("Cycle in MSI directory table")
            row = directories[key]
            parent = install_path(row["Directory_Parent"], seen + (key,))
            name = row["DefaultDir"].split(":")[0].split("|")[-1]
            return parent / name if parent is not None else None

        plan, skipped, exceptions = [], [], []
        for row in msi["File"]:
            folder = install_path(components[row["Component_"]])
            if folder is None:
                skipped.append(row["File"])
                continue
            names = row["FileName"].split("|")
            relative = folder / names[-1]
            destination = (target / relative).resolve()
            destination.relative_to(target)  # Reject paths outside the output directory.
            source = payload.get(row["File"])
            if source is None:
                candidates = [p for p in loose if p.name.casefold() in
                              [n.casefold() for n in names]]
                if len(candidates) != 1:
                    raise ValueError(f"Expected one source for {relative}, got {candidates}")
                source = candidates[0]
            preserve = preserve_unverified_executable and relative.as_posix() == "Game/THUG2.exe"
            actual_size = source.stat().st_size
            if actual_size != row["FileSize"] and not preserve:
                raise ValueError(f"Size mismatch: {relative}")
            digest = hashlib.md5(source.read_bytes()).hexdigest()
            expected = hashes.get(row["File"])
            empty_placeholder = row["FileSize"] == 0 and expected == "0" * 32
            hash_matches = expected is not None and digest == expected
            mismatch = actual_size != row["FileSize"] or (expected and not empty_placeholder and not hash_matches)
            if mismatch and not preserve:
                raise ValueError(f"Installer hash mismatch: {relative}")
            if mismatch:
                exceptions.append({"path": relative.as_posix(), "source": str(source),
                                   "expected_size": row["FileSize"], "actual_size": actual_size,
                                   "expected_md5": expected, "actual_md5": digest,
                                   "note": "Disc executable preserved unchanged; does not match installer metadata."})
            plan.append((source, destination, {"path": relative.as_posix(),
                        "size": actual_size, "md5": digest,
                        "installer_hash_verified": hash_matches,
                        "empty_placeholder_verified": empty_placeholder}))
        if len({str(d).casefold() for _, d, _ in plan}) != len(plan):
            raise ValueError("Duplicate destination paths")
        for source, destination, _ in plan:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        report = {"files": len(plan), "bytes": sum(r["size"] for _, _, r in plan),
                  "installer_hashes_verified": sum(r["installer_hash_verified"] for _, _, r in plan),
                  "empty_placeholders_verified": sum(r["empty_placeholder_verified"] for _, _, r in plan),
                  "verification_exceptions": exceptions,
                  "outside_install_directory_skipped": skipped, "manifest": [r for _, _, r in plan]}
        Path("local/extraction-manifest.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({k: v for k, v in report.items() if k != "manifest"}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preserve-unverified-executable", action="store_true",
                        help="Preserve the disc THUG2.exe with its metadata mismatch recorded")
    restore(parser.parse_args().preserve_unverified_executable)
