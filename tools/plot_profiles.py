#!/usr/bin/env python3
"""從原始 CHEASE/VMEC 輸出畫五張 profile；不執行 solver。見 docs/PROFILES.md。"""
import argparse
import hashlib
import json
import re
from pathlib import Path

import numpy as np
from scipy.io import netcdf_file
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

MU0 = 4e-7 * np.pi
COLUMNS = 'cs csm psi f ffp p pp q jpar ipar jbH jbS0 jbSc B2 RIIE RIVOL fc cpsrf'.split()
PANELS = {
    'q': ('Safety factor', r'$q$ [dimensionless]'),
    'pressure': ('Pressure', r'$p$ [Pa]'),
    'jdotb': ('Current-field contraction', r'$\langle\mathbf{J}\cdot\mathbf{B}\rangle$ [A T m$^{-2}$]'),
    'poloidal_current': ('Weighted poloidal current', r'$j_u^{\mathrm{prof}}$ [A]'),
    'toroidal_current': ('Weighted toroidal current', r'$j_v^{\mathrm{prof}}$ [A]'),
}
XLABELS = {'s_tor': r'Normalized toroidal flux $s=\Phi/\Phi_{edge}$',
           'rho_tor': r'$\rho_{tor}=\sqrt{\Phi/\Phi_{edge}}$',
           'psi_n': r'Normalized poloidal flux $\psi_N$'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def source_info(path):
    return {'path': str(Path(path).resolve()), 'sha256': hashlib.sha256(Path(path).read_bytes()).hexdigest()}


def scales(path):
    text = re.sub(r'!.*', '', Path(path).read_text())
    values = []
    for key in ('R0EXP', 'B0EXP'):
        hits = re.findall(r'\b' + key + r'\s*=\s*([+\-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eEdD][+\-]?\d+)?)\s*(?=,|/|\s|$)', text, re.I)
        require(len(hits) == 1, f'{key} 必須明確且只出現一次')
        v = float(hits[0].replace('D', 'e').replace('d', 'e'))
        require(np.isfinite(v) and v > 0, f'{key} 必須為正有限數')
        values.append(v)
    return values


def check_profiles(data):
    n = len(data['s_tor'])
    require(n >= 4, '至少需要四個原生取樣點')
    for key, arr in data.items():
        require(np.asarray(arr).shape == (n,) and np.all(np.isfinite(arr)), f'{key}: shape/nonfinite 錯誤')
    for key in ('s_tor', 'psi_n', 'rho_tor'):
        a = data[key]
        require(np.all(np.diff(a) > 0) and a[0] >= 0 and np.isclose(a[-1], 1), f'{key}: 座標必須單調且位於 [0,1]')


def load_chease(source, namelist):
    a = np.loadtxt(source, ndmin=2)
    require(a.shape[1] == 18 and len(a) >= 4 and np.all(np.isfinite(a)), 'CHEASE 必須有18欄有限資料，至少4列')
    c = dict(zip(COLUMNS, a.T))
    r0, b0 = scales(namelist)
    cs, cm, cp, q = c['cs'], c['csm'], c['cpsrf'], c['q']
    require(np.all(np.diff(cs) > 0) and np.isclose(cs[0], 0) and np.isclose(cs[-1], 1), 'cs 必須由0單調增加至1')
    require(cp[0] > 0 and np.allclose(cp, cp[0]), 'CPSRF 必須為正常數')
    require(np.allclose(cm, np.r_[(cs[1:]+cs[:-1])/2, 1.], rtol=1e-7, atol=1e-12), 'csm 不是預期中點取樣')
    require(np.allclose(c['psi'], cm**2*cp, rtol=1e-7, atol=1e-12), 'psi/CPSRF 與 csm 不符')
    require(np.all(q > 0) and np.all(c['f'] != 0), '此 CHEASE 轉換需要 q>0 與 f!=0')
    tor = np.r_[0., np.cumsum(q[:-1] * np.diff(cs**2) * cp[0])]
    edge = tor[-1]
    require(np.isfinite(edge) and edge > 0, '無效環向磁通積分')
    sb = tor / edge
    s = np.r_[(sb[1:]+sb[:-1])/2, 1.]
    dpsi_ds = edge / q
    data = {'s_tor': s, 'rho_tor': np.sqrt(s), 'psi_n': cm**2,
            'q': q, 'pressure': c['p']*b0**2/MU0,
            'jdotb': c['jpar']*b0**2/(MU0*r0),
            'poloidal_current': c['ffp']/c['f']*dpsi_ds*b0*r0/MU0,
            'toroidal_current': c['RIIE']*dpsi_ds*b0*r0/(2*np.pi*MU0)}
    check_profiles(data)
    meta = {'sources': [source_info(source), source_info(namelist)], 'R0_m': r0, 'B0_T': b0,
            'column_numbers_1based': {k: i+1 for i, k in enumerate(COLUMNS)},
            'flux_integral_normalized': float(edge), 'flux_edge_magnitude_Wb': float(2*np.pi*edge*b0*r0**2),
            'sampling': 'Original radial midpoints plus edge diagnostic; no invented axis point',
            'coordinate_formula': 'T=cumsum(q[:-1]*diff(cs**2)*CPSRF); s=midpoints(T/Tedge), last=1; psi_n=csm**2',
            'quantity_formulas': {'q': 'column8', 'pressure': 'p*B0**2/mu0', 'jdotb': 'jpar*B0**2/(mu0*R0)',
                                 'poloidal_current': '(ffp/f)*(Tedge/q)*B0*R0/mu0',
                                 'toroidal_current': 'RIIE*(Tedge/q)*B0*R0/(2*pi*mu0)'}}
    return data, meta


def load_vmec(source):
    names = ['phi', 'chi', 'presf', 'iotaf', 'jdotb', 'jcuru', 'jcurv']
    with netcdf_file(source, mmap=False) as f:
        require(all(k in f.variables for k in names), 'VMEC 缺少必要 full-mesh 變數')
        v = {k: np.array(f.variables[k].data, dtype=float, copy=True) for k in names}
    n = len(v['phi'])
    require(n >= 4 and all(x.shape == (n,) and np.all(np.isfinite(x)) for x in v.values()), 'VMEC 變數 shape/nonfinite 錯誤')
    require(np.all(v['iotaf'] != 0), 'iotaf=0，q 不有限')
    for k in ('phi', 'chi'):
        require(v[k][-1] != v[k][0], f'{k} 磁通範圍為0')
    s = (v['phi']-v['phi'][0])/(v['phi'][-1]-v['phi'][0])
    require(np.all(s >= 0), '負正規化環向磁通座標')
    data = {'s_tor': s, 'rho_tor': np.sqrt(s),
            'psi_n': (v['chi']-v['chi'][0])/(v['chi'][-1]-v['chi'][0]),
            'q': 1/v['iotaf'], 'pressure': v['presf'], 'jdotb': v['jdotb'],
            'poloidal_current': v['jcuru'], 'toroidal_current': v['jcurv']}
    check_profiles(data)
    meta = {'sources': [source_info(source)], 'sampling': 'Native full mesh, source-side extrapolated endpoints retained',
            'coordinate_formula': 's=(phi-phi_axis)/(phi_edge-phi_axis); psi_n=(chi-chi_axis)/(chi_edge-chi_axis)',
            'quantity_formulas': {'q': '1/iotaf', 'pressure': 'presf [already Pa]', 'jdotb': 'jdotb',
                                 'poloidal_current': 'jcuru [already A]', 'toroidal_current': 'jcurv [already A]'},
            'source_linear_endpoint_flags': {k: {'axis': bool(np.isclose(v[k][0], 2*v[k][1]-v[k][2])),
                                                 'edge': bool(np.isclose(v[k][-1], 2*v[k][-2]-v[k][-3]))}
                                             for k in ('jcuru', 'jcurv', 'jdotb')}}
    return data, meta


def render(data, meta, output, label, solver, x='s_tor'):
    check_profiles(data)
    output = Path(output)
    require(not output.exists(), '輸出目錄已存在，拒絕覆蓋')
    output.mkdir(parents=True, exist_ok=False)
    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False,
                         'pdf.fonttype': 42, 'savefig.dpi': 180})
    color = '#176a91' if solver == 'chease' else '#ab4d22'
    title = f'{solver.upper()} | {label}'
    footer = f'Source: {Path(meta["sources"][0]["path"]).name} | native signs; no clipping or smoothing'
    def panel(ax, key):
        name, unit = PANELS[key]
        ax.plot(data[x], data[key], color=color, linewidth=1.7)
        ax.set(title=name, xlabel=XLABELS[x], ylabel=unit, xlim=(0, 1))
        ax.grid(alpha=.18)
        ax.ticklabel_format(axis='y', style='sci', scilimits=(-3, 4), useMathText=True)
    with PdfPages(output/'profiles.pdf') as pdf:
        for key in PANELS:
            fig, ax = plt.subplots(figsize=(7.5, 4.8))
            panel(ax, key)
            fig.suptitle(title, fontsize=10)
            fig.text(.02, .015, footer, fontsize=7)
            fig.tight_layout(rect=(0, .045, 1, .95))
            for ext in ('png', 'pdf'):
                fig.savefig(output/f'{key}.{ext}')
            pdf.savefig(fig)
            plt.close(fig)
    fig, axes = plt.subplots(2, 3, figsize=(14, 8.2))
    for ax, key in zip(axes.flat, PANELS):
        panel(ax, key)
    axes.flat[-1].axis('off')
    axes.flat[-1].text(0, .9, 'PROFILE DEFINITIONS\n\nCurrent panels: Jacobian-weighted [A],\nnot local current density [A/m2].\n\nJ.B is a current-field contraction,\nnot J_parallel.\n\nNative signs and endpoints retained.\nPlotting is not a stability test.\n\nExact source files and SHA-256:\nmetadata.json', va='top', fontsize=10, linespacing=1.5)
    fig.suptitle(title, fontsize=13)
    fig.text(.02, .012, footer, fontsize=8)
    fig.tight_layout(rect=(0, .04, 1, .95), w_pad=2.8)
    for ext in ('png', 'pdf'):
        fig.savefig(output/f'overview.{ext}')
    plt.close(fig)
    keys = list(data)
    np.savetxt(output/'profiles.csv', np.column_stack([data[k] for k in keys]), delimiter=',', header=','.join(keys), comments='')
    meta.update({'solver': solver, 'case': label, 'coordinate_plotted': x, 'points': len(data[x]),
                 'units': {'s_tor': '1', 'rho_tor': '1', 'psi_n': '1', 'q': '1', 'pressure': 'Pa',
                           'jdotb': 'A T/m2', 'poloidal_current': 'A', 'toroidal_current': 'A'},
                 'scientific_acceptance': 'NOT_CERTIFIED: plotting does not test stability',
                 'native_signs_retained': True, 'extrema': {k: {'min': float(min(v)), 'max': float(max(v))} for k,v in data.items()},
                 'plotter_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    (output/'metadata.json').write_text(json.dumps(meta, indent=2, allow_nan=False)+'\n')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--solver', choices=['chease', 'vmec'], required=True)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--namelist', type=Path)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--label', default='equilibrium')
    p.add_argument('--x', choices=XLABELS, default='s_tor')
    a = p.parse_args()
    try:
        require(not a.output.exists(), '輸出目錄已存在，拒絕覆蓋')
        require(a.solver != 'chease' or a.namelist is not None, 'CHEASE 需要 --namelist')
        data, meta = load_chease(a.source, a.namelist) if a.solver == 'chease' else load_vmec(a.source)
        render(data, meta, a.output, a.label, a.solver, a.x)
    except (ValueError, OSError, KeyError, TypeError) as e:
        p.exit(2, f'plot_profiles: {e}\n')
    print(json.dumps({'output': str(a.output), 'points': len(data['s_tor']), 'single_profiles': 5}))


if __name__ == '__main__':
    main()
