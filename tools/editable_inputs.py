"""Input snapshots and convergence controls for user-owned editable cases."""
import hashlib
import math
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = {'vmec': ('input.test',), 'chease': ('namelist', 'EXPEQ', 'NIN')}


def identify_input(target, solver_hint=None):
    target = Path(target).resolve()
    if target.is_dir():
        candidates = [(target / name) for kind, name in [('vmec', 'input.test'), ('chease', 'namelist')]
                      if (solver_hint is None or solver_hint == kind) and (target / name).is_file()]
        if len(candidates) != 1:
            raise ValueError('資料夾需有 input.test 或 namelist；兩者並存時請指定檔案或 --solver')
        target = candidates[0]
    if not target.is_file():
        raise ValueError('找不到 input：' + str(target))
    text = re.sub(r'!.*', '', target.read_text())
    groups = set(re.findall(r'[$&]\s*(indata|eqdata)\b', text, re.I))
    kinds = {'vmec' if group.lower() == 'indata' else 'chease' for group in groups}
    if len(kinds) != 1:
        raise ValueError('無法辨識 input：需有 VMEC &INDATA 或 CHEASE $EQDATA/&EQDATA')
    solver = kinds.pop()
    if solver_hint and solver_hint != solver:
        raise ValueError('指定的 solver 與 input 內容不符')
    return target.parent, target, solver


def input_files(directory, solver, main_file=None):
    directory = Path(directory).resolve()
    if not directory.is_dir():
        raise ValueError('Input directory not found: ' + str(directory))
    required = 'input.test' if solver == 'vmec' else 'namelist'
    main = Path(main_file).resolve() if main_file is not None else directory / required
    if not main.is_file():
        raise ValueError('Missing required input: ' + required)
    return [main] + [directory / n for n in FILES[solver][1:] if (directory / n).is_file()]


def snapshot(directory, solver, work, main_file=None):
    # Copy only solver inputs, never old outputs/run.log from an existing run.
    result = {}
    for i, source in enumerate(input_files(directory, solver, main_file)):
        target = Path(work) / (FILES[solver][0] if i == 0 else source.name)
        shutil.copy2(source, target)
        result[target.name] = hashlib.sha256(target.read_bytes()).hexdigest()
    return result


def assignments(text, key):
    text = re.sub(r'!.*', '', text)
    pattern = r'\b' + key + r'\s*(?:\(\s*(\d+)\s*\))?\s*=\s*(.*?)(?=\b[A-Za-z_]\w*\s*(?:\([^)]*\))?\s*=|[/$]|\Z)'
    matches = list(re.finditer(pattern, text, re.I | re.S))
    count = len(re.findall(r'\b' + key + r'\s*(?:\([^)]*\))?\s*=', text, re.I))
    if len(matches) != count:
        raise ValueError('Unsupported namelist index/slice for ' + key)
    result = {}
    for match in matches:
        index = int(match[1] or 1)
        for token in re.split(r'[,\s]+', match[2].strip().rstrip(',')):
            if not token:
                continue
            count, value = token.split('*') if '*' in token else ('1', token)
            count = int(count)
            if not 1 <= count <= 1000:
                raise ValueError('Invalid namelist repeat count')
            value = float(value.replace('d', 'e').replace('D', 'E'))
            if not math.isfinite(value):
                raise ValueError('Nonfinite input: ' + key)
            for _ in range(count):
                result[index] = value
                index += 1
    if not result:
        raise ValueError('Missing or unsupported namelist assignment: ' + key)
    return result


def convergence_limit(directory, solver, main_file=None):
    name = 'input.test' if solver == 'vmec' else 'namelist'
    text = (Path(main_file) if main_file is not None else Path(directory) / name).read_text()
    if solver == 'chease':
        limit = assignments(text, 'EPSLON')[1]
    else:
        mesh = assignments(text, 'NS_ARRAY')
        active = [i for i, n in mesh.items() if n > 0]
        if not active:
            raise ValueError('NS_ARRAY has no active grid')
        tolerances = assignments(text, 'FTOL_ARRAY')
        if max(active) not in tolerances:
            raise ValueError('Specify FTOL_ARRAY for the final active NS_ARRAY grid')
        limit = tolerances[max(active)]
    if not math.isfinite(limit) or limit <= 0:
        raise ValueError('Convergence tolerance must be positive and finite')
    return limit
