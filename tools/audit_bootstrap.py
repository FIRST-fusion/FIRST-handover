#!/usr/bin/env python3
"""Audit a fresh working directory with the pinned FIRST research diagnostics.

Run with FIRST's existing .venv_uv Python. No solver is executed here.
"""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path

SOURCE = Path('/home/ouvic/linliu-reproduction-20260911/src')
SOURCE_HASH = {
    'chease': ('campaign.py', '52d39f6bcae50e30126c7223793fdae0614553f46d3b9d266789a8def1dc855b'),
    'vmec': ('vmec_bootstrap.py', '0b94f33536af1a84e2a27a22efe75fd63ee3f6aedf9c3f64f4d5fc6df5994104'),
}


def module_for(solver):
    name, digest = SOURCE_HASH[solver]
    path = SOURCE / name
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise ValueError('Research diagnostic source SHA mismatch: ' + str(path))
    spec = importlib.util.spec_from_file_location('first_bootstrap_diagnostic', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def audit(solver, work, metadata):
    module = module_for(solver)
    if solver == 'chease':
        import numpy as np
        result = module.diagnostics(work)
        # A=1.2 uses a different prescribed seed: do not report the legacy
        # center=.5 closure as the actual case's closure.
        if 'seed_axis' in metadata:
            profile = np.loadtxt(work / 'linliu_profiles.dat')
            center = metadata.get('seed_center', .5)
            width = metadata.get('seed_width', .03)
            shape = .5 * (1 - np.tanh((profile[:, 1]**2 - center) / width))
            target = np.maximum(metadata['seed_axis'] * shape, profile[:, 10])
            result['closure_default_seed_diagnostic'] = result.pop('closure_max_relative')
            result['closure_fixed_seed'] = float(np.max(abs(profile[:, 8] - target)) / np.max(abs(target)))
            result['seed'] = {key: metadata.get(key, default) for key, default in
                              [('seed_axis', None), ('seed_center', .5), ('seed_width', .03)]}
            closure = result['closure_fixed_seed']
        else:
            closure = result['closure_max_relative']
        result['closure_below_1e-3'] = closure < 1e-3
        result['method'] = 'CHEASE exported Hirshman current + toroidal auxiliary-current integral'
    else:
        # pathlib joining an absolute case path resolves to this new work dir,
        # not the archived ROOT/runs. Never write audit outputs into archives.
        for suffix in ['json', 'dat']:
            if (work / ('bootstrap_hirshman_handover.' + suffix)).exists():
                raise FileExistsError('Refuse to replace an existing VMEC audit')
        result = module.audit(str(work.resolve()), tag='_handover')
        result['closure_below_1e-3'] = None  # VMEC audit measures fBS, not fixed-seed closure.
    ratio = result['fbs_total_hirshman']
    if not math.isfinite(ratio):
        raise ValueError('Nonfinite bootstrap ratio')
    result['fbs_percent'] = 100 * ratio
    result['ratio_in_physical_range'] = 0 <= ratio <= 1
    result['diagnostic_source_sha256'] = SOURCE_HASH[solver][1]
    result['scientific_acceptance'] = 'NOT_CERTIFIED: fBS is not a stability test'
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('solver', choices=SOURCE_HASH)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--metadata', type=Path, required=True)
    args = parser.parse_args()
    work = args.directory.resolve()
    output = work / 'bootstrap.json'
    if output.exists():
        raise FileExistsError(output)
    result = audit(args.solver, work, json.loads(args.metadata.read_text()))
    with output.open('x') as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({'output': str(output), 'fbs': result['fbs_total_hirshman'],
                      'percent': result['fbs_percent']}))


if __name__ == '__main__':
    main()
