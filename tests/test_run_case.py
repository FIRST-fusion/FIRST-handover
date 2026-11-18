import importlib.util,tempfile,unittest,sys,subprocess,json,shutil
from unittest.mock import patch
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
class DirectInputChecks(unittest.TestCase):
    def test_explicit_filename_wins_over_stale_input_test(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t); edited=p/'my edited.in'
            shutil.copy2(r.ROOT/'examples/vmec_lowbeta/input.test',edited)
            (p/'input.test').write_text('STALE AND INVALID')
            request=r.resolve_request(str(edited))
            self.assertTrue(request['custom']);self.assertTrue(request['raw'])
            self.assertEqual(request['file'],edited)
            work=p/'work';work.mkdir()
            hashes=r.snapshot(p,'vmec',work,edited)
            self.assertEqual(set(hashes),{'input.test'})
            self.assertEqual((work/'input.test').read_bytes(),edited.read_bytes())
            self.assertEqual(hashes['input.test'],r.sha(edited))

    def test_directory_detection_without_descriptor(self):
        for solver,base in [('vmec','vmec_lowbeta'),('chease','chease_c50')]:
            with tempfile.TemporaryDirectory() as t:
                for f in (r.ROOT/'examples'/base).iterdir():shutil.copy2(f,Path(t)/f.name)
                request=r.resolve_request(t)
                self.assertEqual(request['solver'],solver)
                self.assertTrue(request['raw'])
                self.assertEqual(request['inputs'],Path(t))
                self.assertEqual(r.resolve_request(None,Path(t))['solver'],solver)

    def test_mixed_folder_requires_selection(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)
            shutil.copy2(r.ROOT/'examples/vmec_lowbeta/input.test',p/'input.test')
            shutil.copy2(r.ROOT/'examples/chease_c50/namelist',p/'namelist')
            with self.assertRaises(ValueError):r.resolve_request(t)
            self.assertEqual(r.resolve_request(t,solver_hint='chease')['solver'],'chease')
            with self.assertRaises(ValueError):r.resolve_request(str(p/'input.test'),solver_hint='chease')

    def test_named_templates_and_research_descriptor(self):
        self.assertFalse(r.resolve_request('vmec_lowbeta')['custom'])
        self.assertTrue(r.resolve_request('freep80_high256')['research'])
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);shutil.copy2(r.ROOT/'examples/vmec_lowbeta/input.test',p/'input.test')
            (p/'case.json').write_text(json.dumps({'template':'vmec_p80_513'}))
            self.assertTrue(r.resolve_request(t)['research'])
            (p/'case.json').write_text(json.dumps({'template':'freep80_high256'}))
            with self.assertRaises(ValueError):r.resolve_request(t)

    def test_bootstrap_file_is_forwarded_without_old_input_substitution(self):
        with tempfile.TemporaryDirectory() as t:
            f=Path(t)/'arbitrary.in';shutil.copy2(r.ROOT/'examples/vmec_lowbeta/input.test',f)
            with patch('run_bootstrap_case.main',return_value=0) as backend:
                self.assertEqual(r.main([str(f),'--bootstrap','--preflight']),0)
                cmd=backend.call_args.args[0]
                self.assertEqual(cmd[cmd.index('--input-file')+1],str(f))
                self.assertIn('--preflight',cmd)

    def test_root_entrypoint_help_and_missing_file(self):
        script=r.ROOT/'run_case.py'
        for args,expected in [(['--help'],0),(['/not/existing/input'],2)]:
            result=subprocess.run([sys.executable,str(script),*args],cwd='/',capture_output=True,text=True)
            self.assertEqual(result.returncode,expected,result.stderr)
            self.assertNotIn('Traceback',result.stderr)

if __name__=='__main__':unittest.main()
