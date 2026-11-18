import importlib.util,tempfile,unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
spec=importlib.util.spec_from_file_location('run_case',Path(__file__).resolve().parents[1]/'tools/run_case.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)

class RunnerChecks(unittest.TestCase):
    def test_chease_residual_and_interface(self):
        text='RESIDU = 1e-11\nSOME QUANTITIES AND THEIR MKSA VALUES\nLINLIU_BETAX = 0.2\nTOTAL CURRENT = 5.5'
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);(p/'INP1').write_bytes(b'nonempty')
            self.assertEqual(r.extract_equilibrium('chease',text,p,1e-10,{},{}),p/'INP1')
            with self.assertRaises(ValueError):r.extract_equilibrium('chease',text.replace('1e-11','1e-4'),p,1e-10,{}, {})
            with self.assertRaises(ValueError):r.extract_equilibrium('chease',text+' NaN',p,1e-10,{}, {})
    def test_vmec_uses_final_residual_not_exit_marker_only(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);(p/'dcon_test.txt').write_text('interface');(p/'wout_test.nc').write_bytes(b'NC')
            log='EXECUTION TERMINATED NORMALLY\n 100 1e-3 1e-3 1e-3 1.5 0.7 0.01\n'
            with self.assertRaises(ValueError):r.extract_equilibrium('vmec',log,p,1e-12,{}, {})
            log+=' 200 1e-14 1e-15 1e-16 1.5 0.7 0.01\n'
            self.assertEqual(r.extract_equilibrium('vmec',log,p,1e-12,{}, {}),p/'dcon_test.txt')
            with self.assertRaises(ValueError):r.extract_equilibrium('vmec',log+'aborting',p,1e-12,{}, {})
    def test_dcon_missing_stable_label_not_inferred(self):
        log="Starting integration of ODE's\nq0=1.2 qmin=1.2 qa=2.0 betat=.01 betan=.1 total=-.2\nFree-boundary mode unstable\nBallooning stable\nMercier stable\nPROGRAM_STOP => Normal termination.\nIEEE_DIVIDE_BY_ZERO"
        metrics,labels,warnings={},{},[]
        r.extract_dcon(log,metrics,labels,warnings)
        self.assertEqual(labels['dcon.reported_fixed'],'unknown')
        self.assertEqual(labels['dcon.reported_free'],'unstable')
        self.assertTrue(warnings)
        for extra in [' NaN',' LSODE- error',' SIGFPE']:
            with self.assertRaises(ValueError):r.extract_dcon(log+extra,{}, {},[])
    def test_template_edit_requires_exactly_one_assignment(self):
        with self.assertRaises(ValueError):r.change('nn=1\nnn=2','nn',3)
        self.assertEqual(r.change('nn=1','nn',2),'nn=2')
if __name__=='__main__':unittest.main()
