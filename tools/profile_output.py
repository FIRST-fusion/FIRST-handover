"""Shared automatic profile postprocessing for FIRST runners (stdlib only)."""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIRST_PYTHON = Path('/home/ouvic/linliu-reproduction-20260911/.venv_uv/bin/python')
DEFAULT_PYTHON = str(FIRST_PYTHON) if FIRST_PYTHON.is_file() else sys.executable
PANELS = ('q', 'pressure', 'jdotb', 'poloidal_current', 'toroidal_current')


def check_plot_python(python):
    subprocess.run([python, '-c', 'import numpy, scipy, matplotlib'], check=True,
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def make_profiles(solver, run, label, python):
    run = Path(run)
    eq, output = run / 'equilibrium', run / 'profiles'
    source = eq / ('linliu_profiles.dat' if solver == 'chease' else 'wout_test.nc')
    command = [python, str(ROOT / 'tools/plot_profiles.py'), '--solver', solver,
               '--source', str(source), '--output', str(output), '--label', label]
    if solver == 'chease':
        command.extend(['--namelist', str(eq / 'namelist')])
    with (run / 'profiles.log').open('w') as log:
        subprocess.run(command, check=True, stdout=log, stderr=subprocess.STDOUT,
                       env={**os.environ, 'OPENBLAS_NUM_THREADS': '1', 'OMP_NUM_THREADS': '1'})
    expected = [f'{key}.{ext}' for key in (*PANELS, 'overview') for ext in ('png', 'pdf')]
    expected += ['profiles.pdf', 'profiles.csv', 'metadata.json']
    for name in expected:
        if not (output / name).is_file() or (output / name).stat().st_size == 0:
            raise ValueError('Missing profile output: ' + name)
    meta = json.loads((output / 'metadata.json').read_text())
    if meta['solver'] != solver or Path(meta['sources'][0]['path']).resolve() != source.resolve():
        raise ValueError('Profiles do not reference this run')
    return {'complete': True, 'single_profiles': 5, 'directory': str(output),
            'overview': str(output / 'overview.png'), 'pdf': str(output / 'profiles.pdf'),
            'metadata': str(output / 'metadata.json'), 'command': command}
