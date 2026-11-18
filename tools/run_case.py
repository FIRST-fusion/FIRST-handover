#!/usr/bin/env python3
"""直接執行 input：python3 run_case.py 檔案或資料夾；也接受原始範例名稱。"""
import argparse, datetime, hashlib, json, math, os, re, shutil, subprocess, sys, time
from pathlib import Path
from profile_output import DEFAULT_PYTHON, check_plot_python, make_profiles
from editable_inputs import input_files, snapshot, convergence_limit, identify_input
ROOT = Path(__file__).resolve().parents[1]
NUMBER = r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[EeDd][+-]?\d+)?'
BAD = re.compile(r'(?i)(?<![A-Za-z_])(?:NaN|Infinity|Inf)(?![A-Za-z_])|segmentation fault|SIGFPE|ZERO PIVOT')

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def change(text, key, value):
    text,n=re.subn(r'(?mi)^(\s*'+re.escape(key)+r'\s*=).*$',lambda m:m[1]+str(value),text)
    if n!=1: raise ValueError('Expected one assignment for '+key)
    return text

def number(text, pattern):
    m=re.search(pattern,text,re.I)
    if not m: raise ValueError('Missing metric: '+pattern)
    value=float(m[1].replace('D','E').replace('d','e'))
    if not math.isfinite(value):raise ValueError('Nonfinite metric')
    return value

def preflight(cfg):
    if sys.platform!='linux':raise RuntimeError('Run on FIRST Linux, not macOS')
    if subprocess.check_output(['hostname'],text=True).strip()!='ncku-first':
        raise RuntimeError('Licensed FIRST runtime is restricted to ncku-first')
    for key,path in cfg['binaries'].items():
        if sha(path)!=cfg['binary_sha256'][key]:raise RuntimeError('Binary SHA mismatch: '+key)
    for image in set(cfg['images'].values()):
        actual=subprocess.check_output(['docker','image','inspect','--format','{{.Id}}',image],text=True).strip()
        if actual!=image:raise RuntimeError('Image mismatch')

def container(stage,cfg,work,script,out):
    name='first-handover-'+stage+'-'+datetime.datetime.now().strftime('%Y%m%d%H%M%S')+'-'+str(os.getpid())
    cmd=['docker','run','--name',name,'--label','org.first.handover=true','--network','none','--read-only',
         '--cap-drop','ALL','--security-opt','no-new-privileges','--cpus','2','--memory','8g','--pids-limit','256',
         '--user',str(os.getuid())+':'+str(os.getgid()),'--tmpfs','/tmp:rw,nosuid,size=256m',
         '-e','OMP_NUM_THREADS=1','-e','OPENBLAS_NUM_THREADS=1','-e','HOME=/tmp',
         '--mount','type=bind,src='+str(work)+',dst=/work',
         '--mount','type=bind,src='+cfg['binaries'][stage]+',dst=/opt/solver,readonly',
         '-w','/work','--entrypoint','/bin/bash',cfg['images'][stage],'-c',script]
    start=time.time()
    with (work/'run.log').open('w') as log:
        r=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
    row={'stage':stage,'container':name,'exit_code':r.returncode,'seconds':time.time()-start,'command':cmd}
    out.append(row)
    if r.returncode:raise RuntimeError(stage+' failed; see '+str(work/'run.log'))
    return (work/'run.log').read_text(errors='replace')

def extract_equilibrium(solver,text,work,limit,metrics,labels):
    if BAD.search(text):raise ValueError('Nonfinite or fatal equilibrium log')
    if solver=='chease':
        residuals=re.findall(r'RESIDU\s*=\s*('+NUMBER+')',text)
        if not residuals or 'SOME QUANTITIES AND THEIR MKSA VALUES' not in text:raise ValueError('CHEASE incomplete')
        residual=float(residuals[-1].replace('D','E'))
        metrics['equilibrium.residual']=residual
        metrics['equilibrium.beta_vac']=number(text,r'LINLIU_BETAX\s*=\s*('+NUMBER+')')
        metrics['equilibrium.current_normalized']=number(text,r'TOTAL CURRENT\s*=\s*('+NUMBER+')')
        interface=work/'INP1'
    else:
        if 'EXECUTION TERMINATED NORMALLY' not in text or re.search(r'aborting|failed to converge',text,re.I):raise ValueError('VMEC incomplete')
        rows=re.findall(r'^\s*\d+\s+'+r'\s+'.join(['('+NUMBER+')']*6)+r'\s*$',text,re.M)
        if not rows:raise ValueError('VMEC final residuals absent')
        for k,v in zip(['fsqr','fsqz','fsql','raxis','delt','wmhd'],rows[-1]):metrics['equilibrium.'+k]=float(v.replace('D','E'))
        residual=max(metrics['equilibrium.'+k] for k in ['fsqr','fsqz','fsql'])
        interface=work/'dcon_test.txt'
        if not (work/'wout_test.nc').is_file():raise ValueError('VMEC wout absent')
    if residual>limit*1.001:raise ValueError('Residual exceeds configured convergence threshold')
    if not interface.is_file() or interface.stat().st_size==0:raise ValueError('Interface absent')
    labels['equilibrium.converged']=True
    return interface

