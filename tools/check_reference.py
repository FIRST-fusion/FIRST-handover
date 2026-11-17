#!/usr/bin/env python3
"""Verify the selected reference artifacts against the recorded SHA-256 manifest."""
import hashlib,json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
rows=json.loads((root/'evidence/reference_manifest.json').read_text())
errors=[]
for row in rows:
    p=(root/row['path']).resolve()
    if root not in p.parents or not p.is_file():errors.append(row['path']+': missing/unsafe');continue
    if hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:errors.append(row['path']+': hash mismatch')
if not rows:errors.append('Empty reference manifest')
print(json.dumps({'checked':len(rows),'passed':not errors,'errors':errors},indent=2))
sys.exit(1 if errors else 0)
