#!/usr/bin/env python3
"""FIRST: replay one archived high-bootstrap equilibrium, then recompute fBS.

No search/closure iteration/DCON is launched. Defaults to archived inputs;
--input-dir accepts edited copies. Use --preflight for checks without execution.
"""
import argparse
import datetime
import json
import math
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from run_case import ROOT, container, extract_equilibrium, preflight, sha
from audit_bootstrap import SOURCE, SOURCE_HASH, validate_settings
from profile_output import DEFAULT_PYTHON, check_plot_python, make_profiles
from editable_inputs import input_files, snapshot, convergence_limit

ARCHIVE = ROOT / 'research-inputs/bootstrap99'
PYTHON = '/home/ouvic/linliu-reproduction-20260911/.venv_uv/bin/python'


def main(argv=None):
    manifest = json.loads((ARCHIVE / 'manifest.json').read_text())
    cases = {case['case']: case for case in manifest['cases']}
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('case', choices=cases)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--input-dir', type=Path, help='Editable inputs; no archived input hash restriction')
    parser.add_argument('--input-file', type=Path, help='Main input file, copied to the solver canonical filename')
    parser.add_argument('--timeout', type=int, default=3600)
    parser.add_argument('--preflight', action='store_true')
    parser.add_argument('--plot-python', default=DEFAULT_PYTHON, help='Python with numpy/scipy/matplotlib for automatic profiles')
    args = parser.parse_args(argv)
    if args.input_file and not args.input_dir:
        args.input_dir = args.input_file.resolve().parent
    if not 1 <= args.timeout <= 14400:
        parser.error('timeout must be 1..14400 seconds')
    solver = cases[args.case]['solver']
    inputs = (args.input_dir or ARCHIVE / 'cases' / args.case / 'inputs').resolve()
    input_files(inputs, solver, args.input_file)
    convergence_limit(inputs, solver, args.input_file)
    if args.input_dir:
        settings_path = inputs / 'bootstrap-settings.json'
        validate_settings(json.loads(settings_path.read_text()) if settings_path.exists() else {})
    cfg = json.loads((ROOT / 'runtime/first.json').read_text())
    if solver == 'chease':
        cfg['binaries']['chease'] = '/home/ouvic/linliu-reproduction-20260911/src_highres/chease_linliu.x'
        cfg['binary_sha256']['chease'] = '6c69f71a88605b9d6963a5f474316393018648a183dcfbf20c7c227eecbd221b'
    # Only this stage is needed; classic DCON is not this research audit's engine.
    cfg = {key: {solver: cfg[key][solver]} for key in ['binaries', 'binary_sha256', 'images']}
    preflight(cfg)
    check_plot_python(args.plot_python)
    source, expected = SOURCE_HASH[solver]
    if sha(SOURCE / source) != expected:
        raise ValueError('Diagnostic source SHA mismatch')
    subprocess.run([PYTHON, '-c', 'import numpy, scipy, netCDF4'], check=True)
    prefix = 'cases/' + args.case + '/'
    for row in manifest['files']:
        if not args.input_dir and row['path'].startswith(prefix) and ('/inputs/' in row['path'] or row['path'] == prefix + 'historical/summary.json'):
            if sha(ARCHIVE / row['path']) != row['sha256']:
                raise ValueError('Archived input/metadata hash mismatch: ' + row['path'])
    if args.preflight:
        print(json.dumps({'case': args.case, 'solver': solver, 'runtime': cfg,
                          'custom_input': bool(args.input_dir), 'input_directory': str(inputs),
                          'preflight_passed': True, 'solver_executed': False}, indent=2))
        return 0
    label = inputs.name if args.input_dir else args.case
    output = (args.output or ROOT / 'runs' / (label + '-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'))).resolve()
    output.mkdir(parents=True, exist_ok=False)
    work = output / 'equilibrium'
    work.mkdir()
    result = {'case': args.case, 'valid': False, 'runtime': cfg, 'stages': [],
              'scientific_acceptance': 'NOT_CERTIFIED: equilibrium and bootstrap audit only; DCON not run',
              'started_at': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        result['input_sha256'] = snapshot(inputs, solver, work, args.input_file)
        result['input_directory'] = str(inputs)
        result['input_file'] = str(args.input_file.resolve()) if args.input_file else str(inputs / ('input.test' if solver == 'vmec' else 'namelist'))
        result['custom_input'] = bool(args.input_dir)
        result['reference_comparison_applicable'] = not bool(args.input_dir)
        metadata = ARCHIVE / prefix / 'historical/summary.json'
        if args.input_dir:
            metadata = work / 'bootstrap-settings.json'
            settings = inputs / 'bootstrap-settings.json'
            metadata.write_text(settings.read_text() if settings.exists() else '{}\n')
            validate_settings(json.loads(metadata.read_text()))
            result['input_sha256'][metadata.name] = sha(metadata)
        limit = convergence_limit(work, solver)
        result['convergence_limit'] = limit
        command = 'exec timeout -k 30 ' + str(args.timeout) + ' /opt/solver '
        command += '< namelist' if solver == 'chease' else 'input.test'
        text = container(solver, cfg, work, command, result['stages'])
        result['metrics'], result['labels'] = {}, {}
        extract_equilibrium(solver, text, work, limit, result['metrics'], result['labels'])
        result['profiles'] = make_profiles(solver, output, label, args.plot_python)
        subprocess.run([PYTHON, str(ROOT / 'tools/audit_bootstrap.py'), solver, str(work),
                        '--metadata', str(metadata)] + (['--custom-input'] if args.input_dir else []), check=True,
                       env={**os.environ, 'OPENBLAS_NUM_THREADS': '1', 'OMP_NUM_THREADS': '1'})
        audit = json.loads((work / 'bootstrap.json').read_text())
        result['bootstrap'] = audit
        result['fbs_total_hirshman'] = audit['fbs_total_hirshman']
        result['fbs_percent'] = audit['fbs_percent']
        result['historical_fbs'] = None if args.input_dir else cases[args.case]['fbs_total_hirshman']
        result['fbs_difference'] = None if args.input_dir else result['fbs_total_hirshman'] - result['historical_fbs']
        result['valid'] = True  # complete equilibrium + finite diagnostic, not stability/closure certification
    except Exception as exc:
        result['error'] = str(exc)
    result['finished_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    (output / 'summary.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'output': str(output), 'valid': result['valid'],
                      'profiles': result.get('profiles'),
                      'fbs': result.get('fbs_total_hirshman'), 'percent': result.get('fbs_percent'),
                      'error': result.get('error')}))
    return 0 if result['valid'] else 1


if __name__ == '__main__':
    sys.exit(main())