def extract_dcon(text,metrics,labels,warnings):
    if BAD.search(text) or 'Normal termination.' not in text or "Starting integration of ODE's" not in text:
        raise ValueError('DCON incomplete or nonfinite')
    if re.search(r'LSODE-|DLSODE|excess work|stepsize underflow',text,re.I):raise ValueError('DCON ODE warning requires review')
    for k in ['q0','qmin','qa','betat','betan','total']:
        metrics['dcon.'+k]=number(text,r'\b'+k+r'\s*=\s*('+NUMBER+')')
    for k,unstable,stable in [
        ('fixed','Fixed-boundary mode unstable','Fixed-boundary mode stable'),
        ('free','Free-boundary mode unstable','All free-boundary modes stable'),
        ('ballooning','Ballooning unstable','Ballooning stable'),
        ('mercier','Mercier unstable','Mercier stable')]:
        labels['dcon.reported_'+k]='unstable' if unstable in text else 'stable' if stable in text else 'unknown'
    # These are solver-reported classifications, not a resolution-converged physics certificate.
    flags=sorted(set(re.findall(r'IEEE_[A-Z_]+',text)))
    labels['dcon.floating_point_flags']=','.join(flags) if flags else 'none'
    if flags:warnings.append('DCON floating-point flags: '+','.join(flags)+'; diagnostic classification is not scientifically certified')
    if labels['dcon.reported_free']=='unknown':raise ValueError('Missing DCON free boundary result')

