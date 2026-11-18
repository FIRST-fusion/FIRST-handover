"""Synthetic physical normalization, malformed inputs, and archive-only CLI tests."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
from scipy.io import netcdf_file

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('plot_profiles', ROOT/'tools/plot_profiles.py')
plot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(plot)


class ProfilesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.nml = self.root/'namelist'
        self.nml.write_text('&eq R0EXP=4.5d-1, B0EXP=2.0, / ! R0EXP=999\n')
        cs = np.array([0., .25, .7, 1.])
        cm = np.r_[(cs[1:]+cs[:-1])/2, 1.]
        self.a = np.ones((4, 18))
        self.a[:, 0] = cs; self.a[:, 1] = cm; self.a[:, 2] = cm**2
        self.a[:, 7] = [2., 3., 5., 6.]
        self.a[:, 8] = -2.
        self.dat = self.root/'linliu_profiles.dat'
        np.savetxt(self.dat, self.a)

    def test_integral_not_multiply_and_scaling(self):
        d, meta = plot.load_chease(self.dat, self.nml)
        expected = np.dot([2., 3., 5.], np.diff(self.a[:, 0]**2))
        self.assertAlmostEqual(meta['flux_integral_normalized'], expected)
        self.assertFalse(np.allclose(d['s_tor'], self.a[:, 1]**2))
        self.assertGreater(d['s_tor'][0], 0)  # no fake axis
        np.testing.assert_allclose(d['pressure'], 4/plot.MU0)
        np.testing.assert_allclose(d['jdotb'], -8/(.45*plot.MU0))
        np.testing.assert_allclose(d['poloidal_current'], expected/self.a[:, 7]*.9/plot.MU0)
        np.testing.assert_allclose(d['toroidal_current'], expected/self.a[:, 7]*.9/(2*np.pi*plot.MU0))

    def test_reject_nonfinite_shape_zero_and_grid(self):
        for field, value in [(5, np.nan), (7, 0.), (3, 0.), (17, 0.)]:
            with self.subTest(field=field):
                a = self.a.copy(); a[1, field] = value; np.savetxt(self.dat, a)
                with self.assertRaises(ValueError): plot.load_chease(self.dat, self.nml)
        np.savetxt(self.dat, self.a[:, :-1])
        with self.assertRaises(ValueError): plot.load_chease(self.dat, self.nml)
        a = self.a.copy(); a[2, 0] = 0; np.savetxt(self.dat, a)
        with self.assertRaises(ValueError): plot.load_chease(self.dat, self.nml)

    def test_require_explicit_unique_normalization(self):
        for text in ['R0EXP=1', 'R0EXP=1, R0EXP=2, B0EXP=1', 'R0EXP=-1, B0EXP=1']:
            self.nml.write_text(text)
            with self.assertRaises(ValueError): plot.scales(self.nml)

    def make_vmec(self, zero_iota=False):
        path = self.root/'wout.nc'
        with netcdf_file(path, 'w') as f:
            f.createDimension('radius', 4)
            values = {'phi': [0, -1, -2, -3], 'chi': [0, .3, .7, 1.],
                      'presf': [30., 20., 10., -.01], 'iotaf': [1., .8, 0 if zero_iota else .6, .4],
                      'jdotb': [-2., -1., 0., 1.], 'jcuru': [-20., -10., 0., 10.],
                      'jcurv': [2., 3., 4., 5.]}
            for k, v in values.items(): f.createVariable(k, 'd', ('radius',))[:] = v
        return path

    def test_vmec_no_extra_mu0_preserves_signs_and_endpoints(self):
        d, meta = plot.load_vmec(self.make_vmec())
        np.testing.assert_allclose(d['poloidal_current'], [-20, -10, 0, 10])
        self.assertEqual(d['pressure'][-1], -.01)
        self.assertEqual(d['q'][-1], 2.5)
        self.assertTrue(meta['source_linear_endpoint_flags']['jcuru']['axis'])

    def test_vmec_zero_iota_rejected(self):
        with self.assertRaises(ValueError): plot.load_vmec(self.make_vmec(True))

    def test_cli_outputs_and_no_overwrite(self):
        out = self.root/'plots'
        cmd = [sys.executable, str(ROOT/'tools/plot_profiles.py'), '--solver', 'chease',
               '--source', str(self.dat), '--namelist', str(self.nml), '--output', str(out), '--label', 'synthetic']
        p = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(len(list(out.glob('*.png'))), 6)
        self.assertEqual(len(list(out.glob('*.pdf'))), 7)
        self.assertEqual(json.loads((out/'metadata.json').read_text())['points'], 4)
        before = {p.name:p.read_bytes() for p in out.iterdir()}
        p = subprocess.run(cmd, capture_output=True, text=True)
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual(before, {p.name:p.read_bytes() for p in out.iterdir()})
