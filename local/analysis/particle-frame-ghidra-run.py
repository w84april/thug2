"""Run the local Ghidra project; keep Java settings/cache inside this workspace.

First import:
  python3 tools/ghidra_headless.py -import local/discs/cd3/Crack/THUG2.exe \
      -postScript ExportThugAnalysis.java local/ghidra-export local/analysis/symbols.tsv
Subsequent scripts: use -process THUG2.exe -noanalysis instead of -import.
"""
import subprocess
import sys
from pathlib import Path

root = Path.cwd()
ghidra = root / ".tools/ghidra_12.1.4_PUBLIC"
java = root / ".tools/jdk-21.0.12.1+1/Contents/Home/bin/java"
local = root / "local"
for directory in ("ghidra-projects", "ghidra-user"):
    (local / directory).mkdir(parents=True, exist_ok=True)
command = [str(java), "-Xmx4G", "-Djava.system.class.loader=ghidra.GhidraClassLoader",
           "-Djava.awt.headless=true", "--enable-native-access=ALL-UNNAMED",
           "-Duser.home=" + str(local / "ghidra-user"),
           "-Dapplication.settingsdir=" + str(local / "ghidra-user/settings"),
           "-Dapplication.cachedir=" + str(local / "ghidra-user/cache"),
           "-cp", str(ghidra / "Ghidra/Framework/Utility/lib/Utility.jar"),
           "ghidra.Ghidra", "ghidra.app.util.headless.AnalyzeHeadless",
           str(local / "ghidra-projects"), "THUG2",
           "-scriptPath", str(root / "tools/ghidra"),
           "-analysisTimeoutPerFile", "600", "-max-cpu", "4",
           "-log", str(root / "local/analysis/particle-frame-ghidra.log"), *sys.argv[1:]]
sys.exit(subprocess.call(command, cwd=root))