def resolve_request(target, override=None, solver_hint=None):
    cfg=json.loads((ROOT/'runtime/first.json').read_text())
    research={row['case']:row for row in json.loads((ROOT/'research-inputs/bootstrap99/manifest.json').read_text())['cases']}
    known={**cfg['cases'],**research}
    template=target if target in known and not Path(target).exists() else None
    if override is not None and target is not None and template is None:
        raise ValueError('請指定一個 input 路徑；不要同時給位置參數路徑和 --input/--input-dir')
    if template is not None and override is None:
        solver=known[template]['solver']
        if solver_hint and solver_hint!=solver:raise ValueError('--solver 與範例不符')
        directory=ROOT/'research-inputs/bootstrap99/cases'/template/'inputs' if template in research else ROOT/'examples'/template
        return {'case':template,'solver':solver,'inputs':directory,'file':directory/('input.test' if solver=='vmec' else 'namelist'),'custom':False,'research':template in research,'raw':False}
    path=Path(override if override is not None else target or '.')
    if not path.exists() and len(path.parts)==1 and (ROOT/'inputs'/path).is_dir():path=ROOT/'inputs'/path
    hint=known[template]['solver'] if template else solver_hint
    directory,source,solver=identify_input(path,hint)
    if solver_hint and solver_hint!=solver:raise ValueError('--solver 與 input 不符')
    descriptor=directory/'case.json'
    if template is None and descriptor.exists():
        template=json.loads(descriptor.read_text())['template']
        if template not in known or known[template]['solver']!=solver:
            raise ValueError('case.json 的 template 與 input 不符；請修正或明確指定原範例名及 --input')
    return {'case':template or ('vmec_lowbeta' if solver=='vmec' else 'chease_c50'),'solver':solver,
            'inputs':directory,'file':source,'custom':True,'research':template in research,'raw':template is None}


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('case',nargs='?',help='input檔案、資料夾或範例名稱；省略則讀取目前資料夾')
    ap.add_argument('--output',type=Path)
    source_group=ap.add_mutually_exclusive_group()
    source_group.add_argument('--input-dir',type=Path,help='相容舊指令：指定自訂input資料夾，不需範例名')
    source_group.add_argument('--input',type=Path,help='指定input檔案或資料夾，也可直接放在位置參數')
    ap.add_argument('--solver',choices=['chease','vmec'],help='資料夾同時有兩種input時指定solver')
    ap.add_argument('--bootstrap',action='store_true',help='自訂input改跑平衡、五圖與fBS，不跑DCON')
    ap.add_argument('--timeout',type=int)
    ap.add_argument('--preflight',action='store_true')
    ap.add_argument('--plot-python',default=DEFAULT_PYTHON,help='Python with numpy/scipy/matplotlib for automatic profiles')
    args=ap.parse_args(argv);cfg=json.loads((ROOT/'runtime/first.json').read_text())
    if args.timeout is not None and not 1 <= args.timeout <= 14400:ap.error('timeout must be 1..14400 seconds')
    override=args.input if args.input is not None else args.input_dir
    if args.preflight and args.case is None and override is None and not any(Path(n).is_file() for n in ('input.test','namelist')):
        preflight(cfg);check_plot_python(args.plot_python)
        print('FIRST images, solver binary hashes and plotting dependencies verified');return 0
    try:
        request=resolve_request(args.case,override,args.solver)
        if args.bootstrap and not request['research']:
            if not request['custom']:
                raise ValueError('--bootstrap 請搭配自己的input路徑，或直接指定研究範例名稱')
            request['research']=True
            request['case']='vmec_p80_513' if request['solver']=='vmec' else 'freep80_high256'
        inputs=request['inputs'];solver=request['solver'];main_file=request['file']
        input_files(inputs,solver,main_file)
        if request['custom']:convergence_limit(inputs,solver,main_file)
    except (ValueError,KeyError,OSError) as exc:
        ap.error(str(exc))
    print('Input: '+str(main_file)+' | solver='+solver+' | workflow='+('bootstrap + profiles (no DCON)' if request['research'] else 'profiles + DCON'),flush=True)
    if request['research']:
        from run_bootstrap_case import main as bootstrap_main
        command=[request['case'],'--plot-python',args.plot_python]
        if request['custom']:command+=['--input-dir',str(inputs),'--input-file',str(main_file)]
        if args.output:command+=['--output',str(args.output)]
        if args.timeout is not None:command+=['--timeout',str(args.timeout)]
        if args.preflight:command+=['--preflight']
        return bootstrap_main(command)
    # Raw CHEASE inputs use the existing larger-capacity build, including restart reads.
    if request['raw'] and solver=='chease':
        cfg['binaries']['chease']='/home/ouvic/linliu-reproduction-20260911/src_highres/chease_linliu.x'
        cfg['binary_sha256']['chease']='6c69f71a88605b9d6963a5f474316393018648a183dcfbf20c7c227eecbd221b'
    preflight(cfg);check_plot_python(args.plot_python)
    if args.preflight:print('FIRST runtime, input and plotting dependencies verified');return 0
    args.timeout=args.timeout or 300
    label=inputs.name if request['custom'] else request['case']
    run=(args.output or ROOT/'runs'/(label+'-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'))).resolve()
    run.mkdir(parents=True,exist_ok=False)
    summary={'case':request['case'],'valid':False,'metrics':{},'labels':{},'warnings':[],
             'scientific_acceptance':'NOT_CERTIFIED: workflow regression only','stages':[],
             'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        case=cfg['cases'][request['case']]
        eq=run/'equilibrium';eq.mkdir()
        summary['input_sha256']=snapshot(inputs,solver,eq,main_file)
        summary['input_directory']=str(inputs)
        summary['input_file']=str(main_file)
        summary['custom_input']=request['custom']
        summary['reference_comparison_applicable']=not request['custom']
        limit=convergence_limit(eq,solver) if request['custom'] else case['residual_limit']
        summary['convergence_limit']=limit
        script='exec timeout '+str(args.timeout)+' /opt/solver '+('< namelist' if solver=='chease' else 'input.test')
        text=container(solver,cfg,eq,script,summary['stages'])
        interface=extract_equilibrium(solver,text,eq,limit,summary['metrics'],summary['labels'])
        # Keep valid equilibrium profiles even if subsequent DCON diagnostics fail.
        summary['profiles']=make_profiles(solver,run,label,args.plot_python)
        dc=run/'dcon';dc.mkdir();shutil.copy2(interface,dc/interface.name)
        equil=(ROOT/'runtime/equil.in').read_text()
        for key,value in [('eq_type','"'+solver+'"'),('eq_filename','"/work/'+interface.name+'"'),('out_eq_1d','t')]:equil=change(equil,key,value)
        (dc/'equil.in').write_text(equil)
        dcon=(ROOT/'runtime/dcon.in').read_text()
        for key,value in [('nn',1),('tol_nr','1e-8'),('tol_r','1e-8'),('singfac_min','1e-3'),('ucrit',10)]:dcon=change(dcon,key,value)
        (dc/'dcon.in').write_text(dcon)
        vac=(ROOT/'runtime/vac.in').read_text()
        # ishape=6 is the installed conformal-wall option; a=0.2 retained explicitly.
        (dc/'vac.in').write_text(vac)
        text=container('dcon',cfg,dc,'exec timeout 300 /opt/solver',summary['stages'])
        extract_dcon(text,summary['metrics'],summary['labels'],summary['warnings'])
        for artifact in [eq/'threed1.test', eq/'linliu_profiles.dat', dc/'dcon.out', dc/'equil_1d.out']:
            if artifact.is_file() and BAD.search(artifact.read_text(errors='replace')):
                raise ValueError('Nonfinite/fatal token in '+artifact.name)
        summary['labels']['input.sha256']=hashlib.sha256(json.dumps(summary['input_sha256'],sort_keys=True).encode()).hexdigest()
        summary['labels']['runtime.sha256']=hashlib.sha256(json.dumps(cfg,sort_keys=True).encode()).hexdigest()
        summary['labels']['controls.sha256']=hashlib.sha256(b''.join((dc/n).read_bytes() for n in ['equil.in','dcon.in','vac.in'])).hexdigest()
        summary['workflow_complete']=True
        summary['valid']=True
    except Exception as exc:
        summary['error']=str(exc)
    summary['runtime']=cfg
    summary['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    (run/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'output':str(run),'valid':summary['valid'],'profiles':summary.get('profiles'), 'error':summary.get('error'),'warnings':summary['warnings']},indent=2))
    return 0 if summary['valid'] else 1
if __name__=='__main__':sys.exit(main())
