"""Read-only scientific/authority guard, not a production simulator runner.

Exit3 is the expected fail-closed result while full admission is incomplete.
There is deliberately no simulator subprocess or authority-lock operation here.
"""
import argparse
from common import *


def evaluate():
    read=lambda n:json.loads((PACK/n).read_text()) if (PACK/n).exists() else {}
    pub=read('PUBLISHED_BINDINGS.json')
    y=read('Y2_GATE_BINDING.json')
    obs=read('OBSERVER_CONTRACT_AUDIT.json')
    auth=read('CURRENT_EXECUTION_ADMISSION.json')
    fd=read('LOCK_FDINFO_SUPPLEMENT.json')
    reg=read('PRE_REGISTRATION_STATUS.json')
    uuids=read('UUID_START_CONFLICT_AUDIT.json')
    checks=dict(X_true_K1_Core_published=pub.get('X_functional_Core') is True,
       V_exact_contract_bound=pub.get('V_contract_commit')==V_SHA,
       Z2_V2_published_bound=pub.get('Z2_contract_id')=='Z2_K1_SOURCE_REQUEST_V2',
       Y2_exact_Core_option_PASS=y.get('accepted_PASS_K1_OO_MODEL_SCOPE') is True,
       Y2_K0_equivalence_gate=y.get('accepted_K0_equivalence') is True,
       shared_event_observer_contract=obs.get('AA2_accepts_observer_parity') is True,
       current_authority_and_resources=bool(auth.get('checks')) and all(auth['checks'].values()),
       no_foreign_fd_locks=fd.get('no_foreign_DTC_fd_locks') is True,
       no_previous_reserved_UUID_RUN_START=uuids.get('status')=='PASS_NO_MATCHING_RUN_START_IN_REGISTERED_LOCAL_DTC_RAW_ROOTS',
       executable_preregistration_complete=reg.get('executable_preregistration_complete') is True,
       exact_preregistration_push_fetch_bound=(ROOT/'EXECUTABLE_PREREG_FETCH_BACK.json').exists(),
       production_runner_released=False)
    return dict(utc=now(),status='HOLD_FAIL_CLOSED_NO_SIMULATOR_LAUNCH',checks=checks,
        blockers=[k for k,v in checks.items() if not v],actual_simulator_starts=0,
        execution_authority_acquired=False,production_runner='UNAVAILABLE_NOT_RELEASED',
        note='This is a guard audit, not a claimed complete executable preregistration. No simulation can be launched by this program.')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--check-only',action='store_true');ap.add_argument('--execute',action='store_true')
    ap.parse_args()
    print(json.dumps(evaluate(),indent=2,ensure_ascii=False))
    raise SystemExit(3)


if __name__=='__main__':main()
