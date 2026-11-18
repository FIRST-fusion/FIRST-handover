import importlib.util,tempfile,unittest,sys,subprocess,json,shutil,hashlib
from types import SimpleNamespace
from unittest.mock import patch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
spec=importlib.util.spec_from_file_location('run_case',Path(__file__).resolve().parents[1]/'tools/run_case.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
import run_bootstrap_case as bootstrap
import run_case as rc
DCON_LOG="Starting integration of ODE's\nq0=1.2 qmin=1.2 qa=2.0 betat=.01 betan=.1 total=-.2\nFree-boundary mode unstable\nBallooning stable\nMercier stable\nPROGRAM_STOP => Normal termination.\nIEEE_DIVIDE_BY_ZERO"
CHEASE_CONTROLS='c1fc396cb0d850ccce9c91ce12e117e1b9944e8609a9a8200d140ab2d296eeb2'
VMEC_CONTROLS='cb2312d21fe5a13450802afb702349fdfddea4e291357369d2a66636b6661889'
HIGHRES_CHEASE='/home/ouvic/linliu-reproduction-20260911/src_highres/chease_linliu.x'
HIGHRES_SHA='6c69f71a88605b9d6963a5f474316393018648a183dcfbf20c7c227eecbd221b'
CHEASE_LOG='RESIDU = 1e-12\nSOME QUANTITIES AND THEIR MKSA VALUES\nLINLIU_BETAX = 0.2\nTOTAL CURRENT = 5.5\n'
INTERFACE=b'equilibrium-interface-v1'

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
    def test_run_dcon_keeps_classic_controls_and_rejects_nonfinite_output(self):
        cfg={'binaries':{'dcon':'/opt/dcon'},'images':{'dcon':'sha256:dcon'}}
        with tempfile.TemporaryDirectory() as t:
            run=Path(t);eq=run/'equilibrium';eq.mkdir();interface=eq/'INP1';interface.write_bytes(b'iface')
            (eq/'linliu_profiles.dat').write_text('finite\n')
            summary={'metrics':{},'labels':{},'warnings':[],'stages':[]}
            with patch.object(r,'container',return_value=DCON_LOG) as container:
                r.run_dcon('chease',cfg,run,interface,summary)
            self.assertEqual(container.call_args.args[3],'exec timeout 300 /opt/solver')
            controls=(run/'dcon'/'dcon.in').read_text()
            self.assertRegex(controls,r'(?m)^\s*nn=1\s*$')
            for token in ['tol_nr=1e-8','tol_r=1e-8','singfac_min=1e-3','ucrit=10']:
                self.assertIn(token,controls)
            equil=(run/'dcon'/'equil.in').read_text()
            self.assertIn('eq_type="chease"',equil)
            self.assertIn('eq_filename="/work/INP1"',equil)
            self.assertIn('out_eq_1d=t',equil)
            self.assertEqual(summary['labels']['controls.sha256'],CHEASE_CONTROLS)
            self.assertEqual(summary['dcon']['controls_sha256'],CHEASE_CONTROLS)
            self.assertEqual(summary['dcon']['source_interface_sha256'],summary['dcon']['copied_interface_sha256'])
            self.assertEqual((run/'dcon'/'INP1').read_bytes(),b'iface')
            self.assertTrue(summary['dcon']['completed'])
            self.assertEqual(summary['dcon']['reported_free'],'unstable')
            self.assertTrue(summary['warnings'])
            self.assertNotIn('valid',summary)
        with tempfile.TemporaryDirectory() as t:
            run=Path(t);eq=run/'equilibrium';eq.mkdir();interface=eq/'INP1';interface.write_bytes(b'iface')
            summary={'metrics':{},'labels':{},'warnings':[],'stages':[]}
            with patch.object(r,'container',return_value=DCON_LOG.replace('Free-boundary mode unstable\n','')):
                with self.assertRaises(ValueError):r.run_dcon('chease',cfg,run,interface,summary)
            self.assertFalse(summary['dcon']['completed'])
            self.assertIsNone(summary['dcon']['reported_free'])
        with tempfile.TemporaryDirectory() as t:
            run=Path(t);eq=run/'equilibrium';eq.mkdir();interface=eq/'INP1';interface.write_bytes(b'iface')
            summary={'metrics':{},'labels':{},'warnings':[],'stages':[]}
            def nonfinite(stage,cfg,work,script,out):
                Path(work,'dcon.out').write_text('NaN\n');return DCON_LOG
            with patch.object(r,'container',side_effect=nonfinite):
                with self.assertRaisesRegex(ValueError,'Nonfinite'):r.run_dcon('chease',cfg,run,interface,summary)
            self.assertFalse(summary['dcon']['completed'])
            self.assertIsNone(summary['dcon']['reported_free'])
            self.assertNotIn('controls.sha256',summary['labels'])
            self.assertEqual(summary['dcon']['controls_sha256'],CHEASE_CONTROLS)
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
                self.assertNotIn('--dcon',cmd)
    def test_dcon_is_forwarded_for_custom_bootstrap_and_research_case(self):
        with tempfile.TemporaryDirectory() as t:
            f=Path(t)/'arbitrary.in';shutil.copy2(r.ROOT/'examples/vmec_lowbeta/input.test',f)
            with patch('run_bootstrap_case.main',return_value=0) as backend:
                self.assertEqual(r.main([str(f),'--bootstrap','--dcon','--preflight','--timeout','120']),0)
                cmd=backend.call_args.args[0]
                self.assertEqual(cmd[0],'vmec_p80_513')
                self.assertEqual(cmd[cmd.index('--input-file')+1],str(f))
                self.assertIn('--dcon',cmd);self.assertIn('--preflight',cmd)
                self.assertEqual(cmd[cmd.index('--timeout')+1],'120')
            with patch('run_bootstrap_case.main',return_value=0) as backend:
                self.assertEqual(r.main(['freep80_high256','--dcon','--preflight']),0)
                cmd=backend.call_args.args[0]
                self.assertEqual(cmd[0],'freep80_high256')
                self.assertIn('--dcon',cmd)
                self.assertNotIn('--input-file',cmd)
    def test_named_tutorial_bootstrap_stays_rejected_when_dcon_is_set(self):
        with patch('run_bootstrap_case.main') as backend:
            with self.assertRaises(SystemExit) as caught:
                r.main(['vmec_lowbeta','--bootstrap','--dcon'])
        self.assertEqual(caught.exception.code,2)
        backend.assert_not_called()
    def test_tutorial_dcon_flag_stays_on_tutorial_preflight(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)
            for item in (r.ROOT/'examples/chease_c50').iterdir():
                if item.is_file():shutil.copy2(item,p/item.name)
            with patch.object(r,'preflight') as preflight,patch.object(r,'check_plot_python'),patch('run_bootstrap_case.main') as backend:
                self.assertEqual(r.main([str(p),'--dcon','--preflight']),0)
            backend.assert_not_called()
            cfg=preflight.call_args.args[0]
            self.assertEqual(cfg['binaries']['chease'],HIGHRES_CHEASE)
            self.assertIn('dcon',cfg['binaries']);self.assertIn('dcon',cfg['images'])

    def test_root_entrypoint_help_and_missing_file(self):
        script=r.ROOT/'run_case.py'
        for args,expected in [(['--help'],0),(['/not/existing/input'],2)]:
            result=subprocess.run([sys.executable,str(script),*args],cwd='/',capture_output=True,text=True)
            self.assertEqual(result.returncode,expected,result.stderr)
            self.assertNotIn('Traceback',result.stderr)
            if args==['--help']:self.assertIn('--dcon',result.stdout)

class TutorialDconChecks(unittest.TestCase):
    def test_tutorial_runs_shared_dcon_once_with_or_without_flag(self):
        vmec_log='EXECUTION TERMINATED NORMALLY\n 200 1e-14 1e-15 1e-16 1.5 0.7 0.01\n'
        for extra in ([],['--dcon']):
            with self.subTest(extra=extra):
                calls=[]
                def fake_container(stage,cfg,work,script,out):
                    calls.append((stage,script))
                    out.append({'stage':stage});work=Path(work)
                    if stage=='vmec':
                        (work/'dcon_test.txt').write_bytes(b'same-interface');(work/'wout_test.nc').write_bytes(b'NC')
                        return vmec_log
                    if stage=='dcon':
                        (work/'dcon.out').write_text('finite\n');return DCON_LOG
                    raise AssertionError(stage)
                with tempfile.TemporaryDirectory() as t:
                    out=Path(t)/'out'
                    with patch.object(r,'preflight'),patch.object(r,'check_plot_python'),patch.object(r,'make_profiles',return_value={'complete':True}),patch.object(r,'container',side_effect=fake_container):
                        code=r.main(['vmec_lowbeta','--output',str(out),*extra])
                    summary=json.loads((out/'summary.json').read_text())
                    self.assertEqual(code,0,summary.get('error'))
                    self.assertEqual([item[0] for item in calls],['vmec','dcon'])
                    self.assertEqual(calls[0][1],'exec timeout 300 /opt/solver input.test')
                    self.assertEqual(calls[1][1],'exec timeout 300 /opt/solver')
                    self.assertEqual((out/'equilibrium'/'dcon_test.txt').read_bytes(),(out/'dcon'/'dcon_test.txt').read_bytes())
                    self.assertEqual(summary['dcon']['source_interface_sha256'],summary['dcon']['copied_interface_sha256'])
                    self.assertEqual(summary['labels']['controls.sha256'],VMEC_CONTROLS)
                    self.assertEqual(list(summary['labels'])[-3:],['input.sha256','runtime.sha256','controls.sha256'])
                    self.assertTrue(summary['dcon']['completed'])
                    self.assertEqual(summary['dcon']['reported_free'],'unstable')
                    self.assertTrue(summary['valid']);self.assertTrue(summary['workflow_complete'])
                    self.assertEqual(summary['scientific_acceptance'],'NOT_CERTIFIED: workflow regression only')
    def test_tutorial_dcon_failure_keeps_profiles_and_fails_workflow(self):
        vmec_log='EXECUTION TERMINATED NORMALLY\n 200 1e-14 1e-15 1e-16 1.5 0.7 0.01\n'
        calls=[]
        def fake_container(stage,cfg,work,script,out):
            calls.append(stage);out.append({'stage':stage});work=Path(work)
            if stage=='vmec':
                (work/'dcon_test.txt').write_bytes(b'same-interface');(work/'wout_test.nc').write_bytes(b'NC')
                return vmec_log
            raise RuntimeError('dcon failed')
        with tempfile.TemporaryDirectory() as t:
            out=Path(t)/'out'
            with patch.object(r,'preflight'),patch.object(r,'check_plot_python'),patch.object(r,'make_profiles',return_value={'complete':True}),patch.object(r,'container',side_effect=fake_container):
                code=r.main(['vmec_lowbeta','--output',str(out)])
            summary=json.loads((out/'summary.json').read_text())
            self.assertEqual(code,1)
            self.assertEqual(calls,['vmec','dcon'])
            self.assertEqual(summary['profiles'],{'complete':True})
            self.assertFalse(summary['valid']);self.assertFalse(summary['workflow_complete'])
            self.assertFalse(summary['dcon']['completed'])
class BootstrapDconChecks(unittest.TestCase):
    def _sha(self):
        from audit_bootstrap import SOURCE_HASH
        real=bootstrap.sha
        def sha(path):
            name=Path(path).name
            if name in ('campaign.py','vmec_bootstrap.py'):
                return SOURCE_HASH['chease' if name=='campaign.py' else 'vmec'][1]
            return real(path)
        return sha
    def _preflight(self,argv):
        with patch.object(bootstrap,'preflight') as preflight,patch.object(bootstrap,'check_plot_python'),patch.object(bootstrap,'sha',side_effect=self._sha()),patch.object(bootstrap,'subprocess') as process:
            process.run.return_value=SimpleNamespace(returncode=0)
            self.assertEqual(bootstrap.main(argv),0)
        self.assertTrue(preflight.called)
        return preflight.call_args.args[0]
    def test_combined_preflight_adds_dcon_without_dropping_highres_chease(self):
        base=json.loads((bootstrap.ROOT/'runtime/first.json').read_text())
        cfg=self._preflight(['freep80_high256','--dcon','--preflight'])
        self.assertEqual(set(cfg['binaries']),{'chease','dcon'})
        self.assertEqual(set(cfg['images']),{'chease','dcon'})
        self.assertEqual(set(cfg['binary_sha256']),{'chease','dcon'})
        self.assertEqual(cfg['binaries']['chease'],HIGHRES_CHEASE)
        self.assertEqual(cfg['binary_sha256']['chease'],HIGHRES_SHA)
        self.assertNotEqual(cfg['binaries']['chease'],base['binaries']['chease'])
        self.assertEqual(cfg['binaries']['dcon'],base['binaries']['dcon'])
        self.assertEqual(cfg['images']['dcon'],base['images']['dcon'])
        self.assertEqual(cfg['binary_sha256']['dcon'],base['binary_sha256']['dcon'])
        vmec=self._preflight(['vmec_p80_513','--dcon','--preflight'])
        self.assertEqual(set(vmec['binaries']),{'vmec','dcon'})
        self.assertEqual(vmec['binaries']['vmec'],base['binaries']['vmec'])
        self.assertEqual(vmec['images']['dcon'],base['images']['dcon'])
    def test_bootstrap_only_preflight_does_not_require_dcon(self):
        cfg=self._preflight(['freep80_high256','--preflight'])
        self.assertEqual(set(cfg['binaries']),{'chease'})
        self.assertEqual(set(cfg['images']),{'chease'})
        self.assertNotIn('dcon',cfg['binary_sha256'])
        self.assertEqual(cfg['binaries']['chease'],HIGHRES_CHEASE)
        self.assertEqual(cfg['binary_sha256']['chease'],HIGHRES_SHA)
    def _run(self,argv,audit='ok',dcon='ok'):
        calls=[];audits=[]
        def fake_container(stage,cfg,work,script,out):
            work=Path(work);calls.append({'stage':stage,'work':work,'script':script,'cfg':cfg});out.append({'stage':stage})
            if stage=='chease':
                (work/'INP1').write_bytes(INTERFACE)
                (work/'threed1.test').write_text('finite\n');(work/'linliu_profiles.dat').write_text('finite\n')
                return CHEASE_LOG
            if stage=='dcon':
                if dcon=='raise':raise RuntimeError('dcon failed; see log')
                (work/'dcon.out').write_text('NaN\n' if dcon=='nonfinite' else 'finite\n')
                return DCON_LOG
            raise AssertionError(stage)
        def fake_run(cmd,check=False,**kwargs):
            cmd=[str(part) for part in cmd]
            if len(cmd)>1 and cmd[1]=='-c':return SimpleNamespace(returncode=0)
            if any(part.endswith('audit_bootstrap.py') for part in cmd):
                audits.append(cmd)
                if audit=='fail':raise subprocess.CalledProcessError(1,cmd)
                Path(cmd[3],'bootstrap.json').write_text(json.dumps({'fbs_total_hirshman':0.25,'fbs_percent':25.0})+'\n')
                return SimpleNamespace(returncode=0)
            raise AssertionError(cmd)
        def fake_profiles(solver,output,label,python):
            marker=Path(output)/'profiles'/'overview.png';marker.parent.mkdir(parents=True);marker.write_bytes(b'png')
            return {'complete':True,'directory':str(marker.parent)}
        with patch.object(bootstrap,'preflight'),patch.object(bootstrap,'check_plot_python'),patch.object(bootstrap,'sha',side_effect=self._sha()),patch.object(bootstrap,'subprocess') as process,patch.object(bootstrap,'make_profiles',side_effect=fake_profiles),patch.object(bootstrap,'container',side_effect=fake_container),patch.object(rc,'container',side_effect=fake_container):
            process.run.side_effect=fake_run
            code=bootstrap.main(argv)
        out=Path(argv[argv.index('--output')+1])
        return code,json.loads((out/'summary.json').read_text()),calls,audits,out
    def test_named_and_custom_cases_use_one_equilibrium_and_the_same_interface(self):
        with tempfile.TemporaryDirectory() as t:
            out=Path(t)/'out'
            code,summary,calls,audits,_=self._run(['freep80_high256','--dcon','--output',str(out)])
            self.assertEqual(code,0,summary.get('error'))
            self._assert_one_interface(summary,calls,audits,out)
            self.assertFalse(summary['custom_input'])
            self.assertEqual(summary['fbs_total_hirshman'],0.25)
        with tempfile.TemporaryDirectory() as t:
            copied=Path(t)/'inputs';copied.mkdir()
            for item in (bootstrap.ROOT/'research-inputs/bootstrap99/cases/freep80_high256/inputs').iterdir():
                if item.is_file():shutil.copy2(item,copied/item.name)
            out=Path(t)/'out'
            code,summary,calls,audits,_=self._run(['freep80_high256','--dcon','--input-dir',str(copied),'--input-file',str(copied/'namelist'),'--output',str(out)])
            self.assertEqual(code,0,summary.get('error'))
            self._assert_one_interface(summary,calls,audits,out)
            self.assertTrue(summary['custom_input']);self.assertIsNone(summary['historical_fbs'])
    def _assert_one_interface(self,summary,calls,audits,out):
        self.assertEqual([item['stage'] for item in calls],['chease','dcon'])
        self.assertEqual(len(audits),1)
        self.assertIn('timeout -k 30 3600',calls[0]['script'])
        self.assertEqual(calls[1]['script'],'exec timeout 300 /opt/solver')
        self.assertEqual(calls[0]['cfg']['binaries']['chease'],HIGHRES_CHEASE)
        self.assertIn('dcon',calls[0]['cfg']['binaries'])
        eq,dc=out/'equilibrium'/'INP1',out/'dcon'/'INP1'
        self.assertEqual(eq.read_bytes(),INTERFACE);self.assertEqual(dc.read_bytes(),INTERFACE)
        self.assertEqual(Path(summary['dcon']['source_interface']).resolve(),eq.resolve())
        self.assertEqual(summary['dcon']['source_interface_sha256'],summary['dcon']['copied_interface_sha256'])
        self.assertEqual(summary['dcon']['source_interface_sha256'],hashlib.sha256(INTERFACE).hexdigest())
        self.assertEqual(summary['dcon']['controls_sha256'],CHEASE_CONTROLS)
        self.assertEqual(summary['labels']['controls.sha256'],CHEASE_CONTROLS)
        self.assertRegex((out/'dcon'/'dcon.in').read_text(),r'(?m)^\s*nn=1\s*$')
        self.assertTrue(summary['dcon']['completed'])
        self.assertEqual(summary['dcon']['reported_free'],'unstable')
        self.assertEqual(summary['labels']['dcon.reported_free'],'unstable')
        self.assertTrue(summary['valid']);self.assertTrue(summary['workflow_complete'])
        self.assertTrue(summary['bootstrap_audit']['completed'])
        self.assertTrue(summary['scientific_acceptance'].startswith('NOT_CERTIFIED'))
        self.assertNotIn('DCON not run',summary['scientific_acceptance'])
        self.assertTrue((out/'equilibrium'/'bootstrap.json').is_file())
        self.assertTrue((out/'profiles'/'overview.png').is_file())
    def test_bootstrap_only_does_not_run_dcon(self):
        with tempfile.TemporaryDirectory() as t:
            out=Path(t)/'out'
            code,summary,calls,audits,_=self._run(['freep80_high256','--output',str(out)])
            self.assertEqual(code,0,summary.get('error'))
            self.assertEqual([item['stage'] for item in calls],['chease'])
            self.assertEqual(len(audits),1)
            self.assertFalse((out/'dcon').exists())
            self.assertFalse(summary['dcon']['requested']);self.assertFalse(summary['dcon']['completed'])
            self.assertNotIn('dcon',calls[0]['cfg']['binaries'])
            self.assertEqual(calls[0]['cfg']['binaries']['chease'],HIGHRES_CHEASE)
            self.assertIn('DCON not run',summary['scientific_acceptance'])
            self.assertEqual(summary['fbs_total_hirshman'],0.25)
            self.assertTrue(summary['valid']);self.assertTrue(summary['workflow_complete'])
    def test_dcon_failure_preserves_bootstrap_and_profiles(self):
        with tempfile.TemporaryDirectory() as t:
            out=Path(t)/'out'
            code,summary,calls,audits,_=self._run(['freep80_high256','--dcon','--output',str(out)],dcon='raise')
            self.assertEqual(code,1)
            self.assertEqual([item['stage'] for item in calls],['chease','dcon'])
            self.assertEqual(len(audits),1)
            self.assertEqual(summary['fbs_total_hirshman'],0.25)
            self.assertEqual(summary['fbs_percent'],25.0)
            self.assertTrue(summary['bootstrap_audit']['completed'])
            self.assertFalse(summary['dcon']['completed'])
            self.assertTrue((out/'equilibrium'/'bootstrap.json').is_file())
            self.assertTrue((out/'profiles'/'overview.png').is_file())
            self.assertTrue(summary['profiles']['complete'])
            self.assertIn('dcon:',summary['error']);self.assertNotIn('bootstrap:',summary['error'])
            self.assertFalse(summary['valid']);self.assertFalse(summary['workflow_complete'])
    def test_bootstrap_failure_still_runs_dcon_and_fails_overall(self):
        with tempfile.TemporaryDirectory() as t:
            out=Path(t)/'out'
            code,summary,calls,audits,_=self._run(['freep80_high256','--dcon','--output',str(out)],audit='fail')
            self.assertEqual(code,1)
            self.assertEqual([item['stage'] for item in calls],['chease','dcon'])
            self.assertEqual(len(audits),1)
            self.assertFalse(summary['bootstrap_audit']['completed'])
            self.assertTrue(summary['dcon']['completed'])
            self.assertEqual(summary['dcon']['reported_free'],'unstable')
            self.assertEqual((out/'equilibrium'/'INP1').read_bytes(),(out/'dcon'/'INP1').read_bytes())
            self.assertNotIn('fbs_total_hirshman',summary)
            self.assertIn('bootstrap:',summary['error']);self.assertNotIn('dcon:',summary['error'])
            self.assertFalse(summary['valid']);self.assertFalse(summary['workflow_complete'])
            self.assertTrue(summary['scientific_acceptance'].startswith('NOT_CERTIFIED'))
    def test_nonfinite_dcon_output_is_rejected_without_losing_fbs(self):
        with tempfile.TemporaryDirectory() as t:
            out=Path(t)/'out'
            code,summary,calls,_,_=self._run(['freep80_high256','--dcon','--output',str(out)],dcon='nonfinite')
            self.assertEqual(code,1)
            self.assertEqual([item['stage'] for item in calls],['chease','dcon'])
            self.assertIn('Nonfinite',summary['dcon']['error'])
            self.assertFalse(summary['dcon']['completed']);self.assertIsNone(summary['dcon']['reported_free'])
            self.assertNotIn('controls.sha256',summary['labels'])
            self.assertEqual(summary['fbs_total_hirshman'],0.25)
            self.assertTrue((out/'equilibrium'/'bootstrap.json').is_file())
            self.assertTrue((out/'profiles'/'overview.png').is_file())
            self.assertFalse(summary['valid']);self.assertFalse(summary['workflow_complete'])
if __name__=='__main__':unittest.main()
