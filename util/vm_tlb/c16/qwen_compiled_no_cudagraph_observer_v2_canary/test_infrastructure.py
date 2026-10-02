#!/usr/bin/env python3
"""CPU-only directed checks for budget accounting and raw manifest verifier."""
import tempfile
from pathlib import Path

from run_guard import GpuGuard, MAX_POINT, MAX_TOTAL
from verify_tree import sha, verify

def main():
    assert MAX_TOTAL==180.0 and MAX_POINT=={"MP02":75.0,"MP03":105.0}
    good=GpuGuard(prior_total=12,prior_by_point={"MP02":12})
    assert good.total==12 and good.by_point["MP02"]==12
    for args in ({"prior_total":180},{"prior_by_point":{"MP02":75}},{"prior_by_point":{"MP03":105}}):
        try: GpuGuard(**args)
        except ValueError: pass
        else: raise AssertionError("invalid budget accepted")
    with tempfile.TemporaryDirectory() as d:
        root=Path(d)
        (root/"payload.json").write_text('{"x":1}\n')
        (root/"RAW_SHA256SUMS").write_text(f"{sha(root/'payload.json')}  payload.json\n")
        assert verify(root)["status"]=="PASS"
        (root/"payload.json").write_text('{"x":2}\n')
        assert verify(root)["status"]=="FAIL"
    print("7 infrastructure directed checks PASS")

if __name__=="__main__": main()
