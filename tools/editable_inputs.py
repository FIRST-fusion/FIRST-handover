"""Input snapshots and convergence controls for user-owned editable cases."""
import hashlib
import math
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = {'vmec': ('input.test',), 'chease': ('namelist', 'EXPEQ', 'NIN')}


def input_files(directory, solver):
    directory = Path(directory).resolve()
    if not directory.is_dir():
        raise ValueError('Input directory not found: ' + str(directory))
    required = 'input.test' if solver == 'vmec' else 'namelist'
    if not (directory / required).is_file():
        raise ValueError('Missing required input: ' + required)
    return [directory / n for n in FILES[solver] if (directory / n).is_file()]


def snapshot(directory, solver, work):
    # Copy only solver inputs, never old outputs/run.log from an existing run.
    result = {}
    for source in input_files(directory, solver):
        target = Path(work) / source.name
        shutil.copy2(source, target)
        result[source.name] = hashlib.sha256(target.read_bytes()).hexdigest()
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


def convergence_limit(directory, solver):
    name = 'input.test' if solver == 'vmec' else 'namelist'
    text = (Path(directory) / name).read_text()
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
