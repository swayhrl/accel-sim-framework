"""Exact binding negatives use production review; no external process mutation."""
from common import *
from audit_site import snapshot,proc
import review_authority as ra
import copy
from unittest.mock import patch

def main():
 s=snapshot();controller=proc(os.getpid())
 b=json.loads((PACK/'ADDITIONAL_EXTERNAL_PROJECT_LOCK_BINDINGS.json').read_text())[0]
 target=b['pid'];rows=[];real_proc=ra.proc;real_sha=ra.sha
 lock=next((x for x in s['FLOCKs'] if x['pid']==target and x['path']==b['lock']),None)
 assert lock is not None,'EXTERNAL_PIN_NO_LONGER_LIVE_TEST_NOT_COVERED'
 a=ra.review(s,controller);assert a['status']=='PASS_CURRENT_NO_OTHER_DTC_DISPATCH_AUTHORITY',a
 rows.append(dict(case='exact_current_binding',status='PASS'))
 for case in ['wrong_ticks','wrong_cwd','wrong_argv','wrong_source_sha','wrong_lock_path','wrong_lock_pid','wrong_lock_ticks']:
  snap=copy.deepcopy(s)
  def patched_proc(p):
   r=real_proc(p)
   if p==target and r:
    if case=='wrong_ticks':r['start_ticks']+=1
    if case=='wrong_cwd':r['cwd']+='/unregistered'
   return r
  def patched_sha(p):return '0'*64 if case=='wrong_source_sha' and str(p)==b['script'] else real_sha(p)
  if case=='wrong_argv':
   # Alter the frozen expectation only in the JSON read result, so the real
   # /proc argv is still read and rejected by production comparison.
   changed=copy.deepcopy(b);changed['argv']+=['--unregistered']
  oldloads=ra.json.loads
  def loads(data,*a,**kw):
   result=oldloads(data,*a,**kw)
   if case=='wrong_argv' and isinstance(result,list) and result and result[0].get('pid')==target:return [changed]
   return result
  if case.startswith('wrong_lock_'):
   for l in snap['FLOCKs']:
    if l['pid']==target and l['path']==b['lock']:
     if case=='wrong_lock_path':l['path']+='.unregistered'
     if case=='wrong_lock_pid':l['pid']+=1000000
     if case=='wrong_lock_ticks':l['start_ticks']+=1
  with patch.object(ra,'proc',patched_proc),patch.object(ra,'sha',patched_sha),patch.object(ra.json,'loads',loads):a=ra.review(snap,controller)
  assert a['status']=='STOP_AUTHORITY_NOT_CLOSED',(case,a)
  rows.append(dict(case=case,status='EXPECTED_REJECT',checks=a['checks']))
 write(PACK/'EXTERNAL_BINDING_TESTS.json',dict(status='PASS',cases=rows,simulator_starts=0,foreign_signals=0))
 print('PASS_EXACT_EXTERNAL_BINDING',len(rows))
if __name__=='__main__':main()
