"""Publish compact metadata and a source allowlist from an audited local checkpoint.

Run the checkpoint's own audit first. This does not replace its behavioral tests.
Original game data, generated pseudocode and memory fixtures remain local.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("checkpoint", type=Path)
parser.add_argument("audit", type=Path)
parser.add_argument("--main-functions", type=int,
                    help="Previously verified maintained routine count; retain unless audited")
args = parser.parse_args()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


checkpoint_path = (ROOT / args.checkpoint).resolve()
audit_path = (ROOT / args.audit).resolve()
checkpoint = json.loads(checkpoint_path.read_text())
audit = json.loads(audit_path.read_text())
if audit.get("result") != "pass" or audit.get("checkpoint_sha256") != digest(checkpoint_path):
    raise SystemExit("Audit must pass and identify this exact checkpoint")

output = ROOT / "progress"
previous = json.loads((output / "recovery.json").read_text()) if (output / "recovery.json").exists() else {}
main = args.main_functions if args.main_functions is not None else previous.get("maintained_functions")
if not isinstance(main, int) or main < 0:
    raise SystemExit("Supply the audited maintained count with --main-functions")
inventory = ROOT / "local/ghidra-export/functions.tsv"
inventory_hash = digest(inventory)
if previous and inventory_hash != previous["baseline_inventory_sha256"]:
    raise SystemExit("The baseline inventory changed; review the denominator before publishing")
baseline = len(inventory.read_text().splitlines()) - 1
experimental = checkpoint["unpromoted_functions_across_separate_experiments"]
total = main + experimental

# Preserve the existing layout and pinned bytes; only explicitly selected local
# sources enter Git. Nested Ghidra pseudocode and binary/JSON fixtures are excluded.
hashes = {}
for group in ("source_hashes", "platform_source_hashes", "artifact_hashes",
              "harness_hashes", "checker_dependency_hashes"):
    for name, value in checkpoint[group].items():
        path = Path(name)
        if path.is_absolute() or ".." in path.parts:
            raise SystemExit(f"Unexpected checkpoint path: {name}")
        authored = path.parts[0] in {"src", "tools"}
        local_source = path.parent == Path("local/analysis") and (
            path.suffix in {".c", ".h", ".py", ".mjs", ".html"}
            or path.name.endswith((".build.json", "-routines.json")))
        if authored or local_source:
            if digest(ROOT / path) != value:
                raise SystemExit(f"Pinned file changed: {name}")
            hashes[name] = value

report = {
    "metric": "Reported recovered routine count / initial Ghidra inventory (estimate)",
    "limitations": "Counts inherit checkpoint bookkeeping, not an independently deduplicated address ledger. The initial inventory has incomplete function discovery. Not byte matching, instruction coverage, effort completed, or playability.",
    "baseline_functions": baseline,
    "baseline_inventory_sha256": inventory_hash,
    "maintained_functions": main,
    "experimental_functions_in_latest_module": checkpoint["unpromoted_functions_in_this_module"],
    "experimental_functions_across_separate_builds": experimental,
    "reported_recovered_functions": total,
    "decompilation_estimate_percent": round(100 * total / baseline, 2),
    "maintained_estimate_percent": round(100 * main / baseline, 2),
    "playable": checkpoint["playable"],
    "checkpoint": str(checkpoint_path.relative_to(ROOT)),
    "checkpoint_sha256": digest(checkpoint_path),
    "audit": audit,
    "scope": checkpoint["scope"],
    "remaining": checkpoint["unrecovered_lifecycle"],
    "browser_suites": checkpoint["browser_suites"],
    "new_cases": checkpoint["new_cases"],
    "new_calls": checkpoint["new_calls_including_existing_dependencies"],
    "instruction_coverage": checkpoint["instruction_coverage"],
    "main_wasm_sha256": checkpoint["main_wasm_sha256"],
    "experimental_wasm_sha256": checkpoint["wasm_sha256"],
    "published_checkpoint_file_hashes": dict(sorted(hashes.items())),
}
output.mkdir(exist_ok=True)
(output / "recovery.json").write_text(json.dumps(report, indent=2) + "\n")
(output / "publication-files.txt").write_text("".join(name + "\n" for name in sorted(hashes)))
print(f"Decompilation estimate: {report['decompilation_estimate_percent']:.2f}% "
      f"({total:,}/{baseline:,} reported routines; {main:,} maintained + {experimental:,} experimental)")
print(f"Selected {len(hashes)} pinned source, harness and build-metadata files; playable: {report['playable']}")
