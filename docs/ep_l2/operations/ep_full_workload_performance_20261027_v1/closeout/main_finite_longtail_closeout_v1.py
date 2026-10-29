"""Main-only finite completion publisher for already-consumed EP attempts.

No simulator launch, native controller restart, budget or registry mutation.
The original dispatcher/postprocessor retain their existing responsibilities.
"""
import argparse
import collections
import csv
import datetime as dt
import fcntl
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time
import traceback
import uuid

J = Path('/root/data/ep_l2_full_workload_performance_20261027_v1')
CONTROL = J/'control/finite_longtail_closeout_20261029_v1'
CONFIG = CONTROL/'CONFIG.json'
TERMINAL = {'CLOSED_ACCEPTED', 'CLOSED_UNACCEPTED', 'PARSE_HOLD'}
LIVE = J/'analysis/live'
BASE = None
CFG = None
BASE_CAPTURE = None


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def ref(path):
    p=Path(path);b=p.read_bytes()
    return {'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}


def exact(r):
    p=Path(r['path']);b=p.read_bytes()
    if hashlib.sha256(b).hexdigest()!=r['sha256']:
        raise ValueError('Pinned code/evidence drift: '+str(p))
    return b


def put(path,value):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    t=p.with_name('.'+p.name+'.'+str(uuid.uuid4())+'.tmp')
    with t.open('xb') as f:
        f.write((json.dumps(value,sort_keys=True,indent=2)+'\n').encode())
        f.flush();os.fsync(f.fileno())
    os.replace(t,p)


def process_alive(pid,start):
    try:
        fields=(Path('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split()
        return int(fields[19])==start and fields[0] not in ('Z','X')
    except (FileNotFoundError,ProcessLookupError):
        return False


def scoped_request():
    registry,_=BASE.authority()
    q=registry['registered_future_requests'][BASE.GOAL]
    if digest(q['admitted_specs'])!=CFG['admitted_specs_digest']:
        raise ValueError('Frozen227 admission changed; do not absorb a new stage')
    if q['remaining']!=0 or set(q['consumed'])!=set(q['admitted_specs']):
        raise ValueError('Only the already-consumed frozen population is permitted')
    for c in CFG['longtail']:
        if q['admitted_specs'].get(c['cohort'])!=c['spec_ref']['sha256']:
            raise ValueError('Longtail exact spec mismatch')
    return q


def state_fingerprint(q):
    return digest({c:{'state':r.get('state'),'point':r.get('accepted_point_ref'),
                      'done':r.get('done_ref'),'archive':r.get('archive_receipt_ref')}
                   for c,r in sorted(q['consumed'].items())})


def analysis_matches(q):
    p=J/'agent_b/results_analysis_20261028_v1/CURRENT.json'
    x=read(p)
    r=next(a for a in x['files'] if a['publish_name']=='RESULTS_ANALYSIS_CURRENT.json')
    a=json.loads(exact(r))
    if a.get('join_holds') or a.get('live_pair_exclusions'):
        return False
    rows={r['cohort']:r for r in a['endpoints']}
    if set(rows)!=set(q['admitted_specs']):
        return False
    for c,r in q['consumed'].items():
        ar=rows[c]
        if ar['state']!=r['state'] or ar['spec_ref']['sha256']!=q['admitted_specs'][c]:
            return False
        if r['state']=='CLOSED_ACCEPTED' and any(ar.get(a)!=r.get(b) for a,b in
                [('point_ref','accepted_point_ref'),('done_ref','done_ref'),('archive_ref','archive_receipt_ref')]):
            return False
    return True


def refresh_analysis(q):
    if analysis_matches(q):
        return {'status':'EXACT_CURRENT_POPULATION_ALREADY_ANALYZED'}
    p=CFG['incremental_analysis_ref'];exact(p)
    folder=CONTROL/'analysis_attempts'/str(uuid.uuid4());folder.mkdir(parents=True)
    with (folder/'stdout').open('wb') as out,(folder/'stderr').open('wb') as err:
        r=subprocess.run(['/usr/bin/python3','-B',p['path']],stdout=out,stderr=err,
                         cwd='/root/workspace',timeout=90)
    result={'utc':utc(),'status':'ANALYSIS_REFRESH_PASS' if r.returncode==0 else 'ANALYSIS_REFRESH_HOLD',
            'returncode':r.returncode,'code_ref':p,'stdout_ref':ref(folder/'stdout'),
            'stderr_ref':ref(folder/'stderr'),'new_models':0,'registry_writes':0}
    put(folder/'RESULT.json',result)
    if r.returncode!=0 or not analysis_matches(scoped_request()):
        raise ValueError('Incremental analysis not current; preserve evidence and retry metadata only')
    return result


def extra_publication_files():
    p=J/'control/FOREGROUND_PUBLICATION_MANIFEST.json'
    if not p.exists():
        return {}
    raw=p.read_bytes();m=json.loads(raw)
    if m['schema']!='EP_MAIN_FOREGROUND_CLOSEOUT_FILES_V1' or m['goal']!=BASE.GOAL:
        raise ValueError('Foreground closeout manifest schema')
    files={}
    allowed_root=(J/'closeout').resolve()
    for r in m['files']:
        name=r['publish_name'];source=Path(r['path']).resolve()
        if not source.is_relative_to(allowed_root) or not name.startswith('closeout/') or '..' in Path(name).parts:
            raise ValueError('Foreground publication scope')
        if Path(name).suffix not in ('.md','.json','.csv','.patch','.py','.cc','.h') or name in files:
            raise ValueError('Foreground extension/duplicate')
        b=exact(r)
        if len(b)>4*1024*1024:
            raise ValueError('Bounded foreground artifact')
        files[name]=b
    if p.read_bytes()!=raw or sum(map(len,files.values()))>8*1024*1024:
        raise ValueError('Foreground snapshot transition/bound')
    files['closeout/FOREGROUND_PUBLICATION_MANIFEST.json']=raw
    return files


def tail_snapshot(q,status,files):
    rows=[]
    for c in CFG['longtail']:
        r=q['consumed'][c['cohort']]
        row={'cohort':c['cohort'],'program':c['program'],'mode':c['mode'],'state':r['state'],
             'cycles':None,'instructions':None,'CTA':None,'kernel_count':None,
             'spec_ref':c['spec_ref'],'accepted_point_ref':r.get('accepted_point_ref'),
             'archive_receipt_ref':r.get('archive_receipt_ref'),'done_ref':r.get('done_ref')}
        if r['state']=='CLOSED_ACCEPTED':
            p=BASE.exact(r['accepted_point_ref'])
            for k in ('cycles','instructions','CTA','kernel_count'):row[k]=p[k]
            row['hardware_drained']=p['hardware_drained']
        rows.append(row)
    cases={r['cohort'] for r in rows}
    pairs=[r for r in BASE.csv_rows(files['MATCHED_PERFORMANCE.csv'])
           if r['S_cohort'] in cases or r['F_cohort'] in cases]
    done=all(r['state'] in TERMINAL and r['done_ref'] for r in rows)
    x={'schema':'EP_FINITE_LONGTAIL_RESULT_UPDATE_V1','goal':BASE.GOAL,'utc':utc(),
       'status':'ALL_SCOPED_LONGTAIL_TERMINAL' if done else 'SCOPED_LONGTAIL_RUNNING',
       'longtail':rows,'newly_available_matched_pairs':pairs,'batch_terminal_counts':status['terminal_counts'],
       'closed_accepted':status['fully_closed_accepted'],'matched_pair_count':status['all_accepted_profile_pairs'],
       'all3_terminal':bool(done),'Source_KEEP':True,'new_scientific_starts':0,'retry_or_refund':False,
       'large_assets':'GENUINE164','global35_or96_GM':None,
       'claim_boundary':'Only complete accepted applications form performance pairs; failures/holds retained. Foreground closure is not proof of full35/96 coverage.',
       'background_config_ref':ref(CONFIG),'publication_source_ref':ref(__file__)}
    names=['cohort','program','mode','state','cycles','instructions','CTA','kernel_count']
    s=io.StringIO();w=csv.DictWriter(s,fieldnames=names,extrasaction='ignore');w.writeheader();w.writerows(rows)
    md=['# Finite longtail result update','',f'UTC: {x["utc"]}. Status: {x["status"]}.',
        '',f'Accepted experiment points: {x["closed_accepted"]}; matched comparisons: {x["matched_pair_count"]}.',
        '', '|program|mode|state|whole-application cycles|','|---|---|---|---:|']
    md += [f'|{r["program"]}|{r["mode"]}|{r["state"]}|{r["cycles"] if r["cycles"] is not None else "PENDING_OR_UNACCEPTED"}|' for r in rows]
    md+=['','All scientific inputs/source remain unchanged. No new simulator start, retry, refund or budget was used.',
         'Acceptance requires the original complete-population/native qualification, genuine164 archive and two independent restore receipts.',
         'A PARSE_HOLD/technical negative is reported as such; it is never filled with zero or treated as performance evidence.',
         '', '## Matched comparisons available after longtail closure','', '|program|S cycles|F cycles|S/F|','|---|---:|---:|---:|']
    md += [f'|{r["program"]}|{r["S_cycles"]}|{r["F_cycles"]}|{r["speedup_S_over_treatment"]}|' for r in pairs]
    md+=['','Full35/96 GM and T-independent speedup remain unproved by these updates. No new workload expansion is automatic.','']
    files['closeout/LONGTAIL_RESULTS_CURRENT.json']=(json.dumps(x,sort_keys=True,indent=2)+'\n').encode()
    files['closeout/LONGTAIL_RESULTS_CURRENT.csv']=s.getvalue().encode()
    files['closeout/LONGTAIL_RESULTS_CURRENT.md']='\n'.join(md).encode()
    if done:
        files['closeout/FINAL_BACKGROUND_COMPLETION.md']=('All three scoped longtail attempts are terminal.\n\n'+
            '\n'.join(md)+'\nScientific negatives and holds remain included; inspect the exact states and receipt references above.\n').encode()
    put(CONTROL/'CURRENT_RESULTS.json',x)
    return x


def capture_with_closeout():
    files,status,q=BASE_CAPTURE()
    scoped_request()
    files.update(extra_publication_files())
    tail_snapshot(q,status,files)
    return files,status,q


def controller_main():
    global BASE,CFG,BASE_CAPTURE
    CFG=read(CONFIG)
    for k in ('base_publication_ref','reporter_ref','incremental_analysis_ref','common_ref'):
        exact(CFG[k])
    exact(CFG['controller_ref'])
    spec=importlib.util.spec_from_file_location('FiniteMainPublicationPrimitives',CFG['base_publication_ref']['path'])
    BASE=importlib.util.module_from_spec(spec);spec.loader.exec_module(BASE)
    BASE.REPORTER_REF=CFG['reporter_ref'];BASE_CAPTURE=BASE.capture
    BASE.capture=capture_with_closeout
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,256*1024*1024))
    resource.setrlimit(resource.RLIMIT_FSIZE,(16*1024*1024,16*1024*1024));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    os.nice(15);os.sched_setaffinity(0,{max(os.sched_getaffinity(0))})
    lock=(BASE.CTRL/'SINGLE_MAIN_PUBLISHER.lock').open('a')
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    ticks=int((Path('/proc')/str(os.getpid())/'stat').read_text().rsplit(')',1)[1].split()[19])
    lease={'schema':'EP_FINITE_LONGTAIL_MAIN_PUBLISHER_LEASE_V1','utc':utc(),'pid':os.getpid(),
           'start_ticks':ticks,'finite_deadline_utc':CFG['finite_deadline_utc'],'config_ref':ref(CONFIG),
           'controller_ref':ref(__file__),'no_new_science_lane':True,'new_scientific_starts':0}
    put(CONTROL/'LEASE.json',lease)
    until=dt.datetime.fromisoformat(CFG['finite_deadline_utc'])
    last_fingerprint=None;last_token=None;next_at=time.monotonic();retry_at=0.
    while dt.datetime.now(dt.timezone.utc)<until and not (CONTROL/'STOP').exists():
        try:
            q=scoped_request();finger=state_fingerprint(q)
            req=BASE.CTRL/'PUBLISH_NOW.json';token=req.read_bytes() if req.exists() else None
            health={k:process_alive(v['pid'],v['start_ticks']) for k,v in CFG['existing_controllers'].items()}
            put(CONTROL/'HEALTH.json',{'utc':utc(),'existing_controllers':health,
                  'no_controller_restarts':True,'pending':[c['cohort'] for c in CFG['longtail'] if q['consumed'][c['cohort']]['state'] not in TERMINAL]})
            due=(time.monotonic()>=next_at or finger!=last_fingerprint or token!=last_token)
            if due and time.monotonic()>=retry_at:
                retry_at=time.monotonic()+15;BASE.refresh_report();q=scoped_request();refresh_analysis(q)
                result=BASE.publication();print(json.dumps(result),flush=True)
                ok=result['status']=='COMMITTED_PUSHED_AND_REMOTE_HEAD_READBACK_PASS'
                if ok:
                    last_fingerprint=finger;last_token=token;next_at=time.monotonic()+1800
                    state=read(CONTROL/'CURRENT_RESULTS.json')
                    foreground_manifest=J/'control/FOREGROUND_PUBLICATION_MANIFEST.json'
                    foreground_ready=foreground_manifest.exists() and read(foreground_manifest).get('foreground_complete') is True
                    if state['all3_terminal'] and analysis_matches(scoped_request()) and foreground_ready:
                        put(CONTROL/'COMPLETION_RECEIPT.json',{'status':'ALL_SCOPED_LONGTAIL_TERMINAL_TABLES_ANALYSIS_AND_REMOTE_HEAD_VERIFIED',
                            'utc':utc(),'publication_receipt':result,'final_results_ref':ref(CONTROL/'CURRENT_RESULTS.json'),
                            'new_scientific_starts':0,'no_retry_refund':True,'lease':lease})
                        return 0
                else:next_at=time.monotonic()+60;retry_at=next_at
                put(BASE.CTRL/'NEXT.json',{'next_regular_utc':(dt.datetime.now(dt.timezone.utc)+dt.timedelta(seconds=max(0,next_at-time.monotonic()))).isoformat(),
                    'last_status':result['status'],'lease':lease,'scope':'ONLY_THREE_ALREADY_CONSUMED_LONGTAILS'})
        except Exception as exc:
            put(CONTROL/'LATEST_HOLD.json',{'utc':utc(),'error':str(exc),'traceback':traceback.format_exc(),
                'new_scientific_starts':0,'retry_scope':'METADATA_AND_GIT_ONLY'})
            next_at=time.monotonic()+60;retry_at=next_at
        time.sleep(15)
    put(CONTROL/'TERMINAL.json',{'status':'FINITE_DEADLINE_OR_MAIN_STOP_PENDING_WORK_PRESERVED','utc':utc(),'lease':lease})
    return 2


if __name__=='__main__':
    sys.exit(controller_main())
