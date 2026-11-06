"""Exactly one pass over the pinned31 natural closures; no daemon or science.

Default CLI is PREPARATION_ONLY. Actual execution requires Main's source-bound
release plus D's kernel-retirement exception review; preparation never calls run.
"""
from pathlib import Path
import argparse,hashlib,json,os,time,types

BASE=Path('/root/data/dtc_controlled_oracle_20261106_v1');ROOT=BASE/'initial8'
S17_SHA='d0d344e4dc50e299d5f72fb361ce5856f4c2960ea4132c5424f43c80cc13b507'
class Hold(RuntimeError):pass
def need(x,message):
 if not x:raise Hold(message)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rd(p):return json.loads(Path(p).read_bytes())
def pin(ref):
 p=Path(ref['path']);need(sha(p)==ref['sha256'],'PIN_DRIFT:'+str(p));return p
def load(p,name):
 p=Path(p);m=types.ModuleType(name);m.__file__=str(p);exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__);return m
def write(p,value,exclusive=False):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);b=(json.dumps(value,sort_keys=True,indent=2)+'\n').encode()
 if exclusive:
  with p.open('xb')as h:h.write(b);h.flush();os.fsync(h.fileno())
 else:
  tmp=p.with_name('.'+p.name+'.'+str(os.getpid())+'.writing');tmp.write_bytes(b);os.replace(tmp,p)

def validate_fixed31(snapshot,auth):
 rows=snapshot['rows']
 need(snapshot['schema']=='DTC_EXTERNAL_FIXED31_NATURAL_DONE_SNAPSHOT_V1'
      and len(rows)==len({x['cohort']for x in rows})==len({x['uuid']for x in rows})==31,
      'EXACT31_ORIGINAL_UUID_ROWS_REQUIRED')
 need(snapshot['excluded_live_or_not_DONE_cohort']=='E2-DTCORACLE-I8-6df3a84b612086e8-DH-OFF_MATCHED-V1',
      'ONLY_ORIGINAL_SCAN_OFF_TAIL_EXCLUDED')
 need(set(auth['authorized_closed_cohorts'])=={x['cohort']for x in rows},'RELEASE_SNAPSHOT_EXACT31')
 need(sum(x['existing_result_sha256']is not None for x in rows)==8,'PRESERVE_ORIGINAL8_RESULTS')
 return sorted(rows,key=lambda x:(x['existing_result_sha256']is None,x['cohort']))

def verify_row(row):
 c=row['cohort'];ip=ROOT/'control/qualification_ledger'/(c+'.INTENT.json');dp=ip.with_name(c+'.DONE.json')
 need(sha(ip)==row['intent_sha256']and sha(dp)==row['DONE_sha256'],'FIXED31_INTENT_DONE_IDENTITY')
 i,d=rd(ip),rd(dp);out=ROOT/'DTC/run/results'/row['uuid']
 need(i['uuid']==d['uuid']==row['uuid']and Path(i['output'])==out
      and d==rd(out/'NATIVE_EXIT.json')and d['raw_sha256']==row['raw_sha256'], 'FIXED31_ORIGINAL_UUID_EXIT_RAW')
 need(d['stop_reason']is None and d['launcher_wait_returncode']==0 and d['native_simulator_observed']is True,
      'FIXED31_NATURAL_ONLY_NOT_NEGATIVE_PROMOTION')
 p=ROOT/'analysis'/(c+'.RESULT.json')
 if row['existing_result_sha256']is not None:need(sha(p)==row['existing_result_sha256'],'ORIGINAL8_RESULT_IMMUTABLE')
 return p

def claim_pass_directory(base,authorization_sha):
 need(len(authorization_sha)==64 and all(c in'0123456789abcdef'for c in authorization_sha),
      'CANONICAL_MAIN_AUTHORIZATION_SHA_REQUIRED')
 out=Path(base)/'control/external_closed31_single_pass'/authorization_sha
 out.mkdir(parents=True,exist_ok=False);return out

