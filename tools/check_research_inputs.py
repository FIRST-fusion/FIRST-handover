#!/usr/bin/env python3
"""Check historical input bytes and index provenance; never execute a solver."""
import hashlib
import json
import math
import sys
from pathlib import Path


def check(root):
    manifest = json.loads((root / 'manifest.json').read_text())
    errors = []
    paths = set()
    for row in manifest['files']:
        name = row['path']
        path = (root / name).resolve()
        if name in paths or root not in path.parents or not path.is_file():
            errors.append(f'{name}: duplicate, unsafe or missing file')
            continue
        paths.add(name)
        data = path.read_bytes()
        if len(data) != row['bytes'] or hashlib.sha256(data).hexdigest() != row['sha256']:
            errors.append(f'{name}: size/hash mismatch')
    cases = manifest['cases']
    names = {case['case'] for case in cases}
    if not cases or len(names) != len(cases) or len(cases) != manifest['case_count']:
        errors.append('Empty/duplicate/inconsistent case index')
    for case in cases:
        prefix = 'cases/' + case['case'] + '/'
        required = ('namelist', 'EXPEQ', 'NIN') if case['solver'] == 'chease' else ('input.test',)
        for name in required:
            if prefix + 'inputs/' + name not in paths:
                errors.append(f'{prefix}{name}: required input not recorded')
        evidence_name = prefix + case['fbs_evidence']
        summary_name = prefix + 'historical/summary.json'
        if evidence_name not in paths or summary_name not in paths:
            errors.append(f'{prefix}: unrecorded summary/bootstrap evidence')
            continue
        evidence = json.loads((root / evidence_name).read_text())
        summary = json.loads((root / summary_name).read_text())
        fbs = case['fbs_total_hirshman']
        if not math.isfinite(fbs) or not 0.99 <= fbs <= 1 or fbs != evidence.get('fbs_total_hirshman'):
            errors.append(f'{prefix}: fBS not supported by raw evidence')
        beta = evidence.get('beta_vac', summary.get('beta_vac'))
        if case['beta_vac'] != beta:
            errors.append(f'{prefix}: beta not supported by raw evidence')
        field = case['closure_field']
        if field is not None and case['closure_relative'] != summary.get(field):
            errors.append(f'{prefix}: closure definition/value mismatch')
        if case['solver'] == 'vmec':
            parent = case['parent']
            if not parent or Path(parent).name not in names:
                errors.append(f'{prefix}: missing CHEASE parent input')
        if case['new_solver_execution'] is not False or case['full_stability_certified'] is not False:
            errors.append(f'{prefix}: historical archive mislabelled as new/certified')
    for path in (root / 'cases').rglob('*'):
        if path.is_file() and path.relative_to(root).as_posix() not in paths:
            errors.append(f'{path.relative_to(root)}: unrecorded artifact')
    return {'cases': len(cases), 'files_checked': len(manifest['files']),
            'passed': not errors, 'solver_executed': False, 'errors': errors}


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1] / 'research-inputs/bootstrap99'
    result = check(root)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result['passed'] else 1)
