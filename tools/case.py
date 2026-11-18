#!/usr/bin/env python3
"""建立可編輯 input：case.py init NAME --from TEMPLATE；修改後：case.py run NAME。"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from editable_inputs import ROOT, input_files


def templates():
    cfg = json.loads((ROOT / 'runtime/first.json').read_text())
    result = {name: {'runner': 'run_case.py', 'solver': row['solver'], 'source': ROOT/'examples'/name}
              for name, row in cfg['cases'].items()}
    archive = ROOT / 'research-inputs/bootstrap99'
    for row in json.loads((archive/'manifest.json').read_text())['cases']:
        result[row['case']] = {'runner': 'run_bootstrap_case.py', 'solver': row['solver'],
                               'source': archive/'cases'/row['case']/'inputs'}
    return result


def case_path(name):
    if not name or name in ('.', '..'):
        raise ValueError('Specify a case name or input directory')
    path = Path(name)
    return (ROOT/'inputs'/path if len(path.parts) == 1 else path).resolve()


def initialize(name, template):
    target = case_path(name)
    entry = templates()[template]
    files = input_files(entry['source'], entry['solver'])
    target.mkdir(parents=True, exist_ok=False)
    for source in files:
        shutil.copy2(source, target/source.name)
    (target/'case.json').write_text(json.dumps({'template': template}, indent=2)+'\n')
    if entry['runner'] == 'run_bootstrap_case.py':
        historical = json.loads((entry['source'].parent/'historical/summary.json').read_text())
        seed = {k: historical[k] for k in ('seed_axis', 'seed_center', 'seed_width') if k in historical}
        (target/'bootstrap-settings.json').write_text(json.dumps(seed, indent=2)+'\n')
    print('Editable inputs: ' + str(target))
    print('Edit ' + ('input.test' if entry['solver'] == 'vmec' else 'namelist / EXPEQ / NIN') + ' with your editor.')
    print('Run: python3 tools/case.py run ' + str(target))
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    init = sub.add_parser('init', help='Copy a template into new editable inputs')
    init.add_argument('name')
    init.add_argument('--from', dest='template', choices=templates(), required=True)
    run = sub.add_parser('run', help='Run edited inputs and generate profiles')
    run.add_argument('name')
    run.add_argument('--output', type=Path)
    run.add_argument('--preflight', action='store_true')
    run.add_argument('--plot-python')
    run.add_argument('--timeout', type=int)
    args = parser.parse_args()
    try:
        if args.action == 'init':
            initialize(args.name, args.template)
            return 0
        path = case_path(args.name)
        template = json.loads((path/'case.json').read_text())['template']
        entry = templates()[template]
        command = [sys.executable, str(ROOT/'tools'/entry['runner']), template, '--input-dir', str(path)]
        for flag in ('output', 'plot_python', 'timeout'):
            value = getattr(args, flag)
            if value is not None:
                command.extend(['--'+flag.replace('_', '-'), str(value)])
        if args.preflight:
            command.append('--preflight')
        return subprocess.run(command).returncode
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(2, str(exc)+'\n')


if __name__ == '__main__':
    sys.exit(main())