def run(config_path,config_sha):
 """Dormant actual entry. Tests only invoke pure validation/mock pass APIs."""
 need(sha(config_path)==config_sha,'EXACT_MAIN_CONFIGURATION_PIN')
 config=rd(config_path);need(config.get('actual_execution_authorized')is True,'DEFAULT_UNARMED_NO_CLOSEOUT')
 auth=rd(pin(config['authorization']))
 need(auth['status']=='AUTHORIZED_CLOSED_ONLY'
      and auth['driver_source_sha256']==sha(__file__)and auth['scope']=='EXTERNAL_FIXED31_KERNEL_RETIRED_SINGLE_PASS',
      'MAIN_SOURCE_BOUND_SINGLE_PASS_RELEASE_REQUIRED')
 snapshot=rd(pin(config['fixed31_snapshot']));rows=validate_fixed31(snapshot,auth)
 ref=config['S17_component'];need(ref['sha256']==S17_SHA,'ONLY_QUALIFIED_S17_COMPONENT');module=load(pin(ref),'EXTERNAL31_S17_ACTUAL')
 out=claim_pass_directory(BASE,config['authorization']['sha256']) # no automatic second pass
 status=dict(schema='DTC_EXTERNAL31_SINGLE_PASS_STATUS_V1',caller_pid=os.getpid(),driver_source_sha256=sha(__file__),
             Main_authorization=config['authorization'],config_sha256=config_sha,fixed31_snapshot=config['fixed31_snapshot'],
             models_started=0,scientific_requests_registered=0,budget_writes=0,owner_or_tracer_actions=0,
             total_fixed_rows=31,completed=[],errors=[],state='ADMISSION_PENDING_NO_CLOSEOUT_YET')
 write(out/'BEGIN.fixed.json',status,True)
 try:
  with module.CloseoutSession(config)as session:
   for row in rows:
    p=verify_row(row);before=sha(p)if p.exists()else None
    need(before==row['existing_result_sha256'],'NO_UNEXPECTED_RESULT_WRITER_BEFORE_THIS_PASS')
    v=session.finish(row['cohort'])
    need(v['uuid']==row['uuid'],'SAME_EXISTING_UUID_FINISHED')
    need(v['state']=='PASS_CONTROLLED_ORACLE_DH_STRICT_ARCHIVE_NATIVE_RESTORE',
         'STRICT_ARCHIVE_NATIVE_RESTORE_ACCEPTED_STATE_REQUIRED')
    after=sha(p)
    if before is not None:need(after==before,'ORIGINAL8_RESULT_CHANGED')
    status['completed'].append(dict(cohort=row['cohort'],uuid=row['uuid'],result_path=str(p),result_sha256=after,
        original_state=v['state'],cycles=v.get('cycles'),preserved_existing_result=before is not None))
    status['state']='CLOSED31_SINGLE_PASS_IN_PROGRESS';write(out/'STATE.json',status)
   need(len(status['completed'])==31,'ALL_FIXED31_REQUIRED_FOR_COMPLETE')
   status['state']='ALL_FIXED31_CLOSED_VERIFIED_PASS_COMPLETE_NO_SCIENCE_RELEASE'
  write(out/'FINAL.fixed.json',status,True);return status
 except BaseException as error:
  status['state']='SINGLE_PASS_ENGINEERING_HOLD_PRESERVE_COMPLETED_NO_AUTOMATIC_RETRY'
  status['errors'].append(repr(error));write(out/'FINAL.fixed.json',status,True);raise

def main():
 p=argparse.ArgumentParser();p.add_argument('--run',action='store_true');p.add_argument('--config');p.add_argument('--config-sha');a=p.parse_args()
 if not a.run:print(json.dumps(dict(status='CPU_PREPARATION_ONLY',actual_closeout=False)));return
 need(a.config and a.config_sha,'MAIN_CONFIGURATION_REQUIRED');run(a.config,a.config_sha)
if __name__=='__main__':main()
