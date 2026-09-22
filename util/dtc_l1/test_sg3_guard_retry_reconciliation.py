#!/usr/bin/env python3
"""Regression guard for the source-audited SG3 merge-tag retry residual."""
import importlib.util
from pathlib import Path

module_path=Path(__file__).with_name("sg3_sensitivity_campaign.py")
spec=importlib.util.spec_from_file_location("sg3_sensitivity_campaign",module_path)
module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)

def values(total, classified):
    result={"L2_total_cache_accesses":10,"L2_total_cache_misses":5,"L2_total_cache_reservation_fails":total}
    for reason in ("LINE_ALLOC_FAIL","MISS_QUEUE_FULL","MSHR_ENRTY_FAIL","MSHR_MERGE_ENRTY_FAIL","MSHR_RW_PENDING"):
        result[f"L2_fail_{reason}"]=0
    result["L2_fail_MSHR_MERGE_ENRTY_FAIL"]=classified
    return result

guard=values(6536,6217)
assert module.l2_terminal_consistency(guard,module.GUARD_RETRY_CORE)
assert guard["L2_fail_merge_tag_identity_guard_retry_inferred"]==319
wrong_core=values(6536,6217)
assert not module.l2_terminal_consistency(wrong_core,"wrong-core")
exact=values(5159,5159)
assert module.l2_terminal_consistency(exact,"wrong-core")
assert exact["L2_fail_merge_tag_identity_guard_retry_inferred"]==0
print("SG3 guard-retry reconciliation regression: PASS")
