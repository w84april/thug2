"""Advance the actual scene-file trace through the first sector's mesh header."""
from pathlib import Path
source=Path('local/analysis/trace-level-scene.py').read_text()
source=source.replace('first sector streaming parser','first streamed mesh body')
source=source.replace('0x4c6b10','0x4d6100').replace('level-scene-trace.json','level-mesh-entry-trace.json')
exec(compile(source,'<original scene stream through first mesh entry>','exec'))
