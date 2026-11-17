#!/usr/bin/env python3
"""FIRST-only isolated container reproduction. Never modifies source inputs or binaries."""
import argparse, datetime, hashlib, json, math, os, re, shutil, subprocess, sys, time
from pathlib import Path
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

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('case',nargs='?',choices=['chease_c50','chease_c51','vmec_smooth','vmec_lowbeta'])
    ap.add_argument('--output',type=Path)
    ap.add_argument('--preflight',action='store_true')
    args=ap.parse_args();cfg=json.loads((ROOT/'runtime/first.json').read_text())
    preflight(cfg)
    if args.preflight:print('FIRST images and solver binary hashes verified');return 0
    if not args.case:ap.error('case required')
    run=(args.output or ROOT/'runs'/(args.case+'-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))).resolve()
    run.mkdir(parents=True,exist_ok=False)
    summary={'case':args.case,'valid':False,'metrics':{},'labels':{},'warnings':[],
             'scientific_acceptance':'NOT_CERTIFIED: workflow regression only','stages':[],
             'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        case=cfg['cases'][args.case];solver=case['solver']
        eq=run/'equilibrium';eq.mkdir()
        inputs=ROOT/'examples'/args.case
        summary['input_sha256']={p.name:sha(p) for p in inputs.iterdir() if p.is_file()}
        for p in inputs.iterdir():
            if p.is_file():shutil.copy2(p,eq/p.name)
        script='exec timeout 300 /opt/solver < namelist' if solver=='chease' else 'exec timeout 300 /opt/solver input.test'
        text=container(solver,cfg,eq,script,summary['stages'])
        interface=extract_equilibrium(solver,text,eq,case['residual_limit'],summary['metrics'],summary['labels'])
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
    print(json.dumps({'output':str(run),'valid':summary['valid'],'error':summary.get('error'),'warnings':summary['warnings']},indent=2))
    return 0 if summary['valid'] else 1
if __name__=='__main__':sys.exit(main())
