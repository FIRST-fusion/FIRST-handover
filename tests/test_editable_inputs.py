import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
import case
import editable_inputs as inputs
import audit_bootstrap
import compare


class EditableInputsTests(unittest.TestCase):
    def test_all_templates_have_convergence_controls(self):
        for item in case.templates().values():
            self.assertGreater(inputs.convergence_limit(item['source'], item['solver']), 0)

    def test_init_copy_edit_snapshot_leaves_template_unchanged(self):
        original = (inputs.ROOT/'examples/vmec_lowbeta/input.test').read_bytes()
        with tempfile.TemporaryDirectory() as temp:
            path = case.initialize(str(Path(temp)/'mine'), 'vmec_lowbeta')
            p = path/'input.test'
            p.write_text(p.read_text().replace('PRES_SCALE=2000', 'PRES_SCALE=1500'))
            (path/'wout_test.nc').write_bytes(b'STALE')
            (path/'run.log').write_text('STALE')
            work = Path(temp)/'work';work.mkdir()
            digest = inputs.snapshot(path, 'vmec', work)
            self.assertEqual(set(digest), {'input.test'})
            self.assertEqual((work/'input.test').read_bytes(), p.read_bytes())
            self.assertEqual((inputs.ROOT/'examples/vmec_lowbeta/input.test').read_bytes(), original)
            self.assertNotIn('wout_test.nc', [p.name for p in work.iterdir()])
            with self.assertRaises(FileExistsError):case.initialize(str(path), 'vmec_lowbeta')

    def test_chease_missing_namelist_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, 'namelist'):inputs.input_files(temp, 'chease')

    def test_tolerance_uses_last_active_mesh_with_repeat_and_index(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'input.test'
            p.write_text('&INDATA\n NS_ARRAY=31,65,129,2*0, FTOL_ARRAY=2*1d-8,1d-12,2*0, ! comment\n FTOL_ARRAY(3)=2d-13, /')
            self.assertEqual(inputs.convergence_limit(temp,'vmec'),2e-13)
            p.write_text('&INDATA NS_ARRAY=31,65,129, FTOL_ARRAY=1e-8, /')
            with self.assertRaises(ValueError):inputs.convergence_limit(temp,'vmec')
            p.write_text('&INDATA NS_ARRAY=31, FTOL_ARRAY=1e-8, FTOL_ARRAY(1:2)=2*1e-12, /')
            with self.assertRaises(ValueError):inputs.convergence_limit(temp,'vmec')
            p.write_text('&INDATA NS_ARRAY=31, FTOL_ARRAY=NaN, /')
            with self.assertRaises(ValueError):inputs.convergence_limit(temp,'vmec')

    def test_chease_nonpositive_tolerance_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            (Path(temp)/'namelist').write_text('$EQDATA EPSLON=-1d-10, $END')
            with self.assertRaises(ValueError):inputs.convergence_limit(temp,'chease')

    def test_new_inputs_forwarded_without_reference_substitution(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp);(path/'case.json').write_text('{"template":"vmec_lowbeta"}')
            with patch.object(sys,'argv',['case.py','run',temp,'--preflight']), patch.object(case.subprocess,'run',return_value=SimpleNamespace(returncode=0)) as run:
                self.assertEqual(case.main(),0)
                cmd=run.call_args.args[0]
                self.assertEqual(cmd[cmd.index('--input-dir')+1],temp)
                self.assertIn('--preflight',cmd)

    def test_custom_bootstrap_does_not_inherit_default_closure(self):
        module=SimpleNamespace(diagnostics=lambda _: {'closure_max_relative':0.0001,'fbs_total_hirshman':0.7})
        with patch.object(audit_bootstrap,'module_for',return_value=module):
            result=audit_bootstrap.audit('chease',Path('.'),{},custom_input=True)
        self.assertIsNone(result['closure_below_1e-3'])
        self.assertNotIn('closure_max_relative',result)
        self.assertEqual(result['fbs_percent'],70)

    def test_invalid_seed_rejected(self):
        for settings in ({'seed_axis':.3}, {'seed_axis':.3,'seed_center':.5,'seed_width':0}, {'seed_axis':'x','seed_center':.5,'seed_width':.03}):
            with self.assertRaises(ValueError):audit_bootstrap.validate_settings(settings)

    def test_custom_case_not_certified_by_reference_comparator(self):
        actual={'valid':True,'custom_input':True,'metrics':{'q':1},'labels':{}}
        expected={'metrics':{'q':{'value':1,'rtol':0,'atol':0}},'labels':{}}
        result=compare.compare(actual,expected)
        self.assertFalse(result['passed'])
        self.assertIn('custom_input',[e['code'] for e in result['errors']])
