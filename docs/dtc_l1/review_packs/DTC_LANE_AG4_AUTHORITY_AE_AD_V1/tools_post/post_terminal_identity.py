"""Terminal read-only identity/process review; no dispatch, signal or lock APIs."""
from common import *
from mapping_roles import verify_file
from strict_screen import echo,input_identity
from audit_site import proc,snapshot
from review_authority import review

def main():
 assert (RAW/'COHORT_TERMINAL.json').is_file()
 prereg=json.loads((PACK/'EXECUTABLE_PREREGISTRATION.json').read_text());checks=[]
 for n,s in prereg['files'].items():checks.append(dict(path=str(PACK/n),expected_sha256=s,current_sha256=sha(PACK/n),unchanged=sha(PACK/n)==s))
 files={e['path']:e for m in json.loads((PACK/'RUNTIME_MAPPING_MANIFESTS.json').read_text()).values() for e in m['files']};roles=[]
 for p,e in files.items():roles.append(dict(path=p,role=e['role'],actual=verify_file(e),expected_sha256=e['sha256']))
 expected_core=prereg['core_commit'];assert git(CORE,'rev-parse','HEAD')==expected_core and not git(CORE,'status','--porcelain')
 specs=[json.loads((PACK/n).read_text()) for n in prereg['ordered_specs']];inputs={};options=[];instances=[]
 active=json.loads((RAW/'AUTHORITY_ACTIVE.json').read_text())
 instances.append(dict(pid=active['owner']['pid'],start_ticks=active['owner']['start_ticks'],role='COORDINATOR'))
 for spec in specs:
  inputs[spec['workload']]=input_identity(spec)
  r=RAW/'attempts'/(spec['point']+'_'+spec['attempt_uuid']);q=r/'ENGINE/stdout'
  if q.exists():
   text=q.read_text(errors='replace');values=echo(text);options.append(dict(point=spec['point'],options_available=bool(values),all270_expected=spec['expected_full_effective_options'],actual_options=values,exact_match=values==spec['expected_full_effective_options'],Core_embedded_version_present=spec['expected_embedded_core_version'] in text,Framework_embedded_version_present=spec['expected_embedded_framework_version'] in text,stdout_sha256=sha(q),scientific_status='SEE_IMMUTABLE_STRICT_RECEIPT_NO_PROMOTION'))
  child=r/'ENGINE/CHILD.json'
  if child.exists():instances.append(dict(**json.loads(child.read_text()),role='MAIN'))
  events=r/'ENGINE/MAP_EVENTS.jsonl'
  if events.exists():
   for l in events.open():
    e=json.loads(l)
    if 'new_owned_pid' in e:instances.append(dict(pid=e['new_owned_pid'],start_ticks=e['child_start_ticks'],role='PTRACED_EVENT_CONFIRMED_DESCENDANT'))
  term=r/'ENGINE/TERMINAL.json'
  if term.exists():
   t=json.loads(term.read_text())
   for p in (t.get('ownership') or {}).get('pending',[]):instances.append(dict(**p['identity'],role='TERMINAL_UNCONFIRMED_PENDING'))
 # All CPU fixture roots and event-confirmed/pending instances are included,
 # including failed pre-performance engineering rounds. Bounded AG4 raw only.
 for child in (RAW/'cpu-qualification').rglob('CHILD.json'):
  row=json.loads(child.read_text());instances.append(dict(**row,role='CPU_FIXTURE_ROOT'))
 for events in (RAW/'cpu-qualification').rglob('MAP_EVENTS.jsonl'):
  for l in events.open():
   e=json.loads(l)
   if 'new_owned_pid' in e and 'child_start_ticks' in e:instances.append(dict(pid=e['new_owned_pid'],start_ticks=e['child_start_ticks'],role='CPU_EVENT_CONFIRMED_DESCENDANT'))
 for term in (RAW/'cpu-qualification').rglob('TERMINAL.json'):
  t=json.loads(term.read_text())
  for p in (t.get('ownership') or {}).get('pending',[]):instances.append(dict(**p['identity'],role='CPU_FAILED_ROUND_PENDING_TRACER_EXITKILL'))
 unique={(p['pid'],p['start_ticks']):p for p in instances}
 for p in unique.values():
  live=proc(p['pid']);p['current']=live;p['same_instance_live']=bool(live and live['start_ticks']==p['start_ticks'])
 snap=snapshot();auth=review(snap);ownlocks=[l for l in snap['FLOCKs'] if l['path']==str(RAW/'AG_execution.lock')]
 write(RAW/'TERMINAL_FULL_SITE_SNAPSHOT.json',snap,exclusive=True)
 result=dict(status='PASS_TERMINAL_IDENTITY_AND_OWN_PROCESS_LOCK_CLOSURE' if all(c['unchanged'] for c in checks) and not any(p['same_instance_live'] for p in unique.values()) and not ownlocks and auth['status']=='PASS_CURRENT_NO_OTHER_DTC_DISPATCH_AUTHORITY' else 'STOP_POST_TERMINAL_CLOSURE',utc=now(),operative_files=checks,runtime_roles=roles,Core_commit=expected_core,Core_clean=True,inputs=inputs,all_owned_instances=list(unique.values()),own_FLOCKs=ownlocks,authority=auth,no_automatic_dispatch=True,foreign_signals=0,old_files_modified=0)
 write(PACK/'POST_TERMINAL_IDENTITY_AND_PROCESS_LOCK.json',result);write(PACK/'ACTUAL_OPTIONS_IDENTITY_REVIEW.json',dict(rows=options,availability='UNAVAILABLE_WHEN_ECHO_NOT_REACHED',no_failed_attempt_promotion=True))
 assert result['status']=='PASS_TERMINAL_IDENTITY_AND_OWN_PROCESS_LOCK_CLOSURE',result['status']
 print(result['status'],len(checks),len(unique))
if __name__=='__main__':main()
