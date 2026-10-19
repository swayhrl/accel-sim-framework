"""Unqualified preparation must not hash trace bodies, allocate UUIDs or fork."""
from common import *
from unittest.mock import patch
import register_screen,freeze_runtime,verify_original_members

def main():
 rows=[]
 for name,fn,needle in [('register_before_input_and_runtime_qualification',register_screen.main,'INPUT_FULL_IDENTITY.json'),('freeze_runtime_before_resources',freeze_runtime.main,'RESOURCE_AUTHORITY_HOLD_NO_RUNTIME_SCAN'),('trace_hash_before_resources',verify_original_members.main,'')]:
  with patch.object(os,'fork',side_effect=AssertionError('FORBIDDEN_FORK')) as fork,patch.object(register_screen.uuid,'uuid4',side_effect=AssertionError('FORBIDDEN_UUID')) as uuid4:
   try:fn()
   except (AssertionError,FileNotFoundError,ValueError) as exc:
    assert not fork.called and not uuid4.called and (not needle or needle in str(exc)),(name,exc)
    rows.append(dict(case=name,status='EXPECTED_HOLD_BEFORE_START',reason=repr(exc),fork_calls=0,real_UUID_calls=0))
   else:raise AssertionError('PRELAUNCH_HOLD_BYPASSED:'+name)
 assert not (PACK/'UUID_RESERVATIONS.json').exists()
 assert not (PACK/'EXECUTABLE_PREREGISTRATION.json').exists()
 assert not (RAW/'input-member-sha').exists()
 write(PACK/'PRELAUNCH_HOLD_CPU_TESTS.json',dict(status='PASS_FAIL_CLOSED_PREPARATION',cases=rows,simulator_starts=0,trace_body_bytes_read=0,real_UUIDs=0))
 print('PASS_PRELAUNCH_HOLDS',len(rows))
if __name__=='__main__':main()
