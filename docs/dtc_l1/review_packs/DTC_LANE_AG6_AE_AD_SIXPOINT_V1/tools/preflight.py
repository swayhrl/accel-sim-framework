"""Two read-only R2/authority samples; no lock, process start or budget charge."""
from common import *
from audit_site import snapshot,proc
from review_authority import review
from resource_policy import admission_checks
import time,argparse

def main(label):
 dest=RAW/'preparation-preflights'/label;dest.mkdir(parents=True,exist_ok=False)
 first=snapshot();write(dest/'FIRST.json',first,exclusive=True)
 time.sleep(10.1)
 second=snapshot();write(dest/'SECOND.json',second,exclusive=True)
 checks=admission_checks(first,second);a=review(second,proc(os.getpid()))
 result=dict(utc=now(),status='PASS_PREPARATION_RESOURCE_SNAPSHOT' if all(checks.values()) and a['status']=='PASS_CURRENT_NO_OTHER_DTC_DISPATCH_AUTHORITY' else 'HOLD_RESOURCE_OR_AUTHORITY_BEFORE_START',all_resource_checks_pass=all(checks.values()),resource_checks=checks,authority=a,first_snapshot=str(dest/'FIRST.json'),second_snapshot=str(dest/'SECOND.json'),simulator_starts=0,starts_consumed=0,not_a_performance_admission=True)
 write(dest/'DECISION.json',result,exclusive=True);write(PACK/'CURRENT_SITE_AUDIT.json',result)
 print(json.dumps(dict(status=result['status'],failed_checks=[k for k,v in checks.items() if not v],disk_free_bytes=second['disk_free_bytes'],IO_full=second['pressure']['io']['full']['avg10'],authority=a['status'])))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--label',required=True);main(p.parse_args().label)
